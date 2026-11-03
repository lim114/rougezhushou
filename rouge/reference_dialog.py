"""Explicit structured offline inputs with invalidation and copyable conditions."""
import json
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QPlainTextEdit,
    QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QVBoxLayout)
from .manual_scenario import parse_preview_object


class ReferenceDialog(QDialog):
    def __init__(self, title, description, defaults, evaluator, formatter, columns, parent=None):
        super().__init__(parent)
        self.result = None; self.evaluator = evaluator; self.formatter = formatter; self.columns = columns
        self.setWindowTitle(title); self.resize(1050,700)
        layout = QVBoxLayout(self)
        label = QLabel(description); label.setWordWrap(True); layout.addWidget(label)
        self.editor = QPlainTextEdit(); self.editor.setMaximumHeight(180)
        self.editor.setPlainText(json.dumps(defaults,ensure_ascii=False,indent=2)); layout.addWidget(self.editor)
        actions = QHBoxLayout()
        self.calculate_button = QPushButton('计算对照'); self.copy_button = QPushButton('复制结果与完整条件')
        actions.addWidget(self.calculate_button); actions.addWidget(self.copy_button); layout.addLayout(actions)
        self.table = QTableWidget(0,len(columns)); self.table.setHorizontalHeaderLabels([label for _,label in columns])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); layout.addWidget(self.table,1)
        self.notice = QPlainTextEdit(); self.notice.setReadOnly(True); layout.addWidget(self.notice,1)
        self.editor.textChanged.connect(self.invalidate)
        self.calculate_button.clicked.connect(self.calculate); self.copy_button.clicked.connect(self.copy)
        self.calculate()

    def invalidate(self):
        self.result = None; self.copy_button.setEnabled(False); self.table.setRowCount(0)
        self.notice.setPlainText('条件已修改，请计算对照。')

    def calculate(self):
        self.invalidate()
        try: result = self.evaluator(parse_preview_object(self.editor.toPlainText(),'对照条件'))
        except (ValueError,KeyError,TypeError) as error: self.notice.setPlainText(str(error)); return
        self.result = result; self.table.setRowCount(len(result['rows']))
        for i,row in enumerate(result['rows']):
            for j,(key,_) in enumerate(self.columns):
                value = row[key]
                text = '未知' if value is None else format(value,'.8g') if type(value) in (int,float) else str(value)
                if row.get(key+'_applicable') is False: text = '不适用'
                self.table.setItem(i,j,QTableWidgetItem(text))
        self.table.resizeColumnsToContents(); self.notice.setPlainText(self.formatter(result)); self.copy_button.setEnabled(True)

    def copy(self):
        if self.result is not None: QApplication.clipboard().setText(self.formatter(self.result))
