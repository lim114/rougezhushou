"""Seal current P1 performance scope and its direct verification evidence."""
import hashlib,json,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def check(mapping):
    for name,digest in mapping.items():
        p=(ROOT/name).resolve()
        assert p.is_relative_to(ROOT) and '.local' not in p.relative_to(ROOT).parts
        assert sha(p)==digest,name


def main():
    names=['CORE_0.61_VERIFICATION.json','NUMERIC_REPLAY_0.61_VERIFICATION.json',
           'NATIVE_UI_0.61_VERIFICATION.json','PACKAGE_0.61_VERIFICATION.json',
           'HELD_REPLAY_0.61_VERIFICATION.json','HELD_PERFORMANCE_0.61_VERIFICATION.json']
    results={name:read(name) for name in names}
    for name,result in results.items():assert result['passed'] and result['version']=='0.61.0',name
    core=results[names[0]];numeric=results[names[1]];package=results[names[3]]
    assert not core['source_drift_during_tests'] and core['failures']==core['errors']==0
    assert numeric['exact_structured_unchanged']==732 and not numeric['allowances']
    assert results[names[4]]['strict_equal_cases']==6
    evidence={name:sha(ROOT/name) for name in names}
    for name,result in results.items():
        for key in ('source_sha256','source_sha256_after','full_formal_source_sha256_after',
                    'replay_receipts','workers'):
            if key in result:check(result[key])
        for key in ('replay_receipts','workers'):
            evidence.update(result.get(key,{}))
    for name in (core['test_log'],numeric['current_output'],numeric['worker_receipt'],package['wheel']):
        evidence[name]=sha(ROOT/name)
    assert evidence[package['wheel']]==package['wheel_sha256']
    research=ROOT/'.cache/research/held-performance-061'
    for p in research.glob('*'):
        if p.is_file():evidence[p.relative_to(ROOT).as_posix()]=sha(p)
    for name in ('inventory.json','baseline-package-seal.json'):
        p=research/'actual-reader'/name;evidence[p.relative_to(ROOT).as_posix()]=sha(p)
    app=read('APP_0.61_LAUNCH_VERIFICATION.json')
    for key in ('only_one_project_window','window_visible_and_restored','within_monitor_work_area',
                'same_run_preserved','history_preserved','settings_and_bindings_unchanged','run_cmd_startup_verified'):
        assert app[key],key
    evidence['APP_0.61_LAUNCH_VERIFICATION.json']=sha(ROOT/'APP_0.61_LAUNCH_VERIFICATION.json')
    files={ROOT/name for name in core['source_sha256_after'] if not name.startswith('.cache/')}
    files.update((ROOT/'scripts').glob('*_061.py'));files.update((ROOT/'tests').glob('*_061.py'))
    files.update(ROOT/name for name in ('pyproject.toml','run.cmd','PROJECT_PROGRESS.md',
                 'PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','BATCH_0.61.md'))
    sources={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(files)}
    check(evidence)
    receipt={'version':'0.61.0','passed':True,'verified_at':time.time(),'source_sha256':sources,
        'receipt_sha256':evidence,'core_tests_run':core['tests_run'],
        'current_tests_passed':core['current_tests_passed'],'historical_skipped':core['historical_tests_skipped'],
        'numeric_exact_cases':732,'actual_reader_equal_cases':6,'all_priority_1_completed':False,
        'private_state_copied':False,'game_actions':0,'chat_requests':0,'automation_recreated':False,
        'scope':'Bounded concurrent original refinement calls; local hotspot benefit only, no universal speed claim.'}
    with (ROOT/'FINAL_0.61_VERIFICATION.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
    print(json.dumps({'passed':True,'source_files':len(sources),'evidence_files':len(evidence)}))


if __name__=='__main__':main()
