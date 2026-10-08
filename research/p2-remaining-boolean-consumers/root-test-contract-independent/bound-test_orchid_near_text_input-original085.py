"""Orchid's selected near-location talent rejects text after existing errors."""
from copy import deepcopy
import unittest
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.operator_engine import selected_talents
from rouge.reporting import format_report

OP='char_1048_orchd2'
MOD='uniequip_002_orchd2'
FIELD='near_previous_deployment'
ERROR=FIELD+' 不接受文本条件；请使用布尔值。'

def scenario(skill=1,mode='frames',**extra):
    return {'operator':OP,'skill':skill,'skill_rank':10,'elite':2,'level':90,
            'base_attack':1000,'timing_mode':mode,'window_seconds':10,**extra}

def record(args):
    result=calculate_damage(args)
    return (result,format_estimate(result),format_report(result),format_report(result,technical=True))

def error(args):
    try:
        calculate_damage(args)
    except Exception as exc:
        return (type(exc).__name__,str(exc))
    raise AssertionError('Expected an original invalid input error.')


class OrchidNearTextInputTests(unittest.TestCase):
    def assert_text_error(self,args):
        before=deepcopy(args)
        self.assertEqual(error(args),('ValueError',ERROR))
        self.assertEqual(args,before)

    def test_selected_all_skills_modes_reject_text_without_decoding_values(self):
        for skill in (1,2,3):
            for mode in ('frames','continuous'):
                for text in ('false','','0',' 未知 '):
                    with self.subTest(skill=skill,mode=mode,text=text):
                        self.assert_text_error(scenario(skill,mode,**{FIELD:text}))

    def test_actual_selected_helper_controls_base_and_module_qualification(self):
        rows=((0,1,1,0,None),(1,1,7,0,.10),(2,1,10,0,.15),
              (2,59,10,3,.15),(2,60,10,1,.15),(2,60,10,2,.20),(2,60,10,3,.20))
        for elite,level,rank,stage,attack_bonus in rows:
            args=scenario(elite=elite,level=level,skill_rank=rank,**{FIELD:'false'})
            if stage:args.update(module_id=MOD,module_level=stage)
            chosen,_=selected_talents(catalog()['operators'][OP],args)
            named=[t for t in chosen if t.get('name')=='翔虫机动']
            if attack_bonus is None:
                self.assertFalse(named)
                self.assertEqual(record(args),record({**args,FIELD:False}))
            else:
                self.assertEqual(named[0]['values']['atk'],attack_bonus)
                self.assertEqual(named[0]['values']['atk_duration'],30)
                self.assert_text_error(args)
                plain=calculate_damage({**args,FIELD:False})
                near=calculate_damage({**args,FIELD:True})
                self.assertEqual(near['estimate']['base_stats']['attack'],1000*(1+attack_bonus))
                self.assertEqual(plain['estimate']['base_stats']['attack'],1000)

    def test_inactive_elite_zero_text_keeps_complete_outputs_and_reports(self):
        for mode in ('frames','continuous'):
            args=scenario(mode=mode,elite=0,level=1,skill_rank=1,module_id=MOD,module_level=3)
            expected=record(args)
            for value in ('false','',True,False,'未知'):
                self.assertEqual(record({**args,FIELD:value}),expected)

    def test_other_owner_ignored_field_keeps_complete_outputs_and_reports(self):
        for owner in ('char_133_mm','char_2025_shu','char_1041_angel2'):
            args={'operator':owner,'skill':1,'window_seconds':10,'base_attack':1000}
            expected=record(args)
            self.assertEqual(record({**args,FIELD:'false'}),expected)

    def test_nontext_bool_numeric_null_and_container_aliases_keep_old_contract(self):
        for elite,level,skill,stage in ((1,1,2,0),(2,90,1,0),(2,60,3,2)):
            for mode in ('frames','continuous'):
                args=scenario(skill,mode,elite=elite,level=level,skill_rank=7 if elite==1 else 10)
                if stage:args.update(module_id=MOD,module_level=stage)
                false=record({**args,FIELD:False});true=record({**args,FIELD:True})
                self.assertEqual(record(args),false)
                for value in (None,0,0.0,-0.0,[],{}):
                    self.assertEqual(record({**args,FIELD:value}),false)
                for value in (1,1.0,-1,[False],{'enabled':False}):
                    self.assertEqual(record({**args,FIELD:value}),true)

    def test_preexisting_preparation_engine_timing_and_relic_errors_take_priority(self):
        for options in ({'elite':0,'skill':2,'skill_rank':1}, {'elite':1,'skill_rank':10},
                        {'skill':0},{'skill_rank':True},{'module_id':MOD,'module_level':0},
                        {'level':91},{'enemy_defense':-1},{'enemy_resistance':101},
                        {'timing':{'target_windows':[[10,0]]}},
                        {'effects':[{'kind':'unsupported','value':1}]},
                        {'target_enemy':{'stage_id':'missing','enemy_id':'missing','level':0}},
                        {'window_seconds':-1}):
            args=scenario(**options)
            expected=error({**args,FIELD:False})
            self.assertNotEqual(expected,('ValueError',ERROR))
            self.assertEqual(error({**args,FIELD:'false'}),expected)

    def test_selected_text_is_rejected_even_without_current_damage(self):
        for skill in (1,2,3):
            for options in ({'window_seconds':0},{'base_attack':0},
                            {'timing':{'target_disappears_seconds':0}},
                            {'timing':{'target_windows':[]}}):
                self.assert_text_error(scenario(skill,**options,**{FIELD:'false'}))

    def test_double_charge_scope_defaults_and_unbound_clock_are_preserved(self):
        args=scenario(**{FIELD:False})
        default=record(args)
        self.assertEqual(record({**args,'double_charge':True}),default)
        self.assertEqual(record({**args,'double_charge':'false'}),default)
        one=calculate_damage({**args,'double_charge':False})
        self.assertFalse(any(c['name']=='刚连射' for c in one['components']))
        self.assertTrue(any(c['name']=='刚连射' for c in default[0]['components']))
        for skill in (2,3):
            args=scenario(skill,**{FIELD:False})
            expected=record(args)
            self.assertEqual(record({**args,'double_charge':'false'}),expected)
        ref=default[0]['orchid_redeploy_reference']
        self.assertFalse(ref['events_scheduled'])
        self.assertIsNone(ref['actual_next_deployment_seconds'])

    def test_caller_cached_catalog_and_returned_result_are_isolated(self):
        cached=deepcopy(catalog())
        args=scenario(3,timing={'target_windows':[[0,10]]},**{FIELD:'false'})
        self.assert_text_error(args)
        good={**args,FIELD:True};before=deepcopy(good)
        original=record(good);expected=deepcopy(original)
        original[0]['estimate']['base_stats']['attack']=-1
        self.assertEqual(record(good),expected)
        self.assertEqual(good,before)
        self.assertEqual(catalog(),cached)


if __name__=='__main__':unittest.main()
