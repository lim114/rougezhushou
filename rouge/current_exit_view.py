"""Exit-table reading conditions; difficulty never selects a hidden original variant."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_exit as model

class CurrentExitPanel(DocumentedEventFlowPanel):
    def __init__(self, target=None, parent=None):
        self.source_request = target['source_request'] if target else None
        super().__init__('exit', parent=parent, reference_model=model, defer_initial_refresh=True)
        row = QHBoxLayout(); row.addWidget(QLabel('仅本页常规模式对照：'))
        for name, label, maximum in (('difficulty', '保密等级', 16), ('action_points', '结算前行动力', 99999), ('gold', '源石锭', 99999)):
            row.addWidget(QLabel(label)); box = QSpinBox(); box.setRange(-1, maximum); box.setSpecialValueText('未知'); box.setValue(-1); box.setAccessibleName('仅本页'+label+'对照'); setattr(self, name, box); row.addWidget(box); box.valueChanged.connect(self._conditions_changed)
        self.add_condition_row(row)
        self.refresh_reference(initial_scene=None, initial=True)
        if target:
            targets = self.result['source_targets'] if self.result else []
            sid, cid = targets[0] if len(targets) == 1 else (None, None)
            self.scene.setCurrentIndex(max(0, self.scene.findData(sid)))
            if cid:
                for i in range(self.choices.count()):
                    if self.choices.item(i).data(Qt.ItemDataRole.UserRole) == cid: self.choices.setCurrentRow(i); break

    def _fresh_reference(self):
        ap,gold,difficulty=(box.value() for box in (self.action_points,self.gold,self.difficulty))
        return model.reference('exit', None if ap<0 else ap, None if gold<0 else gold,
                               None if difficulty<0 else difficulty, self.source_request)

    def _conditions_changed(self, *_): self.refresh_reference()

from .player_window_frame import PlayerDialog


class CurrentExitDialog(PlayerDialog):
    def __init__(self, target=None, parent=None):
        super().__init__(parent); self.setWindowTitle('险路尽头 · 招募、换层与独立奖励'); self.resize(760, 600)
        layout=QVBoxLayout(self); self.panel=CurrentExitPanel(target, self); layout.addWidget(self.panel)
        from .player_map_reader import readable
        readable(self)
    def closeEvent(self, event): self.panel._close_battle(); super().closeEvent(event)
