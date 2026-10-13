"""Source grant quantities, independent activation phases and terminal flow."""
from copy import deepcopy
import html
import json
from urllib.parse import quote

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QHBoxLayout, QComboBox, QPushButton

from .route_resource_ledger import route_resource_ledger
from .route_resident_review_view import ResidentRouteReviewPanel
from .route_constraints_view import _label
from .exploration_planning import reference_data, _type_candidates
from .base_settlement_planning import gold_reference_text


def public_resource_presets():
    graph = {'current_node': 's', 'zone_id': 'zone_1', 'template_id': 'public-source-grants',
             'nodes': [{'id': key, 'row': 0, 'col': ordinal, 'base_node_type': kind, 'scrap_category': 'EVENTS'}
                       for ordinal, (key, kind) in enumerate([('s', 'EMPTY'), ('a', 'BATTLE_SHOP'), ('b', 'SCRAP_SHOP'), ('g', 'FINAL')])],
             'edges': [['s', 'a'], ['a', 'b'], ['b', 'g']]}
    basic = {'graph': graph, 'action_points': 8, 'inventory': [
        {'instance_id': 'gold', 'item_id': 'rogue_6_scrap_M_10', 'remaining_uses': 2},
        {'instance_id': 'hope', 'item_id': 'rogue_6_scrap_M_09', 'remaining_uses': 1},
        {'instance_id': 'spring', 'item_id': 'rogue_6_scrap_M_04', 'remaining_uses': 1}],
        'passive_items': [{'item_id': 'rogue_6_scrap_P_02', 'remaining_activations': 1},
                          {'item_id': 'rogue_6_scrap_P_03', 'remaining_activations': 1}],
        'routes': [{'id': 'grants', 'name': '加工品授予与出口', 'steps': [
            {'mode': 'gold', 'target': 'a'}, {'mode': 'gold', 'target': 'b'}, {'mode': 'hope', 'target': 'g'}]},
            {'id': 'walk', 'name': '相同终点逐格步行', 'steps': [
                {'mode': 'walking', 'target': 'a'}, {'mode': 'walking', 'target': 'b'}, {'mode': 'walking', 'target': 'g'}]}],
        'activation_declarations': {'grants': {'1': {'rogue_6_scrap_P_02': True, 'rogue_6_scrap_P_03': True}}},
        'after_battle_declarations': {},
        'terminals': {key: {'transition': 'main_region_advance', 'exit_node_type': 'FINAL', 'success_declared': True}
                      for key in ['grants', 'walk']}}
    unknown = deepcopy(basic); unknown['activation_declarations'] = {}; unknown['terminals']['grants']['success_declared'] = None
    portal = deepcopy(basic); portal['terminals'] = {key: {'transition': 'portal_return', 'success_declared': True} for key in ['grants', 'walk']}
    battle = deepcopy(basic); battle['graph']['nodes'][1].update(base_node_type='BATTLE_NORMAL', scrap_category='BATTLES')
    battle['inventory'] = [{'instance_id': 'jet', 'item_id': 'rogue_6_scrap_M_08', 'remaining_uses': 1}]
    battle['passive_items'] = [{'item_id': 'rogue_6_scrap_P_01', 'remaining_activations': 1}]
    battle['routes'] = [{'id': 'battle', 'name': '独立战斗后阶段', 'steps': [{'mode': 'jet', 'target': 'a'}]}]
    battle['activation_declarations'] = {'battle': {'1': {'rogue_6_scrap_P_01': True}}}; battle['terminals'] = {}
    battle['after_battle_declarations'] = {'battle': {'1': True}}
    zero = deepcopy(basic); zero['action_points'] = 1
    return [{'id': 'grants', 'label': '加工品、概念体与FINAL完整声明流', 'payload': basic},
            {'id': 'unknown', 'label': '激活及转移未声明保持未知', 'payload': unknown},
            {'id': 'portal', 'label': '秘境返回保留临时加工品', 'payload': portal},
            {'id': 'battle', 'label': '独立战斗后收藏品阶段', 'payload': battle},
            {'id': 'zero', 'label': '停止尾链不累计资源', 'payload': zero}]


RESOURCE_NAMES = {'hope': '希望授予数量', 'gold': '源石锭授予数量', 'shield': '护盾授予数量',
                  'random_relic': '随机收藏品数量', 'random_move_item': '出口加工品数量'}
