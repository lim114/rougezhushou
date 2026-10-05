"""Validate summon references, regression receipts and the actual test window."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from rouge.relics import mechanics
from rouge.offline_scope import partition,scope_counts
from verify_launch_038 import windows,foreground,verify_process

def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

def main():
    core=read('SUMMON_0.38_VERIFICATION.json');ui=read('UI_0.38_VERIFICATION.json')
    launch=read('APP_0.38_LAUNCH_VERIFICATION.json');audit=read('RELIC_VERIFICATION.json')
    evidence=read('.cache/research/summon-038/evidence.json')
    previous=read('FINAL_0.37_VERIFICATION.json');data=mechanics()
    assert all(r['version']=='0.38.0' for r in (core,ui,launch,audit,evidence))
    assert core['passed'] and core['current_tests_passed']==309 and core['new_tests']==18
    assert core['tests_run']==379 and core['historical_combat_tests_skipped']==70
    assert core['failures']==core['errors']==0 and core['exact_public_output_cases']==732
    assert core['module_matrix_cases']==264 and core['eligible_module_cases']==108
    assert core['unaffected_module_cases']==156 and core['all_relic_module_damage_invariance_cases']==544
    assert digest(core['test_log'])==core['test_log_sha256']
    for name,checksum in core['baseline_hashes'].items():assert digest(name)==checksum,name
    scope=scope_counts(data)
    assert scope==core['offline_scope']==audit['offline_scope']==previous['scope']
    assert data['counts']==core['data_rule_counts']==audit['data_rule_counts']
    assert sum(bool(partition(p,rid)[0]) for rid,p in data['relics'].items())==135
    assert scope['offline_mechanism_gaps']=={'pending':10,'partial':9}
    assert digest('.cache/game-data/roguelike_topic_table.json')==data['source_sha256']
    assert evidence['source_commit']==data['commit'] and evidence['recognition_change']=='none'
    assert evidence['numerical_relic_rules_change']=='none' and not evidence['source_revision_pinned']
    assert digest(evidence['source_snapshot'])==evidence['source_snapshot_sha256']
    for name,checksum in evidence['raw_sources_sha256'].items():assert digest(name)==checksum,name
    assert digest(evidence['inherited_evidence'])==evidence['inherited_evidence_sha256']
    assert len(evidence['preview_examples'])==5 and evidence['remaining_specific_unknowns']
    assert len(evidence['new_backlog'])==5 and evidence['battle_map_download_authorized']
    assert evidence['battle_map_assets_downloaded_this_batch']==0
    rules=read('rouge/data/summon-module-rules.json')
    assert list(rules)==['uniequip_002_deepcl']
    rule=rules['uniequip_002_deepcl']
    assert rule['operator']=='char_110_deepcl' and not rule['hp_composition_verified']
    assert rule['concurrent_limit'] is None
    assert ui['passed'] and ui['skills_checked']==87 and ui['panel_scenarios']==348
    assert ui['synthetic_module_panels']==18 and ui['wine_phase_panels']==22 and ui['fixed_delay_panels']==4
    assert all(ui[key] for key in ('unrelated_sections_hidden','native_options_appropriate',
        'event_input_absent','private_data_isolated','module_hp_unknown_guard_visible',
        'only_readonly_module_metrics','synthetic_cultivation_only'))
    assert audit['public_entry_cases']==8704 and audit['bound_recipient_cases']==609
    assert audit['forbidden_skill_cases']==87
    icons=read('TARGET_ICON_VERIFICATION.json');assert len(icons['icons'])==15
    assert not icons['recipient_capture_layout_verified']
    for icon in icons['icons']:assert digest('rouge/data/'+icon['file'])==icon['sha256']
    hashes={}
    for receipt in (core,ui,audit):
        for name,checksum in receipt['source_hashes'].items():
            assert digest(name)==checksum,name;hashes[name]=checksum
    modified={'rouge/relics.py','rouge/operator_engine.py','rouge/operator_options.py','rouge/reporting.py','rouge/app.py'}
    for name,checksum in previous['source_sha256'].items():
        if name.startswith('rouge/') and name not in modified:
            assert digest(name)==checksum,name;hashes[name]=checksum
    for name in ('AGENTS.md','rouge/recognition.py','rouge/visual_recognition.py',
                 'rouge/relic_recognition.py','rouge/run_state.py','rouge/data/relic-mechanics.json'):
        assert digest(name)==previous['source_sha256'][name],name;hashes[name]=digest(name)
    manifest=read('.cache/batch-038-before/manifest.json');assert len(manifest)==12
    baseline=read('.cache/summon-038/baseline.json')
    assert manifest==baseline['source_hashes']
    for name,checksum in manifest.items():assert digest('.cache/batch-038-before/'+name)==checksum,name
    before_app=(ROOT/'.cache/batch-038-before/rouge/app.py').read_text(encoding='utf-8')
    assert (ROOT/'rouge/app.py').read_text(encoding='utf-8')==before_app.replace('0.37','0.38')
    for r in (core,ui,launch,evidence):assert r['chat_requests']==r['game_actions']==0
    for key in ('only_one_project_window','window_visible_and_restored','same_run_preserved',
        'history_preserved','settings_and_bindings_unchanged','run_cmd_startup_verified',
        'within_monitor_work_area','window_raised','previous_app_process_stopped_before_launch'):
        assert launch[key],key
    assert launch['run_state_writes_by_upgrade_script']==0 and launch['launcher_stderr_bytes']==0
    assert len(launch['stability_checks'])==6 and launch['observation_seconds']==20
    assert launch['launcher_sha256']==digest('run.cmd')
    checkpoint=read('.cache/upgrade-0.38-checkpoint.json');run=read('.local/run-state.json')
    assert checkpoint['history_count']==launch['history_count_before']
    assert hashlib.sha256(str(run.get('id')).encode()).hexdigest()==checkpoint['run_id_hash']
    prefix=run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    for name,checksum in checkpoint['config_hashes'].items():assert digest(name)==checksum,name
    live=windows();assert len(live)==1 and live[0]['pid']==launch['process_id']
    assert live[0]['title']=='黑流树海助手 0.38 · 识别与计算测试版'
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    verify_process(live[0]['pid']);focused=foreground(live[0]['hwnd'])
    project=tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))
    assert project['project']['version']=='0.38.0'
    assert 'data/*.json' in project['tool']['setuptools']['package-data']['rouge']
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    names=('SUMMON_0.38_VERIFICATION.json','UI_0.38_VERIFICATION.json','APP_0.38_LAUNCH_VERIFICATION.json',
        'RELIC_VERIFICATION.json','TARGET_ICON_VERIFICATION.json','.cache/research/summon-038/evidence.json',
        evidence['source_snapshot'],core['test_log'],'.cache/summon-038/ui-initial-failure.txt',
        '.cache/batch-038-before/manifest.json','.cache/upgrade-0.38-checkpoint.json',
        'PROJECT_PROGRESS.md','WORK_IN_PROGRESS.md','BATCH_0.38.md','README.md')
    for name in ('scripts/verify_final_038.py','scripts/verify_launch_038.py',
                 'scripts/build_summon_evidence_038.py','pyproject.toml'):hashes[name]=digest(name)
    receipt={'version':'0.38.0','passed':True,'verified_at':time.time(),
        **{k:core[k] for k in ('current_tests_passed','new_tests','historical_combat_tests_skipped',
            'exact_public_output_cases','module_matrix_cases','eligible_module_cases',
            'all_relic_module_damage_invariance_cases')},
        'skills_checked':87,'ui_panel_scenarios':348,'synthetic_module_panels':18,
        'public_entry_cases':8704,'bound_recipient_cases':609,'forbidden_skill_cases':87,'bound_icon_hashes':15,
        'active_relic_rules':135,'scope':scope,'recognition_and_relic_mechanism_data_unchanged':True,
        'source_revision_pinned':False,'deepcolor_module_stages':3,'hp_composition_verified':False,
        'process_id':live[0]['pid'],'test_window_open':True,'window_raised':True,
        'foreground_on_final_check':focused,'run_cmd_startup_verified':True,
        'previous_app_process_stopped_before_launch':True,'same_current_run_and_history_preserved':True,
        'history_count_before':checkpoint['history_count'],'history_count_after':len(run['history']),
        'private_configuration_files_verified':len(checkpoint['config_hashes']),
        'chat_requests':0,'game_actions':0,'new_live_combat_measurements':0,
        'run_state_writes_by_upgrade_script':0,'automation_id':'1-3','automation_status':'DELETED',
        'new_backlog_items':evidence['new_backlog'],'battle_map_download_authorized':True,
        'battle_map_assets_downloaded_this_batch':0,'all_priorities_1_to_3_completed':False,
        'source_sha256':hashes,'evidence_sha256':{name:digest(name) for name in names},
        'limits':core['limits']+['PRTS web reads were saved without pinning a MediaWiki revision.',
            'The module page/UI was tested with synthetic observations, not a new live capture.',
            '10 offline pending and9 data-partial items remain; beneficiary capture layout is unverified.']}
    (ROOT/'FINAL_0.38_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','exact_public_output_cases',
        'module_matrix_cases','ui_panel_scenarios','synthetic_module_panels','test_window_open',
        'process_id','history_count_before','history_count_after','private_configuration_files_verified',
        'all_priorities_1_to_3_completed')}),flush=True)

if __name__=='__main__':main()
