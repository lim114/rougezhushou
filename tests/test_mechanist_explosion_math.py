import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge.mechanist_explosion_math import (mechanist_explosion_reference,public_example,magical_damage_reference,
    final_attack_reference,multiply,ONE,MIN_RAW,MAX_RAW,SOURCE,SOURCE_SHA256)
from rouge.mechanist_barrier_ledger import mechanist_barrier_ledger,public_example as barrier_example


def info(atk=1000*ONE,scale=2*ONE,addition=0,kind='MAGICAL'):
    return {'damage_type':kind,'atk_raw':atk,'atk_scale_raw':scale,'atk_addition_raw':addition}


def ledger():
    p=barrier_example();p['packets']=[p['packets'][2]];p['packets'][0]['explosion_math']=public_example();return p


class ExplosionMathTests(unittest.TestCase):
    def test_rank_ten_two_branches_exact_reference_and_unknown_late_source(self):
        p=public_example();before=copy.deepcopy(p);r=mechanist_explosion_reference(p)
        self.assertEqual(p,before);self.assertEqual(r['scale_raw_reference'],2*ONE)
        self.assertEqual(r['rows'][0]['branches']['scaled']['calculate_damage_raw_reference'],6012954080000)
        self.assertEqual(r['rows'][0]['branches']['baseline']['calculate_damage_raw_reference'],3006477040000)
        self.assertEqual(r['rows'][0]['branches']['scaled']['numeric_reference']['minimum_damage_raw_reference'],429496736000)
        self.assertIsNone(r['rows'][0]['origin_atk_raw_reference'])
        self.assertIsNone(r['actual_total_damage']);self.assertIsNone(r['rows'][0]['actual_modifier_value'])
        self.assertIsNone(r['rows'][0]['actual_hp_loss']);self.assertFalse(r['events_scheduled'])
        vector=magical_damage_reference(info(scale=5*ONE//2),30*ONE,0,0)
        self.assertEqual(vector['calculate_damage_raw_reference'],7516192600000)
        self.assertNotEqual(vector['calculate_damage_raw_reference'],1750*ONE)

    def test_signed_multiply_floor_and_wrap_against_literal_machine_vectors(self):
        for a,b,expected in ((-1,ONE//2,-1),(-3,ONE//2,-2),(MAX_RAW,2*ONE,-2),
                (MIN_RAW,-ONE,MIN_RAW),(1,ONE//2,0),(3,ONE//2,1)):
            self.assertEqual(multiply(a,b),expected)
        for a in (MIN_RAW,MIN_RAW+1,-ONE-1,-3,0,3,ONE,MAX_RAW):
            for b in (MIN_RAW,-ONE,-3,ONE//2,ONE,MAX_RAW):
                # Independent signed-high/unsigned-low limb form from the
                # actual fourteen-instruction method, not the full product.
                higha,highb=a>>32,b>>32;lowa,lowb=a&0xffffffff,b&0xffffffff
                expected=((b*higha+highb*lowa+(lowa*lowb>>32))+(1<<63))%(1<<64)-(1<<63)
                self.assertEqual(multiply(a,b),expected)

    def test_epsilon_addition_gate_and_final_attack_clamp(self):
        for scale,used,final in ((42950,0,42950000),(42951,ONE,ONE+42951000),(0,0,0)):
            r=final_attack_reference(info(scale=scale,addition=ONE))
            self.assertEqual(r['used_addition_raw_reference'],used);self.assertEqual(r['final_atk_raw_reference'],final)
        self.assertEqual(final_attack_reference(info(atk=-ONE))['final_atk_raw_reference'],0)
        self.assertEqual(final_attack_reference(info(atk=MAX_RAW))['final_atk_raw_reference'],0)
        r=final_attack_reference(info(scale=0,addition=None))
        self.assertEqual(r['final_atk_raw_reference'],0)
        self.assertIsNone(final_attack_reference(info(scale=None))['final_atk_raw_reference'])

    def test_resistance_fixed_then_ratio_order_and_ratio_already_fractional(self):
        r=magical_damage_reference(info(),50*ONE,ONE//2,10*ONE)
        self.assertEqual(r['res_after_fixed_raw_reference'],40*ONE)
        self.assertEqual(r['effective_res_raw_reference'],20*ONE)
        self.assertEqual(r['remaining_percent_raw_reference'],80*ONE)
        self.assertEqual(r['calculate_damage_raw_reference'],6871947520000)
        r=magical_damage_reference(info(),30*ONE,0,40*ONE)
        self.assertEqual(r['effective_res_raw_reference'],0)
        self.assertEqual(r['calculate_damage_raw_reference'],8589934400000)
        r=magical_damage_reference(info(),30*ONE,3*ONE//2,0)
        self.assertEqual(r['effective_res_raw_reference'],-15*ONE)
        self.assertEqual(r['remaining_percent_raw_reference'],115*ONE)

    def test_magic_minimum_floor_and_unknown_resistance_not_replaced_by_zero(self):
        for resistance in (95*ONE,100*ONE,200*ONE):
            r=magical_damage_reference(info(),resistance,0,0)
            self.assertEqual(r['calculate_damage_raw_reference'],429496736000)
        r=magical_damage_reference(info(),None,0,0)
        self.assertIsNone(r['calculate_damage_raw_reference'])
        self.assertEqual(r['minimum_damage_raw_reference'],429496736000)
        self.assertIsNone(magical_damage_reference(info(kind='PHYSICAL'),30*ONE,0,0)['calculate_damage_raw_reference'])

    def test_two_attack_and_target_reads_remain_independent_and_baseline_has_no_penetration(self):
        p=public_example();c=p['calls'][0];c['baseline_atk_raw']=2000*ONE
        c['baseline']['magic_res_raw']=20*ONE;c['first']['penetrate_ratio_raw']=ONE//2
        r=mechanist_explosion_reference(p)['rows'][0]
        self.assertEqual(r['branches']['baseline']['prepared_attack_info']['atk_raw'],2000*ONE)
        self.assertEqual(r['branches']['baseline']['numeric_reference']['effective_res_raw_reference'],20*ONE)
        self.assertEqual(r['branches']['scaled']['numeric_reference']['effective_res_raw_reference'],15*ONE)
        self.assertEqual(r['branches']['baseline']['penetrate_ratio_raw_reference'],0)
        self.assertTrue(r['branches']['baseline']['target_event_enabled']);self.assertFalse(r['branches']['baseline']['source_event_enabled'])
        p['calls'][0]['baseline']['penetrate_ratio_raw']=ONE
        with self.assertRaises(ValueError):mechanist_explosion_reference(p)

    def test_pre_event_unknown_does_not_replace_post_event_or_late_snapshots(self):
        p=public_example();c=p['calls'][0];c['first']['info_unchanged']=None
        r=mechanist_explosion_reference(p)['rows'][0]
        self.assertIsNone(r['branches']['scaled']['calculate_damage_raw_reference'])
        self.assertEqual(r['branches']['baseline']['calculate_damage_raw_reference'],3006477040000)
        c['first']['post_event_info']=info(atk=900*ONE,scale=3*ONE)
        r=mechanist_explosion_reference(p)['rows'][0]
        self.assertEqual(r['branches']['scaled']['numeric_reference']['final_atk_raw_reference'],2700*ONE)
        self.assertIsNone(r['origin_atk_raw_reference'])
        c['late_origin_info']=info(atk=800*ONE,scale=3*ONE)
        r=mechanist_explosion_reference(p)['rows'][0];self.assertEqual(r['origin_atk_raw_reference'],2400*ONE)
        c['late_origin_info']=None;c['late_first_info_unchanged']=True
        self.assertEqual(mechanist_explosion_reference(p)['rows'][0]['origin_atk_raw_reference'],2700*ONE)

    def test_numeric_failed_scale_default_one_success_zero_and_unknown(self):
        p=public_example();p['scale_number_readable']=False;r=mechanist_explosion_reference(p)
        self.assertTrue(r['default_one_used_reference']);self.assertEqual(r['scale_raw_reference'],ONE)
        self.assertEqual(r['rows'][0]['branches']['scaled']['calculate_damage_raw_reference'],3006477040000)
        p.update(scale_basis='independent_blackboard_number',scale_number_readable=True,scale_float32_bits=0)
        r=mechanist_explosion_reference(p);self.assertFalse(r['default_one_used_reference'])
        self.assertEqual(r['rows'][0]['branches']['scaled']['calculate_damage_raw_reference'],0)
        p['scale_number_readable']=None;r=mechanist_explosion_reference(p)
        self.assertIsNone(r['default_one_used_reference']);self.assertIsNone(r['scale_raw_reference'])
        self.assertIsNone(r['rows'][0]['branches']['scaled']['calculate_damage_raw_reference'])

    def test_radius_zero_failure_and_unknown_never_borrow_nominal_radius(self):
        p=public_example();p['radius_number_readable']=False
        self.assertEqual(mechanist_explosion_reference(p)['radius_float32_reference'],0.0)
        p.update(radius_number_readable=True,radius_float32_bits=0)
        self.assertEqual(mechanist_explosion_reference(p)['radius_float32_reference'],0.0)
        p['radius_number_readable']=None
        self.assertIsNone(mechanist_explosion_reference(p)['radius_float32_reference'])
        p.update(radius_number_readable=True,radius_float32_bits=0x7fc00000)
        self.assertIsNone(mechanist_explosion_reference(p)['radius_float32_reference'])

    def test_missing_or_unqualified_context_no_numeric_call_or_complete_total(self):
        for field in ('ordinary_native_path','blackboard_available'):
            for v in (False,None):
                p=public_example();p[field]=v;r=mechanist_explosion_reference(p)
                self.assertIsNone(r['rows'][0]['branches']['scaled']['numeric_reference'])
                self.assertIsNone(r['declared_calls_scaled_damage_raw_total'])
        for field in ('target_enumerated','source_attributes_available'):
            p=public_example();p['calls'][0][field]=None
            self.assertIsNone(mechanist_explosion_reference(p)['declared_calls_scaled_damage_raw_total'])
        with patch('rouge.mechanist_explosion_math.source_valid',return_value=False):
            r=mechanist_explosion_reference(public_example())
            self.assertFalse(r['source_valid']);self.assertIsNone(r['declared_calls_scaled_damage_raw_total'])
            self.assertIsNone(final_attack_reference(info())['final_atk_raw_reference'])

    def test_all_ten_skill_parameters_and_partial_calls_keep_total_unknown(self):
        from rouge.catalog import catalog
        for rank,level in enumerate(catalog()['operators']['mechanist']['skills'][1]['levels'],1):
            p=public_example();p['skill_rank']=rank;r=mechanist_explosion_reference(p)
            self.assertEqual(r['nominal_atk_scale'],level['values']['atk_scale'])
            self.assertIsNotNone(r['declared_calls_scaled_damage_raw_total'])
        p=public_example();p['calls'].append(copy.deepcopy(p['calls'][0]));p['calls'][-1]['id']='未知目标输入'
        p['calls'][-1]['first']['info_unchanged']=None;r=mechanist_explosion_reference(p)
        self.assertEqual(r['known_scaled_damage_raw_subtotal'],6012954080000)
        self.assertIsNone(r['declared_calls_scaled_damage_raw_total'])

    def test_ledger_only_includes_math_after_definite_explosion_request(self):
        p=ledger();before=copy.deepcopy(p);r=mechanist_barrier_ledger(p)
        self.assertEqual(p,before);self.assertEqual(r['rows'][0]['declared_explosion_base_raw_reference'],6012954080000)
        self.assertEqual(r['declared_explosion_base_raw_total'],6012954080000)
        self.assertIsNone(r['actual_total_damage']);self.assertIsNone(r['rows'][0]['actual_explosion_hits'])
        p['packets'][0]['main_buff_for_explosion']=False;r=mechanist_barrier_ledger(p)
        self.assertIsNone(r['rows'][0]['explosion_fp_reference']);self.assertEqual(r['declared_explosion_base_raw_total'],0)
        p['packets'][0]['main_buff_for_explosion']=None
        self.assertIsNone(mechanist_barrier_ledger(p)['declared_explosion_base_raw_total'])
        p['packets'][0]['main_buff_for_explosion']=True;p['packets'][0]['no_intervening_barrier_changes']=False
        self.assertIsNone(mechanist_barrier_ledger(p)['rows'][0]['explosion_fp_reference'])

    def test_schema_rejects_context_conflicts_duplicates_and_inappropriate_overrides(self):
        bad=[]
        for k,v in (('operator','kaltsit'),('skill',1),('skill_rank',True),('blackboard_available',1)):
            p=public_example();p[k]=v;bad.append(p)
        p=public_example();p['calls'].append(copy.deepcopy(p['calls'][0]));bad.append(p)
        p=public_example();p['scale_float32_bits']=0;bad.append(p)
        p=public_example();p['calls'][0]['first']['post_event_info']=info();bad.append(p)
        p=public_example();p['calls'][0]['late_first_info_unchanged']=True;p['calls'][0]['late_origin_info']=info();bad.append(p)
        for v in (True,1.1,MAX_RAW+1,MIN_RAW-1):
            p=public_example();p['calls'][0]['first_atk_raw']=v;bad.append(p)
        for p in bad:
            with self.assertRaises(ValueError):mechanist_explosion_reference(p)
        p=ledger();p['packets'][0]['explosion_math']['skill_rank']=1
        with self.assertRaises(ValueError):mechanist_barrier_ledger(p)

    def test_source_binding_twentynine_methods_and_raw_bytes(self):
        root=Path(__file__).resolve().parents[1];raw=(root/SOURCE).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),SOURCE_SHA256)
        source=json.loads(raw);proofraw=(root/source['native_proof']).read_bytes()
        self.assertEqual(hashlib.sha256(proofraw).hexdigest(),source['native_proof_sha256'])
        self.assertEqual(hashlib.sha256((root/source['template_evidence']).read_bytes()).hexdigest(),source['template_evidence_sha256'])
        proof=json.loads(proofraw);self.assertEqual(len(proof['methods']),29)
        self.assertEqual(proof['unique_instruction_count'],3172);self.assertTrue(proof['all_instruction_bytes_rechecked'])
        self.assertFalse(proof['game_dll_executed']);self.assertFalse(proof['process_memory_read'])
        self.assertTrue(all(m['cfg_bounded_traversal_finished'] and not m['limits'] for m in proof['methods']))


class ExplosionViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app=QApplication.instance() or QApplication([])

    def test_chinese_dual_branch_query_and_refresh_preserve_independent_inputs(self):
        from rouge.offline_tools_view import OfflineToolsPanel,public_payload,run_offline_query,render_offline_result
        panel=OfflineToolsPanel();panel.select_query('calibration','explosion-values')
        p=public_payload('calibration','explosion-values');r=run_offline_query('calibration','explosion-values',p)
        html=render_offline_result('calibration','explosion-values',r)
        self.assertIn('两次计算分列',html);self.assertIn('ONE基准分支',html);self.assertIn('≈1399.99996871',html)
        self.assertNotIn('calculate_damage_raw_reference',html)
        before=(panel.editor.toPlainText(),panel.current_query())
        panel.set_scenario({'operator':'kaltsit','skill':1})
        self.assertEqual(before,(panel.editor.toPlainText(),panel.current_query()))
        self.assertFalse(panel.import_scenario.isEnabled())
        r=mechanist_barrier_ledger(ledger());html=render_offline_result('calibration','barrier-ledger',r)
        self.assertIn('已请求爆炸的独立数值',html);panel.close()


if __name__=='__main__':unittest.main()
