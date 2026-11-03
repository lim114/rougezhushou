"""Isolated Qt event-ledger calibration; only explicit actions change inputs."""
from copy import deepcopy
import html
import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QTextBrowser, QComboBox, QDoubleSpinBox, QTabWidget, QSplitter)

from .timing_calibration import LABELS, timing_reference, compare_timing_observation, public_timing_payload


KINDS = {'game_timing': '调用方独立声明的游戏时刻记录', 'public_case': '调用方声明的公开算例',
         'formula_reference': '公式参考时钟账本'}
REASONS = {
    'not_declared_first_readiness_after_deployment': '未明确为部署后的首次就绪',
    'manual_activation_wait_not_sp_readiness': '手动开启等待独立于技力就绪',
    'native_first_release_binding_unknown': '原生首次释放/命中绑定未知',
    'native_release_sequence_unknown': '原生释放/命中序列未知',
    'nominal_parameter_does_not_bind_actual_end': '名义持续不证明实际结束',
    'native_unblocking_phase_unknown': '原生解除阻回相位未知',
    'different_origin_from_model_recharge': '解除阻回起点与模型回转起点不同',
    'observed_charge_requirement_not_declared_compatible': '预存/部分充能或需求未明确匹配模型',
    'existing_model_clock_unknown': '现有模型时钟未知',
    'nonconsecutive_or_different_release_source': '非连续本体释放记录或模型间隔变化',
    'includes_separate_activation_wait': '含下次开启等待，不能当回转周期',
}


def _text(value, signed=False):
    if value is None:
        return '未知'
    if isinstance(value, bool):
        return '是' if value else '否'
    if isinstance(value, (int, float)):
        return format(value, '+.10g' if signed else '.10g')
    return str(value)


def _esc(value):
    return html.escape(_text(value))


def _table(headers, rows):
    return ('<table border="1" cellspacing="0" cellpadding="5"><tr>' +
        ''.join('<th>' + _esc(h) + '</th>' for h in headers) + '</tr>' +
        ''.join('<tr>' + ''.join('<td>' + _esc(value) + '</td>' for value in row) + '</tr>' for row in rows) + '</table>')


