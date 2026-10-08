"""Topic 6 technology display references; no account unlock or numeric effects."""
from collections import Counter
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
import re


@lru_cache(maxsize=1)
def _data():
    return json.loads((Path(__file__).with_name('data')/'technology-reference.json').read_text(encoding='utf-8'))


def technology_nodes(query=''):
    needle = query.strip().casefold()
    return [deepcopy(node) for node in _data()['developments'].values()
            if not needle or needle in (node['buffName']+' '+' '.join(node['rawDesc'])).casefold()]


def technology_node(node_id):
    node = _data()['developments'].get(node_id)
    if node is None:
        raise ValueError('没有找到该长期科技节点。')
    return deepcopy(node)


def technology_gates():
    return deepcopy(_data()['developmentsDifficultyNodeInfos'])


def technology_labels():
    nodes = technology_nodes()
    counts = Counter(n['buffName'] for n in nodes)
    seen = Counter()
    labels = {}
    for node in nodes:
        name = node['buffName']; seen[name] += 1
        labels[node['buffId']] = name+(f'（{seen[name]}/{counts[name]}）' if counts[name]>1 else '')
    return labels


def _plain(text):
    return re.sub(r'<(?:@[^>]*|\$[^>]*|/)>', '', text).replace('\\n', '\n')


def format_technology(node_id, *, technical=False):
    node = technology_node(node_id); labels = technology_labels()
    kinds = {'NORMAL': '普通节点', 'KEY': '关键节点', 'DIFFICULTY': '难度门槛节点'}
    lines = [labels[node_id], kinds.get(node['nodeType'], node['nodeType']),
             f"花费：{node['tokenCost']}", '', *(_plain(t) for t in node['rawDesc'])]
    gate = technology_gates().get(node_id)
    if gate:
        lines += ['', '生效门槛资料：'+gate['enableDesc']]
    for key, label in (('frontNodeId', '前置显示节点'), ('nextNodeId', '后续显示节点')):
        lines += ['', label+'：'+('、'.join(labels[n] for n in node[key]) or '无')]
    lines += ['', '账户解锁状态：未知。这里只展示科技资料，未将效果加入本局计算。',
              '节点连接表示资料中的展示关系；多个前置节点的解锁判定仍待核验。']
    if technical:
        source = _data()['source']
        lines += ['', '节点ID：'+node_id, '固定来源：'+source['url'],
                  '原始位置：'+source['selector'], '原件SHA256：'+source['sha256']]
    return '\n'.join(lines)
