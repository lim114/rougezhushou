"""Independent frozen-product static review; never import product modules."""
from pathlib import Path, PurePosixPath
from collections import Counter
import ast
import hashlib
import json
import subprocess

OUT=Path(__file__).parent
AUTHOR=Path('/workspace/.continuation/p2-remaining-boolean-consumers-086-draft')
PRIOR=Path('/workspace/.continuation/independent-source086/boundary-subreview')
REPO=Path('/workspace/rougezhushou')
BASE='9ef5a469673502754db3be320a8eece9a7fd18d4'
FREEZE_SHA='aa066032869298b11b06819a2533fa53e78096dd725d4006f01bbde551edab55'
PATCH_SHA='4834ec66e47ebdf8df0e8ef0c57e19dafe1693d80f51e9061245879c33005f87'
MARKER='ranged_attack_condition_consumed'
def sha(data):return hashlib.sha256(data).hexdigest()
def checked(path,digest,size=None):
 data=path.read_bytes();assert sha(data)==digest,str(path)
 if size is not None:assert len(data)==size,str(path)
 return data
def write_new(name,data):
 p=OUT/name;assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
def save(name,value):write_new(name,(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())
def parent_map(tree):
 return {child:parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
def source(node,text):return ast.get_source_segment(text,node)
def function(tree,name):return next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
def parse(data):return ast.parse(data.decode())
def simple(node):return ast.dump(node,include_attributes=False)

freeze_bytes=checked(AUTHOR/'review-freeze86.json',FREEZE_SHA)
freeze=json.loads(freeze_bytes)
assert freeze['status']=='FROZEN_FOR_FORMAL_REVIEW' and freeze['base_commit']==BASE
patch_bytes=checked(AUTHOR/'section86.patch',PATCH_SHA,freeze['patch_bytes'])
frozen={r['path']:r for r in freeze['files']}
assert set(frozen)=={'rouge/damage.py','rouge/operator_engine.py','tests/test_remaining_boolean_condition_text_input.py'}
for row in frozen.values():checked(Path(row['source_path']),row['sha256'],row['bytes'])

baseline_freeze_bytes=(AUTHOR/'current-baseline-freeze.json').read_bytes()
baseline_freeze=json.loads(baseline_freeze_bytes)
assert baseline_freeze['base_commit']==BASE and len(baseline_freeze['files'])==723
rows=baseline_freeze['files'];assert len({r['path'] for r in rows})==723
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'rouge','tests','scripts'],cwd=REPO,text=True).splitlines()
assert {p for p in paths if p.endswith(('.py','.json'))}=={r['path'] for r in rows}
buf=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(r['git_blob'] for r in rows)+'\n').encode(),cwd=REPO)
offset=0;old={};unchanged=0
for row in rows:
 end=buf.index(b'\n',offset);header=buf[offset:end].decode().split();assert header[:2]==[row['git_blob'],'blob']
 size=int(header[2]);data=buf[end+1:end+1+size];assert buf[end+1+size:end+2+size]==b'\n';offset=end+2+size
 assert size==row['bytes'] and sha(data)==row['sha256'],row['path']
 assert checked(AUTHOR/'baseline'/row['path'],row['sha256'],row['bytes'])==data
 old[row['path']]=data
 if row['path'] not in ('rouge/damage.py','rouge/operator_engine.py'):
  checked(AUTHOR/'draft'/row['path'],row['sha256'],row['bytes']);unchanged+=1
assert offset==len(buf) and unchanged==721
engine=(AUTHOR/'draft/rouge/operator_engine.py').read_bytes()
damage=(AUTHOR/'draft/rouge/damage.py').read_bytes()
assert engine.count(b'\n')==engine.count(b'\r\n') and damage.count(b'\n')==damage.count(b'\r\n')

# Exact source removal proves no prior calculation, selector, finisher or guard
# was silently replaced. Only frozen production additions are removed.
reset=b'        self.ranged_attack_condition_consumed=False\r\n'
signal=("        if self.s['operator']=='char_4182_oblvns':\r\n"
        "            ranged_overridden=self.s.get('module_id') and self.tv.get('颂乐音符',{}).get('max_cnt',10)>10\r\n"
        "            self.ranged_attack_condition_consumed=not ranged_overridden or normal is not None\r\n").encode()
