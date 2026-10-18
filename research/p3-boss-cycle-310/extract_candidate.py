"""Read public pinned artifacts and propose one future topic; no runtime implementation."""
from pathlib import Path
from hashlib import sha256
import importlib.util,json,re

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('read_public_dom',ROOT/'scripts/build_choice_annotations_307.py')
dom=importlib.util.module_from_spec(spec);spec.loader.exec_module(dom)
def visible(n):
 if isinstance(n,str):return n
 if n.tag in('script','style')or'display:none'in n.attrs.get('style','').replace(' ',''):return''
 if n.tag=='br':return'\n'
 return''.join(visible(c)for c in n.children)+('\n'if n.tag in('p','li','dt','dd','tr')else'')
def serial(n):return n if isinstance(n,str)else{'tag':n.tag,'attributes':n.attrs,'children':[serial(c)for c in n.children]}
def pin(p):return{'file':p.relative_to(ROOT).as_posix(),'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
docs=json.loads((OUT/'http-source-records.json').read_text(encoding='utf-8'));assert len(docs)==4 and all(r['status']==200 for r in docs)
extracted={}
for source in docs[:3]:
 raw=(OUT/source['file']).read_bytes();assert sha256(raw).hexdigest()==source['sha256']
 document=dom.Document(raw.decode('utf-8'));cards=[n for n in document.nodes if dom.cls(n,'ak-card__body')and dom.cls(n,'skill_card')]
 rows=[]
 for index,n in enumerate(cards):
  title=next((c for c in n.children if isinstance(c,dom.Node)and dom.cls(c,'ak-card__title')),None)
  header=visible(title).strip()if title else None
  rows.append({'card_index':index,'complete_visible_header':header,
   'documented_modes':re.findall(r'\[([^\[\]]+)\]',header or''),
   'complete_visible_body':'\n'.join(visible(c).strip()for c in n.children if isinstance(c,dom.Node)and c.tag=='p'),
   'complete_DOM':serial(n)})
 selected_tables=[]
 if source['file']=='module-complete.html':
  selected_tables=[{'selector':'table.wikitable','complete_visible_text':visible(n).strip(),'complete_DOM':serial(n)}for n in document.nodes
   if n.tag=='table'and dom.cls(n,'wikitable')and'源阶方模块'in visible(n)and'装置机制'in visible(n)]
  assert len(selected_tables)==1 and'trap_324_shmbmb'in raw.decode('utf-8')
 extracted[source['title']]={'source':source,'cards':rows,'tables':selected_tables}
assert len(extracted['洛伦茨，扰动之谬']['cards'])==2 and len(extracted['源阶方']['cards'])==7
(OUT/'complete-document-cards.json').write_text(json.dumps(extracted,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

bpath=ROOT/'rouge/data/battle-previews.json';battle=json.loads(bpath.read_bytes());stage=battle['stages']['ro6_b_5']
levelpath=ROOT/'.cache/game-data/levels'/stage['level_source']['url'].split('/levels/',1)[1]
levelraw=levelpath.read_bytes();assert sha256(levelraw).hexdigest()==stage['level_source']['sha256'];level=json.loads(levelraw)
dbpath=ROOT/'.cache/game-data/levels/enemydata/enemy_database.json';dbraw=dbpath.read_bytes()
assert sha256(dbraw).hexdigest()==battle['source']['enemy_database']['sha256']
database=json.loads(dbraw)
ids=('enemy_2147_shophm','enemy_2148_shorbb','enemy_2149_shorsm')
dbrecords={eid:next(row for row in database['enemies']if row['Key']==eid)for eid in ids}
refs={eid:[row for row in level['enemyDbRefs']if row['id']==eid]for eid in ids}
assert all(len(row)==1 and row[0]['level']==0 for row in refs.values())
skillpath=ROOT/'rouge/data/enemy-skill-references.json';skills=json.loads(skillpath.read_bytes())
original={'source_files':[pin(bpath),pin(levelpath),pin(dbpath),pin(skillpath)],
 'complete_canonical_stage':stage,'complete_original_level':level,'complete_original_enemy_records':dbrecords,
 'complete_stage_enemyDbRefs':refs,'complete_skill_definitions':{eid:skills['definitions'][eid]for eid in ids},
 'complete_skill_bindings':{eid:skills['bindings']['ro6_b_5'][eid+'@0']for eid in ids}}
(OUT/'selected-original-records.json').write_text(json.dumps(original,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
candidate={'kind':'FUTURE310_TOPIC_ONLY_NOT_STARTED_OR_COMPLETED','topic':'混沌源阶理论：洛伦茨与源阶方的交替激活和模块条件流程',
 'existing_reader_source_pins':[pin(ROOT/n)for n in('rouge/battle_preview.py','rouge/enemy_skills.py',
  'rouge/auxiliary_enemy_mechanisms.py','rouge/boss_phase_reference.py')],
 'primary_full_tuple':['ro6_b_5','enemy_2147_shophm',0],
 'supporting_full_tuple':['ro6_b_5','enemy_2148_shorbb',0],
 'related_enemy_full_tuple':['ro6_b_5','enemy_2149_shorsm',0],
 'related_module':{'characterKey':'trap_324_shmbmb','kind':'stage_predefined_trap_not_enemy_tuple',
  'source':'complete_original_level.predefines.tokenInsts and branches.boss_trap','actual_spawned':None},
 'existing_player_capability':['双方图鉴概述与裸技能/黑板参数','既有299分支候选和位置资料','309仅畸症的单首领形态资料；其专属入口不覆盖本组','辅助单位4条机制不含本组'],
 'new_player_capability':['按主体分别查看初始/预退场、初始/行动模式及招式归属','将击倒洛伦茨、源阶方激活、模块消失条件、激活中止及双方分别返回的流程完整串起',
  '分开看源阶方首次半血后改变的文献说明与到终点扣命/污染/退场分支','解释模块是可治疗的关卡装置及其生存/归零分支，避免当成需击杀的敌人；不分析本局站位或做治疗/攻击计算'],
 'documentary_flow':[{
  'step_id':'lorentz_knockdown','source_actor':'洛伦茨，扰动之谬','condition':'初始模式被击倒',
  'documented_result':'重生开始时使源阶方强制触发激活；重生结束时洛伦茨进入预退场模式。','source':'洛伦茨441767能力卡'},
  {'step_id':'cube_activate','source_actor':'源阶方','condition':'激活技能结束',
   'documented_result':'进入行动模式，在关卡预设位置召唤源阶方模块；不据此认定本次模块数、组号或实际时刻。','source':'源阶方436997激活卡'},
  {'step_id':'module_clear_gate','source_actor':'洛伦茨，扰动之谬','condition':'预退场模式下检测场上不存在源阶方模块',
   'documented_result':'使源阶方强制触发激活中止，随后洛伦茨回初始模式；两者不是同一个完成回调。','source':'洛伦茨441767能力卡'},
  {'step_id':'cube_deactivate','source_actor':'源阶方','condition':'激活中止技能结束',
   'documented_result':'源阶方回初始模式；该模式文献记载无敌。','source':'源阶方436997激活中止卡/能力卡'},
  {'step_id':'cube_first_half_hp','source_actor':'源阶方','condition':'生命值首次低于50%后（文献）',
   'documented_result':'裂变冷却改为较短一档，源阶粒素改为另一批预设路径；不从当前血量重新推算，也不计算实际倒计时。','source':'源阶方436997失链裂变/召唤源阶粒素卡'},
  {'step_id':'lorentz_endpoint','source_actor':'洛伦茨，扰动之谬','condition':'到达路径终点',
   'documented_result':'扣目标生命、留下持续污染并令源阶方强制触发被摧毁。扣30不等同所有对局必败，不计算实际剩余生命。','source':'洛伦茨441767能力卡'},
  {'step_id':'cube_exit','source_actor':'源阶方','condition':'被摧毁技能结束/自身退场',
   'documented_result':'被摧毁结束时无原因退场；自身退场时直接强制击杀洛伦茨和场上模块并跳过重生。不能据此补造整个关卡结束脚本。','source':'源阶方436997被摧毁卡/能力卡'}],
 'documentary_mode_names':{'洛伦茨，扰动之谬':['初始模式','预退场模式'],'源阶方':['初始模式','行动模式']},
 'important_source_handling':['洛伦茨当前完整441767将后者称预退场模式；旧搜索缓存有重生模式措辞，采用固定完整版本并保版本边界。',
  '两主体按自己的技能完成/检查条件分别变换，不制造同步切换时刻。',
  '未标模式的象限封锁/被摧毁不凭猜测硬绑某个模式；空模式列表也不证明没有能力。',
  '模块的document类别/机关ID与原enemy元组分开，不替换为同名敌人或把初始源阶方当可伤害。',
  '原关卡预设分组/位置只作为声明；实际选了哪组、何时激活/失效和完整控制器仍未知。'],
 'unknowns':['当前服务器/当前实例模式、实际重生和技能调用','技能与模式的原预制体附着/实际回调','模块当前难度完整属性和实际存活、治疗、爆炸/结算','首次半血门的实际触发及状态留存','当前实际目标/路线/位置/全局时钟','完整阶段面板、伤害和倒计时'],
 'no_new_numeric_phase_model':True,'root_implementation_decision_required':True,
 'production_Git_Qt_private_state_game_or_chat_used':False}
(OUT/'candidate-assessment.json').write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files={p.name:{'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}for p in sorted(OUT.iterdir())if p.is_file()and p.name!='HANDOFF.json'}
h={'kind':'FUTURE310_BOSS_CANDIDATE_RESEARCH_ONLY_NOT_SECTION_START','files':files,'candidate':'candidate-assessment.json',
 'complete_docs':'complete-document-cards.json','raw_fixed_originals':'selected-original-records.json','no_runtime_implementation':True,
 'no_phase_stats_or_time_prediction':True,'production_Git_Qt_private_state_game_or_chat_used':False,
 'next':'Root after309 actual publication may decide whether to implement the substantive cross-actor lifecycle reader; this cache itself is no progress section.'}
p=OUT/'HANDOFF.json';p.write_text(json.dumps(h,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'handoff_sha256':sha256(p.read_bytes()).hexdigest(),'candidate':candidate['topic'],
 'sources':[(r['title'],r['revision'])for r in docs],'lorentz_cards':2,'cube_cards':7,'module_complete_tables':1},ensure_ascii=False))
