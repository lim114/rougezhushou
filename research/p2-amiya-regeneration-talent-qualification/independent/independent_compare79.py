"""Independent complete JSON typed-number and report comparison; no API calls."""
import copy
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

REVIEW = Path(__file__).resolve().parent
AUTHOR = REVIEW.with_name('p2-amiya-regeneration-talent-qualification-079')
NAME = '诚挚期许本体生命回复'
NOTE = '尚未统一排入时间轴的输出分项：' + NAME + '。'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False)


def compare(before, after):
    assert len(before) == len(after)
    counts = Counter()
    for i, (a, b) in enumerate(zip(before, after)):
        assert canonical(a['scenario']) == canonical(b['scenario'])
        assert a.get('label') == b.get('label')
        original, changed = a['outcome'], b['outcome']
        args = a['scenario']
        if 'error' in original:
            assert canonical(original) == canonical(changed), (i, 'error drift')
            counts['exact_old_errors'] += 1
            continue
        if args['operator'] == 'char_1037_amiya3' and args.get('elite', 2) == 0:
            expected = copy.deepcopy(original)
            result = expected['result']
            component = [c for c in result['components'] if c['name'] == NAME]
            assert len(component) == 1
            component = component[0]
            assert component['per_hit'] == 0
            assert type(component['total']) is float and component['total'] == 0.0
            component['hits'] = 0.0
            result['estimate']['skill']['hit_counts'][NAME] = 0.0
            if result['timing']['mode'] == 'frames':
                result['timing']['unplaced_components'] = [
                    x for x in result['timing']['unplaced_components'] if x != NAME]
                result['estimate']['notes'] = [x for x in result['estimate']['notes'] if x != NOTE]
                expected['text_report'] = '\n'.join(
                    x for x in expected['text_report'].split('\n') if x != '• ' + NOTE)
            assert canonical(expected) == canonical(changed), (i, 'non-allowed typed JSON/report drift')
            assert canonical(original) != canonical(changed), (i, 'accepted locked case unexpectedly unchanged')
            counts['only_missing_talent_count_disclosure'] += 1
        else:
            assert canonical(original) == canonical(changed), (i, 'qualified or other-form drift')
            counts['whole_accepted_same'] += 1
    return dict(counts)


receipt = {'status': 'PASS', 'API_calls_by_this_script': 0, 'sets': {}, 'input_artifacts': {}}
for label, directory, prefix in (
        ('saved_author_1366', AUTHOR, 'public'), ('fresh_independent_62', REVIEW, 'independent-public')):
    paths = [directory / (prefix + suffix) for suffix in ('-baseline79.json.gz', '-draft79.json.gz')]
    rows = [json.loads(gzip.decompress(p.read_bytes())) for p in paths]
    receipt['sets'][label] = {'pairs': len(rows[0]), 'counts': compare(*rows)}
    for p in paths:
        raw = p.read_bytes()
        receipt['input_artifacts'][str(p)] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
receipt['fresh_public_calls_in_separate_processes'] = 124
receipt['saved_author_2732_calls_not_repeated'] = True
receipt['comparison'] = 'Canonical entire JSON preserves int/float; exact old errors; entire report strings.'
receipt['zero_HP_ordinary_input_unavailable_not_tested'] = True
(REVIEW / 'independent-strict-comparison79.json').write_text(
    json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt['sets'], ensure_ascii=False))
