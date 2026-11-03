"""Editable, isolated before/after evidence workspace for paired calibration."""
from copy import deepcopy
import html
import json

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QPlainTextEdit, QTextBrowser, QComboBox, QDoubleSpinBox,
    QTabWidget, QSplitter)

from .calibration import LABELS, panel_layers
from .paired_calibration import compare_paired_panels, public_paired_payload


STATUS_NAMES = {
    'model_field_unknown': '模型字段未知，保留观察差',
    'delta_mismatch': '差值残差超出声明容差',
    'delta_matches_but_absolute_panels_differ': '差值相符，但两端绝对面板存在偏差',
    'paired_values_match': '共同字段的前后值及差值相符',
}
KIND_NAMES = {'game_panel': '调用方声明的游戏面板', 'public_case': '调用方声明的公开算例',
              'formula_reference': '公式参考算例'}
RELIC_REASONS = {
    'no_declared_condition_change': '声明条件未变化',
    'other_declared_conditions_changed': '存在培养、天赋或其他条件变化，未作藏品单独联接',
    'same_relic_membership_or_order_only': '藏品成员相同，仅顺序或空声明不同',
    'transition_exceeds_existing_diagnostic_limit': '变化藏品数量超出现有每侧12件诊断范围',
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
        ''.join('<tr>' + ''.join('<td>' + _esc(v) + '</td>' for v in row) + '</tr>' for row in rows) + '</table>')


def paired_calibration_html(result):
    """Readable output usable by this workspace or the general offline tools."""
    parts = ['<html><body><h2>首批三名前后成对面板校准</h2>',
        '<p>所有差值为后减前；公开公式参考与声明游戏观察分别保留。未知不补零，未认证实机。</p>',
        '<p>干员：' + _esc(result['operator']) + '；面板：' + _esc(result['panel']) + '</p>',
        '<p>来源类别：' + _esc(KIND_NAMES[result['evidence_kind']]) + '</p>']
    for side, name in (('before', '前组'), ('after', '后组')):
        comparison = result[side]['comparison']
        parts.append('<p>' + name + '来源：' + _esc(comparison['source']) + '</p>')
        parts.append('<p>' + name + '条件标识：' + _esc(comparison['context_token']) + '</p>')
    parts.append(_table(['属性', '前组观察', '后组观察', '前组模型', '后组模型',
        '观察差', '模型差', '差值残差', '前组绝对偏差', '后组绝对偏差', '诊断'], [
            [r['label'], r['before_observed'], r['after_observed'], r['before_model_reference'],
             r['after_model_reference'], _text(r['observed_after_minus_before'], True),
             _text(r['model_after_minus_before'], True), _text(r['delta_residual'], True),
             _text(r['before_observation_minus_model'], True), _text(r['after_observation_minus_model'], True),
             STATUS_NAMES[r['diagnostic_status']]] for r in result['rows']]))
    parts.append('<p>共同字段：' + str(result['shared_field_count']) + '；模型差已知字段：' +
                 str(result['known_model_delta_count']) + '；声明容差：' + _esc(result['tolerance']) + '</p>')
    for side, name in (('before_only_fields', '仅前组填写'), ('after_only_fields', '仅后组填写')):
        parts.append('<p>' + name + '：' + _esc('、'.join(LABELS[k] for k in result[side]) or '无') + '；不作前后比较。</p>')
    parts.append('<p>共同字段差值全部相符：' + _esc(result['all_compared_deltas_match']) +
                 '；共同字段两端绝对面板全部相符：' + _esc(result['all_paired_absolute_values_match']) + '</p>')
    parts.append('<h3>声明条件变化</h3>')
    if result['changed_conditions']:
        parts.append(_table(['条件', '前组声明', '后组声明'], [
            [r['field'], json.dumps(r['before'], ensure_ascii=False) if r['before_present'] else '未声明',
             json.dumps(r['after'], ensure_ascii=False) if r['after_present'] else '未声明']
            for r in result['changed_conditions']]))
    else:
        parts.append('<p>声明条件一致；仍分别保留观察来源。</p>')
    transition = result['relic_transition']
    parts.append('<h3>藏品模型诊断联接</h3>')
    if not transition['available']:
        parts.append('<p>' + _esc(RELIC_REASONS[transition['reason']]) + '。</p>')
    else:
        for key, label in (('before_diagnostics', '前组移除的藏品'), ('after_diagnostics', '后组添加的藏品')):
            diagnostic = transition[key]
            if diagnostic is None:
                continue
            parts.append('<p>' + label + '：' + _esc('、'.join(diagnostic['audited_relic_ids'])) +
                         '；共同背景：' + _esc('、'.join(diagnostic['background_relic_ids']) or '无') + '</p>')
            parts.append(_table(['面板属性', '组合模型差', '单件背景差之和', '非相加模型残差'], [
                [r['label'], _text(r['combined_model_difference'], True),
                 _text(r['sum_single_background_model_differences'], True),
                 _text(r['nonadditive_model_residual'], True)] for r in diagnostic['combination_rows']
                if r['panel'] == result['panel']]))
        parts.append('<p>这些是已有模型的组合诊断；实际藏品因果归属：未知。</p>')
    for side, name in (('before', '前组'), ('after', '后组')):
        for warning in result[side]['model']['warnings']:
            parts.append('<p>' + name + '警告：' + _esc(warning) + '</p>')
    parts.extend('<p>' + _esc(note) + '</p>' for note in result['notes'])
    parts.append('</body></html>')
    return ''.join(parts)