def timing_calibration_html(result):
    reference = result['reference']
    clock = result['clock']
    parts = ['<html><body><h2>首批三人技能事件与回转成对核对</h2>',
        '<p>干员：' + _esc(result['operator']) + '；技能：' + _esc(result['skill_name']) + '</p>',
        '<p>来源类别：' + _esc(KINDS[result['evidence_kind']]) + '；来源：' + _esc(result['source']) + '</p>',
        '<p>记录时钟：' + _esc(clock['id']) + '；单位：' + _esc(clock['unit']) +
        '；视频FPS：' + _esc(clock['fps']) + '；部署坐标：' + _esc(clock['origin_stamp']) + '</p>',
        '<p>视频帧仅按声明FPS换秒；模型自身的时序模式与30Hz条件预览独立保留。未认证实机或原生时钟。</p>',
        '<p>秒数容差：' + _esc(result['tolerance_seconds']) + '；可比较条件时差：' +
        str(result['compared_conditional_clock_count']) + '；其中超出容差：' + str(result['mismatching_conditional_clock_count']) + '</p>',
        '<h3>记录时差与同口径条件参考</h3>']
    parts.append(_table(['周期', '时差口径', '独立观察/秒', '条件参考/秒', '观察减参考/秒',
        '在声明容差内', '原生参考/秒', '未知或不同比较口径'], [
            [row['cycle_id'], row['label'], row['observed_seconds'], row['conditional_reference_seconds'],
             _text(row['observed_minus_conditional_reference'], True), row['matches_declared_tolerance'],
             row['actual_native_reference_seconds'], REASONS.get(row['reference_unavailable_reason'], '')]
            for row in result['comparisons']]))
    parts.append('<h3>连续记录间隔</h3>')
    if result['release_interval_rows']:
        parts.append(_table(['周期', '记录序号', '观察间隔/秒', '已有条件间隔/秒', '观察减参考/秒'], [
            [r['cycle_id'], r['recorded_interval_index'], r['observed_seconds'],
             r['conditional_reference_seconds'], _text(r['observed_minus_conditional_reference'], True)]
            for r in result['release_interval_rows']]))
    else:
        parts.append('<p>未录入至少两个释放/命中时刻；不生成首末时刻或间隔。</p>')
    parts.append('<h3>重复开启与下次就绪分别记录</h3>')
    if result['repeat_cycle_rows']:
        parts.append(_table(['前周期→后周期', '相邻两次开启间隔/秒', '前期开启→下次就绪/秒',
            '下次就绪→后期开启/秒', '模型相邻开启预测'], [
                [r['previous_cycle_id'] + '→' + r['cycle_id'], r['observed_seconds'],
                 r['previous_start_to_next_ready_seconds'], r['next_ready_to_current_start_seconds'],
                 r['actual_native_reference_seconds']] for r in result['repeat_cycle_rows']]))
    parts.append(_table(['重复分项', '已记录个数', '最短/秒', '最长/秒', '范围/秒', '均值/秒'], [
        [label, summary['recorded_count'], summary['minimum_seconds'], summary['maximum_seconds'],
         summary['range_seconds'], summary['mean_seconds']]
        for label, summary in [*[(LABELS[key], value) for key, value in result['variation'].items()],
                               ('相邻开启间隔', result['repeat_variation']), ('释放/命中间隔', result['release_interval_variation'])]]))
    speed = result['attack_speed_comparison']
    parts.append('<h3>独立攻速属性与名义参数</h3>')
    parts.append(_table(['分项', '声明观察', '已有条件参考'], [
        ['技能攻速属性', speed['observed_attribute'], speed['conditional_reference_attribute']],
        ['原表固定持续参数/秒', None, reference['source_duration_parameter_seconds']],
        ['模型持续估计/秒', None, reference['model_duration_reference_seconds']],
        ['名义间隔/秒', None, reference['nominal_interval_reference_seconds']],
        ['同本体已有条件间隔/秒', None, reference['body_interval_conditional_reference_seconds']],
        ['实际结束时钟/秒', None, reference['actual_end_seconds']],
        ['实际解除阻回时钟/秒', None, reference['actual_unblocked_seconds']]]))
    parts.append('<p>攻速观察减参考：' + _esc(_text(speed['observed_minus_reference'], True)) + '。' + _esc(speed['note']) + '</p>')
    parts.extend('<p>警告：' + _esc(note) + '</p>' for note in result['warnings'])
    parts.extend('<p>' + _esc(note) + '</p>' for note in [*reference['notes'], *result['notes']])
    parts.append('</body></html>')
    return ''.join(parts)


