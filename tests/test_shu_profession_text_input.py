"""Shu's selected profession talent rejects text without decoding conditions."""
from copy import deepcopy
import unittest
from rouge.catalog import catalog
from rouge.damage import calculate_damage

SHU='char_2025_shu'
FIELDS=('three_professions','three_same_profession')
TEXTS=('','false','False','0','true','1',' unknown ','\t','未知','否')
def scenario(skill=3,mode='frames',**extra):
    return {'operator':SHU,'skill':skill,'timing_mode':mode,'window_seconds':10,**extra}


class ShuProfessionTextInputTests(unittest.TestCase):
    def assert_field_error(self,args,field):
        before=deepcopy(args)
        with self.assertRaises(ValueError) as raised:
            calculate_damage(args)
        self.assertEqual(str(raised.exception),field+' 不接受文本条件；请使用布尔值。')
        self.assertEqual(args,before)

    def test_each_selected_field_rejects_literal_strings_for_all_skills_modes_and_rank_boundaries(self):
        for field in FIELDS:
            for skill in (1,2,3):
                for mode in ('frames','continuous'):
                    for rank in (1,7,10):
                        for text in TEXTS:
                            with self.subTest(field=field,skill=skill,mode=mode,rank=rank,text=repr(text)):
                                self.assert_field_error(scenario(skill,mode,skill_rank=rank,**{field:text}),field)

    def test_nontext_truthiness_keeps_complete_bool_numeric_null_and_container_results(self):
        for field in FIELDS:
            for skill in (1,2,3):
                for mode in ('frames','continuous'):
                    args=scenario(skill,mode)
                    false=calculate_damage({**args,field:False})
                    true=calculate_damage({**args,field:True})
                    self.assertEqual(calculate_damage(args),false)
                    for value in (None,0,0.0,-0.0,[],{}):
                        self.assertEqual(calculate_damage({**args,field:value}),false)
                    for value in (1,1.0,2,-1,[False],{'enabled':False}):
                        self.assertEqual(calculate_damage({**args,field:value}),true)

    def test_preexisting_training_errors_and_four_sui_errors_take_priority(self):
        for args in (scenario(2,elite=0,skill_rank=1),scenario(1,elite=1,skill_rank=10)):
            with self.assertRaises(ValueError) as raised:
                calculate_damage({**args,**dict.fromkeys(FIELDS,'false'),'four_sui':'false'})
            self.assertEqual(str(raised.exception),'当前精英阶段尚未开放所选技能或专精。')
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                self.assert_field_error(scenario(skill,mode,four_sui='false',**dict.fromkeys(FIELDS,'false')),'four_sui')
                self.assert_field_error(scenario(skill,mode,**dict.fromkeys(FIELDS,'false')),'three_professions')

    def test_unselected_elite_zero_one_fields_keep_whole_outputs(self):
        for elite,rank,skills in ((0,1,(1,)),(1,7,(1,2))):
            for skill in skills:
                for mode in ('frames','continuous'):
                    args=scenario(skill,mode,elite=elite,skill_rank=rank)
                    expected=calculate_damage(args)
                    for field in FIELDS:
                        for value in (False,True,*TEXTS):
                            self.assertEqual(calculate_damage({**args,field:value}),expected)
                    self.assertEqual(calculate_damage({**args,**dict.fromkeys(FIELDS,'false')}),expected)

    def test_other_owners_both_fields_keep_complete_outputs(self):
        for operator,entry in catalog()['operators'].items():
            if operator==SHU:continue
            for skill in range(1,len(entry['skills'])+1):
                for mode in ('frames','continuous'):
                    args=scenario(skill,mode,operator=operator)
                    expected=calculate_damage(args)
                    for field in FIELDS:
                        self.assertEqual(calculate_damage({**args,field:'false'}),expected)
                    self.assertEqual(calculate_damage({**args,**dict.fromkeys(FIELDS,'false')}),expected)

    def test_hp_speed_apply_to_selected_shu_without_changing_periodic_unknown_clock(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                args=scenario(skill,mode,four_sui=True)
                plain=calculate_damage(args)
                selected=calculate_damage({**args,**dict.fromkeys(FIELDS,True)})
                stats=selected['estimate']['base_stats'];base=plain['estimate']['base_stats']
                self.assertAlmostEqual(stats['hp'],base['hp']*1.12)
                self.assertEqual(stats['attack_speed_reference'],base['attack_speed_reference']+12)
                self.assertEqual(stats['attack'],base['attack'])
                self.assertEqual(selected['estimate']['skill']['sp_recovery_per_second'],1)
                ref=selected['shu_periodic_sp_reference']
                self.assertEqual((ref['interval_seconds_parameter'],ref['sp_per_pulse_parameter']),(4,1))
                for key in ('first_tick_seconds','actual_tick_times_seconds','clock_origin','reset_rule','blocked_credit_rule'):
                    self.assertIsNone(ref[key],key)
                self.assertFalse(ref['events_scheduled'])
                for key in ('initial_seconds','recharge_seconds','cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps'):
                    self.assertIsNone(selected['estimate']['skill'][key],key)

    def test_zero_window_target_absence_and_module_boundaries_do_not_bypass_text_guard(self):
        conditions=({'window_seconds':0},{'timing':{'target_disappears_seconds':0}},
                    {'timing':{'target_windows':[]}},
                    {'level':59,'potential':6,'module_id':'uniequip_002_shu','module_level':3},
                    {'level':60,'potential':6,'module_id':'uniequip_002_shu','module_level':3})
        for field in FIELDS:
            for skill in (1,2,3):
                for mode in ('frames','continuous'):
                    for condition in conditions:
                        self.assert_field_error(scenario(skill,mode,**{**condition,field:'false'}),field)
                        false=calculate_damage(scenario(skill,mode,**{**condition,field:False}))
                        self.assertEqual(calculate_damage(scenario(skill,mode,**{**condition,field:0})),false)
                        if condition.get('window_seconds')==0:
                            self.assertEqual(false['total_damage'],0)
                            self.assertEqual(false['total_healing'],0)

    def test_errors_and_successes_leave_caller_and_cached_catalog_isolated(self):
        cached=deepcopy(catalog())
        for field in FIELDS:
            args=scenario(**{field:'false'},timing={'target_windows':[[0,10]]})
            self.assert_field_error(args,field)
        args=scenario(**dict.fromkeys(FIELDS,True))
        before=deepcopy(args)
        first=calculate_damage(args)
        expected=deepcopy(first)
        first['estimate']['base_stats']['hp']=-1
        self.assertEqual(calculate_damage(args),expected)
        self.assertEqual(args,before)
        self.assertEqual(catalog(),cached)


if __name__=='__main__':unittest.main()
