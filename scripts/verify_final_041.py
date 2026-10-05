"""Validate this batch's receipts, preserved state and actual current window."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts,partition
from verify_launch_041 import windows,foreground,verify_process


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    core=read('AMMO_0.41_VERIFICATION.json');ui=read('UI_0.41_VERIFICATION.json')
    launch=read('APP_0.41_LAUNCH_VERIFICATION.json');audit=read('RELIC_VERIFICATION.json')
    evidence=read('.cache/research/ammo-041/evidence.json');previous=read('FINAL_0.40_VERIFICATION.json')
    assert all(r['version']=='0.41.0' for r in (core,ui,launch,audit,evidence))
    assert core['passed'] and core['current_tests_passed']==383 and core['new_tests']==24
    assert core['tests_run']==453 and core['historical_combat_tests_skipped']==70
    assert core['failures']==core['errors']==0 and core['exact_public_output_cases']==732
    assert core['public_baseline_outputs_unchanged'] and core['book_cases']==1008
    assert core['book_comparison']=={'exact_same':468,'non_ammo_unchanged':468,'changed':540,
        'ammo_scenarios':540,'known_ammo_reference':180,'positive_refill':140,
        'unknown_skill_reference':360,'known_no_effect':40}
    assert core['source_files_sha256_and_git_blob_verified'] and core['raw_relic_data_unchanged']
    assert core['battle_source_and_ui_unchanged']
    assert digest(core['test_log'])==core['test_log_sha256']
    for name,sha in core['baseline_hashes'].items():assert digest(name)==sha,name
    assert ui['passed'] and ui['skills_checked']==87 and ui['panel_scenarios']==348
    assert ui['book_panels']==174 and ui['refill_reference_panels']==9 and ui['book_unknown_panels']==9
    assert ui['book_combination_panels']==9 and ui['book_polling_race_guard_visible']
    assert ui['synthetic_module_panels']==18 and ui['wine_phase_panels']==22
    assert ui['private_data_isolated'] and ui['unrelated_sections_hidden'] and ui['native_options_appropriate']
    assert digest(ui['refill_screenshot'])==ui['refill_screenshot_sha256']
    assert ui['battle_stages_checked']==105 and ui['battle_enemy_panels_checked']==1087
    assert ui['battle_occurrence_selections']==4764 and ui['battle_resize_clicks']==3
    assert ui['battle_sample_received_synthetic_verified'] and ui['battle_variant_sync_bidirectional']
    assert ui['battle_unchanged_context_render_reused'] and ui['battle_data_readonly']
    assert audit['audit_count']==272 and audit['public_entry_cases']==8704
    assert audit['bound_recipient_cases']==609 and audit['forbidden_skill_cases']==87
    assert audit['bound_icon_references_verified']==15 and read('TARGET_ICON_VERIFICATION.json')['count']==15
    scope=scope_counts(mechanics());assert scope['offline_mechanism_gaps']=={'pending':10,'partial':9}
    assert sum(bool(partition(p,rid)[0]) for rid,p in mechanics()['relics'].items())==135
    hashes={}
    for receipt in (core,ui,audit):
        for name,sha in receipt['source_hashes'].items():assert digest(name)==sha,name;hashes[name]=sha
    allowed={'rouge/app.py','rouge/relics.py','rouge/relic_events.py','rouge/damage.py',
        'rouge/operator_engine.py','rouge/reporting.py','tests/test_relic_extension.py','pyproject.toml'}
    changed=set()
    for name,sha in previous['source_sha256'].items():
        actual=digest(name)
        if actual!=sha:changed.add(name)
        hashes[name]=actual
    assert changed==allowed,changed
    images=read('.cache/research/battle-039/image-receipt.json')
    assert len(images['images'])==105 and sum(i['bytes'] for i in images['images'].values())==34951925
    for item in images['images'].values():assert digest('rouge/data/'+item['file'])==item['sha256']
    source=read('.cache/research/ammo-041/source-receipt.json')
    assert source['commit']==evidence['timer_commit']==read('rouge/data/ammo-refill-reference.json')['source_commit']
    for name,row in source['files'].items():
        assert digest('.cache/research/ammo-041/'+name)==row['sha256'],name
    assert not read('rouge/data/ammo-refill-reference.json')['client_frame_calibration_verified']
    assert evidence['reference_bound']['measured_client_period'] is False
    assert evidence['web_sources'][0]['pinned_revision_fetch_succeeded'] is False
    assert evidence['remaining_unknown']
    manifest=read('.cache/batch-041-before/manifest.json');assert len(manifest)==15
    assert manifest==read('.cache/ammo-041/baseline.json')['source_hashes']
    for name,sha in manifest.items():assert digest('.cache/batch-041-before/'+name)==sha,name
    checkpoint=read('.cache/upgrade-0.41-checkpoint.json');run=read('.local/run-state.json')
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
    assert live[0]['title']=='黑流树海助手 0.41 · 识别与计算测试版'
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    verify_process(live[0]['pid']);focused=foreground(live[0]['hwnd'])
    project=tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))
    assert project['project']['version']=='0.41.0'
    assert 'data/*.json' in project['tool']['setuptools']['package-data']['rouge']
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    for name in ('scripts/verify_final_041.py','scripts/verify_launch_041.py','AGENTS.md','pyproject.toml'):
        hashes[name]=digest(name)
    receipts=('AMMO_0.41_VERIFICATION.json','UI_0.41_VERIFICATION.json','APP_0.41_LAUNCH_VERIFICATION.json',
        'RELIC_VERIFICATION.json','TARGET_ICON_VERIFICATION.json','.cache/research/ammo-041/evidence.json',
        '.cache/research/ammo-041/source-receipt.json','.cache/research/ammo-041/ammo-template-excerpt.json',
        '.cache/research/ammo-041/relic041_fixed_point.json','.cache/research/ammo-041/relic041_pinned_fixed_point.json',
        '.cache/ammo-041/tests.log','.cache/ammo-041/ui.log','.cache/ammo-041/mechanics.log',
        '.cache/ammo-041/targeted-initial.log','.cache/ammo-041/ui-initial-failure.log',
        '.cache/batch-041-before/manifest.json','.cache/upgrade-0.41-checkpoint.json',
        'PROJECT_PROGRESS.md','WORK_IN_PROGRESS.md','BATCH_0.41.md','README.md','RELIC_COVERAGE.md')
    result={'version':'0.41.0','passed':True,'verified_at':time.time(),
        **{k:core[k] for k in ('current_tests_passed','new_tests','historical_combat_tests_skipped',
            'exact_public_output_cases','public_baseline_outputs_unchanged','book_cases','book_comparison')},
        'skills_checked':87,'ui_panel_scenarios':348,'book_ui_panels':174,'synthetic_module_panels':18,
        'book_unknown_guard_verified':True,'zero_ammo_not_revived':True,'sourced_fixed_point_rounding':True,
        'inherited_battle_data_and_helpers_unchanged':True,'battle_ui_stages':105,'battle_ui_enemy_panels':1087,
        'battle_occurrence_selections':ui['battle_occurrence_selections'],'battle_resize_clicks':3,
        'inherited_map_image_hashes_checked':105,'public_entry_cases':8704,'bound_recipient_cases':609,
        'forbidden_skill_cases':87,'bound_icon_hashes':15,'scope':scope,'active_relic_rules':135,
        'process_id':live[0]['pid'],'test_window_open':True,'window_raised':True,'foreground_on_final_check':focused,
        'run_cmd_startup_verified':True,'same_current_run_and_history_preserved':True,
        'history_count_before':checkpoint['history_count'],'history_count_after':len(run['history']),
        'private_configuration_files_verified':len(checkpoint['config_hashes']),
        'game_actions':0,'chat_requests':0,'new_live_combat_measurements':0,'run_state_writes_by_upgrade_script':0,
        'automation_id':'1-3','automation_status':'DELETED','all_priorities_1_to_3_completed':False,
        'recognition_and_run_state_core_unchanged':True,'ammo_poll_phase_calibrated':False,
        'foreign_runtime_executed':False,'source_sha256':hashes,
        'changed_existing_source_files':sorted(changed),'evidence_sha256':{n:digest(n) for n in receipts},
        'limits':core['limits']+['GUI environment/module observations are synthetic, not new live recognition.',
            'Ordinary ammo references do not resolve full timing templates or all collectible combinations.']}
    (ROOT/'FINAL_0.41_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('passed','current_tests_passed','book_cases',
        'test_window_open','process_id','same_current_run_and_history_preserved','all_priorities_1_to_3_completed')}),flush=True)


if __name__=='__main__':main()
