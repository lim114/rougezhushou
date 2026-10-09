"""Stdlib source-only freezing; root alone executes actual MainWindow/Wine."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import sys

HERE=Path(__file__).resolve().parent
ROOT=Path('/workspace/rougezhushou')
FINAL=Path('/workspace/.continuation/ui-093-account-cache-final')
def sha(data):return hashlib.sha256(data).hexdigest()
def descriptor(path):
    data=path.read_bytes();return {'source_path':str(path),'bytes':len(data),'sha256':sha(data)}
def save(directory,name,obj):
    path=directory/name;assert not path.exists(),('no frozen overwrite',str(path))
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');return path
def row(path,archive):return {**descriptor(path),'archive_path':archive}
assert len(sys.argv)==2
source_path=Path(sys.argv[1]);source_bytes=source_path.read_bytes();source=json.loads(source_bytes)
assert sha(source_bytes)=='0fbfe28e2528ae9987f9f260bfed0068b1e16edf02274ea3349cd6d988aa2180'
assert source['passed'] is True and len(source['source_sha256_after'])==732
for rel,value in source['source_sha256_after'].items():assert sha((ROOT/rel).read_bytes())==value,rel
preflight=HERE/'source-only-preflight093.json';proof=json.loads(preflight.read_text());assert proof['passed'] and proof['AST_parse_only']
pending_path=HERE/'wine-account-window-093-pending.py';pending=pending_path.read_text()
plan_path=HERE/'account-window-plan093.json';plan=json.loads(plan_path.read_text())
assert descriptor(pending_path)==proof['pending_runner'] and descriptor(plan_path)==proof['plan']
assert sha((ROOT/'rouge/app.py').read_bytes())==plan['candidate_v2_app']['sha256']
assert sha((ROOT/'rouge/account_cache.py').read_bytes())==plan['candidate_v2_helper']['sha256']
assert not FINAL.exists(),'Additive new packet only'
ast.parse(pending)
initial=[row(p,'account093/preparation/'+p.name) for p in sorted(HERE.iterdir()) if p.is_file()]
initial_manifest=save(HERE,'public-artifacts-manifest-preparation093.json',{'format_version':1,'status':'SOURCE_ONLY_PREPARATION_STOPWRITE_RUNTIME_UNRUN','files':initial,'file_count':len(initial),'total_bytes':sum(r['bytes'] for r in initial)})
# No writes to preparation after this point.
FINAL.mkdir(mode=0o700)
shutil.copyfile(source_path,FINAL/'wine-account-window-093-source.json')
shutil.copyfile(plan_path,FINAL/'wine-account-window-093-plan.json')
guard_sha=sha(source_bytes);plan_sha=sha(plan_path.read_bytes())
assert pending.count('PENDING_PREPARATION = True')==1 and pending.count('PENDING_ACTUAL_ROOT_SOURCE_SHA256')==1
final=pending.replace('PENDING_PREPARATION = True','PENDING_PREPARATION = False',1).replace('PENDING_ACTUAL_ROOT_SOURCE_SHA256',guard_sha,1)
old_load="PLAN=json.loads(Path(__file__).with_name('wine-account-window-093-plan.json').read_text(encoding='utf-8'))"
bound_load="PLAN_PATH=Path(__file__).with_name('wine-account-window-093-plan.json')\nassert hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest()=='"+plan_sha+"'\nPLAN=json.loads(PLAN_PATH.read_text(encoding='utf-8'))"
assert final.count(old_load)==1;final=final.replace(old_load,bound_load,1)
ast.parse(final)
assert final.replace(bound_load,old_load,1).replace(guard_sha,'PENDING_ACTUAL_ROOT_SOURCE_SHA256',1).replace('PENDING_PREPARATION = False','PENDING_PREPARATION = True',1)==pending
runner=FINAL/'wine-account-window-093-final.py';runner.write_text(final,encoding='utf-8')
save(FINAL,'pending-to-source-bound-final-proof093.json',{'format_version':1,'passed':True,'pending_runner':descriptor(pending_path),'final_runner':descriptor(runner),'root_source':descriptor(source_path),
    'exact_reverse_recovers_pending':True,'original_plan_bytes_unchanged':True,'only_replacements':['earliest pending true to false','actual source guard SHA256','same adjacent plan SHA256 bound before load'],
    'actual_source_count':732,'actual_v2_app_and_helper_bytes_exact':True,'runner_executed':False,'project_calls':0})
save(FINAL,'scope-and-output-artifacts093.json',{'format_version':1,'status':'FINAL_STOPWRITE_ROOT_APPOINTED_SOURCE_REVIEW_PENDING_SOLE_WINE_ROOT',
    'plan_counts':plan['counts'],'expected_PNGs':plan['expected_PNGs'],'coverage_limits':plan['coverage_limits'],
    'runtime_files':[descriptor(runner),descriptor(FINAL/'wine-account-window-093-source.json'),descriptor(FINAL/'wine-account-window-093-plan.json')],
    'native_schema':'flat-typed-graph-v1; exact type/key/order/hex/alias graph, iterative inverse verified per actual snapshot; full JSON projection;500-layer unknown extras need no recursive deepcopy',
    'evidence':'Each state original raw bytes, file SHA and all synthetic existing paths before/after; account/RunState full snapshots; typed caller before/after for numerical API and observation/apply boundaries; helper/formatter/internal/startup/automatic/manual entries measured; numerical states three report strings; None/errors distinct.',
    'protected_disk':'Permanent preservation flag is never fixture-cleared. Real save entry and Path.mkdir/write_text/replace side effects observed; original bytes/no tmp/no writes checked. Clean/missing save controls retain source producer behavior.',
    'runtime_outputs':['wine-account-window-093.json','wine-account-window-093-records.json.gz',*plan['expected_PNGs']],
    'failure_PNG':'wine-account-window-failure-093.png','private_reads':0,'game_capture_requests':0,'chat_requests':0,'prep_project_calls':0,
    'next':'Fresh root-appointed source-only final review; root alone one actual Wine process, view three actual PNGs and preserve successful prefix/native receipt. Same issue third failure deferred with evidence.'})
handoff=save(FINAL,'handoff-account-window093.json',{'format_version':1,'status':'FINAL_STOPWRITE_ACTUAL732_SOURCE_BOUND_RUNTIME_PENDING',
    'runner':descriptor(runner),'source_guard':descriptor(FINAL/'wine-account-window-093-source.json'),'plan':descriptor(FINAL/'wine-account-window-093-plan.json'),
    'initial_preparation_manifest':descriptor(initial_manifest),'preflight':descriptor(preflight),'plan_counts':plan['counts'],
    'sole_formal':'root-appointed fresh final source-only reviewer pending; preparation/source reader is not approval',
    'runtime':'root alone; runner+guard+plan adjacent without changing dependency names','prep_project_calls':0,'manifest':'public-artifacts-manifest-account-window093.json'})
files=initial+[row(initial_manifest,'account093/preparation/'+initial_manifest.name)]+[row(p,'account093/final/'+p.name) for p in sorted(FINAL.iterdir()) if p.is_file()]
manifest=save(FINAL,'public-artifacts-manifest-account-window093.json',{'format_version':1,'status':'FINAL_STABLE_SOURCE_ONLY_ACTUAL_WINDOW_ROOT_PENDING','files':files,'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files),'manifest_self_excluded':True})
print(json.dumps({'runner':descriptor(runner),'guard':descriptor(FINAL/'wine-account-window-093-source.json'),'plan':descriptor(FINAL/'wine-account-window-093-plan.json'),
                  'manifest':descriptor(manifest),'handoff':descriptor(handoff),'files':len(files),'bytes':sum(r['bytes'] for r in files),'project_calls':0}))
