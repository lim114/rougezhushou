from hashlib import sha1,sha256
import unittest
from unittest.mock import patch
from rouge.player_enemy_search import matches
from rouge import current_battle_reference as battle,enemy_portrait_supplement as supplement

class EnemyTextLookup(unittest.TestCase):
 def test_search_only_explicit_name_description_and_handbook_text(self):
  row={'name':'测试敌人','description':'不能被沉默','abilities':['进入隐匿状态'],'tier':'BOSS','key':'opaque-id'}
  self.assertTrue(matches(row,'沉默'));self.assertTrue(matches(row,'隐匿'))
  self.assertFalse(matches(row,'BOSS'));self.assertFalse(matches(row,'opaque-id'))
 def test_negative_sentence_is_text_match_not_a_silence_qualification(self):
  self.assertTrue(matches({'name':'测试','description':'不能被沉默'},'沉默'))
 def test_empty_and_invalid_queries_do_not_invent_hidden_mechanism(self):
  self.assertTrue(matches({'name':'测试'},''));self.assertFalse(matches(None,'测试'));self.assertFalse(matches({'name':'测试'},'尚未公开的机制'))

class ExactPortraitRecovery(unittest.TestCase):
 def enemy(self):return next(e for e in battle.stage_reference('ro6_b_5_b')['enemies']if e['id']=='enemy_1250_lyengs_2')
 def test_original_absent_portrait_recovers_only_exact_original_blob(self):
  enemy=self.enemy();self.assertIsNone(enemy['portrait']);raw=battle.picture_for_enemy(enemy)
  self.assertEqual(len(raw),42983);self.assertEqual(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'b63a8976b894adec953e232076c7ed792ec1a172')
  self.assertEqual(sha256(raw).hexdigest(),'1043584274f60a9b856fe7355cc332280494d8d132802d5a35a3d09a666ccfb8')
 def test_similar_or_stripped_identity_never_borrows_picture(self):
  for identity in('enemy_1250_lyengs','enemy_1250_lyengs_2_a','unknown'):
   self.assertIsNone(supplement.portrait({'id':identity,'name':self.enemy()['name']}))
 def test_unverified_book_and_corrupt_original_remain_missing(self):
  with patch.object(supplement,'BOOK_SHA256','invalid'):self.assertIsNone(battle.picture_for_enemy(self.enemy()))
  enemy=self.enemy();enemy['portrait']={'file':'invalid-original'};self.assertIsNone(battle.picture_for_enemy(enemy))
 def test_existing_enemy_metadata_and_numeric_unknowns_unchanged(self):
  enemy=self.enemy();self.assertIsNone(enemy['expected_stats']);self.assertIsNone(enemy['actual_count']);self.assertIsNone(enemy['portrait'])

if __name__=='__main__':unittest.main()