class PairedCalibrationPanel(QWidget):
    """Owns editable public copies only; host refresh never replaces evidence."""
    resultReady = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scenario = None
        self._result = None
        layout = QVBoxLayout(self)
        self.notice = QLabel('前后各自填写培养/藏品条件及独立观察记录；只比较同干员、同层、同类来源的共同字段。读取分层不会替换观察数值或来源。')
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        bar = QHBoxLayout()
        self.template = QComboBox()
        for operator, name in (('mechanist', '机械师攻击符文公式参考'), ('kaltsit', '凯尔希生命符文公式参考'), ('silverash', '凛御银灰天赋时间公式参考')):
            self.template.addItem(name, operator)
        self.load_template = QPushButton('载入选中公式参考')
        bar.addWidget(self.template, 1)
        bar.addWidget(self.load_template)
        layout.addLayout(bar)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(self.splitter, 1)
        workspace = QWidget()
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs = QTabWidget()
        self.before_editor, self.after_editor = QPlainTextEdit(), QPlainTextEdit()
        self.before_editor.setAccessibleName('前组条件与独立观察JSON')
        self.after_editor.setAccessibleName('后组条件与独立观察JSON')
        self.before_layers_button, self.after_layers_button = QPushButton('读取前组条件分层与标识'), QPushButton('读取后组条件分层与标识')
        self.before_bind_button, self.after_bind_button = QPushButton('确认前组声明条件并填写标识'), QPushButton('确认后组声明条件并填写标识')
        self.before_import_button, self.after_import_button = QPushButton('导入当前干员条件到前组'), QPushButton('导入当前干员条件到后组')
        self.before_levels_button = QPushButton('按等级排查前组面板偏差')
        self.after_levels_button = QPushButton('按等级排查后组面板偏差')
        for name, editor, inspect_button, bind_button, import_button in (
                ('前组', self.before_editor, self.before_layers_button, self.before_bind_button, self.before_import_button),
                ('后组', self.after_editor, self.after_layers_button, self.after_bind_button, self.after_import_button)):
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.addWidget(editor, 1)
            page_layout.addWidget(inspect_button)
            page_layout.addWidget(bind_button)
            page_layout.addWidget(import_button)
            page_layout.addWidget(self.before_levels_button if name == '前组' else self.after_levels_button)
            import_button.setEnabled(False)
            self.tabs.addTab(page, name)
        workspace_layout.addWidget(self.tabs, 1)
        self.context_view = QPlainTextEdit()
        self.context_view.setReadOnly(True)
        self.context_view.setMaximumHeight(150)
        self.context_view.setPlaceholderText('读取条件分层后，在此查看面板与条件标识；观察值保持原填写内容。')
        self.context_view.hide()
        workspace_layout.addWidget(self.context_view)
        self.splitter.addWidget(workspace)
        result_page = QWidget()
        result_layout = QVBoxLayout(result_page)
        result_layout.setContentsMargins(0, 0, 0, 0)
        controls = QHBoxLayout()
        controls.addWidget(QLabel('声明容差'))
        self.tolerance = QDoubleSpinBox()
        self.tolerance.setDecimals(6)
        self.tolerance.setRange(0, 1000000)
        controls.addWidget(self.tolerance)
        self.run_button = QPushButton('比较前后面板与差值')
        controls.addWidget(self.run_button, 1)
        result_layout.addLayout(controls)
        self.status = QLabel('等待独立前后声明。')
        self.status.setWordWrap(True)
        result_layout.addWidget(self.status)
        self.result_view = QTextBrowser()
        self.result_view.setOpenExternalLinks(False)
        result_layout.addWidget(self.result_view, 1)
        self.splitter.addWidget(result_page)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.splitter.setSizes([320, 500])
        self.load_template.clicked.connect(self.load_public_template)
        self.run_button.clicked.connect(self.execute)
        self.before_levels_button.clicked.connect(lambda: self.inspect_levels(self.before_editor, '前组'))
        self.after_levels_button.clicked.connect(lambda: self.inspect_levels(self.after_editor, '后组'))
        for editor, inspect_button, bind_button, import_button, name in (
                (self.before_editor, self.before_layers_button, self.before_bind_button, self.before_import_button, '前组'),
                (self.after_editor, self.after_layers_button, self.after_bind_button, self.after_import_button, '后组')):
            inspect_button.clicked.connect(lambda checked=False, e=editor, n=name: self.inspect(e, n))
            bind_button.clicked.connect(lambda checked=False, e=editor, n=name: self.bind_context(e, n))
            import_button.clicked.connect(lambda checked=False, e=editor, n=name: self.import_scenario(e, n))
        self.load_public_template()

    @staticmethod
    def _parse(editor):
        record = json.loads(editor.toPlainText())
        if not isinstance(record, dict) or set(record) != {'scenario', 'observation'}:
            raise ValueError('每组JSON需包含且仅包含 scenario 与 observation。')
        if not isinstance(record['observation'], dict):
            raise ValueError('observation需为JSON对象。')
        return record

    @staticmethod
    def _write(editor, record):
        editor.setPlainText(json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False))

    def load_public_template(self):
        payload = public_paired_payload(self.template.currentData())
        self._write(self.before_editor, payload['before'])
        self._write(self.after_editor, payload['after'])
        self.tolerance.setValue(payload['tolerance'])
        self._result = None
        self.result_view.clear()
        self.context_view.clear()
        self.context_view.hide()
        self.status.setText('已显式载入公式参考；数值是公开固定算式样例，未作游戏面板认证。')

    def set_scenario(self, scenario):
        self._scenario = deepcopy(scenario)
        valid = isinstance(scenario, dict) and scenario.get('operator') in ('mechanist', 'kaltsit', 'silverash')
        self.before_import_button.setEnabled(valid)
        self.after_import_button.setEnabled(valid)

    def inspect(self, editor, name):
        try:
            model = panel_layers(self._parse(editor)['scenario'])
            self.context_view.setPlainText(name + '条件分层（观察记录未改动）\n' +
                json.dumps({'context_token': model['context_token'], 'panels': model['panels'],
                            'warnings': model['warnings']}, ensure_ascii=False, indent=2, allow_nan=False))
            self.context_view.show()
            self.status.setText(name + '分层已读取；确认观察记录属于此条件后再填写标识。')
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText(name + '条件读取失败：' + str(error))

    def bind_context(self, editor, name):
        try:
            record = self._parse(editor)
            model = panel_layers(record['scenario'])
            record['observation']['context_token'] = model['context_token']
            self._write(editor, record)
            self.status.setText(name + '条件标识已由显式声明填写；观察值、来源和面板层保持原填写内容。')
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText(name + '标识填写失败：' + str(error))

    def import_scenario(self, editor, name):
        try:
            if not isinstance(self._scenario, dict):
                raise ValueError('没有可导入的当前干员条件。')
            record = self._parse(editor)
            record['scenario'] = deepcopy(self._scenario)
            self._write(editor, record)
            self.status.setText(name + '条件已显式导入；原观察记录未改动，需核对其条件标识。')
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText(name + '导入失败：' + str(error))

    def execute(self):
        try:
            result = compare_paired_panels(self._parse(self.before_editor), self._parse(self.after_editor), self.tolerance.value())
            rendered = paired_calibration_html(result)
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self._result = None
            self.result_view.clear()
            self.status.setText('未完成比较：' + str(error))
            return
        self._result = deepcopy(result)
        self.result_view.setHtml(rendered)
        self.status.setText('已比较 ' + str(result['shared_field_count']) + ' 个共同字段；模型未知与绝对偏差分别保留，未认证实机。')
        self.resultReady.emit(deepcopy(result))

    def result_snapshot(self):
        return deepcopy(self._result)

    def inspect_levels(self, editor, name):
        from .level_panel_diagnostics import diagnose_panel_levels
        from .level_panel_view import LevelPanelDialog
        try:
            record = self._parse(editor)
            result = diagnose_panel_levels(record['scenario'], record['observation'], self.tolerance.value())
        except (ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            self.status.setText(name + '等级排查未完成：' + str(error))
            return
        previous = getattr(self, 'level_dialog', None)
        if previous is not None:
            previous.close()
        self.level_dialog = LevelPanelDialog(result, self)
        self.level_dialog.show()
        self.status.setText(name + '等级排查已打开；仅为声明模型假设，原观察及前后比较保持原记录。')
