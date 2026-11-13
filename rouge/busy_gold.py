"""Current-window gold previews while the full sampler is busy or waiting for a sharper frame."""
from dataclasses import dataclass
from threading import Thread

from PySide6.QtCore import QObject, Signal

from .hud_gold_preview import read_gold_preview
from .viewport import prepare_frame


@dataclass(eq=False)
class GoldReference:
    marker: tuple
    frame: dict
    observation: dict
    line_reader: object

    def same_source(self, other):
        """A refreshed reference may describe the same capture source and geometry."""
        return (self.marker == other.marker and self.frame['target'] == other.frame['target']
                and self.frame['client_rect'] == other.frame['client_rect']
                and self.frame['image'].shape == other.frame['image'].shape)


class BusyGold(QObject):
    reference_ready = Signal(object)
    finished = Signal(object)

    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.reference = None
        self.checked_seq = 0
        self.running = False
        self.shown = None
        self.reference_ready.connect(self.accept_reference)
        self.finished.connect(self.accept_result)

    def current_marker(self):
        w = self.owner
        return w.sample_epoch, w.capture.stats()['generation'], w.run.state['id']

    def source_available(self, reference):
        if reference.marker != self.current_marker():
            return False
        if reference.frame['target'] != self.owner.capture.target:
            return False
        try:
            self.owner.capture.check_health()
        except RuntimeError:
            return False
        return True

    def accept_reference(self, reference):
        w = self.owner
        if (w.closing or not w.auto.isChecked() or reference.marker != self.current_marker()
                or reference.frame['seq'] < w.last_sample_seq or reference.frame['client_rect'] is None
                or (self.reference is not None and reference.frame['seq'] < self.reference.frame['seq'])
                or reference.frame['target'] != w.capture.target):
            return
        same_source = self.reference is not None and reference.same_source(self.reference)
        self.reference = reference
        # Preserve successful current readings. A failed attempt may become
        # readable using the refreshed label locations and must remain eligible.
        self.checked_seq = (max(self.shown[0], reference.frame['seq'])
                            if same_source and self.shown is not None else reference.frame['seq'])

    def poll(self):
        w = self.owner
        reference = self.reference
        if self.running or reference is None:
            return
        if not self.source_available(reference):
            self.clear()
            return
        if not w.compact_window.visible_current_resource_strips():
            return
        frame = w.capture.buffer.latest(after_seq=max(self.checked_seq, w.last_sample_seq),
                                        settling_only=not w.busy)
        if frame is None:
            return
        self.checked_seq = frame['seq']
        prior = reference.frame
        if (frame['generation'] != prior['generation'] or frame['target'] != prior['target']
                or frame['client_rect'] != prior['client_rect']
                or frame['image'].shape != prior['image'].shape):
            self.clear()
            return
        self.running = True

        def work():
            gold = None
            try:
                try:
                    _, viewport = prepare_frame(frame['image'], frame['client_rect'])
                except ValueError:
                    # An unusable transition frame cannot qualify a HUD value.
                    return
                gold = read_gold_preview(frame['image'], prior['image'], reference.observation,
                                         viewport, reference.line_reader)
            finally:
                if not w.closing:
                    self.finished.emit((reference, frame['captured_at'], frame['seq'], gold))

        Thread(target=work, daemon=True, name='rouge-current-gold').start()

    def accept_result(self, result):
        self.running = False
        reference, at, seq, gold = result
        w = self.owner
        current = self.reference
        # A full read may refresh the reference while this newer frame is being
        # verified. That revision does not invalidate its freshly checked labels
        # and digits. A later reference frame or a different source still does.
        if (w.closing or current is None or not reference.same_source(current)
                or seq < current.frame['seq']
                or (at, seq) <= (w.last_sample_at, w.last_sample_seq)
                or not w.auto.isChecked()):
            return
        if not self.source_available(reference):
            self.clear()
            return
        if gold is None:
            self.withdraw()
            return
        self.checked_seq = max(self.checked_seq, seq)
        self.shown = (seq, {**gold, 'captured_at': at})
        w.refresh_display_hud()

    def complete(self, marker, seq, *, map_read):
        ref = self.reference
        if ref is None or ref.marker != marker:
            return
        if seq >= ref.frame['seq'] and not map_read:
            self.clear()
        elif self.shown is not None and seq >= self.shown[0]:
            self.withdraw()

    def withdraw(self):
        if self.shown is not None:
            self.shown = None
            self.owner.refresh_display_hud()

    def clear(self):
        self.reference = None
        self.withdraw()
