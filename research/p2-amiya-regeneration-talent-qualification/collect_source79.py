"""Exact medical-form source binding and existing talent selection, not a clock."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'baseline4dd'
sys.path.insert(0, str(BASE))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents

sources = {
    'char_patch_table': (ROOT / 'char_patch_table.json', 'd1850d5aeec1a9246a0531e88c167e66745644957662c8272fc764f54904c57e'),
    'character_table': (Path('/workspace/rougezhushou/.cache/p2-s1-binding/character_table.json'), '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
    'skill_table': (Path('/workspace/rougezhushou/.cache/p2-s1-binding/skill_table.json'), '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'),
    'battle_equip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json'), '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
    'uniequip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json'), 'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9'),
}
tables, hashes = {}, {}
for name, (path, expected) in sources.items():
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected
    tables[name] = json.loads(raw)
    hashes[name] = {'source_path': str(path), 'sha256': expected, 'bytes': len(raw),
                    'fixed_game_data_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
                    'rehashed_actual_complete_original_bytes': True}

OP = 'char_1037_amiya3'
patch = tables['char_patch_table']
assert patch['infos']['char_002_amiya']['tmplIds'] == ['char_002_amiya', 'char_1001_amiya2', OP]
assert patch['patchDetailInfoList'][OP]['patchId'] == OP
assert patch['patchDetailInfoList'][OP]['infoParam'] == '医疗'
original = patch['patchChars'][OP]
profile = catalog()['operators'][OP]
assert original['profession'] == 'MEDIC' and profile['profession'] == original['profession'].lower()
assert original['subProfessionId'] == profile['subprofession_id'] == 'incantationmedic'
assert profile['talents'] == [[{'phase': int(c['unlockCondition']['phase'][-1]),
    'level': c['unlockCondition']['level'], 'potential_rank': c['requiredPotentialRank'],
    'name': c['name'], 'description': c['description'],
    'values': {b['key']: b['value'] for b in c['blackboard']}}
    for c in g['candidates']] for g in original['talents']]
assert len(original['talents']) == 1
candidates = original['talents'][0]['candidates']
assert [c['unlockCondition'] for c in candidates] == [
    {'phase': 'PHASE_1', 'level': 1}, {'phase': 'PHASE_2', 'level': 1}]
assert all(c['name'] == '诚挚期许' for c in candidates)
skills = []
for native, parsed in zip(original['skills'], profile['skills'], strict=True):
    assert parsed['id'] == native['skillId']
    assert parsed['unlock_elite'] == int(native['unlockCond']['phase'][-1])
    ranks = tables['skill_table'][native['skillId']]['levels']
    for raw, current in zip(ranks, parsed['levels'], strict=True):
        assert raw['description'] == current['description']
        assert {b['key']: b['value'] for b in raw['blackboard']} == current['values']
    skills.append({'actual_form_binding': native, 'all_ten_original_levels': ranks})
module = profile['modules'][0]
assert module['id'] == 'uniequip_002_amiya3'
metadata = tables['uniequip_table']['equipDict'][module['id']]
assert metadata['charId'] == 'char_002_amiya' and metadata['tmplId'] == OP
assert module['id'] in tables['uniequip_table']['charEquip'][OP]
assert (metadata['unlockEvolvePhase'], metadata['unlockLevel']) == ('PHASE_2', 50)
module_raw = tables['battle_equip_table'][module['id']]
for native, parsed in zip(module_raw['phases'], module['levels'], strict=True):
    assert parsed['parts'] == native['parts']
    assert parsed['attributes'] == {b['key']: b['value'] for b in native['attributeBlackboard']}

selection = []
for elite in (0, 1, 2):
    for level in (1, profile['phases'][elite]['max_level']):
        for potential in range(1, 7):
            args = {'operator': OP, 'elite': elite, 'level': level, 'potential': potential}
            selected, _ = selected_talents(profile, args)
            assert any(t['name'] == '诚挚期许' for t in selected) == (elite >= 1)
            selection.append({'scenario': args, 'actual_selected_talents': selected})
for elite, level in ((0, 50), (1, 70), (2, 49), (2, 50)):
    for stage in (1, 2, 3):
        args = {'operator': OP, 'elite': elite, 'level': level, 'module_id': module['id'], 'module_level': stage}
        selected, _ = selected_talents(profile, args)
        assert any(t['name'] == '诚挚期许' for t in selected) == (elite >= 1)
        selection.append({'scenario': args, 'actual_selected_talents': selected})

negatives = []
for op, talent in (('char_1046_sbell2', '无垠的雪景'), ('char_1041_angel2', '火力电台')):
    raw = tables['character_table'][op]
    matching = [c for g in raw['talents'] for c in (g['candidates'] or []) if c['name'] == talent]
    assert matching[0]['unlockCondition'] == {'phase': 'PHASE_0', 'level': 1}
    negatives.append({'operator': op, 'talent': talent, 'original_candidates': matching,
                      'conclusion': 'Already available at E0 level1; do not suppress this source merely for low cultivation.'})
(ROOT / 'excluded-neighbor-leads.json').write_text(json.dumps(negatives, ensure_ascii=False, indent=2) + '\n')
prior = [Path('/workspace/rougezhushou/research/p2-amiya-phase-reference') / name
         for name in ('NOTE.md', 'source-receipt.json')]
receipt = {'baseline_commit': '4dd778488c96864a778ccbc25c0cf11cddfa5d86',
    'actual_original_sources': hashes,
    'form_identity': {'infos_selector': 'char_patch_table.infos.char_002_amiya',
        'infos_record': patch['infos']['char_002_amiya'],
        'form_selector': 'char_patch_table.patchChars.char_1037_amiya3',
        'complete_original_medical_form': original,
        'patch_detail_selector': 'char_patch_table.patchDetailInfoList.char_1037_amiya3',
        'patch_detail': patch['patchDetailInfoList'][OP],
        'account_unlock_condition_source_only': patch['unlockConds'][OP],
        'source_does_not_confirm_actual_user_account_form_or_run_training': True},
    'exact_medical_talent_candidates': candidates, 'exact_medical_skills': skills,
    'exact_module_metadata': metadata, 'all_three_module_complete_records': module_raw,
    'actual_selected_talents_controls': selection,
    'prior_research_rehashed': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in prior],
    'public_input_contract': 'No new regeneration event input. Use existing selected_talents gate; preserve window_seconds, original skill duration, existing skill/mastery qualification and all option parsers/errors.',
    'confirmed_scope': 'When medical Amiya has no selected 诚挚期许, effective own-regeneration duration is zero. No generic per-hit or zero-HP suppression; E1/E2 native clock and S2 unknown remain unchanged.',
    'source_reader_shape_corrections': [
        'catalog profession deliberately lowercases original MEDIC to medic; verified build_catalog.py mapping.',
        'Medical Amiya module original metadata belongs to base char_002_amiya and specifically tmplId char_1037_amiya3; both exact fields plus charEquip medical-form binding verified, no same-name fallback.'],
    'native_end_clock_attachment_healing_order_or_form_ownership_verified': False}
(ROOT / 'source-receipt79.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'raw_original_files': len(hashes), 'actual_selection_controls': len(selection),
                  'original_medical_skill_levels': sum(len(s['all_ten_original_levels']) for s in skills),
                  'original_module_levels': len(module_raw['phases']), 'negative_neighbors': len(negatives)}))
