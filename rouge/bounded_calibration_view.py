"""Explicit bounded panel/clock readings; no inferred measurement precision."""
from copy import deepcopy
import html
import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QTextBrowser, QComboBox, QDoubleSpinBox, QTabWidget, QSplitter, QCheckBox)

from .bounded_calibration import bounded_calibration, public_bounded_payload


STATE_NAMES = {'all_compatible': '所有可行值均相符', 'possible_overlap': '仅可能重叠',
    'no_overlap': '无重叠', 'model_unknown': '模型参考未知', 'measurement_unknown': '观察界限未知'}
KIND_NAMES = {'formula_reference': '公式参考', 'public_case': '调用方声明的公开算例',
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


def bounded_calibration_html(result):
    parts = ['<html><body><h2>首批三人面板与时刻界限成对核对</h2>',
        '<p>界限来自独立录入；不自动猜测视频或四舍五入误差，不视为置信度。所有可行值相符与仅可能重叠分别显示。</p>']
    panel = result['panel']
    if panel is not None:
        parts.extend(['<h3>面板界限与前后差</h3>', '<p>干员：' + _esc(panel['operator']) + '；面板：' + _esc(panel['panel']) + '；来源类别：' + _esc(KIND_NAMES[panel['evidence_kind']]) + '</p>',
            '<p>前组来源：' + _esc(panel['before_source']) + '；后组来源：' + _esc(panel['after_source']) + '</p>',
            '<p>调用方明确容差：' + _esc(panel['tolerance']) + '</p>'])
        parts.append(_table(['属性', '前组界限', '后组界限', '可行后减前', '模型差', '残差界限', '差值比较'], [
            [r['label'], r['before_observed_interval'], r['after_observed_interval'],
             r['observed_after_minus_before_interval'], r['model_after_minus_before'], r['delta_residual_interval'],
             STATE_NAMES[r['classification']]] for r in panel['rows']]))
        parts.append(_table(['属性', '前组绝对残差', '前组绝对比较', '后组绝对残差', '后组绝对比较'], [
            [r['label'], r['before_absolute_residual_interval'], STATE_NAMES[r['before_absolute_classification']],
             r['after_absolute_residual_interval'], STATE_NAMES[r['after_absolute_classification']]] for r in panel['rows']]))
        parts.append('<p>仅前组字段：' + _esc('、'.join(panel['before_only_fields']) or '无') + '；仅后组字段：' + _esc('、'.join(panel['after_only_fields']) or '无') + '。单侧字段不补零。</p>')
    timing = result['timing']
    if timing is not None:
        clock = timing['clock']
        protocol = '调用方声明正常链录入协议' if timing['ordering_protocol'] == 'declared_normal_chain' else '调用方显式排序约束'
        parts.extend(['<h3>时刻界限与联合约束</h3>',
            '<p>干员：' + _esc(timing['operator']) + '；技能：' + _esc(timing['skill_name']) + '</p>',
            '<p>来源类别：' + _esc(KIND_NAMES[timing['evidence_kind']]) + '；来源：' + _esc(timing['source']) + '</p>',
            '<p>时钟：' + _esc(clock['id']) + '；单位：' + ('秒' if clock['unit'] == 'seconds' else '视频帧') + '；声明视频FPS：' + _esc(clock['fps']) + '</p>',
            '<p>排序口径：' + protocol + '；联合声明可行：是。排序约束不是已证原生动作顺序。</p>',
            '<p>投射命中、特殊打断或未证先后可使用显式约束；不依事件名称强推正常链。视频FPS与模型30Hz独立。</p>'])
        parts.append('<p>时间界限为连续覆盖范围；视频整帧仅作端点，不是离散整数帧事件集合。</p>')
        parts.append(_table(['周期', '时差口径', '联合可行时差/秒', '条件参考/秒', '残差界限/秒', '比较结论', '原生参考'], [
            [r['cycle_id'], r['label'], r['observed_interval_seconds'], r['conditional_reference_seconds'],
             r['residual_interval_seconds'], STATE_NAMES[r['classification']], r['actual_native_reference_seconds']]
            for r in timing['comparisons'] + timing['release_interval_rows']]))
        if timing['repeat_cycle_rows']:
            parts.append(_table(['相邻周期', '开启间隔界限/秒', '前期开启到下次就绪/秒', '下次就绪到后期开启/秒'], [
                [r['previous_cycle_id'] + '→' + r['cycle_id'], r['observed_interval_seconds'],
                 r['previous_start_to_next_ready_interval_seconds'], r['next_ready_to_current_start_interval_seconds']]
                for r in timing['repeat_cycle_rows']]))
        parts.append('<h3>原录入界限与联合可行界限</h3>')
        parts.append(_table(['声明时刻', '原界限/秒', '依声明排序的可行界限/秒'], [
            [key, timing['original_readings_seconds'][key], value] for key, value in timing['feasible_readings_seconds'].items()]))
        speed = timing['attack_speed_comparison']
        parts.append('<p>独立攻速属性界限：' + _esc(speed['observed_interval']) + '；条件参考：' + _esc(speed['conditional_reference']) + '；比较：' + STATE_NAMES[speed['classification']] + '。' + _esc(speed['note']) + '</p>')
        reference = timing['reference']
        parts.append('<p>原表固定持续参数：' + _esc(reference['source_duration_parameter_seconds']) + '；模型持续估计：' + _esc(reference['model_duration_reference_seconds']) + '；实际结束/解除阻回：未知。</p>')
        for warning in reference['warnings']:
            parts.append('<p>警告：' + _esc(warning) + '</p>')
    parts.extend('<p>' + _esc(note) + '</p>' for note in result['notes'])
    parts.append('<p>未认证当前实机、测量精度或原生时钟；实际因果归属未知。</p></body></html>')
    return ''.join(parts)


class BoundedCalibrationPanel(QWidget):
    resultReady = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scenario = None
        self._result = None
        layout = QVBoxLayout(self)
        notice = QLabel('明确录入每项[下界,上界]。正常链仅为调用方选择的排序协议；其他来源可填写显式约束。不自动生成误差、观察值或测量置信度。')
        notice.setWordWrap(True)
        layout.addWidget(notice)
        templates = QHBoxLayout()
        self.template = QComboBox()
        for key, name in (('kaltsit', '凯尔希字面量公式界限'), ('silverash', '凛御银灰字面量公式界限'), ('mechanist', '机械师字面量公式界限')):
            self.template.addItem(name, key)
        self.load_template = QPushButton('载入选中公式参考')
        templates.addWidget(self.template, 1)
        templates.addWidget(self.load_template)
        layout.addLayout(templates)
        toggles = QHBoxLayout()
        self.use_panel = QCheckBox('比较面板界限')
        self.use_timing = QCheckBox('比较时刻界限')
        self.use_panel.setChecked(True)
        self.use_timing.setChecked(True)
        toggles.addWidget(self.use_panel)
        toggles.addWidget(self.use_timing)
        layout.addLayout(toggles)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(self.splitter, 1)
        inputs = QWidget()
        input_layout = QVBoxLayout(inputs)
        input_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs = QTabWidget()
        self.panel_editor, self.timing_editor = QPlainTextEdit(), QPlainTextEdit()
        self.panel_editor.setAccessibleName('面板前后独立界限JSON')
        self.timing_editor.setAccessibleName('事件时钟界限与声明约束JSON')
        self.tabs.addTab(self.panel_editor, '面板界限与来源')
        self.tabs.addTab(self.timing_editor, '时刻界限与声明约束')
        input_layout.addWidget(self.tabs, 1)
        actions = QHBoxLayout()
        self.reference_button = QPushButton('读取现有条件参考')
        self.bind_button = QPushButton('确认已录入条件并填写标识')
        actions.addWidget(self.reference_button)
        actions.addWidget(self.bind_button)
        input_layout.addLayout(actions)
        imports = QHBoxLayout()
        self.import_target = QComboBox()
        for key, name in (('before', '面板前组'), ('after', '面板后组'), ('timing', '时刻条件')):
            self.import_target.addItem(name, key)
        self.import_button = QPushButton('显式导入当前干员条件')
        self.import_button.setEnabled(False)
        imports.addWidget(self.import_target)
        imports.addWidget(self.import_button, 1)
        input_layout.addLayout(imports)
        self.reference_view = QPlainTextEdit()
        self.reference_view.setReadOnly(True)
        self.reference_view.setMaximumHeight(130)
        self.reference_view.hide()
        input_layout.addWidget(self.reference_view)
        self.splitter.addWidget(inputs)
        outputs = QWidget()
        output_layout = QVBoxLayout(outputs)
        output_layout.setContentsMargins(0, 0, 0, 0)
        controls = QHBoxLayout()
        controls.addWidget(QLabel('明确面板容差'))
        self.panel_tolerance, self.timing_tolerance = QDoubleSpinBox(), QDoubleSpinBox()
        for spin in (self.panel_tolerance, self.timing_tolerance):
            spin.setRange(0, 1000000)
            spin.setDecimals(6)
        controls.addWidget(self.panel_tolerance)
        controls.addWidget(QLabel('明确秒数容差'))
        controls.addWidget(self.timing_tolerance)
        self.run_button = QPushButton('核对界限与联合可行时差')
        controls.addWidget(self.run_button, 1)
        output_layout.addLayout(controls)
        self.status = QLabel('等待独立界限记录。')
        self.status.setWordWrap(True)
        output_layout.addWidget(self.status)
        self.result_view = QTextBrowser()
        self.result_view.setOpenExternalLinks(False)
        output_layout.addWidget(self.result_view, 1)
        self.splitter.addWidget(outputs)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.splitter.setSizes([350, 550])
        self.load_template.clicked.connect(self.load_public_template)
        self.reference_button.clicked.connect(self.inspect)
        self.bind_button.clicked.connect(self.bind_contexts)
        self.import_button.clicked.connect(self.import_scenario)
        self.run_button.clicked.connect(self.execute)
        for editor in (self.panel_editor, self.timing_editor):
            editor.textChanged.connect(self.invalidate)
        for spin in (self.panel_tolerance, self.timing_tolerance):
            spin.valueChanged.connect(self.invalidate)
        self.use_panel.toggled.connect(self.invalidate)
        self.use_timing.toggled.connect(self.invalidate)
        self.load_public_template()

    @staticmethod
    def _parse(editor):
        value = json.loads(editor.toPlainText())
        if not isinstance(value, dict):
            raise ValueError('每组需为JSON对象。')
        return value

    @staticmethod
    def _write(editor, value):
        editor.setPlainText(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))

    def invalidate(self, *_):
        self._result = None
        self.result_view.clear()
        self.status.setText('界限或条件已修改，请重新核对。')

    def load_public_template(self):
        payload = public_bounded_payload(self.template.currentData())
        self._write(self.panel_editor, payload['panel'])
        self._write(self.timing_editor, payload['timing'])
        self.panel_tolerance.setValue(0)
        self.timing_tolerance.setValue(0)
        self.reference_view.clear()
        self.reference_view.hide()
        self.status.setText('已显式载入[v,v]退化公式界限；没有默认游戏精度或置信度。时刻正常链是调用方录入协议。')

    def set_scenario(self, scenario):
        self._scenario = deepcopy(scenario)
        self.import_button.setEnabled(isinstance(scenario, dict) and scenario.get('operator') in ('kaltsit', 'silverash', 'mechanist'))

    def inspect(self):
        from .calibration import panel_layers
        from .timing_calibration import timing_reference
        try:
            references = {}
            if self.use_panel.isChecked():
                panel = self._parse(self.panel_editor)
                references['panel'] = {key: panel_layers(panel[key]['scenario']) for key in ('before', 'after')}
            if self.use_timing.isChecked():
                references['timing'] = timing_reference(self._parse(self.timing_editor)['scenario'])
            self.reference_view.setPlainText(json.dumps(references, ensure_ascii=False, indent=2, allow_nan=False))
            self.reference_view.show()
            self.status.setText('现有参考已读取；独立界限、排序声明与来源保持原填写内容。')
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText('读取失败：' + str(error))

    def bind_contexts(self):
        from .calibration import panel_layers
        from .timing_calibration import timing_reference
        try:
            updates = []
            if self.use_panel.isChecked():
                panel = self._parse(self.panel_editor)
                for key in ('before', 'after'):
                    panel[key]['observation']['context_token'] = panel_layers(panel[key]['scenario'])['context_token']
                updates.append((self.panel_editor, panel))
            if self.use_timing.isChecked():
                timing = self._parse(self.timing_editor)
                timing['observation']['context_token'] = timing_reference(timing['scenario'])['context_token']
                updates.append((self.timing_editor, timing))
            for editor, value in updates:
                self._write(editor, value)
            self.status.setText('条件标识已显式声明；观察界限、干员/技能身份、来源和排序协议未改动。')
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText('填写标识失败：' + str(error))

    def import_scenario(self):
        try:
            if self._scenario is None:
                raise ValueError('没有可导入的当前干员条件。')
            target = self.import_target.currentData()
            editor = self.timing_editor if target == 'timing' else self.panel_editor
            value = self._parse(editor)
            if target == 'timing':
                value['scenario'] = deepcopy(self._scenario)
            else:
                value[target]['scenario'] = deepcopy(self._scenario)
            self._write(editor, value)
            self.status.setText('已显式导入选中条件；独立界限与来源未改动，需核对条件标识。')
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText('导入失败：' + str(error))

    def execute(self):
        self.invalidate()
        try:
            result = bounded_calibration(panel=self._parse(self.panel_editor) if self.use_panel.isChecked() else None,
                timing=self._parse(self.timing_editor) if self.use_timing.isChecked() else None,
                panel_tolerance=self.panel_tolerance.value(), timing_tolerance_seconds=self.timing_tolerance.value())
            rendered = bounded_calibration_html(result)
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText('未完成界限核对：' + str(error))
            return
        self._result = deepcopy(result)
        self.result_view.setHtml(rendered)
        self.status.setText('界限已核对；仅可能重叠不是认证，联合可行只针对调用方声明的排序协议。')
        self.resultReady.emit(deepcopy(result))

    def result_snapshot(self):
        return deepcopy(self._result)
