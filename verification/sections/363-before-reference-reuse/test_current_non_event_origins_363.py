"""Prepared363 checks; not executed or counted as native validation."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,subprocess,sys,unittest
from rouge import current_non_event_origins as model


def clone(root):
    for name in(model.MANIFEST,*json.loads((model.ROOT/model.MANIFEST).read_bytes())['files']):
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((model.ROOT/name).read_bytes())


class CurrentNonEventOrigins363Tests(unittest.TestCase):
    def test_rebuild_and_ten_exact_original_pointers_counts_and_complete_parent_records(self):
        run=subprocess.run([sys.executable,'-B','scripts/build_current_non_event_origins_363.py','--check'],cwd=model.ROOT,capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr)
        result=model.reference();current=model.version.packet()['current']['details']
        self.assertEqual(len(result['rows']),10);self.assertIsNone(result['selected'])
        self.assertEqual({r['source_id']for r in result['rows']},set((*model.SQUADS,*model.RELICS)))
        for row in result['rows']:
            self.assertEqual(row['source_item'],current['items'][row['source_id']])
            self.assertEqual(row['source_effect'],current['relics'][row['source_id']])
            self.assertEqual(row['source_buff'],row['source_effect']['buffs'][row['source_buff_index']])
            board={v['key']:v['valueStr']if v['valueStr']is not None else v['value']for v in row['source_buff']['blackboard']}
            self.assertEqual(board['id'],row['item_id']);self.assertEqual(board['count'],row['reference_quantity'])
            self.assertEqual(row['item'],current['items'][row['item_id']])
        self.assertFalse(result['data']['complete_acquisition_pool']);self.assertFalse(result['run_updated']);self.assertFalse(result['calculation_applied'])
        for key in('actual_eligible','actual_source_active','actual_received','actual_quantity','actual_candidate','actual_cultivation','actual_cost'):
            self.assertIsNone(result[key])

    def test_real_kind_and_timing_intersections_and_exact_name_search(self):
        self.assertEqual(len(model.reference(kind='squad')['rows']),8)
        self.assertEqual(len(model.reference(kind='relic')['rows']),2)
        self.assertEqual(len(model.reference(timing='initial')['rows']),8)
        self.assertEqual(model.reference(kind='relic',timing='initial')['rows'],[])
        rows=model.reference(query='多边贸易')['rows'];self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['reference_quantity'],3)
        self.assertEqual(model.reference(query='枯苔藓球')['rows'],rows)
        self.assertEqual(len(model.reference(query='印')['rows']),2)

    def test_explicit_initial_time_docs_and_geology_different_source_are_preserved(self):
        result=model.reference()
        for row in result['rows']:
            doc=result['data']['documents'][row['source_id']]
            if row['kind']=='squad':
                self.assertEqual(doc['revision'],442954);self.assertEqual(doc['timing'],'initial')
                self.assertIn('初始携带',doc['visible_text']);self.assertIn(row['item_name'].strip('“”'),doc['visible_text'])
                self.assertIn('<tr',doc['full_html']);self.assertGreater(doc['html_character_span'][1],doc['html_character_span'][0])
        row=next(r for r in result['rows']if r['source_id']=='rogue_6_band_21')
        self.assertNotIn('初始携带',row['source_item']['usage'])
        self.assertFalse(result['data']['documents'][row['source_id']]['original_usage_also_explicit'])
        self.assertIn('当前主题文献的补充说明',model.player_text(model.reference(row['id'])))

    def test_old_theme_voucher_timing_not_promoted_and_exact_existing354_ticket_parameters(self):
        from rouge import current_recruit_tickets as recruits
        for row in model.reference(kind='relic')['rows']:
            self.assertEqual(row['time'],'unspecified');self.assertEqual(row['reference_quantity'],1)
            self.assertEqual(row['item'],recruits.reference(row['item_id'])['selected']['original_item'])
            text=model.player_text(model.reference(row['id']))
            self.assertIn('具体时点尚未核验',text);self.assertIn('水月主题下',text)
            self.assertIn('不是任选一名已拥有干员',text);self.assertIn('不将它当作进阶券',text)

    def test_initial_configuration_ranges_are_exact_not_actual_activation_and_do_not_merge_same_name_variants(self):
        current=model.version.packet()['current']['details']
        for row in model.reference(kind='squad')['rows']:
            wanted=[c for c in current['init']if row['source_id']in c['initialBandRelic']]
            self.assertEqual(row['initial_configuration_references'],wanted)
            self.assertEqual(row['band_reference'],current['bandRef'][row['source_id']])
            self.assertIsNone(row['actual_source_active'])
        row=next(r for r in model.reference()['rows']if r['source_id']=='rogue_6_band_5')
        self.assertEqual([c['modeGrade']for c in row['initial_configuration_references']if c['modeId']=='NORMAL'],list(range(6,17)))
        self.assertEqual(len([c for c in row['initial_configuration_references']if c['modeId']=='MONTH_TEAM']),4)
        row=next(r for r in model.reference()['rows']if r['source_id']=='rogue_6_band_27')
        text=model.player_text(model.reference(row['id']))
        self.assertIn('初始3个枯苔藓球',text);self.assertIn('不在这里再加1',text)
        self.assertIn('不等于相应等级下必然选择此档位',text)

    def test_true_bidirectional_original_entries_and_360_361_scope_excluded(self):
        for row in model.reference()['rows']:
            a=model.destination(row['id'],'source');b=model.destination(row['id'],'item')
            self.assertEqual((a['category'],a['key']),(row['source_category'],row['source_id']))
            self.assertEqual((b['category'],b['key']),(row['item_category'],row['item_id']))
            self.assertEqual(model.locate(a['category'],a['key'])['identity'],row['id'])
            self.assertEqual(model.locate(b['category'],b['key'])['identity'],row['id'])
            self.assertEqual(model.locate('items',row['item_id'])['identity'],row['id'])
        for args in(('relics','rogue_6_relic_assign_1'),('relics','rogue_6_legacy_10'),('squads','rogue_6_band_4'),('items','pool_scrap_18')):
            self.assertIsNone(model.locate(*args))

    def test_source_loss_real_file_bytes_and_underlying_reader_loss_fail_closed_then_recover(self):
        from rouge import current_recruit_tickets as recruits
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    path=root/name;raw=path.read_bytes();self.assertIsNotNone(model.packet())
                    path.write_bytes(raw+b'x');self.assertIsNone(model.packet(),name)
                    path.write_bytes(raw);self.assertIsNotNone(model.packet())
        with patch.object(recruits,'packet',return_value=None):self.assertIsNone(model.packet())
        with patch.object(model.version,'packet',return_value=None):self.assertIsNone(model.packet())

    def test_invalid_inputs_missing_exact_pointer_or_mutation_cannot_become_a_grant(self):
        for kwargs in({'identity':True},{'identity':'unknown'},{'kind':True},{'kind':'event'},
                       {'timing':False},{'timing':'gain_now'},{'query':None}):self.assertIsNone(model.reference(**kwargs))
        self.assertIsNone(model.destination('unknown','source'));self.assertIsNone(model.destination(model.reference()['rows'][0]['id'],True))
        current=deepcopy(model.version.packet()['current']['details'])
        current['relics']['rogue_6_band_21']['buffs'][0]['blackboard'][0]['valueStr']='unknown'
        with self.assertRaises(ValueError):model.source_rows(current)
        result=model.reference();result['data']['rows'].clear();result['rows'].clear()
        self.assertEqual(len(model.reference()['rows']),10)


if __name__=='__main__':unittest.main()
