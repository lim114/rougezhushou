"""Public reader replays; sizes are test cases, never layout profiles."""
import unittest
from pathlib import Path
import cv2,numpy as np
from rouge.recognition import ScreenReader

ROOT=Path(__file__).resolve().parents[1]

class DynamicResolutionTests(unittest.TestCase):
    def test_physical_client_rect_excludes_windows_caption_before_black_padding(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-info-trade.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        observed=ScreenReader().read(image,client_rect=[2,45,2050,1125])
        self.assertEqual(observed['run']['config']['difficulty']['value'],10)
        self.assertEqual(observed['run']['config']['squad']['id'],'rogue_6_band_20')
        self.assertEqual(observed['viewport']['content_rect'],[2,45,2050,1125])

    def test_same_reader_relocates_content_on_every_resize_and_padding_change(self):
        source=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-info-trade.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        reader=ScreenReader()
        for width,left,top in [(1337,0,0),(1771,123,211),(1009,43,71)]:
            with self.subTest(width=width):
                height=round(source.shape[0]*width/source.shape[1])
                content=cv2.resize(source,(width,height),interpolation=cv2.INTER_AREA)
                frame=cv2.copyMakeBorder(content,top,top,left,left,cv2.BORDER_CONSTANT,value=0)
                observed=reader.read(frame)
                self.assertEqual(observed['run']['config']['difficulty']['value'],10)
                self.assertEqual(observed['run']['config']['squad']['id'],'rogue_6_band_20')
                self.assertEqual(observed['size'],[frame.shape[1],frame.shape[0]])
                self.assertEqual(observed['viewport']['content_rect'],[left,top,left+width,top+height])

    def test_small_window_retains_all_three_held_items_and_count(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-relic-multicard-closed.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        image=cv2.resize(image,(1366,750),interpolation=cv2.INTER_AREA)
        run=ScreenReader().read(image)['run']
        self.assertEqual(run['relics']['count'],3)
        self.assertEqual(set(run['relics']['ids']),{'rogue_6_relic_fight_26','rogue_6_relic_cargo_1'})
        self.assertEqual(run['tactical_tools']['ids'],['rogue_6_active_tool_5'])

    def test_operator_cultivation_survives_client_crop_resize_and_letterboxing(self):
        reader=ScreenReader()
        for name,identity,potential,ranks in [('operator-mechanist.png','mechanist',6,{1:10,2:9,3:10}),
                ('operator-silverash.png','silverash',1,{1:7,2:7,3:10})]:
            with self.subTest(operator=identity):
                source=cv2.imdecode(np.fromfile(ROOT/'samples/native-client'/name,dtype=np.uint8),cv2.IMREAD_COLOR)
                content=source[45:-2,2:-2]
                height=913;width=round(content.shape[1]*height/content.shape[0])
                resized=cv2.resize(content,(width,height),interpolation=cv2.INTER_AREA)
                frame=cv2.copyMakeBorder(resized,83,67,37,71,cv2.BORDER_CONSTANT,value=0)
                operator=reader.read(frame)['operator']
                self.assertEqual(operator['id'],identity)
                self.assertEqual(operator['fields']['potential'],potential)
                self.assertEqual(operator['fields']['elite'],2)
                self.assertEqual(operator['skill_ranks'],ranks)
                self.assertEqual(operator['fields']['level'],90 if identity=='mechanist' else 60)
                self.assertEqual(operator['fields']['trust_display'],113 if identity=='mechanist' else 200)
                self.assertEqual(operator['fields']['module_level'],3 if identity=='mechanist' else 0)
                self.assertEqual(operator['fields']['selected_skill'],1 if identity=='mechanist' else 3)
