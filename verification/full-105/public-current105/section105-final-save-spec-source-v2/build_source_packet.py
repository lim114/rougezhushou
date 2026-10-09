"""Standard-library Source transport only. Does not execute the generated builder."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

base = Path('/workspace/.continuation')
packet = base/'section105-final-save-spec-source-v2'
original_path = base/'root-section105-spec-builder-v1.py'
raw = original_path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '77d12a76f636ce9934d5746c175cfaedd353fe8c95e5cffc65dab5e079fda764'
source = raw.decode('utf-8')
replacements = [
    ("root-section105-save-spec-v1.json", "root-section105-save-spec-v2.json"),
    ("full105-window-actual-v1/wine-ui-100.json", "full105-window-actual-v2/wine-ui-100.json"),
    ("supervisor=load('full105-window-supervisor-v1.json')", "supervisor=load('full105-window-supervisor-v2.json')"),
    ("'actual_gui_attempts':1", "'actual_gui_attempts':2,'gui_attempts':attempts"),
    ("full105-actual-closure-v1.json", "full105-actual-closure-v2.json"),
    ("full105-progress-report-v1.md", "full105-progress-report-v2.md"),
    ("full105-window-primary-v1.exit-code','root-full105-saved-audit-v1.exit-code", "full105-window-primary-v2.exit-code','root-full105-saved-audit-v1.exit-code"),
    ("本组五节已完成实际检验与断点归档。", "本组五节已完成实际检验；本报告与闭合断点随105归档提交。"),
    ("实际窗口全量一次完成4283检查、52保存状态，四图实际查看，primary/child/supervisor均0。", "实际窗口第2次运行完成4283检查、52保存状态，四图实际查看，最终primary/child/supervisor均0。第1次600秒预算超时，原primary124、child-9、实际600.1465337909904秒、三张已查看PNG且无终稿均完整保留；第一次不计PASS。第2次预算1200秒，简短progress只记录已追加checks下界，不能替代完整终稿或声明全向量测量完成。"),
    ("实际窗口4283检查/52状态/四图/保存读回及无live-owned执行检查通过；", "实际窗口第二次4283检查/52状态/四图/保存读回及无live-owned执行检查通过，保留第一次600秒超时primary124/child-9；"),
]
for old, new in replacements:
    assert source.count(old) == 1, (old, source.count(old))
    source = source.replace(old, new, 1)

anchor = "assert wine['environment_capability_skips']==3\n"
assert source.count(anchor) == 1
checks = r'''
# This fresh builder is Root-executed only after actual retry2 + Saved + visual.
# No output is written until every terminal gate below succeeds.
assert not (BASE/'full105-actual-closure-v2.json').exists()
assert not (BASE/'full105-progress-report-v2.md').exists()
def fingerprint(path):
    path=Path(path);raw=path.read_bytes()
    return {'source':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def actual_exit(name):
    raw=(BASE/name).read_bytes()
    assert raw==b'0\n', (name,raw)
    return fingerprint(BASE/name)
for name in ('root-section105-apply-v1.exit-code','root-full105-guard-builder-v1.exit-code',
             'section105-portable-node-font-actual-wine-v1.exit-code',
             'full105-wine-capability-probe-v1.exit-code','full105-linux-v1.exit-code',
             'full105-wine-v1.exit-code','full105-window-primary-v2.exit-code',
             'root-full105-saved-audit-v1.exit-code'):
    actual_exit(name)

suite_guard_path=BASE/'full105-source-suite-guard-v1.json'
suite_guard_raw=suite_guard_path.read_bytes();suite_guard=json.loads(suite_guard_raw)
assert suite_guard['source_sha256']==guard['source_sha256']
assert suite_guard['source_additional_sha256']==guard['source_additional_sha256']
assert set(guard['source_additional_sha256'])=={'CORE_0.70_VERIFICATION.json'}
for field in ('source_sha256','source_additional_sha256'):
    for relative,expected in guard[field].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==expected, relative
    assert gui[field]==gui[field+'_after']==guard[field]
    assert wine[field]==wine[field+'_after']==guard[field]
assert gui['source_drift']==gui['source_additional_drift']==[]
assert wine['source_drift']==wine['source_additional_drift']==wine['adapter_source_drift']==[]
assert linux['source_drift']==[]
# Linux receipt itself owns its 355-source subset, not the complete748 map.
assert len(linux['source_sha256'])==355
assert all(guard['source_sha256'].get(k)==v for k,v in linux['source_sha256'].items())
linux_all=load('full105-linux-root-source-audit-v1.json')
assert linux_all['passed'] is linux_all['workflow_complete'] is True
assert linux_all['source_count']==748 and linux_all['source_drift']==[]
assert linux_all['source_guard_sha256']==hashlib.sha256(suite_guard_raw).hexdigest()
assert linux_all['native_windows_verified'] is False
assert linux['complete_repository_validation'] is wine['complete_repository_validation'] is False
assert linux['failures']==linux['errors']==wine['failures']==wine['errors']==0

runner_path=BASE/'full105-progress-bounded-window-source-v2/window.py'
supervisor_source=BASE/'full105-progress-bounded-window-source-v2/supervisor105.py'
runner_pin='0004f90b316ec6bc576ac893ce67f52e09e9db4508edd8708f431676b36695a1'
supervisor_pin='477cf622f56e77a87850790f99c37dbdef3d6466b74697e9783417e83cf3efc3'
assert fingerprint(runner_path)['sha256']==runner_pin==gui['runner_sha256']
assert fingerprint(supervisor_source)['sha256']==supervisor_pin==supervisor['supervisor_sha256']
assert gui['source100_guard_sha256']==hashlib.sha256(suite_guard_raw).hexdigest()
assert gui['full105_attempt']==supervisor['full105_attempt']==2
assert gui['deadline_seconds']==supervisor['deadline_seconds']==1200
assert supervisor['after_section']==105 and supervisor['status']=='completed'
assert supervisor['timed_out'] is False
assert supervisor['native_windows_verified'] is supervisor['global_wineserver_terminated'] is False
expected_argv=['/workspace/.compat/run-wine-python.sh',
               'Z:\\workspace\\.continuation\\full105-progress-bounded-window-source-v2\\window.py',
               '--root','Z:\\workspace\\rougezhushou',
               '--guard','Z:\\workspace\\.continuation\\full105-source-suite-guard-v1.json',
               '--out','Z:\\workspace\\.continuation\\full105-window-actual-v2']
assert supervisor['argv']==expected_argv and supervisor['cwd']==str(ROOT)
assert gui['total_actual_checks']==len(gui['checks'])==4283
assert gui['new_state_archive090']['records']==52
assert gui['global_profile_or_trace_used'] is gui['old095_complete_function_vector_measured'] is False
assert gui['specialist101_104_validation_in_this_runner'] is False
progress_path=BASE/'full105-window-actual-v2/full105-progress.json'
progress=json.loads(progress_path.read_bytes())
assert progress['kind']=='FULL105_ATTEMPT2_APPENDED_CHECK_PROGRESS'
assert progress['after_section']==105 and progress['attempt']==2
assert progress['passed'] is progress['workflow_complete'] is progress['complete_function_vector_measured'] is False
assert progress['checkpoint_every_appended_checks']==32
assert type(progress['appended_checks']) is int and 0<=progress['appended_checks']<=len(gui['checks'])
assert progress['appended_checks']%32==0
assert saved['actual_gui_checks']==4283 and saved['main_source_files']==748
assert saved['primary_exit']==0 and saved['source_drift']==[]
assert saved['no_live_owned_execution_verified'] is True
assert saved['saved_archive_sha256']==gui['new_state_archive090']['sha256']
assert saved['png_hashes_checked']==gui['screenshots100']
assert saved['native_aliases_verified_by_this_audit'] is saved['full_result_equality_to_old_gold_verified'] is False
assert saved['old095_complete_function_vector_measured'] is saved['native_windows_game_chat_verified'] is False

first_path=BASE/'full105-window-supervisor-v1.json'
first=fingerprint(first_path)
assert first['sha256']=='b49a2771bea0121cc2a84c6c4e0c6a113d7fb020ffc5b2aed9db81de8103cbb6'
first_supervisor=json.loads(first_path.read_bytes())
assert (BASE/'full105-window-primary-v1.exit-code').read_bytes()==b'124\n'
assert first_supervisor['child_primary_exit']==-9 and first_supervisor['supervisor_exit']==124
assert first_supervisor['timed_out'] is True and first_supervisor['deadline_seconds']==600
assert first_supervisor['elapsed_seconds']==600.1465337909904
assert not (BASE/'full105-window-actual-v1/wine-ui-100.json').exists()
partial_visual=load('full105-visual-partial-ledger-v1.json')
assert partial_visual['actually_viewed_images']==3 and partial_visual['passed_claimed'] is False
assert len(partial_visual['pngs'])==3 and all(row['actually_viewed'] is True for row in partial_visual['pngs'])
attempts=[{'attempt':1,'status':'TIMED_OUT_INCOMPLETE_NOT_PASS','primary_exit':124,
           'child_primary_exit':-9,'supervisor_exit':124,'timed_out':True,'deadline_seconds':600,
           'elapsed_seconds':first_supervisor['elapsed_seconds'],'partial_pngs_actually_viewed':3,
           'final_gui_receipt_present':False,'supervisor':first,
           'primary':fingerprint(BASE/'full105-window-primary-v1.exit-code'),
           'partial_visual_ledger':fingerprint(BASE/'full105-visual-partial-ledger-v1.json')},
          {'attempt':2,'status':'ACTUAL_COMPLETE_BOUNDED_GUI_PASS','primary_exit':0,
           'child_primary_exit':supervisor['child_primary_exit'],'supervisor_exit':supervisor['supervisor_exit'],
           'timed_out':supervisor['timed_out'],'deadline_seconds':supervisor['deadline_seconds'],
           'elapsed_seconds':supervisor['elapsed_seconds'],'actual_checks':gui['total_actual_checks'],
           'saved_states':gui['new_state_archive090']['records'],
           'argv':supervisor['argv'],'runner':fingerprint(runner_path),
           'supervisor_source':fingerprint(supervisor_source),
           'supervisor':fingerprint(BASE/'full105-window-supervisor-v2.json'),
           'primary':fingerprint(BASE/'full105-window-primary-v2.exit-code'),
           'final_gui_receipt':fingerprint(BASE/'full105-window-actual-v2/wine-ui-100.json'),
           'progress_partial_only':fingerprint(progress_path),
           'saved_readback':fingerprint(BASE/'root-full105-saved-audit-v1.json'),
           'actual_visual_ledger':fingerprint(BASE/'full105-visual-audit-v1.json'),
           'no_live_owned_execution_verified':True,
           'owned_session_absence_verified':supervisor['owned_session_closure']['owned_session_absence_verified']}]
'''
source=source.replace(anchor,anchor+checks,1)
anchor="entries.extend([{'source':str(BASE/'section104-publication-v1.json'),'destination':'prior-publication.json'},"
assert source.count(anchor)==1
insert="""entries.append({'source':str(Path(__file__).resolve()),'destination':'actual-root-evidence/root-section105-spec-builder-v2.py'})
"""
source=source.replace(anchor,insert+anchor,1)
path=packet/'root-section105-spec-builder-v2.py'
assert not path.exists()
path.write_text(source,encoding='utf-8')
compile(source,str(path),'exec')
parsed=ast.parse(source)
# Expected Win32 launch strings are read statically; never execute builder.
assignment=next(n for n in ast.walk(parsed) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='expected_argv' for t in n.targets))
expected=ast.literal_eval(assignment.value)
assert expected[1]=='Z:\\workspace\\.continuation\\full105-progress-bounded-window-source-v2\\window.py',repr(expected[1])
(packet/'builder-source.diff').write_text(''.join(difflib.unified_diff(raw.decode('utf-8').splitlines(True),source.splitlines(True),fromfile=str(original_path),tofile=str(path))),encoding='utf-8')
print(json.dumps({'generated_source':str(path),'bytes':len(path.read_bytes()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'compile_only':True,'builder_executed':False},ensure_ascii=False))
