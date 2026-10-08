"""External source-only resume revision. Does not import or execute product or runner."""
from pathlib import Path
import ast,gzip,hashlib,json,pprint,shutil
PARENT=Path('/workspace/.continuation/ui-091-focused-final')
HERE=Path('/workspace/.continuation/ui-091-focused-resume8-v2')
OUT=Path('/workspace/.compat')
def sha(data):return hashlib.sha256(data).hexdigest()
def descriptor(p):
    b=p.read_bytes();return {'source_path':str(p),'bytes':len(b),'sha256':sha(b)}
def save(name,obj):
    p=HERE/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');return p
assert not HERE.exists(),'Use new revision only; preserve original FINAL and run1 evidence'
parent_path=PARENT/'wine-focused-mainwindow-091-final.py'
parent=parent_path.read_text()
assert sha(parent.encode())=='648389a4dafefc8775d39b07f79eb895689a4a417dc2155dc8118679b30552c5'
archive_path=OUT/'wine-focused-mainwindow-091-records.json.gz'
compressed=archive_path.read_bytes()
assert sha(compressed)=='b818640c119c187d0baab2380422ebfef321151e88f86a6bb34cf0768c58793c'
saved=json.loads(gzip.decompress(compressed))
assert len(saved['checks'])==16 and len(saved['states'])==17
assert all(r['passed'] for r in saved['states'][:16]) and saved['states'][16]['passed'] is False
assert len(saved['API_events'])==60 and all(r['outcome']=='returned_dict' for r in saved['API_events'])
last=saved['states'][15]
assert last['id']=='amiya-natural-return-retains-false'
warm_expected={'scenario_native_before':last['scenario_native_before'],'result_native_before':last['result_native_before']}
plan=json.loads((PARENT/'focused-window-state-plan091.json').read_text())
assert len(plan['rows'][16:])==8
assert sum(r.get('numerical_result_expected',True) for r in plan['rows'][16:])==5
assert sum(bool(r.get('explicit_click')) for r in plan['rows'][16:])==4
HERE.mkdir(mode=0o700)
shutil.copyfile(__file__,HERE/'prepare_focused_resume8_v2_091.py')
save('run1-evidence-source-descriptors091.json',{
    'format_version':1,'status':'ORIGINAL_FAILED_RUN1_IMMUTABLE_REUSED_NOT_REEXECUTED',
    'files':[descriptor(p) for p in [archive_path,OUT/'wine-focused-mainwindow-091.json',OUT/'wine-focused-mainwindow-failure-091.png',OUT/'wine-focused-continuous-091.png']],
    'passed_states':16,'failed_record_index':16,'numerical_API_entries':60,'all_API_returned_dict':True,
    'fixture_issue_attempts':1,'failure':'Direct synthetic operator_observations omitted required id; real producer apply_operator_observation retains id. Product unchanged.',
    'source_drift':[],'reader_API_helper_formatter_Qt_Wine':0})
save('warm-reference-original-last-passed-state091.json',last)
save('warm-reference-native-exact-contract091.json',{
    'format_version':1,'baseline_id':last['id'],'baseline_archive':descriptor(archive_path),
    'native_expected':warm_expected,'scope':'Exact native scenario and result tree equality, types/float.hex/dict insertion order included. New id fixture is not a new public scenario field.',
    'explicit_helper_or_formatter_warm_requests':0,'warm_actual_auto_entries':'measured separately, not claimed zero'})
shutil.copyfile(PARENT/'focused-window-state-plan091.json',HERE/'focused-window-state-plan091.json')
shutil.copyfile(PARENT/'actual-joined730-source-binding091.json',HERE/'actual-joined730-source-binding091.json')
changes=[]
text=parent
def replace(old,new,label):
    global text
    assert text.count(old)==1,(label,text.count(old))
    text=text.replace(old,new,1);changes.append({'label':label,'old':old,'new':new})
