import unittest
from copy import deepcopy

from rouge.p2_technology_upgrade import (automatic_gate_qualification, capture_account_reference,
    format_technology_upgrade, source_data, technology_upgrade_plan)


def snapshot(**states):
    return {'profile_name': '公开临时账户声明', 'nodes': states}


def preview(steps=(), **values):
    return {'mode': 'regular', 'grade': 9, 'budget': 10, 'steps': list(steps), **values}


def step(node='rogue_6_outbuff_10', accepted=True, charge=2, refund=0):
    return {'node_id': node, 'accepted': accepted, 'charged_tokens': charge, 'refunded_tokens': refund}


class TechnologyUpgradeTests(unittest.TestCase):
    def test_three_gates_use_any_one_predecessor_not_the_manual_gate_mark(self):
        s = snapshot(rogue_6_outbuff_10='unlocked', rogue_6_outbuff_11='locked',
                     rogue_6_outbuff_25='unlocked', rogue_6_outbuff_38='locked',
                     rogue_6_outbuff_39='unlocked', rogue_6_outbuff_40='unknown',
                     rogue_6_difficulty_1='locked', rogue_6_difficulty_2='locked')
        rows = automatic_gate_qualification(s, 'regular', 9)
        self.assertEqual([row['grade_threshold'] for row in rows], [3, 6, 9])
        self.assertEqual([row['eligible_reference'] for row in rows], [True, True, True])
        self.assertTrue(rows[0]['manual_mark_context_difference'])
        self.assertEqual([row['token_cost_reference'] for row in rows], [0, 0, 0])
        self.assertTrue(all(row['actual_active'] is None and row['buff_numeric_effect'] is None for row in rows))

    def test_grade_edges_and_other_mode_never_promote_activation(self):
        s = snapshot(rogue_6_outbuff_10='unlocked', rogue_6_outbuff_25='unlocked', rogue_6_outbuff_38='unlocked')
        for grade, expected in [(2, [False, False, False]), (3, [True, False, False]),
                                (5, [True, False, False]), (6, [True, True, False]),
                                (8, [True, True, False]), (9, [True, True, True])]:
            with self.subTest(grade=grade):
                self.assertEqual([row['eligible_reference'] for row in automatic_gate_qualification(s, 'regular', grade)], expected)
        self.assertEqual([r['eligible_reference'] for r in automatic_gate_qualification(s, 'other', 15)], [False] * 3)
        self.assertEqual([r['eligible_reference'] for r in automatic_gate_qualification(s, None, 9)], [None] * 3)

    def test_unknown_predecessors_stay_unknown_and_an_unlocked_gate_mark_is_not_a_shortcut(self):
        s = snapshot(rogue_6_outbuff_10='locked', rogue_6_outbuff_11='unknown', rogue_6_difficulty_1='unlocked')
        self.assertIsNone(automatic_gate_qualification(s, 'regular', 3)[0]['eligible_reference'])
        s['nodes']['rogue_6_outbuff_11'] = 'locked'
        gate = automatic_gate_qualification(s, 'regular', 3)[0]
        self.assertFalse(gate['eligible_reference']); self.assertTrue(gate['manual_mark_context_difference'])
        self.assertFalse(automatic_gate_qualification(snapshot(), 'other', None)[0]['eligible_reference'])

    def test_accepted_scenario_updates_automatic_gate_and_budget_without_account_write(self):
        s = snapshot(rogue_6_outbuff_10='locked', rogue_6_outbuff_11='locked', rogue_6_difficulty_1='locked')
        p = preview([step()], grade=3, budget=5); before = deepcopy((s, p))
        plan = technology_upgrade_plan(s, p)
        self.assertFalse(plan['initial_gates'][0]['eligible_reference'])
        self.assertTrue(plan['final_gates'][0]['eligible_reference'])
        self.assertEqual((plan['selected_cost_reference'], plan['planned_remaining_reference'], plan['declared_budget_after']), (2, 3, 3))
        self.assertEqual((s, p), before)
        self.assertEqual(plan['projected_nodes_reference']['rogue_6_difficulty_1'], 'locked')
        self.assertIsNone(plan['actual_activation']); self.assertFalse(plan['game_account_identity_verified'])

    def test_rejected_step_can_have_declared_charge_and_does_not_invent_a_refund(self):
        s = snapshot(rogue_6_outbuff_10='locked', rogue_6_outbuff_11='locked')
        plan = technology_upgrade_plan(s, preview([step(accepted=False, charge=1, refund=0)], budget=5))
        self.assertEqual(plan['declared_budget_after'], 4)
        self.assertEqual(plan['projected_nodes_reference']['rogue_6_outbuff_10'], 'locked')
        self.assertFalse(plan['final_gates'][0]['eligible_reference'])
        plan = technology_upgrade_plan(s, preview([step(accepted=False, charge=None, refund=None)], budget=5))
        self.assertIsNone(plan['declared_budget_after'])

    def test_selected_cost_bound_includes_unknown_unlock_but_not_unselected_prerequisites(self):
        s = snapshot(rogue_6_outbuff_10='locked', rogue_6_outbuff_11='unknown', rogue_6_outbuff_1='unlocked')
        steps = [step('rogue_6_outbuff_1', charge=0), step(), step('rogue_6_outbuff_11')]
        plan = technology_upgrade_plan(s, preview(steps))
        self.assertEqual((plan['selected_cost_min'], plan['selected_cost_max']), (2, 4))
        self.assertIsNone(plan['selected_cost_reference']); self.assertIsNone(plan['planned_remaining_reference'])
        self.assertEqual(plan['rows'][0]['planned_cost_reference'], 0)
        self.assertIsNone(plan['full_prerequisite_cost']); self.assertIsNone(plan['minimum_required_plan'])
        self.assertTrue(all(row['ordinary_prerequisite_logic'] == 'unknown' and row['actual_purchase_legal'] is None for row in plan['rows']))

    def test_unknown_and_negative_declared_budget_never_turn_into_missing_points(self):
        s = snapshot(rogue_6_outbuff_10='locked', rogue_6_outbuff_11='locked')
        plan = technology_upgrade_plan(s, preview([step(charge=None), step('rogue_6_outbuff_11', charge=0)], budget=5))
        self.assertTrue(all(row['declared_budget_after'] is None for row in plan['rows']))
        plan = technology_upgrade_plan(s, preview([step(charge=3), step('rogue_6_outbuff_11', charge=0)], budget=2))
        self.assertEqual(plan['rows'][0]['declared_budget_shortfall'], 1)
        self.assertIsNone(plan['rows'][0]['declared_budget_after']); self.assertIsNone(plan['rows'][1]['declared_budget_after'])
        self.assertIsNone(technology_upgrade_plan(s, preview([step()], budget=None))['declared_budget_after'])

    def test_read_only_account_adapter_only_reads_existing_views(self):
        class ReadOnlyAccount:
            profile_name = '公开测试档案'
            def __init__(self): self.read = []
            def view(self, identity): self.read.append(identity); return {'status': 'locked'}
            def save(self): raise AssertionError('不得保存')
            def set_status(self, *_): raise AssertionError('不得修改')
        account = ReadOnlyAccount(); captured = capture_account_reference(account)
        self.assertEqual(len(captured['nodes']), 57); self.assertEqual(len(account.read), 57)
        self.assertEqual(set(captured['nodes'].values()), {'locked'})

    def test_automatic_nodes_duplicate_purchases_and_noninteger_amounts_rejected(self):
        for steps in ([step('rogue_6_difficulty_1', charge=0)], [step(), step()],
                      [step(accepted=1)], [step(charge=True)], [step(refund=-1)],
                      [step(charge='2')], [dict(step(), extra=0)]):
            with self.subTest(steps=steps), self.assertRaises(ValueError): technology_upgrade_plan(snapshot(), preview(steps))
        for values in ({'grade': True}, {'grade': 16}, {'mode': 'all'}, {'budget': 1.0}, {'budget': -1}):
            with self.subTest(values=values), self.assertRaises(ValueError): technology_upgrade_plan(snapshot(), preview(**values))
        for s in ({'profile_name': 'x', 'nodes': {'missing': 'locked'}},
                  {'profile_name': 'x', 'nodes': {'rogue_6_outbuff_10': True}}):
            with self.assertRaises(ValueError): technology_upgrade_plan(s, preview())

    def test_source_is_immutable_and_copy_preserves_mode_grade_predecessor_context(self):
        before = deepcopy(source_data())
        plan = technology_upgrade_plan(snapshot(rogue_6_outbuff_10='locked'), preview([step()], grade=3))
        plan['public_rule']['quote'] = 'changed'
        self.assertEqual(source_data(), before)
        text = format_technology_upgrade(plan)
        for needle in ('常规行动', '保密等级声明：3', '脊髓', '初始前置声明', '完整前置费用未知', '实际激活未知'):
            self.assertIn(needle, text)


if __name__ == '__main__': unittest.main()
