"""Seal the completed P2 summon composition batch and real test window."""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    names=['CORE_0.68_VERIFICATION.json','NUMERIC_REPLAY_0.68_VERIFICATION.json',
        'NATIVE_UI_0.68_VERIFICATION.json','PACKAGE_0.68_VERIFICATION.json',
        'APP_0.68_LAUNCH_VERIFICATION.json','.cache/research/summon-068/native-proof.json']
    evidence={};receipts=[]
    for name in names:
        p=ROOT/name;data=read(p);receipts.append(data);evidence[name]=sha(p)
        if 'source_sha256' in data:
            assert data['passed'],name
            for source,digest in data['source_sha256'].items():assert sha(ROOT/source)==digest,source
        for field in ('test_log','current_output','worker_receipt','wheel'):
            if field in data:
                p=ROOT/data[field];assert sha(p)==data[field+'_sha256'];evidence[data[field]]=sha(p)
    core,numeric,ui,package,app,proof=receipts
    assert core['tests_run']==1229 and core['current_tests_passed']==1159
    assert numeric['exact_structured_unchanged']==732 and not numeric['allowances']
    assert len(ui['checks'])==45 and sum(c['scope']=='summon_module_hp_composition' for c in ui['checks'])==18
    assert package['assets_checked']==34 and proof['parsed_objects']==9220
    import verify_launch_068 as launch
    import win32gui
    windows=launch.windows();assert len(windows)==1
    w=windows[0]
    assert w['title']==launch.TITLE and w['pid']==app['process_id']
    assert w['visible'] and not w['minimized'] and not w['hung']
    launch.verify_process(w['pid']);focused=launch.foreground(w['hwnd'])
    before=read(launch.CHECK);after=launch.state()
    assert before['config_hashes']==after['config_hashes'] and before['run_id_hash']==after['run_id_hash']
    history=read(ROOT/'.local/run-state.json')['history'][:before['history_count']]
    assert hashlib.sha256(json.dumps(history,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==before['history_prefix_hash']
    old=read(ROOT/'.cache/batch-068-before/manifest.json')['files']
    changed=sorted(n for n,h in old.items() if n.startswith('rouge/') and sha(ROOT/n)!=h)
    assert changed==['rouge/app.py','rouge/data/summon-module-rules.json','rouge/reporting.py','rouge/summons.py'],changed
    added={'BATCH_0.68.md','tests/test_summon_composition_068.py',
        *[p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('verify_*_068.py')]}
    for p in (ROOT/'.cache/research/summon-068').iterdir():
        if p.is_file():evidence[p.relative_to(ROOT).as_posix()]=sha(p)
    result={'version':'0.68.0','passed':True,'verified_at':time.time(),
        'source_sha256':{n:sha(ROOT/n) for n in sorted(set(old)|added)},'evidence_sha256':evidence,
        'existing_production_files_changed':changed,'new_production_files':[],
        'current_priority':'P2 first by latest user instruction','recognition_changed':False,
        'mechanism_data_changed':True,'related_tests_passed':24,'new_regression_tests':6,
        'current_core_tests_passed':1159,'historical_tests_skipped':70,
        'complete_calculation_outputs_unchanged':732,'temporary_qt_checks':45,'new_summon_qt_checks':18,
        'new_live_recognition_acceptance':False,'new_live_panel_acceptance':False,
        'module_hp_composition_verified_against_pinned_sources':True,'concurrent_token_limit_verified':False,
        'current_hotfix_equivalence_proven':False,'all_priority_1_completed':False,'all_priority_2_completed':False,
        'test_window':w,'foreground':focused and win32gui.GetForegroundWindow()==w['hwnd'],
        'same_run_and_history_preserved':True,'configuration_files_preserved':len(after['config_hashes']),
        'package_rebuilt':True,'private_backups_created':False,'game_actions':0,'chat_requests':0,'agents_spawned':0}
    with (ROOT/'FINAL_0.68_VERIFICATION.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:result[k] for k in ('passed','current_core_tests_passed','temporary_qt_checks','test_window','foreground')},ensure_ascii=False))

if __name__=='__main__':main()
