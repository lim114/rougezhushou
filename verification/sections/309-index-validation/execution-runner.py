from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,runpy,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/sections/309-index-validation';OUT.mkdir()
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
assert git('branch','--show-current').decode().strip()=='codex/p2-development'
assert git('rev-parse','HEAD').decode().strip()=='3bde3fa28159c9346d18e5d529e7e5620d3911fa'
assert git('ls-remote','origin','refs/heads/codex/p2-development').decode().split()[0]==git('rev-parse','HEAD').decode().strip()
# This candidate-schema narrative was not a runtime member or build authority.
# Keep the actual test/source receipts untouched; separately bind the reviewed
# documentation-only correction, without claiming the new prose ran in Qt.
doc='research/p3-boss-phase-309/SCHEMA.md';p=ROOT/doc;old=p.read_bytes();s=old.decode('utf8')
marker='源原HANDOFF b2c2318f...始终不改。';assert s.count(marker)==1
s=s.split(marker,1)[0]+'''源原HANDOFF b2c2318f...始终不改。首次代理来源构建和第一次窗口/必要检查原件分别保留在verification/sections/309-preparation/candidate-first-source-build、309-necessary-attempt1和309-native-attempt1；它们不是最终当前源码的运行回执。

根代理随后按静态核对取消未知原技能的全局名称映射，并在飞行招式下直接展开已有文献明确交叉引用的未熄之地效果，保留其完整条件；不合并冷却/技力或新增数值。当前build-receipt.json来自根代理实际重新构建，过程在verification/sections/309-preparation/flight-inline-refinement/source-rebuild/process.json；原DATA及全部原文不变。第二次source --check、83项必要检查与27项原生唯一检查均实际退出0，回执在309-source-attempt2、309-necessary-attempt2、309-native-attempt2。资料范围和未决机制以verification/sections/309.json为准，不据测试通过推定游戏实际阶段。
'''
manifest=read('research/p3-boss-phase-309/source-manifest.json');assert doc not in manifest['runtime_files'] and doc not in manifest['build_authority_files']
p.write_text(s,encoding='utf8');new=p.read_bytes()
correction={'section':309,'kind':'post_validation_documentation_only_correction_not_native_execution','file':doc,'before_sha256':sha256(old).hexdigest(),'after_sha256':sha256(new).hexdigest(),'runtime_or_build_authority_member':False,'only_change':'Replace historical candidate-build description with actual root rebuild/current receipt pointers and flight inline cross-reference. No source data, code, tests, numeric model or receipt altered.','root_reviewed':True,'necessary_or_Qt_repeat_needed':False,'new_prose_claimed_as_native_executed':False}
evidence=ROOT/'verification/sections/309-preparation/schema-current-doc';evidence.mkdir();(evidence/'before.md').write_bytes(old);(evidence/'correction.json').write_bytes(enc(correction))
receipt='verification/sections/309.json';r=read(receipt)
assert r['source_sha256'][doc]==r['validated_source_sha256'][doc]==correction['before_sha256']
r['source_sha256'][doc]=correction['after_sha256'];r['validated_source_sha256'].pop(doc)
r['post_validation_documentation_only_update']={'receipt':(evidence/'correction.json').relative_to(ROOT).as_posix(),'sha256':sha((evidence/'correction.json').relative_to(ROOT)),'exclusion_from_current_native_source_map':doc,'all_executable_and_runtime_source_bytes_unchanged':True}
(ROOT/receipt).write_bytes(enc(r));runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
argv=[sys.executable,'-B','-X','utf8','-m','unittest','tests.test_cloud_index_sync','-q']
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
    child=subprocess.Popen(argv,cwd=ROOT,stdout=stdout,stderr=stderr,stdin=subprocess.DEVNULL);code=child.wait()
log=(OUT/'stderr.txt').read_text('utf8');assert code==0 and 'Ran 25 tests'in log and 'OK'in log
record={'section':309,'passed':True,'argv':argv,'retained_popen_pid':child.pid,'actual_exit':code,'tests_run':25,'observed_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':sha('scripts/update_cloud_index.py'),'full_rerun':False}
(OUT/'process.json').write_bytes(enc(record));(OUT/'process.exit').write_text(str(code)+'\n',encoding='ascii');(OUT/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
r['index_validation']={'receipt':'verification/sections/309-index-validation/process.json','sha256':sha('verification/sections/309-index-validation/process.json'),'tests_run':25};(ROOT/receipt).write_bytes(enc(r))
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
for value in(read('verification/sections/309-necessary-attempt2/process.json'),read('verification/sections/309-native-attempt2/actual/window.json')):
    assert value['passed'] and value['source_sha256_before']==value['source_sha256_after']
    for name,h in value['source_sha256_after'].items():
        if name==doc:assert h==correction['before_sha256'] and sha(name)==correction['after_sha256']
        else:assert sha(name)==h,name
index=read('CLOUD_INDEX.json');cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==cp['latest_functional_section']==309 and cp['next_section']==310
assert index['current_section_label']=='第309节 + '+r['title'] and index['current_completed_change']==r['new_capability']
for name,h in index['public_pointers'].items():assert sha(name)==h,name
allowed=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/battle_view.py','rouge/boss_phase_view.py','rouge/boss_phase_reference.py','rouge/data/boss-phase-reference.json','scripts/build_boss_phase_reference_309.py','scripts/verify_boss_phase_window_309.py','scripts/verify_full_available.py','tests/test_boss_phase_reference_309.py','tests/test_boss_phase_view_309.py','tests/test_boss_phase_integration_309.py','research/p3-boss-phase-309']
allowed.extend(p.relative_to(ROOT).as_posix()for p in(ROOT/'verification/sections').glob('309*'))
subprocess.run(['git','add','-f','--',*allowed],cwd=ROOT,check=True)
staged=git('diff','--cached','--name-only').decode('utf8').splitlines();assert not any(n.startswith(('.cache/','.local/'))or n=='local-settings.json'for n in staged)
assert not git('diff','--name-only').strip()
check=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(OUT/'git-diff-check.txt').write_bytes(check.stdout+check.stderr)
assert check.returncode==0,(check.stdout+check.stderr).decode('utf8',errors='replace')[-6000:]
print(json.dumps({'section':309,'staged_public_files':len(staged),'index_checks_actual_exit':code,'diff_check_exit':check.returncode,'code_and_runtime_sources_current':True,'documentation_only_scope_separately_bound':True,'commit_ready_not_pushed':True},ensure_ascii=False))
