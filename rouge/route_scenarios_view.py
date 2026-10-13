"""Finite explicitly declared scenario matrix; no scenario probabilities."""
from copy import deepcopy
import html
import json
from urllib.parse import quote

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton

from .route_scenarios import scenario_route_matrix
from .route_resident_review_view import ResidentRouteReviewPanel, render_resident_review
from .route_resource_ledger_view import public_resource_presets, render_resource_ledger
from .route_constraints_view import _label
from .exploration_planning import reference_data


def public_scenario_presets():
    """Public compound declarations, each snapshot independent and editable."""
    source = deepcopy(public_resource_presets()[0]['payload'])
    common = {key: deepcopy(value) for key, value in source.items() if key not in ('graph', 'routes')}
    common.update(residents=[], risk_policy='show_all')

    def scenario(identity, name, **changes):
        return {**deepcopy(common), 'id': identity, 'name': name, **deepcopy(changes)}

    spent = deepcopy(common['inventory']); spent[0]['remaining_uses'] = 0
    compound = {'graph': source['graph'], 'routes': source['routes'], 'scenarios': [
        scenario('ap8', '行动力8、明确库存与空居民快照'),
        scenario('ap2', '行动力2，检验付款停止边界', action_points=2),
        scenario('uses0', '触须余次数0', inventory=spent),
        scenario('missing-stock', '明确库存缺少触须实例', inventory=common['inventory'][1:]),
        scenario('unknown-snapshots', '库存与概念体快照未知', inventory=None, passive_items=None,
                 activation_declarations={}),
        scenario('resident-overlap', '居民位于首个目的地，声明避开候选重叠',
                 residents=[{'id': 'public-resident', 'node_id': 'a'}], risk_policy='avoid_candidate_overlap'),
        scenario('missing-tail', '明确库存缺少末步融雪，保留前两步来源',
                 inventory=[common['inventory'][0], common['inventory'][2]])]}
    closed = deepcopy(compound); closed['scenarios'] = [
        scenario('ap8', '行动力8、完整分项声明'),
        scenario('ap9', '行动力9、完整分项声明', action_points=9)]
    unknown = deepcopy(closed)
    unknown['scenarios'][1]['name'] = '激活与转移阶段未声明'
    unknown['scenarios'][1]['activation_declarations'] = {}
    for terminal in unknown['scenarios'][1]['terminals'].values(): terminal['success_declared'] = None
    return [{'id': 'compound', 'label': '行动力、余次数、缺库存、未知快照与居民复合矩阵', 'payload': compound},
            {'id': 'closed', 'label': '完整声明情景的分项数量范围', 'payload': closed},
            {'id': 'unknown', 'label': '独立阶段未知，不生成完整数量范围', 'payload': unknown}]


_MOVEMENT_NAMES = {'closed': '所列移动条件闭合', 'blocked_declared_inventory': '明确库存缺少计划实例',
                   'unknown_declared_inventory': '库存快照未知',
                   'blocked_movement_reference': '明确移动条件不符或行动力不足',
                   'unknown_movement_reference': '移动条件或依赖未知'}
_QUANTITIES = {'hope_grant_quantity': '希望授予', 'shield_grant_quantity': '护盾授予',
               'random_relic_quantity': '随机收藏品数量', 'random_move_item_quantity': '出口加工品数量',
               'base_experience': '基础经验', 'gold': '基础战斗及加工品源石锭', 'gold_interval': '源石锭差值范围'}
