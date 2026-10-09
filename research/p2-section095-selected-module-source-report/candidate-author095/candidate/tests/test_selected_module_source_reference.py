"""Report-only module originals, qualification, formatting and ownership safety."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.module_source_reference import (
    REFERENCE_KEY, SECTION_ID, TECHNICAL_HEADING, _reference_data,
)
from rouge.reporting import format_report


def selected(operator, module=None, stage=3, **extra):
    profile = catalog()['operators'][operator]
    return {'operator': operator, 'skill': 1,
            'module_id': module or profile['modules'][0]['id'],
            'module_level': stage, **extra}


def without_new_reference(result):
    """Only the additive report object and exactly one notes-only block differ."""
    copy = deepcopy(result)
    report = copy['report']
    report.pop(REFERENCE_KEY, None)
    report['sections'] = [block for block in report['sections'] if block['id'] != SECTION_ID]
    return copy


def mutable_ids(value):
    found = set()
    def walk(item):
        if isinstance(item, (dict, list)):
            if id(item) in found:
                return
            found.add(id(item))
            children = list(item.values()) if isinstance(item, dict) else item
            for child in children:
                walk(child)
    walk(value)
    return found


class SelectedModuleSourceReferenceTests(unittest.TestCase):
    def test_every_module_stage_is_report_only_and_preserves_existing_full_native(self):
        for operator, profile in catalog()['operators'].items():
            for module in profile['modules']:
                for stage in (1, 2, 3):
                    with self.subTest(operator=operator, module=module['id'], stage=stage):
                        args = selected(operator, module['id'], stage)
                        caller = deepcopy(args)
                        result = calculate_damage(args)
                        with patch('rouge.module_source_reference.selected_module_reference', return_value=None):
                            original = calculate_damage(args)
                        self.assertEqual(args, caller)
                        self.assertEqual(without_new_reference(result), original)
                        ref = result['report'][REFERENCE_KEY]
                        self.assertEqual(ref['module_level'], stage)
                        self.assertEqual(ref['raw_phase']['equipLevel'], stage)
                        self.assertEqual(ref['raw_phase']['parts'], module['levels'][stage-1]['parts'])
                        self.assertEqual(list(ref['raw_phase']), [
                            'equipLevel', 'parts', 'attributeBlackboard', 'tokenAttributeBlackboard'])
                        blocks = [b for b in result['report']['sections'] if b['id'] == SECTION_ID]
                        self.assertEqual(len(blocks), 1)
                        self.assertIs(blocks[0], result['report']['sections'][-1])
                        self.assertEqual(blocks[0]['metrics'], [])
                        self.assertEqual(format_report(without_new_reference(result)), format_report(original))
                        self.assertEqual(format_report(without_new_reference(result), technical=True),
                                         format_report(original, technical=True))

    def test_absent_none_and_empty_module_never_load_source_or_add_placeholders(self):
        for operator in catalog()['operators']:
            for extra in ({}, {'module_id': None, 'module_level': 3},
                          {'module_id': '', 'module_level': 4}):
                with self.subTest(operator=operator, extra=extra):
                    args = {'operator': operator, 'skill': 1, **extra}
                    with patch('rouge.module_source_reference._reference_data',
                               side_effect=AssertionError('absent module must not load supplement')):
                        result = calculate_damage(args)
                    self.assertNotIn(REFERENCE_KEY, result['report'])
                    self.assertNotIn(SECTION_ID, [b['id'] for b in result['report']['sections']])
                    self.assertNotIn(TECHNICAL_HEADING, format_report(result, technical=True))

    def test_all_operator_specific_level_gates_and_preview_defaults_remain_separate(self):
        for operator, profile in catalog()['operators'].items():
            for module in profile['modules']:
                for level, meets in ((module['unlock_level']-1, False),
                                     (module['unlock_level'], True), (None, True)):
                    with self.subTest(operator=operator, module=module['id'], level=level):
                        args = selected(operator, module['id'], level=level,
                                        unconfirmed_training=['等级', '潜能'])
                        result = calculate_damage(args)
                        q = result['report'][REFERENCE_KEY]['cultivation_qualification']
                        self.assertEqual(q['module_cultivation_gate_met'], meets)
                        self.assertEqual(q['effective_training']['level'],
                                         level if level is not None else profile['phases'][2]['max_level'])
                        self.assertTrue(q['uses_unconfirmed_preview_conditions'])
                        for key in ('account_mission_unlock', 'actual_equipment',
                                    'mode_or_map_applicability', 'native_attachment'):
                            self.assertIsNone(q[key])
                        self.assertFalse(q['new_reference_adds_arithmetic'])
                        self.assertNotIn('applied_to_numeric_estimate', result['report'][REFERENCE_KEY])
        for elite, level, rank in ((0, 50, 1), (1, 80, 7)):
            result = calculate_damage(selected('mechanist', elite=elite, level=level, skill_rank=rank))
            ref = result['report'][REFERENCE_KEY]
            self.assertFalse(ref['cultivation_qualification']['module_cultivation_gate_met'])
            self.assertTrue(all(not q['eligible_under_supplied_cultivation']
                                for q in ref['candidate_qualifications'].values()))

    def test_potential_annotations_do_not_filter_or_mutate_original_candidates(self):
        for operator, rank, lower, upper in (('char_151_myrtle', 4, 4, 5),
                                             ('char_4228_closur', 2, 2, 3)):
            for stage in (2, 3):
                raw_before = None
                for potential, eligible in ((lower, False), (upper, True)):
                    result = calculate_damage(selected(operator, stage=stage, potential=potential))
                    ref = result['report'][REFERENCE_KEY]
                    if raw_before is None:
                        raw_before = deepcopy(ref['raw_phase'])
                    self.assertEqual(ref['raw_phase'], raw_before)
                    matched = 0
                    selector = ref['source']['selectors']['phase']
                    for i, part in enumerate(ref['raw_phase']['parts']):
                        for bundle in ('addOrOverrideTalentDataBundle', 'overrideTraitDataBundle'):
                            for j, candidate in enumerate((part.get(bundle) or {}).get('candidates') or ()):
                                if candidate['requiredPotentialRank'] != rank:
                                    continue
                                q = ref['candidate_qualifications'][
                                    f'{selector}.parts[{i}].{bundle}.candidates[{j}]']
                                self.assertEqual(q['potential_gate_met'], eligible)
                                self.assertEqual(q['eligible_under_supplied_cultivation'], eligible)
                                self.assertIsNone(q['actual_activation'])
                                matched += 1
                    self.assertGreater(matched, 0)

    def test_amiya_patch_ownership_preserves_shared_raw_char_id(self):
        for operator in ('char_1001_amiya2', 'char_1037_amiya3'):
            ref = calculate_damage(selected(operator))['report'][REFERENCE_KEY]
            self.assertEqual(ref['operator_id'], operator)
            self.assertEqual(ref['raw_metadata']['charId'], 'char_002_amiya')
            self.assertEqual(ref['raw_metadata']['tmplId'], operator)
            self.assertEqual(ref['raw_owner']['charEquip_owner_id'], operator)
            self.assertEqual(ref['raw_owner']['charEquip'][ref['raw_owner']['membership_index']], ref['module_id'])
            self.assertEqual(ref['raw_owner']['membership_index'], 1)

    def test_token_blackboards_and_hidden_null_fields_are_untouched_original_data(self):
        for operator, token, cost, maximum in (
                ('char_110_deepcl', 'token_10001_deepcl_tentac', -2.0, 3.0),
                ('char_2027_wang', 'token_10064_wang_stone1', -1.0, 1.0)):
            for stage in (1, 2, 3):
                ref = calculate_damage(selected(operator, stage=stage))['report'][REFERENCE_KEY]
                self.assertEqual(ref['raw_phase']['tokenAttributeBlackboard'][token], [
                    {'key': 'cost', 'value': cost, 'valueStr': None},
                    {'key': 'max_deploy_count', 'value': maximum, 'valueStr': None}])
        cases = (('char_1046_sbell2', None, 1, -1),
                 ('char_1029_yato2', 'uniequip_003_yato2', 2, -1),
                 ('mechanist', None, 4, -2))
        for operator, module, index, talent_index in cases:
            with self.subTest(operator=operator):
                ref = calculate_damage(selected(operator, module))['report'][REFERENCE_KEY]
                part = ref['raw_phase']['parts'][index]
                candidate = part['addOrOverrideTalentDataBundle']['candidates'][0]
                self.assertEqual(candidate['talentIndex'], talent_index)
                if operator == 'char_1029_yato2':
                    self.assertEqual(candidate['name'], '双雷剑麒麟')
                else:
                    self.assertIsNone(candidate['name'])
                self.assertTrue(candidate['isHideTalent'])
                self.assertIn('valueStr', candidate['blackboard'][0])
                if operator == 'mechanist':
                    self.assertTrue(part['isToken'])
                    self.assertEqual(part['validInMapTag'], 'rogue_6')
                    self.assertIsNone(candidate['description'])
        gnosis = calculate_damage(selected('char_206_gnosis', 'uniequip_004_gnosis'))['report'][REFERENCE_KEY]
        self.assertEqual(gnosis['raw_phase']['parts'][1]['validInGameTag'], 'roguelike')

    def test_readable_conditions_preserve_override_spelling_and_no_duplicate_metrics(self):
        for operator, expected in (
                ('char_1041_angel2', '生命值高于80%'),
                ('char_4204_mantra', '元素爆发'),
                ('mechanist', '攻击被自身或召唤物阻挡的敌人'),
                ('char_151_myrtle', '身前一名干员阻挡数')):
            result = calculate_damage(selected(operator))
            block = result['report']['sections'][-1]
            self.assertEqual(block['id'], SECTION_ID)
            self.assertEqual(block['metrics'], [])
            self.assertIn(expected, '\n'.join(block['notes']))
            self.assertTrue(any('原件条件资料' in note for note in block['notes']))
            self.assertFalse(any('https://' in note for note in block['notes']))
        raw = calculate_damage(selected('char_151_myrtle'))['report'][REFERENCE_KEY]['raw_phase']
        trait = raw['parts'][0]['overrideTraitDataBundle']['candidates'][0]
        self.assertIn('overrideDescripton', trait)
        self.assertNotIn('overrideDescription', trait)

    def test_existing_dedicated_coverage_is_exact_and_linked_by_strings(self):
        cases = (('char_133_mm', None, 'mei_airborne_module'),
                 ('char_328_cammou', None, 'drone_trait'),
                 ('char_1038_whitw2', None, 'drone_trait'),
                 ('char_206_gnosis', 'uniequip_004_gnosis', 'gnosis_isw_a'),
                 ('char_437_mizuki', 'uniequip_003_mizuki', 'mizuki_amb_y'),
                 ('char_4202_haruka', None, 'talents'),
                 ('char_110_deepcl', None, 'relic_token_token_10001_deepcl_tentac'),
                 ('char_2027_wang', None, 'relic_token_token_10064_wang_stone1'),
                 ('mechanist', None, 'token_duration_token_10069_mcnist_mcgraf'))
        for operator, module, expected in cases:
            with self.subTest(operator=operator):
                result = calculate_damage(selected(operator, module))
                ref = result['report'][REFERENCE_KEY]
                links = ref['existing_coverage']['report_sections']
                self.assertIn(expected, [link['section_id'] for link in links])
                for link in links:
                    self.assertIsInstance(link['path'], str)
                    index = int(link['path'].split('/')[-1])
                    self.assertEqual(result['report']['sections'][index]['id'], link['section_id'])
                self.assertTrue(all(isinstance(path, str) for path in ref['existing_coverage']['native_paths']))
                with patch('rouge.module_source_reference.selected_module_reference', return_value=None):
                    old = calculate_damage(selected(operator, module))
                self.assertEqual(without_new_reference(result), old)

    def test_nested_mutations_cannot_reach_catalog_cache_caller_native_or_fresh_report(self):
        for operator in ('char_151_myrtle', 'char_110_deepcl', 'char_2027_wang', 'char_206_gnosis'):
            with self.subTest(operator=operator):
                args = selected(operator)
                caller = deepcopy(args)
                before_catalog = deepcopy(catalog())
                before_cache = deepcopy(_reference_data())
                first = calculate_damage(args)
                untouched = deepcopy(first)
                ref = first['report'][REFERENCE_KEY]
                other = without_new_reference(first)
                self.assertFalse(mutable_ids(ref) & mutable_ids(catalog()))
                self.assertFalse(mutable_ids(ref) & mutable_ids(_reference_data()))
                self.assertFalse(mutable_ids(ref) & mutable_ids(other))
                ref['raw_metadata']['uniEquipName'] = 'mutated'
                ref['source']['files']['battle_equip_table']['sha256'] = 'mutated'
                ref['raw_owner']['charEquip'].append('foreign-module')
                ref['raw_phase']['attributeBlackboard'][0]['valueStr'] = 'mutated'
                ref['raw_phase']['parts'][0]['resKey'] = 'mutated'
                for part in ref['raw_phase']['parts']:
                    for bundle in ('addOrOverrideTalentDataBundle', 'overrideTraitDataBundle'):
                        for candidate in (part.get(bundle) or {}).get('candidates') or ():
                            candidate['blackboard'].append({'key': 'mutated', 'value': 9.0, 'valueStr': 'mutated'})
                for blackboard in ref['raw_phase']['tokenAttributeBlackboard'].values():
                    blackboard[0]['value'] = 99.0
                ref['cultivation_qualification']['effective_training']['elite'] = -9
                ref['candidate_qualifications'].clear()
                ref['existing_coverage']['report_sections'].clear()
                self.assertEqual(args, caller)
                self.assertEqual(catalog(), before_catalog)
                self.assertEqual(_reference_data(), before_cache)
                self.assertEqual(without_new_reference(first), without_new_reference(untouched))
                self.assertEqual(calculate_damage(args), untouched)
                second = calculate_damage(selected(operator, stage=1))
                self.assertEqual(second['report'][REFERENCE_KEY]['module_level'], 1)

    def test_technical_trace_is_exact_json_and_bypasses_phrase_replacements(self):
        result = calculate_damage(selected('char_151_myrtle'))
        ref = result['report'][REFERENCE_KEY]
        raw = 'DPS HPS NORMAL ELITE BOSS FOUR_STAR timing.sp_events.initial opaque_script_key'
        ref['raw_metadata']['uniEquipName'] = raw
        ref['raw_phase']['parts'][0]['overrideTraitDataBundle']['candidates'][0]['overrideDescripton'] = raw
        text = format_report(result, technical=True)
        tail = text.split('\n' + TECHNICAL_HEADING + '\n', 1)[1]
        self.assertEqual(tail, json.dumps(ref, ensure_ascii=False, indent=2))
        self.assertEqual(json.loads(tail), ref)
        self.assertIn(raw, tail)
        self.assertNotIn(TECHNICAL_HEADING, format_report(result))
        self.assertEqual(json.loads(json.dumps(result, ensure_ascii=False))['report'][REFERENCE_KEY], ref)

    def test_invalid_requests_preserve_original_error_class_args_and_order(self):
        inputs = [selected('mechanist', stage=stage) for stage in (0, 4, '2', 2.0, True)]
        inputs.extend((selected('mechanist', module='uniequip_002_susuro'),
                       selected('mechanist', module='not-a-module'),
                       selected('mechanist', elite=True, module_level=4),
                       selected('mechanist', skill=0, module_level=4),
                       selected('mechanist', potential=0, module_level=4)))
        for args in inputs:
            with self.subTest(args=args):
                caller = deepcopy(args)
                with self.assertRaises(Exception) as current:
                    calculate_damage(args)
                with patch('rouge.module_source_reference.selected_module_reference', return_value=None):
                    with self.assertRaises(Exception) as old:
                        calculate_damage(args)
                self.assertIs(type(current.exception), type(old.exception))
                self.assertEqual(current.exception.args, old.exception.args)
                self.assertEqual(args, caller)

    def test_shared_report_rebuilds_keep_deployment_and_window_numeric_results(self):
        scenarios = [
            selected('mechanist', skill=1, timing_mode='continuous', deployment_elapsed_seconds=8),
            selected('char_1029_yato2', 'uniequip_003_yato2', skill=2, timing={'target_disappears_seconds': 0}),
            selected('char_151_myrtle', skill=1, timing_mode='continuous', window_seconds=0),
            selected('mechanist', skill=1, relic_ids=['rogue_6_relic_legacy_97']),
        ]
        for args in scenarios:
            with self.subTest(args=args):
                current = calculate_damage(args)
                with patch('rouge.module_source_reference.selected_module_reference', return_value=None):
                    old = calculate_damage(args)
                self.assertEqual(without_new_reference(current), old)
                self.assertEqual(len([s for s in current['report']['sections'] if s['id'] == SECTION_ID]), 1)

    def test_existing_unverified_clock_test_fixture_keeps_phase_rebuild_reports_isolated(self):
        # The current three pinned wines have verified deployment clocks.
        # This explicit test-only fixture exercises the retained unknown-clock
        # envelope branch; it asserts no new game clock or live mechanism.
        from rouge.relics import mechanics
        from rouge.module_source_reference import selected_module_reference
        data = deepcopy(mechanics())
        wine = data['relics']['rogue_6_relic_legacy_97']
        effect = next(e for e in wine['effects'] if e['kind'] == 'periodic_sp')
        self.assertEqual(effect['clock'], 'deployment')
        effect['clock'] = 'unverified_test_fixture'
        refs = []
        def observe(*args):
            ref = selected_module_reference(*args)
            refs.append(ref)
            return ref
        args = selected('mechanist', relic_ids=['rogue_6_relic_legacy_97'])
        with patch('rouge.relics.mechanics', return_value=data):
            with patch('rouge.module_source_reference.selected_module_reference', side_effect=observe):
                current = calculate_damage(args)
            with patch('rouge.module_source_reference.selected_module_reference', return_value=None):
                old = calculate_damage(args)
        self.assertEqual(without_new_reference(current), old)
        self.assertEqual(current['relic_resolution']['phase_estimate']['mode'], 'frame_envelope')
        self.assertGreater(len(refs), 1)
        for left, right in zip(refs, refs[1:]):
            self.assertEqual(left, right)
            self.assertFalse(mutable_ids(left) & mutable_ids(right))


if __name__ == '__main__':
    unittest.main()
