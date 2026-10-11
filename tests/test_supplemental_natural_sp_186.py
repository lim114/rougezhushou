import unittest
from copy import deepcopy
from itertools import permutations
from rouge.supplemental_run import run_skill_reference,format_run_reference
from rouge.supplemental_skills import defaults,supplemental_profiles
from tests.test_supplemental_run_141 import environment


class SupplementalNaturalSP186Tests(unittest.TestCase):
    def test_base_rate_and_recovery_type_for_all_seven(self):
        for identity,p in supplemental_profiles()['operators'].items():
            with self.subTest(identity=identity):
                r=run_skill_reference(defaults(identity),environment())
                sp=r['sp_reference'];raw=p['levels'][6]['spData']
                expected=raw['increment'] if raw['spType']=='INCREASE_WITH_TIME' else None
                self.assertEqual(sp['natural_recovery_rate_parameter'],expected)
                self.assertEqual(sp['natural_recovery_bonus'],0)
                for key in ('initial_seconds','recharge_seconds','cycle_seconds'):
                    self.assertIsNone(sp[key])

    def test_three_global_sources_add_once_for_every_order(self):
        ids=['rogue_6_relic_legacy_2','rogue_6_relic_legacy_3','rogue_6_relic_legacy_4']
        for order in permutations(ids):
            r=run_skill_reference(defaults('char_123_fang'),environment([*order,order[0]]))
            self.assertAlmostEqual(r['sp_reference']['natural_recovery_rate_parameter'],2.05)
            self.assertAlmostEqual(r['sp_reference']['natural_recovery_bonus'],1.05)
            self.assertEqual(r['attribute_resolution']['unsupported'],[])

    def test_medical_selector_and_personal_recipient_are_independent(self):
        ids=['rogue_6_relic_legacy_2','rogue_6_relic_legacy_3','rogue_6_relic_legacy_4','rogue_6_relic_legacy_74']
        e=environment(ids)
        e['operator_metadata']['char_120_hibisc']={'char_buff_ids':['rogue_6_from_relic_15'],'char_buffs_complete':True}
        before=deepcopy(e)
        hibisc=run_skill_reference(defaults('char_120_hibisc'),e)
        fang=run_skill_reference(defaults('char_123_fang'),e)
        self.assertAlmostEqual(hibisc['sp_reference']['natural_recovery_rate_parameter'],3.15)
        self.assertAlmostEqual(fang['sp_reference']['natural_recovery_rate_parameter'],2.05)
        self.assertEqual(e,before)
        self.assertIn('原生冷却槽',format_run_reference(hibisc))

    def test_attack_recovery_does_not_gain_natural_rate_or_false_clock(self):
        e=environment(['rogue_6_relic_legacy_2','rogue_6_relic_legacy_74'])
        for identity in ('char_124_kroos','char_210_stward'):
            e['operator_metadata'][identity]={'char_buff_ids':['rogue_6_from_relic_15'],'char_buffs_complete':True}
            r=run_skill_reference(defaults(identity),e);sp=r['sp_reference']
            self.assertFalse(sp['natural_recovery_applicable'])
            self.assertIsNone(sp['natural_recovery_rate_parameter'])
            self.assertEqual(sp['natural_recovery_bonus'],0)
            self.assertIn('自然回技速度不适用',format_run_reference(r))

    def test_unknown_personal_recipient_blocks_complete_recovery_parameter(self):
        e=environment(['rogue_6_relic_legacy_2','rogue_6_relic_assign_15'])
        r=run_skill_reference(defaults('char_123_fang'),e)
        sp=r['sp_reference']
        self.assertIsNone(sp['natural_recovery_rate_parameter'])
        self.assertTrue(sp['unresolved_recovery_sources'])
        self.assertFalse(r['attribute_resolution']['complete_for_attribute_scope'])

    def test_combat_only_hp_source_stays_reference(self):
        r=run_skill_reference(defaults('char_123_fang'),environment(['rogue_6_relic_fight_15']))
        self.assertEqual(r['sp_reference']['natural_recovery_rate_parameter'],1)
        self.assertEqual(r['sp_reference']['natural_recovery_sources'],[])
        self.assertFalse(r['sp_reference']['current_hotfix_equivalence_proven'])
        self.assertTrue(r['attribute_resolution']['relics'][0]['reference_effects'])
