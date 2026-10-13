"""A controlled-record workspace; hypothesis diagnostics never correct state."""
from copy import deepcopy
import html
import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QTextBrowser, QComboBox, QTabWidget, QSplitter)

from .calibration_experiment import calibration_experiment, public_experiment_payload


STATES = {'blocked': '被阻断', 'evaluable': '可检验', 'contradicted': '声明范围矛盾',
    'compatible': '共同残差假设仍相容', 'compatible_on_declared_ranges': '仅在声明范围内相容',
    'record_blocked': '留出记录被阻断', 'training_unavailable': '训练假设不可用',
    'no_overlap': '无重叠', 'all_training_candidates_allowed': '全部训练候选被留出范围允许',
    'possible_overlap_only': '仅部分训练候选与留出重叠'}
REASONS = {'operator_identity_mismatch': '干员身份不同', 'undeclared_control_change': '未声明允许的控制变量变化',
    'evidence_kind_mismatch': '证据类别不同', 'caller_evidence_version_mismatch': '来源版本声明不同',
    'selected_field_not_recorded': '所选字段未记录', 'existing_model_field_unknown': '模型字段未知',
    'selected_cycle_or_interval_not_recorded': '所选周期/间隔未记录', 'selected_measurement_unknown': '观察界限未知',
    'existing_model_clock_or_matching_definition_unknown': '模型时钟或匹配口径未知', 'record_validation_error': '记录校验失败'}
KINDS = {'formula_reference': '公式参考', 'public_case': '调用方声明的公开算例',
         'game_panel': '调用方声明的游戏面板', 'game_timing': '调用方声明的游戏时刻'}


def _text(value):
    if value is None:
        return '未知'
    if isinstance(value, bool):
        return '是' if value else '否'
    if isinstance(value, (int, float)):
        return format(value, '.10g')
    if isinstance(value, dict) and 'lower_inclusive' in value:
        lo, hi = _text(value['lower']), _text(value['upper'])
        if value['lower_exact'] != value['upper_exact'] and lo == hi:
            lo, hi = value['lower_exact'], value['upper_exact']
        return ('[' if value['lower_inclusive'] else '(') + lo + ', ' + hi + (']' if value['upper_inclusive'] else ')')
    return str(value)


def _esc(value):
    return html.escape(_text(value))


def _table(headers, rows):
    return '<table border="1" cellspacing="0" cellpadding="5"><tr>' + ''.join('<th>' + _esc(h) + '</th>' for h in headers) + '</tr>' + ''.join('<tr>' + ''.join('<td>' + _esc(v) + '</td>' for v in row) + '</tr>' for row in rows) + '</table>'


