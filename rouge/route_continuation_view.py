"""Independent progress and fresh snapshot controls with guarded map links."""
from copy import deepcopy
import html
import json
from urllib.parse import quote

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QPushButton

from .route_continuation import continue_route_plan
from .route_resident_review_view import ResidentRouteReviewPanel
from .route_constraints_view import _label, render_constraint_result, REASONS as SEARCH_REASONS


def public_continuation_presets():
    graph = {'current_node': 's', 'map_instance_id': 'public-map-instance-1', 'zone_id': 'zone_1', 'template_id': 'public-continuation',
             'nodes': [{'id': key, 'row': row, 'col': col, 'base_node_type': kind}
                       for key, row, col, kind in [('s', 0, 0, 'EMPTY'), ('a', 0, 1, 'BATTLE_NORMAL'),
                           ('b', 1, 0, 'EMPTY'), ('c', 1, 1, 'EMPTY'), ('g', 0, 2, 'FINAL')]],
             'edges': [['s', 'a'], ['a', 'g'], ['s', 'b'], ['b', 'c'], ['a', 'c'], ['c', 'g']]}
    before = {'graph': graph, 'action_points': 6,
              'inventory': [{'instance_id': 'jet', 'item_id': 'rogue_6_scrap_M_08', 'remaining_uses': 1}], 'passive_items': []}
    after = deepcopy(before); after['graph']['current_node'] = 'a'; after['action_points'] = 4
    after['graph']['nodes'][1].update(base_node_type='EMPTY', completed_declared=True)
    basic = {'before': before, 'plan': {'id': 'original', 'name': '原声明路线', 'steps': [
                 {'mode': 'walking', 'target': 'a'}, {'mode': 'walking', 'target': 'g'}]},
             'progress': [{'step': 1, 'mode': 'walking', 'target': 'a', 'movement_completed_declared': True, 'battle_result_declared': 'won'}],
             'after': after, 'objectives': {'required_nodes': ['a'], 'checkpoints': ['a', 'g']},
             'max_steps': 4, 'max_results': 10, 'max_transitions': 100}
    edge = deepcopy(basic); edge['after']['graph']['edges'].remove(['a', 'g'])
    missing = deepcopy(basic); missing['plan']['steps'][1]['mode'] = 'jet'; missing['after']['inventory'] = []
    failed = deepcopy(basic); failed['progress'][0]['battle_result_declared'] = 'lost'; failed['continue_after_failure_declared'] = None
    unknown = deepcopy(basic); unknown['progress'][0]['movement_completed_declared'] = None
    new_scope = deepcopy(basic); new_scope['after']['graph'].update(map_instance_id='public-map-instance-2', zone_id='zone_2', template_id='public-continuation-next')
    new_scope['goal_after'] = 'g'; new_scope['objectives_after'] = {}
    return [{'id': 'fresh', 'label': '明示已走前缀与独立新资源差值', 'payload': basic},
            {'id': 'edge', 'label': '原余路断线，重规划替代路线', 'payload': edge},
            {'id': 'missing', 'label': '计划加工品实例已不在新快照', 'payload': missing},
            {'id': 'failed', 'label': '战斗失败后继续资格未声明', 'payload': failed},
            {'id': 'unknown', 'label': '胜利不补未知移动进度', 'payload': unknown},
            {'id': 'scope', 'label': '新区域独立明确新目标', 'payload': new_scope}]


REASONS = {**SEARCH_REASONS,
    'previous_progress_gap': '前面有进度缺口，不累计为已完成前缀',
    'progress_deviates_from_declared_plan': '声明实际路径与原计划不符',
    'movement_not_completed_declared': '已声明本步移动未完成', 'movement_completion_unknown': '本步移动完成未知',
    'prediction_or_anchor_or_new_ap_unknown': '旧预测、新AP或进度锚点未闭合',
    'inventory_prediction_or_new_snapshot_unknown': '旧次数预测或新库存/绑定未知',
    'declared_checkpoint_progress_order_conflict': '明示访问与人工检查点顺序冲突',
    'residual_goal_or_policy_binding_unknown': '残余目标或人工要求节点绑定未知',
    'progress_anchor_or_scope_or_prefix_unknown': '前缀、当前位置锚定或图身份未闭合',
    'failed_battle_continuation_not_declared': '失败后继续资格未知，停止自动续接',
    'failed_battle_continuation_declared_false': '已声明失败后不可继续',
    'fresh_inventory_or_passive_snapshot_unknown': '新库存或概念体快照未知，不借旧预测补全',
    'residual_policy_conflict': '残余人工要求存在冲突', 'suffix_node_binding_unknown': '原余路节点绑定未知',
    'planned_walking_edge_removed': '新图没有原计划的这一条步行连线',
    'suffix_inventory_unknown': '新库存未知，不能确认计划实例', 'planned_item_instance_missing': '新库存明确缺少计划加工品实例',
    'suffix_declaration_not_evaluable': '原余路声明不能独立求值',
    'original_inventory_snapshot_unknown': '旧库存未知，不生成加工品前缀预测',
}


