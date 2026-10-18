"""Prepare a fixed-source research handoff; no product/test/Qt execution."""
from pathlib import Path
from hashlib import sha256
import importlib.util,json

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
L=lambda name:json.loads((OUT/name).read_bytes())
def write(name,obj):
    (OUT/name).write_bytes((json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
def pin(path):
    raw=path.read_bytes()
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
D=L('complete-document-cards-with-tooltips.json')['documents']
P=L('selected-original-records.json')
B='卡德霍，黑流之源';A='痛楚化身';H='猎犬proto'
def source(actor,index):
    doc=D[actor];card=doc['cards'][index]
    return {'file':'complete-document-cards-with-tooltips.json','actor':actor,'card_index':index,
            'location':card['location'],'revision':doc['source']['revision'],'url':doc['source']['final_url']}
def paragraph(text,*refs):return {'text':text,'source_refs':list(refs)}
topics=[
 {'id':'condition_flow','name':'击倒、休整与后续来敌','paragraphs':[
  paragraph('卡德霍首次被击倒时，文献记载会回复全部生命，随后进入休整：此时无法攻击、无法被阻挡，并获得无敌与孤立。孤立的原文提示指不能被同阵营选中。',source(B,4)),
  paragraph('波次说明保留了“从当前波次释放2次（存疑）”，另记5秒后的再次释放。这是文献自己标记的存疑，不据此确认本局波次数、出怪次数或开战后的时间。',source(B,4)),
  paragraph('摘要把后续敌人概括为“召唤”；完整说明明确猎犬proto和痛楚化身由关卡配置生成，而非卡德霍直接召唤。普通版原配置确有这些独立出怪条目，不证明本局已触发或已经清场。',source(B,3),source(B,4)),
  paragraph('文献记载关卡到特定波次时会强制使卡德霍发动【感受痛楚】，技能结束后退场。此处未还原本局波次推进、触发时刻或通关结算。',source(B,3),source(B,4))]},
 {'id':'cadejo','name':'卡德霍的分担伤害与位移','paragraphs':[
  paragraph('普通攻击优先选择阻挡数最高的我方单位；完整文献说明，这一选择不受它是否正被该单位阻挡影响。',source(B,4)),
  paragraph('【痛吼】有两条分支：攻击范围内有我方单位时，由范围内目标分担文献所列总物理伤害；范围内没有我方单位时，改为全场另一档物理伤害和晕眩。两种结果不能相加。',source(B,0)),
  paragraph('【行于荒原】先留下临时弹道，再闪现到下一检查点，弹道随后飞向它的位置，对沿途碰到的我方单位造成法术伤害并降低攻击速度。同名减益不叠加；本局路线和命中未验证。',source(B,1)),
  paragraph('降攻速的持续时间有资料差异：同页摘要写20秒，完整基础技能卡与普通版原配置写10秒。两种记载都保留，不能据此确认当前对局实际持续时间。',source(B,1)),
  paragraph('【湮灭】文献写扣除30点关卡生命并强制击杀自身；不是本局已发生的记录，也不能只凭该数字断定所有对局必然失败。',source(B,2))]},
 {'id':'avatars','name':'痛楚化身离场后的变化','paragraphs':[
  paragraph('痛楚化身文献写出场时获得3秒无敌，普通攻击同样优先阻挡数最高的我方单位。【痛吼】仍分范围内分担和范围内无人时的全场攻击；后者晕眩记为5秒，不套卡德霍的8秒。',source(A,0),source(A,3)),
  paragraph('图鉴原文只写剩余痛楚化身攻击提升；社区修正版及完整能力卡改为当前全场所有敌方单位获得攻击增益。两种记载并列保留，这不是已核对当前服务器的结论。',source(A,3)),
  paragraph('完整能力以痛楚化身“退场”为条件：全场敌方单位获得一层攻击增益（最多2层，叠加时以第一层数值为基础翻倍），按地图预设路径产生一批敌人，并使所有痛楚化身强制发动【行于荒原】。不能擅自把退场只改写为普通击杀，或把最多层数当当前面板。',source(A,3)),
  paragraph('痛楚化身的【行于荒原】在技能结束时闪现并发出弹道；技能期间持有无敌、晕眩和冻结免疫，并提高按生命上限计的回复速度。它与卡德霍的位移卡不同，不共用实际时钟。完整原值与全部限定分别保留。',source(A,1)),
  paragraph('痛楚化身的【湮灭】文献写每个扣除10点关卡生命并强制击杀自身；不由原始冷却字段生成当前倒计时，也不自动补造其它退场效果。',source(A,2))]},
 {'id':'hound','name':'猎犬proto的锁定撕咬','paragraphs':[
  paragraph('猎犬proto只进行阻挡攻击，普通攻击附加狂躁损伤。它不是卡德霍的新形态，不与痛楚化身的原图或技能合并。',source(H,1)),
  paragraph('【持续撕咬】的文献条件是范围内存在非飞行我方单位；发动后传送到目标所在地块中心并锁定持续攻击，结束后返回技能开始时自身所在地块中心。不能把“非飞行”自行改成“只可攻击地面部署位”。',source(H,0)),
  paragraph('该卡记载10秒持续攻击：每秒造成攻击力100%的法术普通伤害，附加30%攻击力的狂躁损伤，并施加1.5秒命中率减益，使物理及法术命中率最终降至20%（不叠加）。这些是固定文献参数，不是本局伤害或命中预测。',source(H,0)),
  paragraph('原文特意说明持续攻击不会随技能一起被打断，另列技能期间的多项免疫。不能简化成所有攻击永远不可打断，也不能用技能结束或打断时间代替实际持续攻击回调。',source(H,0))]}
]
skills=[]
for actor in (B,A,H):
    for c in D[actor]['cards']:
        if c['kind']=='skill':
            skills.append({'actor':actor,'card_index':c['card_index'],
                'name':c['complete_visible_header'].split('\n',1)[0],
                'documented_modes':c['documented_modes_from_complete_header'],
                'full_body_paragraphs':[x['text']for x in c['paragraphs']],
                'source_refs':[source(actor,c['card_index'])],
                'header_DOM_preserved':True,'numeric_header_not_actual_clock':True})
targets=[['ro6_b_4','enemy_2145_cadejo',0],['ro6_b_4','enemy_2146_cadesd',0],['ro6_b_4','enemy_2137_shsdgo',0]]
proposal={'schema':'section311_documentary_player_reading_proposal_v1','title':'永无安宁：卡德霍、痛楚化身与猎犬的条件资料',
 'targets':targets,'topics':topics,'skills':skills,'skill_cards':8,'ability_cards':3,
 'overview_notice':'仅限固定普通版关卡的文献阅读；不同条件分支分别成立，不是本局必经时间轴。',
 'scope_notice':'不新增基础白值、当前模式、时钟、伤害、库存或实际波次计算。完整卡、原表与提示及资料冲突在依据中保留。',
 'unknowns':['当前服务器与当前实例的模式、触发、目标和时钟','波次释放2次的原文存疑、实际波次推进和出怪次数','20秒与10秒记载的当前适用值','buff实际接受/层数、命中、回复、伤害和结算','追猎版两自定义化身与基础文献执行之间尚未独立验证的绑定'],
 'actual_mode':None,'actual_elapsed_time':None,'actual_damage':None,'actual_buff_layers':None,'run_state_updated':False}
write('player-reading-proposal.json',proposal)

# Preserve the original/corrected summary switch, not merely the active text.
spec=importlib.util.spec_from_file_location('source_dom_final',ROOT/'scripts/build_choice_annotations_307.py')
dom=importlib.util.module_from_spec(spec);spec.loader.exec_module(dom)
def text(n,include_hidden=False):
    if isinstance(n,str):return n
    if n.tag in ('script','style')or(not include_hidden and 'display:none'in n.attrs.get('style','').replace(' ','')):return ''
    return ''.join(text(c,include_hidden)for c in n.children)+('\n'if n.tag in ('p','li','br')else '')
def serial(n):return n if isinstance(n,str)else {'tag':n.tag,'attributes':n.attrs,'children':[serial(c)for c in n.children]}
summaries=[]
for filename,actor in [('boss-complete.html',B),('avatar-complete.html',A)]:
    document=dom.Document((OUT/filename).read_text('utf8'))
    parts=[n for n in document.nodes if n.tag=='p'and '·【痛吼】'in text(n)and '·【湮灭】'in text(n)]
    summaries.append({'actor':actor,'file':filename,'versions':[{'complete_visible_text':text(n).strip(),'complete_text_including_tooltips':text(n,True).strip(),'complete_DOM':serial(n)}for n in parts]})
differences={'schema':'section311_source_differences_v1','summary_versions':summaries,'differences':[
 {'id':'duration20_vs10','fact':'卡德霍同页摘要20秒、完整基础Blink卡10秒；普通原配置duration=10.0，追猎覆写duration=20.0。不能因数值相同就断定摘要针对追猎版。'},
 {'id':'summon_vs_configuration','fact':'摘要称召唤；完整能力/感受痛楚卡明确猎犬和化身由关卡配置生成。原主队列/分支有独立SPAWN声明，不代表真实回调已恢复。'},
 {'id':'uncertain_release','fact':'完整能力的释放2次(存疑)保持原样，不以当前level反推唯一执行。'},
 {'id':'avatar_scope','fact':'原图鉴仅剩余痛楚化身，社区修正及完整能力卡为全场敌方单位；保留版本/提示依据，不冒当前服务器观测。'},
 {'id':'variant','fact':'b4_b有独立skills覆写和两条useDb=false自定义化身；definitions={}不等于原配置空，不扩普通版入口。'}],
 'complete_stage_enemyDbRefs':P['complete_stage_enemyDbRefs'],
 'header_rule':'玩家仅用技能名/明确形态；2020/、2040/、450450/、1025/等连写不直接显示，不拆成实际首发或周期秒数。',
 'untagged_mode_rule':'文献未限定不等于始终生效或没有能力。','original_raw_mutated':False}
write('source-differences.json',differences)
assessment={'kind':'SECTION311_CANDIDATE_SOURCE_RESEARCH_NOT_ACCEPTANCE','targets':targets,
 'existing_capabilities':['现有图鉴简述、固定预测面板及原skill/blackboard','299候选组/同包资料','306伪装、309畸症、310洛伦茨/源阶方，均非本组完整阅读'],
 'new_capability':'三个精确普通版身份，按条件阅读卡德霍击倒与关卡生成、双方不同招式、痛楚离场影响与猎犬锁定，并显式阅读资料冲突。',
 'runtime_design_advice':'轻量fresh小固定源+完整当前目标stage/三主体skill对象；完整数据库/原level只在构建时核实，runtime不每次读15MB。精确身份，非目标无新增I/O，source坏清旧恢复手动，deepcopy防污染。',
 'acceptance_scope':['三精确tuple/非法bool或float level/非目标/追猎与两custom不借base','8技能+3能力全限定/tooltip/原header DOM保留','玩家显式20vs10、原文vs修正、存疑波次；无当前伤害/时钟/阶段模型','源坏暖副本失效/恢复手动、输入输出串改防护、父阅读保留','与306/309/310独立，原190资源/事件/地图/本局不变'],
 'source_reuse':{'primary_full_files':P['source_files'],'existing_public_pursuit_level':pin(ROOT/'research/p3-auxiliary-mechanisms/level_rogue6_b-4-b.json')},
 'source_archive_note':'未来公开包不能依赖.cache。五HTML保完整原bytes，原level/数据库按固定commit与SHA核实后精选whole records；已有公开原件优先引用，不复制15MB多份。',
 'no_product_or_test_pass_claimed':True,'production_Git_Qt_game_chat_private_operations':False}
write('candidate-assessment.json',assessment)
markdown="""# 第311节候选：永无安宁的卡德霍、痛楚化身与猎犬proto

来源交接，不是功能或测试通过回执。建议三个普通版精确身份的独立手动阅读入口，按条件分组，不作线性时间轴。现有306/309/310均不覆盖本组完整条件。

完整原文：卡德霍436092、痛楚441718、猎犬436178、永无安宁427937、痛苦将息428754。五份HTTP200与全部头/时间/修订/SHA在http-source-records.json。完整8技能卡+3能力卡/DOM/tooltip/所有wikitable在complete-document-cards-with-tooltips.json。卡片标题不显示2020/等抓平数字；不拆成实际时钟。

普通版三元组为ro6_b_4 + enemy_2145_cadejo@0 / enemy_2146_cadesd@0 / enemy_2137_shsdgo@0。猎犬proto就是固定原名，不创造另一中文专名。追猎b4_b仅完整差异资料，不能继承普通版参数；custom2/3原配置完整，并非空配置。

必须普通页明显说明：降攻速摘要20秒vs基础卡和普通配置10秒；摘要召唤vs完整说明关卡生成；释放2次本身存疑；化身原文仅剩余化身、社区修正全场敌方单位。最多2层30%不是当前面板。原始卡、提示、完整配置分别可查。

玩家草案见player-reading-proposal.json；source-differences.json保原文与修正切换的全部DOM。基础白值由现有预测面板负责，本资料不新增当前模式、伤害、倒计时、波次或掉落计算。25/57、81/59等缺口不减少。
"""
(OUT/'PROPOSAL.md').write_bytes(markdown.encode('utf8'))
write('source-pins.json',{'schema':'section311_research_pins_v1','complete_documents':[pin(OUT/r['file'])for r in L('http-source-records.json')],
 'primary_full_sources':P['source_files'],'existing_code_read':[pin(ROOT/n)for n in ['rouge/battle_preview.py','rouge/enemy_skills.py','rouge/boss_phase_reference.py','rouge/boss_cycle_reference.py','rouge/enemy_form_reference.py','rouge/battle_view.py','PROJECT_PROGRESS.md','CLOUD_HANDOFF.md']],
 'raw_HTML_mutated':False,'source_records':'http-source-records.json'})
print(json.dumps({'targets':targets,'topics':len(topics),'skills':len(skills),'abilities':3,'product_acceptance_claimed':False},ensure_ascii=False))
