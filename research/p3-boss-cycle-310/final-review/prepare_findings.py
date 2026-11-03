"""Source-only audit and wording proposal, with exact clauses and locations."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json

OUT=Path(__file__).parent;ROOT=OUT.parents[1];SOURCE=ROOT/'.cache/p3-310-boss-research'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(n,obj):(OUT/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pin(p):return{'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
review=read(OUT/'complete-visible-cards-and-tooltips.json')
original=read(SOURCE/'selected-original-records.json')
cards={(c['actor'],c['card_index']):c for c in review['cards']}
L='洛伦茨，扰动之谬';C='源阶方';M='源阶方模块'
def clause(actor,index,quote):
 c=cards[actor,index];assert quote in c['complete_visible_body']
 ps=[p for p in c['paragraphs']if quote in p['text']];assert len(ps)==1
 return{'source':deepcopy(c['source']),'source_selector':c['source_selector'],
  'paragraph_index':ps[0]['paragraph_index'],'location':ps[0]['location'],'quote':quote}
def module_clause(quote,skill=False):
 m=review['module'];n=m['skill_tables'][0]if skill else m
 text=n['complete_visible_table'];assert quote in text
 return{'source':deepcopy(m['source']),'source_selector':n['source_selector'],
  'location':n['location'],'quote':quote}

flows=[
 {'step_id':'lorentz_knockdown','condition_actor':L,'affected_actors':[L,C],
  'trigger':'洛伦茨初始模式被击倒；区分其重生开始与结束。',
  'text':'洛伦茨被击倒后重生。重生开始时令源阶方强制触发“激活”；重生结束时洛伦茨进入“预退场模式”。这两个时点不等于源阶方的“激活”技能已经结束。',
  'source_refs':[clause(L,1,'被击倒后进行持续1秒的重生（回复100%生命值），重生开始时使源阶方强制触发技能【激活】，重生结束时进入预退场模式')],
  'do_not_infer':['不按文献1秒生成当前倒计时','不把洛伦茨重生结束等同源阶方激活结束']},
 {'step_id':'cube_activate','condition_actor':C,'affected_actors':[C,M],
  'trigger':'源阶方“激活”技能结束。','text':'源阶方在“激活”技能结束时进入行动模式，并在关卡预设位置召唤数个源阶方模块。文献没有据此给出本次实际召唤数量、分组或时间。',
  'source_refs':[clause(C,1,'技能结束时，进入行动模式并在关卡预设位置召唤数个源阶方模块'),clause(C,1,'※技能持续5秒；洛伦茨，扰动之谬进入重生时可令源阶方强制触发此技能')],
  'do_not_infer':['不把开始激活写成立刻行动/召唤','不按预定义9装置或分支三组推实际本次数量','5秒为文献技能时长，不是本局倒计时']},
 {'step_id':'module_clear_gate','condition_actor':L,'affected_actors':[C,L],
  'trigger':'洛伦茨在预退场模式检测场上已无源阶方模块。',
  'text':'检查“场上是否还有模块”的是预退场模式的洛伦茨。文献记载进入此模式5秒后，每0.2秒检查一次；没有模块时令源阶方强制触发“激活中止”，随后洛伦茨回到初始模式。',
  'source_refs':[clause(L,1,'进入此模式5秒后每0.2秒检测一次：若场上不存在源阶方模块，则使源阶方强制触发技能【激活中止】，随后自身回到初始模式')],
  'do_not_infer':['检测主体不是源阶方或模块','不把检查起点改成源阶方进入行动','不宣称模块消失瞬间立即切换','不假造回调ID或同步结束']},
 {'step_id':'cube_deactivate','condition_actor':C,'affected_actors':[C],
  'trigger':'源阶方“激活中止”技能结束。',
  'text':'源阶方要在自己的“激活中止”技能结束时才回到初始模式；文献记载它在初始模式无敌。不要将这一步与洛伦茨返回合并成同时发生。',
  'source_refs':[clause(C,4,'技能结束时回到初始模式'),clause(C,4,'※洛伦茨，扰动之谬检测到场上不存在源阶方模块时可令源阶方强制触发此技能'),clause(C,6,'初始模式\n无敌')],
  'do_not_infer':['不假定两者同一瞬间返回','不虚构激活中止时长']},
 {'step_id':'cube_first_half_hp','condition_actor':C,'affected_actors':[C,'源阶粒素'],
  'trigger':'源阶方生命值首次低于50%后。',
  'text':'源阶方首次低于半血后，“失链裂变”施加的裂变冷却由文献8秒改为4秒；“召唤源阶粒素”改用另一批关卡预设路径。这里强调“首次”，不能只看当前血量重新判断，也不能换算为本局实际技能周期。',
  'source_refs':[clause(C,2,'对全场范围内的所有我方单位造成攻击力100%的近战途径法术普通伤害（无视迷彩），随后自身获得8秒裂变冷却'),clause(C,2,'※生命值首次低于50%后：改为获得4秒裂变冷却'),clause(C,3,'※生命值首次低于50%后：改为以关卡预设路径召唤另一批源阶粒素')],
  'do_not_infer':['首次门不是当前HP阈值切换','裂变冷却不等于技能真实释放间隔','不推实际召唤波次/数量']},
 {'step_id':'lorentz_endpoint','condition_actor':L,'affected_actors':[C,'目标生命','我方单位'],
  'trigger':'洛伦茨到达路径终点。',
  'text':'洛伦茨到达路径终点会扣除30点目标生命，在源阶方所在位置留下持续时间无限的污染弹道，并强制触发源阶方“被摧毁”。扣30点不代表所有对局必败；还要考虑实际剩余目标生命和其他未核实结算条件。',
  'source_refs':[clause(L,1,'到达路径终点时，扣除30点目标生命值、在源阶方所在位置留下一个持续时间无限的污染弹道、并使源阶方强制触发技能【被摧毁】'),clause(L,1,'※污染弹道使半径99.0范围内的所有我方单位（无视隐匿，不受迷彩制约）获得【源阶方污染】：每0.5秒受到200无来源真实伤害（同名效果不叠加）')],
  'do_not_infer':['不把有限半径99.0改成数学全图','不从扣30直接推必败','不计算实际剩余生命']},
 {'step_id':'cube_exit','condition_actor':C,'affected_actors':[C,L,M],
  'trigger':'两个独立条款：“被摧毁”技能结束；源阶方自身退场时。',
  'text':'“被摧毁”技能结束时，源阶方退场（文献称无原因退场）。另一个通用条款是：源阶方退场时，会直接选中并强制击杀场上的洛伦茨和模块，跳过重生。不能将后一个条款限定为只有“被摧毁”会触发，也不能据此补造关卡结束脚本。',
  'subclauses':[{'condition':'“被摧毁”技能结束','result':'源阶方无原因退场'},{'condition':'源阶方退场时','result':'强制击杀场上洛伦茨与模块、跳过重生'}],
  'source_refs':[clause(C,5,'技能结束时退场（视为无原因退场）'),clause(C,5,'※洛伦茨，扰动之谬到达路径终点时可令源阶方强制触发此技能'),clause(C,6,'退场时，直接选中并强制击杀（跳过重生）场上的洛伦茨，扰动之谬和源阶方模块')],
  'do_not_infer':['不把通用退场条件限制为某一种退场原因','不从退场文本推全关胜负脚本']}
]
for f in flows:f['verdict']='supported_as_pinned_documentary_reading_with_stated_boundaries'

module_success_refs=[module_clause('技能持续1秒，技能结束时：',True),module_clause('①记录自身当前攻击力，随后（使用敌方阵营索敌）使全场范围内的所有我方单位（中点判定，不受迷彩制约）延迟0.8秒后受到记录攻击力20%的预计算无来源无途径法术普通伤害。',True),module_clause('②令源阶方受到源阶方自身最大生命值8%的无来源真实伤害。',True),module_clause('③强制击杀自身。',True)]
module_reading=[
 '源阶方模块是关卡装置，不是敌人列表中的敌人。文献明确它属于我方、可以被我方治疗；它的生命会持续流失，属性随探索难度提升。本页不把表中基础面板当成本局面板。',
 '存活到“全域信息失真”技能完成，与先受到致命伤害，是需要分开阅读的情况。文献记载该技能自动回复、自动触发；实际何时完成仍未知，不能把技力消耗当固定秒数。',
 '“全域信息失真”完成时：对全场我方单位造成少量法术伤害；令源阶方受到其自身最大生命值8%的无来源真实伤害；随后强制击杀模块自身。完整备注还记载技能持续1秒、对我方伤害按当时模块攻击力的20%预计算并延迟0.8秒结算。这些是文献说明，不是本局伤害或倒计时预测。',
 '若模块先受到足以致命的伤害，文献记载按其当时攻击力的100%预计算，对全场我方单位延迟0.8秒造成法术伤害。不要把成功完成技能后的强制击杀直接等同受到致命伤害，再额外叠加一次“大爆炸”；完整执行关系未核实。',
 '装置机制还记载：不可被不同阵营选中、不可阻挡，并免疫晕眩、冻结与沉睡；嘲讽等级额外+1；登场时将最大生命值上下限固定为当时最大生命值。',
 '其自损每0.5秒触发，比例为最大生命值的2%加此前触发次数×0.1%，计次最多按30次，达到上限后每次5%。此处保留原文规则，不推算本局存活时长、治疗需求或伤害。',
 '来自我方的即时技力增加或减少会被取消；原页专门说明，技力自然回复速度的属性增益不属于这种即时调整，仍可生效。不可将其简化为“任何技力增益均无效”。'
]

zero_note=next(n for n in review['global_documentation_notes']if n['actor_page']==C)
zero_quote='※能力变量为0时（例：受到的伤害减少0%）代表其具有相应能力，但其默认值为0。常规情况下可视为不启用，或因刻意设计可触发部分效果。'
assert zero_quote in zero_note['complete_text_including_hidden']
zero_audit={'card_source_refs':[clause(C,6,'每次进入此模式获得1层攻击力+0%的增益（最多叠加999层）'),clause(C,6,'使全场范围内的所有我方单位（无视目标可选性，不受迷彩制约）获得【源阶方污染】：每秒受到0无来源真实伤害（同名效果不叠加）')],
 'nearby_tooltips':[deepcopy(t)for t in cards[C,6]['tooltips']],
 'generic_documentation_note':{'source':zero_note['source'],'location':zero_note['location'],'selector':zero_note['selector'],'quote':zero_quote},
 'no_this_boss_specific_difficulty_formula_in_card_or_its_tooltips':True,
 'difficulty_statement_for_module_only':clause(C,1,'源阶方模块的属性会随探索难度等级而提升'),
 'player_wording':'源阶方行动模式的攻击增益与污染伤害在固定文献中以基准字段0记载；不能据此得到本局加成或污染数值，也不能自行补难度倍率。',
 'do_not_infer':['文献0不等于所有实例实际为0','不能断言实例必非0','模块难度提升不证明源阶方零字段的换算方式']}

level=original['complete_original_level'];stage=original['complete_canonical_stage']
exact=[]
for eid,expected_name in [('enemy_2147_shophm',L),('enemy_2148_shorbb',C)]:
 refs=original['complete_stage_enemyDbRefs'][eid];assert len(refs)==1 and refs[0]['level']==0
 record=original['complete_original_enemy_records'][eid]
 matching=[r for r in record['Value']if r['level']==0];assert len(matching)==1
 name=matching[0]['enemyData']['name'];assert name=={'m_defined':True,'m_value':expected_name}
 exact.append({'full_tuple':[stage['id'],eid,0],'name':expected_name,'stage_ref':refs[0],
  'source_file':'.cache/p3-310-boss-research/selected-original-records.json',
  'paths':['complete_canonical_stage.id','complete_stage_enemyDbRefs.'+eid,
   'complete_original_enemy_records.'+eid+'.Value[level=0].enemyData.name'],
  'exact_pinned_original_enemy_level_zero_only':True})
tokens=[{'token_index':i,'record':r}for i,r in enumerate(level['predefines']['tokenInsts'])if r['inst']['characterKey']=='trap_324_shmbmb']
assert len(tokens)==9 and not any(r['id']=='trap_324_shmbmb'for r in level['enemyDbRefs'])
trap={'characterKey':'trap_324_shmbmb','classification':'predefined_trap_not_enemy_tuple',
 'predefined_complete_records':tokens,'predefined_json_path':'complete_original_level.predefines.tokenInsts',
 'enemyDbRefs_do_not_contain_this_characterKey':True,'enemyDbRefs_actual_ids':[r['id']for r in level['enemyDbRefs']],
 'branch_boss_trap_complete':level['branches']['boss_trap'],'branch_json_path':'complete_original_level.branches.boss_trap',
 'module_page_widget_id_evidence':review['module']['trap_id_occurrences'],
 'module_page_name_and_faction':{'source':review['module']['source'],'location':review['module']['location'],
  'text':'源阶方模块 / Origin Lattice Module；实体类型 默认；阵营 我方'},
 'limits':['9条预定义是完整原关卡声明，不是实际9个同时出现的证明','boss_trap分组动作不证明当前调用了哪组或当前数量','不为trap生成enemy_id/level tuple']}

skills=[]
for c in review['cards']:
 if c['kind']!='skill':continue
 name=c['complete_visible_header'].split('\n',1)[0]
 skills.append({'actor':c['actor'],'card_index':c['card_index'],'name':name,
  'documented_modes':c['documented_mode_labels'],'mode_label':'、'.join(c['documented_mode_labels'])or'文献未限定模式',
  'text':c['complete_visible_body'],'source_ref':{'source':c['source'],'selector':c['source_selector'],'location':c['location']},
  'naked_header_numbers_technical_only':True})
unknowns=['当前实例双方模式、技能调用和全局时钟尚未核实。','实际模块数量、分组、存活情况和难度面板未知。',
 '首次低于半血的实际历史状态未知，不能只据当前血量推断。','文献列间减伤对无来源伤害的适用性原文仍写“存疑”。',
 '技能结束与强制击杀、致命伤害的完整引擎执行关系未恢复，不叠加臆测伤害。','不建立新的阶段面板、实际伤害、倒计时或胜负预测。']
proposal={'kind':'PLAYER_WORDING_PROPOSAL_NOT_RUNTIME_OR_CURRENT_GAME_STATE',
 'primary_full_tuple':exact[0]['full_tuple'],'supporting_full_tuple':exact[1]['full_tuple'],
 'overview_notice':'这是“混沌源阶理论”两名首领及模块的固定文献流程。它解释谁触发谁、何时按文献返回，以及模块的两类结果；不读取或推断当前战斗状态。',
 'scope_notice':'依据PRTS洛伦茨441767、源阶方436997、源阶方模块440218及固定原关卡资料；文献中的秒数、比例是原文说明，不是本局倒计时或计算结果。',
 'documentary_flow':flows,'skills':skills,'module_success_source_refs':module_success_refs,'unknowns':unknowns,
 'topics':[
  {'id':'flow','name':'交替激活与退场流程','paragraphs':[f['text']for f in flows],
   'source_refs':[s for f in flows for s in f['source_refs']]},
  {'id':'lorentz','name':'洛伦茨：初始与预退场','paragraphs':[
   '初始模式被击倒后进行重生；重生开始时强制激活源阶方，结束时进入预退场模式。预退场时无敌、不能移动、不能被同阵营选中，无法攻击或被阻挡。',
   cards[L,0]['complete_visible_body'],
   '“象限封锁”的卡片未标明限定模式，不能擅自绑定初始模式；触发仍需攻击范围内存在可部署且没有封印的地块。',
   '到路径终点的扣命、污染、强制“被摧毁”是另一条分支；详细条件见流程页。'],
   'source_refs':[clause(L,1,'预退场模式\n无敌、自缚、孤立，无法攻击/被阻挡'),clause(L,0,cards[L,0]['complete_visible_body'])]},
  {'id':'cube','name':'源阶方：技能与行动条件','paragraphs':[
   '初始模式无敌；文献给“召唤敌人”和“激活”标注初始模式，“失链裂变”“召唤源阶粒素”“激活中止”标注行动模式。“被摧毁”未标明限定模式。',
   '源阶方不能移动、不可阻挡，不进行普通攻击；具有失衡与沉睡免疫。首次进入行动模式时才显示巨型单位界面。',
   zero_audit['player_wording'],
   '文献另记行动模式令全场敌方移动速度+100%。受到物理或法术伤害时：若源阶方占据的列不包含伤害来源所在列，伤害降至30%；否则降至70%。原文对无来源伤害是否适用仍存疑。本页不分析本局站位或据此计算数值。',
   '各技能的完整作用与限定模式见技能原文；没有目标也可触发失链裂变的前提，是自身未持有裂变冷却。首次半血变化见流程页。'],
   'source_refs':[{'source':cards[C,6]['source'],'selector':cards[C,6]['source_selector'],'location':cards[C,6]['location']}]},
  {'id':'module','name':'模块：治疗、技能完成与致命伤害','paragraphs':module_reading,
   'source_refs':[clause(C,1,cards[C,1]['complete_visible_body']),{'source':review['module']['source'],
    'selector':review['module']['source_selector'],'location':review['module']['location']}]+module_success_refs}
 ]}
dump('player-reading-data-proposal.json',proposal)
audit={'kind':'INDEPENDENT_FINAL_SOURCE_AUDIT_NOT_TEST_OR_RUNTIME_ACCEPTANCE',
 'verdict':'source_supported_with_corrections_and_strict_documentary_boundaries',
 'frozen_handoff':{'file':'.cache/p3-310-boss-research/HANDOFF.json',**pin(SOURCE/'HANDOFF.json')},
 'seven_flow_clause_reviews':flows,'exact_boss_tuple_evidence':exact,'trap_not_enemy_evidence':trap,
 'card_accounting':{'boss_cards':9,'boss_skills':7,'boss_abilities':2,'module_skill_tables':1},
 'module_success_missing_from_initial_extraction':{'fact':'冻结原提取只保存装置机制表；完整HTML还含独立装置技能表。',
  'all_skill_text_in':'complete-visible-cards-and-tooltips.json#module.skill_tables','source_refs':module_success_refs,
  'boundary':'可以按文献展示8%和技能结束三步，不把25技力换成25秒；不自动叠致命伤害爆炸。'},
 'zero_field_review':zero_audit,
 'required_wording_corrections':[
  '9张boss机制卡必须分7技能与2能力，模块另有1技能表。',
  'module_clear_gate原候选“不是同一个完成回调”不能当已证引擎事实；改为文献条件/时点不同，不合并为同时返回。',
  '退出流程保两个独立触发条款，不将通用退场限制为被摧毁原因。',
  '象限封锁/被摧毁未标限定模式，仅写文献未限定，不补绑定。',
  '模块完整技能结束条款已证，原“部分生命值”摘要可以扩充为文献8%但不算本局实际掉血。',
  '模块白值只技术原件；玩家正文仅机制/条件，当前难度实际面板未知。'],
 'unknowns':unknowns,'new_HTTP_requests_during_this_final_review':0,
 'frozen_files_unchanged':read(OUT/'frozen-source-pins-before.json')==read(OUT/'frozen-source-pins-after.json'),
 'no_production_Git_Qt_tests_private_state_game_or_chat_actions':True}
dump('source-review.json',audit)
files={p.name:pin(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='HANDOFF.json'}
dump('HANDOFF.json',{'kind':'FINAL310_SOURCE_REVIEW_ONLY_NOT_IMPLEMENTATION_OR_VALIDATION','files':files,
 'read_first':'source-review.json','player_wording':'player-reading-data-proposal.json',
 'complete_visible_sources':'complete-visible-cards-and-tooltips.json','frozen_input_handoff':audit['frozen_handoff'],
 'frozen_source_before_after_same':True,'no_production_Git_Qt_tests_private_state_game_or_chat_actions':True})
print(json.dumps({'handoff':pin(OUT/'HANDOFF.json'),'files':files,'flows':len(flows)},ensure_ascii=False))
