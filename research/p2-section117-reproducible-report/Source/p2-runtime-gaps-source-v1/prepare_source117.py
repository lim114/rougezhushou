"""Pure stdlib source composition, AST comparison, compile-noexec and sealing."""
from pathlib import Path
import ast
import hashlib
import json
from datetime import datetime,timezone

BASE=Path(__file__).parent
ROOT=Path('/workspace/rougezhushou')
def pin(data):return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def write(name,value):
    raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
    (BASE/name).write_bytes(raw)
    return pin(raw)

before=(ROOT/'rouge/reporting.py').read_bytes()
source=before.decode()
helpers=(BASE/'helpers117.py.txt').read_text()
anchor='def build_report(scenario,result):\n'
call_before='    sections.extend(current_output_breakdown_sections(result))\n'
call_after=call_before+''.join('    sections.extend('+name+'(scenario,result))\n' for name in (
    'reproducible_context_sections','event_clock_reference_sections','output_domain_comparison_sections'))
assert source.count(anchor)==source.count(call_before)==1
candidate=source.replace(anchor,helpers+anchor,1).replace(call_before,call_after,1)
assert before.count(b'\r')==0
(BASE/'reporting.before.py').write_bytes(before)
(BASE/'reporting.candidate.py').write_text(candidate)
old_tree=ast.parse(source)
new_tree=ast.parse(candidate)
old_defs={node.name:node for node in old_tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef))}
new_defs={node.name:node for node in new_tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef))}
unchanged=[]
for name,node in old_defs.items():
    if name=='build_report':continue
    assert ast.dump(node,include_attributes=False)==ast.dump(new_defs[name],include_attributes=False),name
    unchanged.append(name)
build_before=old_defs['build_report']
build_after=new_defs['build_report']
extra=[]
for index,node in enumerate(build_after.body):
    if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute):
        if node.value.func.attr=='extend' and len(node.value.args)==1 and isinstance(node.value.args[0],ast.Call):
            func=node.value.args[0].func
            if isinstance(func,ast.Name) and func.id in ('reproducible_context_sections','event_clock_reference_sections','output_domain_comparison_sections'):
                extra.append(index)
for index in reversed(extra):build_after.body.pop(index)
assert len(extra)==3
assert ast.dump(build_before,include_attributes=False)==ast.dump(build_after,include_attributes=False)
for name in ('reporting.before.py','reporting.candidate.py','test_reproducible_report_117.py'):
    compile((BASE/name).read_text(),str(BASE/name),'exec')
cloud=(ROOT/'scripts/verify_cloud.py').read_bytes()
old_cloud='    "tests.test_current_output_breakdown_115",\n'
new_cloud='    "tests.test_reproducible_report_117",\n'+old_cloud
assert cloud.decode().count(old_cloud)==1
(BASE/'verify_cloud.before.py').write_bytes(cloud)
(BASE/'verify_cloud.candidate.py').write_text(cloud.decode().replace(old_cloud,new_cloud,1))
compile((BASE/'verify_cloud.candidate.py').read_text(),str(BASE/'verify_cloud.candidate.py'),'exec')
transport={'kind':'SOURCE_ONLY_SECTION117_LOCAL_TRANSPORT_NOT_RUNTIME_PASS',
    'section':117,'root_runtime_executed':False,'tracked_files_mutated':False,
    'whole_source_rebind_policy':'Captured original pins are preparation-time source. If section116 changes reporting/cloud, Root must reread actual bytes, prove these exact old anchors occur once, recompose locally preserving every other AST/body and rebind the actual guard; never overwrite current files using full candidate snapshots.',
    'targets':[
        {'path':'rouge/reporting.py','snapshot_before':'reporting.before.py','composed_candidate':'reporting.candidate.py','before':pin(before),'candidate':pin(candidate.encode()),
         'blocks':[{'old':anchor,'new':helpers+anchor},{'old':call_before,'new':call_after}]},
        {'path':'scripts/verify_cloud.py','snapshot_before':'verify_cloud.before.py','composed_candidate':'verify_cloud.candidate.py','before':pin(cloud),'candidate':pin((BASE/'verify_cloud.candidate.py').read_bytes()),
         'blocks':[{'old':old_cloud,'new':new_cloud}]},
        {'path':'tests/test_reproducible_report_117.py','require_absent':True,'source':'test_reproducible_report_117.py','candidate':pin((BASE/'test_reproducible_report_117.py').read_bytes())}]}
write('transport.json',transport)
checks={'kind':'SOURCE_ONLY_AST_AND_BYTE_COMPOSITION_CHECK',
    'generated_at_utc':datetime.now(timezone.utc).isoformat(),
    'source_only':True,'project_imports_executed':False,'runtime_pass_claimed':False,
    'all_preexisting_other_definitions_AST_unchanged':unchanged,
    'build_report_only_three_additive_extend_calls':True,
    'new_helper_definitions':3,'compile_noexec':['reporting.before.py','reporting.candidate.py','test_reproducible_report_117.py','verify_cloud.candidate.py'],
    'candidate_test_method_count':sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(ast.parse((BASE/'test_reproducible_report_117.py').read_text()))),
    'current_source_pins':{str(path.relative_to(ROOT)):pin(path.read_bytes()) for path in (
        ROOT/'rouge/reporting.py',ROOT/'rouge/timing.py',ROOT/'rouge/operator_engine.py',ROOT/'rouge/damage.py',ROOT/'rouge/estimate.py',ROOT/'rouge/catalog.py',ROOT/'rouge/run_modifiers.py',ROOT/'rouge/relics.py',ROOT/'scripts/verify_cloud.py',ROOT/'tests/test_token_full_cast_tail_111.py',ROOT/'tests/test_ammo_observation_window_113.py')}}
write('source-checks.json',checks)
print(json.dumps({'source_only':True,'candidate_report':pin(candidate.encode()),'test_methods':checks['candidate_test_method_count'],'existing_AST_defs_preserved':len(unchanged)},ensure_ascii=False))
