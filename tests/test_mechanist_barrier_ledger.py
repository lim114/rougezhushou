import copy
import hashlib
import itertools
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge.mechanist_barrier_ledger import (mechanist_barrier_ledger, public_example,
    ONE, EPSILON, SOURCE, SOURCE_SHA256)


def single(value, shield=100 * ONE, recipient='owner'):
    p = public_example(); p['packets'] = [p['packets'][1]]
    r = p['packets'][0]; r['recipient'] = recipient; r['value_raw'] = value
    r['following_barrier'] = None
    p['initial_barriers'][recipient]['dynamic_raw'] = shield
    return p


class BarrierLedgerTests(unittest.TestCase):
    def test_ordered_absorption_shared_counter_and_no_automatic_instance(self):
        p=public_example(); before=copy.deepcopy(p); out=mechanist_barrier_ledger(p)
        self.assertEqual(p,before)
        self.assertEqual([r['absorbed_raw'] for r in out['rows']],[40*ONE,60*ONE,100*ONE])
        self.assertEqual([r['modifier_after_block_raw'] for r in out['rows']],[0,10*ONE,10*ONE])
        self.assertEqual([r['ammunition_remaining_reference'] for r in out['rows']],[8,7,6])
        self.assertEqual(out['absorbed_raw_total'],200*ONE)
        self.assertEqual(out['final_barriers']['owner']['dynamic_raw'],100*ONE)
        self.assertIsNone(out['final_barriers']['structure']['dynamic_raw'])
        self.assertIsNone(out['actual_hp_loss']);self.assertIsNone(out['actual_total_damage'])
        self.assertFalse(out['events_scheduled'])

    def test_native_near_zero_entry_and_block_residual_boundaries(self):
        vectors=[(42949,100*ONE,0,100*ONE,42949,False),
            (42950,100*ONE,42950,429496686650,0,False),
            (ONE+42949,ONE,ONE,0,0,True),
            (ONE+42950,ONE,ONE,0,42950,True),
            (-ONE,100*ONE,0,100*ONE,0,False)]
        for value,shield,absorbed,after,modifier,depleted in vectors:
            with self.subTest(value=value,shield=shield):
                r=mechanist_barrier_ledger(single(value,shield))['rows'][0]
                self.assertEqual((r['absorbed_raw'],r['barrier_after_block_raw'],r['modifier_after_block_raw'],r['depletion_gate']),
                    (absorbed,after,modifier,depleted))

    def test_dynamic_epsilon_depletion_and_next_instance_not_invented(self):
        for remainder,expected in ((42949,True),(42950,False)):
            r=mechanist_barrier_ledger(single(ONE,ONE+remainder))['rows'][0]
            self.assertEqual(r['barrier_after_block_raw'],remainder)
            self.assertIs(r['depletion_gate'],expected)
        p=public_example();p['packets'][1]['following_barrier']=None
        p['packets'].append(copy.deepcopy(p['packets'][0]));p['packets'][-1]['id']='未知下一屏障'
        out=mechanist_barrier_ledger(p)
        self.assertIsNone(out['rows'][-1]['absorbed_raw']);self.assertIsNone(out['absorbed_raw_total'])
        self.assertEqual(out['known_absorbed_raw_subtotal'],200*ONE)

    def test_count_gate_matrix_keeps_replenishment_request_separate(self):
        for affecting,ignored,free in itertools.product((False,True),repeat=3):
            p=single(110*ONE);r=p['packets'][0]
            r.update(counting_is_affecting=affecting,counting_ignore_until_cast_end=ignored,counting_not_count_next=free)
            actual=mechanist_barrier_ledger(p)['rows'][0]
            self.assertTrue(actual['replenishment_requested'])
            self.assertEqual(actual['ammunition_consumed_reference'],int(affecting and not ignored and not free))
            self.assertIsNone(actual['actual_replenishment_created'])

    def test_missing_progress_source_does_not_block_replenishment_request(self):
        p=single(110*ONE);p['packets'][0]['progress_source_available']=False
        r=mechanist_barrier_ledger(p)['rows'][0]
        self.assertTrue(r['manual_count_requested']);self.assertTrue(r['replenishment_requested'])
        self.assertEqual(r['ammunition_consumed_reference'],0)
        p['packets'][0]['manual_count_node_success']=False
        r=mechanist_barrier_ledger(p)['rows'][0]
        self.assertTrue(r['manual_count_requested']);self.assertFalse(r['replenishment_requested'])
        self.assertEqual(r['ammunition_consumed_reference'],0);self.assertTrue(r['finish_old_barrier_requested'])

    def test_separate_main_buff_queries_and_finish_after_read(self):
        for first,second in itertools.product((False,True),repeat=2):
            p=single(110*ONE);p['packets'][0].update(main_buff_for_explosion=first,main_buff_for_replenish=second)
            r=mechanist_barrier_ledger(p)['rows'][0]
            self.assertIs(r['explosion_requested'],first);self.assertIs(r['replenishment_requested'],second)
            self.assertEqual(r['ammunition_consumed_reference'],int(second))
            self.assertTrue(r['finish_old_barrier_requested'])
        p=single(110*ONE);p['packets'][0]['ammunition_read_ok']=False
        r=mechanist_barrier_ledger(p)['rows'][0]
        self.assertTrue(r['explosion_requested']);self.assertFalse(r['finish_old_barrier_requested'])
        self.assertFalse(r['replenishment_requested'])

    def test_filtered_sources_only_control_overflow_cancel_not_break_requests(self):
        for total,expected in ((0,True),(42949,True),(42950,False),(ONE,False)):
            p=single(110*ONE,recipient='structure')
            p['packets'][0]['caster_shields']['total_raw']=total
            r=mechanist_barrier_ledger(p)['rows'][0]
            self.assertIs(r['overflow_cancel_requested'],expected)
            self.assertTrue(r['explosion_requested']);self.assertTrue(r['replenishment_requested'])
            self.assertEqual(r['modifier_after_block_raw'],10*ONE)
        p=single(110*ONE,recipient='structure');p['packets'][0]['caster_shields']={'source_available':False,'total_raw':None}
        self.assertTrue(mechanist_barrier_ledger(p)['rows'][0]['overflow_cancel_requested'])

    def test_cancel_all_outer_branch_does_not_finish_or_count(self):
        p=single(110*ONE);p['initial_barriers']['owner']['cancel_all_raw']=ONE
        r=mechanist_barrier_ledger(p)['rows'][0]
        self.assertTrue(r['overflow_cancel_requested']);self.assertFalse(r['explosion_requested'])
        self.assertFalse(r['finish_old_barrier_requested']);self.assertEqual(r['ammunition_consumed_reference'],0)

    def test_entry_filters_no_damage_or_block_bypass_do_not_absorb(self):
        for flag,value in (('is_damage',False),('cancelled',True),('ignore_blocked',True)):
            p=single(110*ONE);p['packets'][0][flag]=value
            r=mechanist_barrier_ledger(p)['rows'][0]
            self.assertEqual(r['absorbed_raw'],0);self.assertEqual(r['barrier_after_block_raw'],100*ONE)
            self.assertFalse(r['explosion_requested'])

    def test_unknown_fields_do_not_become_zero_or_complete(self):
        p=single(110*ONE);p['packets'][0]['counting_is_affecting']=None
        r=mechanist_barrier_ledger(p)['rows'][0]
        self.assertTrue(r['replenishment_requested']);self.assertIsNone(r['ammunition_consumed_reference'])
        self.assertIsNone(r['ammunition_remaining_reference'])
        p=single(110*ONE);p['packets'][0]['no_intervening_barrier_changes']=False
        r=mechanist_barrier_ledger(p)['rows'][0]
        self.assertEqual(r['absorbed_raw'],100*ONE);self.assertIsNone(r['depletion_gate'])
        for native in (None,False):
            p=single(110*ONE);p['ordinary_native_path']=native
            self.assertIsNone(mechanist_barrier_ledger(p)['absorbed_raw_total'])
        with patch('rouge.mechanist_barrier_ledger._source_valid',return_value=False):
            out=mechanist_barrier_ledger(single(110*ONE))
            self.assertIsNone(out['absorbed_raw_total']);self.assertEqual(out['known_packets'],0)

    def test_final_ammunition_still_requests_replacement_and_no_end_clock(self):
        p=single(110*ONE);p['maximum_ammunition']=1
        r=mechanist_barrier_ledger(p)['rows'][0]
        self.assertTrue(r['replenishment_requested']);self.assertEqual(r['ammunition_remaining_reference'],0)
        self.assertIsNone(r['actual_finish_seconds'])
        p['consumed_ammunition']=1;r=mechanist_barrier_ledger(p)['rows'][0]
        self.assertFalse(r['replenishment_requested']);self.assertTrue(r['explosion_requested'])
        self.assertTrue(r['finish_old_barrier_requested'])

    def test_schema_bounds_wrong_operator_and_same_owner_snapshot_rejected(self):
        for field,value in [('skill',1),('operator','kaltsit'),('maximum_ammunition',True),('skill_rank',11)]:
            p=public_example();p[field]=value
            with self.assertRaises(ValueError):mechanist_barrier_ledger(p)
        p=single(ONE);p['initial_barriers']['owner']['dynamic_raw']=-ONE
        with self.assertRaises(ValueError):mechanist_barrier_ledger(p)
        p=single(ONE);p['packets'][0]['caster_shields']['total_raw']=ONE
        with self.assertRaises(ValueError):mechanist_barrier_ledger(p)
        p=public_example();p['packets'][1]['id']=p['packets'][0]['id']
        with self.assertRaises(ValueError):mechanist_barrier_ledger(p)

    def test_source_binding_all_methods_and_native_bytes_receipt(self):
        root=Path(__file__).resolve().parents[1];raw=(root/SOURCE).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),SOURCE_SHA256)
        source=json.loads(raw);proofraw=(root/source['native_proof']).read_bytes()
        self.assertEqual(hashlib.sha256(proofraw).hexdigest(),source['native_proof_sha256'])
        proof=json.loads(proofraw);self.assertEqual(len(proof['methods']),18)
        self.assertEqual(proof['unique_instruction_count'],2211)
        self.assertFalse(proof['game_dll_executed']);self.assertFalse(proof['process_memory_read'])
        self.assertTrue(all(m['cfg_bounded_traversal_finished'] for m in proof['methods']))


class BarrierLedgerViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app=QApplication.instance() or QApplication([])

    def test_readable_query_import_gate_and_refresh_preserve_edits(self):
        from rouge.offline_tools_view import OfflineToolsPanel,run_offline_query,render_offline_result,public_payload
        panel=OfflineToolsPanel();panel.query.setCurrentIndex(panel.query.findData('barrier-ledger'))
        payload=public_payload('calibration','barrier-ledger');result=run_offline_query('calibration','barrier-ledger',payload)
        text=render_offline_result('calibration','barrier-ledger',result)
        self.assertIn('即时吸收算式',text);self.assertIn('后续请求与共享弹匣',text)
        self.assertNotIn('absorbed_raw',text);self.assertIn('实际生命损失',text)
        self.assertFalse(panel.import_scenario.isEnabled())
        editor=panel.editor.toPlainText();panel.set_scenario({'operator':'kaltsit','skill':1})
        self.assertEqual(panel.editor.toPlainText(),editor);self.assertFalse(panel.import_scenario.isEnabled())
        panel.close()


if __name__=='__main__':unittest.main()