_REASONS = {'known_condition_or_ap_failed': '明确条件不符或行动力不足',
            'zero_ap_callback_order_unverified': '付款到零后的执行顺序未证',
            'node_arrival_ap_condition_unknown': '节点到达行动力条件未知',
            'eligibility_or_inventory_condition_unknown': '移动资格或库存余次数未知',
            'unknown_inventory_snapshot': '库存快照未知', 'unknown_passive_snapshot': '概念体快照未知',
            'inventory_snapshot_unknown': '库存快照未知', 'passive_snapshot_unknown': '概念体快照未知',
            'missing_planned_instances': '明确库存缺少计划实例',
            'resident_snapshot_unknown': '居民快照未知', 'residents_snapshot_unknown': '居民快照未知',
            'component_conditions_not_closed': '所列分项条件未全部闭合',
            'quantity_conditions_not_closed': '数量条件未闭合', 'different_declared_goal': '声明终点不同',
            'different_declared_goal_or_terminal': '终点或转移声明不同',
            'different_terminal_declarations': '转移声明不同',
            'declared_policy_rejected': '声明的候选重叠规则排除此情景',
            'risk_policy_rejected': '声明的候选重叠规则排除此情景',
            'planned_instance_not_confirmed': '库存未知，计划实例尚未确认',
            'planned_instance_absent_from_explicit_snapshot': '计划实例不在明确库存快照中',
            'route_ledger_not_evaluated_after_missing_instance': '缺少计划实例后，路线账本未评估',
            'source_grants_or_terminal_not_closed': '来源授予或独立出口条件未闭合',
            'resident_navigation_unknown': '居民移动或回退候选未知',
            'different_goal_or_terminal_declaration': '终点或独立转移声明不同',
            'compound_case_quantities_not_closed': '复合情景的数量条件未闭合',
            'declared_risk_policy_not_matched': '声明的居民候选规则未符合',
            'closed_declared_component_rule': '满足所列分项的保守比较规则',
            'conservative_component_rule_not_satisfied': '未满足所列分项的保守比较规则；不证明实际收益较差'}
_WITNESS_FIELDS = {'movement_status': '移动状态', 'movement_stop_reason': '移动停止原因',
                   'missing_planned_instances': '缺少的计划实例', 'risk_policy_match': '居民候选规则',
                   'quantity_conditions_closed': '所列数量条件', 'known_component_subtotal': '已知分项小计'}


def _text(value):
    if value is None: return '未知'
    if type(value) is bool: return '符合' if value else '不符合'
    if isinstance(value, list): return '；'.join(_text(item) for item in value) or '无'
    if isinstance(value, dict):
        return '；'.join(str(key) + '：' + _text(item) for key, item in value.items())
    return _REASONS.get(value, str(value))


def _body(document):
    """Embed the existing source detail as one body, preserving its map links."""
    return document.partition('<body>')[2].rpartition('</body>')[0] or document


