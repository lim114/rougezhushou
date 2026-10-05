"""Finalize the limited fixed-map batch without restoring real user state."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_launch_044 import windows,verify_process,foreground,state
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts,partition


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def text(name):return (ROOT/name).read_text(encoding='utf-8')


def main():
    core=read('PROJECTION_0.44_VERIFICATION.json');ui=read('UI_0.44_VERIFICATION.json')
    launch=read('APP_0.44_LAUNCH_VERIFICATION.json');evidence=read('.cache/research/map-projection-044/evidence.json')
    previous=read('FINAL_0.43_VERIFICATION.json');checkpoint=read('.cache/upgrade-0.44-checkpoint.json')
    assert all(r['version']=='0.44.0' for r in (core,ui,launch,evidence))
    assert core['passed'] and core['current_tests_passed']==421 and core['new_unit_tests']==18
    assert core['tests_run']==491 and core['historical_combat_tests_skipped']==70
    assert core['errors']==core['failures']==0 and digest(core['test_log'])==core['test_log_sha256']
    assert core['calibrated_original_bitmaps']==3 and len(core['bound_stages'])==6 and core['uncalibrated_stage_count']==99
    assert len(core['independent_bitmap_landmarks'])==15 and core['max_independent_error_px']<=4
    assert core['tolerance_is_not_whole_map_precision_proof'] and core['rejected_calibrations']==['ro6_n_1_3']
    assert core['calibrated_spawn_rows']==126 and core['calibrated_route_point_references']==1048
    assert core['tile_center_inverse_checks']==400 and core['source_images_checked']==105
    assert core['source_image_bytes']==34951925 and core['source_receipts_git_blob_verified']
    assert not core['actual_pathfinding_claimed'] and not core['actual_absolute_spawn_timeline_claimed']
    assert core['no_live_battle_capture_required'] and not core['runtime_external_camera_code_imported']
    assert core['inherited_numeric_public_cases']==732 and not core['numeric_public_replay_rerun']
    assert ui['passed'] and ui['private_data_isolated'] and ui['battle_data_readonly']
    assert ui['battle_stages_checked']==105 and ui['battle_enemy_panels_checked']==1087
    assert ui['battle_occurrence_selections']==4764 and ui['battle_resize_clicks']==3
    assert ui['calibrated_stage_clicks']==18 and ui['projected_row_selection_checks']==138
    assert ui['letterbox_sizes_checked']==4 and ui['run_state_unchanged']
    for key in ('original_and_grid_selection_synced','occurrence_synced_on_original',
            'non_spawn_selection_clears_both_maps','letterbox_clicks_rejected','same_size_wrong_bitmap_rejected',
            'missing_bitmap_rejected','uncalibrated_map_has_no_markers_or_click_mapping',
            'broken_route_continuous_line_not_drawn','continuous_checkpoint_reference_drawn','unknown_stage_cleared'):
        assert ui[key],key
    for key in ('battle_screenshot','enemy_skill_screenshot','fixed_map_screenshot','fixed_map_detail_screenshot'):
        assert digest(ui[key])==ui[key+'_sha256']
    hashes={}
    for receipt in (core,ui):
        for name,sha in receipt['source_hashes'].items():assert digest(name)==sha,name;hashes[name]=sha
    changed=set()
    for name,sha in previous['source_sha256'].items():
        actual=digest(name);hashes[name]=actual
        if actual!=sha:changed.add(name)
    assert changed=={'rouge/app.py','rouge/battle_view.py','pyproject.toml'},changed
    assert changed==set(core['changed_existing_source_files'])
    backup='.cache/batch-044-before/'
    assert text('rouge/app.py').replace('0.44','0.43')==text(backup+'rouge/app.py')
    assert text('pyproject.toml').replace('0.44','0.43')==text(backup+'pyproject.toml')
    progress=text('PROJECT_PROGRESS.md');completed=text('PROJECT_COMPLETED.md')
    for token in ('已接入','已完成','验收：','FINAL_0.','## 上批','## 证据入口'):assert token not in progress,token
    assert '99个关卡、68张独立原图' in progress and '急不可耐' in progress
    assert '猎犬病原' not in progress and '灌水贤者' not in progress
    for line in text(backup+'PROJECT_PROGRESS.md').splitlines():
        if '固定战斗地图映射' not in line and '分支位置与路线' not in line:assert line in progress,line
    assert completed.count('## 0.44 · 六个关卡的固定原图映射')==1
    assert completed.split('## 0.43 ·',1)[1]==text(backup+'PROJECT_COMPLETED.md').split('## 0.43 ·',1)[1]
    assert text('WORK_IN_PROGRESS.md').endswith(text(backup+'WORK_IN_PROGRESS.md').replace(
        '# 0.43交接：识别参考复用与固定战斗预览范围','# 历史0.43交接：识别参考复用与固定战斗预览范围',1))
    assert text('README.md').split('项目持续规则',1)[1]==text(backup+'README.md').split('项目持续规则',1)[1]
    assert '# 黑流树海助手 · 0.44' in text('README.md')
    assert tomllib.loads(text('pyproject.toml'))['project']['version']=='0.44.0'
    assert launch['run_cmd_startup_verified'] and launch['previous_app_process_stopped_before_launch']
    assert launch['only_one_project_window'] and launch['window_visible_and_restored'] and launch['window_raised']
    assert launch['same_run_preserved'] and launch['history_preserved'] and launch['settings_and_bindings_unchanged']
    assert len(launch['stability_checks'])==6 and launch['observation_seconds']==20 and launch['launcher_stderr_bytes']==0
    assert launch['launcher_sha256']==digest('run.cmd')
    after=state();run=read('.local/run-state.json')
    prefix=run['history'][:checkpoint['history_count']]
    assert checkpoint['run_id_hash']==after['run_id_hash']
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    assert checkpoint['config_hashes']==after['config_hashes']
    for receipt in (core,ui,launch,evidence):assert receipt['game_actions']==receipt['chat_requests']==0
    assert evidence['external_code_executed'] is False and evidence['numeric_model_changed'] is False
    live=windows();assert len(live)==1 and live[0]['pid']==launch['process_id']
    assert live[0]['title']=='黑流树海助手 0.44 · 识别与计算测试版'
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    verify_process(live[0]['pid']);focused=foreground(live[0]['hwnd'])
    scope=scope_counts(mechanics());assert scope['offline_mechanism_gaps']=={'pending':10,'partial':9}
    assert sum(bool(partition(p,rid)[0]) for rid,p in mechanics()['relics'].items())==135
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not (Path.home()/'.codex/automations/1-3/automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    for name in ('scripts/verify_final_044.py','scripts/verify_launch_044.py'):hashes[name]=digest(name)
    artifacts=['PROJECTION_0.44_VERIFICATION.json','UI_0.44_VERIFICATION.json','APP_0.44_LAUNCH_VERIFICATION.json',
        'RELIC_VERIFICATION.json','RECOGNITION_0.43_VERIFICATION.json','UI_0.43_VERIFICATION.json',
        '.cache/research/map-projection-044/evidence.json','.cache/research/map-projection-044/web-source.json',
        '.cache/research/map-projection-044/source-receipts.json','.cache/research/map-projection-044/calibration-input.json',
        '.cache/projection-044/tests.log','.cache/projection-044/build.log','.cache/projection-044/build-recheck.log',
        '.cache/projection-044/ui.log','.cache/batch-044-before/manifest.json','.cache/upgrade-0.44-checkpoint.json',
        'PROJECT_PROGRESS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','BATCH_0.44.md','README.md']
    result={'version':'0.44.0','passed':True,'verified_at':time.time(),'current_tests_passed':421,
        'new_unit_tests':18,'historical_combat_tests_skipped':70,
        'calibrated_original_bitmaps':3,'bound_stages':core['bound_stages'],'uncalibrated_stages':99,
        'uncalibrated_bitmap_identities':68,'independent_landmarks':15,'max_independent_error_px':core['max_independent_error_px'],
        'source_pixel_check_tolerance':4,'rejected_calibrations':core['rejected_calibrations'],
        'calibrated_spawn_rows':126,'calibrated_route_point_references':1048,'tile_center_inverse_checks':400,
        'battle_ui_stages':105,'battle_ui_enemy_panels':1087,'battle_occurrence_selections':4764,
        'calibrated_original_clicks':18,'original_letterbox_sizes':4,'inherited_map_image_hashes_checked':105,
        'source_sha256':hashes,'changed_existing_source_files':sorted(changed),
        'evidence_sha256':{n:digest(n) for n in artifacts},'scope':scope,'active_relic_rules':135,
        'numeric_public_cases_inherited_from':'RECOGNITION_0.43_VERIFICATION.json','inherited_numeric_cases':732,
        'numeric_public_replay_rerun':False,'collectible_audit_inherited_from':'0.41.0','collectible_audit_rerun':False,
        'damage_skill_ui_coverage_inherited_from':'UI_0.43_VERIFICATION.json','skill_ui_rerun':False,
        'calculation_and_recognition_core_unchanged':True,'new_recognition_speed_claim':False,
        'completed_scope_removed_from_todo':True,'historical_completed_records_preserved':True,
        'same_current_run_and_history_preserved':True,'history_count_before':checkpoint['history_count'],
        'history_count_after':len(run['history']),'private_configuration_files_verified':len(after['config_hashes']),
        'process_id':live[0]['pid'],'test_window_open':True,'window_raised':True,'foreground_on_final_check':focused,
        'run_cmd_startup_verified':True,'run_state_writes_by_upgrade_script':0,'new_live_battle_captures':0,
        'game_actions':0,'chat_requests':0,'automation_status':'DELETED','all_priorities_1_to_3_completed':False,
        'limits':evidence['remaining_unknown']}
    (ROOT/'FINAL_0.44_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('passed','current_tests_passed','calibrated_original_bitmaps',
        'bound_stages','uncalibrated_stages','test_window_open','process_id','same_current_run_and_history_preserved',
        'history_count_before','history_count_after','all_priorities_1_to_3_completed')},ensure_ascii=False))


if __name__=='__main__':main()
