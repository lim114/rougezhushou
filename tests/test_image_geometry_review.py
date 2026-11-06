"""Coordinate mapping and viewport behavior during recognition cleanup."""
from copy import deepcopy
import unittest
import numpy as np
from rouge.viewport import map_evidence, prepare_frame

class ImageGeometryReviewTests(unittest.TestCase):
    def test_nested_evidence_stays_in_original_capture_coordinates(self):
        value={'items':[{'box':[[0,0],[1,1]],'center':(.5,.5),
                        'nested':{'label_box':[[.25,.75]],'card_position':[0,1]}},
                       {'score':.9,'text':'untouched','center':[1,2,3]}]}
        result=map_evidence(value,{'source_size':[1000,500],'content_rect':[100,50,900,450]})
        self.assertIs(result,value)
        self.assertEqual(result['items'][0],{'box':[[.1,.1],[.9,.9]],'center':[.5,.5],
            'nested':{'label_box':[[.3,.7]],'card_position':[.1,.9]}})
        self.assertEqual(result['items'][1],{'score':.9,'text':'untouched','center':[1,2,3]})

    def test_black_padding_is_removed_but_dark_interior_is_preserved(self):
        image=np.zeros((800,1200,3),np.uint8);image[20:780,30:1170]=10
        image[200:500,300:700]=0
        _,view=prepare_frame(image)
        self.assertEqual(view['content_rect'],[30,20,1170,780])
        self.assertEqual(view['source_size'],[1200,800])

    def test_client_origin_is_preserved_in_mapped_evidence(self):
        image=np.full((900,1400,3),30,np.uint8)
        _,view=prepare_frame(image,(100,50,1300,850))
        self.assertEqual(view['content_rect'],[100,50,1300,850])
        value=map_evidence({'center':[0,0]},view)
        self.assertEqual(value['center'],[100/1400,50/900])
