"""Editable public visit-policy plans, with guarded links to imported maps."""
from copy import deepcopy
import html
import json
from urllib.parse import quote, unquote

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QPlainTextEdit, QTextBrowser, QSplitter, QLineEdit, QGroupBox)

from .route_constraints import constrained_routes
from .exploration_planning import reference_data
from .base_settlement_planning import gold_reference_text


def public_constraint_presets():
    """Synthetic declarations: none of these nodes are current game observations."""
    graph = {'current_node': 's', 'zone_id': 'zone_1', 'template_id': 'public-policy-demo',
             'nodes': [{'id': key, 'row': row, 'col': col, 'base_node_type': 'EMPTY'}
                       for key, row, col in [('s', 0, 0), ('a', 0, 1), ('b', 1, 0),
                                             ('c', 1, 1), ('g', 0, 2)]],
             'edges': [['s', 'a'], ['a', 'g'], ['s', 'b'], ['b', 'c'], ['c', 'g'], ['a', 'c']]}
    basic = {'graph': graph, 'goal': 'g', 'action_points': 8,
             'required_nodes': ['b'], 'avoid_nodes': [], 'checkpoints': [],
             'qualifications': {}, 'max_steps': 5, 'max_results': 20, 'max_transitions': 200}
    ordered = deepcopy(basic); ordered.update(required_nodes=[], checkpoints=['b', 'c'], avoid_nodes=['a'])
    unknown = deepcopy(ordered)
    unknown['qualifications'] = {'c': {'matches': None, 'reason': '示例：此节点的入口资格尚未确认'}}
    failed = deepcopy(ordered)
    failed['qualifications'] = {'c': {'matches': False, 'reason': '示例：声明入口条件不符'}}
    limited = deepcopy(ordered); limited['max_steps'] = 2
    return [{'id': 'required', 'label': '必须经过指定节点', 'payload': basic},
            {'id': 'ordered', 'label': '顺序检查点与避开节点', 'payload': ordered},
            {'id': 'unknown', 'label': '未知入口保留停止前沿', 'payload': unknown},
            {'id': 'failed', 'label': '已声明入口不符', 'payload': failed},
            {'id': 'limited', 'label': '步数不足保留缺项', 'payload': limited}]


def _label(graph, key):
    node = next((row for row in (graph or {}).get('nodes', []) if row.get('id') == key), None)
    if not node:
        return str(key) + '（位置未绑定）'
    raw = node.get('base_node_type') or node.get('node_type_raw')
    name = node.get('observed_type') or reference_data()['node_types'].get(raw, {}).get('name') or '类型未知'
    return f"第{node['row'] + 1}行、第{node['col'] + 1}列 · {name} · {key}"


REASONS = {
    'declared_avoided_node': '进入了声明要避开的节点',
    'declared_checkpoint_order_mismatch': '提前进入了后续顺序检查点',
    'declared_entry_qualification_failed': '声明的节点准入条件不符',
    'declared_entry_qualification_unknown': '声明的节点准入条件未知，保留前沿',
    'declared_goal_prerequisites_missing': '已到声明终点，但仍缺必经节点或顺序检查点',
    'remaining_constraints_exceed_step_budget': '剩余必经节点、检查点与终点超出步数预算',
    'depth_limit': '达到最大步数', 'transition_limit': '达到分支检查上限',
    'result_limit': '达到结果数量上限', 'action_points_unknown': '起始行动力未知',
    'known_condition_or_ap_failed': '已列移动条件不符或行动力不足',
    'eligibility_or_inventory_condition_unknown': '加工品资格、次数或随机目的地未知',
    'zero_ap_callback_order_unverified': '付款到零，耗尽与返还顺序未证',
    'node_arrival_ap_condition_unknown': '到达节点的行动力条件未知',
}


