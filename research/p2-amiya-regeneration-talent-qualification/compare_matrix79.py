"""Permit only unavailable regeneration counts and their one unplaced disclosure."""
import copy
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = '诚挚期许本体生命回复'
UNPLACED = '尚未统一排入时间轴的输出分项：' + NAME + '。'


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def expected_locked_outcome(original):
    expected = copy.deepcopy(original)
    result = expected['result']
    c = next(c for c in result['components'] if c['name'] == NAME)
    assert c['per_hit'] == 0 and c['total'] == 0.0 and type(c['total']) is float
    c['hits'] = 0.0
    result['estimate']['skill']['hit_counts'][NAME] = 0.0
    if result['timing']['mode'] == 'frames':
        result['timing']['unplaced_components'] = [x for x in result['timing']['unplaced_components'] if x != NAME]
        result['estimate']['notes'] = [x for x in result['estimate']['notes'] if x != UNPLACED]
        # format_report derives this final visible line from estimate.notes;
        # do not permit any other report edits or a newly fabricated note.
        expected['text_report'] = '\n'.join(line for line in expected['text_report'].split('\n') if line != '• ' + UNPLACED)
    return expected


with gzip.open(ROOT / 'public-baseline79.json.gz', 'rt', encoding='utf-8') as f:
    before = json.load(f)
with gzip.open(ROOT / 'public-draft79.json.gz', 'rt', encoding='utf-8') as f:
    after = json.load(f)
assert len(before) == len(after)
counts = Counter()
labels = {}
for index, (a, b) in enumerate(zip(before, after)):
    assert a['label'] == b['label'] and canonical(a['scenario']) == canonical(b['scenario'])
    args = a['scenario']
    ao, bo = a['outcome'], b['outcome']
    if 'error' in ao:
        assert canonical(ao) == canonical(bo), (index, args, 'old error drift')
        kind = 'prior_errors_same'
    elif args['operator'] == 'char_1037_amiya3' and args.get('elite', 2) == 0:
        expected = expected_locked_outcome(ao)
        assert canonical(expected) == canonical(bo), (index, args, 'non-allowed complete JSON/report change')
        kind = 'only_locked_regeneration_counts_and_unplaced_disclosure'
    else:
        assert canonical(ao) == canonical(bo), (index, args, 'qualified-or-other-owner whole-output drift')
        kind = 'whole_accepted_same'
    counts[kind] += 1
    labels.setdefault(a['label'], Counter())[kind] += 1
artifacts = {}
for name in ('public-baseline79.json.gz', 'public-draft79.json.gz'):
    raw = (ROOT / name).read_bytes()
    artifacts[name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
receipt = {'baseline_commit': '4dd778488c96864a778ccbc25c0cf11cddfa5d86', 'status': 'PASS',
    'pairs': len(before), 'fresh_public_calls': 2 * len(before), 'counts': dict(counts),
    'comparison': 'Strict canonical complete JSON numeric types, exact old errors and complete format_report strings.',
    'allowed_paths': ['components[only name=诚挚期许本体生命回复].hits',
        'estimate.skill.hit_counts.诚挚期许本体生命回复', 'timing.unplaced_components removal of this exact name only',
        'estimate.notes removal of this exact sole-source unplaced disclosure only',
        'format_report removal of the exact derived sole-source disclosure line only'],
    'qualified_e1_e2_native_clocks_none_scope_and_numerics_preserved': True,
    'legitimate_zero_hp_public_boundary': 'unavailable: base_hp is ignored and negative manual hp_pct rejected; no fabricated verified-rule flag used',
    'labels': {key: dict(v) for key, v in labels.items()}, 'artifacts': artifacts}
(ROOT / 'matrix-comparison79.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: receipt[key] for key in ('status', 'pairs', 'fresh_public_calls', 'counts')}, ensure_ascii=False))
