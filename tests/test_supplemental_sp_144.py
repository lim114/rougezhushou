import unittest
from copy import deepcopy
from rouge.supplemental_run import run_skill_reference,format_run_reference
from rouge.supplemental_skills import defaults,supplemental_profiles
from tests.test_supplemental_run_141 import environment


class SupplementalSP144Tests(unittest.TestCase):
    def test_all_seven_keep_original_parameters_and_unknown_clocks(self):
        for identity,p in supplemental_profiles()['operators'].items():
            r=run_skill_reference(defaults(identity),environment());sp=r['sp_reference'];raw=p['levels'][6]['spData']
            self.assertEqual(sp['cost_parameter'],raw['spCost'])
            self.assertEqual(sp['initial_parameter'],raw['initSp'])
            self.assertEqual(sp['initial_requirement'],max(0,raw['spCost']-raw['initSp']))
            self.assertIsNone(sp['initial_seconds']);self.assertIsNone(sp['cycle_seconds'])

    def test_initial_sources_add_once_and_excess_does_not_generate_zero_clock(self):
        e=environment(['rogue_6_relic_legacy_95','rogue_6_relic_legacy_96','rogue_6_relic_legacy_97',
                       'rogue_6_relic_legacy_98','rogue_6_relic_legacy_99','rogue_6_relic_legacy_99'])
        r=run_skill_reference(defaults('char_123_fang'),e)
        self.assertEqual(r['sp_reference']['initial_parameter'],46)
        self.assertEqual(r['sp_reference']['initial_requirement'],0)
        self.assertIsNone(r['sp_reference']['initial_seconds'])
        self.assertEqual(r['attribute_resolution']['unsupported'],[])

    def test_skill_cost_single_source_and_two_source_unknown(self):
        p=defaults('char_123_fang');e=environment(['rogue_6_relic_hand_1'])
        r=run_skill_reference(p,e);self.assertEqual(r['sp_reference']['cost_parameter'],12.5)
        e['operator_metadata'][p['operator']]={'char_buff_ids':['rogue_6_from_relic_13']}
        r=run_skill_reference(p,e)
        self.assertIsNone(r['sp_reference']['cost_parameter'])
        self.assertIsNone(r['sp_reference']['initial_requirement'])
        self.assertTrue(r['sp_reference']['unresolved_cost_sources'])
        self.assertIn('叠加规则',format_run_reference(r))

    def test_personal_snack_does_not_follow_selected_operator(self):
        e=environment();e['operator_metadata']['char_124_kroos']={'char_buff_ids':['rogue_6_from_relic_13']}
        before=deepcopy(e)
        r=run_skill_reference(defaults('char_124_kroos'),e)
        self.assertEqual(r['sp_reference']['cost_parameter'],3.2)
        other=run_skill_reference(defaults('char_210_stward'),e)
        self.assertEqual(other['sp_reference']['cost_parameter'],4)
        self.assertEqual(e,before)

    def test_end_return_parameter_and_unverified_combination(self):
        e=environment(['rogue_6_relic_fight_27'])
        r=run_skill_reference(defaults(),e)
        self.assertEqual(r['sp_reference']['recharge_requirement'],38)
        self.assertIsNone(r['sp_reference']['recharge_seconds'])
        e['relic_ids'].append('rogue_6_relic_fight_28')
        r=run_skill_reference(defaults(),e)
        self.assertIsNone(r['sp_reference']['end_return_parameter'])
        self.assertIsNone(r['sp_reference']['recharge_requirement'])
        self.assertIn('实际结束',format_run_reference(r))
