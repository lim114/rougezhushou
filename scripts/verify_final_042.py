"""Current receipts, separated remaining work and actual visible test window."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts,partition
from verify_launch_042 import windows,foreground,verify_process


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    core=read('PREVIEW_0.42_VERIFICATION.json');ui=read('UI_0.42_VERIFICATION.json')
    launch=read('APP_0.42_LAUNCH_VERIFICATION.json');audit=read('RELIC_VERIFICATION.json')
    screenshot=read('PREVIEW_SCREENSHOT_0.42_VERIFICATION.json')
    therapy=read('.cache/research/therapy-042/evidence.json')
    build=read('.cache/research/enemy-skills-042/data-receipt.json')
    previous=read('FINAL_0.41_VERIFICATION.json')
    assert all(r['version']=='0.42.0' for r in (core,ui,launch,therapy,build,screenshot))
    assert screenshot['passed'] and screenshot['synthetic_gui_only'] and screenshot['cooldown_parameter_on_screen']
    assert digest(screenshot['screenshot'])==screenshot['screenshot_sha256']
    assert core['passed'] and core['current_tests_passed']==403 and core['new_tests']==20
    assert core['tests_run']==473 and core['historical_combat_tests_skipped']==70
    assert core['failures']==core['errors']==0 and core['exact_public_output_cases']==732
    assert core['public_baseline_outputs_unchanged'] and core['all_source_fields_exact']
    assert core['source_files_sha256_and_git_blob_verified'] and core['preserved_old_source_hashes_checked']
    assert (core['raw_level_definitions'],core['raw_skill_entries'],core['raw_sp_definitions'],
        core['raw_stage_overrides'],core['enemy_references'])==(333,169,21,115,1087)
    assert not core['skill_inheritance_inferred'] and not core['actual_skill_activation_times_verified']
    assert digest(core['test_log'])==core['test_log_sha256']
    for name,sha in core['baseline_hashes'].items():assert digest(name)==sha,name
    assert ui['passed'] and ui['skills_checked']==87 and ui['panel_scenarios']==348
    assert ui['book_panels']==174 and ui['refill_reference_panels']==9 and ui['book_unknown_panels']==9
    assert ui['book_combination_panels']==9 and ui['book_polling_race_guard_visible']
    assert ui['synthetic_module_panels']==18 and ui['wine_phase_panels']==22
    assert ui['private_data_isolated'] and ui['unrelated_sections_hidden'] and ui['native_options_appropriate']
    assert digest(ui['refill_screenshot'])==ui['refill_screenshot_sha256']
    assert digest(ui['enemy_skill_screenshot'])==ui['enemy_skill_screenshot_sha256']
    assert ui['battle_stages_checked']==105 and ui['battle_enemy_panels_checked']==1087
    assert ui['battle_occurrence_selections']==4764 and ui['battle_resize_clicks']==3
    assert ui['battle_sample_received_synthetic_verified'] and ui['battle_variant_sync_bidirectional']
    assert ui['battle_unchanged_context_render_reused'] and ui['battle_data_readonly']
    assert ui['enemy_skill_configuration_panels']+ui['enemy_skill_unknown_only_panels']==1087
    assert ui['enemy_skill_stage_override_panels']==115
    assert ui['enemy_skill_missing_exact_level_panels']==core['exact_requested_definition_missing']
    for key in ('enemy_skill_raw_fields_visible','enemy_skill_no_effective_inheritance_claim',
        'enemy_skill_actual_activation_unknown'):assert ui[key],key
    # The collectible audit is inherited, not relabelled as a fresh 0.42 run.
    assert audit['version']=='0.41.0' and audit['audit_count']==272 and audit['public_entry_cases']==8704
    assert audit['bound_recipient_cases']==609 and audit['forbidden_skill_cases']==87
    assert audit['bound_icon_references_verified']==15 and read('TARGET_ICON_VERIFICATION.json')['count']==15
    scope=scope_counts(mechanics());assert scope['offline_mechanism_gaps']=={'pending':10,'partial':9}
    assert sum(bool(partition(p,rid)[0]) for rid,p in mechanics()['relics'].items())==135
    hashes={}
    for receipt in (core,ui,screenshot):
        for name,sha in receipt['source_hashes'].items():assert digest(name)==sha,name;hashes[name]=sha
    for name,sha in audit['source_hashes'].items():
        if name!='rouge/app.py':assert digest(name)==sha,name
        hashes[name]=digest(name)
    changed=set()
    for name,sha in previous['source_sha256'].items():
        actual=digest(name)
        if actual!=sha:changed.add(name)
        hashes[name]=actual
    allowed={'rouge/app.py','rouge/battle_preview.py','pyproject.toml'}
    assert changed==allowed and changed==set(core['changed_existing_source_files']),changed
    images=read('.cache/research/battle-039/image-receipt.json')
    assert len(images['images'])==105 and sum(i['bytes'] for i in images['images'].values())==34951925
    for item in images['images'].values():assert digest('rouge/data/'+item['file'])==item['sha256']
    assert digest('rouge/data/enemy-skill-references.json')==build['data_sha256']
    assert build['source_all_fields_exact'] and build['skill_lists_not_merged']
    assert not build['actual_activation_times_verified']
    assert therapy['descriptions_verified'] and not therapy['numeric_effect_integrated']
    assert therapy['remaining_unknown'] and therapy['correction']
    assert not therapy['foreign_runtime_executed']
    manifest=read('.cache/batch-042-before/manifest.json');assert len(manifest)==8
    assert manifest==read('.cache/preview-042/baseline.json')['source_hashes']
    for name,sha in manifest.items():assert digest('.cache/batch-042-before/'+name)==sha,name
    remaining=(ROOT/'PROJECT_PROGRESS.md').read_text(encoding='utf-8')
    completed=(ROOT/'PROJECT_COMPLETED.md').read_text(encoding='utf-8')
    old=(ROOT/'.cache/batch-042-before/PROJECT_PROGRESS.md').read_text(encoding='utf-8')
    assert old[old.index('更新：'):old.index('## 未完成事项与建议顺序')].strip() in completed
    assert '0.42' in completed and 'PROJECT_COMPLETED.md' in remaining
    for term in ('已接入','已完成','验收：','FINAL_0.','## 上批','## 证据入口'):assert term not in remaining,term
    checkpoint=read('.cache/upgrade-0.42-checkpoint.json');run=read('.local/run-state.json')
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
    for receipt in (core,ui,therapy,launch,screenshot):assert receipt['chat_requests']==receipt['game_actions']==0
    live=windows();assert len(live)==1 and live[0]['pid']==launch['process_id']
    assert live[0]['title']=='黑流树海助手 0.42 · 识别与计算测试版'
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    verify_process(live[0]['pid']);focused=foreground(live[0]['hwnd'])
    project=tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))
    assert project['project']['version']=='0.42.0'
    assert 'data/*.json' in project['tool']['setuptools']['package-data']['rouge']
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    for name in ('scripts/verify_final_042.py','scripts/verify_launch_042.py','scripts/research_therapy_042.py',
        'scripts/reconcile_progress_042.py','scripts/capture_preview_baseline_042.py','AGENTS.md','pyproject.toml'):
        hashes[name]=digest(name)
    receipts=('PREVIEW_0.42_VERIFICATION.json','UI_0.42_VERIFICATION.json','APP_0.42_LAUNCH_VERIFICATION.json',
        'PREVIEW_SCREENSHOT_0.42_VERIFICATION.json',
        'RELIC_VERIFICATION.json','TARGET_ICON_VERIFICATION.json','.cache/research/therapy-042/evidence.json',
        '.cache/research/therapy-042/source-receipt.json','.cache/research/therapy-042/template-excerpt.json',
        '.cache/research/therapy-042/web-source.json','.cache/research/therapy-042/data-raw-inventory.json',
        '.cache/research/enemy-skills-042/data-receipt.json',
        '.cache/preview-042/tests.log','.cache/preview-042/ui.log','.cache/preview-042/targeted.log',
        '.cache/preview-042/screenshot.log',
        '.cache/batch-042-before/manifest.json','.cache/upgrade-0.42-checkpoint.json',
        'PROJECT_PROGRESS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','BATCH_0.42.md','README.md')
    result={'version':'0.42.0','passed':True,'verified_at':time.time(),
        **{k:core[k] for k in ('current_tests_passed','new_tests','historical_combat_tests_skipped',
            'exact_public_output_cases','public_baseline_outputs_unchanged','raw_level_definitions',
            'raw_skill_entries','raw_sp_definitions','raw_stage_overrides')},
        'skills_checked':87,'ui_panel_scenarios':348,'book_ui_panels':174,'synthetic_module_panels':18,
        'battle_ui_stages':105,'battle_ui_enemy_panels':1087,
        'enemy_skill_configuration_panels':ui['enemy_skill_configuration_panels'],
        'battle_occurrence_selections':ui['battle_occurrence_selections'],'battle_resize_clicks':3,
        'inherited_map_image_hashes_checked':105,
        'collectible_audit_inherited_from':'RELIC_VERIFICATION.json (0.41.0)',
        'collectible_audit_rerun_this_batch':False,'inherited_collectible_source_hashes_verified':True,
        'public_entry_cases_inherited':8704,'bound_recipient_cases_inherited':609,
        'forbidden_skill_cases_inherited':87,'bound_icon_hashes_inherited':15,
        'scope':scope,'active_relic_rules':135,'completed_items_removed_from_todo':True,
        'historical_completed_records_preserved':True,'process_id':live[0]['pid'],'test_window_open':True,
        'window_raised':True,'foreground_on_final_check':focused,'run_cmd_startup_verified':True,
        'same_current_run_and_history_preserved':True,'history_count_before':checkpoint['history_count'],
        'history_count_after':len(run['history']),'private_configuration_files_verified':len(checkpoint['config_hashes']),
        'game_actions':0,'chat_requests':0,'new_live_combat_measurements':0,'run_state_writes_by_upgrade_script':0,
        'automation_id':'1-3','automation_status':'DELETED','all_priorities_1_to_3_completed':False,
        'recognition_and_run_state_core_unchanged':True,'calculation_core_unchanged':True,
        'enemy_skill_inheritance_verified':False,'enemy_skill_actual_activation_times_verified':False,
        'therapy_numeric_effect_integrated':False,'foreign_runtime_executed':False,'source_sha256':hashes,
        'changed_existing_source_files':sorted(changed),'evidence_sha256':{n:digest(n) for n in receipts},
        'limits':core['limits']+['GUI cultivation/environment observations are synthetic, not new live recognition.',
            'Configured enemy cooldown/SP parameters do not establish full hidden scripts or effective damage.']}
    (ROOT/'FINAL_0.42_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('passed','current_tests_passed','raw_level_definitions',
        'test_window_open','process_id','same_current_run_and_history_preserved','completed_items_removed_from_todo',
        'all_priorities_1_to_3_completed')}),flush=True)


if __name__=='__main__':main()