def render_constraint_result(data, graph, links=None):
    links = links or {}
    esc = lambda value: html.escape(str(value))
    def node(key):
        label = esc(_label(graph, key))
        return '<a href="rouge-map-node:' + quote(key, safe='') + '">' + label + '</a>' if key in links else label
    def path(steps):
        return ' → '.join([node(data['start']), *[node(step['target']) for step in steps]])
    parts = ['<html><body><h2>必经、避开与顺序路线规划</h2>',
             '<p>这些约束与准入条件来自您的声明。它们不证明游戏结局前置、真实可达、胜利或完整收益。</p>',
             '<p>声明终点：' + node(data['goal_node']) + '</p>']
    policy = data['policy']
    for key, label in [('required_nodes', '必经节点'), ('avoid_nodes', '避开节点'), ('checkpoints', '顺序检查点')]:
        parts.append('<p>' + label + '：' + (' → '.join(node(key) for key in policy[key]) or '未声明') + '</p>')
    parts.append('<p>分支检查 ' + str(data['examined_transitions']) + '；完整声明候选 ' + str(len(data['plans'])) +
                 '；停止前沿 ' + str(len(data['frontier'])) + '；声明排除 ' + str(len(data['policy_exclusions'])) +
                 '。上限：' + esc(REASONS.get(data['limit_reason'], '未触发上限')) + '；等待前缀 ' +
                 str(data['pending_prefixes_at_limit']) + '；未检查兄弟分支 ' +
                 str(data['pending_sibling_options_at_limit']) + '。</p>')
    by_id = {row['id']: row for row in (data['comparison'] or {}).get('routes', [])}
    for plan in data['plans']:
        reference = by_id[plan['id']]
        parts += ['<h3>' + esc(plan['name']) + '</h3><p>' + path(plan['steps']) + '</p>',
                  '<p>必经与顺序声明相符；不是实机准入核验。净行动力消耗参考：' +
                  esc(reference['net_ap_consumption_reference']) + '；已知基础战斗经验小计：' +
                  esc(reference['known_base_subtotal']['experience']) + '；已知基础源石锭：' +
                  esc(gold_reference_text(reference['known_base_subtotal']['gold'])) + '。</p>']
        parts.append('<p>移动方式：' + '；'.join(
            str(ordinal) + ' ' + ('步行' if step['mode'] == 'walking' else '加工品实例 ' + esc(step['mode']))
            for ordinal, step in enumerate(plan['steps'], 1)) + '。</p>')
        if reference['conditional_base_total'] is None:
            parts.append('<p>战斗结算仍有未证或失败条件；上述仅为已知分项，不能当作完整总量。</p>')
    for field, title in [('frontier', '停止前沿：未知条件或预算边界'),
                         ('policy_exclusions', '按显式声明排除的分支')]:
        parts.append('<h3>' + title + '</h3>')
        if not data[field]:
            parts.append('<p>本次没有记录。</p>')
        for row in data[field]:
            parts += ['<p>' + path(row['steps']) + '<br>' + esc(REASONS.get(row['reason'], row['reason'])) + '</p>']
            declaration = row.get('qualification_declaration')
            if declaration and declaration.get('reason'):
                parts.append('<p>声明理由：' + esc(declaration['reason']) + '</p>')
            if row['remaining_required_nodes']:
                parts.append('<p>尚缺必经节点：' + '、'.join(node(key) for key in row['remaining_required_nodes']) + '</p>')
            if row['remaining_checkpoints']:
                parts.append('<p>后续检查点：' + ' → '.join(node(key) for key in row['remaining_checkpoints']) + '</p>')
    parts += ['<p>实际终点可达性、完整收益、动态住民、失败概率与最优路线：未知。没有候选不证明实际不存在路线。</p>',
              '<p>避开节点指不进入该节点；加工品直达仍使用固定几何，未定义飞越路径。停止前沿不作为后续资源来源。</p>',
              '</body></html>']
    return ''.join(parts)


class _Signals(QObject):
    finished = Signal(int, object, str)


class _Worker(QRunnable):
    def __init__(self, serial, payload):
        super().__init__(); self.serial = serial; self.payload = deepcopy(payload); self.signals = _Signals()
    def run(self):
        try:
            self.signals.finished.emit(self.serial, constrained_routes(**self.payload), '')
        except Exception as exc:
            self.signals.finished.emit(self.serial, None, str(exc))


