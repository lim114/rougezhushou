"""Close only the cooperative checkbox path and its pinned original selectors."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'frozen'))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents

REPO = Path('/workspace/rougezhushou')
COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
sources = {}
raws = {}
for name, expected in (
        ('character_table.json', '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
        ('skill_table.json', '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca')):
    path = REPO / '.cache/p2-s1-binding' / name
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected
    raws[name] = json.loads(data)
    sources[name] = {'sha256': expected, 'bytes': len(data), 'fresh_local_hash_verified': True,
                     'url': f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{COMMIT}/zh_CN/gamedata/excel/{name}'}

profile = catalog()['operators']['silverash']
character = raws['character_table.json']['char_1045_svash2']
binding = character['skills'][2]
assert profile['id'] == 'char_1045_svash2'
assert profile['name'] == '凛御银灰'
assert binding['skillId'] == 'skchr_svash2_3'
assert binding['overrideTokenKey'] == 'token_10057_svash2_eagle3'
assert binding['unlockCond'] == {'phase': 'PHASE_2', 'level': 1}
assert profile['skills'][2]['unlock_elite'] == 2
token = raws['character_table.json'][binding['overrideTokenKey']]
token_binding = token['skills'][2]
assert token_binding['skillId'] == 'sktok_svash2_3'
records = []
for rank in range(10):
    own = raws['skill_table.json']['skchr_svash2_3']['levels'][rank]
    companion = raws['skill_table.json']['sktok_svash2_3']['levels'][rank]
    normalized = profile['skills'][2]['levels'][rank]
    bb = {row['key']: row['value'] for row in own['blackboard']}
    assert bb == normalized['values']
    assert own['description'] == normalized['description']
    assert own['duration'] == normalized['duration']
    records.append({'own_selector': f'skill_table.skchr_svash2_3.levels[{rank}]',
                    'own_record': own,
                    'token_selector': f'skill_table.sktok_svash2_3.levels[{rank}]',
                    'token_record': companion, 'normalized_own_values_equal': True})

talent_cases = []
for elite in (0, 1, 2):
    for potential in (1, 5, 6):
        args = {'operator': 'silverash', 'elite': elite, 'potential': potential}
        talents, parts = selected_talents(profile, args)
        talent_cases.append({'scenario': args, 'selected_talents': talents, 'module_parts': parts})

previous = {}
for path in (Path('/workspace/.continuation/p2-preexisting-fragile-input-064/source-receipt064.json'),
             Path('/workspace/.continuation/p2-four-sui-text-input-062/prior-readonly-audit/contract-audit.json'),
             REPO / 'research/p2-declared-count-input-types/NOTE.md'):
    previous[str(path)] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                           'bytes': path.stat().st_size}
code = {}
for name in ('rouge/damage.py', 'rouge/estimate.py', 'rouge/reporting.py', 'rouge/app.py',
             'rouge/operator_engine.py', 'rouge/data/catalog.json'):
    path = ROOT / 'frozen' / name
    code[name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
receipt = {
    'baseline_head': '0e0d098e8bc8444cd74fb74f32754cc0ff78ecfb', 'source_game_commit': COMMIT,
    'raw_sources': sources, 'source_files': code, 'reused_receipts': previous,
    'alias_binding': {'public_operator': 'silverash', 'native_id': profile['id'], 'name': profile['name']},
    'actual_skill_binding_selector': 'character_table.char_1045_svash2.skills[2]',
    'actual_skill_binding_record': binding,
    'actual_token_binding_selector': 'character_table.token_10057_svash2_eagle3.skills[2]',
    'actual_token_binding_record': token_binding,
    'token_description': token['description'], 'token_talents': token['talents'],
    'own_raw_talents': character['talents'], 'selected_named_talent_cases': talent_cases,
    'all_ten_selected_own_and_token_skill_records': records,
    'actual_execution_path': [
        'calculate_damage -> _prepare_damage: validate skill/rank/cultivation/unlock before legacy path',
        'silverash uses _skill_damage_base, not Combat.calculate; silver S3 is the exact active branch',
        'raw scenario.get(cooperative) truthiness clones the existing own component as 协同丹增',
        'build_estimate recomputes cast/window/cycle through the same compute_skill callback',
        'build_report summon section also uses exact silverash S3 cooperative truthiness; no text parser exists',
        'Named self talents select initial SP/redeploy/defense/regen references; they do not determine this checkbox'],
    'qt_source_contract': {'widget': 'MainWindow.cooperative QCheckBox', 'label': '协同攻击持续覆盖同一目标',
        'visibility': "operator=='silverash' and skill==3", 'serializer': 'self.cooperative.isChecked()',
        'serialized_type': 'Python bool', 'gui_executed_in_this_audit': False},
    'supported_source_facts': [
        'The S3 own binding overrides exactly eagle3 and unlocks at PHASE_2 level1.',
        'sktok_svash2_3 explicitly says the first operator deployment during the skill deploys eagle at that position and it performs simultaneous line attacks; subsequent redeployment can change position.',
        'The offline checkbox declares sustained coverage of the same target; arbitrary text itself confirms neither deployment nor coverage.',
        'Existing own bird_atk_scale and token S3 bird_atk_scale are pinned rank parameters; no new numerical factor is derived from the input audit.'],
    'unknown_mechanisms_not_inferred': [
        'Actual deployment and position or how many simultaneous targets are covered',
        'Real cooperative event ownership, precise release/hit clocks, collision and shared-event ordering',
        'ATK snapshot attachment, external modifiers and fragile stacking/first application/expiry',
        'Hidden cnt/weak[limit] fields do not establish a new cooperative count or overlap rule',
        'Live hotfix equivalence or native gameplay verification'],
    'native_research_reuse': '064 scanned existing local native receipts with no matching S3 template/CFG; no new native search result or absence-of-implementation claim is made.',
    'patch_written': False, 'global_boolean_policy_changed': False, 'tracked_edits': False}
(ROOT / 'source-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'source_game_commit': COMMIT, 'raw_hashes_fresh_verified': True,
                  'skill_rank_pairs': len(records), 'selected_talent_cases': len(talent_cases),
                  'actual_s3_token_override_verified': True, 'patch_written': False}))