assert engine.count(reset)==engine.count(signal)==1
engine_stripped=engine.replace(reset,b'',1).replace(signal,b'',1)
assert engine_stripped==old['rouge/operator_engine.py']
old_call=b'        from .operator_engine import calculate_extended\r\n        result=calculate_extended(scenario,attributes)\r\n'
new_call=b'        from .operator_engine import Combat\r\n        combat=Combat(scenario,attributes)\r\n        result=combat.calculate()\r\n'
assert damage.count(new_call)==1
start=damage.index(b'    # Keep legacy calculation/finisher/report errors before text-only conditions.\r\n')
end=damage.index(b'    return result\r\n',start)
guard=damage[start:end]
assert damage.replace(guard,b'',1).replace(new_call,old_call,1)==old['rouge/damage.py']

engine_text=engine.decode();damage_text=damage.decode()
etree=parse(engine);dtree=parse(damage)
calculate=function(etree,'calculate');plan=function(etree,'plan');core=function(dtree,'_evaluate_damage_once')
wrapper=function(etree,'calculate_extended')
assert simple(wrapper)==simple(function(parse(old['rouge/operator_engine.py']),'calculate_extended'))
assert len(wrapper.body)==1 and isinstance(wrapper.body[0],ast.Return)
assert ast.unparse(wrapper.body[0].value)=='Combat(scenario, attributes).calculate()'
assert ast.unparse(calculate.body[0])=='self.ranged_attack_condition_consumed = False'
normal_assign=next(n for n in calculate.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='normal' for t in n.targets))
assert ast.unparse(normal_assign.value)=="self.plan(normal=True, window=recharge) if cycle is not None and (not (sp['sp_type'] == 'INCREASE_WHEN_ATTACK' and (not self.s.get('continuous_attacks', True)))) else None"
signal_if=calculate.body[calculate.body.index(normal_assign)+1]
assert isinstance(signal_if,ast.If) and ast.unparse(signal_if.test)=="self.s['operator'] == 'char_4182_oblvns'"
override=next(n for n in ast.walk(plan) if isinstance(n,ast.If) and "not normal" in ast.unparse(n.test) and 'max_cnt' in ast.unparse(n.test))
signal_override=signal_if.body[0].value
terms=override.test.values
assert isinstance(override.test,ast.BoolOp) and len(terms)==3
assert ast.unparse(terms[0])=="self.s.get('module_id')"
assert ast.unparse(terms[1])=='not normal'
assert ast.unparse(terms[2])=="self.tv.get('颂乐音符', {}).get('max_cnt', 10) > 10"
assert simple(signal_override.values[0])==simple(terms[0]) and simple(signal_override.values[1])==simple(terms[2])
assert ast.unparse(signal_if.body[1].value)=='not ranged_overridden or normal is not None'
marker_nodes=[n for n in ast.walk(etree) if isinstance(n,ast.Attribute) and n.attr==MARKER]
assert len(marker_nodes)==2 and all(isinstance(n.ctx,ast.Store) for n in marker_nodes)
marker_read=[n for n in ast.walk(core) if isinstance(n,ast.Attribute) and n.attr==MARKER]
assert len(marker_read)==1 and isinstance(marker_read[0].ctx,ast.Load) and ast.unparse(marker_read[0].value)=='combat'
parents=parent_map(dtree)
cur=marker_read[0];owners=[]
while cur in parents:
 cur=parents[cur]
 if isinstance(cur,ast.If):owners.append(ast.unparse(cur.test))
assert owners==["op == 'char_4182_oblvns'"]
extended_branch=next(n for n in core.body if isinstance(n,ast.If) and 'not in' in ast.unparse(n.test))
assert ast.unparse(extended_branch.test)=="scenario['operator'] not in ('kaltsit', 'silverash', 'mechanist')"
assert all(owner!='char_4182_oblvns' for owner in ('kaltsit','silverash','mechanist'))
assert len(extended_branch.body)==3 and ast.unparse(extended_branch.body[1])=='combat = Combat(scenario, attributes)'
assert ast.unparse(extended_branch.body[2])=='result = combat.calculate()'
assert not any(isinstance(n,ast.Constant) and n.value==MARKER for n in ast.walk(etree))
assert not any(isinstance(n,ast.Constant) and n.value==MARKER for n in ast.walk(dtree))