def render_scenario_matrix(data, graph, links=None):
    links = links or {}; esc = lambda value: html.escape(str(value))

    def node(identity):
        label = esc(_label(graph, identity))
        return '<a href="rouge-map-node:' + quote(identity, safe='') + '">' + label + '</a>' if identity in links else label

    def interval(value):
        return esc(value['minimum']) + '～' + esc(value['maximum'])

    parts = ['<html><body><h2>有限声明情景的路线矩阵</h2>',
             '<p>每种情景独立核算。未知快照与明确空列表分别保留；情景没有概率，数量范围不是实际收益或最优路线。</p>',
             '<p>声明起点：' + node(data['start']) + '。</p>']
    names = {case['scenario_id']: case['scenario_name'] for case in data['cases']}
    parts.append('<table border="1" cellpadding="4"><tr><th>情景</th><th>路线</th><th>所列移动条件</th><th>所列数量条件</th><th>声明的居民规则</th></tr>')
    for case in data['cases']:
        for route in case['routes']:
            parts.append('<tr><td>' + esc(case['scenario_name']) + '</td><td>' + esc(route['route_id']) +
                         '</td><td>' + esc(_MOVEMENT_NAMES.get(route['movement_status'], route['movement_status'])) +
                         '</td><td>' + ('闭合' if route['quantity_conditions_closed'] else '未闭合') +
                         '</td><td>' + esc(_text(route['risk_policy_match'])) + '</td></tr>')
    parts.append('</table>')
    for summary in data['route_summaries']:
        parts += ['<h3>路线：' + esc(summary['name']) + '</h3><p>所有已列情景移动条件：' +
                  esc(_text(summary['all_declared_movement_conditions_closed'])) + '；数量条件：' +
                  esc(_text(summary['all_modeled_quantity_conditions_closed'])) + '；声明的居民规则：' +
                  esc(_text(summary['all_declared_risk_policy_matches'])) + '。</p>']
        if 'all_declared_compound_conditions_closed' in summary:
            parts.append('<p>移动、数量及居民规则的复合条件在全部已列情景中闭合：' +
                         ('已全部确认' if summary['all_declared_compound_conditions_closed'] else '未全部确认；具体失败与未知见情景明细') + '。</p>')
        envelope = summary['closed_quantity_envelope']
        parts.append('<p>所有已列情景的闭合分项范围：' +
                     ('；'.join(esc(_QUANTITIES.get(key, key)) + ' ' + interval(value) for key, value in envelope.items())
                      if envelope is not None else '未知；有失败或未知情景时，不用已知情景填补。') + '</p>')
        witnesses = []
        for witness in summary['sensitivity_witnesses']:
            if isinstance(witness, dict) and 'left_scenario_id' in witness and 'right_scenario_id' in witness:
                witnesses.append(names.get(witness['left_scenario_id'], witness['left_scenario_id']) + ' 与 ' +
                                 names.get(witness['right_scenario_id'], witness['right_scenario_id']) + '：' +
                                 '、'.join(_WITNESS_FIELDS.get(key, key) for key in witness.get('changed_fields', [])) + '发生变化')
            else: witnesses.append(_text(witness))
        parts += ['<p>移动闭合情景：' + esc('、'.join(summary['movement_closed_scenario_ids']) or '无') +
                  '；数量闭合情景：' + esc('、'.join(summary['quantity_closed_scenario_ids']) or '无') +
                  '；规则排除情景：' + esc('、'.join(summary['policy_rejected_scenario_ids']) or '无') +
                  '；未知情景：' + esc('、'.join(summary['unknown_scenario_ids']) or '无') + '。</p>',
                  '<p>结论变化见证：' + esc('；'.join(witnesses) or '所列条件状态没有变化') + '。</p>']
    for case in data['cases']:
        snapshot = case['scenario_input']
        parts += ['<h3>情景：' + esc(case['scenario_name']) + ' [' + esc(case['scenario_id']) + ']</h3>',
                  '<p>行动力：' + esc(_text(snapshot.get('action_points'))) + '；声明居民规则：' +
                  ('避开候选重叠' if snapshot.get('risk_policy') == 'avoid_candidate_overlap' else '展示全部候选') + '。</p>']
        for field, label in [('inventory', '加工品库存'), ('passive_items', '概念体快照'), ('residents', '居民快照')]:
            stock = snapshot.get(field)
            description = '未知（不是空列表）' if stock is None else '明确为空' if not stock else esc(json.dumps(stock, ensure_ascii=False))
            parts.append('<p>' + label + '：' + description + '。</p>')
        for route in case['routes']:
            parts += ['<h4>路线 ' + esc(route['route_id']) + '</h4><p>移动：' + esc(_MOVEMENT_NAMES.get(route['movement_status'], route['movement_status'])) +
                      '；声明的居民规则：' + esc(_text(route['risk_policy_match'])) + '；所列数量条件：' +
                      ('闭合' if route['quantity_conditions_closed'] else '未闭合') + '。</p>',
                      '<p>移动停止原因：' + esc('无已列停止原因' if route['movement_status'] == 'closed' and route['movement_stop_reason'] is None else _text(route['movement_stop_reason'])) +
                      '；缺少的计划实例：' + esc(_text(route['missing_planned_instances'])) +
                      '；未知与边界：' + esc(_text(route['unknown_reasons'])) + '。</p>']
            resource = route['resource_reference']
            if resource is not None:
                if resource.get('prefix_only'):
                    parts.append('<p>仅到缺实例之前的' + esc(route.get('evaluated_prefix_step_count', '已评估')) +
                                 '步已知前缀，不是完整路线；缺实例后的尾链未计入完整总量。</p>')
                resource_data = resource if 'routes' in resource else {'start': data['start'], 'routes': [resource], 'pairwise_component_differences': []}
                parts.append(_body(render_resource_ledger(resource_data, graph, links)))
            elif route['movement_status'] == 'blocked_declared_inventory':
                parts.append('<p>明确库存缺少计划实例，来源数量账本未生成；没有补齐库存或替换加工品。</p>')
            elif route['movement_status'] == 'unknown_declared_inventory':
                parts.append('<p>库存快照未知，无法确认计划实例，来源数量账本未生成；没有当作空库存。</p>')
            else: parts.append('<p>来源数量账本未生成；库存或概念体条件继续保留。</p>')
            resident = route['resident_reference']
            if resident is not None and 'routes' in resident:
                parts.append(_body(render_resident_review(resident, graph, links)))
            elif resident is not None:
                parts.append('<p>居民独立参考：' + esc(_text(resident)) + '。</p>')
            elif snapshot.get('residents') is None: parts.append('<p>居民参考未知；未把未提供快照当作没有居民。</p>')
            else: parts.append('<p>居民快照已明确声明，但移动依赖未闭合，本情景居民阶段未评估。</p>')
    for pair in data['pairwise_robust_component_comparisons']:
        relation = pair['declared_component_nonworse_across_all_cases']
        parts += ['<h3>跨情景分项核对：' + esc(pair['left']) + ' 与 ' + esc(pair['right']) + '</h3>',
                  '<p>左方案在所有已列情景是否满足希望、护盾、基础经验和源石锭不少、净行动力消耗不多的保守比较规则：' + esc(_text(relation)) +
                  '。随机品数量与价值不进入此关系；实际路线优劣未知。</p>']
        for row in pair['case_relations']:
            delta = row['component_difference']
            differences = []
            if delta is not None:
                for key, value in delta.items():
                    if key == 'net_ap_consumption': differences.append('净行动力消耗差 ' + str(value))
                    else: differences.append(_QUANTITIES.get(key, key) + ' ' + (interval(value) if isinstance(value, dict) else esc(value)))
            parts.append('<p>情景 ' + esc(row['scenario_id']) + '：' + esc(_text(row['relation'])) + '；' +
                         esc('所列分项比较成立' if row['reason'] is None and row['relation'] is True else
                             '存在较低分项或较高行动力消耗' if row['reason'] is None and row['relation'] is False else _text(row['reason'])) +
                         '；分项差值：' + ('；'.join(differences) if delta is not None else '未知') + '。</p>')
    parts.append('<p>实际最优路线、完整收益和情景概率：未知。结果只覆盖您列出的情景；没有写入本局库存或资源。</p></body></html>')
    return ''.join(parts)


