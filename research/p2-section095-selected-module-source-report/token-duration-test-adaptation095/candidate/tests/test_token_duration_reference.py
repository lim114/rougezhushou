import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.summons import duration_reference, token_attributes

TOKEN = 'token_10069_mcnist_mcgraf'
MODULE = 'uniequip_002_mcnist'


def scenario(**extra):
    return {'operator': 'mechanist', 'skill': 1, 'elite': 2, 'level': 60,
            'module_id': MODULE, 'module_level': 2, **extra}


class TokenDurationReferenceTests(unittest.TestCase):
    def reference(self, **extra):
        return duration_reference(catalog()['operators']['mechanist'], scenario(**extra), TOKEN)

    def test_base_duration_follows_unlocked_token_talent(self):
        for elite, level, seconds in ((1, 1, 20), (1, 80, 20), (2, 1, 30), (2, 90, 30)):
            with self.subTest(elite=elite, level=level):
                r = self.reference(elite=elite, level=level, module_id=None, module_level=0)
                self.assertEqual((r['state'], r['duration_seconds']), ('finite', seconds))
                self.assertTrue(r['unlocked'])

    def test_elite_zero_does_not_infer_lifetime_from_token_attribute_frames(self):
        r = self.reference(elite=0, level=50)
        self.assertEqual(r['state'], 'locked')
        self.assertFalse(r['unlocked'])
        self.assertIsNone(r['duration_seconds'])
        self.assertIsNone(r['base_duration_seconds'])
        result = calculate_damage(scenario(elite=0, level=50, skill_rank=7))
        self.assertEqual(result['token_duration_references'][0], r)

    def test_exact_module_stages_and_level_boundary(self):
        for stage, level, state in ((1, 60, 'finite'), (2, 59, 'finite'),
                                    (2, 60, 'unlimited'), (3, 59, 'finite'), (3, 60, 'unlimited')):
            with self.subTest(stage=stage, level=level):
                r = self.reference(module_level=stage, level=level)
                self.assertEqual(r['state'], state)
                self.assertEqual(r['module_override']['applied'], state == 'unlimited')
                self.assertEqual(r['duration_seconds'], None if state == 'unlimited' else 30)
        self.assertEqual(self.reference(elite=1, level=80)['duration_seconds'], 20)
        self.assertEqual(self.reference(module_id='uniequip_001_mcnist')['duration_seconds'], 30)
        self.assertEqual(self.reference(module_id=None)['duration_seconds'], 30)
        self.assertEqual(self.reference(module_id='uniequip_002_deepcl')['duration_seconds'], 30)

    def test_infinite_parameter_is_confined_to_its_map(self):
        for tag in ('rogue_5', 'main', None, ''):
            with self.subTest(tag=tag):
                r = self.reference(map_tag=tag)
                self.assertEqual((r['state'], r['duration_seconds']), ('finite', 30))
                result = calculate_damage(scenario(map_tag=tag))
                self.assertEqual(result['token_duration_references'][0], r)
        explicit = self.reference(map_tag='rogue_6')
        self.assertEqual((explicit['state'], explicit['map_context']), ('unlimited', 'explicit'))
        self.assertEqual(self.reference()['map_context'], 'current_product_theme')

    def test_other_token_and_owner_pairs_do_not_inherit_mechanist_duration(self):
        mech = catalog()['operators']['mechanist']
        deep = catalog()['operators']['char_110_deepcl']
        tentacle = 'token_10001_deepcl_tentac'
        self.assertIsNone(duration_reference(mech, scenario(), tentacle))
        self.assertIsNone(duration_reference(deep, scenario(), TOKEN))
        self.assertNotIn('duration_reference', token_attributes(deep, {
            'operator': 'char_110_deepcl', 'elite': 2, 'level': 70}, tentacle))
        self.assertNotIn('token_duration_references', calculate_damage({
            'operator': 'char_110_deepcl', 'skill': 1}))

    def test_shared_token_attributes_and_public_calculation_expose_same_reference(self):
        for stage in (1, 2, 3):
            args = scenario(module_level=stage)
            attrs = token_attributes(catalog()['operators']['mechanist'], args, TOKEN)
            result = calculate_damage(args)
            self.assertEqual(attrs['duration_reference'], result['token_duration_references'][0])
            self.assertEqual((attrs['hp'], attrs['attack'], attrs['defense'], attrs['deployment_cost']),
                             (3264, 564, 517, 10))

    def test_token_relic_stats_keep_duration_metadata_separate_from_runes(self):
        args = scenario(relic_ids=['rogue_6_relic_legacy_134'])
        result = calculate_damage(args)
        token = next(t for t in result['relic_token_stats'] if t['id'] == TOKEN)
        self.assertEqual(token['duration_reference'], result['token_duration_references'][0])
        self.assertEqual(token['duration_reference']['duration_seconds'], None)
        self.assertGreater(token['hp'], 3264)

    def test_unlimited_does_not_claim_actual_survival_or_apply_a_clock(self):
        r = self.reference()
        self.assertEqual(r['parameter_value'], -1)
        self.assertIsNone(r['duration_seconds'])
        for key in ('deployment_completed_seconds', 'actual_exit_seconds', 'actual_alive_seconds'):
            self.assertIsNone(r[key])
        self.assertFalse(r['live_state_verified'])
        self.assertFalse(r['damage_timing_applied'])
        self.assertEqual({o['module_level'] for o in r['module_override']['conditions']}, {2, 3})
        self.assertTrue(all(o['map_tag'] == 'rogue_6' and o['unlock_level'] == 60
                            for o in r['module_override']['conditions']))

    def test_input_and_cached_reference_are_isolated(self):
        args = scenario()
        before = copy.deepcopy(args)
        r = duration_reference(catalog()['operators']['mechanist'], args, TOKEN)
        r['module_override']['conditions'][0]['unlock_level'] = 1
        r['sources']['character_table']['sha256'] = 'changed'
        self.assertEqual(args, before)
        fresh = self.reference()
        self.assertEqual(fresh['module_override']['conditions'][0]['unlock_level'], 60)
        self.assertEqual(len(fresh['sources']['character_table']['sha256']), 64)
        public = calculate_damage(args)
        public['token_duration_references'][0]['state'] = 'changed'
        self.assertEqual(calculate_damage(args)['token_duration_references'][0]['state'], 'unlimited')

    def test_report_adds_concise_reference_and_retains_existing_talent_text(self):
        result = calculate_damage(scenario(module_level=3))
        block = next(s for s in result['report']['sections'] if s['id'] == 'token_duration_' + TOKEN)
        self.assertIsNone(block['metrics'][0]['value'])
        self.assertIn('无限', str(block))
        self.assertIn('死亡', str(block))
        talents = next(s for s in result['report']['sections'] if s['id'] == 'talents')
        self.assertIn('持续30秒', str(talents))
        self.assertIn('5秒内未受到伤害', str(talents))
        finite = calculate_damage(scenario(module_level=1))
        finite_block = next(s for s in finite['report']['sections'] if s['id'] == block['id'])
        self.assertEqual(finite_block['metrics'][0]['value'], 30)

    def test_all_public_numeric_stats_damage_and_clocks_are_unchanged(self):
        cases = []
        for elite, skills, ranks in ((1, (1, 2), (1, 7)), (2, (1, 2, 3), (1, 7, 10))):
            for skill in skills:
                for rank in ranks:
                    for mode in ('frames', 'continuous'):
                        for tag in ('rogue_6', 'main'):
                            cases.append(scenario(elite=elite, level=60, skill=skill, skill_rank=rank,
                                timing_mode=mode, map_tag=tag, window_seconds=40,
                                relic_ids=['rogue_6_relic_legacy_134']))
        for args in cases:
            with self.subTest(scenario=args):
                actual = calculate_damage(args)
                source = actual['report']['selected_module_source_reference']
                duration_links = [link for link in source['existing_coverage']['report_sections']
                                  if link['section_id'] == 'token_duration_' + TOKEN]
                self.assertEqual(len(duration_links), 1)
                duration_index = int(duration_links[0]['path'].rsplit('/', 1)[1])
                self.assertEqual(actual['report']['sections'][duration_index]['id'], 'token_duration_' + TOKEN)
                self.assertIn('/token_duration_references', source['existing_coverage']['native_paths'])
                actual.pop('token_duration_references')
                actual['report']['sections'] = [s for s in actual['report']['sections']
                                               if s['id'] != 'token_duration_' + TOKEN]
                for token in actual['relic_token_stats']:
                    token.pop('duration_reference', None)
                with patch('rouge.summons.duration_reference', return_value=None):
                    baseline = calculate_damage(args)
                source = baseline['report']['selected_module_source_reference']
                self.assertFalse(any(link['section_id'] == 'token_duration_' + TOKEN
                                     for link in source['existing_coverage']['report_sections']))
                self.assertNotIn('/token_duration_references', source['existing_coverage']['native_paths'])
                # The new report-only source links reflect reference presence.
                # Remove only its exact object and unique final notes-only block;
                # every old public numeric, estimate and report field stays compared.
                for result in (actual, baseline):
                    report = result['report']
                    self.assertEqual(report['selected_module_source_reference']['module_id'], MODULE)
                    self.assertEqual(sum(block['id'] == 'selected_module_source'
                                         for block in report['sections']), 1)
                    self.assertEqual(report['sections'][-1]['id'], 'selected_module_source')
                    self.assertEqual(report['sections'][-1]['metrics'], [])
                    report.pop('selected_module_source_reference')
                    report['sections'].pop()
                self.assertEqual(actual, baseline)

    def test_persisted_reference_keeps_pinned_sources_and_exact_selectors(self):
        path = Path(__file__).resolve().parents[1] / 'rouge/data/token-duration-reference.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(data['source_commit'], 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add')
        rule, = data['rules']
        self.assertEqual((rule['operator_id'], rule['token_id']), ('char_4230_mcnist', TOKEN))
        self.assertIn('phases[1].parts[3]', rule['module_overrides'][0]['source_selector'])
        self.assertIn('phases[2].parts[2]', rule['module_overrides'][1]['source_selector'])
        self.assertEqual(data['sources']['battle_equip_table']['sha256'],
                         '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460')


if __name__ == '__main__':
    unittest.main()
