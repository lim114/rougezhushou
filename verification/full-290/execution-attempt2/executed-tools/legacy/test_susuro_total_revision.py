"""Original finite/unknown Susuro guard inputs and meaningful regressions."""
import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import selected_talents
from rouge.reporting import format_report
BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_explicit_susuro_unknown_guard',BASE/'susuro-total-current.py')
current=importlib.util.module_from_spec(spec);spec.loader.exec_module(current)
guard=current.require_susuro_checkbox085

def original_cases82():
    source=(BASE/'full260-flower-window-attempt3-bundle/window.py').read_text()
    node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='cases085')
    namespace={'pending_cases083085':lambda:[]}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<original cases085>','exec'),namespace)
    return [case for case in namespace['cases085']() if case['section']==82]

def factor(args):
    talents,_=selected_talents(catalog()['operators'][args['operator']],args)
    return next((t['values']['heal_scale']for t in talents if t['name']=='微创治疗'),1.)

def reference_pair(index=168,**extra):
    args=deepcopy(original_cases82()[index]['input']);args.update(extra)
    plain=calculate_damage({**args,'low_cost_healing_target':False})
    result=calculate_damage(args)
    return args,plain,result

class SusuroTotalRevisionTests(unittest.TestCase):
    def test_all216_original_cases_keep_numerics_unknowns_zero_and_cycles(self):
        cases=original_cases82();self.assertEqual(len(cases),216);anchors={}
        for index,case in enumerate(cases):
            args=deepcopy(case['input']);result=calculate_damage(args)
            key=json.dumps({k:v for k,v in args.items() if k!='low_cost_healing_target'},sort_keys=True)
            if not args['low_cost_healing_target']:anchors[key]=deepcopy(result)
            before=deepcopy((result,args,anchors[key]))
            with self.subTest(index=index,context=case['context']):
                guard(result,args,format_report(result),anchors[key],factor(args))
                self.assertEqual((result,args,anchors[key]),before)

    def test_exact_missing_ratio_boundary_keeps_known_subtotals_and_source(self):
        args,plain,result=reference_pair(168,low_cost_healing_target=True)
        self.assertIsNone(plain['total_healing']);self.assertIsNone(result['total_healing'])
        self.assertAlmostEqual(plain['known_healing_subtotals']['total_healing'],7772.4)
        for key in plain['known_healing_subtotals']:
            self.assertAlmostEqual(result['known_healing_subtotals'][key],plain['known_healing_subtotals'][key]*factor(args))
        guard(result,args,format_report(result),plain,factor(args))
        for ratio in (.4,.8):
            a,b,c=reference_pair(168,healing_target_hp_ratio=ratio,low_cost_healing_target=True)
            self.assertIsNotNone(c['total_healing'])
            guard(c,a,format_report(c),b,factor(a))

    def test_known_numeric_and_unknown_total_forgery_are_rejected(self):
        args,plain,result=reference_pair(0)
        for value in (None,result['total_healing']+1):
            bad=deepcopy(result);bad['total_healing']=value
            with self.assertRaises((AssertionError,TypeError)):guard(bad,args,'',plain,factor(args))
        args,plain,result=reference_pair(168)
        bad=deepcopy(result);bad['total_healing']=0
        with self.assertRaises(AssertionError):guard(bad,args,'',plain,factor(args))
        for key in result['known_healing_subtotals']:
            bad=deepcopy(result);bad['known_healing_subtotals'][key]+=1
            with self.assertRaises(AssertionError):guard(bad,args,'',plain,factor(args))

    def test_false_source_ratio_native_claim_and_fake_unknown_rejected(self):
        args,plain,result=reference_pair(168)
        for key,value in (('evidence','foreign'),('module_id','foreign'),('module_level',9),
                          ('res_key','foreign'),('recipient_hp_ratio',.4),('qualified',True),('factor',1.15),
                          ('compiled_path_verified',False),('current_hotfix_equivalence_proven',True),
                          ('actual_recipient_ratio_verified',True),('actual_recipient_acquisition_verified',True),
                          ('actual_hp_trajectory_verified',True)):
            bad=deepcopy(result);bad['susuro_module_healing_reference'][key]=value
            with self.subTest(key=key):
                with self.assertRaises(AssertionError):guard(bad,args,'',plain,factor(args))
        forged_args={**args,'healing_target_hp_ratio':.8}
        with self.assertRaises(AssertionError):guard(result,forged_args,'',plain,factor(args))

    def test_zero_gate_and_finite_last_use_do_not_gain_unknown_totals(self):
        for extra in ({'window_seconds':0},{'healing_targets':0}):
            args,plain,result=reference_pair(168,**extra)
            self.assertEqual(result['total_healing'],0)
            guard(result,args,format_report(result),plain,factor(args))
            bad=deepcopy(result);bad['total_healing']=1
            with self.assertRaises(AssertionError):guard(bad,args,'',plain,factor(args))
        for mode in ('frames','continuous'):
            args,plain,result=reference_pair(192,timing_mode=mode,low_cost_healing_target=True)
            self.assertEqual(args['casts_used'],1)
            self.assertGreater(result['total_healing'],0)
            self.assertIsNone(result['estimate']['skill']['cycle_healing'])
            self.assertIsNone(result['estimate']['skill']['cycle_seconds'])
            guard(result,args,format_report(result),plain,factor(args))

if __name__=='__main__':unittest.main()
