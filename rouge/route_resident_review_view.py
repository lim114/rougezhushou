"""Readable phase review and explicit resident/post-victory declarations."""
from copy import deepcopy
import html
import json
from urllib.parse import quote

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QPlainTextEdit, QTextBrowser, QSplitter, QGroupBox)

from .route_resident_review import review_resident_routes
from .route_constraints_view import _label, REASONS, RouteConstraintsPanel
from .base_settlement_planning import gold_reference_text


def public_resident_review_presets():
    graph = {'current_node': 's', 'zone_id': 'zone_2', 'template_id': 'public-resident-review',
             'nodes': [{'id': key, 'row': row, 'col': col, 'base_node_type': kind}
                       for key, row, col, kind in [('s', 0, 0, 'EMPTY'), ('a', 0, 1, 'EMPTY'),
                           ('b', 1, 0, 'EMPTY'), ('g', 1, 1, 'FINAL'),
                           ('r', 0, 2, 'EMPTY'), ('p', 1, 2, 'BATTLE_SAVAGE')]],
             'edges': [['s', 'a'], ['a', 'g'], ['s', 'b'], ['b', 'g'], ['r', 'a'], ['r', 'p']]}
    basic = {'graph': graph, 'routes': [
        {'id': 'a-route', 'name': '经甲路径', 'steps': [{'mode': 'walking', 'target': 'a'}, {'mode': 'walking', 'target': 'g'}]},
        {'id': 'b-route', 'name': '经乙路径', 'steps': [{'mode': 'walking', 'target': 'b'}, {'mode': 'walking', 'target': 'g'}]}],
        'residents': [{'id': 'r1', 'node_id': 'r'}], 'action_points': 8,
        'risk_policy': 'show_all', 'resident_post_victories': {}}
    conservative = deepcopy(basic); conservative['risk_policy'] = 'avoid_candidate_overlap'
    fallback = deepcopy(basic); fallback['graph']['edges'].remove(['r', 'a'])
    victory = deepcopy(basic); victory['graph']['edges'].extend([['s', 'p'], ['p', 'g']])
    victory['routes'] = [{'id': 'post', 'name': '声明据点胜利后续行', 'steps': [
        {'mode': 'walking', 'target': 'p'}, {'mode': 'walking', 'target': 'g'}]}]
    victory['resident_post_victories'] = {'post': [1]}
    zero = deepcopy(basic); zero['action_points'] = 1
    return [{'id': 'phases', 'label': '进入前与移动后分开比较', 'payload': basic},
            {'id': 'conservative', 'label': '显式避开候选交集偏好', 'payload': conservative},
            {'id': 'fallback', 'label': '未知回退保持后续未知', 'payload': fallback},
            {'id': 'victory', 'label': '独立据点获胜声明与条件驱逐', 'payload': victory},
            {'id': 'zero', 'label': '付款到零停止居民尾链', 'payload': zero}]


