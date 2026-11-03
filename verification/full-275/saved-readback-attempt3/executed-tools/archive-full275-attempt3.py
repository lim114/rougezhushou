"""Archive only the three completed isolated public fixture outputs and tools."""
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]
VERIFY=ROOT/'verification/full-275'
FREEZE=VERIFY/'source-freeze-reset-repair.json'
PATHS=ROOT/'.cache/full275-reset-execution-paths.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
def write(path,value):
    with path.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def files(directory):
    rows={}
    for path in sorted(directory.rglob('*')):
        assert not path.is_symlink(),path
        if path.is_file() and '__pycache__' not in path.parts:
            rows[path.relative_to(directory).as_posix()]={'sha256':sha(path),'bytes':path.stat().st_size}
    return rows
def copy_one(source,target,expected=None):
    assert source.is_file() and not source.is_symlink()
    raw=source.read_bytes()
    if expected is not None:assert hashlib.sha256(raw).hexdigest()==expected
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(raw)
    assert sha(source)==sha(target)
def copy_tree(source,target):
    pins=files(source)
    for relative,pin in pins.items():copy_one(source/relative,target/relative,pin['sha256'])
    assert files(source)==pins
    return pins

destinations={
    'legacy':VERIFY/'legacy-window-attempt3',
    'current':VERIFY/'current-window-attempt3'}
assert all(not path.exists() for path in destinations.values()),'Archive destination exists; never overwrite'
paths=read(PATHS);freeze=read(FREEZE)
source_before={name:sha(ROOT/name) for name in freeze['source_sha256']}
assert source_before==freeze['source_sha256']
states={};closures={};bundles={};readings={}
for mode in ('legacy','current30','current29'):
    status_path=Path(paths[mode+'_status']);actual_path=Path(paths[mode+'_actual'])
    assert actual_path.resolve().is_relative_to(Path(paths['root']).resolve())
    state=read(status_path);closure=read(actual_path/'native275-launcher-closure.json')
    assert state['status']=='completed' and state['owned_job_no_live_execution_verified'] is True
    assert state['owned_handle_retained'] is True and state['owned_job_assigned'] is True
    assert state['timed_out'] is False
    expected=1 if mode=='current30' else 0
    assert state['child_primary_exit']==state['supervisor_exit']==closure['original_fixture_exit']==expected
    assert closure['source_drift']==closure['executed_tool_drift']==[]
    assert closure['root_freeze_sha256']==sha(FREEZE)
    assert closure['historical_original_windows_or_game_chat_verified'] is False
    assert closure['private_state_isolated'] is True
    bundle=Path(state['argv'][3]).parent
    assert bundle.resolve().is_relative_to((ROOT/'.cache').resolve())
    assert bundle==ROOT/'.cache'/('full275-legacy-attempt3-bundle' if mode=='legacy' else 'full275-current-attempt3-window')
    for name,expected_sha in closure['execution_tools_sha256'].items():assert sha(bundle/name)==expected_sha,name
    states[mode]=(status_path,state);closures[mode]=closure;bundles[mode]=bundle
    reading=read(actual_path/('wine-ui-100.json' if mode=='legacy' else 'window.json'))
    if mode=='legacy':
        assert reading['passed'] is True and reading['complete_ui_validation'] is True
        assert reading['total_actual_checks']==len(reading['checks'])==4283
        assert sum(row.get('passed') is True for row in reading['checks'])==4281
        assert sum('passed' not in row for row in reading['checks'])==2
        assert reading['new_explicit_damage_button_requests090']==52
        assert reading['new_explicit_three_text_requests090']==156
        assert reading['source_drift']==reading['source_additional_drift']==[]
    else:
        assert reading['source_freeze_sha256']==sha(FREEZE)
        assert reading['source_sha256_before']==reading['source_sha256_after']==freeze['source_sha256']
        assert reading['source_drift']==[]
        assert reading['passed'] is (mode=='current29')
        assert len(reading['checks'])==29, (mode,len(reading['checks']))
        if mode=='current30':
            assert reading['failure']['type']=='OSError'
            assert 'WinError 1314' in reading['failure']['message'] and 'symlink_to' in reading['failure']['traceback']
        else:
            assert reading['maintenance261_symlink_specialization']=='unavailable: actual same-kind native Windows probe returned WinError1314'
    readings[mode]=reading

for path in destinations.values():path.mkdir()
for mode in ('legacy','current30','current29'):
    target=destinations['legacy'] if mode=='legacy' else destinations['current']/mode
    target.mkdir(parents=True,exist_ok=True)
    status_path,state=states[mode]
    copy_one(status_path,target/'supervisor.json')
    for stream in ('stdout','stderr'):
        row=state[stream]
        source=status_path.parent/row['file']
        assert sha(source)==row['sha256'] and source.stat().st_size==row['bytes']
        copy_one(source,target/row['file'],row['sha256'])
    copy_tree(Path(paths[mode+'_actual']),target/'actual')
copy_tree(bundles['legacy'],destinations['legacy']/'executed-tools')
assert bundles['current30']==bundles['current29']
copy_tree(bundles['current30'],destinations['current']/'executed-tools')
for kind,out in destinations.items():
    copy_one(FREEZE,out/'root-source-freeze.json')
    pin_map=files(out)
    write(out/'archive-manifest.json',{
        'kind':'ACTUAL_NATIVE_FULL275_ATTEMPT3_RAW_BYTE_ARCHIVE','actual_attempt':3,
        'archive_scope':kind,'files':pin_map,'root_source_freeze_sha256':sha(FREEZE),
        'original_live_outputs_and_executed_tools_unchanged':True,
        'historical_original_Windows_game_chat_or_Linux_Wine_verified':False,
        'private_state_read_or_copied':False,'game_operations':0,'chat_requests':0,
        'process_exit_files_created':False})
source_after={name:sha(ROOT/name) for name in freeze['source_sha256']}
assert source_after==source_before
summary={'kind':'ACTUAL_NATIVE_FULL275_ATTEMPT3_ARCHIVE_READBACK','passed_archive_integrity':True,
    'source_count':len(source_before),'source_files_modified':False,'source_freeze_sha256':sha(FREEZE),
    'legacy':{'archive':destinations['legacy'].relative_to(ROOT).as_posix(),
              'child_exit':states['legacy'][1]['child_primary_exit'],'supervisor_exit':states['legacy'][1]['supervisor_exit'],
              'checks':4283,'passed_flags':4281,'meta_records':2,'saved_states':52,'text_requests':156},
    'current30':{'child_exit':1,'passed':False,'workflow_records_before_failure':29,
                 'failure_kind':'ACTUAL_WINERROR1314_SYMLINK_PRIVILEGE_FAILURE_NOT_PASS'},
    'current29':{'child_exit':0,'passed_available_workflows':True,'workflows':29,
                 'symlink_specialization':'UNAVAILABLE_NOT_PASS'},
    'current_archive':destinations['current'].relative_to(ROOT).as_posix()}
write(VERIFY/'current-window-attempt3'/'archive-summary.json',summary)
print(json.dumps(summary,ensure_ascii=False))
