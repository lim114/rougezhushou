"""Pinned owner and cultivation gates; no bubble clocks or module composition."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
BASELINE = ROOT / 'baseline153'
sys.path.insert(0, str(BASELINE))
from rouge.catalog import catalog
from rouge.operator_options import OPTIONS
from rouge.operator_engine import selected_talents

sources = {
    'character_table': (Path('/workspace/rougezhushou/.cache/p2-s1-binding/character_table.json'),
                        '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
    'skill_table': (Path('/workspace/rougezhushou/.cache/p2-s1-binding/skill_table.json'),
                    '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'),
    'battle_equip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json'),
                          '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
    'uniequip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json'),
                      'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9')}
tables, receipts = {}, {}
for name, (path, expected) in sources.items():
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected
    tables[name] = json.loads(raw)
    receipts[name] = {'path': str(path), 'bytes': len(raw), 'sha256': expected,
                      'commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
                      'url': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/'
                             'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/' + name + '.json',
                      'reused_original_bytes_rehashed': True}
character = tables['character_table']['char_4202_haruka']
profile = catalog()['operators']['char_4202_haruka']
assert len(character['talents']) == 2
first = character['talents'][0]['candidates']
second = character['talents'][1]['candidates']
assert [c['unlockCondition'] for c in first] == [
    {'phase': 'PHASE_0', 'level': 1}, {'phase': 'PHASE_1', 'level': 1}, {'phase': 'PHASE_2', 'level': 1}]
assert all(c['name'] == '浮光泡影' for c in first)
assert all(c['name'] == '扶摇花火' for c in second)
assert all(c['unlockCondition'] == {'phase': 'PHASE_2', 'level': 1} for c in second)
assert [c['requiredPotentialRank'] for c in second] == [0, 4]
assert [{b['key']: b['value'] for b in c['blackboard']} for c in second] == [{'heal_scale': .25}, {'heal_scale': .28}]
for index, candidates in enumerate((first, second)):
    expected = [{'phase': int(c['unlockCondition']['phase'][-1]), 'level': c['unlockCondition']['level'],
                 'potential_rank': c['requiredPotentialRank'], 'name': c['name'], 'description': c['description'],
                 'values': {b['key']: b['value'] for b in c['blackboard']}} for c in candidates]
    assert profile['talents'][index] == expected
skills = []
for index, binding in enumerate(character['skills']):
    selected = profile['skills'][index]
    assert selected['id'] == binding['skillId']
    assert selected['unlock_elite'] == int(binding['unlockCond']['phase'][-1])
    original = tables['skill_table'][binding['skillId']]['levels']
    assert len(original) == len(selected['levels']) == 10
    for native, normalized in zip(original, selected['levels']):
        assert native['description'] == normalized['description']
        assert {b['key']: b['value'] for b in native['blackboard']} == normalized['values']
    skills.append({'binding_selector': 'character_table.char_4202_haruka.skills[' + str(index) + ']',
                   'binding': binding, 'skill_selector': 'skill_table.' + binding['skillId'],
                   'all_ten_levels': original})
for level in tables['skill_table']['skchr_haruka_2']['levels']:
    assert '受到遥的治疗效果时' in level['description']
module = next(m for m in profile['modules'] if m['id'] == 'uniequip_002_haruka')
metadata = tables['uniequip_table']['equipDict']['uniequip_002_haruka']
assert metadata['charId'] == 'char_4202_haruka'
assert (metadata['unlockEvolvePhase'], metadata['unlockLevel']) == ('PHASE_2', 60)
module_raw = tables['battle_equip_table']['uniequip_002_haruka']
for index, native in enumerate(module_raw['phases']):
    assert module['levels'][index]['parts'] == native['parts']
    assert module['levels'][index]['attributes'] == {b['key']: b['value'] for b in native['attributeBlackboard']}
controls = [entry for entry in OPTIONS['char_4202_haruka'] if entry[0] == 'bubble_bursts']
assert controls == [('bubble_bursts', '窗口内浮泡破碎次数', 0, 10000, (1, 2, 3))]
selectors = []
for elite in (0, 1, 2):
    for level in (1, profile['phases'][elite]['max_level']):
        for potential in range(1, 7):
            args = {'operator': 'char_4202_haruka', 'elite': elite, 'level': level, 'potential': potential}
            picked, _ = selected_talents(profile, args)
            flower = next((t for t in picked if t['name'] == '扶摇花火'), None)
            assert bool(flower) == (elite == 2)
            if flower:
                assert flower['values']['heal_scale'] == (.28 if potential >= 5 else .25)
            selectors.append({'scenario': args, 'selected_talents': picked})
prior = [Path('/workspace/rougezhushou/research/p2-independent-events/source-receipt.json'),
         Path('/workspace/rougezhushou/research/p2-independent-events/NOTE.md'),
         Path('/workspace/rougezhushou/research/p2-haruka-healing-targets/source-receipt.json'),
         Path('/workspace/rougezhushou/research/p2-haruka-healing-targets/NOTE.md')]
receipt = {'baseline_commit': '153b5dbf15d6567746047cbdea7f8d00a6879f3a', 'raw_original_files': receipts,
           'exact_character_talent_records': character['talents'], 'exact_skill_records': skills,
           'module_metadata': metadata, 'module_all_three_complete_records': module_raw,
           'catalog_original_full_talents_skills_modules_match': True,
           'public_control_owner_and_scope': {'owner': 'char_4202_haruka', 'controls': controls,
                'meaning': 'Declared Haruka bubble break count. First talent exists at E0; the declaration is not a declaration that second-talent healing is unlocked.'},
           'actual_existing_talent_selection_controls': selectors,
           'prior_research_rehashed': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                                        'bytes': p.stat().st_size} for p in prior],
           'conclusion': {'first_talent_bubbles_eligible_at_e0': True,
                          'second_talent_flower_healing_eligible_only_at_e2_level1': True,
                          's2_damage_dependency': 'Raw S2 requires treatment by Haruka; bubble-derived damage depends on the eligible flower healing, not a raw bubble break alone.',
                          'module_unlock_does_not_grant_flower_to_e0_or_e1': True,
                          'preserve_original_declared_break_count_parser_and_errors': True,
                          'native_attachment_coexistence_composition_and_event_clock_verified': False,
                          'scope': 'Only exclude modeled flower healing and its S2 dependent damage when the actual existing selected_talents gate has no flower. Qualified E2 old outcomes remain exact.'}}
(ROOT / 'source-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'raw_files_verified': len(receipts), 'talent_selection_controls': len(selectors),
                  'all_skill_levels_verified': sum(len(s['all_ten_levels']) for s in skills), 'module_levels_verified': len(module_raw['phases'])}))
