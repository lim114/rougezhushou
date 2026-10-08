"""Independent static boundary audit; no product imports or runtime helper calls."""
from pathlib import Path, PurePosixPath
import ast
from collections import Counter
import hashlib
import json
import subprocess

OUT=Path(__file__).parent
SOURCE=Path('/workspace/.continuation/p2-remaining-boolean-consumers-086-source')
REPO=Path('/workspace/rougezhushou')
BASE='b5a40f30683bfc0945decaabbd4db5914c28427f'
GAME='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
MANIFEST_SHA='43fb5c6cfd2806cca065c734bbc0e30e20dc2a447ff0a2ade5d45baa71647de8'
HANDOFF_SHA='babbe184f0c7d69f546d257c780f6e059aaf463576338e1f7530a69920749a5f'
FLAGS={
 'reinforcement_blocks_target':('char_4228_closur',[1,2,3],'skill and normal trait; no E2 named-talent gate'),
 'enemy_below_half':('char_437_mizuki',[1,2,3],'actual selected named 反移情; skill and normal initialization; E0/E1 add default zero'),
 'frozen_at_skill_end':('char_206_gnosis',[3],'S3 skill terminal component and terminal reference; not normal'),
 'ines_first_deployment':('char_4087_ines',[3],'S3 skill deployment branch and fee report note; not normal'),
 'ranged_attack':('char_4182_oblvns',[1,2,3],'all skill and normal plans; selected max_cnt>10 module overrides skill scale only'),
 'organ_mode':('char_4182_oblvns',[2],'S2 skill attack/speed/type branch; not normal'),
 'fever':('char_4182_oblvns',[2],'S2 skill two-hit multiplier; not normal and not S3 Fever description'),
 'power_coating':('char_1048_orchd2',[1,2,3],'all skill selected 强击瓶专家 value; expression reads in normal but normal multiplier stays1'),
 'double_charge':('char_1048_orchd2',[1],'S1 extra component/source parameter; natural SP initial/recharge; event SP cost; normal arrow plan inactive'),
 'steal_success':('char_1041_angel2',[2],'S2 skill attack speed/interval/ammo-derived statistics; not normal'),
 'delivery_coordinate':('char_1041_angel2',[3],'S3 skill independent conditional source; not normal'),
 'overload':('char_1035_wisdel',[2],'S2 skill four-hit/scaled conditional sources; not normal'),
}
def sha(data):return hashlib.sha256(data).hexdigest()
def checked(path, digest, size=None):
 data=path.read_bytes();assert sha(data)==digest,str(path)
 if size is not None:assert len(data)==size,str(path)
 return data
def write_new(name,data):
 p=OUT/name;assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
def save(name,value):write_new(name,(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())

# Verify every source-preparation artifact before using any claim from it.
manifest_bytes=checked(SOURCE/'archivable-public-manifest.json',MANIFEST_SHA)
manifest=json.loads(manifest_bytes)
assert manifest['format_version']==1 and len(manifest['files'])==manifest['count']==28
for row in manifest['files']:
 rel=PurePosixPath(row['archive_path']);assert not rel.is_absolute() and '..' not in rel.parts
 checked(Path(row['source_path']),row['sha256'],row['bytes'])
handoff_bytes=checked(SOURCE/'source-handoff.json',HANDOFF_SHA)
assert json.loads(handoff_bytes)['base_commit']==BASE
sources={};source_bindings=[]
for path in sorted((SOURCE/'source-excerpts').rglob('*.py')):
 name=path.relative_to(SOURCE/'source-excerpts').as_posix()
 data=path.read_bytes()
 fixed=subprocess.check_output(['git','show',BASE+':'+name],cwd=REPO)
 assert data==fixed,name
 sources[name]=data.decode()
 source_bindings.append({'path':name,'sha256':sha(data),'bytes':len(data),'git_fixed_blob_equal':True})
assert len(sources)==8

# Recompute direct gets, recording body versus orelse rather than treating
# an elif's outer negative branch as a simultaneous positive qualification.
consumers=[]
def walk(node,path,ancestors=()):
 if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='get' and node.args and isinstance(node.args[0],ast.Constant) and node.args[0].value in FLAGS:
  expr=ast.unparse(node.func.value)
  if expr in ('self.s','scenario'):
   consumers.append({'path':path,'field':node.args[0].value,'line':node.lineno,'expression':ast.unparse(node),'enclosing_branches':list(ancestors)})
 for key,value in ast.iter_fields(node):
  children=value if isinstance(value,list) else [value]
  for child in children:
   if not isinstance(child,ast.AST):continue
   extra=()
   if isinstance(node,ast.If) and key in ('body','orelse'):
    extra=({'line':node.lineno,'arm':key,'test':ast.unparse(node.test)},)
   elif isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
    extra=({'function':node.name,'line':node.lineno},)
   walk(child,path,ancestors+extra)
for path in ('rouge/operator_engine.py','rouge/reporting.py'):
 walk(ast.parse(sources[path]),path)
consumers.sort(key=lambda x:(x['path'],x['line'],x['expression']))
saved=json.loads((SOURCE/'frozen-public-consumer-ast.json').read_bytes())['consumers']
key=lambda c:(c['path'],c['field'],c['line'],c['expression'])
assert {key(c) for c in consumers}=={key(c) for c in saved}
counts=Counter(c['field'] for c in consumers)
assert len(consumers)==17 and set(counts)==set(FLAGS)
assert counts==Counter({'double_charge':4,'frozen_at_skill_end':2,'ines_first_deployment':2,**{k:1 for k in FLAGS if k not in ('double_charge','frozen_at_skill_end','ines_first_deployment')}})

options_node=next(n for n in ast.parse(sources['rouge/operator_options.py']).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='OPTIONS' for t in n.targets))
options=ast.literal_eval(options_node.value)
options_checked=[]
for field,(owner,skills,scope) in FLAGS.items():
 entries=[r for r in options[owner] if r[0]==field]
 assert len(entries)==1 and isinstance(entries[0][2],bool) and list(entries[0][4])==skills
 options_checked.append({'owner':owner,'field':field,'skills':skills,'bool_default':entries[0][2],'actual_scope':scope})
