"""Freeze source-only preparation and final focused root-only runner; no product imports."""
from pathlib import Path
import ast,hashlib,json,pprint,shutil,subprocess
HERE=Path(__file__).resolve().parent
ROOT=Path('/workspace/rougezhushou')
FINAL=Path('/workspace/.continuation/ui-091-focused-final')
def sha(data):return hashlib.sha256(data).hexdigest()
def desc(path):
    data=path.read_bytes()
    return {'source_path':str(path),'bytes':len(data),'sha256':sha(data)}
def save(directory,name,obj):
    path=directory/name
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return path
def manifest(directory,name,status,rows):
    assert len({r['archive_path'] for r in rows})==len(rows)
    return save(directory,name,{'format_version':1,'status':status,'files':rows,'file_count':len(rows),'total_bytes':sum(r['bytes'] for r in rows)})
def row(path,archive):return {**desc(path),'archive_path':archive}

assert not FINAL.exists(),'New final directory only; do not overwrite prior frozen evidence'
source_path=Path('/workspace/.continuation/root-source-091.json')
source=json.loads(source_path.read_text())
source_map=source['source_sha256_after']
assert source['passed'] is True and len(source_map)==730
assert source['unchanged_maintained']==726 and len(source['changed_maintained'])==4
author=json.loads((HERE/'frozen-authors-and-expected-four-targets091.json').read_text())
current=[]
for rel,expected in source_map.items():
    path=ROOT/rel
    data=path.read_bytes()
    assert sha(data)==expected,('actual source mismatch',rel)
    current.append({'relative_path':rel,'bytes':len(data),'sha256':expected})
for rel,binding in author['expected_integrated_target_files'].items():
    assert source_map[rel]==binding['sha256']
    assert (ROOT/rel).read_bytes()==Path(binding['source_path']).read_bytes()
head=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
assert head=='2cbc45f03f99ed4f04b9c7e2612b58542f909168'
plan=json.loads((HERE/'focused-window-state-plan091.json').read_text())
assert len(plan['rows'])==24
assert sum(r.get('numerical_result_expected',True) for r in plan['rows'])==21
assert sum(bool(r.get('explicit_click')) for r in plan['rows'])==5
assert len({r['id'] for r in plan['rows']})==24
body=(HERE/'focused-runner-body091.txt').read_text()
assert body.count('SOURCE_LITERAL')==body.count('PLAN_LITERAL')==1
body=body.replace('SOURCE_LITERAL',pprint.pformat(source_map,sort_dicts=False,width=120))
body=body.replace('PLAN_LITERAL',pprint.pformat(plan,sort_dicts=False,width=120))
pending_prefix='PENDING_PREPARATION = True\nif PENDING_PREPARATION:\n    raise SystemExit("Pending focused91 preparation; root alone may execute only the final source-bound runner")\n'
final_prefix=pending_prefix.replace(' = True\n',' = False\n',1)
pending=pending_prefix+body
final=final_prefix+body
ast.parse(pending);ast.parse(final)
save(HERE,'actual-joined730-source-binding091.json',{
    'format_version':1,'status':'ACTUAL_WORKING_SOURCE_BOUND_ROOT_APPLIED_NOT_HEAD_BLOBS',
    'root_source_receipt':desc(source_path),'HEAD_identity':head,'workingtree_identity':'Actual joined section91 four changed product bytes; source730 is working-file hash map, not old HEAD Git blobs.',
    'source_map_count':730,'unchanged_maintained':726,'changed_maintained':source['changed_maintained'],
    'actual_files':current,'product_calls':0,'Qt_calls':0,'Wine_calls':0})
(HERE/'wine-focused-mainwindow-091-pending.py').write_text(pending,encoding='utf-8')
save(HERE,'source-only-preparation-stage-handoff091.json',{
    'format_version':1,'status':'SEALED_SOURCE_ONLY_PENDING_NOT_GUI_PASS','planned_states':24,
    'numerical_states':21,'early_None_states':3,'pending_runner':desc(HERE/'wine-focused-mainwindow-091-pending.py'),
    'source_binding':desc(HERE/'actual-joined730-source-binding091.json'),'API':0,'helper':0,'formatter':0,'tests':0,'Qt':0,'Wine':0,
    'future_execution':'Root sole final focused MainWindow. No full90 or old4217 rerun.'})
stage_rows=[row(p,'focused091/initial-preparation/'+str(p.relative_to(HERE))) for p in sorted(HERE.rglob('*')) if p.is_file()]
stage=manifest(HERE,'public-artifacts-manifest-source-only-stage091.json','FINAL_STABLE_SOURCE_ONLY_PENDING_STAGE',stage_rows)
# From here the preparation tree is immutable. Final is a separate additive packet.
FINAL.mkdir(mode=0o700)
save(FINAL,'actual-joined730-source-binding091.json',json.loads((HERE/'actual-joined730-source-binding091.json').read_text()))
shutil.copyfile(HERE/'focused-window-state-plan091.json',FINAL/'focused-window-state-plan091.json')
shutil.copyfile(source_path,FINAL/'root-source-091-exact-snapshot.json')
(FINAL/'wine-focused-mainwindow-091-final.py').write_text(final,encoding='utf-8')
save(FINAL,'pending-to-final-release-proof091.json',{
    'format_version':1,'passed':True,'original_pending':desc(HERE/'wine-focused-mainwindow-091-pending.py'),
    'final_runner':desc(FINAL/'wine-focused-mainwindow-091-final.py'),
    'difference':'Only earliest literal PENDING_PREPARATION=True to False. Whole following source hashes, input plan, body and assertions identical.',
    'exact_reverse_restores_pending':final.replace(final_prefix,pending_prefix,1)==pending,
    'actual_working730_map_bound':True,'actual_four_candidate_bytes_bound':True,'AST_parse_only':True,'runner_executed':False,
    'API':0,'helper':0,'formatter':0,'tests':0,'Qt':0,'Wine':0})