class RouteConstraintsPanel(QWidget):
    mapNodeSelected = Signal(str, object)
    resultChanged = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._graph_cache = self._graph_import = None
        self._result = None; self._result_links = {}; self._workers = {}; self._contexts = {}; self._serial = 0
        self._result_input_text = None
        layout = QVBoxLayout(self)
        intro = QLabel('必经节点、避开节点和顺序检查点用于局外路线规划。节点准入只使用您的显式声明；未知保留停止前沿。不会推定游戏结局前置或改变本局。')
        intro.setWordWrap(True); layout.addWidget(intro)
        row = QHBoxLayout(); self.preset = QComboBox()
        for preset in public_constraint_presets():
            self.preset.addItem(preset['label'], preset['id'])
        self.load_example = QPushButton('加载公开声明示例'); self.import_graph = QPushButton('导入缓存地图声明')
        row.addWidget(self.preset); row.addWidget(self.load_example); row.addWidget(self.import_graph); layout.addLayout(row)
        row = QHBoxLayout(); self.graph_node = QComboBox(); self.node_action = QComboBox()
        for key, label in [('goal', '设置终点'), ('required_nodes', '加入必经节点'),
                           ('avoid_nodes', '加入避开节点'), ('checkpoints', '追加顺序检查点'),
                           ('qualifications', '设置节点准入声明')]:
            self.node_action.addItem(label, key)
        self.qualification = QComboBox()
        for value, label in [(True, '声明条件相符'), (False, '声明条件不符'), (None, '条件未知')]:
            self.qualification.addItem(label, value)
        self.qualification_reason = QLineEdit(); self.qualification_reason.setPlaceholderText('准入声明理由（可留空）')
        self.apply_node = QPushButton('应用选中节点')
        for widget in [self.graph_node, self.node_action, self.qualification, self.qualification_reason, self.apply_node]:
            row.addWidget(widget)
        layout.addLayout(row)
        guide = QLabel('required_nodes：必须进入；avoid_nodes：不进入；checkpoints：按顺序进入。qualifications以节点ID为键，matches为true/false/null。修改JSON可删除约束及设置行动力、库存、独立战斗声明和上限。所有示例参数都是说明声明。')
        guide.setWordWrap(True); layout.addWidget(guide)
        splitter = QSplitter(Qt.Orientation.Vertical); self.editor = QPlainTextEdit(); self.result_view = QTextBrowser()
        self.result_view.setOpenLinks(False); self.result_view.setOpenExternalLinks(False)
        splitter.addWidget(self.editor); splitter.addWidget(self.result_view); layout.addWidget(splitter, 1)
        self.run_button = QPushButton('构造满足声明约束的候选'); layout.addWidget(self.run_button)
        self.status = QLabel(''); self.status.setWordWrap(True); layout.addWidget(self.status)
        group = QGroupBox('技术结果（JSON，可展开）'); group.setCheckable(True); group.setChecked(False)
        group_layout = QVBoxLayout(group); self.raw_result = QPlainTextEdit(); self.raw_result.setReadOnly(True)
        group_layout.addWidget(self.raw_result); self.raw_result.setVisible(False)
        group.toggled.connect(self.raw_result.setVisible); layout.addWidget(group)
        self.load_example.clicked.connect(self._load_example); self.import_graph.clicked.connect(self._import_graph)
        self.apply_node.clicked.connect(self._apply_node); self.editor.textChanged.connect(self._editor_changed)
        self.node_action.currentIndexChanged.connect(self._update_node_action)
        self.run_button.clicked.connect(self._run); self.result_view.anchorClicked.connect(self._map_anchor)
        self._load_example(); self._update_node_action()

    def _payload(self):
        try:
            value = json.loads(self.editor.toPlainText(), parse_constant=lambda value: (_ for _ in ()).throw(ValueError('不支持非有限数值。')))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError('输入JSON无法读取：' + str(exc)) from exc
        if not isinstance(value, dict):
            raise ValueError('输入需要JSON对象。')
        return value

    def _write(self, payload):
        self.editor.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))

    def _load_example(self):
        payload = next(row['payload'] for row in public_constraint_presets() if row['id'] == self.preset.currentData())
        self._graph_import = None; self._write(payload)
        self.status.setText('已载入公开合成图与说明声明。不是当前游戏地图；旧结果保留至重新运行。')

    def set_graph(self, graph, *, epoch=None, historical=False):
        """Refresh cache only: preserve editor, selected node, result and scroll."""
        self._graph_cache = {'graph': deepcopy(graph), 'epoch': epoch, 'historical': bool(historical)} if isinstance(graph, dict) else None
        self.import_graph.setEnabled(self._graph_cache is not None)

    def _refresh_nodes(self):
        selected = self.graph_node.currentData(); self.graph_node.blockSignals(True); self.graph_node.clear()
        try:
            graph = self._payload().get('graph') or {}
            for node in graph.get('nodes', []):
                if isinstance(node, dict) and isinstance(node.get('id'), str) and type(node.get('row')) is int and type(node.get('col')) is int:
                    self.graph_node.addItem(_label(graph, node['id']), node['id'])
            index = self.graph_node.findData(selected)
            if index >= 0:
                self.graph_node.setCurrentIndex(index)
        except Exception:
            pass
        self.graph_node.blockSignals(False); self.apply_node.setEnabled(self.graph_node.currentData() is not None)
        self.import_graph.setEnabled(self._graph_cache is not None)

    def _editor_changed(self):
        self._refresh_nodes()
        running = self._contexts.get(self._serial)
        if running and self.editor.toPlainText() != running['input_text']:
            self.status.setText('正在核算运行时的此前声明；输入已修改，完成结果将对应此前输入。')
        elif self._result is not None and self.editor.toPlainText() != self._result_input_text:
            self.status.setText('声明已修改；当前显示结果对应此前输入，请重新构造。')

    def _update_node_action(self):
        active = self.node_action.currentData() == 'qualifications'
        self.qualification.setVisible(active); self.qualification_reason.setVisible(active)

    def _apply_node(self):
        try:
            payload = self._payload(); key = self.graph_node.currentData(); field = self.node_action.currentData()
            if not key:
                raise ValueError('请选择声明图节点。')
            if field == 'goal':
                payload[field] = key
            elif field == 'qualifications':
                value = payload.get(field) or {}
                if not isinstance(value, dict):
                    raise ValueError('qualifications需要对象。')
                value[key] = {'matches': self.qualification.currentData(), 'reason': self.qualification_reason.text()}
                payload[field] = value
            else:
                value = payload.get(field) or []
                if not isinstance(value, list):
                    raise ValueError(field + '需要列表。')
                if key not in value:
                    value.append(key)
                payload[field] = value
            self._write(payload); self.status.setText('已修改临时声明。请重新构造候选；不改变实际地图或本局。')
        except Exception as exc:
            self.status.setText('未修改：' + str(exc))

    def _import_graph(self):
        try:
            if not self._graph_cache:
                raise ValueError('没有可导入的缓存地图。')
            payload = self._payload(); payload['graph'] = deepcopy(self._graph_cache['graph'])
            self._graph_import = deepcopy(self._graph_cache); self._write(payload)
            self.status.setText('已显式导入缓存地图；终点、必经、避开、顺序、资格与资源声明保留，请核对节点ID是否仍适用。')
        except Exception as exc:
            self.status.setText('未导入：' + str(exc))

    @staticmethod
    def _layout(graph):
        if not isinstance(graph, dict) or not isinstance(graph.get('nodes'), list):
            return None
        rows = []
        for node in graph['nodes']:
            if (not isinstance(node, dict) or not isinstance(node.get('id'), str) or
                    type(node.get('row')) is not int or type(node.get('col')) is not int):
                return None
            rows.append((node['id'], node['row'], node['col']))
        return graph.get('zone_id'), graph.get('template_id'), tuple(sorted(rows))

    def _bindings(self, graph):
        imported = self._graph_import
        if (not imported or imported.get('epoch') is None or not graph.get('zone_id') or
                not graph.get('template_id') or self._layout(graph) != self._layout(imported['graph'])):
            return {}
        return {node['id']: {'epoch': imported['epoch'], 'zone_id': graph['zone_id'],
                            'template_id': graph['template_id'], 'node_id': node['id'],
                            'row': node['row'], 'col': node['col']} for node in graph['nodes']}

    def _run(self):
        try:
            payload = self._payload(); graph = payload.get('graph') or {}
            bindings = self._bindings(graph)
        except Exception as exc:
            self.status.setText('未运行：' + str(exc)); return
        self._serial += 1; serial = self._serial
        worker = _Worker(serial, payload); self._workers[serial] = worker
        self._contexts[serial] = {'graph': deepcopy(graph), 'links': bindings,
                                  'input_text': self.editor.toPlainText()}
        worker.signals.finished.connect(self._finished)
        self.run_button.setEnabled(False); self.status.setText('正在核算临时声明图与独立资源账本……')
        QThreadPool.globalInstance().start(worker)

    def _finished(self, serial, result, error):
        self._workers.pop(serial, None); context = self._contexts.pop(serial, {})
        if serial != self._serial:
            return
        self.run_button.setEnabled(True)
        if error:
            self.status.setText('未生成新结果：' + error + '；保留此前结果。'); return
        self._result = deepcopy(result); self._result_links = deepcopy(context['links'])
        self._result_input_text = context['input_text']
        self.result_view.setHtml(render_constraint_result(result, context['graph'], self._result_links))
        self.raw_result.setPlainText(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        if self.editor.toPlainText() != self._result_input_text:
            self.status.setText('此前运行的声明规划完成；输入已修改，当前显示结果对应此前输入，请重新构造。')
        else:
            self.status.setText('局外声明规划完成。停止前沿、缺少条件与上限均已保留；实际可达和最优路线未知。')
        self.resultChanged.emit(deepcopy(result))

    def _map_anchor(self, url):
        if url.scheme() != 'rouge-map-node':
            return
        key = unquote(url.path()); binding = self._result_links.get(key); cache = self._graph_cache
        current = (cache or {}).get('graph') or {}
        nodes = current.get('nodes')
        node = next((row for row in nodes if isinstance(row, dict) and row.get('id') == key), None) if isinstance(nodes, list) else None
        if (not binding or not cache or cache['epoch'] != binding['epoch'] or not node or
                current.get('zone_id') != binding['zone_id'] or current.get('template_id') != binding['template_id'] or
                type(node.get('row')) is not int or type(node.get('col')) is not int or
                node['row'] != binding['row'] or node['col'] != binding['col']):
            self.status.setText('地图链接已过期或来源未绑定；请显式导入缓存地图后重新运行。'); return
        self.mapNodeSelected.emit(key, deepcopy(binding))

    def result_snapshot(self):
        return deepcopy(self._result)
