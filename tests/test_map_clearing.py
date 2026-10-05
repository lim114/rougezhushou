"""Visible clearing nodes through the agreed ScreenReader / RunState seams."""
import copy
from functools import lru_cache
from pathlib import Path
import tempfile
import unittest

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
