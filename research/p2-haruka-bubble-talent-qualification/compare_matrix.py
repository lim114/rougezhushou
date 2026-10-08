"""Strict complete JSON/error pairs; locked results match old zero-event controls."""
import copy
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTE = '当前培养尚未解锁扶摇花火；浮泡破碎声明保留，但不产生该天赋治疗或二技能中依赖该治疗的派生伤害。'


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def normalize_declaration(result):
    result = copy.deepcopy(result)
    for ref in (result['external_event_reference'], result['external_event_reference']['window_reference']):
        ref['parameter_rows'][0] = ['声明窗口内浮泡破碎次数', 0.0, '次']
        ref['notes'] = [note for note in ref['notes'] if note != NOTE]
    for section in result['report']['sections']:
        if section['id'] == 'external_events':
            section['notes'] = [note for note in section['notes'] if note != NOTE]
            next(m for m in section['metrics'] if m['key'] == 'parameter_0')['value'] = 0.0
    return result


with gzip.open(ROOT / 'public-baseline.json.gz', 'rt', encoding='utf-8') as f:
    before = json.load(f)
with gzip.open(ROOT / 'public-draft.json.gz', 'rt', encoding='utf-8') as f:
    after = json.load(f)
assert len(before) == len(after)
totals = Counter()
labels = {}
changed_cases = []
for index, (a, b) in enumerate(zip(before, after)):
    assert canonical(a['scenario']) == canonical(b['scenario']) and a['label'] == b['label']
    label = a['label']
    counts = labels.setdefault(label, Counter())
    args = a['scenario']
    ao, bo = a['outcome'], b['outcome']
    if 'error' in ao:
        assert canonical(ao) == canonical(bo), (index, args, 'error changed')
        status = 'prior_error_unchanged'
    elif 'zero_count_control' in a:
        assert 'zero_count_control' in b
        ca, cb = a['zero_count_control'], b['zero_count_control']
        assert canonical(ca) == canonical(cb), (index, args, 'zero control drift')
        assert canonical(normalize_declaration(bo['result'])) == canonical(ca['outcome']['result']), (index, args, 'unexpected output change')
        expected = float(args['bubble_bursts'])
        assert bo['result']['external_event_reference']['parameter_rows'][0][1] == expected
        assert bo['result']['external_event_reference']['parameter_rows'][0] == ao['result']['external_event_reference']['parameter_rows'][0]
        for name in ('扶摇花火', '浮泡治疗衍生伤害'):
            matched = [c for c in bo['result']['components'] if c['name'] == name]
            for c in matched:
                assert c['hits'] == 0 and c['total'] == 0 and 'actual_total' not in c
        status = 'locked_talent_excluded_matches_whole_old_zero_control'
        changed_cases.append({'index': index, 'label': label, 'elite': args['elite'], 'skill': args['skill'],
                              'before_total_healing': ao['result']['total_healing'],
                              'after_total_healing': bo['result']['total_healing'],
                              'before_total_damage': ao['result']['total_damage'],
                              'after_total_damage': bo['result']['total_damage']})
    else:
        assert canonical(ao) == canonical(bo), (index, args, 'unexpected whole-output drift')
        status = 'whole_output_unchanged'
    totals[status] += 1
    counts[status] += 1

artifacts = {}
for name in ('public-baseline.json.gz', 'public-draft.json.gz'):
    raw = (ROOT / name).read_bytes()
    artifacts[name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
receipt = {'baseline_commit': '153b5dbf15d6567746047cbdea7f8d00a6879f3a',
           'comparison': 'strict canonical complete JSON, including numeric JSON types and exact prior errors',
           'total_pairs': len(before), 'totals': dict(totals),
           'labels': {key: dict(value) for key, value in labels.items()},
           'zero_count_control_pairs': sum('zero_count_control' in a for a in before),
           'fresh_public_calls_total': 2 * (len(before) + sum('zero_count_control' in a for a in before)),
           'whole_e2_output_preserved': True, 'raw_declaration_preserved': True,
           'native_clock_attachment_composition_promoted': False, 'artifacts': artifacts,
           'changed_cases': changed_cases}
(ROOT / 'matrix-comparison.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: receipt[key] for key in ('total_pairs', 'totals', 'zero_count_control_pairs', 'fresh_public_calls_total')}, ensure_ascii=False))
