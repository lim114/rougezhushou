"""Strict independent comparison of saved real output. No calculation calls."""
from pathlib import Path
import collections
import hashlib
import json
import math
import re

OUT = Path(__file__).resolve().parent
PARENT = Path('/workspace/.continuation/p2-amiya-trait-scale-080')
OP = 'char_1037_amiya3'
MODULE = 'uniequip_002_amiya3'
HEAL = '咒愈师伤害转治疗'
HEAL_METRICS = {
    ('healing', 'active_hps'), ('healing', 'hps'), ('healing', 'per_cast'),
    ('healing', 'window_healing'), ('healing', 'window_hps'),
    ('amiya_phase', 'opening_healing'),
    ('known_healing_subtotals', 'cast'), ('known_healing_subtotals', 'window'),
}
NUMERIC_KEYS = {'total_healing', 'phase_healing', 'window_healing', 'cycle_healing', 'cycle_hps', 'window_hps'}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def equivalent(a, b):
    return json.dumps(a, ensure_ascii=False, sort_keys=True, allow_nan=False) == json.dumps(b, ensure_ascii=False, sort_keys=True, allow_nan=False)


def diff(a, b, path=()):
    if type(a) is not type(b): return [path]
    if isinstance(a, dict):
        assert a.keys() == b.keys(), ('key shape changed', path)
        return [p for key in a for p in diff(a[key], b[key], path + (key,))]
    if isinstance(a, list):
        assert len(a) == len(b), ('list shape changed', path)
        return [p for index, (x, y) in enumerate(zip(a, b)) for p in diff(x, y, path + (index,))]
    return [path] if a != b else []


def at(value, path):
    for part in path: value = value[part]
    return value


def allowed(path, before, after):
    a, b = at(before, path), at(after, path)
    assert type(a) is type(b), ('type changed', path, a, b)
    if path[0] in ('estimate_text', 'report_text', 'technical_report_text'):
        assert len(path) == 1
        # The formatter source is unchanged. All underlying damage/timing fields
        # are compared strictly; rendered words and line structure must also stay.
        assert re.sub(r'[-+]?\d[\d,.]*', '<number>', a) == re.sub(r'[-+]?\d[\d,.]*', '<number>', b), ('rendered wording changed', path)
        return True
    if not path or path[0] != 'result': return False
    numeric = type(a) in (int, float) and type(b) in (int, float)
    if not numeric: return False
    p = path[1:]
    if p == ('total_healing',): return True
    if len(p) == 3 and p[:2] == ('estimate', 'skill') and p[2] in NUMERIC_KEYS: return True
    if len(p) == 2 and p[0] == 'known_healing_subtotals' and p[1] in NUMERIC_KEYS: return True
    if p in [('amiya_phase_reference', 'opening_healing_reference'),
             ('amiya_phase_reference', 'window_reference', 'opening_healing_reference')]: return True
    if p[0] == 'components':
        component = after['result']['components'][p[1]]
        if component['name'] != HEAL: return False
        tail = p[2:]
        return tail in [('per_hit',), ('total',), ('damage_healing', 'ratio')] or (
            len(tail) == 2 and tail[0] == 'event_amounts' and type(tail[1]) is int) or (
            len(tail) == 3 and tail[0] == 'known_healing_sources' and tail[2] in ('total', 'per_hit')) or (
            len(tail) == 4 and tail[0] == 'known_healing_sources' and tail[2] == 'event_amounts')
    if len(p) == 6 and p[:2] == ('report', 'sections') and p[3] == 'metrics' and p[5] == 'value':
        section = after['result']['report']['sections'][p[2]]
        metric = section['metrics'][p[4]]
        return (section['id'], metric['key']) in HEAL_METRICS
    return False


def assert_close(a, b, context):
    assert math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-8), (context, a, b)


def coefficient(s):
    if s['operator'] != OP: return None
    elite = s.get('elite', 2)
    level = s.get('level') or {0: 50, 1: 70, 2: 80}[elite]
    return .6 if s.get('module_id') == MODULE and elite == 2 and level >= 50 else .5