replace("RECEIPT=OUT/'wine-focused-mainwindow-091.json'","RECEIPT=OUT/'wine-focused-mainwindow-091-resume8-v2.json'",'new receipt sink')
replace("CHECKPOINT=OUT/'wine-focused-mainwindow-091-records.json.gz'","CHECKPOINT=OUT/'wine-focused-mainwindow-091-resume8-v2-records.json.gz'",'new checkpoint sink')
replace("window=None;app=None;started=time.perf_counter()","window=None;app=None;started=time.perf_counter();warm_state=None\nWARM_EXPECTED="+pprint.pformat(warm_expected,sort_dicts=False,width=120), 'saved native warm reference and warm slot')
replace("'planned_states':24,'old_full90_or4217_replayed':False", "'planned_states':8,'original_total_states':24,'original_passed_states_reused':16,'resume_remaining_indices':[16,24],\n    'original_run1_archive_sha256':'"+sha(compressed)+"','same_fixture_issue_runtime_attempt':2,'old_full90_or4217_replayed':False", 'bounded resume receipt scope')
replace("'passed':receipt['passed'],'current_step':current_step}","'passed':receipt['passed'],'current_step':current_step,'warm_recovery':warm_state}", 'save warm recovery in lossless checkpoint')
replace("window.operator_observations[owner]={'fields':copy.deepcopy(row['training']),", "window.operator_observations[owner]={'id':owner,'fields':copy.deepcopy(row['training']),", 'only fixture correction required id')
replace("        results={}\n        for row in PLAN['rows']:","""        current_step='warm-recovery-original-last-passed-row15'
        warm_before=dict(entry_counts)
        checkpoint()
        checkbox.setChecked(False);app.processEvents()
        train(PLAN['rows'][15]);app.processEvents()
        assert checkbox.isChecked() is False and window.damage_result
        warm_raw=window.damage_result['scenario'];warm_result=window.damage_result['result']
        warm_state={'reference_id':PLAN['rows'][15]['id'],'passed':False,
            'scenario':copy.deepcopy(warm_raw),'result':copy.deepcopy(warm_result),
            'scenario_native':native(warm_raw),'result_native':native(warm_result),
            'actual_entries':delta(warm_before,entry_counts),'explicit_helper_or_formatter_requests':0}
        checkpoint()
        assert warm_state['scenario_native']==WARM_EXPECTED['scenario_native_before'],'warm public caller native differs from original passed row15'
        assert warm_state['result_native']==WARM_EXPECTED['result_native_before'],'warm full result native differs from original passed row15'
        warm_state['passed']=True
        receipt['warm_recovery_native_exact_passed']=True
        receipt['warm_recovery_actual_entries']=delta(warm_before,entry_counts)
        receipt['post_warm_actual_entries']=dict(entry_counts)
        phase_before=dict(entry_counts)
        checkpoint()
        results={}
        for row in PLAN['rows'][16:]:""",'exact warm recovery then only eight remaining states')
replace("path=OUT/row['screenshot'];assert window.grab().save(str(path))", "path=OUT/({'wine-focused-deepcolor-091.png':'wine-focused-deepcolor-091-resume8-v2.png'}.get(row['screenshot'],row['screenshot']));assert window.grab().save(str(path))", 'new Deep screenshot sink without changing plan literal')
replace("assert len(states)==len(checks)==24", "assert len(states)==len(checks)==8", 'remaining cardinality')
replace("assert explicit_buttons==5 and explicit_text_requests==63", "assert explicit_buttons==4 and explicit_text_requests==15", 'remaining explicit cardinality')
replace("path=OUT/'wine-focused-mainwindow-failure-091.png'", "path=OUT/'wine-focused-mainwindow-failure-091-resume8-v2.png'", 'new failure screenshot sink')
ast.parse(text)
runner=HERE/'wine-focused-mainwindow-091-resume8-v2.py';runner.write_text(text,encoding='utf-8')
reverse=text
for change in reversed(changes):
    assert reverse.count(change['new'])==1,change['label']
    reverse=reverse.replace(change['new'],change['old'],1)
assert reverse==parent
pt=ast.parse(parent);nt=ast.parse(text)
def assignment(tree,name):
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
assert assignment(pt,'SOURCE_HASHES')==assignment(nt,'SOURCE_HASHES')
assert assignment(pt,'PLAN')==assignment(nt,'PLAN')
assert assignment(nt,'WARM_EXPECTED')==warm_expected
save('exact-byte-delta-and-native-recovery-proof091.json',{
    'format_version':1,'status':'FINAL_STATIC_REVISION_PRODUCT_RUNTIME_PENDING','parent_runner':descriptor(parent_path),
    'resume_runner':descriptor(runner),'changes':changes,'exact_reverse_restores_whole_parent':True,
    'original_PLAN_AST_literal_unchanged':True,'original_730_source_AST_literal_unchanged':True,
    'warm_expected_saved_original_native_bound':True,'only_fixture_schema_change':'id:owner',
    'public_product_changes':0,'project_calls':0,'AST_parse_only':True})
