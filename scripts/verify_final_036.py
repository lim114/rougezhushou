"""Audit exact results, measured scope, unique visible app and fresh run prefix."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from rouge.relics import mechanics
from rouge.offline_scope import partition,scope_counts
from verify_launch_036 import windows,foreground,verify_process


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    core=read('PHASE_0.36_VERIFICATION.json');ui=read('UI_0.36_VERIFICATION.json')
    perf=read('PERFORMANCE_0.36_VERIFICATION.json');launch=read('APP_0.36_LAUNCH_VERIFICATION.json')
    audit=read('RELIC_VERIFICATION.json');evidence=read('.cache/research/phase-036/evidence.json')
    previous=read('FINAL_0.35_VERIFICATION.json');data=mechanics()
    assert all(r['version']=='0.36.0' for r in (core,ui,perf,launch,audit,evidence))
    assert core['passed'] and core['current_tests_passed']==277 and core['new_tests']==9
    assert core['tests_run']==347 and core['historical_combat_tests_skipped']==70
    assert core['failures']==core['errors']==0
    assert core['full_public_output_cases']==core['exact_unchanged_cases']==732
    assert digest(core['test_log'])==core['test_log_sha256']
    assert digest('.cache/phase-036/before-public-results.json')==core['baseline_sha256']
    scope=scope_counts(data)
    assert scope==core['offline_scope']==audit['offline_scope']==previous['scope']
    assert data['counts']==core['data_rule_counts']==audit['data_rule_counts']
    active=[rid for rid,p in data['relics'].items() if partition(p,rid)[0]]
    assert len(active)==135 and scope['offline_mechanism_gaps']=={'pending':10,'partial':9}
    assert digest('rouge/data/relic-mechanics.json')==previous['source_sha256']['rouge/data/relic-mechanics.json']
    assert digest('.cache/game-data/roguelike_topic_table.json')==data['source_sha256']
    assert evidence['mechanism_change']==evidence['recognition_change']=='none'
    assert evidence['source_commit']==data['commit'] and not evidence['hand_4_matching_current_profiles']
    assert evidence['standing_instruction_file']=='AGENTS.md' and evidence['unknowns']
    assert len(evidence['primary_sources']['animation_head_checks'])==2
    assert perf['passed'] and len(perf['cases'])==4 and perf['allocation_samples']==1
    for case in perf['cases']:
        assert case['paired_repeats']==7
        assert case['preparation_calls']['after']=={'cultivation':1,'relics':1,'run_environment':1}
        assert all(len(values)==7 for values in case['durations_ms'].values())
    traced=[case for case in perf['cases'] if case['traced_peak_bytes']]
    assert len(traced)==1 and traced[0]['traced_peak_bytes']['after']<traced[0]['traced_peak_bytes']['before']
    assert perf['current_source_sha256']==digest('rouge/damage.py')
    assert ui['passed'] and ui['skills_checked']==87 and ui['panel_scenarios']==348
    assert ui['wine_phase_panels']>0
    assert all(ui[key] for key in ('unrelated_sections_hidden','native_options_appropriate',
                                   'event_input_absent','private_data_isolated'))
    assert audit['public_entry_cases']==8704 and audit['bound_recipient_cases']==609
    assert audit['forbidden_skill_cases']==87
    icons=read('TARGET_ICON_VERIFICATION.json');assert len(icons['icons'])==15
    assert not icons['recipient_capture_layout_verified']
    for icon in icons['icons']:assert digest('rouge/data/'+icon['file'])==icon['sha256']
    hashes={}
    for receipt in (core,ui,audit):
        for name,checksum in receipt['source_hashes'].items():
            assert digest(name)==checksum,name
            hashes[name]=checksum
    for name,checksum in core['existing_model_hashes'].items():assert digest(name)==checksum,name
    preserved=('rouge/relic_recognition.py','rouge/run_state.py','rouge/run_config.py',
        'rouge/run_recognition.py','rouge/resource_recognition.py','rouge/recognition.py',
        'rouge/visual_recognition.py','rouge/data/run-config.json',
        'rouge/data/relic-reference-equivalence.json','rouge/operator_engine.py',
        'rouge/elemental_relics.py','rouge/relics.py','rouge/estimate.py','rouge/timing.py',
        'rouge/sp_events.py','rouge/run_modifiers.py','rouge/reporting.py','rouge/offline_scope.py',
        'rouge/deployment.py','rouge/catalog.py','AGENTS.md')
    for name in preserved:
        assert digest(name)==previous['source_sha256'][name],name
        hashes[name]=digest(name)
    manifest=read('.cache/batch-036-before/manifest.json')
    assert len(manifest)==9
    for name,checksum in manifest.items():assert digest('.cache/batch-036-before/'+name)==checksum,name
    assert digest('.cache/batch-036-before/rouge/damage.py')==perf['baseline_source_sha256']
    before_app=(ROOT/'.cache/batch-036-before/rouge/app.py').read_text(encoding='utf-8')
    assert (ROOT/'rouge/app.py').read_text(encoding='utf-8')==before_app.replace(
        '黑流树海助手 0.35 · 识别与计算测试版','黑流树海助手 0.36 · 识别与计算测试版')
    for r in (core,ui,perf,launch):assert r['chat_requests']==r['game_actions']==0
    for key in ('only_one_project_window','window_visible_and_restored','same_run_preserved',
                'history_preserved','settings_and_bindings_unchanged','run_cmd_startup_verified',
                'within_monitor_work_area','window_raised','previous_app_process_stopped_before_launch'):
        assert launch[key],key
    assert launch['run_state_writes_by_upgrade_script']==0 and launch['launcher_stderr_bytes']==0
    assert len(launch['stability_checks'])==6 and launch['observation_seconds']==20
    assert launch['launcher_sha256']==digest('run.cmd')
    checkpoint=read('.cache/upgrade-0.36-checkpoint.json');run=read('.local/run-state.json')
    assert checkpoint['history_count']==launch['history_count_before']
    assert hashlib.sha256(str(run.get('id')).encode()).hexdigest()==checkpoint['run_id_hash']
    prefix=run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    for name,checksum in checkpoint['config_hashes'].items():assert digest(name)==checksum,name
    assert len(checkpoint['config_hashes'])==launch['configuration_files_checked']
    live=windows();assert len(live)==1 and live[0]['pid']==launch['process_id']
    assert live[0]['title']=='黑流树海助手 0.36 · 识别与计算测试版'
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    verify_process(live[0]['pid'])
    assert tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']=='0.36.0'
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    names=('PHASE_0.36_VERIFICATION.json','PERFORMANCE_0.36_VERIFICATION.json','UI_0.36_VERIFICATION.json',
        'APP_0.36_LAUNCH_VERIFICATION.json','RELIC_VERIFICATION.json','TARGET_ICON_VERIFICATION.json',
        '.cache/research/phase-036/evidence.json','.cache/research/timing-036/head-check.json',
        '.cache/phase-036/before-public-results.json',core['test_log'],'.cache/batch-036-before/manifest.json',
        '.cache/upgrade-0.36-checkpoint.json','PROJECT_PROGRESS.md','WORK_IN_PROGRESS.md','BATCH_0.36.md','README.md')
    for name in ('scripts/verify_final_036.py','scripts/verify_launch_036.py',
                 'scripts/benchmark_phase_flow_036.py','pyproject.toml'):hashes[name]=digest(name)
    receipt={'version':'0.36.0','passed':True,'verified_at':time.time(),'current_tests_passed':277,'new_tests':9,
        'historical_combat_tests_skipped':70,'full_public_output_cases':732,'exact_unchanged_cases':732,
        'skills_checked':87,'ui_panel_scenarios':348,'public_entry_cases':8704,
        'bound_recipient_cases':609,'forbidden_skill_cases':87,'bound_icon_hashes':15,
        'active_relic_rules':135,'scope':scope,'recognition_and_mechanism_data_unchanged':True,
        'process_id':live[0]['pid'],'test_window_open':True,'window_raised':True,
        'foreground_on_final_check':foreground(live[0]['hwnd']),'run_cmd_startup_verified':True,
        'previous_app_process_stopped_before_launch':True,'same_current_run_and_history_preserved':True,
        'history_count_before':checkpoint['history_count'],'history_count_after':len(run['history']),
        'private_configuration_files_verified':len(checkpoint['config_hashes']),
        'chat_requests':0,'game_actions':0,'new_live_combat_measurements':0,
        'run_state_writes_by_upgrade_script':0,'automation_id':'1-3','automation_status':'DELETED',
        'all_priorities_1_to_3_completed':False,'source_sha256':hashes,
        'evidence_sha256':{name:digest(name) for name in names},
        'limits':core['limits']+perf['limits']+[
            'No new full-page recognition speed or complete inventory accuracy claim.',
            '10 offline pending and 9 data-partial items remain; beneficiary capture layout is unverified.']}
    (ROOT/'FINAL_0.36_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','full_public_output_cases',
        'ui_panel_scenarios','test_window_open','process_id','history_count_before','history_count_after',
        'private_configuration_files_verified','all_priorities_1_to_3_completed')}),flush=True)


if __name__=='__main__':main()
