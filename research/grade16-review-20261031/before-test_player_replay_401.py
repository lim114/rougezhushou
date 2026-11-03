from copy import deepcopy
import unittest
from rouge.player_replay import history_rows, observation_time, event_text

class ReplayTests(unittest.TestCase):
    def test_saved_order_is_not_reordered_by_timestamps(self):
        state={'history':[{'at':5,'kind':'node_content_seen','title':'遗忘时间'},None,{'at':2,'kind':'resource_updated','resource':'gold','value':2}]}
        before=deepcopy(state);rows=history_rows(state)
        self.assertEqual([row['index']for row in rows],[0,2]);self.assertEqual(state,before)
        rows[0]['event']['title']='changed';self.assertEqual(state,before)

    def test_unknown_time_and_kind_never_crash_or_invent_log(self):
        for value in(None,True,float('inf'),float('nan'),'5',10**50):self.assertEqual(observation_time(value),'读取时间未确认')
        row=history_rows({'history':[{'kind':'future_field'}]})[0]
        self.assertEqual(row['label'],'其他读取记录');self.assertIn('不是完整游戏日志',event_text(row))

    def test_explicit_read_name_and_configuration_are_player_readable(self):
        row=history_rows({'history':[{'at':1,'kind':'node_content_seen','title':'险路尽头'}]})[0]
        self.assertIn('险路尽头',event_text(row));self.assertNotIn('node_content_seen',event_text(row))
        row=history_rows({'history':[{'at':1,'kind':'config_updated','field':'difficulty','current':{'value':15}}]})[0]
        self.assertIn('保密等级：15',event_text(row))
        row=history_rows({'history':[{'at':1,'kind':'config_updated','field':'difficulty','current':{'value':16}}]})[0]
        self.assertIn('这条记录写有16',event_text(row));self.assertIn('尚未核验',event_text(row))

    def test_empty_and_malformed_history_have_no_invented_entries(self):
        for raw in(None,{},'history'):self.assertEqual(history_rows({'history':raw}),[])
        self.assertEqual(history_rows({}),[])

    def test_opaque_configuration_field_does_not_crash_or_become_difficulty(self):
        for field in ([],{},True,1,None):
            state={'history':[{'at':1,'kind':'config_updated','field':field,'current':{'value':15}}]}
            before=deepcopy(state)
            text=event_text(history_rows(state)[0])
            self.assertIn('对局信息：尚未核验',text)
            self.assertNotIn('保密等级：15',text)
            self.assertEqual(state,before)

if __name__=='__main__':unittest.main()
