"""Source-only extraction and proposed reading data, no runtime application."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import importlib.util,json,re

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('source_dom',ROOT/'scripts/build_choice_annotations_307.py')
dom=importlib.util.module_from_spec(spec);spec.loader.exec_module(dom)
def serial(n):return n if isinstance(n,str)else{'tag':n.tag,'attributes':n.attrs,'children':[serial(c)for c in n.children]}
def clean(n):
 if isinstance(n,str):return n
 if n.tag in('script','style')or'display:none'in n.attrs.get('style','').replace(' ',''):return''
 if n.tag=='br':return'\n'
 value=''.join(clean(c)for c in n.children)
 return value+('\n'if n.tag in('p','li','dt','dd')else'')
def pin(p):return{'file':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
sources=json.loads((OUT/'http-source-records.json').read_text(encoding='utf-8'))
assert all(r['status']==200 and r.get('revision')for r in sources)
page=OUT/'boss-complete.html';doc=dom.Document(page.read_text(encoding='utf-8'))
cards=[n for n in doc.nodes if dom.cls(n,'ak-card__body')and dom.cls(n,'skill_card')]
assert len(cards)==7
skills=[]
for index,card in enumerate(cards[:6]):
 title=next(c for c in card.children if isinstance(c,dom.Node)and dom.cls(c,'ak-card__title'))
 header=clean(title).strip().split('\n',1)[0]
 name=header.split('[',1)[0];modes=re.findall(r'\[([^\[\]]+)\]',header)
 effect=next(c for c in card.children if isinstance(c,dom.Node)and c.tag=='p')
 skills.append({'skill_id':('calamity_mouth','unextinguished_ground','repeat_calamity','takeoff','flying_ground','landing')[index],
  'name':name,'documented_modes':modes,'effect_text':clean(effect).strip(),
  'source_selector':f'.ak-card__body.skill_card[{index}]','complete_DOM':serial(card),
  'source_has_uncertain_clause':'存疑'in clean(effect),
  'engine_skill_index_binding_verified':False,'actual_cooldown_or_activation':None})
assert [s['name']for s in skills]==['灾厄之口','未熄之地','再次释放','起飞','未熄之地(飞行)','降落']
ability=clean(cards[-1]).strip()
original_path=ROOT/'.cache/game-data/levels/enemydata/enemy_database.json';raw=original_path.read_bytes()
assert sha256(raw).hexdigest()=='f8dd03997d0e3eae65cc4b77bcb6b5ef198488504f738defc31cad5e13c3680c'
database=json.loads(raw);enemy=next(r for r in database['enemies']if r['Key']=='enemy_2150_shchmr')
preview_path=ROOT/'rouge/data/battle-previews.json';preview=json.loads(preview_path.read_bytes());stage=preview['stages']['ro6_b_6']
body=next(e for e in stage['enemies']if e['id']=='enemy_2150_shchmr'and e['level']==0)
level_path=ROOT/'.cache/game-data/levels'/stage['level_source']['url'].split('/levels/',1)[1];levelraw=level_path.read_bytes()
assert sha256(levelraw).hexdigest()==stage['level_source']['sha256']
level=json.loads(levelraw);refs=[e for e in level['enemyDbRefs']if e['id']=='enemy_2150_shchmr']
assert len(refs)==1 and refs[0]['level']==0 and refs[0]['useDb']is True and refs[0]['overwrittenData']is None
skill_path=ROOT/'rouge/data/enemy-skill-references.json';skilldata=json.loads(skill_path.read_bytes())
original={'source_files':[pin(original_path),pin(level_path),pin(preview_path),pin(skill_path)],
 'enemy_database_complete_record':enemy,'stage_complete_enemyDbRefs_record':refs[0],
 'canonical_stage_complete':stage,'canonical_enemy_complete':body,
 'current_skill_definition_complete':skilldata['definitions']['enemy_2150_shchmr'],
 'current_skill_binding_complete':skilldata['bindings']['ro6_b_6']['enemy_2150_shchmr@0']}
(OUT/'selected-original-records.json').write_text(json.dumps(original,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source_ref={'file':'boss-complete.html','revision':sources[0]['revision'],'sha256':sources[0]['sha256'],
 'url':'https://m.prts.wiki/w/玻利瓦尔，症结之核?oldid='+sources[0]['revision']}
phases=[
 {'phase_id':'first','name':'第一形态','kind':'main_combat_form','skill_ids':[],
  'summary':'文献称为第一形态的主要战斗形态。普通攻击的资料另见共同能力。被击倒后的重生和转入灾厄形态，见转换流程；这里不识别本局入场状态。'},
 {'phase_id':'calamity_1','name':'灾厄形态(一)','kind':'intermediate_calamity_form','skill_ids':['calamity_mouth'],
  'summary':'第一次重生后进入的中间形态。文献列为无敌、孤立、自缚、不可阻挡，且不能攻击；在这里施放灾厄之口。'},
 {'phase_id':'second','name':'第二形态','kind':'main_combat_form','skill_ids':['unextinguished_ground'],
  'summary':'第一次灾厄阶段完成后的战斗形态。文献将未熄之地列在此形态；被击倒后经过重生转入灾厄形态(二)。'},
 {'phase_id':'calamity_2','name':'灾厄形态(二)','kind':'intermediate_calamity_form','skill_ids':['calamity_mouth'],
  'summary':'第二次重生后进入；第三形态也可以通过“再次释放”返回这里。两条进入途径不要混为再次重生。'},
 {'phase_id':'third','name':'第三形态','kind':'main_combat_form','skill_ids':['unextinguished_ground','repeat_calamity','takeoff'],
  'summary':'文献分别列出未熄之地、再次释放和起飞；可以返回灾厄形态(二)，也可以进入飞行子形态，不是一条必然按顺序执行的时间表。'},
 {'phase_id':'flying','name':'飞行形态','kind':'third_form_flight_subform','skill_ids':['flying_ground','landing'],
  'summary':'由第三形态起飞后进入，不进行普通攻击；文献列出飞行版未熄之地与降落，降落后回第三形态。不能仅因多列一项，就将其算作额外一条血或新的关卡引用。'}]
edges=[
 ('first_to_calamity1','first','calamity_1','第一形态被击倒','文献：先进行3.6秒重生并回复100%生命，重生结束后进入灾厄形态(一)。属性强化的口径另见来源差异，不在此换算。'),
 ('calamity1_to_second','calamity_1','second','灾厄之口未被打断并完成后续过程','文献：技能结束后获得1.63秒强制缴械；该效果结束后进入第二形态。主目标退场导致的技能中断与重新施放另见招式说明，不能把每次中断当成进入下一形态。'),
 ('second_to_calamity2','second','calamity_2','第二形态被击倒','文献：先进行3.6秒重生并回复100%生命，重生结束后进入灾厄形态(二)。第二次强化字段与文献尚不能直接对算。'),
 ('calamity2_to_third','calamity_2','third','灾厄之口未被打断并完成后续过程','文献：技能结束后获得1.63秒强制缴械；该效果结束后进入第三形态。这次转换不经过重生。'),
 ('third_to_calamity2','third','calamity_2','第三形态的“再次释放”技能结束','文献：返回灾厄形态(二)，这次返回不经过重生；不是再次被击倒。实际就绪和发动时点仍未知。'),
 ('third_to_flying','third','flying','第三形态的“起飞”技能结束','文献：获得近地悬浮并进入飞行形态，15秒内不能触发降落。这里不据冷却参数制作实际倒计时。'),
 ('flying_to_third','flying','third','飞行形态的“降落”技能结束','文献：解除近地悬浮并回到第三形态。')]
transitions=[{'transition_id':key,'from_phase_id':one,'to_phase_id':two,'condition':condition,'text':text,
 'source_refs':[source_ref],'actual_transition':None}for key,one,two,condition,text in edges]
differences=[
 {'difference_id':'second_rebirth_value_basis','title':'重生加成尚不能直接对算',
  'document_text':'文献将第一/第二形态重生时的增益写为最大生命值+50%、攻击力+20%，并写明不会被重生清除。',
  'fixed_fields':{'reborn_1.max_hp':0.5,'reborn_1.atk':0.2,'reborn_2.max_hp':1.0,'reborn_2.atk':0.3},
  'reading_notice':'这些字段可能采用相对基准、累计或其它执行口径；尚未核对，不能认定两份来源互斥、任选一方改值，或换算阶段面板。'},
 {'difference_id':'extension_clock_basis','title':'延长时长的计时口径未闭合',
  'document_text':'灾厄之口详细说明记载主目标退场中断时消耗1层延长灾厄并额外增加11秒持续时间。',
  'fixed_fields':{'Fire.duration_extend':10.0,'Fire.cooldown':1.0},
  'reading_notice':'原字段10与文献11不证明谁错，也不能擅自以10+1解释；实际计时、重启和表现口径仍未核验。'},
 {'difference_id':'highest_hp_selection_wording','title':'目标选择的具体口径分开保留',
  'document_text':'图鉴概述写生命值最高的干员，详细技能写最大生命值最高的我方干员，随后才是自身；范围中心还带“存疑”。',
  'fixed_fields':None,'reading_notice':'保留两处原文和存疑标记；不自动读取或选定本局目标，不对范围或索敌结果作确定预测。'},
 {'difference_id':'raw_mode_index_binding','title':'同名技能记录没有恢复模式绑定',
  'document_text':'文献以模式标签分列或合并招式，原定义则有两个Fire、两个Fireball记录。',
  'fixed_fields':None,'reading_notice':'不能仅按数组先后把同名原技能分别归入某个形态；文献归属与引擎实际附着是两项证据。'}]
data={'kind':'SOURCE_ONLY_PLAYER_DATA_PROPOSAL_NOT_RUNTIME_ACCEPTANCE','identity':{'stage_id':'ro6_b_6','enemy_id':'enemy_2150_shchmr','level':0},
 'title':'畸症 · 玻利瓦尔，症结之核：形态与转换资料',
 'overview_notice':'这里按固定文献查看招式归属、转换条件和返回关系；不识别当前形态，也不改预计面板、伤害、地图或本局记录。',
 'scope_notice':'第一、第二、第三是文献中的主要战斗形态；两种灾厄形态是中间过程，飞行是第三形态的子形态。不要将列表项数理解为血条数、击倒次数或通关保证。',
 'phases':phases,'transitions':transitions,'skills':skills,
 'common_documented_context':{'source_selector':'.ak-card__body.skill_card[6]','text':ability,'complete_DOM':serial(cards[-1]),
  'reading_notes':['锁定在此文献中指无法部署，封印指无法点选；这些是机制说明，不是助手执行的游戏操作。',
   '文献明确说明第三形态与灾厄形态(二)之间不经过重生，因此未用完的延长灾厄可留到之后；不能把每次返回都当清空层数。',
   '文献的三项结局削弱说明与既有302调谐仪式资料相关；复用原入口，不新判定持有、提交或实际生效。']},
 'source_differences':differences,'source_docs':sources,
 'existing_description_already_covers':['三主要形态概述','击倒触发灾厄之口','第二形态火球与地面火焰','第三形态起飞与再次灾厄的概述'],
 'new_player_capability':['按明确文献模式查看招式归属','查看完整转换条件和第三形态循环/飞行返回关系','分开阅读灾厄阶段共同影响及主目标退场的中断条件','同时查看文献与原字段未能直接对算的差异'],
 'unknowns':['当前服务器与当前对局实际形态/转换/层数','原预制体模式及同名技能记录的实际附着/继承/执行','阶段HP/ATK的基准、叠加和完整修正顺序','真实首发、冷却推进、重启与转场时钟','范围中心和实际索敌对象','第三或飞行形态被击倒后的未明确终止流程；不据此承诺通关'],
 'actual_phase':None,'actual_transition':None,'phase_stats':None,'actual_damage':None,'actual_elapsed_time':None,
 'numerical_phase_model_added':False,'game_runtime_verified':False,'inventory_or_run_updated':False,'modifiers_or_maps_changed':False}
for phase in data['phases']:phase['source_refs']=[source_ref]
(OUT/'player-reading-data-candidate.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source_doc_revisions':[s['revision']for s in sources],'documented_mode_names':[p['name']for p in phases],
 'documented_skill_cards':len(skills),'transitions':len(transitions),'differences':len(differences),'runtime_code_written':False},ensure_ascii=False))