def check_pair(x, y):
    assert equivalent(x['scenario'], y['scenario'])
    if 'error' in x or 'error' in y:
        assert equivalent(x, y), ('old error changed', x.get('label', x.get('index')))
        return 'exact_old_error', []
    r = y['result']; old = x['result']; s = y['scenario']
    paths = diff(x, y)
    for path in paths:
        assert allowed(path, x, y), ('unauthorized difference', x.get('label', x.get('index')), path)
    if s['operator'] != OP:
        assert not paths
        return 'whole_accepted_same', paths
    ratio = coefficient(s) * min(1, s.get('healing_targets', 1))
    c = next(c for c in r['components'] if c['name'] == HEAL)
    old_c = next(c for c in old['components'] if c['name'] == HEAL)
    assert c['damage_healing']['ratio'] == ratio
    if coefficient(s) == .5 or ratio == 0:
        assert not paths, ('unchanged qualification changed', s)
    factors = s.get('relic_ids', [])
    factor = 1.2 if factors == ['rogue_6_relic_legacy_81'] else 1
    parents = [r['components'][i] for i in c['damage_healing']['sources']]
    assert_close(c['total'], sum(parent['total'] for parent in parents) * ratio * factor, 'settled damage to direct healing')
    if c['hits']:
        assert_close(c['per_hit'], c['total'] / c['hits'], 'per hit')
    else:
        assert c['per_hit'] == 0
    for source in c.get('known_healing_sources', []):
        parent = next(p for p in parents if p['name'] == source['name'])
        assert_close(source['total'], parent['total'] * ratio * factor, 'known parent healing total')
        assert_close(source['per_hit'], parent['per_hit'] * ratio * factor, 'known parent healing per hit')
    for field in ('complete', 'timing', 'warnings', 'scope', 'total_damage', 'known_damage_subtotals'):
        assert equivalent(r.get(field), old.get(field)), field
    old_components = {component['name']: component for component in old['components']}
    for component in r['components']:
        if component['name'] != HEAL:
            assert equivalent(component, old_components[component['name']]), component['name']
    if s['skill'] == 1:
        assert_close(r['total_healing'], sum(component['total'] for component in r['components'] if component['damage_type'] == 'healing'), 'S1 whole direct healing')
        skill, old_skill = r['estimate']['skill'], old['estimate']['skill']
        delta_ratio = ratio - old_c['damage_healing']['ratio']
        for heal_key, damage_key in [('total_healing', 'total_damage'), ('phase_healing', 'phase_damage'), ('cycle_healing', 'cycle_damage')]:
            if old_skill[heal_key] is not None and old_skill[damage_key] is not None:
                assert_close(skill[heal_key], old_skill[heal_key] + old_skill[damage_key] * delta_ratio * factor, 'S1 phase/cycle oracle ' + heal_key)
        if 'window_seconds' not in s and s.get('healing_targets', 1) > 0 and skill['cycle_damage'] != skill['phase_damage']:
            # Preserve the pre-existing half-open phase treatment convention.
            # Continuous rank7 can leave the unchanged boundary AoE reference
            # in this residual, so compare the trait's incremental contribution.
            assert_close((skill['cycle_healing'] - skill['phase_healing']) -
                         (old_skill['cycle_healing'] - old_skill['phase_healing']),
                         (old_skill['cycle_damage'] - old_skill['phase_damage']) *
                         delta_ratio * factor, 'normal recharge same-trait increment; old AoE boundary preserved')
    else:
        amiya = r['amiya_phase_reference']
        for field in ('actual_strengthening_start_seconds', 'actual_skill_end_seconds'):
            assert amiya[field] is None
        assert amiya['phase_clock_verified'] is False
        assert amiya['opening_buff_healing_order_verified'] is False
        for field in ('duration_seconds', 'recharge_seconds', 'cycle_seconds'):
            assert r['estimate']['skill'][field] is None
        assert r['total_damage'] is old['total_damage'] is None or r['total_damage'] == old['total_damage']
        assert (r['total_healing'] is None) == (old['total_healing'] is None)
        if s.get('base_attack') == 0 and s.get('healing_targets', 1) > 0:
            assert r['total_damage'] is None and r['total_healing'] is None
        if factors == ['rogue_6_relic_legacy_81']:
            assert r['relic_regeneration_multiplier'] == 1.2
            regeneration = next(component for component in r['components'] if component['name'] == '诚挚期许本体生命回复')
            per_hp = {1: .025, 2: .03, 3: .035}[s['module_level']]
            assert_close(regeneration['per_hit'], r['estimate']['base_stats']['hp'] * per_hp * 1.2, 'independent regeneration existing factor')
            assert regeneration['actual_total'] is None
    if len(factors) == 2:
        assert '组合 heal_scale 的叠加规则尚未核验，未套用该组合。' in r['warnings']
        assert '组合 received_regeneration 的叠加规则尚未核验，未套用该组合。' in r['warnings']
        assert r['complete'] is False
    return ('whole_accepted_same' if not paths else 'derived_trait_healing_only'), paths


