import hashlib
import json
import sys
from pathlib import Path

OUT = Path(__file__).parent
ROOT = Path('/workspace/rougezhushou')
sys.path.insert(0, str(OUT / 'baseline'))
from rouge.catalog import catalog, operator_profiles

def digest(p):
    b = p.read_bytes()
    return {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}

rawpath = ROOT / '.cache/p2-s1-binding/character_table.json'
skillpath = ROOT / '.cache/p2-s1-binding/skill_table.json'
raw = json.loads(rawpath.read_text())
source = raw['char_298_susuro']
forms = []
for op, profile in catalog()['operators'].items():
    native = {'kaltsit': 'char_1052_kalts2', 'silverash': 'char_1045_svash2', 'mechanist': 'char_4230_mcnist'}.get(op, op)
    original = raw.get(native)
    row = {'operator': op, 'native_id': native, 'name': profile['name'], 'rarity': operator_profiles()[op]['rarity'],
           'phase_max_levels': [x['max_level'] for x in profile['phases']],
           'skills': [{'id': s['id'], 'unlock_elite': s['unlock_elite'], 'rank_count': len(s['levels'])} for s in profile['skills']],
           'raw_character_available': original is not None}
    if original:
        assert row['phase_max_levels'] == [x['maxLevel'] for x in original['phases']]
        assert [s['id'] for s in row['skills']] == [s['skillId'] for s in original['skills']]
        assert [s['unlock_elite'] for s in row['skills']] == [int(s['unlockCond']['phase'].split('_')[1]) for s in original['skills']]
    else:
        assert native in ('char_1001_amiya2', 'char_1037_amiya3')
        row['pinned_patch_selector'] = '$.patchChars.' + native + '.skills'
        row['raw_patch_rehashed_in_this_rebuild'] = False
    forms.append(row)
reuse = ROOT / 'research/p2-gnosis-isw-a-reference/source-receipt.json'
receipt = {'raw_current_verification': {'character_table': {'path': str(rawpath), **digest(rawpath)},
                                      'skill_table': {'path': str(skillpath), **digest(skillpath)}},
           'forms_count': len(forms), 'skills_count': sum(len(x['skills']) for x in forms), 'forms': forms,
           'susuro_training_selector': '$.char_298_susuro.allSkillLvlup[0..5].unlockCond',
           'susuro_training_conditions': [x['unlockCond'] for x in source['allSkillLvlup']],
           'training_unlock_is_not_run_skill_use_cap': True, 'e0_skill_use_limit_verified': False,
           'rank_policy_changed': False,
           'reused_committed_gamedata_const_receipt': {'path': str(reuse), **digest(reuse),
                                                      'original_record': json.loads(reuse.read_text())['sources']['gamedata_const'],
                                                      'raw_gamedata_const_rehashed_in_this_rebuild': False},
           'lost_tmp_sources_not_revalidated': ['roguelike_topic_table.json', 'roguelike_table.json',
                                               'char_patch_table.json', 'gamedata_const.json'],
           'mechanism_source_download_needed_for_boolean_type_fix': False,
           'source_reason': 'Current API integer validation and separately typed boolean fields already establish the input-type contract; no native numerical model is changed.'}
assert receipt['raw_current_verification']['character_table']['sha256'] == '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'
assert receipt['raw_current_verification']['skill_table']['sha256'] == '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'
(OUT / 'source-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'forms': len(forms), 'skills': receipt['skills_count'], 'patch_forms_not_rehashed': 2,
                  'e0_use_limit_verified': False, 'raw_character_skill_hashes_verified': True}))
