"""Validate the documented impact delay, receipts, state and actual test window."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from rouge.relics import mechanics
from rouge.offline_scope import partition,scope_counts
from verify_launch_037 import windows,foreground,verify_process


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    core=read('IMPACT_0.37_VERIFICATION.json');ui=read('UI_0.37_VERIFICATION.json')
    launch=read('APP_0.37_LAUNCH_VERIFICATION.json');audit=read('RELIC_VERIFICATION.json')
    evidence=read('.cache/research/impact-037/evidence.json')
    previous=read('FINAL_0.36_VERIFICATION.json');data=mechanics()
    assert all(r['version']=='0.37.0' for r in (core,ui,launch,audit,evidence))
    assert core['passed'] and core['current_tests_passed']==291 and core['new_tests']==14
    assert core['tests_run']==361 and core['historical_combat_tests_skipped']==70
    assert core['failures']==core['errors']==0
    assert core['full_public_output_cases']==732 and core['exact_unchanged_cases']==728
    assert core['documented_delay_cases']==4 and core['previous_output_reproduced_without_new_delay']
    assert digest(core['test_log'])==core['test_log_sha256']
    assert digest('.cache/impact-037/before-public-results.json')==core['baseline_sha256']
    scope=scope_counts(data)
    assert scope==core['offline_scope']==audit['offline_scope']==previous['scope']
    assert data['counts']==core['data_rule_counts']==audit['data_rule_counts']
    active=[rid for rid,p in data['relics'].items() if partition(p,rid)[0]]
    assert len(active)==135 and scope['offline_mechanism_gaps']=={'pending':10,'partial':9}
    assert digest('.cache/game-data/roguelike_topic_table.json')==data['source_sha256']
    assert evidence['recognition_change']=='none' and evidence['source_commit']==data['commit']
    assert evidence['standing_instruction_file']=='AGENTS.md' and evidence['inherited_unknowns']
    assert digest(evidence['source_snapshot'])==evidence['source_snapshot_sha256']
    assert digest(evidence['raw_skill_source'])==evidence['raw_skill_source_sha256']
    assert digest(evidence['inherited_evidence'])==evidence['inherited_evidence_sha256']
    assert not evidence['source_revision_pinned'] and evidence['delay_not_in_skill_blackboard']
    assert len(evidence['preview_examples'])==3 and evidence['remaining_specific_unknowns']
    fixed=read('rouge/data/skill-impact-delays.json')
    assert list(fixed)==['mechanist'] and list(fixed['mechanist'])==['3']
    assert fixed['mechanist']['3']['seconds']==.8
    assert fixed['mechanist']['3']['source_url']==evidence['source_page']
    assert ui['passed'] and ui['skills_checked']==87 and ui['panel_scenarios']==348
    assert ui['wine_phase_panels']==22 and ui['fixed_delay_panels']==4
    assert all(ui[key] for key in ('unrelated_sections_hidden','native_options_appropriate',
        'event_input_absent','private_data_isolated','fixed_delay_only_on_supported_skill'))
    assert audit['public_entry_cases']==8704 and audit['bound_recipient_cases']==609
    assert audit['forbidden_skill_cases']==87
    icons=read('TARGET_ICON_VERIFICATION.json');assert len(icons['icons'])==15
    assert not icons['recipient_capture_layout_verified']
    for icon in icons['icons']:assert digest('rouge/data/'+icon['file'])==icon['sha256']
    hashes={}
    for receipt in (core,ui,audit):
        for name,checksum in receipt['source_hashes'].items():
            assert digest(name)==checksum,name;hashes[name]=checksum
    for name,checksum in core['preserved_source_hashes'].items():
        assert digest(name)==checksum,name;hashes[name]=checksum
    preserved=('rouge/relic_recognition.py','rouge/run_state.py','rouge/run_config.py',
        'rouge/run_recognition.py','rouge/resource_recognition.py','rouge/recognition.py',
        'rouge/visual_recognition.py','rouge/data/run-config.json',
        'rouge/data/relic-reference-equivalence.json','rouge/operator_engine.py',
        'rouge/elemental_relics.py','rouge/relics.py','rouge/estimate.py','rouge/damage.py',
        'rouge/sp_events.py','rouge/run_modifiers.py','rouge/offline_scope.py',
        'rouge/deployment.py','rouge/catalog.py','AGENTS.md')
    for name in preserved:
        assert digest(name)==previous['source_sha256'][name],name;hashes[name]=digest(name)
    manifest=read('.cache/batch-037-before/manifest.json');assert len(manifest)==12
    for name,checksum in manifest.items():assert digest('.cache/batch-037-before/'+name)==checksum,name
    baseline=read('.cache/impact-037/baseline.json')
    for name in ('rouge/timing.py','rouge/reporting.py','tests/test_relics.py','tests/test_timing.py'):
        recorded=(baseline['source_hashes'][name] if name in baseline['source_hashes']
                  else previous['source_sha256'][name])
        assert manifest[name]==recorded,name
    before_app=(ROOT/'.cache/batch-037-before/rouge/app.py').read_text(encoding='utf-8')
    assert (ROOT/'rouge/app.py').read_text(encoding='utf-8')==before_app.replace('0.36','0.37')
    for r in (core,ui,launch,evidence):assert r['chat_requests']==r['game_actions']==0
    for key in ('only_one_project_window','window_visible_and_restored','same_run_preserved',
        'history_preserved','settings_and_bindings_unchanged','run_cmd_startup_verified',
        'within_monitor_work_area','window_raised','previous_app_process_stopped_before_launch'):
        assert launch[key],key
    assert launch['run_state_writes_by_upgrade_script']==0 and launch['launcher_stderr_bytes']==0
    assert len(launch['stability_checks'])==6 and launch['observation_seconds']==20
    assert launch['launcher_sha256']==digest('run.cmd')
    checkpoint=read('.cache/upgrade-0.37-checkpoint.json');run=read('.local/run-state.json')
    assert checkpoint['history_count']==launch['history_count_before']
    assert hashlib.sha256(str(run.get('id')).encode()).hexdigest()==checkpoint['run_id_hash']
    prefix=run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    for name,checksum in checkpoint['config_hashes'].items():assert digest(name)==checksum,name
    assert len(checkpoint['config_hashes'])==launch['configuration_files_checked']
    live=windows();assert len(live)==1 and live[0]['pid']==launch['process_id']
    assert live[0]['title']=='黑流树海助手 0.37 · 识别与计算测试版'
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    verify_process(live[0]['pid']);focused=foreground(live[0]['hwnd'])
    project=tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))
    assert project['project']['version']=='0.37.0'
    assert 'data/*.json' in project['tool']['setuptools']['package-data']['rouge']
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    names=('IMPACT_0.37_VERIFICATION.json','UI_0.37_VERIFICATION.json','APP_0.37_LAUNCH_VERIFICATION.json',
        'RELIC_VERIFICATION.json','TARGET_ICON_VERIFICATION.json','.cache/research/impact-037/evidence.json',
        evidence['source_snapshot'],'.cache/impact-037/before-public-results.json',core['test_log'],
        '.cache/impact-037/initial-tests.log','.cache/batch-037-before/manifest.json',
        '.cache/upgrade-0.37-checkpoint.json','PROJECT_PROGRESS.md','WORK_IN_PROGRESS.md','BATCH_0.37.md','README.md')
    for name in ('scripts/verify_final_037.py','scripts/verify_launch_037.py',
        'scripts/build_impact_evidence_037.py','pyproject.toml'):hashes[name]=digest(name)
    receipt={'version':'0.37.0','passed':True,'verified_at':time.time(),
        'current_tests_passed':291,'new_tests':14,'historical_combat_tests_skipped':70,
        'full_public_output_cases':732,'exact_unchanged_cases':728,'documented_delay_cases':4,
        'skills_checked':87,'ui_panel_scenarios':348,'fixed_delay_panels':4,
        'public_entry_cases':8704,'bound_recipient_cases':609,'forbidden_skill_cases':87,'bound_icon_hashes':15,
        'active_relic_rules':135,'scope':scope,'recognition_and_relic_mechanism_data_unchanged':True,
        'mechanist_s3_fixed_impact_delay_seconds':.8,'source_revision_pinned':False,
        'process_id':live[0]['pid'],'test_window_open':True,'window_raised':True,
        'foreground_on_final_check':focused,'run_cmd_startup_verified':True,
        'previous_app_process_stopped_before_launch':True,'same_current_run_and_history_preserved':True,
        'history_count_before':checkpoint['history_count'],'history_count_after':len(run['history']),
        'private_configuration_files_verified':len(checkpoint['config_hashes']),
        'chat_requests':0,'game_actions':0,'new_live_combat_measurements':0,
        'run_state_writes_by_upgrade_script':0,'automation_id':'1-3','automation_status':'DELETED',
        'all_priorities_1_to_3_completed':False,'source_sha256':hashes,
        'evidence_sha256':{name:digest(name) for name in names},
        'limits':core['limits']+['The PRTS web content is saved, but its MediaWiki revision fetch failed.',
            '10 offline pending and9 data-partial items remain; beneficiary capture layout is unverified.']}
    (ROOT/'FINAL_0.37_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','full_public_output_cases',
        'exact_unchanged_cases','documented_delay_cases','ui_panel_scenarios','test_window_open',
        'process_id','history_count_before','history_count_after','private_configuration_files_verified',
        'all_priorities_1_to_3_completed')}),flush=True)


if __name__=='__main__':main()
