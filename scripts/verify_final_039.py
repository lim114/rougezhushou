"""Verify preview receipts and the actual current window without resetting state."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts,partition
from verify_launch_039 import windows,foreground,verify_process

def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

def main():
    core=read('BATTLE_0.39_VERIFICATION.json');ui=read('UI_0.39_VERIFICATION.json')
    launch=read('APP_0.39_LAUNCH_VERIFICATION.json');audit=read('RELIC_VERIFICATION.json')
    evidence=read('.cache/research/battle-039/evidence.json');data=read('.cache/research/battle-039/data-receipt.json')
    previous=read('FINAL_0.38_VERIFICATION.json');images=read('.cache/research/battle-039/image-receipt.json')
    assert all(r['version']=='0.39.0' for r in (core,ui,launch,audit,evidence,data))
    assert core['passed'] and core['current_tests_passed']==333 and core['new_tests']==24
    assert core['tests_run']==403 and core['historical_combat_tests_skipped']==70
    assert core['failures']==core['errors']==0 and core['exact_public_output_cases']==732
    assert core['calculation_outputs_unchanged'] and core['source_actions_and_geometry_exactly_preserved']
    assert core['stages']==core['images']==105 and core['main_spawn_rows']==core['main_spawns_mapped']==3639
    assert core['conditional_branch_rows']==core['branch_spawns_unmapped']==299
    assert core['enemy_references']==1087 and core['enemy_environment_scenarios']==2174
    assert digest(core['test_log'])==core['test_log_sha256']
    for name,sha in core['baseline_hashes'].items():assert digest(name)==sha,name
    assert evidence['game_and_image_commits_pinned'] and evidence['download_authorized']
    assert evidence['assets_downloaded']==105 and evidence['remaining_specific_unknowns']
    assert evidence['recognition_change'].startswith('none') and evidence['calculation_core_change']=='none'
    assert evidence['relic_mechanism_change']=='none' and not evidence['all_priorities_1_to_3_completed']
    assert data['source']==read('rouge/data/battle-previews.json')['source']
    assert digest('rouge/data/battle-previews.json')==data['data_sha256']
    assert evidence['game_commit']==data['source']['game_commit']
    assert evidence['resource_commit']==data['source']['resource_commit']==images['resource_commit']
    assert digest('.cache/research/battle-039/enemy_handbook_table.json')==data['source']['handbook']['sha256']
    assert len(images['images'])==105 and sum(i['bytes'] for i in images['images'].values())==34951925
    for image in images['images'].values():assert digest('rouge/data/'+image['file'])==image['sha256']
    assert ui['passed'] and ui['skills_checked']==87 and ui['panel_scenarios']==348
    assert ui['synthetic_module_panels']==18 and ui['battle_stages_checked']==105
    assert ui['battle_enemy_panels_checked']==1087 and ui['battle_resize_clicks']==3
    assert ui['battle_main_spawn_rows']==3639 and ui['battle_branch_rows']==299
    assert all(ui[key] for key in ('private_data_isolated','native_options_appropriate','event_input_absent',
        'battle_data_readonly','battle_context_correction_verified','battle_unchanged_context_render_reused',
        'battle_sample_received_synthetic_verified','battle_variant_sync_bidirectional','battle_empty_unknown_variant_cleared'))
    assert (ROOT/ui['battle_screenshot']).exists()
    scope=scope_counts(mechanics())
    assert scope==core['offline_scope']==audit['offline_scope']==previous['scope']
    assert mechanics()['counts']==core['data_rule_counts']==audit['data_rule_counts']
    assert sum(bool(partition(p,rid)[0]) for rid,p in mechanics()['relics'].items())==135
    assert scope['offline_mechanism_gaps']=={'pending':10,'partial':9}
    assert audit['public_entry_cases']==8704 and audit['bound_recipient_cases']==609 and audit['forbidden_skill_cases']==87
    icons=read('TARGET_ICON_VERIFICATION.json');assert len(icons['icons'])==15
    for icon in icons['icons']:assert digest('rouge/data/'+icon['file'])==icon['sha256']
    hashes={}
    for receipt in (core,ui,audit):
        for name,sha in receipt['source_hashes'].items():assert digest(name)==sha,name;hashes[name]=sha
    for name,sha in previous['source_sha256'].items():
        if name.startswith('rouge/') and name!='rouge/app.py':assert digest(name)==sha,name;hashes[name]=sha
    manifest=read('.cache/batch-039-before/manifest.json');assert len(manifest)==8
    assert manifest==read('.cache/battle-039/baseline.json')['source_hashes']
    for name,sha in manifest.items():assert digest('.cache/batch-039-before/'+name)==sha,name
    checkpoint=read('.cache/upgrade-0.39-checkpoint.json');run=read('.local/run-state.json')
    assert hashlib.sha256(str(run.get('id')).encode()).hexdigest()==checkpoint['run_id_hash']
    assert hashlib.sha256(json.dumps(run['history'][:checkpoint['history_count']],sort_keys=True,
        ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    for name,sha in checkpoint['config_hashes'].items():assert digest(name)==sha,name
    for key in ('only_one_project_window','window_visible_and_restored','window_raised','within_monitor_work_area',
        'same_run_preserved','history_preserved','settings_and_bindings_unchanged',
        'run_cmd_startup_verified','previous_app_process_stopped_before_launch'):assert launch[key],key
    assert len(launch['stability_checks'])==6 and launch['observation_seconds']==20
    assert launch['launcher_stderr_bytes']==launch['run_state_writes_by_upgrade_script']==0
    assert launch['launcher_sha256']==digest('run.cmd')
    for receipt in (core,ui,evidence,launch):assert receipt['chat_requests']==receipt['game_actions']==0
    live=windows();assert len(live)==1 and live[0]['pid']==launch['process_id']
    assert live[0]['title']=='黑流树海助手 0.39 · 识别与计算测试版'
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    verify_process(live[0]['pid']);focused=foreground(live[0]['hwnd'])
    project=tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))
    assert project['project']['version']=='0.39.0'
    assert 'data/battle-maps/*.png' in project['tool']['setuptools']['package-data']['rouge']
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    for name in ('scripts/verify_final_039.py','scripts/verify_launch_039.py','AGENTS.md','pyproject.toml'):
        hashes[name]=digest(name)
    receipts=('BATTLE_0.39_VERIFICATION.json','UI_0.39_VERIFICATION.json','APP_0.39_LAUNCH_VERIFICATION.json',
        'RELIC_VERIFICATION.json','TARGET_ICON_VERIFICATION.json','.cache/research/battle-039/evidence.json',
        '.cache/research/battle-039/data-receipt.json','.cache/research/battle-039/image-receipt.json',
        '.cache/research/battle-039/web-source.json','.cache/battle-039/tests.log',
        '.cache/battle-039/initial-test-failure.txt','.cache/batch-039-before/manifest.json',
        '.cache/upgrade-0.39-checkpoint.json','PROJECT_PROGRESS.md','WORK_IN_PROGRESS.md','BATCH_0.39.md','README.md')
    result={'version':'0.39.0','passed':True,'verified_at':time.time(),
        **{k:core[k] for k in ('current_tests_passed','new_tests','historical_combat_tests_skipped',
            'exact_public_output_cases','calculation_outputs_unchanged','stages','images','main_spawns_mapped',
            'branch_spawns_unmapped','enemy_references','enemy_environment_scenarios')},
        'skills_checked':87,'ui_panel_scenarios':348,'synthetic_module_panels':18,
        'battle_ui_stages':105,'battle_ui_enemy_panels':1087,'battle_resize_clicks':3,
        'public_entry_cases':8704,'bound_recipient_cases':609,'forbidden_skill_cases':87,'bound_icon_hashes':15,
        'scope':scope,'active_relic_rules':135,'process_id':live[0]['pid'],'test_window_open':True,
        'window_raised':True,'foreground_on_final_check':focused,'run_cmd_startup_verified':True,
        'same_current_run_and_history_preserved':True,'history_count_before':checkpoint['history_count'],
        'history_count_after':len(run['history']),'private_configuration_files_verified':len(checkpoint['config_hashes']),
        'game_actions':0,'chat_requests':0,'new_live_combat_measurements':0,'run_state_writes_by_upgrade_script':0,
        'automation_id':'1-3','automation_status':'DELETED','all_priorities_1_to_3_completed':False,
        'recognition_and_calculation_core_unchanged':True,'absolute_spawn_time_verified':False,
        'branch_route_scope_verified':False,'original_image_projection_verified':False,
        'source_sha256':hashes,'evidence_sha256':{name:digest(name) for name in receipts},
        'limits':core['limits']+['Node auto-sync is synthetic-wiring tested, not a new live recognition sample.',
            'Expanded enemy fields are base references, not complete script/relic-adjusted values.',
            'P1-P3 remain incomplete; no new inventory accuracy or recognition speed claim.']}
    (ROOT/'FINAL_0.39_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('passed','current_tests_passed','stages','main_spawns_mapped',
        'test_window_open','process_id','same_current_run_and_history_preserved','all_priorities_1_to_3_completed')}),flush=True)

if __name__=='__main__':main()
