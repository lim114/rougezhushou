"""Seal verified token caps, research boundaries, delivery and preserved run."""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    names=['CORE_0.69_VERIFICATION.json','NUMERIC_REPLAY_0.69_VERIFICATION.json',
        'NATIVE_UI_0.69_VERIFICATION.json','PACKAGE_0.69_VERIFICATION.json',
        'APP_0.69_LAUNCH_VERIFICATION.json','.cache/research/summon-limit-069/native-proof.json',
        '.cache/research/phatm2-s1-069/native-proof.json']
    receipts=[];evidence={}
    for name in names:
        data=read(ROOT/name);receipts.append(data);evidence[name]=sha(ROOT/name)
        if 'source_sha256' in data:
            assert data['passed'],name
            for source,digest in data['source_sha256'].items():assert sha(ROOT/source)==digest,source
        for field in ('test_log','current_output','worker_receipt','wheel'):
            if field in data:
                p=ROOT/data[field];assert sha(p)==data[field+'_sha256'];evidence[data[field]]=sha(p)
    core,numeric,ui,package,app,cap,wine=receipts
    assert core['tests_run']==1238 and core['current_tests_passed']==1168
    assert core['historical_tests_skipped']==70 and not core['failures'] and not core['errors']
    assert numeric['exact_structured_unchanged']==716 and numeric['all_existing_numerical_fields_unchanged']==732
    assert len(numeric['allowances'])==numeric['expected_report_only_cases']==16 and not numeric['unexpected_changes']
    assert len(ui['checks'])==58
    assert sum(c['scope']=='summon_concurrent_count' for c in ui['checks'])==6
    assert sum(c['scope'].startswith('summon_') and c['scope']!='summon_module_hp_composition' for c in ui['checks'])==13
    assert package['assets_checked']==34 and package['passed']
    assert cap['passed'] and cap['default_limits_without_module']==[2,3,4]
    assert cap['default_e2_limit_with_unlocked_SUM_Y']==7 and cap['instruction_count']==4827
    assert len(cap['verified_methods'])==32
    assert wine['passed'] and wine['native_methods_verified']==16 and wine['native_instructions_verified']==1496
    assert not wine['numerical_model_changed'] and not wine['full_skill_lifecycle_verified']
    assert cap['game_dll_sha256']==wine['dll_sha256'] and cap['metadata_sha256']==wine['metadata_sha256']
    for name,digest in cap['raw_sources_sha256'].items():assert sha(ROOT/'.cache/game-data'/name)==digest,name
    rules=read(ROOT/'rouge/data/summon-module-rules.json')['uniequip_002_deepcl']
    assert rules['concurrent_limit_verified'] and rules['concurrent_limit']==7
    assert rules['base_concurrent_limits']=={'0':2,'1':3,'2':4}
    assert all(row['token_blackboard']['max_deploy_count']==3 for row in cap['module_token_attributes'])
    cfgs=[*sorted((ROOT/'.cache/research/summon-limit-069').glob('*-cfg.json')),
        *sorted((ROOT/'.cache/research/phatm2-s1-069').glob('*-cfg.json'))]
    assert len(cfgs)==13
    first=read(cfgs[0]);dll=Path(first['source_game_dll'])
    meta=dll.parent/'Arknights_Data/il2cpp_data/Metadata/global-metadata.dat'
    dh,mh=sha(dll),sha(meta);count=0;methods=0
    assert dh==wine['dll_sha256'] and mh==wine['metadata_sha256']
    with dll.open('rb') as f:
        for path in cfgs:
            cfg=read(path);assert cfg['dll_sha256']==dh and cfg['metadata_sha256']==mh
            for method in cfg['methods']:
                assert method['cfg_bounded_traversal_finished'] and not method['limits'];methods+=1
                for ins in method['instructions']:
                    data=bytes.fromhex(ins['bytes']);f.seek(int(ins['physical_offset'],16))
                    assert f.read(len(data))==data;count+=1
    assert methods==48 and count==6323
    old=read(ROOT/'.cache/batch-069-before/manifest.json')['files']
    changed=sorted(n for n,h in old.items() if n.startswith('rouge/') and sha(ROOT/n)!=h)
    assert changed==['rouge/app.py','rouge/data/summon-module-rules.json','rouge/operator_engine.py',
        'rouge/operator_options.py','rouge/reporting.py','rouge/summons.py'],changed
    old_engine=(ROOT/'.cache/batch-069-before/rouge/operator_engine.py').read_text(encoding='utf-8')
    engine=(ROOT/'rouge/operator_engine.py').read_text(encoding='utf-8')
    wine_branch=lambda s:s.split("        elif op=='char_1042_phatm2':")[1].split("        elif op=='char_4204_mantra':")[0]
    assert wine_branch(engine)==wine_branch(old_engine),'Wine timing research is not a numerical fix.'
    import verify_launch_069 as launch
    import win32gui
    live=launch.windows();assert len(live)==1
    w=live[0];assert w['title']==launch.TITLE and w['pid']==app['process_id']
    assert w['visible'] and not w['minimized'] and not w['hung']
    launch.verify_process(w['pid']);focused=launch.foreground(w['hwnd'])
    before=read(launch.CHECK);after=launch.state()
    assert before['config_hashes']==after['config_hashes'] and before['run_id_hash']==after['run_id_hash']
    history=read(ROOT/'.local/run-state.json')['history'][:before['history_count']]
    assert hashlib.sha256(json.dumps(history,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==before['history_prefix_hash']
    added={'BATCH_0.69.md','tests/test_summon_limits_069.py',
        '.cache/research/summon-limit-069/REPORT.md','.cache/research/phatm2-s1-069/REPORT.md',
        *[p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('verify_*_069.py')]}
    for folder in ('summon-limit-069','phatm2-s1-069'):
        for p in (ROOT/'.cache/research'/folder).iterdir():
            if p.is_file():evidence[p.relative_to(ROOT).as_posix()]=sha(p)
    result={'version':'0.69.0','passed':True,'verified_at':time.time(),
        'source_sha256':{n:sha(ROOT/n) for n in sorted(set(old)|added)},'evidence_sha256':evidence,
        'existing_production_files_changed':changed,'new_production_files':[],
        'current_priority':'P2 first by latest user instruction','recognition_changed':False,
        'mechanism_data_changed':True,'related_tests_passed':33,'new_regression_tests':9,
        'current_core_tests_passed':1168,'historical_tests_skipped':70,
        'existing_numerical_outputs_unchanged':732,'exact_structured_outputs_unchanged':716,
        'report_only_cases_updated':16,'temporary_qt_checks':58,'new_summon_qt_checks':13,
        'new_live_recognition_acceptance':False,'new_live_panel_acceptance':False,
        'default_concurrent_token_limit_verified':True,'wine_full_lifecycle_verified':False,
        'wine_numerical_model_changed':False,'native_methods_verified':methods,'native_instructions_verified':count,
        'current_hotfix_equivalence_proven':False,'all_priority_1_completed':False,'all_priority_2_completed':False,
        'test_window':w,'foreground':focused and win32gui.GetForegroundWindow()==w['hwnd'],
        'same_run_and_history_preserved':True,'configuration_files_preserved':len(after['config_hashes']),
        'package_rebuilt':True,'private_backups_created':False,'game_actions':0,'chat_requests':0,
        'agents_spawned':1,'agent_scope':'read-only mechanism research and review; no production edits or overlapping checks'}
    with (ROOT/'FINAL_0.69_VERIFICATION.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:result[k] for k in ('passed','current_core_tests_passed','temporary_qt_checks',
        'native_instructions_verified','test_window','foreground')},ensure_ascii=False))

if __name__=='__main__':main()
