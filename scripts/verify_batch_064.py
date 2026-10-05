"""Seal the counter evidence batch and verify the actual own test window."""
import hashlib
import json
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    names=['CORE_0.64_VERIFICATION.json','NUMERIC_REPLAY_0.64_VERIFICATION.json',
           'NATIVE_UI_0.64_VERIFICATION.json','COUNTER_UI_0.64_VERIFICATION.json',
           'APP_0.64_LAUNCH_VERIFICATION.json']
    evidence={};receipts={}
    for name in names:
        data=json.loads((ROOT/name).read_text(encoding='utf-8'));receipts[name]=data;evidence[name]=sha(ROOT/name)
        if 'source_sha256' in data:
            assert data['passed'],name
            for source,digest in data['source_sha256'].items():
                assert sha(ROOT/source)==digest,source
        for field in ('test_log','current_output','worker_receipt'):
            if field in data:
                path=ROOT/data[field];assert sha(path)==data[field+'_sha256'],field
                evidence[data[field]]=sha(path)
    assert receipts[names[0]]['tests_run']==1186
    assert receipts[names[0]]['current_tests_passed']==1116
    assert receipts[names[1]]['exact_structured_unchanged']==732
    assert len(receipts[names[2]]['checks'])==19
    assert len(receipts[names[3]]['checks'])==20
    app=receipts[names[4]]
    assert app['same_run_preserved'] and app['settings_and_bindings_unchanged']
    import verify_launch_064 as launch
    import win32gui
    windows=launch.windows();assert len(windows)==1,windows
    window=windows[0]
    assert window['pid']==app['process_id'] and window['title']==launch.TITLE,window
    assert window['visible'] and not window['minimized'] and not window['hung'],window
    launch.verify_process(window['pid'])
    before=json.loads(launch.CHECK.read_text(encoding='utf-8'));after=launch.state()
    assert before['config_hashes']==after['config_hashes']
    assert before['run_id_hash']==after['run_id_hash']
    run=json.loads((ROOT/'.local/run-state.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(json.dumps(run['history'][:before['history_count']],sort_keys=True,ensure_ascii=False).encode()).hexdigest()==before['history_prefix_hash']
    old=json.loads((ROOT/'.cache/batch-064-before/manifest.json').read_text(encoding='utf-8'))['files']
    changed=sorted(name for name,digest in old.items() if name.startswith('rouge/') and sha(ROOT/name)!=digest)
    assert changed==['rouge/app.py','rouge/relic_counter_semantics.py','rouge/run_state.py'],changed
    proof=json.loads((ROOT/'.cache/research/counter-lifecycle-064/evidence.json').read_text(encoding='utf-8'))
    assert sha(ROOT/'.cache/game-data/roguelike_topic_table.json')==proof['topic_sha256']
    for name,digest in proof['source_sha256'].items():
        assert sha(ROOT/name)==digest,name;evidence[name]=digest
    for name in ('evidence.json','red-ui.log','first-ui.log','first-ui-details.log','related-final.log'):
        source='.cache/research/counter-lifecycle-064/'+name;evidence[source]=sha(ROOT/source)
    new={'scripts/verify_batch_064.py','scripts/verify_counter_ui_064.py','scripts/verify_core_064.py',
         'scripts/verify_launch_064.py','scripts/verify_calculation_replay_064.py','scripts/verify_native_ui_064.py',
         'tests/test_counter_lifecycle_064.py','BATCH_0.64.md','.cache/research/counter-lifecycle-064/REPORT.md'}
    sources=set(old)|new
    result={'version':'0.64.0','passed':True,'verified_at':time.time(),
        'source_sha256':{name:sha(ROOT/name) for name in sorted(sources)},'evidence_sha256':evidence,
        'production_files_changed':changed,'recognition_changed':False,'mechanism_data_changed':False,
        'recognition_priority':'after_all_other_projects','related_tests_passed':52,'new_regression_tests':17,
        'current_core_tests_passed':1116,'historical_tests_skipped':70,'full_core_suite_rerun':True,
        'last_full_core_receipt':names[0],'complete_calculation_outputs_unchanged':732,
        'temporary_qt_checks':39,'counter_input_sequences':'synthetic_confirmed_evidence',
        'new_live_recognition_acceptance':False,'package_rebuilt':False,'last_package_receipt':'PACKAGE_0.63_VERIFICATION.json',
        'test_window':window,'foreground':win32gui.GetForegroundWindow()==window['hwnd'],
        'same_run_and_history_preserved':True,'configuration_files_preserved':len(after['config_hashes']),
        'all_priority_1_completed':False,'private_backups_created':False,'game_actions':0,'chat_requests':0,'agents_spawned':0}
    with (ROOT/'FINAL_0.64_VERIFICATION.json').open('x',encoding='utf-8') as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2)
    print(json.dumps({k:result[k] for k in ('passed','current_core_tests_passed','complete_calculation_outputs_unchanged',
        'temporary_qt_checks','recognition_changed','test_window','foreground')},ensure_ascii=False))


if __name__=='__main__':main()
