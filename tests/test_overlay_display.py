"""Display-only overlay fixes; original freshness and identity limits remain."""
from pathlib import Path
from types import SimpleNamespace
from copy import deepcopy
from unittest.mock import patch
import json,tempfile,time,unittest
import numpy as np
from PySide6.QtWidgets import QApplication,QWidget
from rouge.player_game_map import payload,GameMapOverlay
from rouge.player_overlay_settings import OverlayPreferences
from rouge.viewport import map_evidence
from tests.test_player_feature_424 import fixture
from tests import test_sampling_flow as flow


class OverlayPreferenceTests(unittest.TestCase):
    def test_missing_preference_defaults_on_without_creating_file(self):
        with tempfile.TemporaryDirectory()as d:
            path=Path(d)/'overlay.json';settings=OverlayPreferences(path)
            self.assertTrue(settings.enabled);self.assertFalse(path.exists())

    def test_explicit_false_and_unknown_keys_survive_load_and_save(self):
        with tempfile.TemporaryDirectory()as d:
            path=Path(d)/'overlay.json';path.write_text(json.dumps({'enabled':False,'other':{'keep':7}}),'utf8')
            before=path.read_bytes();settings=OverlayPreferences(path)
            self.assertFalse(settings.enabled);self.assertEqual(path.read_bytes(),before)
            self.assertEqual(settings.save(True),'')
            self.assertEqual(json.loads(path.read_bytes()),{'enabled':True,'other':{'keep':7}})
            settings.save(False);self.assertFalse(OverlayPreferences(path).enabled)

    def test_unreadable_preference_is_not_overwritten(self):
        for raw in ('{','[]','{"enabled":"false"}'):
            with self.subTest(raw=raw),tempfile.TemporaryDirectory()as d:
                path=Path(d)/'overlay.json';path.write_text(raw,'utf8');settings=OverlayPreferences(path)
                self.assertFalse(settings.enabled);self.assertTrue(settings.save(True))
                self.assertEqual(path.read_text('utf8'),raw)


def labelled():
    reference,current,snapshot=fixture();rng=np.random.default_rng(17)
    for i,node in enumerate(reference['observation']['map']['nodes']):
        x=150+i*260;y=380;patch=rng.integers(30,220,(24,70,3),dtype=np.uint8)
        reference['image'][y:y+24,x:x+70]=patch
        node['label_box']=[[x/1000,y/600],[(x+70)/1000,y/600],[(x+70)/1000,(y+24)/600],[x/1000,(y+24)/600]]
    current['image']=reference['image'].copy()
    return reference,current,snapshot


class OverlayAnchorTests(unittest.TestCase):
    def test_animated_centers_do_not_invalidate_stable_labels(self):
        a,b,s=labelled();b['image'][290:310,240:260]=180;diagnostics={}
        self.assertIsNotNone(payload(a,b,s,'one',100,diagnostics=diagnostics))
        self.assertEqual(diagnostics['anchor_strategy'],'node_labels')

    def test_small_background_noise_is_accepted_but_changed_label_is_rejected(self):
        a,b,s=labelled();b['image'][380:404,150:220]=np.clip(b['image'][380:404,150:220].astype(int)+1,0,255).astype(np.uint8)
        self.assertIsNotNone(payload(a,b,s,'one',100))
        b['image'][380:404,150:220]=np.flip(b['image'][380:404,150:220],axis=1)
        self.assertIsNone(payload(a,b,s,'one',100))

    def test_dimming_title_change_and_original_age_limits_still_reject(self):
        a,b,s=labelled();b['image'][380:404,150:220]//=2
        self.assertIsNone(payload(a,b,s,'one',100))
        a,b,s=labelled();b['image'][65,400]=61
        self.assertIsNone(payload(a,b,s,'one',100))
        for target,at,reason in(('reference',69,'reference_expired'),('current',97,'current_frame_expired')):
            a,b,s=labelled();(a if target=='reference'else b)['captured_at']=at;diagnostics={}
            self.assertIsNone(payload(a,b,s,'one',100,diagnostics=diagnostics));self.assertEqual(diagnostics['reason'],reason)

    def test_label_background_brightness_shift_retains_shape_and_contrast(self):
        a,b,s=labelled();b['image'][380:404,150:220]+=8
        self.assertIsNotNone(payload(a,b,s,'one',100))

    def test_slow_glow_does_not_hide_same_text_but_displaced_text_does(self):
        a,b,s=labelled()
        glow=np.linspace(0,18,70,dtype=np.float32)[None,:,None]
        b['image'][380:404,150:220]=(b['image'][380:404,150:220]+glow).astype(np.uint8)
        self.assertIsNotNone(payload(a,b,s,'one',100))
        b['image'][380:404,150:220]=np.roll(b['image'][380:404,150:220],3,axis=1)
        self.assertIsNone(payload(a,b,s,'one',100))

    def test_geometry_and_foreground_still_reject_with_matching_labels(self):
        a,b,s=labelled();b['client_rect']=[0,0,960,540]
        self.assertIsNone(payload(a,b,s,'one',100))
        a,b,s=labelled();s['foreground_on_game']=False
        self.assertIsNone(payload(a,b,s,'one',100))

    def test_label_boxes_map_to_source_coordinates_once(self):
        value={'map':{'nodes':[{'label_box':[[.2,.3],[.4,.3],[.4,.5],[.2,.5]]}]}}
        map_evidence(value,{'source_size':[1000,600],'content_rect':[100,60,900,540]})
        self.assertEqual(value['map']['nodes'][0]['label_box'][0],[.26,.34])

    def test_unfiltered_layer_can_show_existing_header_without_node_type_choice(self):
        app=QApplication.instance()or QApplication([]);reference,current,snapshot=fixture();companion=QWidget()
        companion.hidden_windows=None;companion.game_binding=SimpleNamespace(api=SimpleNamespace(read=lambda target:snapshot),target=lambda:reference['target'])
        owner=SimpleNamespace(map_overlay_reference=reference,closing=False,run=SimpleNamespace(state={'id':'one','maps':{},'config':{}}),capture=SimpleNamespace(buffer=SimpleNamespace(latest=lambda:current)))
        overlay=GameMapOverlay(companion,owner);overlay.timer.stop()
        try:
            with patch('rouge.player_game_map.time.time',return_value=100):overlay.set_enabled(True)
            app.processEvents();self.assertTrue(overlay.surface.isVisible());self.assertIsNone(overlay.kind)
            with patch('rouge.player_game_map.time.time',return_value=103):overlay.tick()
            self.assertFalse(overlay.surface.isVisible())
        finally:overlay.close();companion.close()


