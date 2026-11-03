from pathlib import Path
import collections, copy, datetime, hashlib, itertools, json, subprocess, sys

base = Path(__file__).parent
sys.path.insert(0, str(base / 'baseline'))
from rouge.catalog import catalog, stage_previews
from rouge.damage import calculate_damage
from rouge.operator_engine import selected_talents

OP = 'char_1015_aglna2'
root = Path('/workspace/rougezhushou')
commit = '225cb66dc89143a3cd3a884bd6c62f47ed9d36bc'
prior_dir = base / 'prior-research'
prior_dir.mkdir(exist_ok=True)
prior_names = ('research/p2-aglna-manual-weight/NOTE.md', 'research/p2-aglna-manual-weight/source-receipt.json')
prior = {}
for name in prior_names:
    raw = subprocess.check_output(['git', 'show', commit + ':' + name], cwd=root)
    path = prior_dir / Path(name).name
    path.write_bytes(raw)
    prior[name] = {'fixed_commit': commit, 'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
sources = {}
tables = {}
for name, expected, size in (
    ('character_table', '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697', 14975251),
    ('skill_table', '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca', 11447929)):
    path = root / '.cache/p2-s1-binding' / (name + '.json')
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    assert sha == expected and len(raw) == size
    tables[name] = json.loads(raw)
    sources[name] = {'path': str(path), 'sha256': sha, 'bytes': len(raw), 'existing_fixed_public_file_reused': True,
                     'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
                     'url': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/' + name + '.json'}
character = tables['character_table'][OP]
profile = catalog()['operators'][OP]
first = character['talents'][0]
assert len(first['candidates']) == len(profile['talents'][0]) == 4
for raw, projected in zip(first['candidates'], profile['talents'][0]):
    assert raw['name'] == projected['name'] == '飘浮大地之上'
    assert int(raw['unlockCondition']['phase'][-1]) == projected['phase']
    assert raw['unlockCondition']['level'] == projected['level'] == 1
    assert raw['requiredPotentialRank'] == projected['potential_rank']
    assert {b['key']: b['value'] for b in raw['blackboard']} == projected['values']
assert [(t['unlockCondition']['phase'], t['requiredPotentialRank']) for t in first['candidates']] == [
    ('PHASE_1', 0), ('PHASE_1', 2), ('PHASE_2', 0), ('PHASE_2', 2)]
skills = {}
for number, raw in enumerate(character['skills'], 1):
    skill = tables['skill_table'][raw['skillId']]
    projected = profile['skills'][number - 1]
    assert raw['skillId'] == projected['id']
    assert raw['unlockCond']['phase'] == 'PHASE_' + str(projected['unlock_elite'])
    assert len(skill['levels']) == len(projected['levels']) == 10
    for level, local in zip(skill['levels'], projected['levels']):
        assert {b['key']: b['value'] for b in level['blackboard']} == local['values']
    skills[str(number)] = {'character_skill_complete': raw, 'skill_table_complete': skill}
raw_objects = {'operator_id': OP, 'character_table_complete_selected_character': character, 'skills_complete': skills}
(base / 'selected-original-objects077.json').write_text(json.dumps(raw_objects, ensure_ascii=False, indent=2) + '\n')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


before_catalog = digest(catalog())
before_previews = digest(stage_previews())
records = []
seen = set()


def add(group, request):
    key = canonical(request)
    if key in seen:
        return
    seen.add(key)
    request = json.loads(key)
    original = copy.deepcopy(request)
    row = {'group': group, 'request': original}
    try:
        result = json.loads(canonical(calculate_damage(request)))
        row['full_result'] = result
        row['full_result_sha256'] = digest(result)
        row['selected_talents'] = selected_talents(profile, request)[0]
    except Exception as error:
        row['error'] = {'type': type(error).__name__, 'message': str(error)}
    assert request == original
    records.append(row)


for elite, maximum, potential, mode, weight, window in itertools.product((0, 1, 2), (False, True), (1, 3),
                                                                     ('frames', 'continuous'), (3, 4), (0, 10)):
    level = profile['phases'][elite]['max_level'] if maximum else 1
    add('source_qualification_and_actual_E0_phantom_events',
        {'operator': OP, 'skill': 1, 'elite': elite, 'level': level, 'potential': potential, 'skill_rank': 1,
         'timing_mode': mode, 'enemy_weight': weight, 'window_seconds': window})
for elite, skill, mode, zero in itertools.product((0, 1, 2), (1, 2, 3), ('frames', 'continuous'), (False, True)):
    add('skill_unlock_and_zero_global_enemy_lifetime_controls',
        {'operator': OP, 'skill': skill, 'elite': elite, 'skill_rank': 1, 'timing_mode': mode, 'window_seconds': 10,
         **({'timing': {'target_disappears_seconds': 0}} if zero else {})})
for value in (True, '4', None, -1, 101, 3.5):
    add('prior_manual_weight_errors_preserved_even_when_talent_locked',
        {'operator': OP, 'skill': 1, 'elite': 0, 'skill_rank': 1, 'enemy_weight': value})
assert digest(catalog()) == before_catalog and digest(stage_previews()) == before_previews
(base / 'readonly-public-results077.json').write_text(json.dumps(
    {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'public_calls': len(records), 'records': records,
     'callers_and_public_catalog_and_stage_previews_preserved': True}, ensure_ascii=False, indent=2) + '\n')
phantom = [row for row in records if 'full_result' in row and not row['selected_talents'] and
           any(c['name'] == '飘浮大地之上' and c['hits'] > 0 for c in row['full_result']['components'])]
owners = {op: {'name': p['name'], 'talent_candidates_projection': p['talents']}
          for op, p in catalog()['operators'].items()
          if op not in {'char_206_gnosis', 'char_437_mizuki', 'char_4087_ines', 'char_1035_wisdel', 'char_4202_haruka'}}
receipt = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'baseline_commit': commit,
           'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'sources': sources, 'prior_research': prior,
           'exact_character_selector': 'character_table.char_1015_aglna2',
           'exact_first_talent_selector': 'character_table.char_1015_aglna2.talents[0].candidates',
           'first_talent_complete_raw_bundle': first,
           'all_three_skills_all_30_levels_bb_projection_checked': True,
           'E0_skill1_unlock_verified': True, 'E0_has_no_selected_first_talent_verified': True,
           'readonly_public_calls': len(records), 'positive_window_E0_phantom_talent_component_examples': len(phantom),
           'original_predicate_is_cultivation_phase_and_level_and_potential_not_weight_alone': True,
           'weight_damage_formula_unchanged_and_existing_source_reused': True,
           'source_names_or_neighbor_flags_not_used_to_infer_qualification': True,
           'rejected_neighbor_hypothesis': 'Yato first talent actually starts at E0 with .06; no missing qualification and no patch.',
           'scanned_other_owner_projection_not_full_original_dictionaries': owners,
           'narrow_candidate': 'Only when Aglna first talent is not selected, retain the zero-valued component shape but suppress its phantom event hit count/timestamps in skill/window/ordinary-recharge plans. Keep existing weight validation, all numerical totals, training and completion flags.',
           'unknowns_unchanged': ['native extra-damage snapshot/order/hotfix beyond prior coverage', 'S2 actual takeoff/start/end clock', 'global manual-weight interpretation remains a reference, not runtime target identity'],
           'no_tracked_edits': True, 'no_gui_wine_private_or_native_binary_downloads': True}
(base / 'source-receipt077.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print({'readonly_public_calls': len(records), 'positive_window_E0_phantom_examples': len(phantom),
       'first_talent_gates': [(t['unlockCondition'], t['requiredPotentialRank']) for t in first['candidates']],
       'skill1_unlock': character['skills'][0]['unlockCond'], 'sources': sources,
       'prior_errors': dict(collections.Counter(row['error']['message'] for row in records if 'error' in row))})