# Old named/raw eligibility evidence remains immutable; rehash it without
# repeating original table, rank/module audits or any probe/helper execution.
prior_manifest_bytes=checked(PRIOR/'public-artifacts-manifest086.json','35581c4c3fc7edfd4f47de9abc4465a9dd9023ec6f2acb05cc4983fc41df6f30')
prior_manifest=json.loads(prior_manifest_bytes);assert len(prior_manifest['files'])==9
for row in prior_manifest['files']:checked(Path(row['source_path']),row['sha256'],row['bytes'])
prior_handoff_bytes=checked(PRIOR/'handoff-boundary-final086.json','79c6538f7a2f016732c5ee7689d2cda93be1605491fd5887f153cfd7b8c87a94')
prior_ast=json.loads((PRIOR/'independent-ast-boundary086.json').read_bytes())
flags={r['field']:r for r in prior_ast['options_static']}
assert len(flags)==12
consumers=[]
for path,data in [('rouge/operator_engine.py',engine),('rouge/reporting.py',old['rouge/reporting.py'])]:
 for n in ast.walk(parse(data)):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='get' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value in flags and ast.unparse(n.func.value) in ('self.s','scenario'):
   consumers.append({'path':path,'field':n.args[0].value,'line':n.lineno,'expression':ast.unparse(n)})
assert len(consumers)==17
count=Counter(c['field'] for c in consumers)
assert count==Counter(prior_ast['counts'])
old_pair=lambda c:(c['path'],c['field'],c['expression'])
assert Counter(old_pair(c) for c in consumers)==Counter(old_pair(c) for c in prior_ast['consumers'])

expected_guard="""    # Keep legacy calculation/finisher/report errors before text-only conditions.
    op=scenario['operator'];number=scenario['skill']
    conditions={
        'char_4228_closur':('reinforcement_blocks_target',),
        'char_206_gnosis':('frozen_at_skill_end',) if number==3 else (),
        'char_4087_ines':('ines_first_deployment',) if number==3 else (),
        'char_1041_angel2':('steal_success',) if number==2 else ('delivery_coordinate',) if number==3 else (),
        'char_1035_wisdel':('overload',) if number==2 else (),
    }.get(op,())
    if op=='char_4182_oblvns':
        conditions=(('ranged_attack',) if combat.ranged_attack_condition_consumed else ())
        if number==2:conditions+=('organ_mode','fever')
    if op in ('char_437_mizuki','char_1048_orchd2'):
        field,talent=('enemy_below_half','反移情') if op=='char_437_mizuki' else ('power_coating','强击瓶专家')
        if isinstance(scenario.get(field),str):
            from .operator_engine import selected_talents
            talents,_=selected_talents(catalog()['operators'][op],scenario)
            if any(t.get('name')==talent for t in talents):conditions+=(field,)
        if op=='char_1048_orchd2' and number==1:conditions+=('double_charge',)
    for field in conditions:
        if isinstance(scenario.get(field),str):
            raise ValueError(field+' 不接受文本条件；请使用布尔值。')
""".replace('\n','\r\n').encode()
assert guard==expected_guard
core_body=core.body
report_assign=next(n for n in core_body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Subscript) and isinstance(t.slice,ast.Constant) and t.slice.value=='report' for t in n.targets))
op_assign=next(n for n in core_body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='op' for t in n.targets))
assert core_body.index(report_assign)<core_body.index(op_assign)
assert core_body[-1].__class__ is ast.Return
assert core_body[-2].__class__ is ast.For
assert ast.unparse(core_body[-2].body[0].test)=='isinstance(scenario.get(field), str)'

spans={
 'rouge/damage.py':[(288,357),(359,389)],
 'rouge/operator_engine.py':[(13,29),(79,85),(150,151),(219,226),(616,650),(853,879),(1025,1050),(1297,1316),(1389,1399),(1439,1452),(1462,1483),(1549,1559),(1961,1961)],
 'rouge/reporting.py':[(146,151)],
}
excerpts=[]
for path,ranges in spans.items():
 data=engine if path=='rouge/operator_engine.py' else damage if path=='rouge/damage.py' else old[path]
 lines=data.decode().splitlines()
 excerpts.append({'path':path,'sha256':sha(data),'ranges':[{'start':a,'end':b,'lines':[{'line':i,'text':lines[i-1]} for i in range(a,b+1)]} for a,b in ranges]})