ORIGINS = {'processed_item': '加工品移动', 'passive': '独立概念体阶段',
           'terminal_conversion': '出口行动力兑换', 'terminal_item_grant': '出口加工品授予'}
REASONS = {'movement_chain_unresolved': '移动依赖链未闭合', 'grant_condition_unknown': '授予条件未知',
           'after_battle_completion_not_declared': '战斗结束未独立声明',
           'passive_activation_not_declared': '概念体激活未独立声明',
           'passive_availability_or_type_unknown': '次数、节点类型或此前消耗未知',
           'boss_conversion_ratio_unknown': '首领出口兑换比率未证',
           'terminal_success_or_movement_unknown': '转移成功或移动依赖未闭合',
           'declared_or_source_condition_failed': '独立声明或来源条件不符'}


def render_resource_ledger(data, graph, links=None):
    links = links or {}; esc = lambda value: html.escape(str(value))
    def node(key):
        label = esc(_label(graph, key))
        return '<a href="rouge-map-node:' + quote(key, safe='') + '">' + label + '</a>' if key in links else label
    parts = ['<html><body><h2>路线资源授予与出口账本</h2>',
             '<p>只合并来源明确的条件数量。概念体激活、战斗结束、转移成功分别独立声明；实际收到、完整奖励池与最终资源未知。</p>']
    for route in data['routes']:
        subtotal = route['known_combined_component_subtotal']
        parts += ['<h3>' + esc(route['name']) + '</h3><p>' + ' → '.join([node(data['start']), *[node(row['target']) for row in route['declared_steps']]]) + '</p>',
                  '<p>已知分项小计：希望授予 ' + str(subtotal['hope_grant_quantity']) + '；护盾授予 ' + str(subtotal['shield_grant_quantity']) +
                  '；随机收藏品 ' + str(subtotal['random_relic_quantity']) + '；出口加工品 ' + str(subtotal['random_move_item_quantity']) +
                  '；基础经验 ' + str(subtotal['base_experience']) + '；基础战斗及加工品源石锭 ' + esc(gold_reference_text(subtotal['gold'])) + '。</p>',
                  '<p>所列分项条件：' + ('闭合，仅限声明范围' if route['complete_modeled_grant_conditions'] else '仍有未知或失败，不给完整分项总量') + '。随机品的具名池、品质、价值和概率未证。</p>']
        for grant in route['grant_rows']:
            condition = '纳入条件数量小计' if grant['condition_matches'] is True else '条件未知，不纳入' if grant['condition_matches'] is None else '已列条件不符，不纳入'
            item = reference_data()['items'].get(grant.get('item_id'), {})
            parts += ['<p>步骤' + str(grant['step']) + ' ' + node(grant['node_id']) + '；' + esc(ORIGINS[grant['origin']]) +
                      ('（' + esc(item['name']) + '）' if item else '') + '：' + esc(RESOURCE_NAMES[grant['resource']]) +
                      ' ' + esc(grant['source_stated_quantity'] if grant['source_stated_quantity'] is not None else '未知') + '；' + condition + '。</p>']
            if grant.get('unresolved_reason'):
                parts.append('<p>边界：' + esc(REASONS.get(grant['unresolved_reason'], grant['unresolved_reason'])) + '。</p>')
        for passive in route['passive_availability_reference_state']:
            parts.append('<p>临时概念体余激活参考：' + esc(reference_data()['items'][passive['item_id']]['name']) +
                         ' ' + esc(passive.get('remaining_activations') if passive.get('remaining_activations') is not None else '未知') + '。</p>')
        for conflict in route['declaration_conflicts']:
            parts.append('<p>声明冲突：步骤' + str(conflict['step']) + ' ' + node(conflict['node_id']) + '；' +
                         esc(reference_data()['items'][conflict['item_id']]['name']) + '已声明激活，但余次数或节点来源条件不符，不能补第二次奖励。</p>')
        terminal = route['terminal_phase']
        if terminal:
            labels = {'main_region_advance': '进入下一主区域', 'portal_enter': '进入秘境', 'portal_return': '返回原区域'}
            parts.append('<p>独立转移阶段：' + labels[terminal['declaration']['transition']] + '；' +
                         ('声明成功且移动条件闭合' if terminal['admitted_to_conditional_terminal_phase'] else '声明成功或到达条件未闭合，未累计终端授予/损失') + '。</p>')
            names = {row['instance_id']: row['name'] for row in terminal['reference']['inventory_conditions']}
            parts.append('<p>条件损坏的余持有实例：' + esc('、'.join(names[key] + ' [' + key + ']' for key in terminal['conditional_expired_instances']) or '无已纳入实例') +
                         '；秘境例外条件保留：' + esc('、'.join(names[key] + ' [' + key + ']' for key in terminal['conditional_portal_preserved_instances']) or '无已纳入实例') + '。</p>')
            for item in terminal['unresolved_inventory_dispositions']:
                parts.append('<p>库存处置未知：小八界 [' + esc(item['instance_id']) + '] 返回原区域时是否损坏未证；文档只明确进入特殊层，不纳入已确认保留。</p>')
    for pair in data['pairwise_component_differences']:
        delta = pair['known_subtotal_difference_left_minus_right']
        parts.append('<h3>数量差值：' + esc(pair['left']) + ' 减 ' + esc(pair['right']) + '</h3><p>' +
                     ('同终点与转移声明的所列分项条件闭合。' if pair['conditional_component_difference'] is not None else '仅已知小计差值；终点、转移或分项条件未全部闭合，完整差值未知。') +
                     '希望授予差 ' + str(delta['hope_grant_quantity']) + '；护盾授予差 ' + str(delta['shield_grant_quantity']) +
                     '；随机收藏品数量差 ' + str(delta['random_relic_quantity']) + '；源石锭差值范围 ' +
                     esc(gold_reference_text(delta['gold_interval'])) + '。数量差不等于收益优劣，随机品价值不可比。</p>')
    parts += ['<p>实际最优、最终资源和完整收益：未知。没有将这些条件数量写入本局；未把战斗攻速资料或随机品未知价值加入资源总量。</p></body></html>']
    return ''.join(parts)


