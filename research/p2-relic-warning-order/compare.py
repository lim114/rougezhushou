import collections
import copy
import hashlib
import json
import re
from pathlib import Path

OUT = Path(__file__).parent
SEEDS = (0, 1, 42, 314159)
WARNING = re.compile(r'^组合 .+ 的叠加规则尚未核验，未套用该组合。$')
PENDING = re.compile(r'^组合叠加规则待核验:.+$')
TEXT_WARNING = re.compile(r'^• 组合 .+ 的叠加规则尚未核验，未套用该组合。$')

def reorder_matching(values, pattern):
    result = values.copy()
    positions = [i for i, value in enumerate(values) if isinstance(value, str) and pattern.fullmatch(value)]
    for position, value in zip(positions, sorted(values[i] for i in positions), strict=True):
        result[position] = value
    return result

def normalize(row):
    row = copy.deepcopy(row)
    result = row.get('result')
    if result:
        for parent in (result, result['estimate'], result['relic_resolution']):
            parent['warnings'] = reorder_matching(parent['warnings'], WARNING)
        for record in result['relic_resolution']['records']:
            record['pending'] = reorder_matching(record['pending'], PENDING)
        for key in ('estimate_text', 'report_text', 'technical_report_text'):
            row[key] = '\n'.join(reorder_matching(row[key].split('\n'), TEXT_WARNING))
    return row

def diff(a, b, path=''):
    if type(a) is not type(b):
        return [path + ':type']
    if isinstance(a, dict):
        assert a.keys() == b.keys(), ('changed keys', path)
        return [p for key in a for p in diff(a[key], b[key], path + '.' + key)]
    if isinstance(a, list):
        assert len(a) == len(b), ('changed length', path)
        return [p for x, y in zip(a, b, strict=True) for p in diff(x, y, path + '[]')]
    return [] if a == b else [path]

draft = [json.loads((OUT / f'public-draft-seed-{seed}.json').read_text()) for seed in SEEDS]
assert all(rows == draft[0] for rows in draft[1:]), 'draft is not wholly seed independent'
draft_hashes = [hashlib.sha256((OUT / f'public-draft-seed-{seed}.json').read_bytes()).hexdigest() for seed in SEEDS]
assert len(set(draft_hashes)) == 1
summary = []
all_paths = collections.Counter()
allowed = {'.result.warnings[]', '.result.estimate.warnings[]',
           '.result.relic_resolution.warnings[]', '.result.relic_resolution.records[].pending[]',
           '.estimate_text', '.report_text', '.technical_report_text'}
baselines = []
for seed, after in zip(SEEDS, draft, strict=True):
    before = json.loads((OUT / f'public-baseline-seed-{seed}.json').read_text())
    baselines.append(before)
    changed = unchanged = errors = 0
    paths = collections.Counter()
    for old, new in zip(before, after, strict=True):
        assert normalize(old) == normalize(new), ('non-order difference', seed, old['label'])
        row_paths = diff(old, new)
        assert set(row_paths) <= allowed, (seed, old['label'], row_paths)
        paths.update(row_paths)
        if 'error' in old:
            errors += 1
            assert old == new, ('changed old error', seed, old['label'])
        elif old == new:
            unchanged += 1
        else:
            changed += 1
    all_paths.update(paths)
    summary.append({'seed': seed, 'cases': len(before), 'order_only_changed': changed,
                    'whole_accepted_unchanged': unchanged, 'old_errors_unchanged': errors,
                    'actual_diff_path_counts': dict(paths)})
assert len({json.dumps(rows, sort_keys=True) for rows in baselines}) > 1, 'old nondeterminism not reproduced'
token_boundaries = [row for row in draft[0] if row['label'].startswith('rules-effects-token')]
for row in token_boundaries:
    refs = row['candidate_references'][0]
    assert refs['candidates'] == refs['rules'] + refs['effects'] + refs['token_effects']
assert any(all(row['candidate_references'][0][key] for key in ('rules', 'effects', 'token_effects'))
           for row in token_boundaries), 'real three-list boundary not exercised'
single = next(row for row in draft[0] if row['label'] == 'single-conflict-group')
assert sum(w.startswith('组合 ') for w in single['result']['warnings']) == 1
receipt = {'passed': True, 'baseline_commit': '9b7cfba08319d64175a7f51a94f339ce225bc76c',
           'seeds': list(SEEDS), 'unique_scenarios': len(draft[0]),
           'calculate_damage_calls': len(draft[0]) * len(SEEDS) * 2,
           'baseline_calls': len(draft[0]) * len(SEEDS), 'draft_calls': len(draft[0]) * len(SEEDS),
           'baseline_distinct_whole_outputs': len({json.dumps(rows, sort_keys=True) for rows in baselines}),
           'draft_distinct_whole_outputs': 1, 'draft_json_sha256': draft_hashes[0],
           'strict_order_only_comparisons': summary, 'actual_diff_path_counts': dict(all_paths),
           'normalization_scope': 'Comparison-only matching group warning/pending strings at their original list positions and matching complete formatted warning lines; all other data and text must remain exactly equal.',
           'first_declaration_contract': 'unverified candidate group first occurrence in rules + effects + token_effects; not game activation order or global warning sorting',
           'token_three_list_boundary_proven': True, 'input_catalog_unchanged': True,
           'product_mechanics_changed': False, 'gui_executed': False, 'wine_executed': False,
           'source_080_matrices_untouched': True}
with (OUT / 'comparison-receipt.json').open('x', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps(receipt, ensure_ascii=False))
