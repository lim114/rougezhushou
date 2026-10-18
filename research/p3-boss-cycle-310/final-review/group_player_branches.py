"""Add grouped reading proposal; keep the first review/HANDOFF bytes intact."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import json

OUT=Path(__file__).parent;SOURCE=OUT.parent/'p3-310-boss-research'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def pin(p):return{'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def dump(n,o):(OUT/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
initial=read(OUT/'HANDOFF.json')
for n,p in initial['files'].items():assert pin(OUT/n)==p
data=read(OUT/'player-reading-data-proposal.json');base=deepcopy(data)
data['overview_notice']='这是“混沌源阶理论”两名首领及模块的固定文献阅读。主交替条件链、首次半血变化、终点与退场、模块结果是四组不同条件，不是七个必然依次发生的阶段；不读取或推断当前战斗状态。'
groups=[{'id':'alternating_conditions','name':'主交替条件链','step_ids':['lorentz_knockdown','cube_activate','module_clear_gate','cube_deactivate']},
 {'id':'first_half_hp_change','name':'首次半血的独立变化','step_ids':['cube_first_half_hp']},
 {'id':'endpoint_and_exit','name':'终点、被摧毁与退场分支','step_ids':['lorentz_endpoint','cube_exit']},
 {'id':'module_outcomes','name':'模块存活完成与致命伤害分支','step_ids':[]}]
mapping={s:g['id']for g in groups for s in g['step_ids']}
for f in data['documentary_flow']:f['flow_group']=mapping[f['step_id']]
data['flow_groups']=groups
byid={f['step_id']:f for f in data['documentary_flow']}
flowtopic=next(t for t in data['topics']if t['id']=='flow')
paragraphs=['以下按触发条件分组阅读，不表示这些事情会依次发生，也不代表实际对局会走完所有分支。']
for group in groups:
 paragraphs.append(group['name'])
 if group['step_ids']:paragraphs.extend(byid[i]['text']for i in group['step_ids'])
 else:
  paragraphs.extend([
   '模块可被我方治疗且持续自损。若存活到“全域信息失真”技能完成，文献记载对全场我方造成少量法术伤害，令源阶方受到其自身最大生命值8%的无来源真实伤害，再强制击杀模块自身。实际完成时间和本次扣血不作预测。',
   '模块若受到足以致命的伤害，则另有按当时模块攻击力100%造成全场法术伤害的文献条款；不能把这条自动叠在技能完成后的强制击杀上。具体比例、延迟及技力限制见模块页的原文说明。'])
flowtopic['paragraphs']=paragraphs
flowtopic['source_refs'].extend(deepcopy(data['module_success_source_refs']))
module_doc=read(OUT/'complete-visible-cards-and-tooltips.json')['module']
flowtopic['source_refs'].append({'source':module_doc['source'],'source_selector':module_doc['source_selector'],
 'location':module_doc['location'],'quote':'受到足以致命的伤害时，记录自身当前攻击力，随后（使用敌方阵营索敌）使全场范围内的所有我方单位（中点判定，不受迷彩制约）延迟0.8秒后受到记录攻击力100%的预计算无来源无途径法术普通伤害。'})
data['not_a_linear_timeline']=True
dump('player-reading-data-proposal-grouped.json',data)
dump('grouping-amendment.json',{'kind':'GROUPING_ONLY_AMENDMENT_TO_PREVENT_FALSE_LINEAR_ORDER','original_handoff':pin(OUT/'HANDOFF.json'),
 'original_proposal':pin(OUT/'player-reading-data-proposal.json'),'grouped_proposal':pin(OUT/'player-reading-data-proposal-grouped.json'),
 'changes':['overview_notice明确四组非线性条件','documentary_flow逐条增加flow_group','新增flow_groups',
  'flow主题四组中文组头，模块结果独立列出并补来源','新增not_a_linear_timeline=true'],
 'all_skills_unchanged':data['skills']==base['skills'],
 'other_three_topics_unchanged':data['topics'][1:]==base['topics'][1:],
 'seven_clause_texts_and_source_refs_unchanged':all({k:v for k,v in new.items()if k!='flow_group'}==old for new,old in zip(data['documentary_flow'],base['documentary_flow'])),
 'source_review_unchanged':pin(OUT/'source-review.json')==initial['files']['source-review.json']})
for n,p in initial['files'].items():assert pin(OUT/n)==p
frozen=read(SOURCE/'HANDOFF.json');assert all(pin(SOURCE/n)==p for n,p in frozen['files'].items())
files={p.name:pin(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='HANDOFF_FINAL.json'}
dump('HANDOFF_FINAL.json',{'kind':'FINAL310_SOURCE_REVIEW_ONLY_NOT_IMPLEMENTATION_OR_VALIDATION','files':files,
 'read_first':'source-review.json','player_wording':'player-reading-data-proposal-grouped.json',
 'grouping_amendment':'grouping-amendment.json','complete_visible_sources':'complete-visible-cards-and-tooltips.json',
 'frozen_input_handoff':{'file':'.cache/p3-310-boss-research/HANDOFF.json',**pin(SOURCE/'HANDOFF.json')},
 'original_review_handoff_preserved':pin(OUT/'HANDOFF.json'),
 'frozen_source_before_after_same':True,'no_production_Git_Qt_tests_private_state_game_or_chat_actions':True})
print(json.dumps({'final_handoff':pin(OUT/'HANDOFF_FINAL.json'),'grouped':pin(OUT/'player-reading-data-proposal-grouped.json')},ensure_ascii=False))
