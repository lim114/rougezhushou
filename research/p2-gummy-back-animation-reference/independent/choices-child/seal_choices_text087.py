"""Static text-and-byte choices audit; no parser/import/helper/application calls."""
from pathlib import Path
import hashlib
import json
import subprocess

OUT=Path(__file__).parent
SOURCE=Path('/workspace/.continuation/p2-gummy-back-parser-source087')
BASE='9ef5a469673502754db3be320a8eece9a7fd18d4'
REPO=Path('/workspace/rougezhushou')
def sha(data):return hashlib.sha256(data).hexdigest()
def checked(path,digest,size=None):
 data=path.read_bytes();assert sha(data)==digest,str(path)
 if size is not None:assert len(data)==size,str(path)
 return data
def save_new(name,value):
 p=OUT/name;assert not p.exists(),str(p)
 p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
expected={
 'rouge/animation_reference.py':('3e0c98edfec28e13db3263fc0240e872ed6aaaac53f02729f0e4d17e139b2f1f',2354),
 'scripts/build_original_animation_048.py':('b27c4d80010e721bc519748c17203780ebab7a98386d0e7b139f2268bffc8d5e',6621),
 'scripts/build_animation_selection_048.py':('86271f1e85332dc518e0c7ad9586e4969e0f2f12180d8e9aaa3a38021c8a2b45',1592),
}
texts={};bindings=[]
for path,(digest,size) in expected.items():
 data=subprocess.check_output(['git','show',BASE+':'+path],cwd=REPO)
 assert sha(data)==digest and len(data)==size,path
 texts[path]=data.decode();bindings.append({'path':path,'fixed_commit':BASE,'sha256':digest,'bytes':size})
# These already sealed results are read as plain bytes/text. No JSON reader,
# AST parser, raw source skeleton parser or product code is used.
back_path=SOURCE/'parse-Back-result.json'
back=checked(back_path,'2b3785b65d526bf74329f249b90bf2034c02eb79708e25ec12bdebe73709dd77',7837)
operation_path=SOURCE/'parse-Back-operation.json'
operation=checked(operation_path,'324b57b1b567abc14c174dccffadb2ce184ca55a272ad317136fd11cf90dbf87',3149)
findings_path=SOURCE/'source-findings087.json'
findings=checked(findings_path,'22a886924e5822e3c14fb57c46660fac3906d20dde852390d7820be87bbe1ef8',4174)
manifest_path=SOURCE/'public-artifacts-manifest087.json'
manifest=checked(manifest_path,'db2679793321d9d4a0f817757c53d93f88a16c4d4261f65f54223f69fb8b5265',32415)
assert back.count(b'"name": "Attack"')==1 and back.count(b'"name": "Skill"')==1
assert all(back.count(('"name": "'+name+'"').encode())==1 for name in ('Default','Idle','Start'))
assert b'2b3785b65d526bf74329f249b90bf2034c02eb79708e25ec12bdebe73709dd77' in operation
assert b'"animation_count": 5' in operation
assert b'"animation_names": ["Attack", "Default", "Idle", "Skill", "Start"]' in findings
assert b'"actual_UI_choices_measured": false' in findings
policy=texts['scripts/build_original_animation_048.py']
assert 'FPS = 30' in policy and 'EPSILON_FRAMES = 1e-5  # representation tolerance, not a gameplay/tick tolerance' in policy
assert 'normalized = round(value) if abs(value - round(value)) <= EPSILON_FRAMES else value' in policy
assert "'strict_ceil_frames_30hz': math.ceil(value)" in policy
assert "'ceil_frames_30hz': math.ceil(normalized)" in policy
assert "'recovery_frames': total - windup" in policy
choices=texts['rouge/animation_reference.py']
assert "if not record['selectable_as_conventional_reference']:continue" in choices
assert "ordinary=name.startswith('Attack')" in choices
assert 'if identity is None:return None' in choices
assert "'runtime_binding_verified':False" in choices
assert "if 'Deploy' in record['animation'] and record['selectable_as_conventional_reference']:" in texts['scripts/build_animation_selection_048.py']

