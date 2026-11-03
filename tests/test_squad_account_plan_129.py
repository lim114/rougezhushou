import unittest
from copy import deepcopy
from rouge.squad_account_plan import squad_account_plan, format_squad_plan
from rouge.technology_state import TechnologyState
from rouge.run_config import config_data


class SquadAccountPlanTests(unittest.TestCase):
    def test_all_conditions_and_manual_unknowns(self):
        state = TechnologyState(); before = state.snapshot()
        plan = squad_account_plan(state, 0)
        self.assertEqual(len(plan['rows']), 7)
        for row in plan['rows']:
            self.assertEqual(row['condition'], config_data()['squads'][row['squad_id']]['unlockCondDesc'])
            self.assertEqual(row['manual_status'], 'unknown')
            self.assertIsNone(row['account_unlocked']); self.assertIsNone(row['actual_activation'])
        self.assertEqual(state.snapshot(), before)

    def test_profile_switch_and_grade_do_not_authorize_effects(self):
        state = TechnologyState(); state.set_status('rogue_6_difficulty_3', 'unlocked')
        for grade in (0, 8, 9, 15):
            row = next(r for r in squad_account_plan(state, grade)['rows'] if r['squad_id'] == 'rogue_6_band_7')
            self.assertEqual(row['manual_status'], 'unlocked'); self.assertEqual(row['grade_parameter_met'], grade >= 9)
            self.assertIsNone(row['actual_activation'])
        state.create_profile('另一份资料')
        self.assertTrue(all(r['manual_status'] == 'unknown' for r in squad_account_plan(state, 15)['rows']))
        state.select_profile('default')
        self.assertIn('已解锁', format_squad_plan(squad_account_plan(state, 9)))

    def test_manual_locked_and_special_squad_independent(self):
        state = TechnologyState(); state.set_status('rogue_6_outbuff_43', 'locked')
        rows = squad_account_plan(state, 15)['rows']
        self.assertEqual(next(r for r in rows if r['squad_id'] == 'rogue_6_band_16')['manual_status'], 'locked')
        special = next(r for r in rows if r['squad_id'] == 'rogue_6_band_22')
        self.assertIsNone(special['technology_id']); self.assertIsNone(special['grade_parameter_met'])

    def test_invalid_grade_and_copied_sources(self):
        state = TechnologyState(); source = deepcopy(config_data())
        for grade in (True, 1.0, -1, 16, '9', None):
            with self.assertRaises(ValueError): squad_account_plan(state, grade)
        plan = squad_account_plan(state, 9); plan['rows'][0]['reference']['source']['sha256'] = 'edited'
        self.assertEqual(config_data(), source)
        self.assertIn('账户身份', format_squad_plan(squad_account_plan(state, 9)))