class _Signals(QObject): finished = Signal(int, object, str)
class _Worker(QRunnable):
    def __init__(self, serial, payload):
        super().__init__(); self.serial = serial; self.payload = deepcopy(payload); self.signals = _Signals()
    def run(self):
        try: self.signals.finished.emit(self.serial, route_resource_ledger(**self.payload), '')
        except Exception as exc: self.signals.finished.emit(self.serial, None, str(exc))


class RouteResourceLedgerPanel(ResidentRouteReviewPanel):
    """Reuse sealed graph/editor/snapshot/map guards, not resident game logic."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.preset.clear()
        for preset in public_resource_presets(): self.preset.addItem(preset['label'], preset['id'])
        self.add_resident.hide(); self.declare_victory.hide()
        self.layout().itemAt(0).widget().setText('路线资源授予账本：加工品、概念体、基础战斗与独立出口阶段分开核算。未知激活保持后续次数未知，不推断实际领取。')
        self.layout().itemAt(3).widget().setText('activation_declarations按路线ID、步骤文字序号、概念体ID声明true/false/null。after_battle_declarations独立声明战斗结束；terminals独立声明转移及success_declared。余AP不会由失败或未知尾链资助出口。所有JSON均可编辑删除。')
        row = QHBoxLayout(); self.passive_select = QComboBox()
        for key, item in reference_data()['items'].items():
            if item['kind'] == 'PASSIVE': self.passive_select.addItem(item['name'], key)
        self.phase_match = QComboBox()
        for value, label in [(True, '独立声明发生'), (False, '独立声明未发生'), (None, '阶段未知')]: self.phase_match.addItem(label, value)
        self.set_activation = QPushButton('设置选中步骤的概念体激活'); self.set_after_battle = QPushButton('设置选中步骤的战斗结束')
        for widget in [self.passive_select, self.phase_match, self.set_activation, self.set_after_battle]: row.addWidget(widget)
        self.layout().insertLayout(4, row)
        row = QHBoxLayout(); self.transition_select = QComboBox()
        for key, label in [('main_region_advance', '主区域前进'), ('portal_enter', '进入秘境'), ('portal_return', '返回原区域')]: self.transition_select.addItem(label, key)
        self.set_terminal = QPushButton('设置选中路线的独立转移声明'); row.addWidget(self.transition_select); row.addWidget(self.set_terminal)
        self.layout().insertLayout(5, row)
        self.set_activation.clicked.connect(self._set_activation); self.set_after_battle.clicked.connect(self._set_after_battle)
        self.set_terminal.clicked.connect(self._set_terminal); self.run_button.setText('核算声明路线的来源数量与出口'); self._load_example()

    def _load_example(self):
        preset = next((row for row in public_resource_presets() if row['id'] == self.preset.currentData()), public_resource_presets()[0])
        self._graph_import = None; self._write(preset['payload'])
        if hasattr(self, 'passive_select') and preset['payload'].get('passive_items'):
            self.passive_select.setCurrentIndex(self.passive_select.findData(preset['payload']['passive_items'][0]['item_id']))
        self.status.setText('已载入公开合成图和说明声明；不是当前观测。旧结果保留至重新核算。')

    def _set_activation(self):
        try:
            payload = self._payload(); identity = self.route_select.currentData(); ordinal = self.step_select.currentData(); key = self.passive_select.currentData()
            if not identity or not ordinal: raise ValueError('请选择路线与步骤。')
            if key not in {row.get('item_id') for row in payload.get('passive_items') or []}: raise ValueError('该概念体未在passive_items中声明持有，请先核对。')
            payload.setdefault('activation_declarations', {}).setdefault(identity, {}).setdefault(str(ordinal), {})[key] = self.phase_match.currentData()
            self._write(payload); self.status.setText('已独立声明概念体阶段；旧结果对应此前输入，请重新核算。')
        except Exception as exc: self.status.setText('未设置：' + str(exc))

    def _set_after_battle(self):
        try:
            payload = self._payload(); identity = self.route_select.currentData(); ordinal = self.step_select.currentData()
            if not identity or not ordinal: raise ValueError('请选择路线与步骤。')
            payload.setdefault('after_battle_declarations', {}).setdefault(identity, {})[str(ordinal)] = self.phase_match.currentData()
            self._write(payload); self.status.setText('已独立声明战斗结束阶段；不由基础奖励或抵达推定，请重新核算。')
        except Exception as exc: self.status.setText('未设置：' + str(exc))

    def _set_terminal(self):
        try:
            payload = self._payload(); identity = self.route_select.currentData(); route = next(row for row in payload['routes'] if row['id'] == identity)
            transition = self.transition_select.currentData(); declaration = {'transition': transition, 'success_declared': self.phase_match.currentData()}
            if transition == 'main_region_advance':
                target = route['steps'][-1]['target']; node = next(row for row in payload['graph']['nodes'] if row['id'] == target); types, _ = _type_candidates(node)
                if len(types) != 1 or types[0] not in ('FINAL', 'EVACUATE', 'BATTLE_BOSS'): raise ValueError('主区域转移需明确出口原类型；请核对终点。')
                declaration['exit_node_type'] = types[0]
            payload.setdefault('terminals', {})[identity] = declaration; self._write(payload)
            self.status.setText('已设置独立转移和成功声明；不由抵达推定，旧结果需重新核算。')
        except Exception as exc: self.status.setText('未设置：' + str(exc))

    def _run(self):
        try: payload = self._payload(); graph = payload.get('graph') or {}; bindings = self._bindings(graph)
        except Exception as exc: self.status.setText('未运行：' + str(exc)); return
        self._serial += 1; serial = self._serial; worker = _Worker(serial, payload); self._workers[serial] = worker
        self._contexts[serial] = {'graph': deepcopy(graph), 'links': bindings, 'input_text': self.editor.toPlainText()}
        worker.signals.finished.connect(self._finished); self.run_button.setEnabled(False)
        self.status.setText('正在核算临时来源数量与出口阶段……'); QThreadPool.globalInstance().start(worker)

    def _finished(self, serial, result, error):
        self._workers.pop(serial, None); context = self._contexts.pop(serial, {})
        if serial != self._serial: return
        self.run_button.setEnabled(True)
        if error: self.status.setText('未生成新结果：' + error + '；保留此前结果。'); return
        self._result = deepcopy(result); self._result_links = deepcopy(context['links']); self._result_input_text = context['input_text']
        self.result_view.setHtml(render_resource_ledger(result, context['graph'], self._result_links)); self.raw_result.setPlainText(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        self.status.setText('输入已修改，结果对应此前输入，请重新核算。' if self.editor.toPlainText() != self._result_input_text else '局外来源数量核算完成；实际领取、完整池和最终资源未知。')
        self.resultChanged.emit(deepcopy(result))
