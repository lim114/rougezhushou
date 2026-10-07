from pathlib import Path
import unittest,json,copy
from rouge.damage import calculate_damage
from rouge.catalog import catalog
from rouge.reporting import format_report
OUT=Path(__file__).parent
KEY='wisdel_summon_qualification_reference';SID='wisdel_summon_qualification'
S=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def evaluate(**kw):return calculate_damage({'operator':'char_1035_wisdel','skill':1,'skill_rank':7,'base_attack':1000,'window_seconds':3,'ghost_count':1,'ghost_casts':2,**kw})
def source_section(r):return next(s for s in r['report']['sections'] if s['id']==SID)
class IndependentWisdelSourceReview(unittest.TestCase):
 def test_second_talent_token_identity_and_cultivation_match_original_bytes(self):
  original=json.loads((OUT/'readonly-source-identities.json').read_text())['selectors']['character_table.char_1035_wisdel.talents[1]']['candidates'][0]
  data=json.loads((OUT/'draft74-independent/rouge/data/wisdel-summon-qualification-reference.json').read_text())['talent_route']
  self.assertEqual(data['token_key'],original['tokenKey']);self.assertEqual(data['name'],original['name']);self.assertEqual(data['description'],original['description']);self.assertEqual(data['prefab_key'],original['prefabKey'])
  self.assertEqual((data['unlock_elite'],data['unlock_level'],data['required_potential_rank']),(2,1,0))
 def test_s3_all_ten_original_descriptions_and_parameters_are_exact(self):
  original=json.loads((OUT/'readonly-source-identities.json').read_text())['selectors']
  data=json.loads((OUT/'draft74-independent/rouge/data/wisdel-summon-qualification-reference.json').read_text())['skill_route']
  self.assertEqual(data['override_token_key'],original['character_table.char_1035_wisdel.skills[2]']['overrideTokenKey'])
  for i,level in enumerate(data['levels']):
   raw=original[f'skill_table.skchr_wisdel_3.levels[{i}]']
   self.assertEqual(level['description'],raw['description']);self.assertEqual(S(level['values']),S({b['key']:b['value'] for b in raw['blackboard']}))
   self.assertTrue(all(fragment in raw['description'] for fragment in data['original_common_fragments']))
 def test_all_potentials_distinguish_original_qualification_from_actual_presence(self):
  for elite in [0,1,2]:
   for potential in range(1,7):
    r=evaluate(elite=elite,level=1,potential=potential);ref=r[KEY]
    self.assertEqual(ref['talent_route']['cultivation_qualified'],elite==2);self.assertEqual(ref['skill_route']['cultivation_qualified'],elite==2)
    self.assertIsNone(ref['actual_source_provenance']);self.assertFalse(ref['actual_presence_verified']);self.assertFalse(ref['actual_cast_clock_verified'])
    self.assertEqual(r['wisdel_secondary_reference']['ghost_casts_requested'],2)
 def test_unselected_s3_never_inherits_selected_s1_or_s2_rank(self):
  for skill in [1,2]:
   for rank in [1,6,7,10]:
    r=evaluate(skill=skill,skill_rank=rank);route=r[KEY]['skill_route']
    self.assertIsNone(route['selected_level_source']);self.assertFalse(route['currently_selected'])
    self.assertEqual(source_section(r)['notes'][1],'第三技能各级原文共通部分（省略数量）：立刻在攻击范围内召唤…个魂灵之影（最多存在3个，技能结束后保留）')
 def test_actual_s3_description_binds_only_its_own_rank(self):
  for rank in range(1,11):
   r=evaluate(skill=3,skill_rank=rank);level=r[KEY]['skill_route']['selected_level_source'];count=1 if rank<=6 else 2
   self.assertEqual(level['rank'],rank);self.assertEqual(level['values']['max_cnt'],count)
   self.assertTrue(source_section(r)['notes'][1].startswith(f'当前第三技能原文：立刻在攻击范围内召唤{count}个魂灵之影'))
 def test_original_routes_do_not_reinterpret_declarations_or_claim_all_paths(self):
  for elite in [0,1,2]:
   r=evaluate(elite=elite);ref=r[KEY]
   self.assertFalse(ref['declared_counts_reinterpreted']);self.assertFalse(ref['covers_all_routes'])
   self.assertGreater(r['wisdel_secondary_reference']['ghost_declared_count_damage_reference'],0)
   self.assertIn('未确定其来源归属',format_report(r));self.assertIn('不涵盖模组或藏品',format_report(r))
 def test_returned_sources_cannot_mutate_cached_source_or_catalog(self):
  before=S(catalog());r=evaluate(skill=3);expected=S(evaluate(skill=3)[KEY])
  r[KEY]['skill_route']['selected_level_source']['values']['max_cnt']=99
  r[KEY]['skill_route']['original_common_fragments'].clear();r[KEY]['talent_route']['description']='bad'
  self.assertEqual(S(evaluate(skill=3)[KEY]),expected);self.assertEqual(S(catalog()),before)
 def test_unknown_secondary_and_cast_clocks_remain_unknown(self):
  r=evaluate(skill=3);old=r['wisdel_secondary_reference']
  self.assertIsNone(old['ghost_cast_times_seconds']);self.assertIsNone(old['secondary_hit_times_seconds']);self.assertIsNone(old['explosion_expected_count'])
  self.assertFalse(old['random_independence_verified']);self.assertFalse(old['shadow_lifecycle_verified'])
  self.assertIsNone(r[KEY]['actual_source_provenance'])
