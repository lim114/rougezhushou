"""Immutable, isolated level diagnostic result from a declared panel snapshot."""
from copy import deepcopy
import json
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QPlainTextEdit)
from .level_panel_diagnostics import STATUS_NAMES, format_level_diagnostics


class LevelPanelDialog(QDialog):
    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.result = deepcopy(result)
        self.setWindowTitle('等级与面板偏差排查 · 独立声明快照')
        self.resize(1250, 900)
        layout = QVBoxLayout(self)
        self.summary = QLabel(format_level_diagnostics(self.result))
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.filter = QComboBox()
        self.filter.addItem('全部合法等级', None)
        for status, name in STATUS_NAMES.items():
            self.filter.addItem(name, status)
        layout.addWidget(self.filter)
        self.fields = self.result['field_constraints']
        self.table = QTableWidget(0, len(self.fields) + 2)
        self.table.setHorizontalHeaderLabels(['等级', '排查结果'] +
            [field['label'] + ' · 预测 / 观察减预测' for field in self.fields])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, 1)
        self.conditions = QPlainTextEdit()
        self.conditions.setReadOnly(True)
        self.conditions.setMaximumHeight(160)
        self.conditions.setPlainText(json.dumps({'fixed_conditions': self.result['fixed_conditions'],
            'original_level': self.result['original_level'], 'observation': self.result['observation'],
            'tolerance': self.result['tolerance'], 'source': self.result['source']},
            ensure_ascii=False, indent=2, allow_nan=False))
        layout.addWidget(self.conditions)
        self.filter.currentIndexChanged.connect(self.populate)
        self.populate()

    def populate(self):
        status = self.filter.currentData()
        rows = [r for r in self.result['rows'] if status is None or r['status'] == status]
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            values = [str(row['level']), STATUS_NAMES[row['status']]]
            by_field = {f['field']: f for f in row['fields']}
            for field in self.fields:
                value = by_field.get(field['field'])
                values.append('未知' if value is None or value['predicted'] is None else
                    format(value['predicted'], '.10g') + ' / ' + format(value['difference'], '+.10g'))
            for j, text in enumerate(values):
                item = QTableWidgetItem(text)
                if row['error']:
                    item.setToolTip(row['error'])
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()
