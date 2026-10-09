"""Author stdlib Source builder only; never import/run prepared code or project."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

CONT=Path('/workspace/.continuation')
ADAPTER_BASIS=CONT/'full110-suite-adapters-source-v1'
WINDOW_BASIS=CONT/'full110-bounded-window-source-active-v1'
ADAPTER_OUT=CONT/'full115-suite-adapters-source-v1'
WINDOW_OUT=CONT/'full115-bounded-window-source-draft-v1'
SHA=lambda b:hashlib.sha256(b).hexdigest()
JS=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')


def transform(old,rows):
    fresh=old
    for row in rows:
        assert fresh.count(row['before'])==1, row['before']
        fresh=fresh.replace(row['before'],row['after'],1)
    inverse=fresh
    for row in reversed(rows):
        assert inverse.count(row['after'])==1, row['after']
        inverse=inverse.replace(row['after'],row['before'],1)
    assert inverse==old
    compile(ast.parse(fresh.decode()),'<prepared-source-only>','exec')
    return fresh


def row(before,after):
    return {'before':before.encode(),'after':after.encode()}


def serial(rows):
    return [{'before':v['before'].decode(),'after':v['after'].decode()} for v in rows]

suite_rows=[
 row("'suite_common110.py', 'wine_capability_probe110.py', 'wine_full110.py'", "'suite_common115.py', 'wine_capability_probe115.py', 'wine_full115.py'"),
 row("'wine_selected110.py', 'source-contract.json'", "'wine_selected115.py', 'source-contract.json'"),
 row("guard.get('section') == 110 and type(guard.get('section')) is int", "guard.get('section') == 115 and type(guard.get('section')) is int"),
 row('An actual completed110 Root guard is required; historical095 or pending guards are forbidden','An actual final115 Root guard is required; historical095 or pending guards are forbidden'),
 row('Actual maintained rouge/tests/scripts .py/.json set or bytes differ from Root110 guard','Actual maintained rouge/tests/scripts .py/.json set or bytes differ from Root115 guard'),
 row('Exact sealed adapter Source differs from Root110 guard','Exact sealed adapter Source differs from Root115 guard'),
 row("'format_version': 1, 'section': 110, 'checked_at': now()", "'format_version': 1, 'section': 115, 'checked_at': now()"),
]
old=(ADAPTER_BASIS/'suite_common110.py').read_bytes()
new=transform(old,suite_rows)
(ADAPTER_OUT/'suite_common115.py').write_bytes(new)
adapters=[{'old':'suite_common110.py','new':'suite_common115.py','local_transports':serial(suite_rows),'old_bytes':len(old),'old_sha256':SHA(old),'new_bytes':len(new),'new_sha256':SHA(new),'inverse_byte_exact':True}]
for stem in ['wine_capability_probe','wine_full','wine_selected']:
    old=(ADAPTER_BASIS/(stem+'110.py')).read_bytes()
    rows=[row('from suite_common110 import','from suite_common115 import')]
    new=transform(old,rows)
    (ADAPTER_OUT/(stem+'115.py')).write_bytes(new)
    adapters.append({'old':stem+'110.py','new':stem+'115.py','local_transports':serial(rows),'old_bytes':len(old),'old_sha256':SHA(old),'new_bytes':len(new),'new_sha256':SHA(new),'inverse_byte_exact':True})
old_ast=ast.parse((ADAPTER_BASIS/'suite_common110.py').read_text())
new_ast=ast.parse((ADAPTER_OUT/'suite_common115.py').read_text())
old_fn={n.name:ast.dump(n,include_attributes=False) for n in old_ast.body if isinstance(n,ast.FunctionDef)}
new_fn={n.name:ast.dump(n,include_attributes=False) for n in new_ast.body if isinstance(n,ast.FunctionDef)}
assert set(old_fn)==set(new_fn)
changed=[name for name in old_fn if old_fn[name]!=new_fn[name]]
assert changed==['bind_suite','common_receipt'],changed
# Function-body changes are section gates/diagnostic/receipt labels only;
# capability, exact TEST_IDS, AvailableResult gate and classifiers remain whole AST.
for n in ['TEST_IDS','SKIP_REASON','KERNELBASE_SHA','NTDLL_SHA','EXPECTED_CLASSIFIER_AST']:
    def assignment(tree):
        return next(v for v in tree.body if isinstance(v,ast.Assign) and any(isinstance(t,ast.Name) and t.id==n for t in v.targets))
    assert ast.dump(assignment(old_ast),include_attributes=False)==ast.dump(assignment(new_ast),include_attributes=False)
for record in adapters[1:]:
    a=ast.parse((ADAPTER_BASIS/record['old']).read_text())
    b=ast.parse((ADAPTER_OUT/record['new']).read_text())
    for v in ast.walk(b):
        if isinstance(v,ast.ImportFrom) and v.module=='suite_common115':v.module='suite_common110'
    assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)

window_rows=[
 row('"""Inactive bounded full110 Window Source draft; Root final109 guard binding pending."""','"""Inactive bounded full115 Window Source draft; Root final115 guard binding pending."""'),
 row('# Draft deliberately refuses execution before Root final109 Source binding.','# Draft deliberately refuses execution before Root final115 Source binding.'),
 row("_SOURCE110_GUARD_SHA256 = 'ac629aec8d42caefa2ff53497bd34929d45c1fd4d72b75e1c06a5b8ee19a6b4b'",'_SOURCE115_GUARD_SHA256 = None'),
 row('_SOURCE110_MAINTAINED_COUNT = 753','_SOURCE115_MAINTAINED_COUNT = None'),
 row('if _SOURCE110_GUARD_SHA256 is None or _SOURCE110_MAINTAINED_COUNT is None:','if _SOURCE115_GUARD_SHA256 is None or _SOURCE115_MAINTAINED_COUNT is None:'),
 row('Inactive full110 Source draft: actual completed109/final110 guard not bound','Inactive full115 Source draft: actual final115 guard not bound'),
 row('hexdigest() != _SOURCE110_GUARD_SHA256:','hexdigest() != _SOURCE115_GUARD_SHA256:'),
 row('Exact Root final109/final110 public Source guard bytes required','Exact Root final115 public Source guard bytes required'),
 row("len(_expected100)!=_SOURCE110_MAINTAINED_COUNT:","len(_expected100)!=_SOURCE115_MAINTAINED_COUNT:"),
 row('Exact actual completed109/final110 maintained Source count is required','Exact actual final115 maintained Source count is required'),
 row('Completed109/final110 additional Source map must include CORE registration','Final115 additional Source map must include CORE registration'),
 row('Completed109/final110 maintained Source drift before project imports','Final115 maintained Source drift before project imports'),
 row('Completed109/final110 supplemental Source drift before project imports','Final115 supplemental Source drift before project imports'),
 row('Fresh full110 attempt1 deadline of1200 seconds reached','Fresh full115 attempt1 deadline of1200 seconds reached'),
 row("'scope': 'actual full110 attempt1 hard deadline', 'after_section': 110", "'scope': 'actual full115 attempt1 hard deadline', 'after_section': 115"),
 row("'kind': 'FULL110_ATTEMPT1_APPENDED_CHECK_PROGRESS'", "'kind': 'FULL115_ATTEMPT1_APPENDED_CHECK_PROGRESS'"),
 row("'after_section': 110, 'attempt': 1, 'passed': False", "'after_section': 115, 'attempt': 1, 'passed': False"),
 row("'full110-progress.json.tmp'", "'full115-progress.json.tmp'"),
 row("os.replace(temporary, OUT / 'full110-progress.json')", "os.replace(temporary, OUT / 'full115-progress.json')"),
 row("'after_section':110,'current_maintained_source_count_expected':_SOURCE110_MAINTAINED_COUNT", "'after_section':115,'current_maintained_source_count_expected':_SOURCE115_MAINTAINED_COUNT"),
 row("'specialist101_109_validation_in_this_runner':False", "'specialist101_115_validation_in_this_runner':False"),
 row("'full110_attempt':1,'progress_checkpoint_file':'full110-progress.json'", "'full115_attempt':1,'progress_checkpoint_file':'full115-progress.json'"),
 row('Inherited actual successful full105 progressv2 functional suite transported to actual completed109/final110 Source. Separate96-109 specialist receipts required. Legacy projection-only/producer/no-alias limitations remain unchanged. No old095 complete invocation vector, native Windows, capture or chat certification.','Inherited actual successful full105 progressv2 functional suite transported through Source110 to final115 Source. Separate96-115 specialist receipts required. Legacy projection-only/producer/no-alias limitations remain unchanged. No old095 complete invocation vector, native Windows, capture or chat certification.'),
]
old=(WINDOW_BASIS/'window.py').read_bytes()
assert SHA(old)=='58b84c583bddc1c4400c88d198ef4e1779574c560b916747b7c92037c67c57bb'
new=transform(old,window_rows)
(WINDOW_OUT/'window.py').write_bytes(new)
a=ast.parse(old.decode());b=ast.parse(new.decode())
old_assert=[ast.dump(v,include_attributes=False) for v in ast.walk(a) if isinstance(v,ast.Assert)]
new_assert=[ast.dump(v,include_attributes=False) for v in ast.walk(b) if isinstance(v,ast.Assert)]
assert len(old_assert)==831 and new_assert==old_assert
old_try=max((v for v in ast.walk(a) if isinstance(v,ast.Try)),key=lambda v:v.end_lineno-v.lineno)
new_try=max((v for v in ast.walk(b) if isinstance(v,ast.Try)),key=lambda v:v.end_lineno-v.lineno)
def source_bytes(raw,node):
    return b''.join(raw.splitlines(keepends=True)[node.lineno-1:node.end_lineno])
assert source_bytes(old,old_try)==source_bytes(new,new_try)
assert ast.dump(old_try,include_attributes=False)==ast.dump(new_try,include_attributes=False)
windows={'old_window_sha256':SHA(old),'new_window_sha256':SHA(new),'old_window_bytes':len(old),'new_window_bytes':len(new),'window_local_transports':serial(window_rows),'inverse_byte_exact':True,'all_831_assert_AST_order_same':True,'functional_Try_bytes':len(source_bytes(new,new_try)),'functional_Try_sha256':SHA(source_bytes(new,new_try)),'functional_Try_AST_sha256':SHA(ast.dump(new_try,include_attributes=False).encode()),'functional_Try_byte_exact_to_actual110_Source':True,'guard_constants_NULL':True}
for name in ['rows090','saved89_states090','expected89_contract090']:
    def assignment(tree):
        return next(v for v in ast.walk(tree) if isinstance(v,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in v.targets))
    x,y=assignment(a),assignment(b)
    assert source_bytes(old,x)==source_bytes(new,y)
windows['three_large_public_literal_assignments_byte_same']=True
super_rows=[row('inactive full110 attempt1 Source launcher','inactive full115 attempt1 Source launcher'),row("'after_section': 110, 'full110_attempt': 1", "'after_section': 115, 'full115_attempt': 1")]
super_old=(WINDOW_BASIS/'supervisor110.py').read_bytes()
assert SHA(super_old)=='89e453eb52e69666d702f6240db22e803899c63efb29a8cd5b486b27337b3811'
super_new=transform(super_old,super_rows)
(WINDOW_OUT/'supervisor115.py').write_bytes(super_new)
sa=ast.parse(super_old.decode());sb=ast.parse(super_new.decode())
for name in ['session_members','finish_owned_session']:
    x=next(v for v in sa.body if isinstance(v,ast.FunctionDef) and v.name==name)
    y=next(v for v in sb.body if isinstance(v,ast.FunctionDef) and v.name==name)
    assert source_bytes(super_old,x)==source_bytes(super_new,y)
windows.update({'supervisor_local_transports':serial(super_rows),'old_supervisor_sha256':SHA(super_old),'new_supervisor_sha256':SHA(super_new),'supervisor_inverse_byte_exact':True,'owned_session_methods_byte_same':True,'deadline_seconds':1200,'runtime_executed':False,'product_pass':False,'section_complete':False})
JS(WINDOW_OUT/'metadata-local-transports.json',windows)
(WINDOW_OUT/'window-local.diff').write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='active110/window.py',tofile='inactive115/window.py')))
(WINDOW_OUT/'supervisor-local.diff').write_text(''.join(difflib.unified_diff(super_old.decode().splitlines(True),super_new.decode().splitlines(True),fromfile='active110/supervisor110.py',tofile='inactive115/supervisor115.py')))
JS(ADAPTER_OUT/'source-contract.json',{'kind':'INACTIVE_SOURCE_ONLY_FULL115_ADAPTERS','section':115,'runtime_executed':False,'apply_or_execution_ready':False,'product_pass':False,'section_complete':False,'basis_directory':str(ADAPTER_BASIS),'basis_manifest_sha256':SHA((ADAPTER_BASIS/'manifest.json').read_bytes()),'basis_current110_runtime_claim':False,'only_metadata_transports':adapters,'future_actual':{'Root_guard_path':None,'Root_guard_sha256':None,'complete_maintained_Source_count':None,'complete_Source_map':None,'CORE_additional_map':None,'selector_union':None,'independent_capability_probe_path':None,'independent_capability_probe_sha256':None,'independent_capability_probe_primary_path':None,'Linux_full_outcome':None,'Wine_full_outcome':None,'Wine_selected_outcome':None,'Window115_or_Saved_outcome':None},'common_changed_functions_metadata_only':changed,'all_other_common_function_AST_same':True,'capability_and_classifier_constants_AST_same':True,'exact3_skip_ids_same':True,'classifier_AST_gate_same':True,'per_run_fresh_controls_same':True,'capability_skip_counted_passed':0,'skip_rows_overlap_ordinary':True,'U_classifier_unchanged':True,'new115_report_components_functional_acceptance':'Root separate115 actual function checks; these inherited suites are additional regression, not a section milestone','old095_deferred':True})
JS(WINDOW_OUT/'AUTHOR_SOURCE_CHECK.json',{'kind':'SOURCE_ONLY_INACTIVE_FULL115','stdlib_Source_builder_only':True,'project_or_helper_or_codec_or_test_or_Qt_or_Wine_or_Git_executed':False,'tracked_changed':False,'local_window_transports':len(window_rows),'local_supervisor_transports':len(super_rows),'all_831_assert_AST_order_same':True,'whole_functional_Try_byte_same':True,'three_public_large_literal_byte_same':True,'owned_supervisor_methods_byte_same':True,'compile_only':True,'future_actual_final115_guard':None,'future_actual_final115_Source_count':None,'deadline_seconds':1200,'Root110_actual_runtime_currently_pending_no_PASS_claim':True})
print(json.dumps({'adapter_metadata_transports':len(suite_rows),'window_metadata_transports':len(window_rows),'supervisor_metadata_transports':len(super_rows),'831_assert_AST_same':True,'whole_try_byte_same':True,'future_115_binding_NULL':True,'runtime_executed':False}))
