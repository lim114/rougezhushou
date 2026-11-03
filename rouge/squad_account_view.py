"""A live view of the selected manual profile; all changes stay in its editor."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)
from .squad_account_plan import format_squad_plan, squad_account_plan
from .technology_state import STATUS_LABELS


class SquadAccountPanel(QWidget):
    technology_requested = Signal(str)

    def __init__(self, account_state, parent=None):
        super().__init__(parent)
        self.account_state = account_state
        layout = QVBoxLayout(self)
        actions = QHBoxLayout()
        actions.addWidget(QLabel('强化分队条件 · 对照等级'))
        self.grade = QComboBox()
        for value in range(16): self.grade.addItem(str(value), value)
        actions.addWidget(self.grade)
        self.search = QLineEdit(); self.search.setPlaceholderText('筛选分队或条件')
        actions.addWidget(self.search, 1)
        self.jump_button = QPushButton('查看对应科技'); actions.addWidget(self.jump_button)
        self.copy_button = QPushButton('复制完整条件清单'); actions.addWidget(self.copy_button)
        layout.addLayout(actions)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['分队', '原表条件', '本档案手动科技记录', '等级门槛参数对照'])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        self.notice = QPlainTextEdit(); self.notice.setReadOnly(True); self.notice.setMaximumHeight(100)
        layout.addWidget(self.notice)
        self.grade.currentIndexChanged.connect(self.refresh)
        self.search.textChanged.connect(self.refresh)
        self.table.itemSelectionChanged.connect(self.selection_changed)
        self.jump_button.clicked.connect(self.jump)
        self.copy_button.clicked.connect(lambda: QApplication.clipboard().setText(format_squad_plan(self.plan)))
        self.refresh()

    def refresh(self, *_args):
        self.plan = squad_account_plan(self.account_state, self.grade.currentData())
        query = self.search.text().strip().casefold()
        self.rows = [r for r in self.plan['rows'] if query in (r['name'] + r['condition']).casefold()]
        self.table.setRowCount(len(self.rows))
        for index, row in enumerate(self.rows):
            gate = row['gate_grade_parameter']
            values = [row['name'], row['condition'],
                      STATUS_LABELS[row['manual_status']] if row['technology_id'] else '需另核验账户培养',
                      '无此门槛资料' if gate is None else f"{gate}：参数{'达到' if row['grade_parameter_met'] else '未达到'}"]
            for column, value in enumerate(values): self.table.setItem(index, column, QTableWidgetItem(value))
        self.table.resizeColumnsToContents()
        self.notice.setPlainText('资料档案：' + self.plan['profile_name'] + '\n' + '\n'.join(self.plan['notes']))
        self.selection_changed()

    def selection_changed(self):
        index = self.table.currentRow()
        self.jump_button.setEnabled(0 <= index < len(self.rows) and self.rows[index]['technology_id'] is not None)

    def jump(self):
        index = self.table.currentRow()
        if 0 <= index < len(self.rows) and self.rows[index]['technology_id']:
            self.technology_requested.emit(self.rows[index]['technology_id'])
