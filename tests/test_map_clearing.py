"""Visible clearing nodes through the agreed ScreenReader / RunState seams."""
import copy
import json
from functools import lru_cache
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from rouge.recognition import ScreenReader
from rouge.run_state import RunState

ROOT=Path(__file__).resolve().parents[1]


def sample(name):
    return cv2.imdecode(np.fromfile(ROOT/'samples/native-client'/name,dtype=np.uint8),1)


@lru_cache(maxsize=1)
def original_read():
    return ScreenReader().read(sample('exploration-map.png'))


class MapClearingTests(unittest.TestCase):
    def test_missing_ring_requires_visible_pixels_at_the_matched_grid_slot(self):
        from rouge.map_recognition import _visible_clearing_at
        image = sample('exploration-map.png')
        observation = original_read()
        font = np.median([np.ptp([pt[1] for pt in node['box']]) for node in observation['nodes']]) * image.shape[0]
        nodes = {n['id']: n for n in observation['map']['nodes']}
        center = nodes['0,2']['center']
        self.assertTrue(_visible_clearing_at(image, center, font))
        self.assertFalse(_visible_clearing_at(image, nodes['1,3']['center'], font))
        x, y = round(center[0] * image.shape[1]), round(center[1] * image.shape[0])
        half = round(font * 2)
        image[y-half:y+half, x-half:x+half] = 20
        self.assertFalse(_visible_clearing_at(image, center, font))

    def test_visible_merchant_emblem_wins_over_a_ring_when_its_label_is_covered(self):
        from rouge.map_art import ART
        from rouge.map_recognition import read_map

        # Known 1b layout. The other node labels and the ring at the merchant
        # are the detections supplied to the map reader, independent of OCR.
        types = [['', '未知的诡秘', '秘境行商', '林间空地', '险路尽头'],
                 ['林间空地', '林间空地', '林间空地', None, ''],
                 ['', '林间空地', '林间空地', '林间空地', '险路尽头']]
        image = np.full((900, 1500, 3), 30, np.uint8)
        coords = lambda row, col: (.10 + .19 * col, .18 + .29 * row)
        labels, rings = [], []
        for row, line in enumerate(types):
            for col, kind in enumerate(line):
                x,y = coords(row, col)
                if kind is None or kind == '林间空地':
                    rings.append({'center':[x,y], 'source':'可见空白圆环'})
                elif kind:
                    y += (3 if kind == '险路尽头' else 1.8) * 24/900
                    box = [[x-.03,y-12/900],[x+.03,y-12/900],[x+.03,y+12/900],[x-.03,y+12/900]]
                    labels.append({'type':kind, 'box':box, 'confidence':1.})
        assets = json.loads((ART/'sources.json').read_bytes())['sprites']
        atlas = cv2.imdecode(np.fromfile(ART/'nodes.png',dtype=np.uint8),cv2.IMREAD_UNCHANGED)
        cx,cy = coords(1,3)
        for key in ('rogue-trader', 'secret-trader', 'unknown-mystery', 'combat'):
            with self.subTest(art=key):
                s = assets[key]
                tile = atlas[s['y']:s['y']+s['height'],s['x']:s['x']+s['width']]
                tile = cv2.resize(tile,(208,184),interpolation=cv2.INTER_AREA)
                frame = image.copy()
                left,top = round(cx*1500)-104,round(cy*900)-92
                part = frame[top:top+184,left:left+208]
                alpha = tile[:,:,3:4]/255
                part[:] = part*(1-alpha) + tile[:,:,:3]*alpha
                with patch('rouge.map_recognition._rings',return_value=copy.deepcopy(rings)):
                    graph=read_map(frame, [], labels, {'config':{'zone':{'id':'zone_1'}}})
                self.assertEqual(graph['template_id'], '1b')
                nodes = {n['id']:n for n in graph['nodes']}
                if key == 'rogue-trader':
                    self.assertEqual(nodes['1,3']['observed_type'], '诡意行商')
                    self.assertEqual(nodes['1,3']['observation_source'], 'visible_node_sprite')
                    self.assertEqual(nodes['1,0']['observed_type'], '林间空地')
                else:
                    self.assertNotEqual(nodes['1,3']['observed_type'], '诡意行商')

    def test_visible_small_rings_are_clearings_without_requiring_text(self):
        graph=original_read()['map']
        self.assertEqual((graph['status'],graph['template_id']),('matched','1b'))
        nodes={n['id']:n for n in graph['nodes']}
        self.assertEqual({key for key,n in nodes.items() if n['observed_type']=='林间空地'},
                         {'0,2','1,0','1,2'})
        self.assertEqual(nodes['0,1']['observed_type'],'未知的凶戾')
        self.assertEqual(nodes['1,3']['observed_type'],'未知的诡秘')
        for key in ('0,2','1,0','1,2'):
            self.assertEqual(nodes[key]['observation_source'],'visible_clearing_ring')
            self.assertTrue(nodes[key]['visible'])

    def test_clearings_do_not_force_a_choice_between_compatible_layouts(self):
        graph=ScreenReader().read(sample('map-live-0.19-2d.png'))['map']
        self.assertEqual((graph['status'],graph['template_id']),('ambiguous',None))
        self.assertEqual({c['id'] for c in graph['candidate_templates']},{'2b','2d'})
        self.assertEqual(graph['nodes'],[])
        self.assertEqual(graph['edges'],[])

    def test_wide_detail_page_reads_visible_clearings_around_overlay(self):
        graph=ScreenReader().read(sample('map-template-node-detail.png'),client_rect=[2,45,2050,1125])['map']
        self.assertEqual((graph['status'],graph['template_id']),('matched','1c'))
        self.assertEqual({n['id'] for n in graph['nodes'] if n['observed_type']=='林间空地'},
                         {'1,1','1,2','2,1','2,3'})

    def test_resized_and_translated_content_preserves_clearing_identity(self):
        source=sample('exploration-map.png')
        for width,height,left,top in ((960,720,210,72),(1920,1440,0,0)):
            with self.subTest(width=width,offset=(left,top)):
                image=np.zeros((height+top*2,width+left*2,3),np.uint8)
                image[top:top+height,left:left+width]=cv2.resize(source,(width,height),interpolation=cv2.INTER_AREA)
                graph=ScreenReader().read(image)['map']
                self.assertEqual((graph['status'],graph['template_id']),('matched','1b'))
                self.assertEqual({n['id'] for n in graph['nodes'] if n['observed_type']=='林间空地'},
                                 {'0,2','1,0','1,2'})
                center=next(n['center'] for n in graph['nodes'] if n['id']=='0,2')
                self.assertAlmostEqual(center[0],(left+.5*width)/image.shape[1],delta=.012)
                self.assertAlmostEqual(center[1],(top+.223*height)/image.shape[0],delta=.012)

    def test_hidden_icon_with_unreadable_label_is_not_a_clearing(self):
        # Cover only text; both purple and teal full-size icons remain visible.
        for key,(left,top,right,bottom) in (('0,1',(432,312,592,351)),('1,3',(1003,602,1183,643))):
            with self.subTest(node=key):
                image=sample('exploration-map.png');image[top:bottom,left:right]=15
                graph=ScreenReader().read(image)['map']
                if graph['status']=='matched':
                    node=next(n for n in graph['nodes'] if n['id']==key)
                    self.assertNotEqual(node['observed_type'],'林间空地')
                self.assertFalse(any(n['id']==key and n['observed_type']=='林间空地' for n in graph['nodes']))

    def test_occluded_ring_is_not_inferred_from_template_or_history(self):
        image=sample('exploration-map.png')
        image[224:305,753:846]=15
        graph=ScreenReader().read(image)['map']
        if graph['status']=='matched':
            node=next(n for n in graph['nodes'] if n['id']=='0,2')
            self.assertIsNone(node['observed_type'])
            self.assertFalse(node['visible'])
        self.assertFalse(any(n['id']=='0,2' and n['observed_type']=='林间空地' for n in graph['nodes']))

    def test_cropped_map_does_not_invent_current_clearings(self):
        image=sample('exploration-map.png')
        image[:,650:]=15
        graph=ScreenReader().read(image)['map']
        self.assertNotEqual(graph['status'],'matched')
        self.assertEqual(graph['nodes'],[])

    def test_clearings_preserve_prior_type_budget_without_inventing_visits(self):
        observed=copy.deepcopy(original_read()['run'])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'run.json';run=RunState(path);at=run.state['started_at']+1
            run.apply(observed,at)
            nodes={n['id']:n for n in run.state['maps']['zone_1']['nodes']}
            self.assertFalse(nodes['0,2'].get('visited',False))
            self.assertFalse(nodes['1,2'].get('visited',False))
            self.assertNotIn('remembered_type',nodes['0,2'])
            # The current player marker independently proves the start visit.
            self.assertTrue(nodes['1,0']['visited'])
            revealed=copy.deepcopy(observed)
            prior=next(n for n in revealed['map']['nodes'] if n['id']=='0,2')
            prior.update(observed_type='诡意行商',observation_source='visible_node_label')
            run.apply(revealed,at+1)
            run.apply(observed,at+2)
            current=run.state['maps']['zone_1']
            cleared=next(n for n in current['nodes'] if n['id']=='0,2')
            self.assertEqual(cleared['observed_type'],'林间空地')
            self.assertEqual(cleared['remembered_type'],'诡意行商')
            self.assertTrue(cleared['visited'])
            self.assertEqual(current['generation_budget']['诡意行商']['known_total'],2)
            self.assertEqual(current['generation_budget']['诡意行商']['remaining_capacity'],0)
            partial=copy.deepcopy(observed);partial['map']={'status':'insufficient','zone_id':'zone_1'}
            run.apply(partial,at+3)
            reloaded=RunState(path)
            saved=next(n for n in reloaded.state['maps']['zone_1']['nodes'] if n['id']=='0,2')
            self.assertEqual(saved['remembered_type'],'诡意行商')
            self.assertTrue(saved['visited'])
            self.assertEqual(reloaded.state['maps']['zone_1']['generation_budget']['诡意行商']['known_total'],2)
            reloaded.reset()
            self.assertEqual(reloaded.state['maps'],{})


if __name__=='__main__':unittest.main()
