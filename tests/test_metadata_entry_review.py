from copy import deepcopy
from unittest.mock import patch
import unittest
from rouge.run_metadata_view import format_run_buff_status
from rouge import recipient_state

class MetadataEntryTests(unittest.TestCase):
    def test_buff_label_qualifies_mask_and_presence_once(self):
        class Record(dict):
            mask_reads=0
            presence_reads=0
            def get(self,key,default=None):
                if key=='unconfirmed_run_metadata':self.mask_reads+=1
                return super().get(key,default)
            def __getitem__(self,key):
                if key=='present':self.presence_reads+=1
                return super().__getitem__(key)
        state=Record(scope='run',present=True,char_buff_ids=['retained'],qualified_char_buff_ids=['fresh'],
            unconfirmed_run_metadata=['char_buff_ids'],char_buffs_complete=True)
        before=dict(state)
        self.assertEqual(format_run_buff_status(state,{'fresh':{'name':'已读强化'}}),
            '已读强化；其他保留的个人强化资格尚未重新确认。')
        self.assertEqual(state.mask_reads,1);self.assertEqual(state.presence_reads,1)
        self.assertEqual(state,before)

    def test_grant_candidates_share_one_absence_snapshot_and_keep_all_reasons(self):
        member={'id':'op','scope':'run','present':True,'char_buff_ids':['positive'],
            'char_buff_absent_ids':['a','b'],'char_buff_absence_observed_at':10}
        state={'operators':{'op':member},'relics':{'r1':{'captured_at':11},'r2':{'captured_at':12}},'history':[]}
        rules={'r1':{'trigger':'gain_random','char_buff_ids':['a']},'r2':{'trigger':'gain_random','char_buff_ids':['b']}}
        with patch.object(recipient_state,'lifecycle_rules',return_value=rules),patch.object(recipient_state,'compatible_buffs',return_value={'a','b','positive'}),patch.object(recipient_state,'absent_buffs',wraps=recipient_state.absent_buffs)as absent:
            recipient_state.invalidate_recipient_absence(state,[],{'r1','r2'},set(),13)
            self.assertEqual(absent.call_count,1)
        self.assertEqual(member['char_buff_ids'],['positive'])
        self.assertEqual(member['char_buff_absent_ids'],[])
        self.assertEqual(member['char_buff_pending_ids'],['a','b'])
        self.assertEqual(state['history'][0]['reasons'],[{'relic_id':'r1','trigger':'gain_random','observation':'newly_confirmed_item'},
            {'relic_id':'r2','trigger':'gain_random','observation':'newly_confirmed_item'}])

    def test_no_trigger_keeps_absence_unread_and_state_unchanged(self):
        state={'operators':{'op':{'id':'op','scope':'run','present':True}},'relics':{},'history':[]}
        before=deepcopy(state)
        with patch.object(recipient_state,'lifecycle_rules',return_value={'r1':{'trigger':'gain_random','char_buff_ids':['a']}}),patch.object(recipient_state,'absent_buffs',side_effect=AssertionError('inactive absence read')):
            recipient_state.invalidate_recipient_absence(state,[],set(),set(),13)
        self.assertEqual(state,before)

    def test_team_refresh_reads_each_saved_selection_once(self):
        from types import SimpleNamespace
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from rouge.player_team import TeamPanel
        from rouge.catalog import operator_profiles
        qt=QApplication.instance()or QApplication([])
        run=SimpleNamespace(state={'operators':{'mechanist':{}}})
        panel=TeamPanel(run);self.addCleanup(panel.close)
        listing=panel.lists[operator_profiles()['mechanist']['profession']]
        listing.setCurrentRow(0)
        run.state['operators']['mechanist']['fields']={'level':50}
        with patch.object(listing,'currentItem',wraps=listing.currentItem)as selected:
            panel.refresh();self.assertEqual(selected.call_count,1)
        self.assertEqual(listing.currentItem().data(Qt.ItemDataRole.UserRole),'mechanist')

if __name__=='__main__':unittest.main()