class TimingCalibrationPanel(QWidget):
    resultReady = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scenario = None
        self._result = None
        layout = QVBoxLayout(self)
        self.notice = QLabel('分别填写条件与独立时刻来源。各事件使用相同时钟，未知填null；就绪、开启、释放/命中、结束及解除阻回分别记录，不以名义参数补观察。')
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        templates = QHBoxLayout()
        self.template = QComboBox()
        for key, name in (('kaltsit', '凯尔希一技能公式时钟'), ('silverash', '凛御银灰三技能公式时钟'), ('mechanist', '机械师三技能公式时钟')):
            self.template.addItem(name, key)
        self.load_template = QPushButton('载入选中公式参考')
        templates.addWidget(self.template, 1)
        templates.addWidget(self.load_template)
        layout.addLayout(templates)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(self.splitter, 1)
        inputs = QWidget()
        input_layout = QVBoxLayout(inputs)
        input_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs = QTabWidget()
        self.scenario_editor, self.observation_editor = QPlainTextEdit(), QPlainTextEdit()
        self.scenario_editor.setAccessibleName('独立技能时钟校准条件JSON')
        self.observation_editor.setAccessibleName('独立事件时刻与来源JSON')
        self.tabs.addTab(self.scenario_editor, '声明条件')
        self.tabs.addTab(self.observation_editor, '独立时刻记录')
        input_layout.addWidget(self.tabs, 1)
        actions = QHBoxLayout()
        self.reference_button = QPushButton('读取条件参考与标识')
        self.bind_button = QPushButton('确认记录条件并填写标识')
        self.import_button = QPushButton('显式导入当前干员条件')
        self.import_button.setEnabled(False)
        for button in (self.reference_button, self.bind_button, self.import_button):
            actions.addWidget(button)
        input_layout.addLayout(actions)
        self.reference_view = QPlainTextEdit()
        self.reference_view.setReadOnly(True)
        self.reference_view.setMaximumHeight(150)
        self.reference_view.hide()
        input_layout.addWidget(self.reference_view)
        self.splitter.addWidget(inputs)
        outputs = QWidget()
        output_layout = QVBoxLayout(outputs)
        output_layout.setContentsMargins(0, 0, 0, 0)
        controls = QHBoxLayout()
        controls.addWidget(QLabel('秒数容差'))
        self.tolerance = QDoubleSpinBox()
        self.tolerance.setRange(0, 1000000)
        self.tolerance.setDecimals(6)
        controls.addWidget(self.tolerance)
        self.run_button = QPushButton('计算记录时差与成对对照')
        controls.addWidget(self.run_button, 1)
        output_layout.addLayout(controls)
        self.status = QLabel('等待独立记录。')
        self.status.setWordWrap(True)
        output_layout.addWidget(self.status)
        self.result_view = QTextBrowser()
        self.result_view.setOpenExternalLinks(False)
        output_layout.addWidget(self.result_view, 1)
        self.splitter.addWidget(outputs)
        self.splitter.setSizes([320, 480])
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.load_template.clicked.connect(self.load_public_template)
        self.reference_button.clicked.connect(self.inspect)
        self.bind_button.clicked.connect(self.bind_context)
        self.import_button.clicked.connect(self.import_scenario)
        self.run_button.clicked.connect(self.execute)
        self.scenario_editor.textChanged.connect(self.invalidate)
        self.observation_editor.textChanged.connect(self.invalidate)
        self.tolerance.valueChanged.connect(self.invalidate)
        self.load_public_template()

    @staticmethod
    def _parse(editor, name):
        value = json.loads(editor.toPlainText())
        if not isinstance(value, dict):
            raise ValueError(name + '需为JSON对象。')
        return value

    @staticmethod
    def _write(editor, value):
        editor.setPlainText(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))

    def invalidate(self, *_):
        self._result = None
        self.result_view.clear()
        self.status.setText('条件或独立记录已修改，请重新计算。')

    def load_public_template(self):
        payload = public_timing_payload(self.template.currentData())
        self._write(self.scenario_editor, payload['scenario'])
        self._write(self.observation_editor, payload['observation'])
        self.tolerance.setValue(payload['tolerance_seconds'])
        self.reference_view.clear()
        self.reference_view.hide()
        self.status.setText('已显式载入字面量公式参考；有意分别声明首次等待2秒、第二次等待3秒，未提供首末释放与解除阻回。')

    def set_scenario(self, scenario):
        self._scenario = deepcopy(scenario)
        self.import_button.setEnabled(isinstance(scenario, dict) and scenario.get('operator') in ('kaltsit', 'silverash', 'mechanist'))

    def inspect(self):
        try:
            reference = timing_reference(self._parse(self.scenario_editor, '条件'))
            self.reference_view.setPlainText(json.dumps(reference, ensure_ascii=False, indent=2, allow_nan=False))
            self.reference_view.show()
            self.status.setText('条件参考已读取；独立观察时刻和来源均保持原填写内容。')
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText('条件参考读取失败：' + str(error))

    def bind_context(self):
        try:
            reference = timing_reference(self._parse(self.scenario_editor, '条件'))
            observation = self._parse(self.observation_editor, '记录')
            observation['context_token'] = reference['context_token']
            self._write(self.observation_editor, observation)
            self.status.setText('条件标识由显式声明填写；干员/技能身份、时钟、来源及事件时刻未改动，仍需分别核对。')
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText('标识填写失败：' + str(error))

    def import_scenario(self):
        if self._scenario is None:
            self.status.setText('没有可导入的当前干员条件。')
            return
        self._write(self.scenario_editor, deepcopy(self._scenario))
        self.status.setText('当前条件已显式导入；独立记录未改动，需核对条件标识及技能身份。')

    def execute(self):
        self.invalidate()
        try:
            result = compare_timing_observation(self._parse(self.scenario_editor, '条件'),
                self._parse(self.observation_editor, '独立记录'), self.tolerance.value())
            rendered = timing_calibration_html(result)
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText('未完成时钟对照：' + str(error))
            return
        self._result = deepcopy(result)
        self.result_view.setHtml(rendered)
        self.status.setText('已测量 ' + str(len(result['cycles'])) + ' 个记录周期；' +
            str(result['compared_conditional_clock_count']) + ' 个同口径条件时差可比较，原生相位未知仍保留。')
        self.resultReady.emit(deepcopy(result))

    def result_snapshot(self):
        return deepcopy(self._result)
