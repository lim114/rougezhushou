"""Source-only final freezing after root applies92; never import/execute project or Qt."""
from pathlib import Path
import ast,hashlib,json,shutil,sys
HERE=Path(__file__).resolve().parent
ROOT=Path('/workspace/rougezhushou')
FINAL=Path('/workspace/.continuation/ui-092-focused-final')
def sha(b):return hashlib.sha256(b).hexdigest()
def descriptor(p):
    b=p.read_bytes();return {'source_path':str(p),'bytes':len(b),'sha256':sha(b)}
def save(directory,name,obj):
    p=directory/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');return p
def manifest(directory,name,status,files):
    return save(directory,name,{'format_version':1,'status':status,'files':files,'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files)})
def row(p,name):return {**descriptor(p),'archive_path':name}
assert len(sys.argv)==2,'Explicit actual root source receipt required'
source_path=Path(sys.argv[1]);source=json.loads(source_path.read_text())
assert source['passed'] is True and len(source['source_sha256_after'])==730
integration=json.loads(Path('/workspace/.continuation/root-integration-plan092.json').read_text())
expected=dict(integration['before_maintained_sha256'])
for change in integration['changes']:expected[change['target_path']]=change['new_sha256']
assert source['source_sha256_after']==expected,'Actual root730 must equal exactly the qualified two candidate substitutions'
for rel,digest in expected.items():assert sha((ROOT/rel).read_bytes())==digest,('actual maintained mismatch',rel)
for change in integration['changes']:
    assert (ROOT/change['target_path']).read_bytes()==Path(change['source_path']).read_bytes()
assert not FINAL.exists(),'New final only; no frozen packet overwritten'
pending_path=HERE/'wine-focused-window-092-pending.py';pending=pending_path.read_text()
plan_path=HERE/'focused-window-plan092.json';plan=json.loads(plan_path.read_text())
ast.parse(pending)
assert len(plan['rows'])==19 and sum('error' not in r for r in plan['rows'])==15
assert sum(r.get('button',False) for r in plan['rows'])==2
save(HERE,'actual-source-and-static-freeze092.json',{
    'format_version':1,'passed':True,'root_source':descriptor(source_path),'root_integration_plan':descriptor(Path('/workspace/.continuation/root-integration-plan092.json')),
    'two_candidate_targets':integration['changes'],'actual_working_source_count':730,'unchanged_source_count':728,
    'scope':'Actual post-apply working bytes, not old91 Git blobs. No project imports/API/helper/formatter/tests/Qt/Wine.',
    'pending_runner':descriptor(pending_path),'plan':descriptor(plan_path),'AST_parse_only':True,'project_calls':0})
initial_files=[row(p,'focused092/initial-preparation/'+p.name) for p in sorted(HERE.iterdir()) if p.is_file()]
initial_manifest=manifest(HERE,'public-artifacts-manifest-initial-preparation092.json','FINAL_STABLE_SOURCE_ONLY_PENDING_PREPARATION',initial_files)
# Preparation immutable after this line; final is an additive new packet.
FINAL.mkdir(mode=0o700)
shutil.copyfile(source_path,FINAL/'wine-focused-window-092-source.json')
shutil.copyfile(plan_path,FINAL/'wine-focused-window-092-plan.json')
guard_sha=sha((FINAL/'wine-focused-window-092-source.json').read_bytes())
plan_sha=sha((FINAL/'wine-focused-window-092-plan.json').read_bytes())
assert pending.count('PENDING_PREPARATION = True')==1 and pending.count('PENDING_ACTUAL_ROOT_SOURCE_SHA256')==1
final=pending.replace('PENDING_PREPARATION = True','PENDING_PREPARATION = False',1).replace('PENDING_ACTUAL_ROOT_SOURCE_SHA256',guard_sha,1)
plan_load="PLAN=json.loads(Path(__file__).with_name('wine-focused-window-092-plan.json').read_text(encoding='utf-8'))"
assert final.count(plan_load)==1
bound_load="PLAN_PATH=Path(__file__).with_name('wine-focused-window-092-plan.json')\nassert hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest()=='"+plan_sha+"'\nPLAN=json.loads(PLAN_PATH.read_text(encoding='utf-8'))"
final=final.replace(plan_load,bound_load,1)
ast.parse(final)
runner=FINAL/'wine-focused-window-092-final.py';runner.write_text(final,encoding='utf-8')
reverse=final.replace(bound_load,plan_load,1).replace(guard_sha,'PENDING_ACTUAL_ROOT_SOURCE_SHA256',1).replace('PENDING_PREPARATION = False','PENDING_PREPARATION = True',1)
assert reverse==pending
save(FINAL,'pending-to-source-bound-final-proof092.json',{
    'format_version':1,'passed':True,'pending_runner':descriptor(pending_path),'final_runner':descriptor(runner),
    'exact_reverse_recovers_pending':True,'changes':['earliest pending True to False','actual source guard SHA256 constant','exact unchanged external plan SHA256 bound before load'],
    'actual_730_working_source_bound':True,'two_author_candidate_target_bytes_exact':True,'original19state_inputs_unchanged':True,
    'runner_executed':False,'project_calls':0})
save(FINAL,'focused-window-scope-and-output-artifacts092.json',{
    'format_version':1,'status':'FINAL_STOPWRITE_ROOT_SOLE_FOCUSED_WINDOW_PENDING','states':19,'numeric_states':15,'different_existing_error_states':4,
    'explicit_buttons':2,'explicit_three_text_requests':45,'success_PNGs':2,
    'calls':'Measure startup/common/focused main-thread functions, Qt signal emissions, explicit requests and all automatic entries. API entries are separated into returned_dict/raised_exception/uncollected, not equated with success count.',
    'source_guard':'External JSON beside runner, exact SHA256 before load and730 before/after hashes. Root must transport all three runtime files without renaming dependencies.',
    'runtime_files':[descriptor(runner),descriptor(FINAL/'wine-focused-window-092-source.json'),descriptor(FINAL/'wine-focused-window-092-plan.json')],
    'native_archive':'Full typed caller before/after + native tagged and JSON projection for every successful automatic/explicit API entry; original exceptions; each selected state raw/native/report strings, checks and checkpoints before assertions.',
    'report_scope':'Effective window from each existing estimate, damage/healing metric dictionaries checked per section. At0 observe new length row and omission of existing positive-only average row; no universal total0 or new undefined literal.',
    'models':'Source-qualified finite Silverash legacy alias S3 (48), GummyS2 (30/disarm10), current kaltsit alias S3 friendly fallback. No classic Mon3tr or all-model clipping inference. 30Hz is a reference model, not native-clock certification.',
    'output_artifacts':['wine-focused-window-092.json','wine-focused-window-092-records.json.gz','wine-focused-window-zero-092.png','wine-focused-window-friendly-092.png'],
    'failure_artifact':'wine-focused-window-failure-092.png','private_temp_state_isolated':True,'capture_chat_requests':0,
    'old91_failed_fixture_or_two_calculate_exceptions_reused':False,'old91_or_full90_matrix_replayed':False,
    'source49_and_author_public_API_comparison_reexecuted':False,'prep_project_Qt_Wine_calls':0,
    'next':'Sole independent source-only formal; root actual Wine once, then view actual two PNGs and archive receipt/native checkpoint. Preserve successful prefix if failure, same issue third failure deferred.'})
(FINAL/'CHECKPOINT.md').write_text('FINAL STOPWRITE:19 focused92 states (15 numerical plus4 different existing error boundaries),2 explicit buttons/45 explicit report requests/two success PNG. Root alone actualWine pending formal; no prep API/helper/formatter/tests/Qt/Wine. Runtime requires runner + exact source guard JSON + exact plan JSON adjacent. Actual730 joined working source uses two candidate substitutions, not old HEAD blobs. Real fixtures all contain id, no old91/full90 replay or author API comparison rerun.\n',encoding='utf-8')
handoff=save(FINAL,'handoff-focused-window092.json',{
    'format_version':1,'status':'FINAL_STOPWRITE_STATIC_FROZEN_ACTUAL_ROOT_WINDOW_PENDING','runner':descriptor(runner),
    'source_guard':descriptor(FINAL/'wine-focused-window-092-source.json'),'plan':descriptor(FINAL/'wine-focused-window-092-plan.json'),
    'initial_preparation_manifest':descriptor(initial_manifest),'initial_preparation_file_count':len(initial_files),
    'counts':plan['counts'],'root_source_receipt':descriptor(source_path),'author_public_inputs_source':descriptor(Path('/workspace/.continuation/p2-window-target-timing-flow-092-author/public-inputs092.json')),
    'sole_formal':'source080 source-only,0project calls; root executes one Wine acceptance after PASS','prep_project_calls':0,
    'manifest':'public-artifacts-manifest-focused-window092.json'})
files=initial_files+[row(initial_manifest,'focused092/initial-preparation/'+initial_manifest.name)]
files += [row(p,'focused092/final/'+p.name) for p in sorted(FINAL.iterdir()) if p.is_file()]
mf=manifest(FINAL,'public-artifacts-manifest-focused-window092.json','FINAL_STABLE_FOCUSED_WINDOW_ROOT_EXECUTION_PENDING',files)
print(json.dumps({'runner':descriptor(runner),'source_guard':descriptor(FINAL/'wine-focused-window-092-source.json'),'plan':descriptor(FINAL/'wine-focused-window-092-plan.json'),
    'manifest':descriptor(mf),'handoff':descriptor(handoff),'files':len(files),'bytes':sum(r['bytes'] for r in files),'project_calls':0}))