class _Signals(QObject): finished = Signal(int, object, str)


class _Worker(QRunnable):
    def __init__(self, serial, payload):
        super().__init__(); self.serial = serial; self.payload = deepcopy(payload); self.signals = _Signals()

    def run(self):
        try: self.signals.finished.emit(self.serial, scenario_route_matrix(**self.payload), '')
        except Exception as exc: self.signals.finished.emit(self.serial, None, str(exc))


class RouteScenarioMatrixPanel(ResidentRouteReviewPanel):
    """Reuse sealed editing/snapshot/map guards; scenario computations are separate."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.preset.clear()
        for preset in public_scenario_presets(): self.preset.addItem(preset['label'], preset['id'])
        self.add_resident.hide(); self.declare_victory.hide()
        self.layout().itemAt(0).widget().setText('路线情景矩阵：把行动力、库存余次数、概念体及居民快照作为独立复合情景，查看变化见证与所列分项范围。')
        self.layout().itemAt(3).widget().setText('每种情景显式声明行动力、加工品库存及概念体快照。未知写“未知”或null，明确没有写[]；激活、战斗结束和转移声明仍互相独立。JSON可直接编辑全部情景、路线与来源声明。')
        row = QHBoxLayout(); self.scenario_select = QComboBox(); self.scenario_ap = QLineEdit(); self.scenario_ap.setPlaceholderText('非负整数或未知')
        self.set_scenario_ap = QPushButton('设置选中情景行动力')
        for widget in [QLabel('情景'), self.scenario_select, QLabel('行动力'), self.scenario_ap, self.set_scenario_ap]: row.addWidget(widget)
        self.layout().insertLayout(4, row)
        row = QHBoxLayout(); self.snapshot_item = QComboBox(); self.snapshot_uses = QLineEdit(); self.snapshot_uses.setPlaceholderText('非负整数或未知')
        self.set_snapshot_uses = QPushButton('设置选中库存实例余次数')
        for widget in [QLabel('本情景库存实例'), self.snapshot_item, QLabel('余次数'), self.snapshot_uses, self.set_snapshot_uses]: row.addWidget(widget)
        self.layout().insertLayout(5, row)
        self.scenario_select.currentIndexChanged.connect(self._refresh_scenario_fields)
        self.snapshot_item.currentIndexChanged.connect(self._refresh_uses)
        self.set_scenario_ap.clicked.connect(self._set_scenario_ap); self.set_snapshot_uses.clicked.connect(self._set_snapshot_uses)
        self.run_button.setText('核对全部声明情景的路线矩阵'); self._load_example()

    def _load_example(self):
        preset = next((row for row in public_scenario_presets() if row['id'] == self.preset.currentData()), public_scenario_presets()[0])
        self._graph_import = None; self._write(preset['payload'])
        self.status.setText('已载入公开合成图与独立情景声明；不是当前游戏观测。旧结果保留至重新核对。')

    def _editor_changed(self):
        super()._editor_changed()
        if not hasattr(self, 'scenario_select'): return
        choice = self.scenario_select.currentData(); self.scenario_select.blockSignals(True); self.scenario_select.clear()
        try:
            for row in self._payload().get('scenarios') or []:
                if isinstance(row, dict) and isinstance(row.get('id'), str): self.scenario_select.addItem(row.get('name') or row['id'], row['id'])
            if self.scenario_select.findData(choice) >= 0: self.scenario_select.setCurrentIndex(self.scenario_select.findData(choice))
        except Exception: pass
        self.scenario_select.blockSignals(False); self._refresh_scenario_fields()

    def _scenario(self, payload):
        return next(row for row in payload.get('scenarios') or [] if row.get('id') == self.scenario_select.currentData())

    def _refresh_scenario_fields(self):
        choice = self.snapshot_item.currentData(); self.snapshot_item.blockSignals(True); self.snapshot_item.clear(); self.scenario_ap.clear()
        try:
            scenario = self._scenario(self._payload()); ap = scenario.get('action_points'); self.scenario_ap.setText('未知' if ap is None else str(ap))
            stock = scenario.get('inventory')
            if stock is None: self.snapshot_item.addItem('库存快照未知', None)
            elif not stock: self.snapshot_item.addItem('明确空库存', None)
            else:
                for ordinal, item in enumerate(stock, 1):
                    identity = item.get('instance_id', 'inventory:' + str(ordinal)); name = reference_data()['items'].get(item.get('item_id'), {}).get('name', item.get('item_id', '未知加工品'))
                    self.snapshot_item.addItem(name + ' [' + identity + ']', identity)
            if self.snapshot_item.findData(choice) >= 0: self.snapshot_item.setCurrentIndex(self.snapshot_item.findData(choice))
        except Exception: pass
        self.snapshot_item.blockSignals(False); self._refresh_uses()

    def _refresh_uses(self):
        self.snapshot_uses.clear(); self.set_snapshot_uses.setEnabled(self.snapshot_item.currentData() is not None)
        try:
            stock = self._scenario(self._payload())['inventory']; identity = self.snapshot_item.currentData()
            item = next(row for ordinal, row in enumerate(stock, 1) if row.get('instance_id', 'inventory:' + str(ordinal)) == identity)
            value = item.get('remaining_uses'); self.snapshot_uses.setText('未知' if value is None else str(value))
        except Exception: pass

    @staticmethod
    def _optional_integer(value):
        value = value.strip()
        if value in ('', '未知', 'null'): return None
        if not value.isascii() or not value.isdigit(): raise ValueError('需要非负整数，或“未知”/null。')
        return int(value)

    def _set_scenario_ap(self):
        try:
            payload = self._payload(); self._scenario(payload)['action_points'] = self._optional_integer(self.scenario_ap.text()); self._write(payload)
            self.status.setText('已修改选中情景行动力；其它情景保留，旧结果需重新核对。')
        except Exception as exc: self.status.setText('未设置：' + str(exc))

    def _set_snapshot_uses(self):
        try:
            payload = self._payload(); stock = self._scenario(payload)['inventory']; identity = self.snapshot_item.currentData()
            if stock is None or identity is None: raise ValueError('库存未知或明确为空，没有可编辑实例。')
            item = next(row for ordinal, row in enumerate(stock, 1) if row.get('instance_id', 'inventory:' + str(ordinal)) == identity)
            value = self._optional_integer(self.snapshot_uses.text()); maximum = reference_data()['items'][item['item_id']]['raw']['count']
            if value is not None and value > maximum: raise ValueError('余次数超过固定原件初始次数。')
            item['remaining_uses'] = value; self._write(payload)
            self.status.setText('已修改选中情景的库存实例余次数；其它情景保留，旧结果需重新核对。')
        except Exception as exc: self.status.setText('未设置：' + str(exc))

    def _import_graph(self):
        super()._import_graph()
        if self.status.text().startswith('已显式导入'): self.status.setText('已显式导入缓存地图；各情景、库存与独立阶段声明保留，请核对路线及节点是否仍适用。')

    def _run(self):
        try: payload = self._payload(); graph = payload.get('graph') or {}; bindings = self._bindings(graph)
        except Exception as exc: self.status.setText('未运行：' + str(exc)); return
        self._serial += 1; serial = self._serial; worker = _Worker(serial, payload); self._workers[serial] = worker
        self._contexts[serial] = {'graph': deepcopy(graph), 'links': bindings, 'input_text': self.editor.toPlainText()}
        worker.signals.finished.connect(self._finished); self.run_button.setEnabled(False)
        self.status.setText('正在独立核对每种情景的路线与所列分项……'); QThreadPool.globalInstance().start(worker)

    def _finished(self, serial, result, error):
        self._workers.pop(serial, None); context = self._contexts.pop(serial, {})
        if serial != self._serial: return
        self.run_button.setEnabled(True)
        if error: self.status.setText('未生成新结果：' + error + '；保留此前结果。'); return
        try: rendered = render_scenario_matrix(result, context['graph'], context['links'])
        except Exception as exc: self.status.setText('结果显示失败：' + str(exc) + '；保留此前结果。'); return
        self._result = deepcopy(result); self._result_links = deepcopy(context['links']); self._result_input_text = context['input_text']
        self.result_view.setHtml(rendered); self.raw_result.setPlainText(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        self.status.setText('输入已修改，结果对应此前输入，请重新核对。' if self.editor.toPlainText() != self._result_input_text else '有限情景核对完成；实际收益、最优路线和情景概率未知。')
        self.resultChanged.emit(deepcopy(result))
