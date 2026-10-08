from pathlib import Path
import datetime, hashlib, io, json, subprocess, sys, tarfile

base = Path(__file__).parent
root = Path('/workspace/rougezhushou')
commit = '225cb66dc89143a3cd3a884bd6c62f47ed9d36bc'
snapshot = base / 'baseline'
assert not snapshot.exists()
snapshot.mkdir()
paths = ['rouge', 'tests', 'PROJECT_PROGRESS.md', 'PROJECT_COMPLETED.md', 'research/p2-independent-events']
data = subprocess.check_output(['git', 'archive', commit, *paths], cwd=root)
with tarfile.open(fileobj=io.BytesIO(data)) as archive:
    archive.extractall(snapshot, filter='data')
files = {str(p.relative_to(snapshot)): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
         for p in sorted(snapshot.rglob('*')) if p.is_file()}
(base / 'baseline-freeze078.json').write_text(json.dumps(
    {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'commit': commit,
     'method': 'git archive exact committed public paths', 'root_wip_not_included': True,
     'file_count': len(files), 'files': files}, ensure_ascii=False, indent=2) + '\n')
sys.path.insert(0, str(snapshot))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
from rouge.operator_options import options_for

OP = 'char_4204_mantra'
tables = {}
sources = {}
for name, expected, size in (
    ('character_table', '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697', 14975251),
    ('skill_table', '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca', 11447929)):
    path = root / '.cache/p2-s1-binding' / (name + '.json')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected and len(raw) == size
    tables[name] = json.loads(raw)
    sources[name] = {'path': str(path), 'sha256': expected, 'bytes': size,
                     'existing_fixed_public_source_reused_no_download': True,
                     'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
                     'url': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/' + name + '.json'}
character = tables['character_table'][OP]
profile = catalog()['operators'][OP]
talent = character['talents'][0]
assert len(talent['candidates']) == len(profile['talents'][0]) == 4
for raw, local in zip(talent['candidates'], profile['talents'][0]):
    assert raw['name'] == local['name'] == '噤声限域'
    assert int(raw['unlockCondition']['phase'][-1]) == local['phase']
    assert raw['unlockCondition']['level'] == local['level'] == 1
    assert raw['requiredPotentialRank'] == local['potential_rank']
    assert {b['key']: b['value'] for b in raw['blackboard']} == local['values']
assert [(row['unlockCondition']['phase'], row['requiredPotentialRank']) for row in talent['candidates']] == [
    ('PHASE_1', 0), ('PHASE_1', 4), ('PHASE_2', 0), ('PHASE_2', 4)]
skills = {}
for number, raw in enumerate(character['skills'], 1):
    skill = tables['skill_table'][raw['skillId']]
    local = profile['skills'][number - 1]
    assert raw['skillId'] == local['id']
    assert raw['unlockCond']['phase'] == 'PHASE_' + str(local['unlock_elite'])
    assert len(skill['levels']) == len(local['levels']) == 10
    for level, projected in zip(skill['levels'], local['levels']):
        assert {b['key']: b['value'] for b in level['blackboard']} == projected['values']
    skills[str(number)] = {'character_skill_complete': raw, 'skill_table_complete': skill}
assert character['skills'][0]['unlockCond'] == {'phase': 'PHASE_0', 'level': 1}
selection = {}
for elite in (0, 1, 2):
    for potential in (1, 5):
        selection[f'E{elite}P{potential}'] = selected_talents(profile, {'elite': elite, 'level': 1, 'potential': potential})[0]
assert not selection['E0P1'] and not selection['E0P5']
control = next(row for row in options_for(OP, 1) if row[0] == 'palsy_triggers')
assert control == ('palsy_triggers', '窗口内目标麻痹触发次数', 0, 10000, (1, 2, 3))
raw_objects = {'operator_id': OP, 'character_table_complete_selected_character': character, 'skills_complete': skills}
(base / 'selected-original-objects078.json').write_text(json.dumps(raw_objects, ensure_ascii=False, indent=2) + '\n')
initial = json.loads((base / 'initial-public-results078.json').read_bytes())
assert initial['fixed_package_baseline'] == commit and initial['public_calls'] == len(initial['records']) == 8
for row in initial['records']:
    if row['request']['elite'] == 0:
        assert not row['selected_talents']
        assert row['full_result']['total_damage'] == (1900 if row['request']['palsy_triggers'] == 0 else None)
receipt = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'baseline_commit': commit,
           'baseline_public_files': len(files), 'sources': sources,
           'exact_talent_selector': 'character_table.char_4204_mantra.talents[0].candidates',
           'complete_raw_talent_bundle': talent, 'source_skill_bindings_all_30_levels_checked': True,
           'current_selected_talent_qualification_examples': selection,
           'palsy_declared_control': {'tuple': control, 'producer_kind': 'integer QSpinBox because default is int, not bool',
                                    'note': 'actual options builder code retained; no GUI execution'},
           'initial_public_calls': 8, 'initial_full_before_results_sha256': hashlib.sha256((base / 'initial-public-results078.json').read_bytes()).hexdigest(),
           'actual_mask_chain': ['not-normal Mantra caller validates palsy_triggers then emits absent-talent zero-damage positive count',
                                'preserve_unplaced_sources sets actual_total None whenever possible window and positive hits',
                                'mask_pending_damage turns direct total/phase/window/cycle fields unknown due that impossible source'],
           'narrow_fix': 'retain raw palsy parsing/count/range and metadata; only use zero effective emitted talent count when actual selected talent name is absent',
           'must_preserve': ['global external palsy declarations and sources', 'S3 overflow independent count', 'all E1/E2 selected outputs including base_attack0 unknowns',
                             'zero-current-enemy and zero-window boundaries', 'elemental resistance/immunity and first-hit guards', 'skill/training/input prior error precedence',
                             'actual source_possible window/lifetime meaning; not silently redefine it as cultivation qualification'],
           'existing_source_files': {name: files[name] for name in ('rouge/operator_engine.py', 'rouge/operator_options.py', 'rouge/damage.py',
               'rouge/uncertain_sources.py', 'rouge/reporting.py', 'tests/test_mantra_manual_events.py', 'research/p2-independent-events/NOTE.md')},
           'unknowns_unchanged': ['palsy origin/stack consumption order', 'actual event times/skill-stage snapshot', 'S1 same-hit new burst ordering',
                                  'S3 overflow multi-target return and actual interval'],
           '77_patch_not_included': True, 'no_tracked_private_gui_wine_or_native_binary_downloads': True}
(base / 'source-receipt078.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print({'baseline_commit': commit, 'public_files': len(files), 'original_first_talent_gates': [
    (row['unlockCondition'], row['requiredPotentialRank']) for row in talent['candidates']],
       'source_skill_bindings_all_30_levels_checked': True, 'palsy_control': control, 'initial_public_calls': 8,
       'E0_positive_declared_count_causes_wrong_unknown': True})
