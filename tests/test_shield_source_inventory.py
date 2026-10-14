import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge.shield_source_inventory import (mechanist_shield_inventory, public_example,
    float32_signed_number_raw, ONE, MIN_RAW, SOURCE, SOURCE_SHA256)
from rouge.mechanist_barrier_ledger import mechanist_barrier_ledger, public_example as ledger_example


def filter_row(inventory, role='caster'):
    return mechanist_shield_inventory(inventory)['source_filters'][role]


def only_values(*raws):
    p=public_example();base=p['shields'][0];p['shields']=[]
    for i,raw in enumerate(raws):
        item=copy.deepcopy(base);item['id']='独立盾'+str(i);item['value']['raw']=raw;p['shields'].append(item)
    return p


def blackboard(bits=None, readable=True, available=True, direct=True):
    return {'kind':'blackboard_number','ordinary_direct_data_path':direct,
        'blackboard_available':available,'number_readable':readable,'float32_bits':bits}


def inventory_ledger(inventory):
    p=ledger_example();packet=p['packets'][2];packet['following_barrier']=None
    del packet['caster_shields'];del packet['recipient_shields']
    packet['source_shield_inventory']=copy.deepcopy(inventory);p['packets']=[packet]
    return p


class ShieldSourceInventoryTests(unittest.TestCase):
    def test_two_sources_ignore_third_party_and_preserve_input(self):
        p=public_example();before=copy.deepcopy(p);out=mechanist_shield_inventory(p)
        self.assertEqual(p,before)
        self.assertEqual(out['source_filters']['caster']['total_raw_reference'],20*ONE)
        self.assertEqual(out['source_filters']['recipient']['total_raw_reference'],0)
        self.assertFalse(out['both_filters_pass_reference'])
        self.assertIsNone(out['source_filters']['caster']['rows'][0]['value_reference']['default_zero_used'])
        self.assertFalse(out['events_scheduled']);self.assertIsNone(out['actual_inventory_complete'])
        self.assertIsNone(out['actual_overflow_cancelled'])
        owner=mechanist_shield_inventory(public_example('owner'))['source_filters']
        self.assertEqual(owner['caster']['total_raw_reference'],20*ONE)
        self.assertEqual(owner['caster']['total_raw_reference'],owner['recipient']['total_raw_reference'])

    def test_inactive_null_not_shield_and_different_source_short_circuit_bad_bb(self):
        for field,value in (('finished_or_disabled',True),('buff_reference_present',False),
                ('has_shield',False),('source_reference_present',False),('source_identity','不同来源')):
            p=only_values(20*ONE);p['shields'][0][field]=value
            p['shields'][0]['value']=blackboard(available=False)
            r=filter_row(p)
            self.assertEqual(r['total_raw_reference'],0,(field,value))
            self.assertEqual(r['rows'][0]['contribution_raw_reference'],0)
            self.assertFalse(r['rows'][0]['eligible_reference'])
        p=public_example();p['shields'][1]['finished_or_disabled']=True
        self.assertTrue(mechanist_shield_inventory(p)['both_filters_pass_reference'])

    def test_mask_none_zero_and_unrelated_bits_never_filter_source_shields(self):
        for mask in (None,0,1,0xffffffff):
            p=only_values(20*ONE);p['shields'][0]['damage_mask_bits']=mask
            r=filter_row(p);self.assertEqual(r['total_raw_reference'],20*ONE)
            self.assertFalse(r['filter_le_zero_reference']);self.assertFalse(r['rows'][0]['mask_used_for_filtering'])

    def test_sum_before_epsilon_comparison(self):
        for a,b,total,passed in ((21475,21474,42949,True),(21475,21475,42950,False),(-1,42950,42949,True)):
            r=filter_row(only_values(a,b))
            self.assertEqual(r['total_raw_reference'],total)
            self.assertIs(r['filter_le_zero_reference'],passed)

    def test_signed_native_wrap_is_not_clamped_or_float_rounded(self):
        r=filter_row(only_values(1<<62,1<<62))
        self.assertEqual(r['total_raw_reference'],MIN_RAW);self.assertTrue(r['signed_wrap_occurred'])
        self.assertTrue(r['filter_le_zero_reference'])
        r=filter_row(only_values(MIN_RAW,-1))
        self.assertEqual(r['total_raw_reference'],(1<<63)-1)
        self.assertFalse(r['filter_le_zero_reference'])
        r=filter_row(only_values(-ONE,0));self.assertEqual(r['total_raw_reference'],-ONE)

    def test_complete_empty_inventory_zero_incomplete_empty_unknown(self):
        p=only_values();self.assertEqual(filter_row(p)['total_raw_reference'],0)
        for complete in (False,None):
            p['inventory_complete']=complete;r=filter_row(p)
            self.assertIsNone(r['total_raw_reference']);self.assertIsNone(r['filter_le_zero_reference'])
            self.assertEqual(r['known_wrapped_raw_subtotal'],0);self.assertFalse(r['subtotal_is_lower_bound'])

    def test_unknown_active_qualification_or_getter_cannot_be_zero(self):
        for field in ('buff_reference_present','finished_or_disabled','source_reference_present','has_shield'):
            p=only_values(0);p['shields'][0][field]=None;r=filter_row(p)
            self.assertIsNone(r['total_raw_reference'],field)
            self.assertIsNone(r['rows'][0]['contribution_raw_reference'])
        for returned,raw in ((None,ONE),(False,ONE),(True,None)):
            p=only_values(ONE);p['shields'][0]['value'].update(getter_returned=returned,raw=raw)
            self.assertIsNone(filter_row(p)['total_raw_reference'])

    def test_blackboard_object_absence_lookup_failure_and_unknown_are_distinct(self):
        p=only_values(0)
        p['shields'][0]['value']=blackboard(readable=False)
        r=filter_row(p);self.assertEqual(r['total_raw_reference'],0)
        self.assertTrue(r['rows'][0]['value_reference']['default_zero_used'])
        for available,readable,direct in ((False,False,True),(None,False,True),
                (True,None,True),(True,False,None),(True,False,False)):
            p['shields'][0]['value']=blackboard(readable=readable,available=available,direct=direct)
            r=filter_row(p);self.assertIsNone(r['total_raw_reference'])
            self.assertIsNone(r['rows'][0]['value_reference']['default_zero_used'])
        p['shields'][0]['value']=blackboard(0,True)
        r=filter_row(p);self.assertEqual(r['total_raw_reference'],0)
        self.assertFalse(r['rows'][0]['value_reference']['default_zero_used'])

    def test_signed_float32_conversion_boundaries_and_direct_sum(self):
        cases={0:0,0x80000000:0,1:0,0x80000001:0,0x3f800000:ONE,0xbf800000:-ONE,
            0x2f800000:1,0xaf800000:-1,0xcf000000:MIN_RAW,
            0x4f000000:None,0xcf000001:None,0x7f800000:None,0x7fc00000:None}
        for bits,expected in cases.items():
            self.assertEqual(float32_signed_number_raw(bits),expected,hex(bits))
        p=only_values(0,0)
        p['shields'][0]['value']=blackboard(0x3f800000)
        p['shields'][1]['value']=blackboard(0xbf800000)
        self.assertEqual(filter_row(p)['total_raw_reference'],0)
        p['shields'][1]['value']=blackboard(0x7fc00000)
        self.assertIsNone(filter_row(p)['total_raw_reference'])

    def test_partial_inventory_is_not_a_lower_bound_or_complete_total(self):
        p=only_values(20*ONE);p['inventory_complete']=False;r=filter_row(p)
        self.assertEqual(r['known_wrapped_raw_subtotal'],20*ONE)
        self.assertFalse(r['subtotal_is_lower_bound']);self.assertIsNone(r['total_raw_reference'])
        p['shields'].append(copy.deepcopy(p['shields'][0]));p['shields'][-1]['id']='未知贡献'
        p['shields'][-1]['value']['raw']=None;p['inventory_complete']=True
        r=filter_row(p);self.assertEqual(r['known_wrapped_raw_subtotal'],20*ONE)
        self.assertIsNone(r['filter_le_zero_reference'])

    def test_missing_source_pass_missing_target_fail_container_unknown(self):
        p=only_values();p['caster']['available']=False
        out=mechanist_shield_inventory(p);self.assertTrue(out['source_filters']['caster']['filter_le_zero_reference'])
        self.assertIsNone(out['source_filters']['caster']['total_raw_reference'])
        self.assertTrue(out['both_filters_pass_reference'])
        p['recipient']['available']=False;out=mechanist_shield_inventory(p)
        self.assertFalse(out['source_filters']['caster']['filter_le_zero_reference'])
        self.assertFalse(out['source_filters']['recipient']['filter_le_zero_reference'])
        for flag in (False,None):
            p=only_values();p['recipient_container_available']=flag
            self.assertIsNone(filter_row(p)['total_raw_reference'])
            self.assertIsNone(filter_row(p)['filter_le_zero_reference'])

    def test_unqualified_native_or_readpoint_continuity_and_source_fail_closed(self):
        for field in ('ordinary_native_path','no_changes_between_filters'):
            for value in (False,None):
                p=only_values();p[field]=value;out=mechanist_shield_inventory(p)
                self.assertIsNone(out['both_filters_pass_reference'])
                self.assertIsNone(out['source_filters']['caster']['total_raw_reference'])
        with patch('rouge.shield_source_inventory.source_valid',return_value=False):
            out=mechanist_shield_inventory(only_values())
            self.assertFalse(out['source_valid']);self.assertIsNone(out['both_filters_pass_reference'])

    def test_schema_and_identity_conflicts_rejected(self):
        invalid=[]
        for field,value in (('operator','kaltsit'),('skill',True),('read_point','pre_hit'),('inventory_complete',1)):
            p=public_example();p[field]=value;invalid.append(p)
        p=public_example('owner');p['recipient']['identity']='不同本体';invalid.append(p)
        p=public_example();p['shields'].append(copy.deepcopy(p['shields'][0]));invalid.append(p)
        for raw in (True,0.5,1<<63,MIN_RAW-1):
            p=only_values(0);p['shields'][0]['value']['raw']=raw;invalid.append(p)
        p=public_example();p['caster']['identity']=None;invalid.append(p)
        p=public_example();p['shields'][0]['value']['unexpected']=1;invalid.append(p)
        for p in invalid:
            with self.assertRaises(ValueError):mechanist_shield_inventory(p)

    def test_inventory_replaces_manual_totals_in_real_packet_ledger(self):
        p=inventory_ledger(public_example());before=copy.deepcopy(p);out=mechanist_barrier_ledger(p);row=out['rows'][0]
        self.assertEqual(p,before);self.assertTrue(row['depletion_gate'])
        self.assertFalse(row['overflow_cancel_requested']);self.assertTrue(row['explosion_requested'])
        self.assertTrue(row['replenishment_requested']);self.assertEqual(row['ammunition_consumed_reference'],1)
        self.assertEqual(row['source_shield_inventory_reference']['source_filters']['caster']['total_raw_reference'],20*ONE)
        self.assertIsNone(row['following_barrier_state']['dynamic_raw'])
        self.assertIsNone(row['actual_hp_loss'])
        p['packets'][0]['source_shield_inventory']['shields'][1]['finished_or_disabled']=True
        self.assertTrue(mechanist_barrier_ledger(p)['rows'][0]['overflow_cancel_requested'])
        p['packets'][0]['source_shield_inventory']['inventory_complete']=False
        self.assertIsNone(mechanist_barrier_ledger(p)['rows'][0]['overflow_cancel_requested'])

    def test_packet_mode_conflicts_wrong_recipient_and_legacy_signed_total(self):
        p=inventory_ledger(public_example());p['packets'][0]['caster_shields']={'source_available':True,'total_raw':0}
        with self.assertRaises(ValueError):mechanist_barrier_ledger(p)
        p=inventory_ledger(public_example('owner'))
        with self.assertRaises(ValueError):mechanist_barrier_ledger(p)
        p=ledger_example();p['packets']=[p['packets'][2]];p['packets'][0]['caster_shields']['total_raw']=MIN_RAW
        self.assertTrue(mechanist_barrier_ledger(p)['rows'][0]['overflow_cancel_requested'])
        self.assertIsNone(p['packets'][0]['following_barrier'])

    def test_ordered_filter_exception_blocks_downstream_but_second_filter_is_short_circuited(self):
        p=public_example();p['shields'][1]['value']=blackboard(readable=False,available=False)
        out=mechanist_shield_inventory(p)
        self.assertFalse(out['ordered_filters_returned_reference']);self.assertFalse(out['recipient_filter_called_reference'])
        row=mechanist_barrier_ledger(inventory_ledger(p))['rows'][0]
        for field in ('overflow_cancel_requested','explosion_requested','manual_count_requested',
                'replenishment_requested','finish_old_barrier_requested','ammunition_consumed_reference','ammunition_remaining_reference'):
            self.assertIsNone(row[field],field)
        p=public_example();p['shields'][2]['value']=blackboard(available=False)
        out=mechanist_shield_inventory(p)
        self.assertFalse(out['source_filters']['recipient']['normal_return_reference'])
        self.assertFalse(out['recipient_filter_called_reference']);self.assertTrue(out['ordered_filters_returned_reference'])
        row=mechanist_barrier_ledger(inventory_ledger(p))['rows'][0]
        self.assertFalse(row['overflow_cancel_requested']);self.assertTrue(row['explosion_requested'])
        self.assertEqual(row['ammunition_consumed_reference'],1)
        p['shields'][1]['finished_or_disabled']=True
        out=mechanist_shield_inventory(p);self.assertTrue(out['recipient_filter_called_reference'])
        self.assertFalse(out['ordered_filters_returned_reference'])
        self.assertIsNone(mechanist_barrier_ledger(inventory_ledger(p))['rows'][0]['ammunition_consumed_reference'])

    def test_missing_container_exception_and_missing_source_early_return(self):
        p=only_values();p['recipient_container_available']=False
        self.assertFalse(filter_row(p)['normal_return_reference'])
        self.assertFalse(mechanist_shield_inventory(p)['ordered_filters_returned_reference'])
        p['caster']['available']=False
        self.assertTrue(filter_row(p)['normal_return_reference']);self.assertTrue(filter_row(p)['filter_le_zero_reference'])
        self.assertFalse(mechanist_shield_inventory(p)['source_filters']['recipient']['normal_return_reference'])

    def test_completeness_qualifies_normal_return_but_unknown_value_alone_does_not(self):
        for complete in (False,None):
            p=only_values(0);p['inventory_complete']=complete
            out=mechanist_shield_inventory(p)
            self.assertIsNone(out['ordered_filters_returned_reference'])
            row=mechanist_barrier_ledger(inventory_ledger(p))['rows'][0]
            self.assertIsNone(row['explosion_requested']);self.assertIsNone(row['ammunition_consumed_reference'])
            p['shields'][0]['value']=blackboard(available=False)
            self.assertFalse(mechanist_shield_inventory(p)['ordered_filters_returned_reference'])
        p=only_values(None);out=mechanist_shield_inventory(p)
        self.assertIsNone(out['source_filters']['caster']['total_raw_reference'])
        self.assertTrue(out['ordered_filters_returned_reference'])
        row=mechanist_barrier_ledger(inventory_ledger(p))['rows'][0]
        self.assertTrue(row['explosion_requested']);self.assertEqual(row['ammunition_consumed_reference'],1)

    def test_source_hash_and_fifteen_method_native_receipt_binding(self):
        root=Path(__file__).resolve().parents[1];raw=(root/SOURCE).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),SOURCE_SHA256)
        source=json.loads(raw);proofraw=(root/source['native_proof']).read_bytes()
        self.assertEqual(hashlib.sha256(proofraw).hexdigest(),source['native_proof_sha256'])
        proof=json.loads(proofraw);self.assertEqual(len(proof['methods']),15)
        self.assertEqual(proof['unique_instruction_count'],1028)
        self.assertTrue(proof['all_instruction_bytes_rechecked'])
        self.assertFalse(proof['game_dll_executed']);self.assertFalse(proof['process_memory_read'])
        self.assertEqual(sum(m['method']['metadata_method_index'] is None for m in proof['methods']),3)
        self.assertTrue(all(m['cfg_bounded_traversal_finished'] and not m['limits'] for m in proof['methods']))


class ShieldInventoryViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app=QApplication.instance() or QApplication([])

    def test_chinese_query_packet_details_and_refresh_preserve_snapshots(self):
        from rouge.offline_tools_view import OfflineToolsPanel,public_payload,run_offline_query,render_offline_result
        panel=OfflineToolsPanel();panel.select_query('calibration','shield-inventory')
        payload=public_payload('calibration','shield-inventory');result=run_offline_query('calibration','shield-inventory',payload)
        rendered=render_offline_result('calibration','shield-inventory',result)
        self.assertIn('按来源汇总与双筛选门',rendered);self.assertIn('逐实例资格与贡献',rendered)
        self.assertIn('已证分项不是下界',rendered);self.assertNotIn('total_raw_reference',rendered)
        original=(panel.editor.toPlainText(),panel.current_query())
        panel.set_scenario({'operator':'kaltsit','skill':1})
        self.assertEqual(original,(panel.editor.toPlainText(),panel.current_query()))
        self.assertFalse(panel.import_scenario.isEnabled())
        packet=mechanist_barrier_ledger(inventory_ledger(public_example()))
        rendered=render_offline_result('calibration','barrier-ledger',packet)
        self.assertIn('独立受击后库存',rendered);self.assertIn('机械师来源',rendered)
        panel.close()


if __name__=='__main__':unittest.main()
