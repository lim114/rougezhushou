"""Convert public game-layout facts, never execute downloaded JavaScript."""
import collections
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache/research/maps'


def literal(source, name):
    start = source.index(name + '=') + len(name) + 1
    assert source[start] == '['
    quoted = escaped = False
    depth = 0
    for end in range(start, len(source)):
        char = source[end]
        if quoted:
            if escaped: escaped = False
            elif char == '\\': escaped = True
            elif char == '"': quoted = False
            continue
        if char == '"': quoted = True
        elif char in '[{': depth += 1
        elif char in ']}':
            depth -= 1
            if depth == 0: break
    value = source[start:end + 1]
    value = re.sub(r'([{,])([A-Za-z_$][\w$]*):', r'\1"\2":', value)
    value = value.replace('1/0', 'null')
    return json.loads(value)


def main():
    payload = (CACHE / 'arkrog-map.js').read_bytes()
    raw = payload.decode('utf-8')
    templates = literal(raw, 'me')
    rules = literal(raw, 'ue')
    output = {'source': {
        'url': 'https://arkrog.com/tool/blackflowmap',
        'asset_url': 'https://arkrog.com/assets-v2/index-C-GScw2O.js',
        'asset_sha256': hashlib.sha256(payload).hexdigest(),
        'evidence': 'community_collected_layouts_and_rules',
        'date': '2026-10-02',
        'note': '转换布局坐标、连线和生成范围事实；不复制或执行第三方程序代码。不是官方隐藏生成脚本。',
    }, 'templates': [], 'rules': {}}
    for item in templates:
        pairs = [(tuple(e[:2]), tuple(e[2:])) for e in item['edges']]
        occupied = {v for edge in pairs for v in edge} | {tuple(item['start'])}
        adj = {n: set() for n in occupied}
        for a, b in pairs:
            assert a != b and abs(a[0]-b[0])+abs(a[1]-b[1]) == 1
            adj[a].add(b); adj[b].add(a)
        start = tuple(item['start']); distance = {start: 0}; queue = collections.deque([start])
        while queue:
            a = queue.popleft()
            for b in adj[a]:
                if b not in distance: distance[b] = distance[a]+1; queue.append(b)
        assert len(distance) == len(occupied), item['id']
        ends = {tuple(v) for v in item.get('ends', [])}
        boss = tuple(item['battleEnd']) if item.get('battleEnd') else None
        battles = {tuple(v) for v in item.get('knownBattles', [])}
        shops = {tuple(v) for v in item.get('knownShops', [])}
        fixed = {start: '起点', **{v: '险路尽头' for v in ends},
                 **{v: '作战' for v in battles}, **{v: '诡意行商' for v in shops}}
        if boss: fixed[boss] = '险路恶敌'
        assert all(v in occupied for v in fixed), item['id']
        def key(n): return f'{n[0]},{n[1]}'
        output['templates'].append({
            'id': item['id'], 'zone_id': item['zone'], 'rows': item['rows'], 'cols': item['cols'],
            'start': key(start), 'ends': [key(v) for v in sorted(ends)],
            'boss': key(boss) if boss else None,
            'nodes': [{'id': key(n), 'row': n[0], 'col': n[1], 'distance': distance[n],
                       'fixed_type': fixed.get(n)} for n in sorted(occupied)],
            'edges': [[key(a), key(b)] for a, b in pairs],
        })
    for item in rules:
        if item['name'].startswith('未知'): continue
        output['rules'][item['name']] = {'category': item['type'],
            'zones': {step['zone']: {'min': step.get('min'), 'max': step.get('max'),
                                    'max_count': step.get('maxAllowed')} for step in item['steps']}}
    path = ROOT / 'rouge/data/map-templates.json'
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'templates': len(output['templates']),
                      'by_zone': dict(collections.Counter(t['zone_id'] for t in output['templates'])),
                      'rules': len(output['rules']), 'source': output['source']}, ensure_ascii=False))


if __name__ == '__main__': main()
