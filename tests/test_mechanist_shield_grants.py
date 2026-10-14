import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge.barrier_blackboard import (blackboard_storage_reference, shield_product_reference,
    float32_number_raw, ONE, MAX_RAW, SOURCE, SOURCE_SHA256)
from rouge.mechanist_shield_grants import mechanist_shield_grants, public_snapshots
from rouge.mechanist_barrier_ledger import mechanist_barrier_ledger, public_example


class BlackboardPrecisionTests(unittest.TestCase):
    def test_float_parameter_and_floor_multiplication_literals(self):
        ratio=float32_number_raw(0x3dcccccd)
        self.assertEqual(ratio,429496736)
        for hp,rate,product,readback in ((1,ONE//2,0,0),(3,ONE//2,1,1),
                (1000*ONE,ratio,429496736000,429496729600),
                (3001*ONE,ratio,1288919704736,1288919711744)):
            with self.subTest(hp=hp):
                r=shield_product_reference(hp,rate,'nearest_even')
                self.assertEqual((r['product_raw'],r['shield_readback_raw']),(product,readback))

    def test_direct_int64_to_single_avoids_double_rounding(self):
        raw=(1<<60)+(1<<36)+1
        expected={'nearest_even':1152921642045800448,'toward_zero':1152921504606846976,
            'toward_positive':1152921642045800448,'toward_negative':1152921504606846976}
        for mode,value in expected.items():
            self.assertEqual(blackboard_storage_reference(raw,mode)['readback_raw'],value)
        even_tie=1<<60 | 1<<36
        self.assertEqual(blackboard_storage_reference(even_tie,'nearest_even')['readback_raw'],1<<60)
        odd_tie=(1<<60)+(1<<37)+(1<<36)
        self.assertEqual(blackboard_storage_reference(odd_tie,'nearest_even')['readback_raw'],(1<<60)+(1<<38))

    def test_safe_roundtrip_boundary_is_not_clamped(self):
        last=9223371761976868863
        self.assertEqual(blackboard_storage_reference(last,'nearest_even')['readback_raw'],9223371487098961920)
        overflow=blackboard_storage_reference(last+1,'nearest_even')
        self.assertIsNone(overflow['readback_raw']);self.assertEqual(overflow['status'],'unqualified_signed64_overflow')
        self.assertIsNone(shield_product_reference(MAX_RAW,2*ONE,'nearest_even')['product_raw'])
        self.assertEqual(blackboard_storage_reference(MAX_RAW,'toward_zero')['readback_raw'],9223371487098961920)

    def test_unknown_rounding_and_source_remain_unknown(self):
        self.assertIsNone(blackboard_storage_reference(100*ONE,None)['readback_raw'])
        with patch('rouge.barrier_blackboard.source_valid',return_value=False):
            self.assertIsNone(shield_product_reference(1000*ONE,ONE,'nearest_even')['product_raw'])
        for value in (-1,True,1.5):
            with self.assertRaises(ValueError):blackboard_storage_reference(value,'nearest_even')
        for bits in (True,-1,0x7f800000,0x7fc00000,0xbf800000):
            with self.assertRaises(ValueError):float32_number_raw(bits)
        self.assertEqual(float32_number_raw(0),0)
        self.assertIsNone(float32_number_raw(0x4f000000))

    def test_section266_counterexample_uses_stored_readback(self):
        p=public_example();p['packets']=p['packets'][:2]
        p['packets'][0]['value_raw']=42950
        p['packets'][1]['value_raw']=429496643701;p['packets'][1]['following_barrier']=None
        r=mechanist_barrier_ledger(p)
        self.assertEqual(r['rows'][0]['barrier_after_subtraction_raw'],429496686650)
        self.assertEqual(r['rows'][0]['barrier_after_block_raw'],429496696832)
        self.assertEqual(r['rows'][1]['barrier_before_raw'],429496696832)
        self.assertEqual(r['rows'][1]['barrier_after_block_raw'],53131)
        self.assertFalse(r['rows'][1]['depletion_gate'])
        self.assertEqual(r['ammunition_consumed_reference'],0)
        self.assertFalse(r['rows'][1]['replenishment_requested'])

    def test_legacy_ledger_missing_rounding_does_not_default_it(self):
        p=public_example();del p['float_rounding']
        r=mechanist_barrier_ledger(p)
        self.assertEqual(r['rows'][0]['absorbed_raw'],40*ONE)
        self.assertIsNone(r['rows'][0]['barrier_after_block_raw'])
        self.assertIsNone(r['rows'][0]['depletion_gate'])
        p['initial_barriers']['owner']['cancel_all_raw']=ONE
        self.assertFalse(mechanist_barrier_ledger(p)['rows'][0]['depletion_gate'])

    def test_callback_changes_and_cancel_all_unknown_have_distinct_dependencies(self):
        p=public_example();p['packets']=p['packets'][:1]
        p['packets'][0]['no_intervening_barrier_changes']=False
        r=mechanist_barrier_ledger(p)['rows'][0]
        self.assertEqual(r['barrier_storage_reference']['readback_raw'],60*ONE)
        self.assertIsNone(r['barrier_after_block_raw']);self.assertIsNone(r['depletion_gate'])
        self.assertIsNone(r['following_barrier_state']['dynamic_raw'])
        self.assertIsNone(r['ammunition_remaining_reference'])
        p['packets'][0]['no_intervening_barrier_changes']=True
        p['initial_barriers']['owner']['cancel_all_raw']=None
        r=mechanist_barrier_ledger(p)['rows'][0]
        self.assertFalse(r['depletion_gate']);self.assertIsNone(r['overflow_cancel_requested'])
        self.assertFalse(r['explosion_requested']);self.assertEqual(r['ammunition_consumed_reference'],0)
        self.assertEqual(r['following_barrier_state']['dynamic_raw'],60*ONE)

    def test_source_and_ten_current_native_bodies_bound(self):
        root=Path(__file__).resolve().parents[1];raw=(root/SOURCE).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),SOURCE_SHA256)
        source=json.loads(raw);proof=(root/source['native_proof']).read_bytes()
        self.assertEqual(hashlib.sha256(proof).hexdigest(),source['native_proof_sha256'])
        p=json.loads(proof);self.assertEqual(len(p['methods']),10);self.assertEqual(p['unique_instruction_count'],533)
        self.assertFalse(p['game_dll_executed']);self.assertFalse(p['process_memory_read'])