def render_continuation(data, graph, links=None):
    links = links or {}; esc = lambda value: html.escape(str(value))
    def fresh_node(key):
        label = esc(_label(graph, key))
        return '<a href="rouge-map-node:' + quote(key, safe='') + '">' + label + '</a>' if key in links else label
    def old_node(key):
        return esc(_label(data['before_snapshot']['graph'], key))
    parts = ['<html><body><h2>路线续接与变化诊断</h2>',
             '<p>移动完成、战斗结果、新图位置和资源分别独立声明。胜利没有自动更新AP、库存、完成标志或居民。</p>',
             '<p>原起点：' + old_node(data['start_before']) + '；新声明当前位置：' + fresh_node(data['start_after']) + '。</p>',
             '<p>地图实例/区域/模板声明身份：' + ('相符' if data['scope_identity_match'] is True else '不同' if data['scope_identity_match'] is False else '未知') +
             '；连续匹配且明确完成前缀：' + str(data['matched_completed_prefix_count']) + '步；进度锚定：' +
             {'matched': '匹配', 'mismatch': '当前位置与声明前缀不符', 'unknown': '身份或节点绑定未知'}[data['anchor_status']] + '。</p>']
    for receipt in data['progress_rows']:
        parts.append('<p>步骤' + str(receipt['step']) + ' ' + old_node(receipt['target']) + '：' +
                     ('纳入人工访问前缀' if receipt['admitted_to_prefix'] else esc(REASONS.get(receipt['reason'], receipt['reason']))) +
                     '；独立战斗结果：' + {'won': '声明获胜', 'lost': '声明失败', None: '未知或未声明'}[receipt.get('battle_result_declared')] + '。</p>')
    ap = data['state_differences']['action_points']
    parts += ['<h3>新声明与名义来源分项的差值</h3><p>前缀AP参考：' + esc(ap['predicted_reference'] if ap['predicted_reference'] is not None else '未知') +
              '；新AP声明：' + esc(ap['after_declared'] if ap['after_declared'] is not None else '未知') + '；差值：' +
              esc(ap['delta'] if ap['delta'] is not None else '未知') + '。差值原因未核验，不归因于战斗结果或机制错误。</p>']
    kinds = {'changed': '余次数不同', 'added': '新声明出现实例', 'missing': '新声明缺少实例', 'unknown': '次数或库存参考未知', 'identity_conflict': '同实例ID的原件身份冲突'}
    for item in data['state_differences']['inventory']:
        parts.append('<p>库存 ' + esc(item.get('instance_id') or '整体') + '：' + kinds[item['kind']] +
                     ('；次数差值 ' + str(item['delta']) if item.get('delta') is not None else '') + '。没有推断获取、丢失或消耗原因。</p>')
    field_names = {'base_node_type': '原类型', 'node_type_raw': '原类型', 'completed_declared': '完成声明', 'occupied_declared': '占领声明',
                   'other_blocked_declared': '其它阻断声明', 'light_arrival_declaration': '羽瞰点首次/领取声明', 'node_binding_unknown_or_changed': '节点缺失或位置绑定变化'}
    for node in data['state_differences']['nodes']:
        parts.append('<p>图状态变化 ' + fresh_node(node['node_id']) + '：' + '、'.join(field_names[key] for key in node['changes']) + '。来自独立新图，未由胜利自动转换。</p>')
    for key, label in [('removed', '新图缺少原连线'), ('added', '新图新声明连线')]:
        for edge in data['state_differences']['edges'][key]: parts.append('<p>' + label + '：' + ' ↔ '.join(fresh_node(node) for node in edge) + '。</p>')
    if data['remaining_objectives'] is not None:
        parts.append('<h3>残余人工目标</h3>')
        for key, label in [('required_nodes', '仍需进入'), ('avoid_nodes', '仍需避开'), ('checkpoints', '后续顺序检查点')]:
            parts.append('<p>' + label + '：' + (' → '.join(fresh_node(node) for node in data['remaining_objectives'][key]) or '没有已列要求') + '。</p>')
    suffix = data['remaining_plan_review']
    if suffix:
        parts.append('<h3>原余路逐步复核</h3>')
        if suffix['failure_continuation_condition_matches'] is not True:
            parts.append('<p>失败后的继续资格未成立；以下移动算式仅为独立新快照参考，不证明可继续。</p>')
        for row in suffix['blocked_or_unknown_rows']:
            parts.append('<p>原步骤' + str(row['step']) + ' ' + fresh_node(row['node_id']) + '：' + esc(REASONS.get(row['reason'], row['reason'])) + '。</p>')
        if not suffix['blocked_or_unknown_rows']:
            parts.append('<p>' + ('声明路线目标已抵达；结局是否完成未知。' if not suffix['steps'] else '所列余路移动分项条件相符；实际继续与战斗条件未核验。') + '</p>')
    for row in data['replanning_frontier']:
        parts.append('<p>续接停止前沿：' + fresh_node(row['node_id']) + '；' + esc(REASONS.get(row['reason'], row['reason'])) + '。</p>')
    if data['alternatives']:
        document = render_constraint_result(data['alternatives'], graph, links)
        parts.append(document.partition('<body>')[2].rpartition('</body>')[0])
    elif data['replanning_status'] == 'declared_target_reached':
        parts.append('<p>已声明抵达目标且没有剩余人工访问要求。游戏结局、完整奖励与实际成功仍未知。</p>')
    parts += ['<p>重规划目标来源：' + ('独立新图目标与完整人工要求' if data['replanning_origin'] == 'explicit_new_goal_and_objectives' else '原目标与已核对明示前缀' if data['replanning_origin'] else '尚未建立') +
              '。未知库存不由旧名义账本补齐，旧战斗身份未搬入新图。</p>',
              '<p>实际目标完成、收益和最优路线：未知。不会修改本局或执行游戏操作。</p></body></html>']
    return ''.join(parts)