def compare(before_path, after_path, expected_count):
    before = json.loads(before_path.read_text()); after = json.loads(after_path.read_text())
    assert len(before) == len(after) == expected_count
    counts = collections.Counter(); fields = collections.Counter(); results = []
    for x, y in zip(before, after):
        group, paths = check_pair(x, y)
        counts[group] += 1
        for path in paths:
            fields['.'.join('*' if type(p) is int else p for p in path)] += 1
        results.append({'label': x.get('label', x.get('index')), 'group': group, 'changed_field_count': len(paths)})
    return {'pairs': expected_count, 'classification': dict(counts), 'changed_fields': dict(fields),
            'results': results, 'saved_inputs': [{'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path)} for path in (before_path, after_path)],
            'new_public_calls_for_comparison': 0}


independent = compare(OUT / 'baseline-public080.json', OUT / 'draft-public080.json', 82)
author = compare(PARENT / 'public-baseline80.json', PARENT / 'public-draft80.json', 818)
assert author['classification'] == {'whole_accepted_same': 496, 'derived_trait_healing_only': 246, 'exact_old_error': 76}
new_tests = json.loads((OUT / 'independent-new-tests080.json').read_text())
assert new_tests['status'] == 'passed' and new_tests['tests_run'] == 9 and new_tests['skipped'] == 0
freeze = json.loads((OUT / 'freeze080.json').read_text())
for rel, entries in freeze['sources'].items():
    for kind in ('baseline', 'draft'):
        assert sha(PARENT / kind / rel) == entries[kind + '_sha256'], (kind, rel)
assert sha(Path(freeze['new_test']['path'])) == freeze['new_test']['sha256']
receipt = {'status': 'passed_final_numeric_review', 'independent_source_review_directory': '/workspace/.continuation/p2-amiya-trait-080-independent-readonly',
           'source_review_unchanged': True, 'independent_new_public_pairs': independent,
           'readonly_author_saved_matrix_review': author, 'actual_independent_public_calls': 164,
           'actual_public_calls_inside_nine_new_tests': new_tests['actual_public_calls_inside_new_tests'],
           'total_actual_new_public_calls_by_this_numeric_reviewer': 164 + new_tests['actual_public_calls_inside_new_tests'],
           'independent_tests_run': 9, 'new_api_calls_for_818_saved_matrix': 0,
           'source_file_count_no_drift': len(freeze['sources']), 'hash_seed': '0',
           'qt_executed': False, 'wine_executed': False, 'native_windows_executed': False, 'tracked_edits': False,
           'limits': 'Frozen section 77 + section 80 draft only; section 79 own-regeneration gate will be integrated separately by root. No native clocks/attachment/friendly treatment proof.'}
target = OUT / 'numeric-review080.json'
with target.open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2); stream.write('\n')
print(json.dumps({'status': receipt['status'], 'independent': independent['classification'], 'author_saved': author['classification'],
                  'actual_public_calls': receipt['total_actual_new_public_calls_by_this_numeric_reviewer'],
                  'receipt_sha256': sha(target)}, ensure_ascii=False))
