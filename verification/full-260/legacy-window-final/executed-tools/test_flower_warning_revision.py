"""Independent probes for the explicit current warning-contract revision."""
import ast
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from rouge.damage import calculate_damage
from rouge.reporting import format_report
from rouge.relic_healing_factors import healing_factor,regeneration_factor

BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_explicit_current_flower_guard',BASE/'flower-warning-current.py')
guard_module=importlib.util.module_from_spec(spec)
guard_module.ROOT=ROOT
spec.loader.exec_module(guard_module)
guard=guard_module.require_warning_order085

def original_cases81():
    source=(BASE/'full260-reset-window-attempt2-bundle/window.py').read_text()
    tree=ast.parse(source)
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='cases085')
    # Only the separately probed section81 family is requested here. The full
    # revised window retains the complete original pending-family generator.
    namespace={'pending_cases083085':lambda:[]}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<original cases085>','exec'),namespace)
    return [case for case in namespace['cases085']() if case['section']==81]

def pair_result():
    args=deepcopy(original_cases81()[2]['input'])
    return args,calculate_damage(args)

class FlowerWarningRevisionTests(unittest.TestCase):
    def test_all136_original_section81_cases_actual_results_and_text(self):
        cases=original_cases81()
        self.assertEqual(len(cases),136)
        for index,case in enumerate(cases):
            with self.subTest(index=index,operator=case['input']['operator'],relics=case['input']['relic_ids']):
                args=deepcopy(case['input']);result=calculate_damage(args)
                before=deepcopy((args,result))
                guard(result,args,format_report(result,technical=case['technical']),case['technical'])
                self.assertEqual((args,result),before)

    def test_pair_forged_native_composition_provenance_is_rejected(self):
        args,result=pair_result()
        mutations=(('relic_id','unknown'),('source_buff_key','char_attribute_mul'),
            ('source_buff_index',9),('source_buff_index',True),('value',1.1),
            ('composition_evidence','unknown'),('stacking','unverified'),('_verified_rule',False))
        for field,value in mutations:
            with self.subTest(field=field,value=value):
                bad=deepcopy(result)
                rule=next(r for r in bad['relic_resolution']['rules']
                    if r['relic_id']=='rogue_6_relic_legacy_82' and r['kind']=='healing_factor')
                rule[field]=value
                with self.assertRaises(AssertionError):guard(bad,args,'',False)

    def test_external_composition_and_false_native_execution_claims_rejected(self):
        args,result=pair_result()
        for kind in ('healing_factor','regeneration_factor'):
            rules=deepcopy([r for r in result['relic_resolution']['rules'] if r['kind']==kind])
            target=next(r for r in rules if r['relic_id']=='rogue_6_relic_legacy_82')
            target['relic_id']='foreign_source'
            function=healing_factor if kind=='healing_factor' else regeneration_factor
            self.assertIsNone(function(rules))
            bad=deepcopy(result);bad['relic_resolution']['rules'].extend(rules)
            with self.assertRaises(AssertionError):guard(bad,args,'',False)
        for field in ('actual_buff_attachment_verified','actual_ticks_verified'):
            bad=deepcopy(result);bad['relic_resolution'][field]=True
            with self.assertRaises(AssertionError):guard(bad,args,'',False)
        bad=deepcopy(result);bad['relic_resolution']['combat_effects_reference_only']=False
        with self.assertRaises(AssertionError):guard(bad,args,'',False)
        bad=deepcopy(result);bad['relic_resolution']['records'].reverse()
        with self.assertRaises(AssertionError):guard(bad,args,'',False)

    def test_source_receipt_tamper_rejected(self):
        args,result=pair_result()
        original=Path.read_bytes
        target=ROOT/'research/p2-flower-healing-composition-current/receipt.json'
        def modified(path):
            raw=original(path)
            return raw+b' ' if path==target else raw
        with patch.object(Path,'read_bytes',modified):
            with self.assertRaises(AssertionError):guard(result,args,'',False)

    def test_actual_healing_consumption_and_zero_gate_keep_other_sources(self):
        flower_ids={'rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83'}
        oracles={():1.,('rogue_6_relic_legacy_81',):1.2,
            ('rogue_6_relic_legacy_81','rogue_6_relic_legacy_82'):1.56,
            ('rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83'):2.184}
        for case in original_cases81():
            if case['technical']:continue
            args=deepcopy(case['input']);result=calculate_damage(args)
            plain_args=deepcopy(args)
            plain_args['relic_ids']=[rid for rid in args['relic_ids'] if rid not in flower_ids]
            plain=calculate_damage(plain_args)
            factor=oracles[tuple(rid for rid in args['relic_ids'] if rid in flower_ids)]
            self.assertEqual(result['total_damage'],plain['total_damage'])
            for actual,base,keys in ((result,plain,('total_healing',)),
                    (result['estimate']['skill'],plain['estimate']['skill'],
                     ('total_healing','phase_healing','window_healing','cycle_healing','cycle_hps','window_hps'))):
                for key in keys:
                    if key not in base:self.assertNotIn(key,actual)
                    elif base[key] is None:self.assertIsNone(actual.get(key))
                    else:self.assertAlmostEqual(actual[key],base[key]*factor,places=8)
            if args['window_seconds']==0:
                bad=deepcopy(result);bad['total_damage']=1
                with self.assertRaises(AssertionError):guard(bad,args,'',case['technical'])

if __name__=='__main__':unittest.main()
