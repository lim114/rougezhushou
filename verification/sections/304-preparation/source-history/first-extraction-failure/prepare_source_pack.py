"""Prepare only selected complete public sources and exact five-row document map."""
from pathlib import Path
from hashlib import sha256
import json
import re
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CANDIDATE=HERE/'candidate'
PACK=CANDIDATE/'research/p3-curiosity-node-rules-304'
PACK.mkdir(parents=True,exist_ok=True)
raw=(HERE/'source-records.json').read_bytes()
assert sha256(raw).hexdigest()=='187ded7d38f6d8b926fbeebf9f8977d4d7ad2ad2370d5ac84d4fd71254a2cb62'
authority=json.loads(raw)
target=PACK/'selected-authority-records.json'
assert not target.exists()
target.write_bytes(raw)
assert target.read_bytes()==raw


def encoded(value):return(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def pin(path):
 raw=path.read_bytes();return{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}


text=authority['complete_ending_documentation']['text']
paragraphs=[p.strip()for p in re.split(r'\n\s*\n',text)if p.strip()]
def paragraph(starts):
 matches=[p for p in paragraphs if p.startswith(starts)]
 assert len(matches)==1,(starts,len(matches))
 value=matches[0]
 return{'selector':'main_complete_ending_blocks.end2.text','paragraph_index':paragraphs.index(value),'text':value}

general=[{'rule_id':'prior_ending_unlock','display_text':'固定资料记载：完成“强制重启”后解锁相关选项和收藏品；账户实际解锁未知。',
          'source_paragraph':paragraph('完成游戏结局')},
 {'rule_id':'three_indistinguishable_nodes','display_text':'固定资料的第Ⅴ层有3个命运所指：2个“好奇心与死”、1个“窥视箱中”，外观不能区分。不能据此替当前地图指定真节点。',
  'source_paragraph':paragraph('抵达第Ⅴ层')},
 {'rule_id':'both_sand_tables_marker','display_text':'固定资料记载：同时持有沙盘α与沙盘β，可将对应节点标记为“谜题与谜底”；实际持有与地图标记未知。',
  'source_paragraph':paragraph('同时持有两个')},
 {'rule_id':'documented_ending_limit','display_text':'固定资料描述的结局条件还包括：未持有怦然信标，完成相关作战并通过第Ⅴ层；本局是否达成未知。',
  'source_paragraph':paragraph('以不持有')}]

specs={
 ('community_group_030','community_group_030:scene:0','community_group_030:scene:0:choice:0'):{
  'role':'marker_purchase_reference','title':'标记目标位置',
  'summary':'在文献所述尚未标记的情况下，可花费50源石锭标记位置。',
  'source_paragraph':paragraph('若遭遇的是好奇心与死'),
  'requirement_text':'保留原目录条件：同时持有沙盘α与沙盘β，或访问过“窥视箱中”时，不会出现这一选项。这里只说明条件，不新增评估。',
  'resource_reference':{'resource':'gold','quantity_reference':50,'direction':'cost'},'related_stage':None,
  'not_this_choice':['unnamed_relic_reward','node_conversion','cannot_leave_after_conversion','temporary_leave_or_revisit']},
 ('community_group_030','community_group_030:scene:0','community_group_030:scene:0:choice:1'):{
  'role':'unnamed_relic_reward_reference','title':'取得一件未具名收藏品',
  'summary':'原选项记载获得1件收藏品；具体物品、完整候选池和实际领取未确认。',
  'source_paragraph':paragraph('若遭遇的是好奇心与死'),
  'requirement_text':None,'resource_reference':{'resource':'relic','quantity_reference':1,'direction':'gain'},'related_stage':None,
  'not_this_choice':['marker_purchase','node_conversion','cannot_leave_after_conversion','temporary_leave_or_revisit']},
 ('community_group_031','community_group_031:scene:0','community_group_031:scene:0:choice:0'):{
  'role':'node_conversion_reference','title':'节点变化与离开限制',
  'summary':'固定资料记载：选择后，该节点变为“混沌源阶理论”；变化后不能离开。对“作战节点”生效的效果不能在此险路恶敌中生效，资料以概念体举例。',
  'source_paragraph':paragraph('窥视箱中：选择'),
  'requirement_text':None,'resource_reference':None,
  'related_stage':{'stage_id':'ro6_b_5','title':'混沌源阶理论','role':'documented_related_fixed_material_only','reference_only':True,
                   'not_new_immediate_event_battle_link':True},
  'not_this_choice':['marker_purchase','unnamed_relic_reward','temporary_leave_or_revisit']},
 ('community_group_031','community_group_031:scene:0','community_group_031:scene:0:choice:1'):{
  'role':'temporary_leave_reference','title':'暂离与之后再次访问',
  'summary':'固定资料记载：暂离并完成该节点；节点可重复且会被标记，之后可再次访问。实际节点是否已完成、标记或可再次访问未确认。',
  'source_paragraph':paragraph('若选择【她在说什么疯话'),
  'requirement_text':None,'resource_reference':None,'related_stage':None,
  'not_this_choice':['marker_purchase','unnamed_relic_reward','node_conversion','cannot_leave_after_conversion']},
 ('community_group_031','community_group_031:scene:2','community_group_031:scene:2:choice:0'):{
  'role':'existing_battle_decision_reference','title':'已有的决战资料入口',
  'summary':'原目录写“遭遇与当前区域首领的决战”，并已关联固定关卡“混沌源阶理论”。这不是本节新增战斗链接，也不证明当前已进入战斗。',
  'source_paragraph':None,'requirement_text':None,'resource_reference':None,
  'related_stage':{'stage_id':'ro6_b_5','title':'混沌源阶理论','role':'existing_catalog_battle_reference','reference_only':True,
                   'not_new_immediate_event_battle_link':True},
  'not_this_choice':['marker_purchase','unnamed_relic_reward','temporary_leave_or_revisit']},
}
rows=[]
for original in authority['exact_five_choice_rows']:
 identity=tuple(original[k]for k in('event_id','scene_key','choice_key'))
 spec=specs[identity]
 row={k:original[k]for k in('event_id','scene_key','choice_key')}
 row.update(spec)
 row.update(original_choice_ids=list(original['complete_original_choice_candidates']),
  choice_title=original['complete_community_choice']['title'],
  community_description=original['complete_community_choice']['description'],
  community_conditional=original['complete_community_choice']['conditional'],
  primary_original_selection_unknown=original['original_choice_candidate_selection_unknown'],
  actual_node_id=None,actual_marked=None,actual_node_type=None,actual_converted=None,
  actual_revisit_available=None,actual_server_eligible=None,actual_stage_id=None,actual_original_choice_id=None)
 rows.append(row)
assert len(rows)==len(specs)==5
source_map={'schema':'curiosity-node-rules-document-map-v1','event_ids':['community_group_030','community_group_031'],
 'general_documented_rules':general,'choices':rows,
 'parameter_reference_only_feature_ids':[key for key in authority['complete_items']if key.startswith('rogue_6_end_2_')],
 'primary_candidate_boundary':'031 scene0 choice0 has two original records. end2_1 itemId is end_2_change; end2_4 itemId is null. No active record is selected or merged.',
 'source_version':'fixed primary a550f5e + fixed community 427904/440271/433770, not verified current-server execution',
 'old_battle_links_qualification_resource_named_rewards_not_reimplemented':True,
 'original_entry_gaps_unchanged':[25,57],'unparsed_notes_not_resolved_by_this_source_map':10,
 'game_actions_inventory_updates_probabilities_or_route_advice':False}
(PACK/'choice-rule-map.json').write_bytes(encoded(source_map))
(PACK/'SOURCE_SCHEMA.md').write_bytes('''# 调查记录来源合同

selected-authority-records.json逐字节复制本轮实际提取原件，字段与research/source-records相同。
完整当前event、原6choice/6scene、11FEATURE+双沙盘+bubble03共14item/relic、两版完整DOM、唯一end2全文块均保留。
choice-rule-map.json只按5个完整(event_id,scene_key,choice_key)关系映射文献结果，不恢复原入口或生成机制。

顶层event_ids只含030/031，general_documented_rules是共用背景，不能塞入每个选项的结果。
choices字段：event_id/scene_key/choice_key、role/title/summary、source_paragraph(完整end2文本中的索引及原段)、
requirement_text、resource_reference、related_stage、not_this_choice、original_choice_ids、choice_title、
community_description/community_conditional、primary_original_selection_unknown以及8个actual_*均null。
resource_reference仅原文数量(50源石锭费用或1件不具名收藏品)，不更新资源/背包，不能补完整池。
related_stage只在转换行与已有决战行出现；是手动固定资料，不能向event_battle_links添加立即转场边。
031 scene0 choice0必须保留end2_1/end2_4两个完整原候选，不选择实际原记录，不合并displayData字段。

FEATURE为配置旁证。limit/count/not_hold等参数不证明具体执行/消费/数量/附着；bubble03名字不能由编号猜出。
任何资料状态source_valid只说明固定资料，不说明本局。所有actual_*始终null，恢复后仍须手选。

完整原topic和HTML继续引用已公开300/301，不重复复制。本包由后端builder生成最终data及source-manifest，
但不得覆盖本包原件；builder必须从完整权威原件重新核对这些完整对象和DOM，再产生相同语义data。
runtime只fresh小精选记录、data和完整当前目标catalog，不能每刷新重读17MB。返回深拷贝与warm缓存完整性必需。
'''.encode('utf8'))
(PACK/'README.md').write_bytes('''# 好奇心与死 / 窥视箱中 · 固定流程资料来源

拟提供按精确选项阅读标记、节点转换、变化后不能离开和暂离再访的资料；不推荐路线、不操作游戏。
当前旧功能已包含完整目录、50锭选项的条件评估、031决战的混沌源阶理论入口。本包不重复登记它们。
所有原场景入口、实际标记/节点变化/再访、当前服务器与脚本执行仍未知；25/57、17typed和完整池缺口不变。

主页面433770的唯一end2折叠块证明文献中的3个命运所指/外观不可区分、双沙盘谜题与谜底标记、
50源石锭标记、选择后转换/离开限制和暂离再访；不是从故事或FEATURE键推断实际机制。
原topic固定a550f5e完整17,943,244字节与两版事件DOM均复用公开原件，不重复存储或新抓网络。
source-authority.json列出原始权威字节和本包小文件pins；后端最终manifest应区分build完整源和runtime精选源。

两条相同“保护证据”完整原记录分别保存，只有end2_1带change机制物品，end2_4为空；实际使用者未知。
本包是来源与候选合同，不是产品正式验收。文献文本保留PRTS署名/版本，原游戏材料权利属于原权利人。
'''.encode('utf8'))
authority_manifest={'schema':'curiosity-node-rules-source-authority-v1',
 'build_authority_files':authority['source_pins'],
 'selected_whole_records_file':'research/p3-curiosity-node-rules-304/selected-authority-records.json',
 'files':{str(p.relative_to(CANDIDATE)).replace('\\','/'):pin(p)for p in sorted(PACK.iterdir())if p.is_file()},
 'source_raw_table_or_HTML_duplicated':False,'current_server_or_callback_verified':False,
 'backend_builder_owns_final_data_and_source_manifest':True}
(PACK/'source-authority.json').write_bytes(encoded(authority_manifest))
handoff={'kind':'SECTION304_CURIOSTY_SOURCE_RESEARCH_READY_NOT_BACKEND_OR_PRODUCT_ACCEPTANCE',
 'candidate_root':str(CANDIDATE.relative_to(ROOT)).replace('\\','/'),
 'promotion_files':{str(p.relative_to(CANDIDATE)).replace('\\','/'):pin(p)for p in sorted(PACK.iterdir())if p.is_file()},
 'source_authority_files':authority['source_pins'],
 'related_stage_id':'ro6_b_5','existing_battle_entry_not_new':True,
 'complete_event_count':2,'complete_scene_count':6,'community_choice_count':5,'primary_choice_count':6,
 'feature_records_reference_only':11,'raw14_items_and_relics_complete':True,
 'source_build_extraction_actual_exit':0,'actual_source_extraction':'extract.process.exit',
 'network_tests_Qt_game_chat_Git_private_changes':False}
(HERE/'HANDOFF.json').write_bytes(encoded(handoff))
print(json.dumps({'HANDOFF':pin(HERE/'HANDOFF.json'),'promotion_files':len(handoff['promotion_files']),
 'selected_authority':pin(target),'choice_rule_map':pin(PACK/'choice-rule-map.json'),
 'only_source_preparation':True,'source_manifest_final_owned_by_backend':True},ensure_ascii=False))
