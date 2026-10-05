"""Seal P1 contracts, source evidence and the actual visible test application."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_launch_050 import windows,verify_process,foreground,state
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts,partition


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def text(name):return (ROOT/name).read_text(encoding='utf-8')
def verify_file(name,record):
    data=(ROOT/name).read_bytes()
    assert hashlib.sha256(data).hexdigest()==record['sha256'],name
    if 'bytes' in record:assert len(data)==record['bytes'],name


def main():
    core=read('P1_0.50_VERIFICATION.json');ui=read('UI_0.50_VERIFICATION.json')
    skills=read('SKILL_UI_0.50_VERIFICATION.json');launch=read('APP_0.50_LAUNCH_VERIFICATION.json')
    hashes={}
    for receipt in (core,ui,skills):
        assert receipt['passed'] and receipt['version']=='0.50.0'
        assert receipt['game_actions']==receipt['chat_requests']==0
        for name,sha in receipt.get('source_sha256',receipt.get('source_hashes',{})).items():
            assert digest(name)==sha,name;hashes[name.replace('\\','/')]=sha
    assert (core['tests_run'],core['current_tests_passed'],core['new_unit_tests'])==(662,592,22)
    assert core['historical_combat_tests_skipped']==70 and core['errors']==core['failures']==0
    assert core['deterministic_builds']==2 and core['char_buff_formulas_unchanged']
    assert core['numeric_public_replay_rerun'] and core['default_public_outputs_unchanged']
    assert core['exact_default_public_replays']==732
    assert digest(core['test_log'])==core['test_log_sha256']
    assert digest(core['fresh_previous_public_baseline'])==core['fresh_previous_public_baseline_sha256']
    assert ui['parents_checked']==7 and len(ui['cases'])==26 and all(c['passed'] for c in ui['cases'])
    assert ui['private_state_isolated'] and ui['game_captures']==0
    for name,sha in ui['screenshots'].items():assert digest(name)==sha,name
    assert (skills['skills_checked'],skills['panel_scenarios'],skills['book_panels'],skills['synthetic_module_panels'])==(87,348,174,18)
    assert skills['book_unknown_panels']==skills['book_combination_panels']==9
    assert skills['private_data_isolated'] and skills['unrelated_sections_hidden']
    assert digest(skills['refill_screenshot'])==skills['refill_screenshot_sha256']
    backup='.cache/batch-050-before/';manifest=read(backup+'manifest.json')
    assert len(manifest)==12 and all(digest(backup+n)==sha for n,sha in manifest.items())
    assert not any(n.startswith(('.local/','local-settings')) for n in manifest)
    rules='.cache/research/p1-rules-050/'
    rm=read(rules+'manifest.json');assert len(rm['files'])==12
    for item in rm['files']:verify_file(rules+item['file'],item)
    assert sum(item['bytes'] for item in rm['files'])==rm['total_bytes']==28093642
    download=read(rules+'download-receipt.json');verify_file(download['path'],download)
    data=(ROOT/download['path']).read_bytes()
    assert len(data)==27996217
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==download['git_blob']
    comparison=read(rules+'template-comparison.json')
    assert comparison['old_count']==8292 and comparison['new_count']==8469 and len(comparison['added_keys'])==177
    evidence=read(rules+'evidence.json')
    for item in evidence['sources']:
        name=backup+item['file'] if item['file']=='rouge/data/relic-mechanics.json' else item['file']
        verify_file(name,item)
    assert not evidence['therapy_or_hand4_creation_gap_closed'] and not evidence['private_files_read']
    stack='.cache/research/p1-stack-050/'
    sm=read(stack+'manifest.json')
    for item in sm['files']+sm['source_files']:verify_file(item['path'],item)
    assert len(sm['files'])==10 and len(sm['source_files'])==5
    audit='.cache/research/p1-binding-audit-050/'
    am=read(audit+'manifest.json')
    for item in am['files']:verify_file(audit+item['file'],item)
    for name,sha in am['source_snapshot'].items():assert digest(name)==sha,name
    ae=read(audit+'evidence.json')
    assert len(ae['seven_original_mapping_checks'])==7 and not ae['numeric_double_count_found']
    assert ae['current_operator_scope_and_absence_checks_passed'] and ae['no_recipient_assigned_from_holding']
    assert all(not row['report_claims_numeric_application'] for row in ae['report_counterexamples'])
    assert not ae['automatic_recipient_capture_verified'] and not ae['private_files_read']
    recognition='.cache/research/p1-recognition-050/'
    im=read(recognition+'manifest.json')
    for name,item in im['files'].items():verify_file(name,item)
    prior=read(recognition+'before-backup-replay.json');fixed=read(recognition+'post-fix.json')
    assert prior['tests']['run']==9 and prior['tests']['passed']==4 and len(prior['tests']['failures'])==5
    assert prior['source_sha256']['tested_run_state_backup']==digest(backup+'rouge/run_state.py')
    assert fixed['tests']['run']==fixed['tests']['passed']==9 and not fixed['tests']['errors']
    assert fixed['source_sha256']['rouge/run_state.py']==digest('rouge/run_state.py')
    assert len(fixed['reference_records'])==239 and len(fixed['char_buff_reference_links'])==15
    assert fixed['coverage']['catalog_relics']==272 and not fixed['coverage']['missing_relic_references']
    assert not any(fixed['static_seams'].values())
    for item in fixed['reference_records']:
        name='rouge/data/'+item['file'];verify_file(name,item)
        data=(ROOT/name).read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['git_blob_sha1']
    sampled=read(recognition+'after-root-fix.json');assert len(sampled['saved_samples'])==2
    for sample in sampled['saved_samples']:
        assert digest(sample['file'])==sample['sha256']
        assert len(sample['icons'])==3
    for name in ('rouge/recognition.py','rouge/run_recognition.py','rouge/relic_recognition.py'):
        assert digest(name)==sampled['source_sha256'][name],name
    for name,item in read('.cache/recipient-050/manifest.json')['files'].items():verify_file(name,item)
    assert scope_counts(mechanics())['offline_mechanism_gaps']=={'pending':3,'partial':9}
    assert sum(bool(partition(p,rid)[0]) for rid,p in mechanics()['relics'].items())==135
    assert sum(bool(p.get('recipient_binding')) for p in mechanics()['relics'].values())==7
    old=read('FINAL_0.49_VERIFICATION.json');inherited=[]
    for name in ('rouge/exploration_routes.py','rouge/map_reporting.py','rouge/map_view.py',
        'rouge/map_projection.py','rouge/battle_view.py','rouge/battle_preview.py',
        'rouge/data/battle-map-projections.json','rouge/data/battle-previews.json'):
        assert digest(name)==old['source_sha256'][name],name;inherited.append(name)
    progress=text('PROJECT_PROGRESS.md')
    assert '3件待接入' in progress and '7类稳定强化领取者' in progress
    for token in ('已接入','已完成','验收：','FINAL_0.','## 上批'):assert token not in progress
    header='## 0.49 · 当前位置路线参考与固定地图扩展'
    assert text('PROJECT_COMPLETED.md').split(header,1)[1]==text(backup+'PROJECT_COMPLETED.md').split(header,1)[1]
    assert text('WORK_IN_PROGRESS.md').endswith(text(backup+'WORK_IN_PROGRESS.md'))
    assert '# 黑流树海助手 · 0.50' in text('README.md')
    assert tomllib.loads(text('pyproject.toml'))['project']['version']=='0.50.0'
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not (Path.home()/'.codex/automations/1-3/automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    assert launch['version']=='0.50.0' and launch['game_actions']==launch['chat_requests']==0
    assert all(launch[k] for k in ('only_one_project_window','window_visible_and_restored','window_raised',
        'within_monitor_work_area','previous_app_process_stopped_before_launch','same_run_preserved',
        'history_preserved','settings_and_bindings_unchanged','run_cmd_startup_verified'))
    assert launch['configuration_files_checked']==2 and launch['observation_seconds']==20
    assert len(launch['stability_checks'])==6 and launch['launcher_stderr_bytes']==0
    assert digest('run.cmd')==launch['launcher_sha256']
    checkpoint=read(launch['checkpoint']);after=state();run=read('.local/run-state.json')
    assert checkpoint['run_id_hash']==after['run_id_hash'] and checkpoint['config_hashes']==after['config_hashes']
    prefix=run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    live=windows();assert len(live)==1 and live[0]['pid']==launch['process_id']
    verify_process(live[0]['pid']);focused=foreground(live[0]['hwnd'])
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    for path in (ROOT/'rouge').glob('*.py'):hashes[path.relative_to(ROOT).as_posix()]=digest(path.relative_to(ROOT))
    for base in ('scripts','tests'):
        for path in (ROOT/base).glob('*050.py'):hashes[path.relative_to(ROOT).as_posix()]=digest(path.relative_to(ROOT))
    artifacts=['P1_0.50_VERIFICATION.json','UI_0.50_VERIFICATION.json','SKILL_UI_0.50_VERIFICATION.json',
        'APP_0.50_LAUNCH_VERIFICATION.json','BATCH_0.50.md','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md',
        'README.md','WORK_IN_PROGRESS.md',backup+'manifest.json']
    for directory in ('.cache/p1-050','.cache/mechanisms-050','.cache/recipient-050',
        '.cache/research/p1-rules-050','.cache/research/p1-stack-050',
        '.cache/research/p1-recognition-050','.cache/research/p1-binding-audit-050'):
        artifacts += [p.relative_to(ROOT).as_posix() for p in (ROOT/directory).rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts]
    result={'version':'0.50.0','passed':True,'verified_at':time.time(),'current_tests_passed':592,
        'new_unit_tests':22,'historical_combat_tests_skipped':70,'exact_default_public_replays':732,
        'stable_binding_parent_entries':7,'recipient_ui_cases':26,'char_buff_formulas_unchanged':True,
        'offline_mechanism_gaps':{'pending':3,'partial':9},'activity_relics':135,
        'inventory_regression_tests':9,'prior_code_inventory_failures':5,'reference_png_files_checked':239,
        'saved_inventory_pages':2,'automatic_recipient_reading_verified':False,
        'inherited_map_related_sources_unchanged':inherited,'new_map_gui_replay':False,
        'source_sha256':hashes,'artifact_sha256':{n:digest(n) for n in sorted(set(artifacts))},
        'process_id':live[0]['pid'],'window_title':live[0]['title'],'test_window_open':True,'foreground_verified':focused,
        'history_count_before':checkpoint['history_count'],'history_count_after':after['history_count'],
        'same_current_run_and_history_preserved':True,'configuration_files_unchanged':2,
        'game_actions':0,'chat_requests':0,'recognition_speed_claim':False,
        'all_priorities_1_to_3_completed':False,'all_priority_1_completed':False,
        'limitations':['Stable recipient behavior is synthetic; user has no corresponding enhancement in this run.',
            'Multi-page inventory snapshot and persistent counter/recipient reading are unverified.',
            'New template data do not establish missing creation or stacking scripts.',
            'Current PRTS facts are not downloaded fixed-revision bodies.']}
    (ROOT/'FINAL_0.50_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('passed','current_tests_passed','offline_mechanism_gaps',
        'test_window_open','process_id','history_count_before','history_count_after')},ensure_ascii=False))


if __name__=='__main__':main()