def experiment_html(result):
    parts = ['<html><body><h2>多记录实验共同残差假设与留出复核</h2>',
        '<p>干员：' + _esc(result['operator']) + '；通道：' + _esc(result['channel_label']) + '</p>',
        '<p>来源类别：' + _esc(KINDS[result['evidence_kind']]) + '</p>',
        '<p>假设：同一加性残差b；没有拟合或回写修正。来源版本：' + _esc(result['evidence_version']) + '（调用方声明）。</p>',
        '<p>允许变化条件：' + _esc('、'.join(result['varying_fields']) or '无') + '；其他条件逐样本核对。</p>',
        '<p>训练结论：' + STATES[result['training_state']] + '；共同b范围：' + _esc(result['training_hypothesis_range']) + '</p>',
        '<p>全记录结论：' + STATES[result['overall_state']] + '；共同范围：' + _esc(result['overall_hypothesis_range']) + '</p>',
        '<h3>独立记录与控制变量</h3>']
    parts.append(_table(['记录', '角色', '观察界限', '模型参考', '残差界限', '状态', '阻断原因', '同条件重复'], [
        [r['id'], '训练' if r['role'] == 'training' else '留出', r['observed_interval'], r['model_reference'],
         r['residual_interval'], STATES[r['state']], '；'.join(REASONS.get(reason, reason) for reason in r['blocking_reasons']),
         '、'.join(r['same_context_repeat_ids']) or '无'] for r in result['records']]))
    for record in result['records']:
        parts.append('<p>' + _esc(record['id']) + '来源：' + _esc(record['source']) + '；版本声明：' + _esc(record['evidence_version']) + '</p>')
        if record['changed_controls']:
            parts.append(_table(['记录条件变化', '控制声明', '样本声明', '允许变化'], [
                [r['field'], json.dumps(r['control'], ensure_ascii=False) if r['control_present'] else '未声明',
                 json.dumps(r['record'], ensure_ascii=False) if r['record_present'] else '未声明', r['allowed_to_vary']]
                for r in record['changed_controls']]))
        if record.get('validation_error'):
            parts.append('<p>记录校验：' + _esc(record['validation_error']) + '</p>')
    parts.append('<h3>留出复核</h3>')
    if result['held_out_checks']:
        parts.append(_table(['留出记录', '训练候选范围', '留出残差范围', '复核后剩余范围', '结论'], [
            [r['record_id'], r['allowed_training_residual_range'], r['held_out_residual_range'],
             r['remaining_hypothesis_range'], STATES[r['state']]] for r in result['held_out_checks']]))
    else:
        parts.append('<p>尚未提供留出记录；不能把训练相容当成留出验收。</p>')
    parts.append('<h3>两记录矛盾见证</h3>')
    witnesses = [result['training_contradiction_witness'], result['overall_contradiction_witness'],
                 *[r['contradiction_witness'] for r in result['held_out_checks']]]
    seen = set()
    for witness in witnesses:
        if witness is None or tuple(witness['record_ids']) in seen:
            continue
        seen.add(tuple(witness['record_ids']))
        parts.append('<p>记录 ' + _esc(' ↔ '.join(witness['record_ids'])) + ' 无共同b：' +
                     _esc(witness['lower_witness_residual']) + ' 与 ' + _esc(witness['upper_witness_residual']) + '。</p>')
    if not seen:
        parts.append('<p>没有可报告的两记录矛盾；被阻断的记录不能按通过处理。</p>')
    parts.extend('<p>' + _esc(note) + '</p>' for note in result['notes'])
    parts.append('<p>原生认证：否；引擎修正：未知且未生成；实际偏差原因：未知。</p></body></html>')
    return ''.join(parts)


