import unittest
from copy import deepcopy
import cv2
import numpy as np
from rouge.software_pointer import SoftwarePointer
from rouge.player_game_map import payload
from tests.test_overlay_display import labelled


class SoftwarePointerTests(unittest.TestCase):
    def test_fast_crossing_recovers_only_one_confirmed_frozen_pointer(self):
        seed = self.image()
        scene = np.zeros((400, 800, 3), np.uint8)
        scene[160:310, 420:620] = seed[40:190, 60:260]
        tracker = SoftwarePointer()
        tracker.locate(seed, (100, 80))
        self.assertEqual(tracker.locate(scene, (750, 350), may_learn=False),
                         [458, 198, 513, 262])
        other = SoftwarePointer()
        other.locate(seed, (100, 80))
        scene[160:310, 200:400] = seed[40:190, 60:260]
        self.assertIsNone(other.locate(scene, (750, 350), may_learn=False))

    def image(self):
        image=np.zeros((250,350,3),np.uint8)
        cv2.fillPoly(image,[np.array([[100,80],[118,100],[126,95],[150,125],[145,139],[117,127],[111,108]])],(220,220,220))
        return image

    def test_locates_visible_pixels_and_tracks_frozen_cursor_without_native_point(self):
        tracker=SoftwarePointer();image=self.image();box=tracker.locate(image,(100,80))
        self.assertIsNotNone(box);self.assertEqual(tracker.locate(image,None),box)
        self.assertIsNone(tracker.locate(np.zeros_like(image),None))

    def test_mouse_position_alone_or_white_text_does_not_provide_exclusion(self):
        image=np.zeros((250,350,3),np.uint8);cv2.putText(image,'NODE',(100,100),cv2.FONT_HERSHEY_SIMPLEX,.6,(255,255,255))
        self.assertIsNone(SoftwarePointer().locate(image,(100,80)))
        self.assertIsNone(SoftwarePointer().locate(image,None))

    def test_visible_system_pointer_does_not_teach_but_can_locate_frozen_game_pointer(self):
        tracker=SoftwarePointer();image=self.image()
        self.assertIsNone(tracker.locate(image,(100,80),may_learn=False))
        tracker.locate(image,(100,80))
        moved=np.zeros_like(image);moved[100:200,210:310]=image[60:160,80:180]
        self.assertIsNotNone(tracker.locate(moved,(230,120),may_learn=False))

    def frames(self):
        a,b,s=labelled();node=deepcopy(a['observation']['map']['nodes'][0]);node.update(id='extra',center=[.9,.65],label_box=[[.85,.63],[.92,.63],[.92,.68],[.85,.68]])
        a['observation']['map']['nodes'].append(node)
        return a,b,s

    def test_occluded_label_is_omitted_only_with_frame_bound_pointer_evidence(self):
        a,b,s=self.frames();b['image'][380:404,150:220]=255
        self.assertIsNone(payload(a,b,s,'one',100))
        b['pointer_bounds']=[150,380,220,404];d={}
        self.assertIsNotNone(payload(a,b,s,'one',100,diagnostics=d));self.assertEqual(d['cursor_occluded_anchors'],1)
        self.assertEqual(d['anchor_count'],4)
        a['pointer_bounds']=b.pop('pointer_bounds')
        self.assertIsNotNone(payload(a,b,s,'one',100))

    def test_insufficient_unoccluded_nodes_title_and_other_changes_still_reject(self):
        a,b,s=labelled();b['pointer_bounds']=[150,380,220,404];d={}
        self.assertIsNone(payload(a,b,s,'one',100,diagnostics=d));self.assertEqual(d['reason'],'anchors_insufficient')
        a,b,s=self.frames();b['pointer_bounds']=[150,380,220,404];b['image'][380:404,410:480]=0
        self.assertIsNone(payload(a,b,s,'one',100))
        a,b,s=self.frames();b['pointer_bounds']=[0,0,1000,100];b['image'][65,400]=61
        self.assertIsNone(payload(a,b,s,'one',100))

if __name__=='__main__':unittest.main()
