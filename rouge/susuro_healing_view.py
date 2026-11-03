"""An explicit optional recipient ratio; unchecked means no assumption."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QCheckBox,QDoubleSpinBox,QHBoxLayout

class RecipientRatioInput(QWidget):
    valueChanged=Signal(object)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.known=QCheckBox('指定参考')
        self.ratio=QDoubleSpinBox();self.ratio.setRange(0,1)
        self.ratio.setDecimals(8);self.ratio.setSingleStep(.01);self.ratio.setValue(.5)
        self.ratio.setEnabled(False)
        row=QHBoxLayout(self);row.setContentsMargins(0,0,0,0)
        row.addWidget(self.known);row.addWidget(self.ratio)
        self.known.toggled.connect(self._toggle)
        self.ratio.valueChanged.connect(lambda _:self.valueChanged.emit(self.value()))

    def _toggle(self,checked):
        self.ratio.setEnabled(checked);self.valueChanged.emit(self.value())

    def value(self):return self.ratio.value() if self.known.isChecked() else None

    def setValue(self,value):
        # Also used by temporary UI fixtures; no setting or run-memory writes.
        self.known.setChecked(value is not None)
        if value is not None:self.ratio.setValue(value)
