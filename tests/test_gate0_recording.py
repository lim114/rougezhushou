"""Local instrumentation, privacy allowlist and unchanged overlay decisions."""
import ast
from contextlib import closing
from copy import deepcopy
import json
import math
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication, QWidget
from rouge import player_game_map as overlay
from rouge.session_recording import SessionRecorder, state_snapshot
from scripts.gate0_report import summarize
from scripts.benchmark_gate0_recording import benchmark


def fixture():
    image=np.full((100,100,3),50,np.uint8)
    frame={'captured_at':100,'image':image,'client_rect':[0,0,100,100], 'target':{'hwnd':1,'pid':2}}
    reference={**frame,'run_id':'run-test','observation':{'page':'exploration','texts':[
        {'text':'固定层','confidence':.99,'box':[[.1,.1],[.3,.1],[.3,.2],[.1,.2]]}],
        'map':{'zone_id':'z','template_id':'t','status':'matched','nodes':[
            {'id':str(i),'center':p,'visible':True}for i,p in enumerate(((.2,.4),(.5,.5),(.8,.8)))]}}}
    snapshot={'active':True,'foreground_on_game':True,'key':(1,2),'physical_client':(0,0,100,100),'logical_client':QRect(0,0,100,100)}
    return reference,deepcopy(frame),snapshot


