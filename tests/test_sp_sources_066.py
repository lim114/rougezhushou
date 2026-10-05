"""Public calculator checks against pinned SP source scopes and additive values."""
import itertools
import runpy
import unittest
from pathlib import Path

from rouge.catalog import catalog
from rouge.damage import calculate_damage

MEDIC = 'rogue_6_relic_legacy_74'
GENERAL = ['rogue_6_relic_legacy_' + str(n) for n in (2, 3, 4)]
COOKIE = 'rogue_6_from_relic_15'


class NaturalSpSources(unittest.TestCase):
    def test_medical_scope_all_supported_skills(self):
        for op, profile in catalog()['operators'].items():
            for skill in range(1, len(profile['skills']) + 1):
                with self.subTest(operator=op, skill=skill):
                    scenario = {'operator':op, 'skill':skill}
                    base = calculate_damage(scenario)
                    held = calculate_damage({**scenario, 'relic_ids':[MEDIC]})
                    if profile['profession'] != 'medic':
                        self.assertEqual(held['estimate']['skill'], base['estimate']['skill'])
                        self.assertEqual(held['total_damage'], base['total_damage'])
                        self.assertIn(MEDIC, held['relic_resolution']['inapplicable'])
                    else:
                        manual = calculate_damage({**scenario, 'effects':[{'kind':'sp_recovery','value':.3}]})
                        self.assertEqual(held['estimate']['skill'], manual['estimate']['skill'])
                        self.assertNotIn(MEDIC, held['relic_resolution']['inapplicable'])

    def test_pioneer_dp_rotation_is_not_accelerated(self):
        scenario = {'operator':'char_151_myrtle','skill':1,'timing_mode':'continuous'}
        baseline = calculate_damage(scenario)
        actual = calculate_damage({**scenario,'relic_ids':[MEDIC]})
        self.assertEqual(actual['estimate']['skill'], baseline['estimate']['skill'])
        self.assertEqual(actual['estimate'].get('utility'), baseline['estimate'].get('utility'))

    def test_tank_healing_does_not_make_operator_a_medic(self):
        scenario = {'operator':'char_2025_shu','skill':3}
        baseline = calculate_damage(scenario)
        actual = calculate_damage({**scenario,'relic_ids':[MEDIC]})
        self.assertEqual(actual['estimate']['skill'], baseline['estimate']['skill'])

    def test_all_three_general_items_add_without_medic_leak(self):
        for op in ('kaltsit','silverash','char_2025_shu','char_328_cammou'):
            with self.subTest(operator=op):
                actual = calculate_damage({'operator':op,'skill':1,'relic_ids':[*GENERAL,MEDIC]})
                expected = 1 + .2 + .35 + .5 + (.3 if catalog()['operators'][op]['profession']=='medic' else 0)
                self.assertAlmostEqual(actual['estimate']['skill']['sp_recovery_per_second'], expected)

    def test_permutations_and_duplicate_ids_do_not_change_rate(self):
        scenario = {'operator':'kaltsit','skill':1}
        expected = calculate_damage({**scenario,'relic_ids':[*GENERAL,MEDIC]})['estimate']['skill']
        for ids in itertools.permutations([*GENERAL,MEDIC]):
            actual = calculate_damage({**scenario,'relic_ids':[*ids,ids[0]]})
            self.assertEqual(actual['estimate']['skill'], expected)

    def test_bound_cookie_adds_only_to_its_recipient(self):
        for op in ('kaltsit','silverash'):
            scenario = {'operator':op,'skill':1,'relic_ids':[*GENERAL,MEDIC,'rogue_6_relic_assign_15']}
            absent = calculate_damage({**scenario,'char_buff_ids':[],'char_buffs_complete':True})
            recipient = calculate_damage({**scenario,'char_buff_ids':[COOKIE]})
            self.assertAlmostEqual(recipient['estimate']['skill']['sp_recovery_per_second'],
                absent['estimate']['skill']['sp_recovery_per_second'] + .8)

    def test_combat_hp_source_remains_reference_only(self):
        for hp in (1,.65,.3,0):
            scenario = {'operator':'kaltsit','skill':1,'relic_ids':[*GENERAL,MEDIC,'rogue_6_relic_fight_15'],
                'char_buff_ids':[COOKIE],'relic_context':{'current_hp_ratio':hp}}
            actual = calculate_damage(scenario)
            self.assertAlmostEqual(actual['estimate']['skill']['sp_recovery_per_second'], 1+1.05+.3+.8)

    def test_natural_recovery_does_not_replace_attack_recovery(self):
        for op, skill in [('mechanist',1),('char_133_mm',1)]:
            scenario = {'operator':op,'skill':skill}
            baseline = calculate_damage(scenario)
            actual = calculate_damage({**scenario,'relic_ids':[*GENERAL,MEDIC],'char_buff_ids':[COOKIE]})
            self.assertIsNone(actual['estimate']['skill']['sp_recovery_per_second'])
            self.assertEqual(actual['estimate']['skill'], baseline['estimate']['skill'])

    def test_generator_preserves_the_prefab_medical_selector(self):
        module = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/build_relic_mechanics.py'))
        effects, pending = module['extract'](module['data']['relics'][MEDIC]['buffs'][0], MEDIC)
        self.assertFalse(pending)
        self.assertEqual(effects[0]['profession'], 'medic')

    def test_regeneration_preserves_completed_river_reference_descriptions(self):
        from rouge.relics import mechanics
        module = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/build_relic_mechanics.py'))
        identity = 'rogue_6_relic_fight_22'
        pending = []
        for buff in module['data']['relics'][identity]['buffs']:
            _, messages = module['extract'](buff, identity)
            pending.extend(messages)
        self.assertEqual(pending, mechanics()['relics'][identity]['pending'])


if __name__ == '__main__': unittest.main()
