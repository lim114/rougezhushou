"""Only qualified Four-Sui text conditions are rejected; no guessing or decoding."""
from copy import deepcopy
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage

SHU='char_2025_shu'
ERROR='four_sui 不接受文本条件；请使用布尔值。'
TEXTS=('false','unknown','0','1','true','False','True','',' false ','\t','未知','是','否')


def scenario(skill=3, mode='frames', **extra):
    return {'operator':SHU,'skill':skill,'base_attack':1000,
            'timing_mode':mode,'window_seconds':10,**extra}


class FourSuiTextInputTests(unittest.TestCase):
    def assert_text_error(self, args):
        before=deepcopy(args)
        with self.assertRaises(ValueError) as raised:
            calculate_damage(args)
        self.assertEqual(str(raised.exception),ERROR)
        self.assertEqual(args,before)

    def test_raw_text_is_an_explicit_input_error_for_each_qualified_skill_and_mode(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                for text in TEXTS:
                    with self.subTest(skill=skill,mode=mode,text=repr(text)):
                        self.assert_text_error(scenario(skill,mode,four_sui=text))

    def test_error_uses_the_exact_declared_field_and_literal_instead_of_a_result_flag(self):
        # These raw original characters remain text, including empty and padded values.
        for text in ('false','unknown','0','1','',' false ','未知'):
            args=scenario(four_sui=text)
            self.assert_text_error(args)
            self.assertEqual(args['four_sui'],text)

    def test_bool_numeric_null_absence_and_other_nontext_compatibility_is_preserved(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                false=calculate_damage(scenario(skill,mode,four_sui=False))
                true=calculate_damage(scenario(skill,mode,four_sui=True))
                self.assertEqual(calculate_damage(scenario(skill,mode)),false)
                for value in (None,0,0.0,[],{}):
                    self.assertEqual(calculate_damage(scenario(skill,mode,four_sui=value)),false)
                for value in (1,1.0,2,-1,[0],{'declared':False}):
                    self.assertEqual(calculate_damage(scenario(skill,mode,four_sui=value)),true)

    def test_unlocked_true_and_false_keep_the_existing_static_and_unknown_clock_boundary(self):
        for mode in ('frames','continuous'):
            plain=calculate_damage(scenario(3,mode,four_sui=False))
            qualified=calculate_damage(scenario(3,mode,four_sui=True))
            self.assertEqual(plain['attack'],1500)
            self.assertEqual(qualified['attack'],1620)
            self.assertEqual(plain['total_damage'],12000)
            self.assertEqual(qualified['total_damage'],12960)
            self.assertEqual(qualified['shu_periodic_sp_reference']['interval_seconds_parameter'],4)
            self.assertIsNone(qualified['shu_periodic_sp_reference']['first_tick_seconds'])
            self.assertFalse(qualified['shu_periodic_sp_reference']['events_scheduled'])
            self.assertIsNone(qualified['estimate']['skill']['initial_seconds'])
            self.assertIsNone(qualified['estimate']['skill']['recharge_seconds'])

    def test_ineligible_talent_keeps_text_as_an_ignored_field(self):
        for elite,rank,skills in ((0,1,(1,)),(1,7,(1,2))):
            for skill in skills:
                for mode in ('frames','continuous'):
                    args=scenario(skill,mode,elite=elite,skill_rank=rank)
                    absent=calculate_damage(args)
                    for text in TEXTS:
                        with self.subTest(elite=elite,skill=skill,mode=mode,text=repr(text)):
                            self.assertEqual(calculate_damage({**args,'four_sui':text}),absent)

    def test_other_owners_keep_text_as_an_ignored_field(self):
        for operator in ('kaltsit','silverash','mechanist','char_002_amiya','char_298_susuro'):
            for skill in range(1,len(catalog()['operators'][operator]['skills'])+1):
                for mode in ('frames','continuous'):
                    args=scenario(skill,mode,operator=operator)
                    absent=calculate_damage(args)
                    for text in ('false','unknown','0','1',''):
                        self.assertEqual(calculate_damage({**args,'four_sui':text}),absent)

    def test_inactive_checkbox_text_and_prior_training_errors_are_preserved(self):
        for mode in ('frames','continuous'):
            # S3 conditions are guarded separately; unrelated S1/S2 stay ignored.
            for skill in (1,2):
                inactive=scenario(skill,mode,operator='silverash')
                absent=calculate_damage(inactive)
                self.assertEqual(calculate_damage({**inactive,'preexisting_fragile':'false'}),absent)
                self.assertEqual(calculate_damage({**inactive,'cooperative':'unknown'}),absent)
        for args in (scenario(2,elite=0,skill_rank=1,four_sui='false'),
                     scenario(1,elite=1,skill_rank=10,four_sui='unknown')):
            with self.assertRaises(ValueError) as raised:
                calculate_damage(args)
            self.assertEqual(str(raised.exception),'当前精英阶段尚未开放所选技能或专精。')


if __name__=='__main__':
    unittest.main()