class Gate0Tests(unittest.TestCase):
    def test_overlay_capture_times_do_not_turn_each_tick_into_a_new_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            recorder=SessionRecorder(Path(tmp)/'session',scenario='overlay_heartbeat')
            for now in(0,.5,1,1.5):
                recorder.overlay({'reason':'eligible','evaluated_at':now,'current_captured_at':now,
                                  'reference_captured_at':now,'label_min_correlation':.999-now*.0001},
                                 did_show=True,enabled=True,kind=None,now=now)
            recorder.close()
            rows=[json.loads(line) for line in (recorder.folder/'events.jsonl').read_text('utf8').splitlines()]
            self.assertEqual(len([row for row in rows if row['event']=='overlay']),2)

    def test_ocr_row_counters_are_recorded_without_raw_inputs_or_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            recorder=SessionRecorder(Path(tmp)/'session',scenario='row_reuse')
            state={'id':'isolated','config':{},'resources':{},'operators':{},'relics':{},'tactical_tools':{}}
            observation={'page':'test','performance':{'ocr':{'mode':'full_discovery',
                'inferred_text_rows':1,'reused_text_rows':4,'detected_boxes':5,
                'complete_current_texts':True,'raw_text':'PRIVATE_TEXT',
                'frame_signature':{'sha256':'PRIVATE_DIGEST'}}}}
            recorder.sample(observation,state,applied=True,reason='test');recorder.close()
            raw=(recorder.folder/'events.jsonl').read_text('utf8')
            self.assertNotIn('PRIVATE',raw)
            sample=next(json.loads(line) for line in raw.splitlines() if json.loads(line)['event']=='sample')
            self.assertEqual(sample['performance']['ocr']['reused_text_rows'],4)
            self.assertEqual(sample['performance']['ocr']['inferred_text_rows'],1)

    def test_overlay_matches_original_decisions_and_coordinates(self):
        raw=subprocess.check_output(['git','show','e17cd2237fd60a6bac71b0ee87fded16302796a2:rouge/player_game_map.py'])
        node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='payload')
        namespace={'__package__':'rouge','time':time,'math':math,'np':np}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'baseline-payload','exec'),namespace)
        cases=[]
        cases.append(fixture())
        for field,value in [('captured_at',None),('captured_at',True),('captured_at',float('nan')),('captured_at',69),('run_id','other')]:
            a,b,c=fixture();a[field]=value;cases.append((a,b,c))
        a,b,c=fixture();b['captured_at']=97;cases.append((a,b,c))
        a,b,c=fixture();a['observation']['map']['nodes'].pop();cases.append((a,b,c))
        a,b,c=fixture();b['client_rect']=[0,0,99,100];cases.append((a,b,c))
        a,b,c=fixture();b['image'][10:21,10:31]=90;cases.append((a,b,c))
        a,b,c=fixture();c['foreground_on_game']=False;cases.append((a,b,c))
        with patch('rouge.run_config.config_data',return_value={'zones':{'z':{'name':'固定层'}}}):
            for a,b,c in cases:
                expected=namespace['payload'](a,b,c,'run-test',now=100)
                self.assertEqual(overlay.payload(a,b,c,'run-test',now=100),expected)
                self.assertEqual(overlay.payload(a,b,c,'run-test',now=100,diagnostics={}),expected)

    def test_three_target_scenarios_report_current_rules_without_fixing_them(self):
        with patch('rouge.run_config.config_data',return_value={'zones':{'z':{'name':'固定层'}}}):
            a,b,c=fixture();a['captured_at']=40;d={}
            self.assertIsNone(overlay.payload(a,b,c,'run-test',now=100,diagnostics=d))
            self.assertEqual(d['reason'],'reference_expired')
            a,b,c=fixture();a['observation']['map']['nodes'].pop();d={}
            self.assertIsNone(overlay.payload(a,b,c,'run-test',now=100,diagnostics=d))
            self.assertEqual((d['reason'],d['anchor_count']),('anchors_insufficient',3))
            a,b,c=fixture();b['client_rect']=[0,0,90,100];d={}
            self.assertIsNone(overlay.payload(a,b,c,'run-test',now=100,diagnostics=d))
            self.assertEqual(d['reason'],'geometry_changed')
            a['client_rect']=b['client_rect'];c['physical_client']=(0,0,90,100)
            self.assertIsNotNone(overlay.payload(a,b,c,'run-test',now=100,diagnostics={}))

    def test_recording_diff_is_detached_and_excludes_private_text(self):
        state={'id':'r','resources':{'life':{'value':0}},'operators':{},'relics':{},'notes':'PRIVATE_NOTE','chat':'PRIVATE_CHAT','api_key':'PRIVATE_KEY'}
        observation={'page':'exploration','performance':{'total_ms':12,'raw_ocr':'PRIVATE_OCR','routing':{'strategy':'visual_region_ocr','text':'PRIVATE_TEXT'}}}
        with tempfile.TemporaryDirectory()as tmp, closing(SessionRecorder(Path(tmp)/'session',scenario='normal'))as r:
            r.sample(observation,state,applied=True,reason='applied')
            r.sample(observation,state,applied=True,reason='applied')
            state['resources']['life']['value']=1
            r.sample(observation,state,applied=True,reason='applied');r.close()
            raw=(r.folder/'events.jsonl').read_text('utf8');rows=[json.loads(v)for v in raw.splitlines()]
            self.assertNotIn('PRIVATE',raw)
            samples=[v for v in rows if v['event']=='sample']
            self.assertEqual(samples[0]['state_diff']['resources']['life']['value'],0)
            self.assertEqual(samples[1]['state_diff'],{})
            self.assertEqual(samples[2]['state_diff']['resources']['life']['value'],1)
            self.assertEqual(rows[-1]['event'],'session_end')
            report=summarize(r.folder)
            self.assertEqual(report['samples'],3);self.assertFalse(report['gate0_passed']);self.assertIsNone(report['page_accuracy'])
            overhead=benchmark(r.folder/'events.jsonl',repeats=2)
            self.assertEqual(overhead['enabled']['events'],6)
            self.assertEqual(overhead['disabled']['events'],6)

    def test_overlay_records_changes_and_one_second_heartbeat(self):
        with tempfile.TemporaryDirectory()as tmp, closing(SessionRecorder(Path(tmp)/'session',scenario='resize'))as r:
            for t in (0,.5,1,1.5):r.overlay({'reason':'reference_expired','reference_age_s':31+t},did_show=False,enabled=True,kind='作战',now=t)
            r.overlay({'reason':'eligible'},did_show=True,enabled=True,kind='作战',now=1.6)
            r.close();rows=[json.loads(v)for v in(r.folder/'events.jsonl').read_text('utf8').splitlines()]
            events=[v for v in rows if v['event']=='overlay']
            self.assertEqual(len(events),3);self.assertTrue(events[-1]['did_show']);self.assertIsNone(events[-1]['would_show'])

    def test_surface_inventory_only_counts_visible_runtime_widgets_without_titles(self):
        app=QApplication.instance()or QApplication([])
        with tempfile.TemporaryDirectory()as tmp, closing(SessionRecorder(Path(tmp)/'session',scenario='normal'))as r:
            a=QWidget();a.setWindowTitle('PRIVATE_TITLE');a.show();hidden=QWidget();app.processEvents()
            r.surfaces(app,entry='TestPage');r.surfaces(app,entry='TestPage');a.hide();r.surfaces(app,entry='TestPage');r.close()
            raw=(r.folder/'events.jsonl').read_text('utf8');rows=[json.loads(v)for v in raw.splitlines()if json.loads(v)['event']=='surfaces']
            self.assertNotIn('PRIVATE_TITLE',raw);self.assertEqual(len(rows),2)
            self.assertEqual(len(rows[0]['visible']),len(rows[1]['visible'])+1)
            a.close();hidden.close()


if __name__=='__main__':unittest.main()
