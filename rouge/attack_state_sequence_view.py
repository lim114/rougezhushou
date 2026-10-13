"""Editable public declarations; no account, run state, game or chat access."""
from copy import deepcopy
import json

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QPlainTextEdit, QDoubleSpinBox)

from .attack_state_sequence import (SCOPES, NAMES, sequence_choices, public_sequence_payload,
    project_attack_state_sequence, format_attack_state_sequence)
from .animation_reference import label


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('JSON字段重复：' + key)
        result[key] = value
    return result


class AttackStateSequencePanel(QWidget):
    resultReady = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result = None
        layout = QVBoxLayout(self)
        notice = QLabel('显式声明进入攻击状态或同状态继续，再选原件动作候选。累计仅为等待分项之和；实际首击、结束和整串耗时未知。')
        notice.setWordWrap(True)
        layout.addWidget(notice)
        bar = QHBoxLayout()
        self.operator = QComboBox()
        for operator in SCOPES:
            self.operator.addItem(NAMES[operator], operator)
        self.scope = QComboBox()
        self.load_template = QPushButton('载入公开声明示例')
        bar.addWidget(self.operator)
        bar.addWidget(self.scope)
        bar.addWidget(self.load_template)
        layout.addLayout(bar)
        row = QHBoxLayout()
        self.candidate = QComboBox()
        self.period = QDoubleSpinBox()
        self.period.setRange(.000001, 3600)
        self.period.setDecimals(6)
        self.period.setValue(2.55)
        self.period.setSuffix(' 秒参考周期')
        self.add_entry = QPushButton('追加entry')
        self.add_continue = QPushButton('追加continue')
        row.addWidget(self.candidate, 1)
        row.addWidget(self.period)
        row.addWidget(self.add_entry)
        row.addWidget(self.add_continue)
        layout.addLayout(row)
        self.editor = QPlainTextEdit()
        self.editor.setAccessibleName('攻击状态声明序列JSON')
        layout.addWidget(self.editor, 1)
        self.calculate_button = QPushButton('计算状态门与逐段等待')
        layout.addWidget(self.calculate_button)
        self.status = QLabel('载入示例或填写声明后计算。')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.result_view = QPlainTextEdit()
        self.result_view.setReadOnly(True)
        self.result_view.setAccessibleName('攻击状态序列条件计算结果')
        layout.addWidget(self.result_view, 1)
        self.operator.currentIndexChanged.connect(self._operator_changed)
        self.scope.currentIndexChanged.connect(self._scope_changed)
        self.load_template.clicked.connect(self._load_template)
        self.add_entry.clicked.connect(lambda: self._append('entry'))
        self.add_continue.clicked.connect(lambda: self._append('continue'))
        self.calculate_button.clicked.connect(self.calculate)
        self.editor.textChanged.connect(self._edited)
        self._operator_changed()

    def _operator_changed(self, *_):
        self.scope.blockSignals(True)
        self.scope.clear()
        for scope in SCOPES[self.operator.currentData()]:
            self.scope.addItem('普通攻击' if scope == 'normal' else '技能' + scope, scope)
        self.scope.blockSignals(False)
        self._scope_changed()

    def _scope_changed(self, *_):
        self.candidate.clear()
        for record in sequence_choices(self.operator.currentData(), self.scope.currentData()):
            self.candidate.addItem(label(record), record['id'])

    def _edited(self):
        self._result = None
        self.result_view.clear()
        self.status.setText('声明已编辑；重新计算后显示结果。')

    def _load_template(self):
        payload = public_sequence_payload(self.operator.currentData(), self.scope.currentData())
        self.editor.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))

    def current_query(self):
        try:
            return json.loads(self.editor.toPlainText(), object_pairs_hook=_unique_pairs,
                parse_constant=lambda name: (_ for _ in ()).throw(ValueError('JSON需要有限数字：' + name)))
        except json.JSONDecodeError as error:
            raise ValueError('声明JSON格式错误：' + str(error)) from None

    def _append(self, state):
        try:
            payload = self.current_query()
            project_attack_state_sequence(payload)
            if payload['operator'] != self.operator.currentData() or payload['scope'] != self.scope.currentData():
                raise ValueError('追加候选与编辑中的干员/作用域不符；先选择对应候选。')
            payload['steps'].append({'state': state, 'reference_id': self.candidate.currentData(),
                                     'cooldown_seconds': self.period.value()})
            project_attack_state_sequence(payload)
            self.editor.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
        except (ValueError, TypeError) as error:
            self.status.setText(str(error))

    def calculate(self):
        try:
            result = project_attack_state_sequence(self.current_query())
        except (ValueError, TypeError) as error:
            self._result = None
            self.result_view.clear()
            self.status.setText(str(error))
            return
        self._result = result
        self.result_view.setPlainText(format_attack_state_sequence(result))
        self.status.setText('已计算声明路径的状态门与等待分项；实际攻击时钟仍未知。')
        self.resultReady.emit(deepcopy(result))

    def result_snapshot(self):
        return deepcopy(self._result)

    def set_context(self, scenario):
        """Host selection only changes selectors; never replaces edited rows."""
        operator = scenario.get('operator') if type(scenario) is dict else None
        index = self.operator.findData(operator)
        if index >= 0:
            self.operator.setCurrentIndex(index)
        elif operator is not None:
            self.status.setText('当前干员没有此三段状态门原件；声明编辑与已计算结果保留。')
