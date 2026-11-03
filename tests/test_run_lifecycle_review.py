"""Continuous public lifecycle through real state, roster and calculation UI."""
from copy import deepcopy
from unittest.mock import patch
import json,unittest
from PySide6.QtWidgets import QApplication
from rouge import app as application
from rouge.run_state import RunState
from rouge.player_team import crew_rows
from tests import test_state_calculation_updates as update_fixture
from tests.test_recipient_lifecycle_063 import full_bar,member,popup,SNACK,SNACK_BUFF,COOKIE,COOKIE_BUFF

TRANSITIONS=[]
observation=update_fixture.observation

class RunLifecycleReviewTests(unittest.TestCase):
 setUp=update_fixture.StateCalculationUpdateTests.setUp
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def apply(self,observed,label):
  w=self.window;before=deepcopy(observed);at=(w.run.state.get('last_read')or w.run.state['started_at'])+1
  with patch.object(application,'calculate_damage',wraps=application.calculate_damage)as calculate:self.assertTrue(w.apply_run_observation(observed,at))
  self.assertEqual(observed,before);self.assertEqual(calculate.call_count,1)
  rows=crew_rows(w.run.state);scenario=deepcopy(w.damage_result['scenario'])
  TRANSITIONS.append({'scenario':label,'present_ids':[r['id']for r in rows],'operator':scenario['operator'],'elite':scenario['elite'],'level':scenario['level'],'skill':scenario['skill'],'skill_rank':scenario['skill_rank'],'char_buff_ids':scenario['char_buff_ids'],'char_buff_pending_ids':scenario['char_buff_pending_ids'],'recruitment_kind':scenario['recruitment_kind']})
  return w.run.state['operators'].get('mechanist',{}),scenario
 def test_continuous_recruit_promote_targeted_buffs_reload_depart_and_rejoin(self):
  TRANSITIONS.clear();w=self.window;initial=observation();initial['operators'][0]['recruitment_kind']='non_emergency';initial_id=w.run.state['id']
  record,s=self.apply(initial,'精一招募');self.assertEqual((s['elite'],s['level'],s['skill_rank']),(1,80,7))
  self.apply({'operators':[popup(fields={'elite':1},advanced=False)]},'完整强化页确认未领取')
  self.apply(full_bar(SNACK,COOKIE),'读取两件定向藏品')
  record,s=self.apply({'operators':[member(fields={'elite':2},advanced=True)]},'读取进阶但不猜模组或专精')
  self.assertIn(SNACK_BUFF,record['char_buff_pending_ids']);self.assertIn(COOKIE_BUFF,record['char_buff_pending_ids']);self.assertIn('selected_skill',record['invalid_fields']);self.assertIn('1',record['invalid_skill_ranks'])
  record,s=self.apply({'operators':[popup([SNACK_BUFF],complete=False)]},'局部强化页只确认零食盒')
  self.assertIn(SNACK_BUFF,s['char_buff_ids']);self.assertNotIn(COOKIE_BUFF,s['char_buff_ids']);self.assertIn(COOKIE_BUFF,s['char_buff_pending_ids'])
  record,s=self.apply({'operators':[popup([SNACK_BUFF,COOKIE_BUFF])]},'完整强化页确认两个领取')
  self.assertEqual(set(s['char_buff_ids']),{SNACK_BUFF,COOKIE_BUFF});self.assertEqual(s['char_buff_pending_ids'],[])
  record,s=self.apply({'operators':[member(fields={'level':90,'module_id':None,'module_level':0,'selected_skill':3},skill_ranks={'3':10})]},'补齐本局等级与三技能专精')
  self.assertEqual((s['level'],s['skill'],s['skill_rank']),(90,3,10));self.assertEqual(record['invalid_fields'],[])
  stable=deepcopy(record);history=deepcopy(w.run.state['history']);selected=w.operator.currentData()
  record,s=self.apply({'operators':[member()]},'普通页面复用培养与强化');self.assertEqual(record['fields'],stable['fields']);self.assertEqual(record['char_buff_ids'],stable['char_buff_ids']);self.assertEqual(w.run.state['history'],history)
  w.run=RunState(w.run.file);w.refresh_operator_overview();w.sync_run_config();w.sync_run_relics();w.update_operator();self.assertEqual(w.run.state['id'],initial_id);self.assertEqual(w.operator.currentData(),selected);self.assertEqual(w.run.state['operators']['mechanist']['char_buff_ids'],stable['char_buff_ids'])
  record,s=self.apply({'operators':[member()]},'重启后继续复用')
  record,s=self.apply({'crew_count':1,'operators':[member('char_151_myrtle',fields={'elite':1,'level':60})]},'完整队伍确认机械师离队')
  self.assertFalse(record['present']);self.assertEqual({r['id']for r in crew_rows(w.run.state)},{'char_151_myrtle'})
  self.assertEqual(s['char_buff_ids'],[])
  record,s=self.apply({'operators':[member(recruitment_kind='emergency_hire')]},'重新招募不沿用旧培养与强化')
  self.assertTrue(record['present']);self.assertEqual(record['char_buff_ids'],[]);self.assertEqual(s['char_buff_ids'],[]);self.assertTrue(set(stable['fields'])<=set(record['invalid_fields']));self.assertIn('3',record['invalid_skill_ranks']);self.assertEqual(record['char_buff_absent_ids'],[])
  before=deepcopy(w.run.state);self.assertFalse(w.apply_run_observation(initial,1001));self.assertEqual(w.run.state,before)
  self.assertEqual(w.run.state['id'],initial_id);self.assertEqual(w.run.state['history'][:len(history)],history)
 def test_origin_discovery_and_incomplete_roster_never_erase_confirmed_owned_buffs(self):
  w=self.window;self.apply(observation(),'本局初读');record,s=self.apply({'operators':[popup([SNACK_BUFF],fields={'elite':1})]},'归属先于招募来源读取')
  before=deepcopy(record);record,s=self.apply({'operators':[member(recruitment_kind='non_emergency')]},'首次确认来源不当重新招募');self.assertEqual(record['fields'],before['fields']);self.assertEqual(s['char_buff_ids'],[SNACK_BUFF])
  self.apply({'operators':[member('char_151_myrtle',fields={'elite':1,'level':60})]},'局部队伍不证明其他成员离队');self.assertEqual({r['id']for r in crew_rows(w.run.state)},{'mechanist','char_151_myrtle'})
  record,s=self.apply(full_bar(),'母藏品离开后保留已确认个人强化');self.assertEqual(record['char_buff_ids'],[SNACK_BUFF]);self.assertEqual(s['char_buff_ids'],[SNACK_BUFF]);self.assertFalse(any(e['kind']=='recruitment_changed'and e.get('id')=='mechanist'for e in w.run.state['history']))
 def test_only_explicit_temporary_reset_clears_memory_and_stale_run_context_is_rejected(self):
  w=self.window;self.apply(observation(),'开始手动重置前的隔离局');before=deepcopy(w.run.state);old_id=before['id'];old_path=w.run.file
  self.assertFalse(w.reset_run());self.assertNotEqual(w.run.state['id'],old_id);self.assertEqual(w.run.state['operators'],{});self.assertEqual(w.run.state['config'],{})
  # reset_run returns None on successful existing UI path, so assert effects.
  self.assertEqual(w.run.file,old_path);fresh=deepcopy(w.run.state);at=fresh['started_at']+1
  with patch.object(application,'calculate_damage',wraps=application.calculate_damage)as calculate:self.assertFalse(w.apply_run_observation({**observation(),'config_reuse':{'run_id':old_id}},at))
  self.assertEqual(calculate.call_count,0);self.assertEqual(w.run.state,fresh)

if __name__=='__main__':unittest.main()