class ShieldGrantTests(unittest.TestCase):
    def test_all_skill_ranks_use_recipient_hp_and_preserve_inputs(self):
        snapshots=public_snapshots();before=copy.deepcopy(snapshots)
        for rank in range(1,11):
            r=mechanist_shield_grants({'operator':'mechanist','skill':2,'skill_rank':rank},snapshots,True,'nearest_even')
            self.assertEqual(r['rows'][0]['max_hp_snapshot_raw_reference'],3631*ONE)
            self.assertEqual(r['rows'][0]['shield_readback_raw_reference'],1559502651392)
            self.assertEqual(r['rows'][1]['shield_readback_raw_reference'],1288919711744)
            self.assertIsNone(r['actual_initial_shield'])
        self.assertEqual(snapshots,before)

    def test_cultivation_relic_subtotal_and_independent_token_snapshot(self):
        s={'operator':'mechanist','skill':2,'level':90,'relic_ids':['rogue_6_relic_legacy_27']}
        r=mechanist_shield_grants(s,public_snapshots(),True,'nearest_even')
        self.assertEqual(r['rows'][0]['model_hp_known_subtotal'],3740)
        self.assertEqual(r['rows'][0]['shield_readback_raw_reference'],374*ONE)
        self.assertEqual(r['rows'][1]['max_hp_snapshot_raw_reference'],3001*ONE)
        self.assertIsNone(r['rows'][0]['actual_initial_shield'])
        s['level']=60;r=mechanist_shield_grants(s,public_snapshots(),True,'nearest_even')
        self.assertEqual(r['rows'][0]['model_hp_known_subtotal'],3387)
        self.assertEqual(r['rows'][1]['max_hp_snapshot_raw_reference'],3001*ONE)

    def test_lookup_failure_default_one_zero_and_unknown_are_distinct(self):
        snapshots=public_snapshots();x=snapshots[1]
        x['ratio_numeric_readable']=False
        r=mechanist_shield_grants({'operator':'mechanist','skill':2},snapshots,True,'nearest_even')['rows'][1]
        self.assertTrue(r['default_one_used_reference']);self.assertEqual(r['shield_readback_raw_reference'],3001*ONE)
        x.update(ratio_numeric_readable=True,ratio_basis='independent_float32_bits',ratio_float32_bits=0)
        r=mechanist_shield_grants({'operator':'mechanist','skill':2},snapshots,True,'nearest_even')['rows'][1]
        self.assertFalse(r['default_one_used_reference']);self.assertEqual(r['shield_readback_raw_reference'],0)
        x['ratio_numeric_readable']=None
        r=mechanist_shield_grants({'operator':'mechanist','skill':2},snapshots,True,'nearest_even')['rows'][1]
        self.assertIsNone(r['shield_readback_raw_reference'])
        self.assertIsNone(r['default_one_used_reference'])
        x['blackboard_available']=None
        self.assertIsNone(mechanist_shield_grants({'operator':'mechanist','skill':2},snapshots,True,'nearest_even')['rows'][1]['default_one_used_reference'])

    def test_missing_node_qualifiers_and_unknown_snapshot_do_not_assign_zero(self):
        for field in ('blackboard_available','target_attributes_available'):
            snapshots=public_snapshots();snapshots[1][field]=False
            r=mechanist_shield_grants({'operator':'mechanist','skill':2},snapshots,True,'nearest_even')['rows'][1]
            self.assertFalse(r['initialization_gate']);self.assertIsNone(r['shield_readback_raw_reference'])
        snapshots=public_snapshots();snapshots[1]['max_hp_raw']=None
        self.assertIsNone(mechanist_shield_grants({'operator':'mechanist','skill':2},snapshots,True,'nearest_even')['rows'][1]['shield_readback_raw_reference'])
        for ordinary in (False,None):
            r=mechanist_shield_grants({'operator':'mechanist','skill':2},public_snapshots(),ordinary,'nearest_even')
            self.assertIsNone(r['rows'][0]['numeric_reference'])

    def test_unsupported_operator_model_borrowing_and_overrides_rejected(self):
        for s in ({'operator':'kaltsit','skill':2},{'operator':'mechanist','skill':1},
                {'operator':'mechanist','skill':2,'base_attack':900}):
            with self.assertRaises(ValueError):mechanist_shield_grants(s,public_snapshots(),True,'nearest_even')
        snapshots=public_snapshots();snapshots[1].update(basis='owner_model_known_subtotal',max_hp_raw=None)
        with self.assertRaises(ValueError):mechanist_shield_grants({'operator':'mechanist','skill':2},snapshots,True,'nearest_even')


class ShieldGrantViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app=QApplication.instance() or QApplication([])

    def test_query_render_import_and_refresh_preserve_declarations(self):
        from rouge.offline_tools_view import OfflineToolsPanel,public_payload,run_offline_query,render_offline_result
        p=OfflineToolsPanel();p.select_query('calibration','shield-grants')
        data=run_offline_query('calibration','shield-grants',public_payload('calibration','shield-grants'))
        html=render_offline_result('calibration','shield-grants',data)
        self.assertIn('创建节点数值参考',html);self.assertIn('单精度写回与资格',html)
        self.assertNotIn('shield_readback_raw',html)
        original=json.loads(p.editor.toPlainText())['snapshots']
        p.set_scenario({'operator':'mechanist','skill':2,'level':60})
        p.import_scenario.click();modified=json.loads(p.editor.toPlainText())
        self.assertEqual(modified['scenario']['level'],60);self.assertEqual(modified['snapshots'],original)
        editor=p.editor.toPlainText();p.set_scenario({'operator':'kaltsit','skill':1})
        self.assertEqual(editor,p.editor.toPlainText());p.close()


if __name__=='__main__':unittest.main()
