"""Only a qualified current map may publish before the inventory matcher."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import numpy as np

from rouge.recognition import ScreenReader
from rouge.player_map_acceptance import fixtures


class MapProgressTests(unittest.TestCase):
    def test_qualified_map_precedes_icons_with_unchanged_final_observation(self):
        image=np.full((600,1000,3),80,np.uint8)
        viewport={'source_size':[1000,600],'content_rect':[0,0,1000,600],
                  'analysis_size':[1000,600],'scale':1.,'coordinate_space':'source_frame_normalized'}
        graph=deepcopy(fixtures()[0][0]);graph['status']='matched'
        names=['收藏品','目标生命值','指挥等级','零件箱','未知的凶戾']
        raw=[([[10+i*100,10],[80+i*100,10],[80+i*100,30],[10+i*100,30]],name,.99)
             for i,name in enumerate(names)]
        config={'difficulty':{'value':5}}
        for mode in ('matched','insufficient','shop','expanded'):
            with self.subTest(mode=mode):
                progress=[];order=[];reader=ScreenReader()
                current=deepcopy(graph);current['status']='insufficient' if mode=='insufficient' else 'matched'
                rows=raw+([([[10,40],[80,40],[80,60],[10,60]],'收起',.99)] if mode=='expanded' else [])
                def icons(*args,**kwargs):order.append('icons');return []
                def publish(observation):order.append('map');progress.append(observation)
                with patch('rouge.recognition.read_operator',return_value=None), \
                     patch('rouge.recognition.read_module_page',return_value=None), \
                     patch('rouge.player_shop_hover.shop_snapshot',return_value={'items':[]} if mode=='shop' else None), \
                     patch('rouge.recognition.read_node_content',return_value=None), \
                     patch('rouge.recognition.read_map',side_effect=lambda *args:deepcopy(current)), \
                     patch('rouge.run_recognition.read_config',return_value=config), \
                     patch('rouge.run_recognition.read_resources',return_value={}), \
                     patch('rouge.run_recognition.near_number',return_value=3), \
                     patch('rouge.run_recognition.match_held_icons',side_effect=icons):
                    expected=reader._interpret(image,viewport,rows,lambda name:None,{})
                    order.clear()
                    actual=reader._interpret(image,viewport,rows,lambda name:None,{},on_map=publish)
                expected.pop('observed_at');actual.pop('observed_at')
                self.assertEqual(actual,expected)
                if mode=='matched':
                    self.assertEqual(order,['map','icons'])
                    self.assertEqual(progress[0]['map'],actual['map'])
                    self.assertEqual(progress[0]['map_config'],actual['run']['config'])
                    self.assertIsNone(progress[0]['run'])
                    self.assertIsNot(progress[0]['map'],actual['map'])
                else:self.assertFalse(progress)


if __name__=='__main__':unittest.main()
