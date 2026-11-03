from copy import deepcopy
from pathlib import Path
import json
import sys
import unittest
sys.dont_write_bytecode = True
sys.path.insert(0,str(Path(sys.argv.pop(1)).resolve()))
from rouge.catalog import catalog, operator_attributes
from rouge.damage import calculate_damage
from rouge.operator_engine import Combat
from rouge.operator_options import OPTIONS
from rouge.relics import mechanics
from rouge.reporting import format_report

OP = 'char_2025_shu'
FIELD = 'enemy_on_sown_tile'
ERROR = 'enemy_on_sown_tile 不接受文本条件；请使用布尔值。'


def strict(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)


def calculate(value=False,**extra):
    return calculate_damage({'operator':OP,'skill':3,'elite':2,'base_attack':1000,
                             'window_seconds':10,FIELD:value,**extra})


def outcome(value,**extra):
    try:
        return {'accepted':True,'result':calculate(value,**extra)}
    except Exception as exc:
        return {'accepted':False,'error_type':type(exc).__name__,'error':str(exc)}


class IndependentEnemySownTileTests(unittest.TestCase):
    def test_active_text_is_exact_error_at_all_ranks_and_real_modes(self):
        for mode in ('frames','continuous'):
            for rank in range(1,11):
                for raw in ('false','true','False','0','1','',' ','off','null'):
                    with self.subTest(mode=mode,rank=rank,raw=raw):
                        self.assertEqual(outcome(raw,timing_mode=mode,skill_rank=rank),
                            {'accepted':False,'error_type':'ValueError','error':ERROR})

    def test_nontext_inputs_keep_complete_original_truthiness_contract(self):
        for mode in ('frames','continuous'):
            for raw in (False,True,0,1,None,0.0,1.0,{},[],[0],{'declared':False}):
                with self.subTest(mode=mode,raw=raw):
                    a=calculate(raw,timing_mode=mode);b=calculate(bool(raw),timing_mode=mode)
                    self.assertEqual(strict(a),strict(b))
                    self.assertEqual(format_report(a),format_report(b))

    def test_skill_qualification_and_other_earlier_errors_keep_priority(self):
        for elite in (0,1):
            for rank in (1,7,10):
                self.assertEqual(outcome('false',elite=elite,skill_rank=rank),
                                 outcome(False,elite=elite,skill_rank=rank))
                self.assertFalse(outcome('false',elite=elite,skill_rank=rank)['accepted'])
        for extra in ({'skill_rank':True},{'healing_targets':True},
                      {'window_seconds':-1},{'window_seconds':'bad'}, {'four_sui':'false'}):
            with self.subTest(extra=extra):
                self.assertEqual(outcome('false',**extra),outcome(False,**extra))
                self.assertFalse(outcome(False,**extra)['accepted'])

    def test_inactive_other_skills_and_owners_keep_complete_result(self):
        for operator,skill in ((OP,1),(OP,2),('mechanist',3),('silverash',3),('char_1042_phatm2',2)):
            for mode in ('frames','continuous'):
                base={'operator':operator,'skill':skill,'base_attack':1000,
                      'timing_mode':mode,'window_seconds':10}
                expected=calculate_damage(base)
                for raw in ('false','','true',{},None):
                    with self.subTest(operator=operator,skill=skill,mode=mode,raw=raw):
                        self.assertEqual(strict(calculate_damage({**base,FIELD:raw})),strict(expected))

    def test_internal_normal_phase_does_not_query_s3_condition(self):
        attributes=operator_attributes(OP,2,60,100,1)
        for mode in ('frames','continuous'):
            base={'operator':OP,'skill':3,'elite':2,'level':60,'base_attack':1000,
                  'window_seconds':10,'timing_mode':mode}
            expected=Combat({**base,FIELD:False},deepcopy(attributes)).plan(normal=True,window=10)
            for raw in ('false','true',''):
                with self.subTest(mode=mode,raw=raw):
                    actual=Combat({**base,FIELD:raw},deepcopy(attributes)).plan(normal=True,window=10)
                    self.assertEqual(strict(actual),strict(expected))

    def test_known_skill_parameters_and_source_exact_label_are_preserved(self):
        control=next(x for x in OPTIONS[OP]if x[0]==FIELD)
        self.assertEqual(control,(FIELD,'存在地面敌人处于播种地块',False,1,(3,)))
        for rank,level in enumerate(catalog()['operators'][OP]['skills'][2]['levels'],1):
            false=calculate(False,skill_rank=rank);true=calculate(True,skill_rank=rank)
            self.assertAlmostEqual(true['attack']-false['attack'],1000*level['values']['e_atk'])
            self.assertAlmostEqual(true['attack_speed_reference']-false['attack_speed_reference'],level['values']['e_attack_speed'])

    def test_empty_window_and_target_scopes_still_query_active_text(self):
        for mode in ('frames','continuous'):
            for extra in ({'window_seconds':0},{'timing':{'target_disappears_seconds':0}},
                          {'timing':{'target_windows':[]}}):
                with self.subTest(mode=mode,extra=extra):
                    self.assertEqual(outcome('false',timing_mode=mode,**extra),
                                     {'accepted':False,'error_type':'ValueError','error':ERROR})

    def test_four_sui_clock_and_public_input_caches_remain_unbound(self):
        before_catalog,before_mechanics=deepcopy(catalog()),deepcopy(mechanics())
        for mode in ('frames','continuous'):
            for raw in (False,True,0,1,None):
                result=calculate(raw,timing_mode=mode,four_sui=True)
                self.assertIsNone(result['estimate']['skill']['recharge_seconds'])
                self.assertIsNone(result['estimate']['skill']['cycle_seconds'])
                self.assertFalse(result['timing']['resource_and_damage_shared_clock'])
                self.assertTrue(result['timing']['phase_clock_unbound'])
        for raw in ('false',False,True,None):
            scenario={'operator':OP,'skill':3,FIELD:raw};original=deepcopy(scenario)
            try:
                calculate_damage(scenario)
            except ValueError:
                pass
            self.assertEqual(strict(scenario),strict(original))
        self.assertEqual(catalog(),before_catalog);self.assertEqual(mechanics(),before_mechanics)


if __name__=='__main__':
    unittest.main()