app=sources['rouge/app.py'].splitlines()
assert "if isinstance(default,bool):" in app[664]
assert 'widget=QCheckBox(label);widget.setChecked(default)' in app[665]
assert 'if owner==op and self.skill.currentData() in skills:' in app[1035]
assert 'widget.isChecked() if isinstance(widget,QCheckBox)' in app[1036]

# Fresh table bytes, then narrow raw identities only. No 240-rank repeat or
# ordinary/special module semantic audit is performed by this subreview.
raw_receipt=json.loads((SOURCE/'original-source-hash-receipt.json').read_bytes())
raw={};raw_bindings=[]
for row in raw_receipt:
 data=checked(Path(row['source_path']),row['sha256'],row['bytes'])
 assert row['source_commit']==GAME
 raw[row['table']]=json.loads(data)
 raw_bindings.append({k:row[k] for k in ('table','source_path','bytes','sha256','source_commit')})
original=json.loads((SOURCE/'original-eight-owner-closure.json').read_bytes())['operators']
narrow=[]
for op,name in [('char_437_mizuki','反移情'),('char_4182_oblvns','颂乐音符'),('char_1048_orchd2','强击瓶专家')]:
 char=raw['character_table'][op]
 groups=original[op]['talents']
 for group in groups:
  assert group['original_group']==char['talents'][group['talent_index']]
 named=[{'talent_index':i,'candidate_index':j,'candidate':c} for i,g in enumerate(char['talents']) for j,c in enumerate(g['candidates']) if c.get('name')==name]
 assert named
 narrow.append({'operator':op,'name':name,'raw_candidates':named})
mizuki=narrow[0]['raw_candidates']
assert len(mizuki)==2 and all(c['talent_index']==1 and c['candidate']['prefabKey']=='2' and c['candidate']['unlockCondition']=={'phase':'PHASE_2','level':1} for c in mizuki)
orchid=narrow[2]['raw_candidates']
assert any(c['candidate']['unlockCondition']=={'phase':'PHASE_0','level':1} and c['candidate']['requiredPotentialRank']==0 for c in orchid)
module=original['char_4182_oblvns']['module_binding_parts'][0]
mid=module['module_id'];assert mid=='uniequip_002_oblvns'
assert module['identity']==raw['uniequip_table']['equipDict'][mid]
assert module['original_parts_per_level']==[p['parts'] for p in raw['battle_equip_table'][mid]['phases']]
assert module['identity']['unlockEvolvePhase']=='PHASE_2' and module['identity']['unlockLevel']==60
overrides=[]
for stage,parts in enumerate(module['original_parts_per_level'],1):
 for part in parts:
  for candidate in (part.get('addOrOverrideTalentDataBundle') or {}).get('candidates') or []:
   if candidate.get('name')=='颂乐音符':
    bb={r['key']:r['value'] for r in candidate['blackboard']}
    assert stage in (2,3) and candidate['talentIndex']==0 and candidate['prefabKey']=='1' and bb['max_cnt']==12
    overrides.append({'stage':stage,'target':part['target'],'candidate':candidate})
assert len(overrides)==2
s1=original['char_1048_orchd2']['skills'][0]
assert s1['skill_id']=='skchr_orchd2_1'
assert s1['original_levels'][9]==raw['skill_table'][s1['skill_id']]['levels'][9]
assert '额外消耗1层' in s1['original_levels'][9]['description']

