"""Public precision declarations and order inspection, with no run writes."""
from copy import deepcopy
import json

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QPlainTextEdit)

from .relic_order_precision import (IDS, supported_precision_sources, diagnose_relic_processing_order,
    public_relic_order_payload, format_relic_processing_order)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('JSON字段重复：' + key)
        result[key] = value
    return result


class RelicOrderPrecisionPanel(QWidget):
    resultReady = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result = None
        layout = QVBoxLayout(self)
        self.notice = QLabel('检查六件固定来源的声明处理顺序、单精度逐步结果与十进制模型差。物理和法术分别计算；枚举计数不是概率，实际获取顺序和最终伤害未知。')
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        bar = QHBoxLayout()
        self.template = QComboBox()
        for key, name in [('magic', '三件法术来源'), ('physical', '三件物理来源'), ('both', '全部六件来源')]:
            self.template.addItem(name, key)
        self.load_template = QPushButton('载入公开精度示例')
        bar.addWidget(self.template, 1)
        bar.addWidget(self.load_template)
        layout.addLayout(bar)
        constraints = QHBoxLayout()
        self.before = QComboBox()
        self.after = QComboBox()
        names = {r['relic_id']: r['name'] for r in supported_precision_sources()}
        for identity in IDS:
            self.before.addItem(names.get(identity, identity), identity)
            self.after.addItem(names.get(identity, identity), identity)
        self.after.setCurrentIndex(1)
        self.add_constraint = QPushButton('明确添加先后约束')
        constraints.addWidget(self.before, 1)
        constraints.addWidget(QLabel('先于'))
        constraints.addWidget(self.after, 1)
        constraints.addWidget(self.add_constraint)
        layout.addLayout(constraints)
        self.editor = QPlainTextEdit()
        self.editor.setAccessibleName('藏品处理顺序与先后约束JSON')
        layout.addWidget(self.editor, 1)
        self.calculate_button = QPushButton('枚举接受顺序与精度范围')
        layout.addWidget(self.calculate_button)
        self.status = QLabel('选择示例或填写声明后计算。')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.result_view = QPlainTextEdit()
        self.result_view.setReadOnly(True)
        self.result_view.setAccessibleName('藏品单精度范围与模型差')
        layout.addWidget(self.result_view, 1)
        inspect = QHBoxLayout()
        self.order_selector = QComboBox()
        self.order_selector.setAccessibleName('查看一个可接受处理顺序')
        self.declare_viewed_order = QPushButton('将查看顺序写为明确声明')
        inspect.addWidget(self.order_selector, 1)
        inspect.addWidget(self.declare_viewed_order)
        layout.addLayout(inspect)
        hint = QLabel('选择下方查看对象只用于检查某个排列；点击写入按钮才改变声明，不证明实际游戏顺序。')
        hint.setWordWrap(True)
        layout.addWidget(hint)
        self.order_detail = QPlainTextEdit()
        self.order_detail.setReadOnly(True)
        self.order_detail.setAccessibleName('查看顺序的逐步单精度bit结果')
        layout.addWidget(self.order_detail, 1)
        self.load_template.clicked.connect(self._load_template)
        self.add_constraint.clicked.connect(self._add_constraint)
        self.calculate_button.clicked.connect(self.calculate)
        self.editor.textChanged.connect(self._edited)
        self.order_selector.currentIndexChanged.connect(self._inspect_order)
        self.declare_viewed_order.clicked.connect(self._declare_order)
        self.declare_viewed_order.setEnabled(False)

    def current_query(self):
        try:
            return json.loads(self.editor.toPlainText(), object_pairs_hook=_unique_pairs,
                parse_constant=lambda name: (_ for _ in ()).throw(ValueError('JSON需要有限声明：' + name)))
        except json.JSONDecodeError as error:
            raise ValueError('声明JSON格式错误：' + str(error)) from None

    def _edited(self):
        self._result = None
        self.result_view.clear()
        self.order_selector.clear()
        self.order_detail.clear()
        self.declare_viewed_order.setEnabled(False)
        self.status.setText('声明已编辑；重新计算后显示结果。')

    def _load_template(self):
        payload = public_relic_order_payload(self.template.currentData())
        self.editor.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
        self.before.setCurrentIndex(self.before.findData(payload['relic_ids'][0]))
        self.after.setCurrentIndex(self.after.findData(payload['relic_ids'][1]))

    def _add_constraint(self):
        try:
            payload = self.current_query()
            diagnose_relic_processing_order(payload)
            payload.setdefault('before_constraints', []).append([self.before.currentData(), self.after.currentData()])
            diagnose_relic_processing_order(payload)
            self.editor.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
        except (ValueError, TypeError) as error:
            self.status.setText(str(error))

    def calculate(self):
        try:
            result = diagnose_relic_processing_order(self.current_query())
        except (ValueError, TypeError) as error:
            self._edited()
            self.status.setText(str(error))
            return
        self._result = result
        self.result_view.setPlainText(format_relic_processing_order(result))
        self.order_selector.blockSignals(True)
        self.order_selector.clear()
        sources = {r['relic_id']: r['name'] for r in result['selected_sources'] or []}
        for ordinal, outcome in enumerate(result['order_outcomes'] or [], 1):
            self.order_selector.addItem(str(ordinal) + ' · ' + ' → '.join(sources[i] for i in outcome['order']), outcome['order'])
        if result['declared_processing_order'] is not None:
            for i in range(self.order_selector.count()):
                if self.order_selector.itemData(i) == result['declared_processing_order']:
                    self.order_selector.setCurrentIndex(i)
                    break
        self.order_selector.blockSignals(False)
        self.declare_viewed_order.setEnabled(bool(self.order_selector.count()))
        self._inspect_order()
        self.status.setText('已枚举声明约束下的单精度参数结果；实际顺序与最终FP包未知。' if result['source_available'] else
                            '固定来源包不可用；数值和范围保持未知。')
        self.resultReady.emit(deepcopy(result))

    def _inspect_order(self, *_):
        order = self.order_selector.currentData()
        if self._result is None or order is None:
            self.order_detail.clear()
            return
        payload = deepcopy(self._result['declaration'])
        payload['declared_processing_order'] = order
        inspection = diagnose_relic_processing_order(payload)
        trace = inspection['declared_order_trace']
        lines = ['当前查看的枚举顺序，仅检查计算步骤，尚不改变上方声明：']
        if trace is None:
            lines.append('来源不可用，逐步值未知。')
        else:
            for row in trace['steps']:
                added = '首件直接复制' if row['rounded_addition_f32'] is None else f"加后取单精度{row['rounded_addition_f32']:.17g} / {row['rounded_addition_bits']}"
                lines.append(f"{row['ordinal']}. {row['name']} · {row['prefab_group']}：输入{row['incoming_f32']:.17g} / {row['incoming_bits']}；{added}；"
                    f"结果{row['group_result_f32']:.17g} / {row['group_result_bits']}；相对十进制差{row['f32_minus_exact_decimal_text']}")
        self.order_detail.setPlainText('\n'.join(lines))

    def _declare_order(self):
        order = self.order_selector.currentData()
        if self._result is None or order is None:
            return
        payload = self.current_query()
        payload['declared_processing_order'] = list(order)
        diagnose_relic_processing_order(payload)
        self.editor.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))

    def result_snapshot(self):
        return deepcopy(self._result)

    def set_context(self, scenario):
        if type(scenario) is dict:
            selected = scenario.get('relic_ids', [])
            count = sum(i in IDS for i in selected) if type(selected) is list else 0
            self.notice.setText(f'当前情景包含{count}件此诊断支持的来源。这里只更新提示，编辑中的清单、约束和顺序保留；当前持有清单不能证明实际处理顺序。')