class _Signals(QObject): finished = Signal(int, object, str)
class _Worker(QRunnable):
    def __init__(self, serial, payload):
        super().__init__(); self.serial = serial; self.payload = deepcopy(payload); self.signals = _Signals()
    def run(self):
        try: self.signals.finished.emit(self.serial, continue_route_plan(**self.payload), '')
        except Exception as exc: self.signals.finished.emit(self.serial, None, str(exc))


class RouteContinuationPanel(ResidentRouteReviewPanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.preset.clear()
        for row in public_continuation_presets(): self.preset.addItem(row['label'], row['id'])
        self.add_resident.hide(); self.declare_victory.hide()
        self.layout().itemAt(0).widget().setText('路线续接：明确已完成移动和战斗结果后，用独立新图/AP/库存复核原余路与人工目标。没有从结果推断新状态。')
        self.layout().itemAt(3).widget().setText('before/after独立声明图与资源；graph.map_instance_id明确地图实例，同模板重生成不能借旧目标。progress独立声明移动/战斗。跨区域新规划需goal_after及完整objectives_after。JSON可编辑全部内容。')
        row = QHBoxLayout(); self.move_match = QComboBox(); self.battle_result = QComboBox()
        for value, label in [(True, '明确移动已完成'), (False, '明确移动未完成'), (None, '移动完成未知')]: self.move_match.addItem(label, value)
        for value, label in [(None, '战斗结果未声明'), ('won', '独立声明获胜'), ('lost', '独立声明失败')]: self.battle_result.addItem(label, value)
        self.set_progress = QPushButton('设置选中原步骤进度'); self.set_current_after = QPushButton('独立设置新图当前位置')
        for widget in [self.move_match, self.battle_result, self.set_progress, self.set_current_after]: row.addWidget(widget)
        self.layout().insertLayout(4, row)
        row = QHBoxLayout(); self.failure_match = QComboBox()
        for value, label in [(None, '失败后继续资格未知'), (True, '独立声明失败后可继续'), (False, '独立声明失败后不可继续')]: self.failure_match.addItem(label, value)
        self.set_failure = QPushButton('设置独立继续资格'); row.addWidget(self.failure_match); row.addWidget(self.set_failure); self.layout().insertLayout(5, row)
        self.set_progress.clicked.connect(self._set_progress); self.set_current_after.clicked.connect(self._set_current_after); self.set_failure.clicked.connect(self._set_failure)
        self.run_button.setText('复核变化并构造有限续接候选'); self._load_example()

    def _load_example(self):
        row = next((row for row in public_continuation_presets() if row['id'] == self.preset.currentData()), public_continuation_presets()[0])
        self._graph_import = None; self._write(row['payload']); self.status.setText('已载入合成公开图与独立进度/新状态声明；旧结果保留至重算。')

    def _editor_changed(self):
        choice = self.graph_node.currentData(); step_choice = self.step_select.currentData()
        self.graph_node.blockSignals(True); self.route_select.blockSignals(True); self.step_select.blockSignals(True)
        self.graph_node.clear(); self.route_select.clear(); self.step_select.clear()
        try:
            payload = self._payload(); graph = payload['after']['graph']; before_graph = payload['before']['graph']; plan = payload['plan']
            for node in graph.get('nodes') or []:
                if isinstance(node, dict) and isinstance(node.get('id'), str) and type(node.get('row')) is int and type(node.get('col')) is int:
                    self.graph_node.addItem(_label(graph, node['id']), node['id'])
            self.route_select.addItem(plan.get('name') or plan['id'], plan['id'])
            for ordinal, step in enumerate(plan['steps'], 1): self.step_select.addItem('原步骤' + str(ordinal) + ' ' + _label(before_graph, step['target']), ordinal)
            if self.graph_node.findData(choice) >= 0: self.graph_node.setCurrentIndex(self.graph_node.findData(choice))
            if self.step_select.findData(step_choice) >= 0: self.step_select.setCurrentIndex(self.step_select.findData(step_choice))
        except Exception: pass
        self.graph_node.blockSignals(False); self.route_select.blockSignals(False); self.step_select.blockSignals(False)
        self.import_graph.setEnabled(self._graph_cache is not None)
        running = self._contexts.get(self._serial)
        if running and self.editor.toPlainText() != running['input_text']: self.status.setText('正在核算此前输入；声明已修改，结果将对应此前输入。')
        elif self._result is not None and self.editor.toPlainText() != self._result_input_text: self.status.setText('声明已修改，结果对应此前输入，请重新复核。')

    def _refresh_steps(self): pass
    def _update_victory_button(self): self.declare_victory.setEnabled(False)

    def _set_progress(self):
        try:
            payload = self._payload(); ordinal = self.step_select.currentData()
            if not ordinal: raise ValueError('请选择原步骤。')
            progress = payload.setdefault('progress', [])
            if not isinstance(progress, list): raise ValueError('progress需要列表。')
            while len(progress) < ordinal:
                index = len(progress); step = payload['plan']['steps'][index]
                progress.append({'step': index + 1, 'target': step['target'], 'mode': step['mode'], 'movement_completed_declared': None, 'battle_result_declared': None})
            progress[ordinal - 1].update(movement_completed_declared=self.move_match.currentData(), battle_result_declared=self.battle_result.currentData())
            self._write(payload); self.status.setText('只更新选中步骤的独立进度声明；没有更新新图/AP/库存或补齐之前未知移动，请重新复核。')
        except Exception as exc: self.status.setText('未设置：' + str(exc))

    def _set_current_after(self):
        try:
            payload = self._payload(); key = self.graph_node.currentData()
            if not key: raise ValueError('请选择新图节点。')
            payload['after']['graph']['current_node'] = key; self._write(payload); self.status.setText('已独立声明新图当前位置；未推断移动、AP和库存，请重新复核。')
        except Exception as exc: self.status.setText('未设置：' + str(exc))

    def _set_failure(self):
        try:
            payload = self._payload(); payload['continue_after_failure_declared'] = self.failure_match.currentData(); self._write(payload)
            self.status.setText('已独立声明失败后的继续资格；没有生成资源或胜利，请重新复核。')
        except Exception as exc: self.status.setText('未设置：' + str(exc))

    def _import_graph(self):
        try:
            if not self._graph_cache: raise ValueError('没有可导入新图。')
            payload = self._payload(); payload['after']['graph'] = deepcopy(self._graph_cache['graph']); self._graph_import = deepcopy(self._graph_cache); self._write(payload)
            self.status.setText('只显式导入after新图；原图、计划、进度与新AP/库存声明保留，请核对身份和当前位置。')
        except Exception as exc: self.status.setText('未导入：' + str(exc))

    def _run(self):
        try: payload = self._payload(); graph = payload['after']['graph']; bindings = self._bindings(graph)
        except Exception as exc: self.status.setText('未运行：' + str(exc)); return
        self._serial += 1; serial = self._serial; worker = _Worker(serial, payload); self._workers[serial] = worker
        self._contexts[serial] = {'graph': deepcopy(graph), 'links': bindings, 'input_text': self.editor.toPlainText()}; worker.signals.finished.connect(self._finished)
        self.run_button.setEnabled(False); self.status.setText('正在复核明示前缀、独立新状态与余路……'); QThreadPool.globalInstance().start(worker)

    def _finished(self, serial, result, error):
        self._workers.pop(serial, None); context = self._contexts.pop(serial, {})
        if serial != self._serial: return
        self.run_button.setEnabled(True)
        if error: self.status.setText('未生成新结果：' + error + '；保留此前结果。'); return
        self._result = deepcopy(result); self._result_links = deepcopy(context['links']); self._result_input_text = context['input_text']
        self.result_view.setHtml(render_continuation(result, context['graph'], self._result_links)); self.raw_result.setPlainText(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        self.status.setText('声明已修改，结果对应此前输入，请重新复核。' if self.editor.toPlainText() != self._result_input_text else '声明续接复核完成；实际成功、完整收益与最优路线未知。')
        self.resultChanged.emit(deepcopy(result))