def render_resident_review(data, graph, links=None):
    links = links or {}; esc = lambda value: html.escape(str(value))
    def node(key):
        label = esc(_label(graph, key))
        return '<a href="rouge-map-node:' + quote(key, safe='') + '">' + label + '</a>' if key in links else label
    def phase(value):
        if value is None:
            return '未评估；不能当作无风险'
        status = {'source_candidate_overlap': '声明候选与该目标有交集',
                  'navigation_position_unknown': '回退或后续位置未知',
                  'no_declared_candidate_overlap': '本阶段已列候选与目标无交集；不证明安全'}[value['status']]
        text = status + '。位置候选：' + ('、'.join(node(key) for key in value['possible_occupied_union']) or '没有已列位置候选')
        if value['position_unknown_residents']:
            text += '；后续位置未知的居民：' + esc('、'.join(value['position_unknown_residents']))
        return text
    parts = ['<html><body><h2>居民路线分阶段候选核对</h2>',
             '<p>居民快照、计划步骤及据点获胜是独立声明。进入前、移动后和声明获胜后分别显示；实际进入、移动、碰撞和战斗顺序未知。</p>',
             '<p>规划偏好：' + ('保留全部声明路线' if data['risk_policy'] == 'show_all' else '按显式偏好排除候选交集路线') +
             '。保留：' + esc('、'.join(data['policy_retained_route_ids']) or '无') + '；按偏好排除：' +
             esc('、'.join(data['policy_excluded_route_ids']) or '无') + '。</p>']
    refs = {row['id']: row for row in data['movement_and_base_comparison']['routes']}
    for route in data['routes']:
        reference = refs[route['id']]
        parts += ['<h3>' + esc(route['name']) + '</h3><p>' + ' → '.join(
            [node(data['start']), *[node(step['target']) for step in route['declared_steps']]]) + '</p>',
            '<p>移动净行动力消耗参考：' + esc(reference['net_ap_consumption_reference'] if reference['net_ap_consumption_reference'] is not None else '未知') +
            '；已知基础战斗经验小计：' + esc(reference['known_base_subtotal']['experience']) + '；已知基础源石锭：' +
            esc(gold_reference_text(reference['known_base_subtotal']['gold'])) + '。居民候选不改写这些独立分项；不是完整收益。</p>']
        for row in route['phase_rows']:
            parts.append('<h4>步骤' + str(row['step']) + '：' + node(row['node_id']) + '</h4>')
            parts.append('<p>进入前：' + phase(row['pre_entry_reference']) + '</p>')
            parts.append('<p>移动后（假设该次移动成功）：' + phase(row['post_move_reference']) + '</p>')
            if row['status'] == 'movement_dependency_unresolved':
                parts.append('<p>移动依赖链停止：' + esc(REASONS.get(row['movement_stop_reason'], row['movement_stop_reason'])) + '；不据此执行居民移动。</p>')
            elif row['status'] == 'not_evaluated_after_movement_stop':
                parts.append('<p>前序移动链停止，居民尾链未评估。</p>')
            for resident in row['resident_navigation_references']:
                if resident['source_excluded_transitions']:
                    parts.append('<p>' + esc(resident['resident_id']) + ' 来源明确排除的目的地：' +
                                 '、'.join(node(key) for key in sorted({edge['to'] for edge in resident['source_excluded_transitions']})) + '。</p>')
                if resident['unresolved_fallbacks'] or resident['prior_position_unknown']:
                    parts.append('<p>' + esc(resident['resident_id']) + '：没有未排除相邻节点的分支或此前位置未知，未知继续保留；空候选不表示消失或安全。</p>')
            if row['after_declared_post_victory_reference'] is not None:
                parts.append('<p>独立声明据点获胜后：按固定文档条件驱逐本区域全部居民；后续候选为空仅依赖这一获胜声明。实际获胜和驱逐未核验。</p>')
            elif row['resident_post_victory_declared']:
                parts.append('<p>本步已声明据点获胜，但移动依赖未闭合，未计入条件驱逐。</p>')
    parts += ['<p>实际安全、失败概率、住民同步选择、完整收益与最佳路线：未知。候选并集不表示能同时占领；未出现交集不保证安全。</p>',
              '<p>来源：PRTS固定版本433770流窜居民段落。未更新本局位置、节点完成、费用、库存或奖励。</p></body></html>']
    return ''.join(parts)


class _Signals(QObject):
    finished = Signal(int, object, str)


class _Worker(QRunnable):
    def __init__(self, serial, payload):
        super().__init__(); self.serial = serial; self.payload = deepcopy(payload); self.signals = _Signals()
    def run(self):
        try:
            self.signals.finished.emit(self.serial, review_resident_routes(**self.payload), '')
        except Exception as exc:
            self.signals.finished.emit(self.serial, None, str(exc))


