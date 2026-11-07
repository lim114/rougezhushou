"""Coordinate mapping and viewport behavior during recognition cleanup."""
from copy import deepcopy
import unittest
import numpy as np
from rouge.anchors import crop
from rouge.viewport import map_evidence, prepare_frame

class ImageGeometryReviewTests(unittest.TestCase):
    def test_gold_search_needs_both_life_label_and_numeric_candidate(self):
        from unittest.mock import patch
        from rouge.resource_recognition import read_resources

        image = np.zeros((600, 800, 3), dtype=np.uint8)
        box = [[.1, .1], [.2, .1], [.2, .15], [.1, .15]]
        for text in ('目标生命值', '12'):
            with self.subTest(text=text), patch('rouge.resource_recognition.cv2.cvtColor') as convert:
                self.assertEqual(read_resources(image, [{'text': text, 'confidence': .99, 'box': box}]), {})
                convert.assert_not_called()

    def test_local_crop_intersects_the_image_on_all_four_sides(self):
        image = np.arange(600*800, dtype=np.int32).reshape(600,800)
        for bounds in [(-.1,.12,-.02,.18), (.1,-.2,.2,-.1),
                       (1.01,.1,1.2,.2), (.1,1.01,.2,1.2),
                       (-.1,.1,0,.2), (.1,-.1,.2,0)]:
            with self.subTest(bounds=bounds):
                self.assertEqual(crop(image,bounds).size,0)
        for bounds, expected in [
                ((-.1,-.1,.2,.2), image[:120,:160]),
                ((.8,.8,1.1,1.1), image[480:,640:]),
                ((.1,.2,.4,.5), image[120:300,80:320])]:
            with self.subTest(bounds=bounds):
                np.testing.assert_array_equal(crop(image,bounds), expected)

    def test_fully_offscreen_resource_does_not_call_ocr(self):
        from unittest.mock import Mock
        from rouge.hud_resources import _number
        engine = Mock()
        value = _number(np.zeros((600,800,3), np.uint8), [], (-.10,.12,-.02,.18), engine)
        self.assertIsNone(value)
        engine.assert_not_called()

    def test_invalid_client_rect_is_not_replaced_by_full_frame(self):
        image=np.full((900,1400,3),30,np.uint8)
        for rect in ((-1,0,800,600),(0,0,1500,600),(100,50,100,850),
                     (0,0,319,180),(0,0,320,179)):
            with self.subTest(rect=rect),self.assertRaisesRegex(ValueError,'客户区'):
                prepare_frame(image,rect)

    def test_small_detected_content_is_not_replaced_by_client_frame(self):
        image=np.zeros((800,1200,3),np.uint8);image[300:400,400:600]=30
        with self.assertRaisesRegex(ValueError,'有效画面'):
            prepare_frame(image)

    def test_black_frame_keeps_normal_no_visible_edge_result(self):
        _,view=prepare_frame(np.zeros((600,800,3),np.uint8))
        self.assertEqual(view['content_rect'],[0,0,800,600])

    def test_nested_evidence_stays_in_original_capture_coordinates(self):
        value={'items':[{'box':[[0,0],[1,1]],'center':(.5,.5),
                        'nested':{'label_box':[[.25,.75]],'card_position':[0,1]}},
                       {'score':.9,'text':'untouched','center':[1,2,3]}]}
        result=map_evidence(value,{'source_size':[1000,500],'content_rect':[100,50,900,450]})
        self.assertIs(result,value)
        self.assertEqual(result['items'][0],{'box':[[.1,.1],[.9,.9]],'center':[.5,.5],
            'nested':{'label_box':[[.3,.7]],'card_position':[.1,.9]}})
        self.assertEqual(result['items'][1],{'score':.9,'text':'untouched','center':[1,2,3]})

    def test_black_cutoff_uses_color_channels_and_ignores_alpha(self):
        for dtype in (np.uint8, np.float32):
            for channel in range(3):
                with self.subTest(dtype=dtype, channel=channel):
                    image = np.full((240, 380, 4), 3, dtype=dtype)
                    image[:, :, 3] = 255
                    image[12:224, 21:354, channel] = 4
                    _, view = prepare_frame(image)
                    self.assertEqual(view['content_rect'], [21, 12, 354, 224])

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
