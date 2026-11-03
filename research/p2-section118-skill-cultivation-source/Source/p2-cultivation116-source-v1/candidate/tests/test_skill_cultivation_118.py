"""Read-source selection and original training/use separation.

Authored as Source only. Root must run these against the applied product and
separately exercise the actual window, checkbox reset and saved-state boundary.
"""
from copy import deepcopy
import json
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.reporting import format_report
from rouge.skill_cultivation import select_rank, rank_label, explanation, format_explanation, _source_data


OP = 'char_298_susuro'


def record(rank=None, *, scope='run', skill=1, missing=False, **extra):
    return {'scope': scope, 'fields': {}, 'skill_ranks': {} if missing else {str(skill): rank}, **extra}


class SkillCultivation118Tests(unittest.TestCase):
    def choose(self, elite=1, *, op=OP, skill=1, state=None, account=None, prefer=False):
        before = deepcopy((state, account))
        selected = select_rank(catalog()['operators'][op], skill, elite,
                               state=state, account=account, account_reference=prefer)
        self.assertEqual((state, account), before)
        return selected

    def row(self, selected, *, op=OP, skill=1, elite=1):
        source_before = json.dumps(_source_data(), ensure_ascii=False)
        row = explanation(op, catalog()['operators'][op], skill, elite, selected)
        self.assertEqual(json.dumps(_source_data(), ensure_ascii=False), source_before)
        return row

    def test_default_missing_run_rank_keeps_old_preview_and_does_not_fill_account(self):
        for elite, expected in ((0, 7), (1, 7), (2, 10)):
            selected = self.choose(elite, state=record(missing=True), account=record(3, scope='operator_profile'))
            self.assertEqual(selected['rank'], expected)
            self.assertEqual(selected['source'], 'preview_unconfirmed')
            self.assertFalse(selected['manual_reference_applied'])

    def test_default_run_rank_wins_over_different_account_rank(self):
        selected = self.choose(state=record(3), account=record(7, scope='operator_profile'))
        self.assertEqual(selected['rank'], 3)
        self.assertEqual(selected['source'], 'run_confirmed')
        self.assertEqual(rank_label(selected), '等级 3（读取）')

    def test_explicit_account_reference_can_choose_higher_and_lower_read_rank(self):
        for run, account in ((3, 7), (7, 2)):
            selected = self.choose(state=record(run), account=record(account, scope='operator_profile'), prefer=True)
            self.assertEqual(selected['rank'], account)
            self.assertEqual(selected['source'], 'manual_account_reference')
            self.assertTrue(selected['manual_reference_applied'])
            self.assertIn('局外模拟', rank_label(selected))
            text = format_explanation(self.row(selected))
            self.assertIn('本局未确认', text)
            self.assertIn('取消勾选可恢复', text)

    def test_cancelling_reference_returns_to_original_run_rank(self):
        args = {'state': record(3), 'account': record(7, scope='operator_profile')}
        self.assertEqual(self.choose(prefer=True, **args)['rank'], 7)
        returned = self.choose(prefer=False, **args)
        self.assertEqual(returned['rank'], 3)
        self.assertEqual(returned['source'], 'run_confirmed')

    def test_account_only_view_is_reference_and_keeps_old_read_label(self):
        selected = self.choose(state=record(5, scope='operator_profile'))
        self.assertEqual(selected['source'], 'account_reference')
        self.assertEqual(rank_label(selected), '等级 5（读取）')
        self.assertIn('账号档案参考，本局未确认', format_explanation(self.row(selected)))

    def test_compatible_account_mastery_is_available_only_at_existing_elite2_gate(self):
        for elite in (0, 1):
            selected = self.choose(elite, state=record(3), account=record(10, scope='operator_profile'), prefer=True)
            self.assertEqual(selected['rank'], 3)
            self.assertFalse(selected['account_usable'])
            self.assertIn('不会自动改成7级', selected['account_reason'])
        selected = self.choose(2, state=record(7), account=record(10, scope='operator_profile'), prefer=True)
        self.assertEqual(selected['rank'], 10)
        self.assertTrue(selected['manual_reference_applied'])

    def test_locked_skill_cannot_adopt_account_reference_or_gain_new_unlock(self):
        selected = self.choose(0, op='mechanist', skill=2, state=record(missing=True),
                               account=record(7, scope='operator_profile', skill=2), prefer=True)
        self.assertFalse(selected['account_usable'])
        row = self.row(selected, op='mechanist', skill=2, elite=0)
        self.assertFalse(row['model_gate_met'])
        self.assertEqual(row['skill_unlock_elite'], 1)
        with self.assertRaisesRegex(ValueError, '当前精英阶段尚未开放'):
            calculate_damage({'operator':'mechanist','skill':2,'skill_rank':selected['rank'],'elite':0,'level':1})

    def test_invalid_new_reference_leaves_never_replace_qualified_default(self):
        for rank in (None, False, True, 0, 11, 7.0, '7', [], {}):
            with self.subTest(rank=repr(rank)):
                selected = self.choose(state=record(3), account=record(rank, scope='operator_profile'), prefer=True)
                self.assertEqual(selected['rank'], 3)
                self.assertFalse(selected['manual_reference_applied'])
                self.assertTrue(selected['account_reason'])

    def test_masked_account_reference_is_not_used(self):
        for invalid in (['1'], [1]):
            selected = self.choose(state=record(3), account=record(7, scope='operator_profile', invalid_skill_ranks=invalid), prefer=True)
            self.assertEqual(selected['rank'], 3)
            self.assertFalse(selected['account_usable'])

    def test_string_and_integer_keys_keep_old_priority(self):
        state = {'scope':'run', 'skill_ranks':{'1':3,1:7}}
        account = {'scope':'operator_profile', 'skill_ranks':{'1':5,1:2}}
        self.assertEqual(self.choose(state=state, account=account)['rank'], 3)
        self.assertEqual(self.choose(state=state, account=account, prefer=True)['rank'], 5)

    def test_e0_common5to7_training_gate_does_not_claim_use_evidence(self):
        for rank in (5, 6, 7):
            selected = self.choose(0, state=record(rank))
            row = self.row(selected, elite=0)
            self.assertEqual(row['training_requirement']['raw'], {'phase':'PHASE_1','level':1})
            self.assertTrue(row['model_gate_met'])
            self.assertIsNone(row['e0_common_use_verified'])
            self.assertFalse(row['arithmetic_changed_by_explanation'])
            text = format_explanation(row)
            self.assertIn('实际', text)
            self.assertIn('仍未核验', text)
            self.assertIn('这是训练条件', text)

    def test_all_30_original_forms_and_83_skills_have_exact_training_coordinates(self):
        source = _source_data()
        self.assertEqual(len(source['operators']), 30)
        self.assertEqual(sum(len(p['skills']) for p in source['operators'].values()), 83)
        for op, original in source['operators'].items():
            profile = catalog()['operators'][op]
            for skill in range(1, len(profile['skills'])+1):
                for rank in (1, 4, 7, 8, 10):
                    selected = self.choose(2, op=op, skill=skill, state=record(rank, skill=skill))
                    row = self.row(selected, op=op, skill=skill, elite=2)
                    self.assertEqual(row['original_source_status'], 'located')
                    if rank == 1:
                        self.assertIsNone(row['training_requirement'])
                    elif rank <= 7:
                        self.assertEqual(row['training_requirement']['raw'], original['allSkillLvlup'][rank-2]['unlockCond'])
                        self.assertTrue(row['training_requirement']['path'].endswith(f'allSkillLvlup[{rank-2}].unlockCond'))
                    else:
                        self.assertEqual(row['training_requirement']['raw'], original['skills'][skill-1]['levelUpCostCond'][rank-8]['unlockCond'])
                        self.assertIn(f'skills[{skill-1}].levelUpCostCond[{rank-8}]', row['training_requirement']['path'])

    def test_missing_patch_form_originals_remain_missing_without_borrowing_caster(self):
        for op in ('char_1001_amiya2','char_1037_amiya3'):
            selected = self.choose(2, op=op, state=record(10))
            row = self.row(selected, op=op, elite=2)
            self.assertEqual(row['original_source_status'], 'missing')
            self.assertIsNone(row['training_requirement'])
            self.assertIsNone(row['skill_original_gate'])
            self.assertIn('不借用其他职业', format_explanation(row))

    def test_changed_skill_identity_or_unlock_cannot_locate_old_original(self):
        profile = deepcopy(catalog()['operators'][OP])
        selected = self.choose(state=record(7))
        for field, value in (('id','public_unmatched_skill'), ('unlock_elite',2)):
            changed = deepcopy(profile)
            changed['skills'][0][field] = value
            row = explanation(OP, changed, 1, 2, selected)
            self.assertEqual(row['original_source_status'], 'missing')

    def test_original_recruit_caps_are_reference_and_do_not_fill_skill_facts(self):
        selected = self.choose(state=record(missing=True))
        row = self.row(selected)
        self.assertEqual(row['recruit_upper_bounds']['0'], {'evolvePhase':'PHASE_1','skillLevel':7,'skillSpecializeLevel':0})
        self.assertEqual(row['recruit_upper_bounds']['1'], {'evolvePhase':'PHASE_2','skillLevel':7,'skillSpecializeLevel':3})
        self.assertEqual(row['rank_source'], 'preview_unconfirmed')
        self.assertIsNone(row['actual_activation_verified'])
        self.assertIsNone(row['account_training_verified'])

    def test_default_old_preview_label_and_no_selection_remain(self):
        self.assertEqual(rank_label(self.choose(0, state=record(missing=True))), '等级 7（未确认，档案预览）')
        self.assertEqual(rank_label(self.choose(2, state=record(missing=True))), '专精 3（未确认，档案预览）')
        for profile, skill in ((None, None), (catalog()['operators'][OP], None), (catalog()['operators'][OP], True)):
            selected = select_rank(profile, skill, 2, account_reference=True)
            self.assertIsNone(selected['rank'])
            self.assertFalse(selected['account_usable'])
            self.assertEqual(rank_label(selected), '无可用技能')

    def test_explicit_reference_drives_real_healing_level_and_cancel_restores_full_result(self):
        for mode in ('frames','continuous'):
            args = {'operator':OP,'skill':1,'elite':1,'level':40,'trust':0,'potential':1,
                    'window_seconds':10,'timing_mode':mode,'continuous_attacks':True,
                    'low_cost_healing_target':False}
            state, account = record(3), record(7, scope='operator_profile')
            chosen = self.choose(state=state, account=account, prefer=True)
            plain = self.choose(state=state, account=account, prefer=False)
            selected_result = calculate_damage({**args,'skill_rank':chosen['rank']})
            original_result = calculate_damage({**args,'skill_rank':plain['rank']})
            self.assertEqual(selected_result, calculate_damage({**args,'skill_rank':7}))
            self.assertEqual(original_result, calculate_damage({**args,'skill_rank':3}))
            self.assertNotEqual(selected_result['estimate']['skill']['total_healing'], original_result['estimate']['skill']['total_healing'])
            before = deepcopy(selected_result)
            format_report(selected_result['report'])
            format_report(selected_result['report'], technical=True)
            self.assertEqual(selected_result, before)

    def test_e0_accepted_common5to7_results_stay_old_api_results(self):
        for mode in ('frames','continuous'):
            for rank in (5,6,7):
                args = {'operator':OP,'skill':1,'elite':0,'level':1,'trust':0,'potential':1,
                        'skill_rank':rank,'window_seconds':10,'timing_mode':mode}
                before = deepcopy(args)
                baseline = calculate_damage(args)
                selected = self.choose(0, state=record(rank), account=record(3, scope='operator_profile'))
                self.assertEqual(calculate_damage({**args,'skill_rank':selected['rank']}), baseline)
                self.row(selected, elite=0)
                self.assertEqual(args, before)


if __name__ == '__main__':
    unittest.main()
