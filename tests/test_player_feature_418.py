import unittest
from unittest.mock import patch
import numpy as np
from PySide6.QtWidgets import QApplication,QWidget
from rouge.player_shop_hover import ShopNameReader
from rouge.player_source_cards import SourceCards
from tests.test_player_feature_417 import shop_fixture
class HoverReuseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def test_text_reused_only_when_all_header_pixels_unchanged(self):
  calls=[];reader=ShopNameReader(lambda *a,**k:(calls.append(1)or shop_fixture(),None));image=np.zeros((600,800,3),np.uint8)
  first=reader.identify(image,(245,170));second=reader.identify(image,(345,170));self.assertNotEqual(first['id'],second['id']);self.assertEqual(len(calls),1)
  image[120,300]=1;reader.identify(image,(245,170));self.assertEqual(len(calls),2)
  reader.cached['at']-=31;reader.identify(image,(245,170));self.assertEqual(len(calls),3)
  reader.identify(np.zeros((650,800,3),np.uint8),(245,170));self.assertEqual(len(calls),4)
 def test_changed_shop_anchor_invalidates_and_nonshop_not_cached(self):
  calls=[];raw=shop_fixture();reader=ShopNameReader(lambda *a,**k:(calls.append(1)or raw,None));image=np.zeros((600,800,3),np.uint8)
  self.assertIsNotNone(reader.identify(image,(245,170)));image[10,600]=1;raw=[];self.assertIsNone(reader.identify(image,(245,170)));self.assertFalse(reader.is_shop);self.assertIsNone(reader.cached);self.assertEqual(len(calls),2)
 def test_long_cards_have_plain_wrapped_labels_and_preserve_identity(self):
  card=SourceCards();chosen=[];card.poolChosen.connect(chosen.append)
  try:
   row={'id':'exact','title':'很长的收藏品来源名称，需要在窄窗口中完整显示','frequency':'可作为交换提供物，并非奖励池','counts':'','version':'dlc1'};card.install({'pools':[row,row],'nodes':[]});card.resize(390,420);card.show();self.gui.processEvents()
   self.assertTrue(all(b.caption.wordWrap()for b in card.buttons));card.buttons[0].click();self.assertEqual(chosen,['exact']);self.assertLessEqual(card.horizontalScrollBar().maximum(),0)
  finally:card.close()