excerpts=[]
spans={
 'rouge/animation_reference.py':[(13,23),(26,39),(42,51)],
 'scripts/build_original_animation_048.py':[(15,29),(64,100)],
 'scripts/build_animation_selection_048.py':[(7,22)],
}
for path,ranges in spans.items():
 lines=texts[path].splitlines()
 excerpts.append({'path':path,'sha256':expected[path][0],'ranges':[{'start':a,'end':b,'lines':[{'line':i,'text':lines[i-1]} for i in range(a,b+1)]} for a,b in ranges]})
records=[
 {'animation':'Attack','saved_duration_seconds':1.3333333730697632,'saved_events':[{'name':'OnAttack','seconds':0.5333333611488342}],'existing_builder_eligible_interpretation':True,'why':'Exactly one event, OnAttack strictly inside positive duration; named Attack; no loop/transition/Deploy name.','existing_choice_interpretation':'Attack prefix can enter normal and non-normal branches only after publication and selectable gate; still requires explicit descriptor selection.','label_interpretation':'Back -> 背面; Attack -> 普通攻击; preview frame values come from published normalized reference.','native_binding_inferred':False},
 {'animation':'Default','saved_duration_seconds':0,'saved_events':[],'existing_builder_eligible_interpretation':False,'why':'No OnAttack, no named Attack/Skill, absent named events.','existing_choice_interpretation':'Cannot pass selectable gate.','native_binding_inferred':False},
 {'animation':'Idle','saved_duration_seconds':1,'saved_events':[],'existing_builder_eligible_interpretation':False,'why':'No OnAttack, no named Attack/Skill, absent named events.','existing_choice_interpretation':'Cannot pass selectable gate.','native_binding_inferred':False},
 {'animation':'Skill','saved_duration_seconds':1.3333333730697632,'saved_events':[{'name':'OnAttack','seconds':0.4333333373069763}],'existing_builder_eligible_interpretation':True,'why':'Exactly one OnAttack strictly inside positive duration; starts Skill; no loop/transition/Deploy name.','existing_choice_interpretation':'Literal Skill has no numbered regex match and does not start Attack; neither normal nor skill choices accept it.','label_interpretation':'Generic fallback 攻击动作参考 does not grant choices eligibility or identify S1/S2.','native_binding_inferred':False},
 {'animation':'Start','saved_duration_seconds':1,'saved_events':[{'name':'OnStart','seconds':0.13333334028720856}],'existing_builder_eligible_interpretation':False,'why':'Only OnStart, no OnAttack and not a named Attack/Skill. Start is not asserted to match the distinct Begin/End/Restart textual exclusions.','existing_choice_interpretation':'Cannot pass selectable gate.','native_binding_inferred':False},
]
receipt={'status':'PASS_FINAL_FIXED_SOURCE_AND_SAVED_CHOICES_BOUNDARY_ONLY','planned_section':87,'fixed_product_commit':BASE,'resource_commit':'d0b5af0b004b044d322397ce5ae79632b6d9fcdd','source_bindings':bindings,'saved_attachments':[{'source_path':str(back_path),'bytes':len(back),'sha256':sha(back)},{'source_path':str(operation_path),'bytes':len(operation),'sha256':sha(operation)},{'source_path':str(findings_path),'bytes':len(findings),'sha256':sha(findings)},{'source_path':str(manifest_path),'bytes':len(manifest),'sha256':sha(manifest)}],'sealed102_package_entries_reaudited':False,'raw_skeleton_files_read':0,'records_manual_static_interpretation':records,'builder_policy':{'FPS':30,'EPSILON_FRAMES':1e-5,'normalization':'Only if float(seconds)*30 is within 1e-5 frames of an integer; representation tolerance, no tick/gameplay tolerance.','raw_and_strict_ceil_retained':True,'preview':'Windup/event and total/duration use normalized ceil; recovery=total-windup.','eligibility':'Exactly one OnAttack strictly within positive duration, named attack/Skill, no Loop/Begin/End/Restart, exactly one named event; post-selection excludes Deploy.','new_numeric_frame_conversion_executed':False},'descriptor_scope':{'normal_field':'normal_animation_reference','skill_field':'animation_reference','identity_None_returns_None':True,'identity_must_match_current_choices':True,'missing_or_ineligible_identity_raises_existing_ValueError':True,'runtime_binding_verified_stays_false':True,'literal_Skill_assigned_skill_number':False,'Attack_normal_native_binding_inferred':False},'actual_UI_option_count_measured':False,'new_UI_option_count_claimed':False,'author_product_data_publication_or_finalfreeze_verified_by_this_child':False,'new_source_JSON_AST_or_binary_parse_calls':0,'new_production_imports_or_helper_calls':0,'new_application_API_calls':0,'new_formatter_calls':0,'tests_run':0,'network_calls':0,'Qt_calls':0,'Wine_calls':0,'tracked_edits':0,'known_unknowns':['actual published data and author final freeze are separate parent responsibilities','native skill/normal/skin binding, damage/healing phase, SP and first hit clocks','atlas/render/geometry and current hotupdate equivalence','actual UI selection/options and any parser historical root cause or total'],'preparation_failures':[],'source_excerpts':excerpts}
save_new('choices-boundary-receipt-final087.json',receipt)
note='''# 087 choices静态边界

固定9ef5a46的animation_reference及两份048 builder与已封Back5 saved字节绑定；只读文本，没有执行产品、JSON/AST/骨架parser或frame converter。父审负责新5数据发布、旧923/计数/来源hash与作者最终freeze，此附件不是那部分的执行证明。

既有builder可将Back Attack与无编号Skill记录为selectable来源候选，因为各有一个正时长内OnAttack。Default/Idle没有OnAttack，Start只有OnStart，不能通过既有eligible gate。这里没有拿Start当Begin/End/Restart textual match，也没有借Front填补Back未有动作。

choices先检查published record的selectable标记，再判Attack前缀或编号Skill regex。literal Skill缺编号且不是Attack，所以不能进入任何normal/skill choices。label fallback攻击动作参考没有授权选择资格。Attack在normal及非normal分支都满足ordinary命名条件，但还需要正式发布、selectable gate和descriptor显式identity；identity=None直接None，id必须匹配当前choices。没有测量或宣称新增UI选项数。

30Hz与1e-5是已有浮点表示规则：raw frames/strict ceil保留，近整数才representation-normalize，preview使用normalized ceil及total-windup。它不是游戏tick宽容、实际出手/恢复/技能结束、伤害治疗或SP时钟，native binding继续False。本审不执行新增数值frame换算。

所有结论是固定源码加保存结果的静态映射，没有调用choices/label/descriptor、应用API、formatter、tests、Qt、Wine或网络，没有tracked改动。不对作者尚未冻结草案的默认行为或完整发布作承诺；finalfreeze后也不自行补测试/API。
'''
p=OUT/'NOTE.md';assert not p.exists();p.write_text(note)
save_new('handoff-choices-final087.json',{'status':receipt['status'],'receipt_path':str(OUT/'choices-boundary-receipt-final087.json'),'receipt_sha256':sha((OUT/'choices-boundary-receipt-final087.json').read_bytes()),'source_script_path':str(OUT/'seal_choices_text087.py'),'source_script_sha256':sha((OUT/'seal_choices_text087.py').read_bytes()),'explicit_final_frozen':True,'new_parser_import_helper_API_formatter_tests_network_Qt_Wine_tracked':0,'product_finalfreeze_reviewed':False,'scope':'source-only existing choices/label/descriptor/representation/eligible rules plus already saved Back5; parent owns raw/publication/count checks'})
files=[]
for path in sorted(OUT.iterdir()):
 if path.is_file():
  data=path.read_bytes();files.append({'source_path':str(path),'archive_path':path.name,'bytes':len(data),'sha256':sha(data)})
save_new('public-artifacts-manifest-choices087.json',{'format_version':1,'status':'FINAL_SEALED_SOURCE_BOUNDARY','planned_section':87,'files':files,'file_count':len(files),'total_bytes':sum(row['bytes'] for row in files),'manifest_self_excluded':True,'public_artifacts_only':True,'excluded':['source102 package/large product reference JSON/raw binary skeletons not copied or reaudited','three complete fixed source files only hash-bound and small excerpts retained','author final draft/test/API artifacts not owned by source-text child']})
for row in files:checked(Path(row['source_path']),row['sha256'],row['bytes'])
print(json.dumps({'status':receipt['status'],'handoff_sha256':sha((OUT/'handoff-choices-final087.json').read_bytes()),'receipt_sha256':sha((OUT/'choices-boundary-receipt-final087.json').read_bytes()),'manifest_sha256':sha((OUT/'public-artifacts-manifest-choices087.json').read_bytes()),'file_count':len(files),'total_bytes':sum(row['bytes'] for row in files)},ensure_ascii=False))
