"""Finish recognition-only optimization with current receipts and native launch."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts,partition
from verify_launch_043 import windows,verify_process,foreground


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    core=read('RECOGNITION_0.43_VERIFICATION.json');ui=read('UI_0.43_VERIFICATION.json')
    launch=read('APP_0.43_LAUNCH_VERIFICATION.json');evidence=read('.cache/research/cost-043/evidence.json')
    previous=read('FINAL_0.42_VERIFICATION.json');audit=read('RELIC_VERIFICATION.json')
    assert all(r['version']=='0.43.0' for r in (core,ui,launch,evidence))
    assert core['passed'] and core['current_tests_passed']==403 and core['new_unit_tests']==0
    assert core['tests_run']==473 and core['historical_combat_tests_skipped']==70
    assert core['failures']==core['errors']==0 and core['exact_public_output_cases']==732
    assert core['public_baseline_outputs_unchanged'] and core['paired_visual_cases']==14 and core['public_reader_cases']==5
    assert core['exact_records_scores_centers_preserved'] and core['exact_public_observation_fields_preserved']
    assert core['recognition_identity_thresholds_unchanged'] and core['no_previous_frame_approximate_reuse']
    assert core['current_frame_terms_recomputed'] and core['warm_repeats_per_version']==7
    prep=core['scale_preparation'];assert prep['before']['png_decode_calls']==956 and prep['after']['png_decode_calls']==239
    assert core['raw_art_cache_max_entries']==256 and core['scaled_template_cache_max_entries']==3
    assert digest(core['test_log'])==core['test_log_sha256'] and digest(core['replay'])==core['replay_sha256']
    assert not evidence['numeric_model_changed'] and evidence['remaining_unknown']
    assert ui['passed'] and ui['skills_checked']==87 and ui['panel_scenarios']==348
    assert ui['book_panels']==174 and ui['refill_reference_panels']==9 and ui['book_unknown_panels']==9
    assert ui['book_combination_panels']==9 and ui['book_polling_race_guard_visible']
    assert ui['synthetic_module_panels']==18 and ui['wine_phase_panels']==22
    assert ui['private_data_isolated'] and ui['unrelated_sections_hidden'] and ui['native_options_appropriate']
    assert ui['battle_stages_checked']==105 and ui['battle_enemy_panels_checked']==1087
    assert ui['battle_occurrence_selections']==4764 and ui['battle_resize_clicks']==3
    assert ui['battle_data_readonly'] and ui['battle_sample_received_synthetic_verified'] and ui['battle_variant_sync_bidirectional']
    assert ui['enemy_skill_configuration_panels']==878 and ui['enemy_skill_unknown_only_panels']==209
    assert ui['enemy_skill_stage_override_panels']==115 and ui['enemy_skill_missing_exact_level_panels']==58
    assert ui['enemy_skill_raw_fields_visible'] and ui['enemy_skill_actual_activation_unknown']
    assert digest(ui['refill_screenshot'])==ui['refill_screenshot_sha256']
    assert digest(ui['enemy_skill_screenshot'])==ui['enemy_skill_screenshot_sha256']
    hashes={}
    for receipt in (core,ui):
        for name,sha in receipt['source_hashes'].items():assert digest(name)==sha,name;hashes[name]=sha
    changed=set()
    for name,sha in previous['source_sha256'].items():
        actual=digest(name);hashes[name]=actual
        if actual!=sha:changed.add(name)
    assert changed=={'rouge/app.py','rouge/relic_recognition.py','AGENTS.md','pyproject.toml'}
    assert changed==set(core['changed_existing_source_files'])
    # The old numeric-entry audit was not repeated or relabelled. Its matcher
    # and title hashes changed; those paths have fresh paired/current checks.
    assert audit['version']=='0.41.0' and audit['public_entry_cases']==8704
    assert audit['bound_recipient_cases']==609 and audit['forbidden_skill_cases']==87 and audit['bound_icon_references_verified']==15
    audit_changed={n for n,sha in audit['source_hashes'].items() if digest(n)!=sha}
    assert audit_changed=={'rouge/app.py','rouge/relic_recognition.py'}
    images=read('.cache/research/battle-039/image-receipt.json');assert len(images['images'])==105
    for item in images['images'].values():assert digest('rouge/data/'+item['file'])==item['sha256']
    manifest=read('.cache/batch-043-before/manifest.json');assert len(manifest)==8
    assert manifest==read('.cache/recognition-043/baseline.json')['source_hashes']
    for name,sha in manifest.items():assert digest('.cache/batch-043-before/'+name)==sha,name
    assert len(read('.cache/recognition-043/before-public-results.json'))==732
    remaining=(ROOT/'PROJECT_PROGRESS.md').read_text(encoding='utf-8')
    completed=(ROOT/'PROJECT_COMPLETED.md').read_text(encoding='utf-8')
    old=(ROOT/'.cache/batch-043-before/PROJECT_COMPLETED.md').read_text(encoding='utf-8')
    assert old[old.index('## 0.42'):].strip() in completed
    assert '0.43' in completed and 'PROJECT_COMPLETED.md' in remaining
    for term in ('已接入','已完成','验收：','FINAL_0.','## 上批','## 证据入口'):assert term not in remaining
    checkpoint=read('.cache/upgrade-0.43-checkpoint.json');run=read('.local/run-state.json')
    assert hashlib.sha256(str(run.get('id')).encode()).hexdigest()==checkpoint['run_id_hash']
    assert hashlib.sha256(json.dumps(run['history'][:checkpoint['history_count']],sort_keys=True,
        ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    for name,sha in checkpoint['config_hashes'].items():assert digest(name)==sha,name
    for key in ('only_one_project_window','window_visible_and_restored','window_raised','within_monitor_work_area',
        'same_run_preserved','history_preserved','settings_and_bindings_unchanged',
        'run_cmd_startup_verified','previous_app_process_stopped_before_launch'):assert launch[key],key
    assert launch['observation_seconds']==20 and len(launch['stability_checks'])==6
    assert launch['launcher_stderr_bytes']==launch['run_state_writes_by_upgrade_script']==0
    assert launch['launcher_sha256']==digest('run.cmd')
    for receipt in (core,ui,launch,evidence):assert receipt['game_actions']==receipt['chat_requests']==0
    live=windows();assert len(live)==1 and live[0]['pid']==launch['process_id']
    assert live[0]['title']=='黑流树海助手 0.43 · 识别与计算测试版'
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    verify_process(live[0]['pid']);focused=foreground(live[0]['hwnd'])
    scope=scope_counts(mechanics());assert scope['offline_mechanism_gaps']=={'pending':10,'partial':9}
    assert sum(bool(partition(p,rid)[0]) for rid,p in mechanics()['relics'].items())==135
    assert tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']=='0.43.0'
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    for name in ('scripts/verify_final_043.py','scripts/verify_launch_043.py'):hashes[name]=digest(name)
    receipts=('RECOGNITION_0.43_VERIFICATION.json','UI_0.43_VERIFICATION.json','APP_0.43_LAUNCH_VERIFICATION.json',
        'RELIC_VERIFICATION.json','TARGET_ICON_VERIFICATION.json','.cache/research/cost-043/evidence.json',
        '.cache/research/cost-043/web-source.json','.cache/recognition-043/tests.log',
        '.cache/recognition-043/ui.log','.cache/recognition-043/paired-replay.json',
        '.cache/recognition-043/baseline.json','.cache/batch-043-before/manifest.json',
        '.cache/upgrade-0.43-checkpoint.json','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md',
        'WORK_IN_PROGRESS.md','BATCH_0.43.md','README.md')
    result={'version':'0.43.0','passed':True,'verified_at':time.time(),
        **{k:core[k] for k in ('current_tests_passed','new_unit_tests','historical_combat_tests_skipped',
            'exact_public_output_cases','public_baseline_outputs_unchanged','paired_visual_cases','public_reader_cases',
            'scale_preparation','immutable_raw_art_cache_bytes','projection_template_bytes_at_height_900','benchmarks')},
        'skills_checked':87,'ui_panel_scenarios':348,'book_ui_panels':174,'synthetic_module_panels':18,
        'battle_ui_stages':105,'battle_ui_enemy_panels':1087,'battle_occurrence_selections':4764,'battle_resize_clicks':3,
        'inherited_map_image_hashes_checked':105,'collectible_numeric_entry_audit_inherited_from':'0.41.0',
        'collectible_audit_rerun_this_batch':False,'inherited_audit_changed_sources':sorted(audit_changed),
        'public_entry_cases_inherited':8704,'bound_recipient_cases_inherited':609,'forbidden_skill_cases_inherited':87,
        'scope':scope,'active_relic_rules':135,'completed_items_removed_from_todo':True,
        'historical_completed_records_preserved':True,'process_id':live[0]['pid'],'test_window_open':True,
        'window_raised':True,'foreground_on_final_check':focused,'same_current_run_and_history_preserved':True,
        'history_count_before':checkpoint['history_count'],'history_count_after':len(run['history']),
        'private_configuration_files_verified':len(checkpoint['config_hashes']),'run_state_writes_by_upgrade_script':0,
        'game_actions':0,'chat_requests':0,'new_live_captures':0,'run_cmd_startup_verified':True,
        'automation_status':'DELETED','all_priorities_1_to_3_completed':False,'calculation_core_unchanged':True,
        'identity_thresholds_unchanged':True,'previous_frame_approximate_reuse':False,'cost_numeric_model_changed':False,
        'source_sha256':hashes,'changed_existing_source_files':sorted(changed),
        'evidence_sha256':{n:digest(n) for n in receipts},'limits':core['limits']}
    (ROOT/'FINAL_0.43_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('passed','current_tests_passed','paired_visual_cases',
        'test_window_open','process_id','same_current_run_and_history_preserved','all_priorities_1_to_3_completed')}),flush=True)


if __name__=='__main__':main()