class ResidentRouteReviewPanel(QWidget):
    mapNodeSelected = Signal(str, object)
    resultChanged = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._graph_cache = self._graph_import = None; self._result = None; self._result_input_text = None
        self._result_links = {}; self._workers = {}; self._contexts = {}; self._serial = 0
        layout = QVBoxLayout(self)
        intro = QLabel('居民路线核对：沿声明连线展开每次移动后的候选，进入前和移动后分开显示。未知回退保留后续未知；不赋概率或断言安全。')
        intro.setWordWrap(True); layout.addWidget(intro)
        row = QHBoxLayout(); self.preset = QComboBox()
        for preset in public_resident_review_presets(): self.preset.addItem(preset['label'], preset['id'])
        self.load_example = QPushButton('加载公开声明示例'); self.import_graph = QPushButton('导入缓存地图声明')
        for widget in [self.preset, self.load_example, self.import_graph]: row.addWidget(widget)
        layout.addLayout(row)
        row = QHBoxLayout(); self.graph_node = QComboBox(); self.add_resident = QPushButton('追加居民快照位置')
        self.route_select = QComboBox(); self.step_select = QComboBox(); self.declare_victory = QPushButton('声明本步骤据点获胜')
        for widget in [self.graph_node, self.add_resident, self.route_select, self.step_select, self.declare_victory]: row.addWidget(widget)
        layout.addLayout(row)
        guide = QLabel('residents必须显式列出0–3名居民；空列表也是您的快照声明。routes每步walking需一条相邻连线，加工品用独立实例ID；每条最多10步。resident_post_victories按路线ID列获胜步骤，只用于明确居民据点，不能由抵达推定。JSON可编辑或删除全部声明。')
        guide.setWordWrap(True); layout.addWidget(guide)
        splitter = QSplitter(Qt.Orientation.Vertical); self.editor = QPlainTextEdit(); self.result_view = QTextBrowser()
        self.result_view.setOpenLinks(False); self.result_view.setOpenExternalLinks(False)
        splitter.addWidget(self.editor); splitter.addWidget(self.result_view); layout.addWidget(splitter, 1)
        self.run_button = QPushButton('核对声明路线的居民候选阶段'); layout.addWidget(self.run_button)
        self.status = QLabel(''); self.status.setWordWrap(True); layout.addWidget(self.status)
        group = QGroupBox('技术结果（JSON，可展开）'); group.setCheckable(True); group.setChecked(False)
        gl = QVBoxLayout(group); self.raw_result = QPlainTextEdit(); self.raw_result.setReadOnly(True); gl.addWidget(self.raw_result)
        self.raw_result.hide(); group.toggled.connect(self.raw_result.setVisible); layout.addWidget(group)
        self.editor.textChanged.connect(self._editor_changed); self.route_select.currentIndexChanged.connect(self._refresh_steps)
        self.step_select.currentIndexChanged.connect(self._update_victory_button)
        self.load_example.clicked.connect(self._load_example); self.import_graph.clicked.connect(self._import_graph)
        self.add_resident.clicked.connect(self._add_resident); self.declare_victory.clicked.connect(self._declare_victory)
        self.run_button.clicked.connect(self._run); self.result_view.anchorClicked.connect(self._map_anchor)
        self._load_example()

    def _payload(self):
        try: value = json.loads(self.editor.toPlainText(), parse_constant=lambda value: (_ for _ in ()).throw(ValueError('不支持非有限数值。')))
        except (json.JSONDecodeError, ValueError) as exc: raise ValueError('输入JSON无法读取：' + str(exc)) from exc
        if not isinstance(value, dict): raise ValueError('输入需要JSON对象。')
        return value

    def _write(self, payload): self.editor.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))

    def _load_example(self):
        payload = next(row['payload'] for row in public_resident_review_presets() if row['id'] == self.preset.currentData())
        self._graph_import = None; self._write(payload)
        self.status.setText('已载入合成公开图与说明声明；不是当前游戏观测。旧结果保留至重新运行。')

    def set_graph(self, graph, *, epoch=None, historical=False):
        self._graph_cache = {'graph': deepcopy(graph), 'epoch': epoch, 'historical': bool(historical)} if isinstance(graph, dict) else None
        self.import_graph.setEnabled(self._graph_cache is not None)

    def _editor_changed(self):
        node_choice, route_choice = self.graph_node.currentData(), self.route_select.currentData()
        self.graph_node.blockSignals(True); self.route_select.blockSignals(True); self.graph_node.clear(); self.route_select.clear()
        try:
            payload = self._payload(); graph = payload.get('graph') or {}
            for node in graph.get('nodes', []):
                if isinstance(node, dict) and isinstance(node.get('id'), str) and type(node.get('row')) is int and type(node.get('col')) is int:
                    self.graph_node.addItem(_label(graph, node['id']), node['id'])
            for route in payload.get('routes') or []:
                if isinstance(route, dict) and isinstance(route.get('id'), str):
                    self.route_select.addItem(route.get('name') or route['id'], route['id'])
            if self.graph_node.findData(node_choice) >= 0: self.graph_node.setCurrentIndex(self.graph_node.findData(node_choice))
            if self.route_select.findData(route_choice) >= 0: self.route_select.setCurrentIndex(self.route_select.findData(route_choice))
        except Exception: pass
        self.graph_node.blockSignals(False); self.route_select.blockSignals(False); self._refresh_steps()
        self.add_resident.setEnabled(self.graph_node.currentData() is not None); self.import_graph.setEnabled(self._graph_cache is not None)
        running = self._contexts.get(self._serial)
        if running and self.editor.toPlainText() != running['input_text']:
            self.status.setText('正在核对运行时此前声明；输入已修改，结果将对应此前输入。')
        elif self._result is not None and self.editor.toPlainText() != self._result_input_text:
            self.status.setText('声明已修改；当前结果对应此前输入，请重新核对。')

    def _refresh_steps(self):
        choice = self.step_select.currentData(); self.step_select.blockSignals(True); self.step_select.clear()
        try:
            payload = self._payload(); graph = payload.get('graph') or {}
            route = next(row for row in payload.get('routes') or [] if row.get('id') == self.route_select.currentData())
            for ordinal, step in enumerate(route.get('steps') or [], 1):
                if isinstance(step, dict) and isinstance(step.get('target'), str):
                    self.step_select.addItem('步骤' + str(ordinal) + ' ' + _label(graph, step['target']), ordinal)
            if self.step_select.findData(choice) >= 0: self.step_select.setCurrentIndex(self.step_select.findData(choice))
        except Exception: pass
        self.step_select.blockSignals(False); self._update_victory_button()

    def _update_victory_button(self):
        enabled = False
        try:
            payload = self._payload(); route = next(row for row in payload.get('routes') or [] if row.get('id') == self.route_select.currentData())
            ordinal = self.step_select.currentData(); target = route['steps'][ordinal - 1]['target']
            node = next(row for row in payload['graph']['nodes'] if row['id'] == target)
            from .exploration_planning import _type_candidates
            enabled = _type_candidates(node)[0] == ['BATTLE_SAVAGE']
        except Exception: pass
        self.declare_victory.setEnabled(enabled)

    def _add_resident(self):
        try:
            payload = self._payload(); residents = payload.get('residents')
            if not isinstance(residents, list) or len(residents) >= 3: raise ValueError('居民快照必须是0–3项列表；可在JSON中删除或修改原位置。')
            if not self.graph_node.currentData(): raise ValueError('请选择图中节点。')
            used = {row.get('id', 'resident:' + str(index)) for index, row in enumerate(residents, 1) if isinstance(row, dict)}; ordinal = 1
            while 'resident:' + str(ordinal) in used: ordinal += 1
            residents.append({'id': 'resident:' + str(ordinal), 'node_id': self.graph_node.currentData()}); self._write(payload)
            self.status.setText('已追加临时居民快照声明；旧结果对应此前输入，请重新核对。')
        except Exception as exc: self.status.setText('未追加：' + str(exc))

    def _declare_victory(self):
        try:
            payload = self._payload(); identity = self.route_select.currentData(); ordinal = self.step_select.currentData()
            if not self.declare_victory.isEnabled(): raise ValueError('所选步骤不是明确居民据点。')
            events = payload.get('resident_post_victories') or {}
            if not isinstance(events, dict): raise ValueError('resident_post_victories需要对象。')
            steps = events.setdefault(identity, [])
            if not isinstance(steps, list): raise ValueError('获胜步骤需要列表。')
            if ordinal not in steps: steps.append(ordinal)
            payload['resident_post_victories'] = events; self._write(payload)
            self.status.setText('已独立声明本步骤据点获胜；不是由抵达推定。请重新核对条件驱逐，实际获胜仍未验证。')
        except Exception as exc: self.status.setText('未声明：' + str(exc))

    def _import_graph(self):
        try:
            if not self._graph_cache: raise ValueError('没有可导入的缓存地图。')
            payload = self._payload(); payload['graph'] = deepcopy(self._graph_cache['graph'])
            self._graph_import = deepcopy(self._graph_cache); self._write(payload)
            self.status.setText('已显式导入缓存地图；居民、路线、资源及胜利声明保留，请核对节点与连线是否仍适用。')
        except Exception as exc: self.status.setText('未导入：' + str(exc))

    _layout = staticmethod(RouteConstraintsPanel._layout)
    _bindings = RouteConstraintsPanel._bindings
    _map_anchor = RouteConstraintsPanel._map_anchor

    def _run(self):
        try:
            payload = self._payload(); graph = payload.get('graph') or {}; bindings = self._bindings(graph)
        except Exception as exc: self.status.setText('未运行：' + str(exc)); return
        self._serial += 1; serial = self._serial; worker = _Worker(serial, payload); self._workers[serial] = worker
        self._contexts[serial] = {'graph': deepcopy(graph), 'links': bindings, 'input_text': self.editor.toPlainText()}
        worker.signals.finished.connect(self._finished); self.run_button.setEnabled(False)
        self.status.setText('正在核对临时声明路线的居民阶段……'); QThreadPool.globalInstance().start(worker)

    def _finished(self, serial, result, error):
        self._workers.pop(serial, None); context = self._contexts.pop(serial, {})
        if serial != self._serial: return
        self.run_button.setEnabled(True)
        if error: self.status.setText('未生成新结果：' + error + '；保留此前结果。'); return
        self._result = deepcopy(result); self._result_links = deepcopy(context['links']); self._result_input_text = context['input_text']
        self.result_view.setHtml(render_resident_review(result, context['graph'], self._result_links))
        self.raw_result.setPlainText(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        self.status.setText('此前声明核对完成；输入已修改，当前结果对应此前输入，请重新核对。' if self.editor.toPlainText() != self._result_input_text else '局外阶段核对完成；实际安全、移动/战斗顺序和失败概率未知。')
        self.resultChanged.emit(deepcopy(result))

    def result_snapshot(self): return deepcopy(self._result)