# Evidence excerpts only; complete execution sources are not copied.
ranges={
 'rouge/operator_engine.py':[(13,29),(75,85),(124,128),(150,151),(211,226),(284,295),(394,398),(616,650),(662,689),(853,879),(1025,1050),(1058,1088),(1091,1130),(1297,1315),(1422,1422),(1439,1448),(1461,1478),(1545,1555)],
 'rouge/damage.py':[(237,250),(262,285),(288,321),(323,351)],
 'rouge/reporting.py':[(100,109),(146,151)],
 'rouge/app.py':[(661,677),(1035,1037)],
}
excerpts=[]
for path,spans in ranges.items():
 lines=sources[path].splitlines()
 excerpts.append({'path':path,'sha256':sha(sources[path].encode()),'spans':[{'start':a,'end':b,'lines':[{'line':i,'text':lines[i-1]} for i in range(a,b+1)]} for a,b in spans]})
olderrors=[
 {'path':'rouge/damage.py','lines':[244,249,262,265,274,275,277,282],'scope':'attributes/skill unlock/raw stolen count/run/relic/attribute rune/raw timing preparation before engine'},
 {'path':'rouge/operator_engine.py','lines':[108,110,111,112,114,116],'scope':'existing effect/numeric errors before self talent initialization'},
 {'path':'rouge/operator_engine.py','lines':[617,854,1049,1120,1125,1126,1127,1442,1447],'scope':'actual cold_state/note_count/dragon_arrow_hits/ghost_count/ghost_casts/zero-window/event SP consumers may raise before core result'},
 {'path':'rouge/reporting.py','lines':[100,107],'scope':'fee-section prior-cast validity is inside later report construction'},
 {'path':'rouge/damage.py','lines':[298,303,305,307,308,309,316,318,320],'scope':'calculate engine then charge/shield/timing/relic/run/stat/summon finishers then report; source order only'},
]
write_new('bound-source-manifest086.json',manifest_bytes)
write_new('bound-source-handoff086.json',handoff_bytes)
save('independent-ast-boundary086.json',{'fixed_commit':BASE,'fields':12,'direct_gets':17,'counts':dict(counts),'all_saved_direct_gets_recomputed_equal':True,'consumers':consumers,'options_static':options_checked,'AST_limits':'Positive/negative branch arm recorded, but manual source inspection determines actual numerical scope; AST alone is not execution.'})
save('narrow-original-boundaries086.json',{'game_commit':GAME,'raw_tables_fresh_hashes':raw_bindings,'three_named_talent_identities':narrow,'oblvns_named_module_overrides':overrides,'oblvns_module_gate':{'elite':2,'level':60},'orchid_s1_rank10_original_description':s1['original_levels'][9]['description'],'normal_scope':'Mizuki initialize-selected bonus and Closur/Oblvns trait can affect normal. Orchid power reads get but multiplier normal1. Normal plan in calculate1470 executes only with known cycle and relevant continuous attack condition. No claim that each module-qualified whole API input changes.', 'all240_skill_rank_reaudit':False,'module_semantic_audit':False})
save('boundary-source-excerpts086.json',{'fixed_commit':BASE,'complete_source_byte_bindings':source_bindings,'excerpts':excerpts,'old_error_static_order':olderrors})
note='''# 086独立消费边界子审

固定b5a40f的8份源码全部与git原字节一致；上游28件清单逐件核hash后，独立AST重算12字段17处直接get。AST记录body/orelse，避免将elif之前的负分支误当同时满足的正资格。未导入或运行任何产品代码。

水月225/226的enemy_below_half虽然在owner分支读值，加成来自实际选中反移情。构造84/85先经selected_talents生成tv，talent151缺名取0；原index1/prefab2两候选均E2L1，不能将E0/E1纸面读值等同有效加成。模组要经过selected29的实际培养门槛，此审不推断AMB-Y附着。

祥子857读取远程80%/100%；858仅有请求模组、not normal、实际所选颂乐音符max_cnt>10时把技能比例覆写1。原模块2/3同index0/prefab1 max_cnt12、E2L60与描述支持该已有范围。859的normal仍使用远程比例；1470的normal执行还有cycle及连续攻击条件，故只证明存在真实正常攻击consumer，不宣称所有合资格模组API输入都必然产生差异。

梓兰double_charge四个get不是仅箭项：1031刚连射、1034条件参数、1313自然SP初动/回转双成本、1440事件SP成本。均S1；normal不发额外箭。power_coating1026先读取get但normal固定倍率1；原强击瓶专家E0起存在，全skill倍率仍使用实际选中值，不能把normal的读取称为有效加成。

其余范围：Closur全skill/normal；Gnosis S3终结及终结资料；Ines S3部署及费用note；Oblvns organ/fever S2；Angel2 steal S2、coordinate S3；Wisdel overload S2，后三组都无normal条件效果。Gnosis零窗口等数值不能直接推成整个API字段失效，因为终结reference另读该条件。

原准备、引擎数值/声明事件/SP、finishers及费用报告各有旧错误路径，附件逐行指明；这里只证明固定源码顺序，没有执行旧错误或提出新的guard方案。外层deployment/wine会重复核心评价，未知外层分支的全局错误先后不能由每次core源码外推。

四原表完整字节重新核hash；只对三具名天赋、祥子单模组具名覆盖、梓兰S1rank10原文做窄原选择核对，没有重做240rank/102module语义审计。上游36探针及其历史结果完全没有重跑，此子审也不把它们当自己的执行证明。原生clock、附着、位置/目标覆盖、箭资源与live游戏均保留未知。
'''
write_new('NOTE.md',note.encode())
receipt={'status':'PASS_FINAL_STATIC_BOUNDARY_ONLY','section':86,'fixed_product_commit':BASE,'game_commit':GAME,'source_handoff_sha256':HANDOFF_SHA,'source_manifest_sha256':MANIFEST_SHA,'source_manifest28_all_hashes_checked':True,'fixed_sources8_byte_equal':True,'direct_fields':12,'direct_gets':17,'direct_gets_by_field':dict(counts),'Mizuki_E0_E1_zero_by_missing_named_talent_not_active_numeric_consumer':True,'Oblvns_skill_module_override_does_not_disable_normal_consumer':True,'Oblvns_normal_runtime_gates_explicit':True,'Orchid_double_charge_four_plan_parameter_natural_SP_event_SP_consumers':True,'Orchid_power_coating_normal_read_not_numeric_effect':True,'actual_Qt_producer_static_only':True,'old_errors_source_order_only':True,'product_guard_plan_proposed':False,'raw_tables4_fresh_hashes_checked':True,'native_clock_or_attachment_verified':False,'new_calculate_damage_calls':0,'new_selected_talents_or_other_product_helper_calls':0,'new_tests':0,'GUI_calls':0,'Wine_calls':0,'tracked_edits':0,'historical36_probes_reexecuted':False,'all240_ranks_reaudited':False,'ordinary102_module_semantics_reaudited':False,'preparation_read_diagnostics':[{'path':'public-artifacts-manifest.json','reason':'filename absent; corrected by reading directory to archivable-public-manifest.json; no dependent mutation'},{'reason':'narrow display initially assumed direct candidates field; actual preserved extract uses original_group.candidates; corrected from inspected keys before any writes'}],'unknowns':['native attachment/clock/tick/order/live game','actual placement/target coverage/arrow resource consumption','unexecuted outer branch old-error priority and whole API module output equality'],'restart_conditions':'Any product proposal or matrix needs separate authorization and current-root snapshot; this sealed b5 static source audit cannot overwrite83/84/85.'}
save('receipt-boundary-final086.json',receipt)
handoff={'status':receipt['status'],'receipt_path':str(OUT/'receipt-boundary-final086.json'),'receipt_sha256':sha((OUT/'receipt-boundary-final086.json').read_bytes()),'source_script_path':str(OUT/'audit_boundary086.py'),'source_script_sha256':sha((OUT/'audit_boundary086.py').read_bytes()),'new_API_helper_tests_GUI_Wine_tracked':0,'scope':'12fields17gets actual positive/negative source qualification and normal/multiconsumer/old-error order; no product proposal or fresh execution','explicit_final_frozen':True}
save('handoff-boundary-final086.json',handoff)
files=[]
for path in sorted(OUT.iterdir()):
 if path.is_file():
  data=path.read_bytes();files.append({'source_path':str(path),'archive_path':path.name,'bytes':len(data),'sha256':sha(data)})
save('public-artifacts-manifest086.json',{'format_version':1,'status':'FINAL_SEALED','section':86,'files':files,'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files),'manifest_self_excluded':True,'public_artifacts_only':True,'excluded':['source full execution copies; all8 exact fixed Git source bytes are hash-bound in excerpt receipt','entire raw tables; four complete hashes and narrow raw selections retained','historical36 public probe records; bound upstream manifest provides their existing paths/hashes']})
for row in files:checked(Path(row['source_path']),row['sha256'],row['bytes'])
print(json.dumps({'status':receipt['status'],'handoff_sha256':sha((OUT/'handoff-boundary-final086.json').read_bytes()),'receipt_sha256':handoff['receipt_sha256'],'manifest_sha256':sha((OUT/'public-artifacts-manifest086.json').read_bytes()),'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files)},ensure_ascii=False))