bindings={'fixed_commit':BASE,'author_freeze_sha256':FREEZE_SHA,'frozen_patch_sha256':PATCH_SHA,'baseline_count':723,'unchanged_old_draft':721,'full_git_fixed_blob_and_baseline_byte_check':True,'new_test_sha256':frozen['tests/test_remaining_boolean_condition_text_input.py']['sha256'],'production_changes':{p:{'old_sha256':sha(old[p]),'draft_sha256':sha(engine if p.endswith('operator_engine.py') else damage)} for p in ('rouge/damage.py','rouge/operator_engine.py')},'old_engine_restored_by_removing_only_reset1_signal3_lines':True,'old_damage_restored_by_removing_guard_and_reverting_exact_wrapper_call':True,'guard_sha256':sha(guard),'marker_reset_sha256':sha(reset),'marker_update_sha256':sha(signal),'old83_85_guards_and_every_other_prior_byte_preserved':True}
write_new('bound-author-review-freeze86.json',freeze_bytes)
write_new('bound-current-baseline-freeze86.json',baseline_freeze_bytes)
write_new('bound-frozen-section86.patch',patch_bytes)
write_new('bound-prior-boundary-manifest086.json',prior_manifest_bytes)
write_new('bound-prior-boundary-handoff086.json',prior_handoff_bytes)
save('current-snapshot-and-strip-proof086.json',bindings)
save('guard-scope-and-source-excerpts086.json',{'source_bindings':bindings,'consumers17':sorted(consumers,key=lambda c:(c['path'],c['line'])),'consumer_counts':dict(count),'guard11_other_fields_eligibility':'Fixed owner/number domains exactly match prior source; Mizuki 反移情 and Orchid 强击瓶专家 query actual selected_talents before adding field; nonstr aliases preserved. Gnosis/Ines second consumers and all4 Orchid double_charge reads unchanged.', 'oblvns_marker':{'reset_line':1298,'normal_assign_line':1471,'update_lines':[1473,1474,1475],'skill_override_test':ast.unparse(override.test),'whole_api_marker_expr':ast.unparse(signal_if.body[1].value),'normal_actual_gate':ast.unparse(normal_assign.value),'dominant_construction_line':298,'read_guard_owner':'char_4182_oblvns','legacy_owners_have_no_marker_read':True,'S1_unbound_duration_recharge_None_lines':[1389,1390,1462],'S2_switch_nonrepeat_no_normal_lines':[1394,1397,1398],'marker_not_input_or_public_result':True},'late_error_order':'After core report321, unchanged neural323, Haruka327, Orchidnear329; actual per-core preparation/engine/finishers/report legacy errors remain earlier. No outer universal error-order claim.','excerpts':excerpts})
note='''# 086冻结草案独立静态审查

固定9ef5a46的723个公开py/json逐blob与作者baseline核字节；draft721个未改旧文件全SHA匹配，两个产品文件及新test匹配explicit freeze。去engine仅1行reset+3行marker更新即完全恢复旧engine；去damage晚期guard并还原旧2行wrapper调用即全字节恢复当前旧damage，83/84/85保护没有被覆盖。

calculate1298每次先将对象signal置False。1471实际normal表达式赋值完成后，1473–1475才更新；覆写条件逐AST核对plan858的请求module及实际tv颂乐音符max_cnt>10，只有normal分支语境被换成normal是否实际返回。不是读取用户scenario标记，也不写public结果。S1原unbound来源令1390 duration/recharge=None，在1462得到cycle=None，所以合资格模组且无normal时不拒远程文本。S2原switch/nonrepeat同样不虚构normal。S3实际normal由cycle及当前SP类型/continuous_attacks控制；只有实际normal完成，才使模组覆写后字段重新成为whole-contract消费者。

damage344仅在Oblvns owner分支读combat属性。该owner不属于legacy三owner，296–299的构造和calculate成功返回支配这一读取；legacy分支不碰未定义combat。当前保留wrapper1961原样return Combat(...).calculate()，新局部对象调用与这一未修改wrapper表达式展开一致，没有引入其他数值操作。

其余11field与原12field/17get资格闭合：固定owner/skill，Mizuki实际反移情、Orchid实际强击瓶专家才追加拒绝字段；Gnosis终结reference和Ines费用note二consumer、Orchid四个double_charge箭项/来源参数/自然SP/eventSP读取均原字节保留。只str被新保护拒绝，没有文本解析或非str规则变化。

保护位于321核心报告及83–85旧保护之后，已通过源码次序/旧字节保持证明每次core的准备、engine、finisher、report旧错误先行。外层deployment/wine会多次评价或有后续错误，不能称所有外层错误都先于新保护。此报告没有执行runtime行为或新的产品方案。

旧readonly9附件只复hash绑定，不重复上游28来源/240rank/12module语义/36probes。0 calculate_damage、0 selected_talents或其他产品helper、0测试、Qt、Wine、tracked修改。正式父审负责saved268与不同fresh/newtests；这里的静态PASS不替代父数值PASS或root当前集成与全量检查。原生clock、资源、附着与live游戏仍未知。
'''
write_new('NOTE.md',note.encode())
receipt={'status':'PASS_FINAL_STATIC_GUARDS_ONLY','section':86,'fixed_commit':BASE,'review_freeze_sha256':FREEZE_SHA,'patch_sha256':PATCH_SHA,'baseline723_verified':True,'unchanged_old_draft721_verified':True,'all_prior_product_bytes_preserved_except_exact_frozen_changes':True,'actual_selected_talent_qualification_verified_static':True,'actual_normal_execution_signal_and_exact_module_override_verified_static':True,'legacy_branch_dominated_Combat_use':True,'current_wrapper_expansion_source_equivalent':True,'Gnosis_Ines_secondary_and_Orchid4_consumers_unchanged':True,'old_per_core_error_order_preserved_static':True,'outer_universal_error_order_claimed':False,'marker_public_schema_or_input_change':False,'new_calculate_API_calls':0,'new_product_helper_calls':0,'tests_run':0,'GUI_calls':0,'Wine_calls':0,'tracked_changes':0,'prior_source28_rank240_module12_or_probe36_reexecuted':False,'parent_numeric_review_separate_pending_at_static_seal':True,'unknown_native_clock_resource_attachment_or_live_state_inferred':False,'preparation_failures':[],'source_complete_copies_in_manifest':False}
save('receipt-static-final086.json',receipt)
save('handoff-static-final086.json',{'status':receipt['status'],'receipt_path':str(OUT/'receipt-static-final086.json'),'receipt_sha256':sha((OUT/'receipt-static-final086.json').read_bytes()),'source_script_path':str(OUT/'review_static_guards086.py'),'source_script_sha256':sha((OUT/'review_static_guards086.py').read_bytes()),'explicit_final_frozen':True,'all_runtime_API_helper_tests_GUI_Wine_tracked':0,'scope':'current frozen86 guard scope/normal signal/legacy dominance/per-core olderror source only; parent owns numerical and fresh checks'})
files=[]
for path in sorted(OUT.iterdir()):
 if path.is_file():
  data=path.read_bytes();files.append({'source_path':str(path),'archive_path':path.name,'bytes':len(data),'sha256':sha(data)})
save('public-artifacts-manifest086.json',{'format_version':1,'status':'FINAL_SEALED','section':86,'files':files,'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files),'manifest_self_excluded':True,'public_artifacts_only':True,'excluded':['author/baseline and draft complete execution copies: 723 fixed Git byte receipt retained','original raw tables/240rank/12module/probe36 copies: immutable prior source packet bound, not repeated','numeric saved268/fresh/newtest records: parent formal reviewer owns these']})
for row in files:checked(Path(row['source_path']),row['sha256'],row['bytes'])
print(json.dumps({'status':receipt['status'],'handoff_sha256':sha((OUT/'handoff-static-final086.json').read_bytes()),'receipt_sha256':sha((OUT/'receipt-static-final086.json').read_bytes()),'manifest_sha256':sha((OUT/'public-artifacts-manifest086.json').read_bytes()),'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files)},ensure_ascii=False))
