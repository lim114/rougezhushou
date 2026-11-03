"""Isolated HP original-value declarations and independent post-ratio input."""
from copy import deepcopy
import json
import re

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QCheckBox, QPlainTextEdit)

from rouge.recipient_native_ratio import (OPERATORS, public_recipient_ratio_payload,
    recipient_native_ratio_diagnostic, format_recipient_ratio_diagnostic)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('JSON字段重复：' + key)
        result[key] = value
    return result


def _integer_text(value, label):
    if re.fullmatch(r'[0-9]+', value) is None or len(value) > 19:
        raise ValueError(label + '需要限定长度的非负整数原文。')
    return int(value)


class RecipientNativeRatioPanel(QWidget):
    resultReady = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result = None
        layout = QVBoxLayout(self)
        self.notice = QLabel('先填写HP/最大HP的整数或FP原值和证据。Clamp01方法体仍缺，分商不自动成为后置比例；独立明示后置原值才显示其资格参数。')
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        toolbar = QHBoxLayout()
        self.operator = QComboBox()
        for identity, name in zip(OPERATORS, ('古米', '黍', '苏苏洛')):
            self.operator.addItem(name, identity)
        self.load_template = QPushButton('载入公开原值算术参考')
        toolbar.addWidget(self.operator, 1)
        toolbar.addWidget(self.load_template)
        layout.addLayout(toolbar)
        values = QHBoxLayout()
        self.label = QLineEdit('新原值观察')
        self.hp = QLineEdit('49999')
        self.maximum = QLineEdit('100000')
        self.unit = QComboBox()
        self.unit.addItem('整数HP声明', 'integer_hp')
        self.unit.addItem('FP32.32原值声明', 'fp_raw')
        for widget in (self.label, self.hp, self.maximum, self.unit):
            values.addWidget(widget)
        layout.addLayout(values)
        self.label.setAccessibleName('新原值观察标签')
        self.hp.setAccessibleName('声明当前HP整数或原值')
        self.maximum.setAccessibleName('声明最大HP整数或原值')
        evidence = QHBoxLayout()
        self.evidence_kind = QComboBox()
        for key, name in [('formula_reference', '公式参考'), ('public_case', '公开算例声明'),
                          ('game_panel_declaration', '游戏面板声明（未核验）')]:
            self.evidence_kind.addItem(name, key)
        self.evidence_source = QLineEdit('调用方新填的整数HP参考；非游戏内部采样')
        self.post_known = QCheckBox('独立明示后置比例原值')
        self.post_raw = QLineEdit('0')
        self.post_raw.setEnabled(False)
        self.post_raw.setAccessibleName('独立声明的后置比例FP原值')
        evidence.addWidget(self.evidence_kind)
        evidence.addWidget(self.evidence_source, 1)
        evidence.addWidget(self.post_known)
        evidence.addWidget(self.post_raw)
        layout.addLayout(evidence)
        self.append_observation = QPushButton('将这项原值与来源追加到声明')
        layout.addWidget(self.append_observation)
        self.editor = QPlainTextEdit()
        self.editor.setAccessibleName('受疗原值观察与培养JSON')
        layout.addWidget(self.editor, 1)
        self.calculate_button = QPushButton('计算原生分商、严格门与观察变化')
        layout.addWidget(self.calculate_button)
        self.status = QLabel('载入参考或填写声明后计算。')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.result_view = QPlainTextEdit()
        self.result_view.setReadOnly(True)
        self.result_view.setAccessibleName('分商阶段与独立后置资格结果')
        layout.addWidget(self.result_view, 1)
        self.load_template.clicked.connect(self._load_template)
        self.append_observation.clicked.connect(self._append)
        self.calculate_button.clicked.connect(self.calculate)
        self.editor.textChanged.connect(self._edited)
        self.post_known.toggled.connect(self.post_raw.setEnabled)

    def current_query(self):
        try:
            return json.loads(self.editor.toPlainText(), object_pairs_hook=_unique_pairs,
                parse_constant=lambda name: (_ for _ in ()).throw(ValueError('JSON需要有限声明：' + name)))
        except json.JSONDecodeError as error:
            raise ValueError('声明JSON格式错误：' + str(error)) from None

    def _edited(self):
        self._result = None
        self.result_view.clear()
        self.status.setText('原值声明已编辑；重新计算后显示结果。')

    def _load_template(self):
        payload = public_recipient_ratio_payload(self.operator.currentData())
        self.editor.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))

    def _append(self):
        try:
            payload = self.current_query()
            recipient_native_ratio_diagnostic(payload)
            if payload['operator'] != self.operator.currentData():
                raise ValueError('追加原值的干员与编辑中的培养作用域不符。')
            payload['observations'].append({'label': self.label.text(),
                'hp': _integer_text(self.hp.text(), '当前HP'),
                'max_hp': _integer_text(self.maximum.text(), '最大HP'), 'unit': self.unit.currentData(),
                'post_clamp_ratio_raw': _integer_text(self.post_raw.text(), '后置原值') if self.post_known.isChecked() else None,
                'evidence': {'kind': self.evidence_kind.currentData(), 'source': self.evidence_source.text()}})
            recipient_native_ratio_diagnostic(payload)
            self.editor.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
        except (ValueError, TypeError) as error:
            self.status.setText(str(error))

    def calculate(self):
        try:
            result = recipient_native_ratio_diagnostic(self.current_query())
        except (ValueError, TypeError) as error:
            self._result = None
            self.result_view.clear()
            self.status.setText(str(error))
            return
        self._result = result
        self.result_view.setPlainText(format_recipient_ratio_diagnostic(result))
        self.status.setText('已计算声明分商与独立后置门参考；实际get_hpRatio和受疗资格仍未知。' if result['source_available'] else
                            '固定原件派生包不可用；分商和资格数值保持未知。')
        self.resultReady.emit(deepcopy(result))

    def result_snapshot(self):
        return deepcopy(self._result)

    def set_context(self, scenario):
        identity = scenario.get('operator') if type(scenario) is dict else None
        index = self.operator.findData(identity)
        if index >= 0:
            self.operator.setCurrentIndex(index)
        self.notice.setText('当前情景仅更新干员选择；已填HP、原值来源和后置比例声明保留。整数面板声明不证明内部原值；实际Clamp01与受疗资格仍未知。')
