"""Typed full saved comparison; normalize only actual conflicting group messages."""
import copy
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-relic-warning-order-081')
SEEDS = (0, 1, 42, 314159)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def groups_for(row):
    refs = row['candidate_references']
    if not refs:
        return []
    assert len(refs) == 1
    refs = refs[0]
    assert canonical(refs['candidates']) == canonical(refs['rules'] + refs['effects'] + refs['token_effects'])
    candidates = refs['candidates']
    groups = list(dict.fromkeys(r.get('group') for r in candidates if r.get('stacking') == 'unverified'))
    return [group for group in groups if len({r['relic_id'] for r in candidates if r.get('group') == group}) > 1]


def warning(group):
    return '组合 ' + str(group) + ' 的叠加规则尚未核验，未套用该组合。'


def reorder_exact(values, messages):
    result = list(values)
    positions = [i for i, value in enumerate(values) if value in messages]
    for pos, value in zip(positions, sorted(values[i] for i in positions), strict=True):
        result[pos] = value
    return result


def normalize(row):
    normalized = copy.deepcopy(row)
    if 'result' not in normalized:
        return normalized
    groups = groups_for(row)
    warnings = {warning(group) for group in groups}
    pending = {'组合叠加规则待核验:' + str(group) for group in groups}
    result = normalized['result']
    for parent in (result, result['estimate'], result['relic_resolution']):
        parent['warnings'] = reorder_exact(parent['warnings'], warnings)
    for record in result['relic_resolution']['records']:
        record['pending'] = reorder_exact(record['pending'], pending)
    for key in ('estimate_text', 'report_text', 'technical_report_text'):
        normalized[key] = '\n'.join(reorder_exact(normalized[key].split('\n'), {'• ' + w for w in warnings}))
    return normalized


receipt = {'status': 'PASS', 'saved_calculate_calls_repeated': 0, 'saved_pairs_reviewed': 140,
           'author_saved_calls': 280, 'seed_summaries': [], 'input_hashes': {}}
draft_bytes = []
for seed in SEEDS:
    rows = []
    for tree in ('baseline', 'draft'):
        path = AUTHOR / f'public-{tree}-seed-{seed}.json.gz'
        raw = path.read_bytes()
        uncompressed = gzip.decompress(raw)
        assert uncompressed == path.with_suffix('').read_bytes()
        receipt['input_hashes'][str(path)] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
                                            'decompressed_sha256': hashlib.sha256(uncompressed).hexdigest()}
        rows.append(json.loads(uncompressed))
        if tree == 'draft':
            draft_bytes.append(uncompressed)
    assert len(rows[0]) == len(rows[1]) == 35
    counts = Counter()
    for old, new in zip(*rows, strict=True):
        assert canonical(old['scenario']) == canonical(new['scenario'])
        assert canonical(normalize(old)) == canonical(normalize(new)), (seed, old['label'], 'non-allowed typed JSON/text drift')
        if 'error' in old:
            assert canonical(old) == canonical(new)
            counts['exact_old_errors'] += 1
        else:
            groups = groups_for(new)
            actual = [w for w in new['result']['relic_resolution']['warnings'] if w in {warning(g) for g in groups}]
            assert actual == [warning(g) for g in groups], (seed, new['label'], 'not first candidate order')
            if canonical(old) == canonical(new):
                counts['whole_accepted_same'] += 1
            else:
                counts['only_group_warning_pending_order'] += 1
    receipt['seed_summaries'].append({'seed': seed, 'pairs': 35, 'counts': dict(counts)})
assert all(raw == draft_bytes[0] for raw in draft_bytes[1:])
receipt['draft_all_four_seeds_byte_equal_without_normalizing'] = True
receipt['draft_raw_json_sha256'] = hashlib.sha256(draft_bytes[0]).hexdigest()
receipt['normalization'] = 'Only exact messages generated from actual captured conflicting candidate groups, at their original list or text-line positions; typed complete canonical JSON otherwise.'
(OUT / 'independent-saved-comparison081.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in receipt.items() if k != 'input_hashes'}, ensure_ascii=False))
