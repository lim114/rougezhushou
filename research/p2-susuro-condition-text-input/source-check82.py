import hashlib
import json
import sys
from pathlib import Path

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT / 'frozen'))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents

GAME = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
original_paths = {
    'character_table': (Path('/workspace/rougezhushou/.cache/p2-s1-binding/character_table.json'), '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
    'skill_table': (Path('/workspace/rougezhushou/.cache/p2-s1-binding/skill_table.json'), '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'),
    'battle_equip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json'), '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
    'uniequip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json'), 'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9'),
}
tables, proofs = {}, {}
for name, (path, expected) in original_paths.items():
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected
    tables[name] = json.loads(data)
    proofs[name] = {'path': str(path), 'sha256': expected, 'bytes': len(data)}
owner = tables['character_table']['char_298_susuro']
current = catalog()['operators']['char_298_susuro']
assert owner['name'] == current['name'] == '苏苏洛'
for raw, projected in zip(owner['talents'][0]['candidates'], current['talents'][0], strict=True):
    assert raw['name'] == projected['name'] == '微创治疗'
    assert raw['description'] == projected['description']
    assert int(raw['unlockCondition']['phase'][-1]) == projected['phase']
    assert raw['unlockCondition']['level'] == projected['level']
    assert raw['requiredPotentialRank'] == projected['potential_rank']
    assert {b['key']: b['value'] for b in raw['blackboard']} == projected['values']
skills = {}
for entry, projected in zip(owner['skills'], current['skills'], strict=True):
    raw = tables['skill_table'][entry['skillId']]
    assert len(raw['levels']) == len(projected['levels']) == 10
    for level, part in zip(raw['levels'], projected['levels'], strict=True):
        assert {b['key']: b['value'] for b in level['blackboard']} == part['values']
        assert level['description'] == part['description']
    skills[entry['skillId']] = raw
selections = []
for elite in (0, 1, 2):
    for potential in (1, 4, 5, 6):
        scenario = {'elite': elite, 'level': 1, 'potential': potential}
        chosen, parts = selected_talents(current, scenario)
        assert not parts
        assert bool(chosen) == (elite >= 1)
        selections.append({'scenario': scenario, 'selected_talents': chosen, 'module_parts': parts})
module = current['modules'][0]
assert module['id'] == 'uniequip_002_susuro'
raw_module = tables['battle_equip_table'][module['id']]
raw_meta = tables['uniequip_table']['equipDict'][module['id']]
assert raw_meta['charId'] == current['id']
assert raw_meta['unlockEvolvePhase'] == 'PHASE_2' and raw_meta['unlockLevel'] == 40
assert module['unlock_elite'] == 2 and module['unlock_level'] == 40
for raw, projected in zip(raw_module['phases'], module['levels'], strict=True):
    assert raw['equipLevel'] == projected['level']
    assert raw['parts'] == projected['parts']
    assert {b['key']: b['value'] for b in raw['attributeBlackboard']} == projected['attributes']
    for part in raw['parts']:
        candidates = (part.get('addOrOverrideTalentDataBundle') or {}).get('candidates') or []
        for candidate in candidates:
            assert part['target'] == 'TALENT_DATA_ONLY' and part['isToken'] is False
            assert part['validInGameTag'] is None and part['validInMapTag'] is None
            assert candidate['talentIndex'] == 0 and candidate['prefabKey'] == '1'
            assert candidate['name'] == '微创治疗' and candidate['tokenKey'] is None
            assert candidate['isHideTalent'] is False and candidate['validModeIndices'] is None
module_selections = []
for level in (39, 40):
    for stage in (1, 2, 3):
        for potential in (1, 4, 5):
            scenario = {'elite': 2, 'level': level, 'potential': potential,
                        'module_id': module['id'], 'module_level': stage}
            chosen, parts = selected_talents(current, scenario)
            assert bool(parts) == (level >= 40)
            assert chosen[0]['name'] == '微创治疗'
            expected = (1.2 if potential < 5 else 1.23) if level < 40 or stage == 1 else (
                (1.23 if potential < 5 else 1.26) if stage == 2 else (1.25 if potential < 5 else 1.28))
            assert chosen[0]['values']['heal_scale'] == expected
            module_selections.append({'scenario': scenario, 'selected_talents': chosen,
                                      'module_parts': parts})
options = (OUT / 'frozen/rouge/operator_options.py').read_text()
app = (OUT / 'frozen/rouge/app.py').read_text()
engine = (OUT / 'frozen/rouge/operator_engine.py').read_text()
option = "('low_cost_healing_target','受疗干员初始费用不超过10',False,1,(1,2))"
assert option in options
assert 'widget=QCheckBox(label);widget.setChecked(default)' in app
assert 'scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()' in app
assert "recipient_factor=self.talent('微创治疗','heal_scale',1) if (" in engine
assert "op=='char_298_susuro' and self.s.get('low_cost_healing_target')) else 1" in engine
receipt = {'passed': True, 'kind': 'software condition binding; no new mechanism', 'section_candidate': 82,
           'baseline_commit': 'c950fbc800245f7f784d6070f7126890352ffcc9', 'source_commit': GAME,
           'source_files': proofs, 'complete_selected_character': owner,
           'complete_selected_skill_objects': skills, 'skill_levels_checked': 20,
           'actual_frozen_selected_talent_results': selections,
           'complete_selected_module_battle_object': raw_module,
           'complete_selected_module_metadata': raw_meta,
           'actual_frozen_module_boundary_results': module_selections,
           'actual_ui_control': {'option_tuple': option, 'control': 'QCheckBox',
                                 'scenario_value': 'widget.isChecked()', 'ui_executed': False},
           'current_consumer': {'function': 'Combat.plan', 'parameter': 'low_cost_healing_target',
                                'truthiness_selects_existing_factor': True,
                                'recipient_scope': 'existing skill and recharge treatment branch only',
                                'healing_target_validation_precedes_consumer': True},
           'existing_contracts_consulted': ['research/p2-susuro-recipient-factor/NOTE.md',
                                            'research/p2-shu-profession-text-input/NOTE068.md',
                                            'research/p2-cooperative-text-input/NOTE.md',
                                            'research/p2-enemy-sown-tile-input/author/HANDOFF.md',
                                            'tests/test_target_count_input_types.py',
                                            'tests/test_declared_count_input_types.py'],
           'proposed_scope': 'Reject strings only when the current actual selected talent 微创治疗 exists and the existing recipient consumer is reached; retain every non-string existing declaration and all absent-talent/other-owner inactive behavior.',
           'guard_message': 'low_cost_healing_target 不接受文本条件；请使用布尔值。',
           'mechanism_changes': False, 'new_calculate_damage_calls': 0,
           'native_attachment_or_recipient_acquisition_newly_verified': False,
           'unknowns_retained': ['actual friendly acquisition', 'overhealing', 'external teams and recipient cultivation',
                                 'new stacking and native attachment not inferred'],
           'gui_executed': False, 'wine_executed': False, 'tracked_edits': False}
with (OUT / 'source-receipt82.json').open('x', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'passed': True, 'source_sha256': hashlib.sha256((OUT / 'source-receipt82.json').read_bytes()).hexdigest(),
                  'actual_source_selections': len(selections), 'skill_levels': 20}))