save(FINAL,'focused-runner-scope-and-artifacts091.json',{
    'format_version':1,'status':'FINAL_SOURCE_FROZEN_ACTUAL_WINDOW_PENDING_ROOT',
    'base_HEAD':head,'actual_source_count':730,'joined_working_source':True,
    'planned_states':24,'planned_numerical_states':21,'planned_early_None_states':3,
    'explicit_button_requests':5,'explicit_three_text_requests':63,
    'expected_actual_API_entry_count':'Measured; 5 explicit clicks + all existing automatic refreshes. Do not infer numeric call count from 21 states.',
    'formatter_entry_count':'Measured format_estimate/default/technical individually including estimate delegation and real render refreshes.',
    'readonly_metadata':'Selected owner/rank SP type is projected from actual source-guarded catalog/profile JSON and compared to real selected controls.',
    'same_call_Amiya_talent_trace':'Observe existing operator_engine.talent returns via sys.profile; no helper invocation added. Empty timing keeps ordinary finite conditional parameter clocks, does not require restricted dictionary or claim native clock.',
    'private_state':'Temporary run/account/settings/chat paths established before MainWindow construction; no capture target, auto polling or chat request.',
    'checkpoint':'Lossless gzip before each state/action, immediately after actual raw/result and three texts, then after assertions. Saves actual API caller native before/after and main-thread library entries. Failing state remains in archive; no success replay authorized.',
    'result_transport':'Each numeric state full native tagged tree plus independent JSON projection and own estimate/default/technical texts; early None states actual visible status and zero new numeric API entries.',
    'output_artifacts':['wine-focused-mainwindow-091.json','wine-focused-mainwindow-091-records.json.gz','wine-focused-continuous-091.png','wine-focused-deepcolor-091.png'],
    'failure_artifact':'wine-focused-mainwindow-failure-091.png','success_PNG_count':2,
    'completed_source_only_preparation':True,'Qt_executed':False,'Wine_executed':False,'API_preflight_executed':False,
    'old_full90_4283_or4217_rerun':False,'source16_author6_or_other_saved_matrices_rerun':False,
    'root_execution':'Copy final runner after verifying packet + final independent receipt; execute exactly once on existing root Wine prefix. Do not run pending preparation.',
    'user_three_attempt_policy':'Preserve complete failure; same issue unresolved after three attempts is deferred, with existing successful rows retained.'})
(FINAL/'CHECKPOINT.md').write_text('FINAL STOPWRITE: focused91 source-only packet frozen. 24 states (21 numeric + 3 real None early statuses), 5 explicit button requests, 63 explicit report requests; actual automatic/API/formatter/library entries remain pending root sole execution. Joined working730 source is bound to root-source-091 receipt (726 unchanged plus 4 exact author targets), HEAD remains full90 2cbc. Original early-return and ordinary-Amiya preparation mistakes, original bodies/plans and corrected source contracts remain archived; no product/API/helper/formatter/tests/Qt/Wine calls. Initial pending stage is immutable. Next: sole independent static formal, root single actual focused MainWindow, view two real PNG and archive actual lossless checkpoint/receipt.\n',encoding='utf-8')
save(FINAL,'handoff-focused-mainwindow091.json',{
    'format_version':1,'status':'FINAL_STOPWRITE_SOURCE_FROZEN_ROOT_ACTUAL_WINDOW_PENDING',
    'runner':desc(FINAL/'wine-focused-mainwindow-091-final.py'),
    'plan':desc(FINAL/'focused-window-state-plan091.json'),
    'source_binding':desc(FINAL/'actual-joined730-source-binding091.json'),
    'root_source_snapshot':desc(FINAL/'root-source-091-exact-snapshot.json'),
    'initial_stage_manifest':desc(stage),'initial_stage_files':len(stage_rows),
    'planned_checks':24,'planned_numeric':21,'planned_None_early':3,
    'explicit_buttons':5,'explicit_text_requests':63,'success_PNGs':2,
    'prepared_project_calls':0,'prepared_Qt_calls':0,'prepared_Wine_calls':0,
    'formal_gate':'sole source080 static independent, no fresh API/helper/formatter/test/Qt/Wine. Actual root entry counts must be observed.',
    'immutable_authors_reused':{key:value for key,value in author.items() if key.endswith('manifest')},
    'packet_manifest':'public-artifacts-manifest-focused-mainwindow091.json'})
outer_rows=list(stage_rows)+[row(stage,'focused091/initial-preparation/'+stage.name)]
outer_rows += [row(p,'focused091/final/'+p.name) for p in sorted(FINAL.iterdir()) if p.is_file()]
mf=manifest(FINAL,'public-artifacts-manifest-focused-mainwindow091.json','FINAL_STABLE_FOCUSED_MAINWINDOW_ROOT_EXECUTION_PENDING',outer_rows)
print(json.dumps({'final_runner':desc(FINAL/'wine-focused-mainwindow-091-final.py'),'manifest':desc(mf),
    'handoff':desc(FINAL/'handoff-focused-mainwindow091.json'),'files':len(outer_rows),'bytes':sum(r['bytes'] for r in outer_rows),'initial_stage_files':len(stage_rows),'project_calls':0},ensure_ascii=False))