class CalibrationExperimentPanel(QWidget):
    resultReady = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scenario = None
        self._result = None
        self._record_id = None
        self._record_drafts = {}
        self._loading_record = False
        layout = QVBoxLayout(self)
        notice = QLabel('明示控制变量、证据类别与来源版本；训练样本求共同残差b的允许范围，留出样本独立复核。范围相容不证明机制，也不修正引擎。')
        notice.setWordWrap(True)
        layout.addWidget(notice)
        templates = QHBoxLayout()
        self.operator, self.channel, self.variant = QComboBox(), QComboBox(), QComboBox()
        for key, name in (('mechanist', '机械师'), ('kaltsit', '凯尔希·思衡托'), ('silverash', '凛御银灰')):
            self.operator.addItem(name, key)
        for key, name in (('panel', '三等级培养攻击实验'), ('timing', '三技能初动实验')):
            self.channel.addItem(name, key)
        for key, name in (('compatible', '共同假设相容'), ('held_out_conflict', '留出反例'), ('control_drift', '未允许的控制变化')):
            self.variant.addItem(name, key)
        self.load_template = QPushButton('显式载入公式实验')
        for widget in (self.operator, self.channel, self.variant, self.load_template):
            templates.addWidget(widget)
        layout.addLayout(templates)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(self.splitter, 1)
        inputs = QWidget()
        input_layout = QVBoxLayout(inputs)
        input_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs = QTabWidget()
        self.editor = QPlainTextEdit()
        self.editor.setAccessibleName('完整实验与独立记录JSON')
        self.tabs.addTab(self.editor, '实验总表')
        record_page = QWidget()
        record_layout = QVBoxLayout(record_page)
        record_layout.setContentsMargins(0, 0, 0, 0)
        selection = QHBoxLayout()
        self.record_choice, self.role_choice = QComboBox(), QComboBox()
        self.role_choice.addItem('训练记录', 'training')
        self.role_choice.addItem('留出记录', 'held_out')
        self.reload_records_button = QPushButton('读取当前样本列表')
        self.apply_role_button = QPushButton('明确设置所选角色')
        for widget in (self.record_choice, self.role_choice, self.reload_records_button, self.apply_role_button):
            selection.addWidget(widget)
        record_layout.addLayout(selection)
        self.record_editor = QPlainTextEdit()
        self.record_editor.setAccessibleName('选中独立记录草稿JSON')
        record_layout.addWidget(self.record_editor, 1)
        actions = QHBoxLayout()
        self.save_record_button = QPushButton('将选中草稿保存到实验总表')
        self.bind_button = QPushButton('确认所选记录条件并填写标识')
        self.import_button = QPushButton('显式导入当前条件到所选记录')
        self.import_button.setEnabled(False)
        for button in (self.save_record_button, self.bind_button, self.import_button):
            actions.addWidget(button)
        record_layout.addLayout(actions)
        self.tabs.addTab(record_page, '独立样本编辑')
        input_layout.addWidget(self.tabs, 1)
        self.splitter.addWidget(inputs)
        outputs = QWidget()
        output_layout = QVBoxLayout(outputs)
        output_layout.setContentsMargins(0, 0, 0, 0)
        actions = QHBoxLayout()
        self.run_button = QPushButton('检验共同假设与留出记录')
        self.witness_choice = QComboBox()
        self.locate_witness_button = QPushButton('定位矛盾见证记录')
        self.locate_witness_button.setEnabled(False)
        actions.addWidget(self.run_button, 1)
        actions.addWidget(self.witness_choice)
        actions.addWidget(self.locate_witness_button)
        output_layout.addLayout(actions)
        self.status = QLabel('等待独立实验声明。')
        self.status.setWordWrap(True)
        output_layout.addWidget(self.status)
        self.result_view = QTextBrowser()
        self.result_view.setOpenExternalLinks(False)
        output_layout.addWidget(self.result_view, 1)
        self.splitter.addWidget(outputs)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.splitter.setSizes([350, 500])
        self.editor.textChanged.connect(self.invalidate)
        self.record_editor.textChanged.connect(self.store_record_draft)
        self.record_choice.currentIndexChanged.connect(self.show_record)
        self.load_template.clicked.connect(self.load_public_template)
        self.reload_records_button.clicked.connect(self.reload_records)
        self.save_record_button.clicked.connect(self.save_record)
        self.apply_role_button.clicked.connect(self.apply_role)
        self.bind_button.clicked.connect(self.bind_record)
        self.import_button.clicked.connect(self.import_scenario)
        self.run_button.clicked.connect(self.execute)
        self.locate_witness_button.clicked.connect(self.locate_witness)
        self.load_public_template()

    @staticmethod
    def _parse(editor):
        value = json.loads(editor.toPlainText())
        if not isinstance(value, dict):
            raise ValueError('需为JSON对象。')
        return value

    @staticmethod
    def _write(editor, value):
        editor.setPlainText(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))

    def invalidate(self, *_):
        self._result = None
        self.result_view.clear()
        self.witness_choice.clear()
        self.locate_witness_button.setEnabled(False)
        self.status.setText('实验总表已修改，请重新检验；未保存的独立草稿不进入计算。')

    def store_record_draft(self):
        if not self._loading_record and self._record_id:
            self._record_drafts[self._record_id] = self.record_editor.toPlainText()

    def load_public_template(self):
        payload = public_experiment_payload(self.operator.currentData(), self.channel.currentData(), self.variant.currentData())
        self._record_id = None
        self._record_drafts.clear()
        self._write(self.editor, payload)
        self.reload_records()
        self.status.setText('已显式载入字面量公式实验；声明+5属性或+2秒只为共同残差假设演示，不是游戏观测或修正量。')

    def reload_records(self):
        try:
            payload = self._parse(self.editor)
            records = payload['experiment']['records']
            selected = self._record_id
            self.record_choice.blockSignals(True)
            self.record_choice.clear()
            for record in records:
                self.record_choice.addItem(record['id'] + ' · ' + ('训练' if record['role'] == 'training' else '留出'), record['id'])
            index = self.record_choice.findData(selected)
            self.record_choice.setCurrentIndex(max(0, index))
            self.record_choice.blockSignals(False)
            self.show_record()
        except (ValueError, TypeError, KeyError, IndexError) as error:
            self.record_choice.blockSignals(False)
            self.status.setText('样本列表读取失败：' + str(error))

    def show_record(self, *_):
        key = self.record_choice.currentData()
        if key is None:
            return
        try:
            records = self._parse(self.editor)['experiment']['records']
            record = next(r for r in records if r['id'] == key)
            self._record_id = key
            self._loading_record = True
            if key in self._record_drafts:
                self.record_editor.setPlainText(self._record_drafts[key])
            else:
                self._write(self.record_editor, record)
            self._loading_record = False
            self.role_choice.setCurrentIndex(self.role_choice.findData(record['role']))
        except (ValueError, TypeError, KeyError, IndexError, StopIteration) as error:
            self._loading_record = False
            self.status.setText('样本读取失败：' + str(error))

    def save_record(self):
        try:
            payload = self._parse(self.editor)
            record = self._parse(self.record_editor)
            old_id = self._record_id
            records = payload['experiment']['records']
            index = next(i for i, r in enumerate(records) if r['id'] == old_id)
            if not isinstance(record.get('id'), str) or not record['id'].strip() or any(r['id'] == record['id'] for i, r in enumerate(records) if i != index):
                raise ValueError('保存的记录ID需唯一非空。')
            records[index] = record
            self._record_drafts.pop(old_id, None)
            self._record_id = record['id']
            self._write(self.editor, payload)
            self.reload_records()
            self.status.setText('所选独立草稿已显式保存；来源与界限按填写内容保留，请重新检验。')
        except (ValueError, TypeError, KeyError, IndexError, StopIteration) as error:
            self.status.setText('样本保存失败：' + str(error))

    def apply_role(self):
        try:
            record = self._parse(self.record_editor)
            record['role'] = self.role_choice.currentData()
            self._write(self.record_editor, record)
            self.save_record()
        except (ValueError, TypeError, KeyError, IndexError) as error:
            self.status.setText('角色设置失败：' + str(error))

    def set_scenario(self, scenario):
        self._scenario = deepcopy(scenario)
        self.import_button.setEnabled(isinstance(scenario, dict) and scenario.get('operator') in ('kaltsit', 'silverash', 'mechanist'))

    def import_scenario(self):
        try:
            if self._scenario is None:
                raise ValueError('没有可导入的条件。')
            record = self._parse(self.record_editor)
            record['data']['scenario'] = deepcopy(self._scenario)
            self._write(self.record_editor, record)
            self.status.setText('当前条件已显式导入所选草稿；独立观察与来源未改动，保存前须核对标识和控制变量。')
        except (ValueError, TypeError, KeyError, IndexError) as error:
            self.status.setText('导入失败：' + str(error))

    def bind_record(self):
        from .calibration import panel_layers
        try:
            record = self._parse(self.record_editor)
            record['data']['observation']['context_token'] = panel_layers(record['data']['scenario'])['context_token']
            self._write(self.record_editor, record)
            self.status.setText('所选草稿标识已显式声明；界限、来源、版本、干员/技能身份均未改动，请保存后检验。')
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText('标识填写失败：' + str(error))

    def execute(self):
        self.invalidate()
        try:
            result = calibration_experiment(**self._parse(self.editor))
            rendered = experiment_html(result)
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText('未完成实验检验：' + str(error))
            return
        self._result = deepcopy(result)
        self.result_view.setHtml(rendered)
        self.reload_records()
        witness_ids = []
        for witness in [result['training_contradiction_witness'], result['overall_contradiction_witness'], *[r['contradiction_witness'] for r in result['held_out_checks']]]:
            if witness:
                witness_ids.extend(key for key in witness['record_ids'] if key not in witness_ids)
        for key in witness_ids:
            self.witness_choice.addItem(key, key)
        self.locate_witness_button.setEnabled(bool(witness_ids))
        pending = '；有' + str(len(self._record_drafts)) + '条未保存草稿，本次仅检验总表' if self._record_drafts else ''
        self.status.setText('实验结论：' + STATES[result['overall_state']] + '；共同b仅为声明假设，未修正引擎或认证实机' + pending + '。')
        self.resultReady.emit(deepcopy(result))

    def locate_witness(self):
        key = self.witness_choice.currentData()
        index = self.record_choice.findData(key)
        if index >= 0:
            self.record_choice.setCurrentIndex(index)
            self.tabs.setCurrentIndex(1)

    def result_snapshot(self):
        return deepcopy(self._result)
