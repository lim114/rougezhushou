"""Exit-table reading conditions; difficulty never selects a hidden original variant."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_exit as model

class CurrentExitPanel(DocumentedEventFlowPanel):
    def __init__(self, target=None, parent=None):
        self.source_request = target['source_request'] if target else None
        super().__init__('exit', parent=parent, reference_model=model)
        row = QHBoxLayout(); row.addWidget(QLabel('仅本页常规模式对照：'))
        for name, label, maximum in (('difficulty', '保密等级', 16), ('action_points', '结算前行动力', 99999), ('gold', '源石锭', 99999)):
            row.addWidget(QLabel(label)); box = QSpinBox(); box.setRange(-1, maximum); box.setSpecialValueText('未知'); box.setValue(-1); box.setAccessibleName('仅本页'+label+'对照'); setattr(self, name, box); row.addWidget(box); box.valueChanged.connect(self._conditions_changed)
        self.layout().insertLayout(1, row)
        if target:
            targets = self.result['source_targets'] if self.result else []
            sid, cid = targets[0] if len(targets) == 1 else (None, None)
            self.scene.setCurrentIndex(max(0, self.scene.findData(sid)))
            if cid:
                for i in range(self.choices.count()):
                    if self.choices.item(i).data(Qt.ItemDataRole.UserRole) == cid: self.choices.setCurrentRow(i); break

    def _fresh_reference(self):
        def number(name):
            w = getattr(self, name, None); return None if w is None or w.value() < 0 else w.value()
        return model.reference('exit', number('action_points'), number('gold'), number('difficulty'), self.source_request)

    def _conditions_changed(self, *_): self.refresh_reference()

class CurrentExitDialog(QDialog):
    def __init__(self, target=None, parent=None):
        super().__init__(parent); self.setWindowTitle('险路尽头 · 招募、换层与独立奖励'); self.resize(1100, 820)
        layout=QVBoxLayout(self); self.panel=CurrentExitPanel(target, self); layout.addWidget(self.panel)
    def closeEvent(self, event): self.panel._close_battle(); super().closeEvent(event)
