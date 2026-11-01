"""Compact reader controls using the already adopted BSD superqt disclosure."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from .collapsible_section import QCollapsible


class MechanismReaderHeader(QWidget):
    def __init__(self, notice, choices, portrait, refresh):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0)
        self.scope = QCollapsible('固定机制资料 · 非本局实况', expandedIcon='−', collapsedIcon='+')
        self.scope.setAccessibleName('固定关卡参考，不代表本局实况；展开查看适用说明')
        self.scope.setDuration(0); self.scope.addWidget(notice)
        self.scope.content().hide(); self.scope.toggled.connect(self.scope.content().setVisible)
        bar = QHBoxLayout(); bar.addWidget(self.scope, 1)
        refresh.setToolTip(refresh.text()); refresh.setText('刷新资料')
        bar.addWidget(refresh, 0, Qt.AlignmentFlag.AlignTop); layout.addLayout(bar)
        portrait.setMaximumWidth(150); portrait.setWordWrap(True)
        row = QHBoxLayout(); row.addWidget(portrait); row.addWidget(choices, 1)
        layout.addLayout(row)