save('resume8-scope-and-output-artifacts091.json',{
    'format_version':1,'status':'FINAL_STOPWRITE_ONLY_REMAINING_ROOT_EXECUTION_PENDING',
    'original_total_states':24,'original_passed_states_reused':16,'remaining_states':8,
    'remaining_numeric':5,'remaining_None_early':3,'remaining_explicit_buttons':4,'remaining_explicit_three_texts':15,
    'startup_common_warm_phase_ledger':'Startup and initial/common snapshots unchanged; warm delta recorded independently; focused phase_before reset only after exact native warm equality. All automatic/helper/formatter entries observed.',
    'warm_extra_explicit_helper_or_formatter_requests':0,
    'fixture_policy':'Source producer preserves id; synthetic fixture adds id, does not call observation apply/capture/native OCR. No product changes.',
    'actual_runtime_same_issue_attempt':2,'third_failed_same_issue_policy':'Defer unresolved harness issue with saved breakpoint; never replay the already passed prefix.',
    'actual_source_guard':730,'original_plan_inputs_and_qualification_unchanged':True,
    'output_artifacts':['wine-focused-mainwindow-091-resume8-v2.json','wine-focused-mainwindow-091-resume8-v2-records.json.gz','wine-focused-deepcolor-091-resume8-v2.png'],
    'failure_artifact':'wine-focused-mainwindow-failure-091-resume8-v2.png',
    'original_continuous_PNG_reused':descriptor(OUT/'wine-focused-continuous-091.png'),
    'original_failure_checkpoint_and_receipt':'Preserved and referenced with exact descriptors; neither overwritten nor resumed as success.',
    'actual_API_Qt_Wine_executed_by_author':False,'prepared_project_calls':0})
(HERE/'CHECKPOINT.md').write_text('FINAL STOPWRITE: minimum resume8 v2. Original focused final/run1 evidence immutable; 16 passed prefix reused, failed row17 retained. Add id to synthetic account fixture only. Root must recover isolated common defaults, checkbox False and original last-passed Amiya row15, then exact native full caller/result equality before remaining PLAN[16:] eight states (five numeric + three None early), four explicit buttons and 15 text requests. Warm and startup/common automatic entries measured separately, no additional explicit helper/formatter warm requests. Root sole runtime attempt2 for this fixture issue; no author API/Qt/Wine.\n',encoding='utf-8')
save('handoff-focused-resume8-v2-091.json',{
    'format_version':1,'status':'FINAL_STOPWRITE_ROOT_SOLE_RESUME_PENDING','runner':descriptor(runner),
    'parent_runner':descriptor(parent_path),'parent_packet_manifest':descriptor(PARENT/'public-artifacts-manifest-focused-mainwindow091.json'),
    'original_run1_archive':descriptor(archive_path),'remaining':8,'numeric':5,'early_None':3,'buttons':4,'text_requests':15,
    'source_guard':730,'warm_native_exact_required':True,'old_passed_states_reexecuted':False,
    'API_helper_formatter_tests_Qt_Wine_author_calls':0,
    'manifest':'public-artifacts-manifest-focused-resume8-v2-091.json'})
files=[{**descriptor(p),'archive_path':'focused091/resume8-v2/'+p.name} for p in sorted(HERE.iterdir()) if p.is_file()]
mf=save('public-artifacts-manifest-focused-resume8-v2-091.json',{'format_version':1,'status':'FINAL_STABLE_RESUME8_V2_RUNTIME_PENDING','files':files,'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files)})
print(json.dumps({'runner':descriptor(runner),'manifest':descriptor(mf),'handoff':descriptor(HERE/'handoff-focused-resume8-v2-091.json'),'files':len(files),'bytes':sum(r['bytes'] for r in files),'delta_spans':len(changes),'project_calls':0}))
