"""AST/raw-byte preflight only; no runner/codec/project execution."""
from pathlib import Path
import ast
import hashlib
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=Path('/workspace/rougezhushou')
def sha(data):return hashlib.sha256(data).hexdigest()
def descriptor(path):
    data=path.read_bytes();return {'source_path':str(path),'bytes':len(data),'sha256':sha(data)}
assert len(sys.argv)==2
source_path=Path(sys.argv[1]);source_bytes=source_path.read_bytes();source=json.loads(source_bytes)
assert sha(source_bytes)=='0fbfe28e2528ae9987f9f260bfed0068b1e16edf02274ea3349cd6d988aa2180'
assert source['passed'] is True and len(source['source_sha256_after'])==732
for rel,value in source['source_sha256_after'].items():assert sha((ROOT/rel).read_bytes())==value,rel
runner=HERE/'wine-account-window-093-pending.py';body=runner.read_text();tree=ast.parse(body)
assert isinstance(tree.body[0],ast.Assign) and tree.body[0].targets[0].id=='PENDING_PREPARATION' and tree.body[0].value.value is True
assert isinstance(tree.body[1],ast.If) and tree.body[1].test.id=='PENDING_PREPARATION'
assert isinstance(tree.body[1].body[0],ast.Raise)
assert body.count('PENDING_PREPARATION = True')==1 and body.count('PENDING_ACTUAL_ROOT_SOURCE_SHA256')==1
assert not any(isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='blockSignals' for node in ast.walk(tree))
for node in ast.walk(tree):
    if isinstance(node,ast.Assign):
        assert all(not isinstance(target,ast.Attribute) or target.attr not in ('preserve_original','operator_observations','state') for target in node.targets)
assert not any(isinstance(node,ast.ClassDef) for node in ast.walk(tree))
functions={node.name:node for node in tree.body if isinstance(node,ast.FunctionDef)}
assert all(name in functions for name in ('flat_native','native_inverse','snapshot','profile','trace','filesystem'))
for name in ('flat_native','native_inverse'):
    assert any(isinstance(node,ast.While) for node in ast.walk(functions[name]))
    assert not any(isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id==name for node in ast.walk(functions[name]))
plan_path=HERE/'account-window-plan093.json';plan=json.loads(plan_path.read_text())
assert sha((ROOT/'rouge/app.py').read_bytes())==plan['candidate_v2_app']['sha256']
assert sha((ROOT/'rouge/account_cache.py').read_bytes())==plan['candidate_v2_helper']['sha256']
assert len(plan['constraints'])==12
cases=plan['cases'];steps=[row for case in cases for row in case['steps']]
assert len(cases)==31 and len(steps)==132
assert len({case['id'] for case in cases})==31
assert len({case['id']+'/'+row['id'] for case in cases for row in case['steps']})==132
assert sum(row['action']=='button' for row in steps)==2
assert {row['screenshot'] for row in steps if 'screenshot' in row}==set(plan['expected_PNGs'])
allowed={'startup','select','observe','sample','run','button','restore_level','level','run_training','overview','timing','relic_context','relic','view_top'}
assert {row['action'] for row in steps}<=allowed
assert all(case['steps'][0]['action']=='startup' for case in cases)
assert all('id' in row['operator'] for row in steps if row['action'] in ('observe','sample'))
known=set(json.loads((ROOT/'rouge/data/operator-profiles.json').read_text())['operators']) | set(json.loads((ROOT/'rouge/data/catalog.json').read_text())['operators'])
assert all(row['operator']['id'] in known for row in steps if row['action'] in ('observe','sample'))
output=HERE/'source-only-preflight093.json';assert not output.exists()
proof={'format_version':1,'status':'CODE_READY_AST_RAW_SOURCE_PASS_RUNTIME_UNRUN_ACTUAL732_BOUND_FOR_FINAL',
       'passed':True,'root_source':descriptor(source_path),'pending_runner':descriptor(runner),'plan':descriptor(plan_path),
       'candidate_v2_actual_app_and_helper_exact':True,'actual_source_count':732,'unchanged_existing_count':728,
       'AST_parse_only':True,'earliest_pending_true_raise_before_imports':True,'no_runner_signal_blocking':True,
       'no_fixture_assignment_to_preservation_flag_account_alias_or_RunState_state':True,
       'flat_codec_iterative_source_check_only':True,'codec_executed_in_preparation':False,
       'native_inverse_runtime_assertions':'Each actual snapshot verifies encode(inverse(graph)) == graph before recording full JSON projection.',
       'base_actual92_Git':'f509d186e501bfcfd042e45b46e398ec756840ec',
       'base_sources_Git_readonly_check':'HEAD exact f509 and git diff --name-only HEAD over RunState/catalog/profiles/summary/branch/relic/offline scope files returned empty; root actual guard binds all their current bytes.',
       'plan_counts':plan['counts'],'runtime_executed':False,'project_imports':0,'API':0,'helper':0,'formatter':0,'tests':0,'Qt':0,'Wine':0,'tracked_writes':0}
output.write_text(json.dumps(proof,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'proof':descriptor(output),'pending':descriptor(runner),'plan':descriptor(plan_path),'project_calls':0}))
