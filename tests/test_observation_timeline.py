"""Out-of-order recognition must equal the original chronological reducers."""
from copy import deepcopy
from itertools import permutations
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from rouge.run_state import RunState
from rouge.account_cache import AccountCache
from rouge.catalog import catalog,operator_profiles
from rouge.observation_timeline import ObservationTimeline,memory_model
from rouge.frame_buffer import FrameBuffer
import numpy as np


class ObservationTimelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.folder=Path(self.temp.name)
        self.run=RunState(self.folder/'run.json');self.account=AccountCache(self.folder/'account.json',operator_profiles(),catalog()['operators'])
        self.at=self.run.state['started_at']+1

    def observations(self):
        relic='rogue_6_relic_cargo_1'
        member={'id':'mechanist','scope':'run','fields':{'elite':1,'level':80},'skill_ranks':{'1':7},'present':True}
        return [
            {'captured_at':self.at,'run':{'config':{'difficulty':{'value':5}},'resources':{'gold':{'value':2}},'operators':[member],'crew_count':1},'operator':{'id':'kaltsit','scope':'account','fields':{'elite':2,'level':60}}},
            {'captured_at':self.at+1,'run':{'resources':{'gold':{'value':1}},'relics':{'ids':[relic],'icons':[{'id':relic,'candidates':[relic],'confirmed':True}],'count':1,'source':'held_bar'},'node_content':{'kind':'event','title':'较早事件'}}},
            {'captured_at':self.at+2,'run':{'operators':[{**member,'fields':{'elite':2,'level':90},'skill_ranks':{'2':10}}]},'operator':{'id':'kaltsit','scope':'account','fields':{'potential':3}}},
            {'captured_at':self.at+3,'run':{'resources':{'gold':{'value':9}},'relics':{'ids':[],'icons':[],'count':0,'source':'held_bar'},'node_content':{'kind':'battle','title':'较新关卡'}},'operator':{'id':'kaltsit','scope':'account','fields':{'level':90}}}]

    def test_every_completion_order_matches_chronological_state_and_history(self):
        rows=self.observations();oracle=type('Oracle',(),{})()
        oracle.run=memory_model(self.run,('state',));oracle.account=memory_model(self.account,('records','issues'))
        for row in rows:
            if row.get('run'):oracle.run.apply(row['run'],row['captured_at'])
            if row.get('operator'):oracle.account.observe(row['operator'],row['captured_at'])
        for order in permutations(range(1,5)):
            with self.subTest(order=order):
                timeline=ObservationTimeline(self.run,self.account);remaining=set(order)
                for seq in order:
                    remaining.remove(seq);timeline=timeline.prepare(rows[seq-1],seq,min(remaining)if remaining else None)
                self.assertEqual(timeline.run.state,oracle.run.state)
                self.assertEqual(timeline.account.records,oracle.account.records)
                self.assertFalse(timeline.pending);self.assertEqual(timeline.committed_seq,4)
        self.assertEqual(oracle.run.state['resources']['gold']['value'],9)
        self.assertEqual(oracle.run.state['last_node_content']['title'],'较新关卡')
        self.assertEqual(oracle.account.records['kaltsit']['fields']['potential'],3)
        self.assertEqual(oracle.account.records['kaltsit']['fields']['level'],90)
        self.assertTrue(any(row['kind']=='relic_no_longer_held'for row in oracle.run.state['history']))

    def test_prepare_has_no_disk_IO_or_mutation_until_complete_commit(self):
        timeline=ObservationTimeline(self.run,self.account);before=deepcopy(self.run.state)
        with patch.object(self.run,'save',wraps=self.run.save)as save_run,patch.object(self.account,'save',wraps=self.account.save)as save_account:
            prepared=timeline.prepare(self.observations()[3],4,1)
            save_run.assert_not_called();save_account.assert_not_called()
            self.assertEqual(self.run.state,before);self.assertFalse(timeline.pending)
            prepared.commit(self.run,self.account)
            self.assertEqual(save_run.call_count,1);self.assertEqual(save_account.call_count,1)
        self.assertTrue((self.folder/'run.json').is_file());self.assertTrue((self.folder/'account.json').is_file())

    def test_protected_private_records_are_not_unprotected_by_replay(self):
        self.run.preserve_unreadable=True;self.account.preserve_original=True
        timeline=ObservationTimeline(self.run,self.account).prepare(self.observations()[3],4,None)
        timeline.commit(self.run,self.account)
        self.assertTrue(self.run.preserve_unreadable);self.assertTrue(self.account.preserve_original)
        self.assertFalse((self.folder/'run.json').exists());self.assertFalse((self.folder/'account.json').exists())

    def test_replay_discovered_damage_keeps_original_file(self):
        self.account.observe(self.observations()[0]['operator'],self.at)
        original=self.account.path.read_bytes()
        self.account.records['kaltsit']['fields']['potential']=0
        self.assertFalse(self.account.preserve_original)
        timeline=ObservationTimeline(self.run,self.account).prepare(self.observations()[3],4,None)
        self.assertTrue(timeline.account.preserve_original)
        self.assertFalse(self.account.preserve_original)
        _,changed=timeline.commit(self.run,self.account)
        self.assertTrue(changed)
        self.assertTrue(self.account.preserve_original)
        self.assertEqual(self.account.path.read_bytes(),original)
        self.assertEqual(self.account.records['kaltsit']['fields']['level'],90)

    def test_protection_added_after_prepare_is_not_lost(self):
        self.account.observe(self.observations()[0]['operator'],self.at)
        original=self.account.path.read_bytes()
        timeline=ObservationTimeline(self.run,self.account).prepare(self.observations()[3],4,None)
        self.assertFalse(timeline.account.preserve_original)
        self.account.preserve_original=True
        timeline.commit(self.run,self.account)
        self.assertTrue(self.account.preserve_original)
        self.assertEqual(self.account.path.read_bytes(),original)

    def test_current_first_retains_each_short_capture_and_drains_earliest_next(self):
        buffer=FrameBuffer(settle_seconds=0)
        for i in range(1,9):buffer.offer(np.full((20,30,3),20*i,np.uint8),self.at+i)
        current=buffer.take(prefer_latest=True);self.assertEqual(current['seq'],8)
        self.assertEqual(buffer.stats()['oldest_seq'],1)
        history=[]
        while buffer.stats()['pending']:history.append(buffer.take()['seq'])
        self.assertEqual(history,list(range(1,8)));self.assertEqual(buffer.stats()['overflow'],0)

    def test_repeated_sequence_cannot_duplicate_already_committed_events(self):
        timeline=ObservationTimeline(self.run,self.account);row=self.observations()[1]
        first=timeline.prepare(row,2,None);second=first.prepare(row,2,None)
        self.assertEqual(first.run.state,second.run.state);self.assertEqual(first.account.records,second.account.records)

    def test_passed_map_node_and_departure_recruitment_history_survive_latest_first(self):
        from rouge.player_map_acceptance import fixtures
        graph=deepcopy(fixtures()[0][0]);graph['status']='matched'
        node=next(n for n in graph['nodes']if not n.get('template_type'));node['observed_type']='诡意行商';node['visible']=True
        passed=deepcopy(graph);next(n for n in passed['nodes']if n['id']==node['id'])['observed_type']='林间空地'
        member={'id':'mechanist','scope':'run','fields':{'elite':1,'level':80},'skill_ranks':{},'recruitment_kind':'non_emergency'}
        rows=[{'captured_at':self.at,'run':{'map':graph,'operators':[member],'crew_count':1}},
              {'captured_at':self.at+1,'run':{'map':passed,'operators':[],'crew_count':0}},
              {'captured_at':self.at+2,'run':{'operators':[{**member,'fields':{'elite':2,'level':90},'recruitment_kind':'emergency_hire'}],'crew_count':1}}]
        oracle=memory_model(self.run,('state',))
        for row in rows:oracle.apply(row['run'],row['captured_at'])
        timeline=ObservationTimeline(self.run,self.account)
        for seq,floor in((3,1),(1,2),(2,None)):timeline=timeline.prepare(rows[seq-1],seq,floor)
        self.assertEqual(timeline.run.state,oracle.state)
        recorded=next(n for n in timeline.run.state['maps'][graph['zone_id']]['nodes']if n['id']==node['id'])
        self.assertEqual(recorded['observed_type'],'林间空地');self.assertEqual(recorded['remembered_type'],'诡意行商')
        self.assertTrue(timeline.run.state['operators']['mechanist']['present'])
        self.assertEqual(timeline.run.state['operators']['mechanist']['recruitment_kind'],'emergency_hire')

    def test_current_first_still_retains_short_page_during_local_animation_overload(self):
        import cv2
        from tests.test_frame_buffer import page
        buffer=FrameBuffer(max_frames=4,settle_seconds=0)
        buffer.offer(page(30,label='OPERATOR'),1)
        for i in range(30):
            image=page(150,label='MAP');cv2.rectangle(image,(20+i*5,140),(40+i*5,160),(220,100,40),-1)
            buffer.offer(image,2+i*.1)
        self.assertEqual(buffer.take(prefer_latest=True)['captured_at'],4.9)
        self.assertEqual(buffer.take()['captured_at'],1)
        self.assertGreater(buffer.stats()['overflow_low_novelty'],0)

if __name__=='__main__':unittest.main()