class OverlaySamplingTests(unittest.TestCase):
    setUpClass=classmethod(flow.SamplingFlowTests.setUpClass.__func__)
    setUp=flow.SamplingFlowTests.setUp
    offer=flow.SamplingFlowTests.offer
    wait_for=flow.SamplingFlowTests.wait_for

    def test_ambiguous_same_zone_keeps_real_reference_but_other_page_replaces_it(self):
        w=self.window;at=time.time();image=np.zeros((30,40,3),np.uint8)
        old={'captured_at':at-3,'observation':{'page':'exploration','map':{'zone_id':'z','status':'matched'}}}
        w.map_overlay_reference=old
        for page,zone,status,retain in [('exploration','z','ambiguous',True),('exploration','z','insufficient',True),('exploration','other','ambiguous',False),('inventory','z','ambiguous',False)]:
            with self.subTest(page=page,zone=zone,status=status):
                w.map_overlay_reference=old;at+=1
                frame={'captured_at':at,'image':image}
                w.sample_received((image,{'page':page,'nodes':[],'map':{'zone_id':zone,'status':status},'captured_at':at,'_overlay_frame':frame}))
                if retain:self.assertIs(w.map_overlay_reference,old)
                else:self.assertEqual(w.map_overlay_reference['captured_at'],at)

    def test_saved_off_stays_off_on_actual_compact_startup(self):
        from rouge import app as module
        path=module.ROOT/'.local/player-map-overlay.json';path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('{"enabled":false,"keep":3}','utf8');before=path.read_bytes()
        self.window.show_compact();c=self.window.compact_window
        self.assertFalse(c.map_overlay_enabled.isChecked());self.assertFalse(c.game_overlay.enabled)
        self.assertEqual(path.read_bytes(),before)

    def test_static_map_refresh_takes_fresh_latest_without_fabricating_timestamp(self):
        w=self.window;w.show_compact();w.compact_window.game_overlay.timer.stop();self.release.set()
        stamp=time.time();self.offer(20,stamp);w.capture.buffer.take(force=True)
        self.assertEqual(w.capture.stats()['pending'],0)
        w.map_overlay_reference={'captured_at':stamp-21,'observation':{'page':'exploration','map':{'status':'matched'}}}
        w.auto.blockSignals(True);w.auto.setChecked(True);w.auto.blockSignals(False)
        with patch.object(w.capture,'next_frame',wraps=w.capture.next_frame)as take:
            w.sample_now(automatic=True);self.wait_for(lambda:len(self.seen)==1 and not w.busy)
            self.assertTrue(take.call_args_list[0].kwargs['force']);self.assertTrue(take.call_args_list[0].kwargs['prefer_latest'])
        self.assertEqual(w.observation['captured_at'],stamp)

    def test_disabled_overlay_does_not_force_static_repeat(self):
        w=self.window;w.show_compact();w.compact_window.game_overlay.timer.stop();w.compact_window.game_overlay.set_enabled(False)
        stamp=time.time();self.offer(20,stamp);w.capture.buffer.take(force=True)
        w.map_overlay_reference={'captured_at':stamp-21,'observation':{'page':'exploration','map':{'status':'matched'}}}
        w.auto.blockSignals(True);w.auto.setChecked(True);w.auto.blockSignals(False)
        with patch.object(w.capture,'next_frame',wraps=w.capture.next_frame)as take:w.sample_now(automatic=True)
        self.assertFalse(take.call_args.kwargs['force']);self.assertFalse(self.seen)

    def test_repeated_map_refresh_does_not_starve_short_page_backfill(self):
        w=self.window;w.show_compact();w.compact_window.game_overlay.timer.stop();self.release.set()
        stamp=time.time();original=w.reader.read
        def incomplete(image,**kwargs):
            original(image,**kwargs)
            return {'page':'exploration','nodes':[],'map':{'zone_id':'z','status':'insufficient'}}
        w.reader.read=incomplete
        w.map_overlay_reference={'captured_at':stamp-21,'observation':{'page':'exploration','map':{'zone_id':'z','status':'matched'}}}
        for value in(20,40,60,80):self.offer(value,stamp)
        w.auto.setChecked(True);self.wait_for(lambda:len(self.seen)==4 and not w.busy)
        self.assertEqual(self.seen,[80,20,60,40])

if __name__=='__main__':unittest.main()
