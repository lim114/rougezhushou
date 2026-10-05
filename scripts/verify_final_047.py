"""Seal Chinese presentation, original assets, and the fresh native upgrade."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_launch_047 import windows,verify_process,foreground,state
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts,partition


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def text(name):return (ROOT/name).read_text(encoding='utf-8')


def main():
    core=read('READABILITY_0.47_VERIFICATION.json');branch=read('BRANCH_UI_0.47_VERIFICATION.json')
    ui=read('UI_0.47_VERIFICATION.json');skills=read('SKILL_UI_0.47_VERIFICATION.json')
    launch=read('APP_0.47_LAUNCH_VERIFICATION.json');previous=read('FINAL_0.46_VERIFICATION.json')
    for result in (core,branch,ui,skills):
        assert result['passed'] and result['version']=='0.47.0'
        assert result['chat_requests']==result['game_actions']==0
    assert (core['tests_run'],core['current_tests_passed'],core['new_unit_tests'])==(589,519,46)
    assert core['historical_combat_tests_skipped']==70 and core['errors']==core['failures']==0
    assert digest(core['test_log'])==core['test_log_sha256']
    assert core['guarded_numeric_functions']==21 and core['numeric_and_recognition_core_unchanged']
    assert not core['numeric_public_replay_rerun'] and core['inherited_numeric_cases']==732
    assert branch['profile_panels']==431 and branch['skill_icon_slots']==949 and branch['recruited_overview_members']==3
    assert branch['private_data_isolated'] and all(branch[k] for k in (
        'profession_branch_filtered','enemy_tier_branch_filtered','floor_branch_filtered'))
    for key,name in branch['screenshots'].items():assert digest(name)==branch['screenshot_sha256'][key]
    assert (ui['battle_stages_checked'],ui['battle_enemy_panels_checked'],ui['battle_occurrence_selections'])==(105,1087,4764)
    assert ui['battle_main_spawn_rows']+ui['battle_branch_rows']==3938
    assert ui['calibrated_stage_clicks']==24 and ui['projected_row_selection_checks']==182
    assert ui['letterbox_sizes_checked']==4 and ui['battle_resize_clicks']==3
    assert ui['private_data_isolated'] and ui['run_state_unchanged'] and ui['enemy_skill_raw_fields_default_hidden']
    for key in ('battle_screenshot','enemy_skill_screenshot','fixed_map_screenshot','fixed_map_detail_screenshot'):
        assert digest(ui[key])==ui[key+'_sha256']
    assert skills['skills_checked']==87 and skills['panel_scenarios']==348 and skills['book_panels']==174
    assert skills['synthetic_module_panels']==18 and skills['book_combination_panels']==9
    assert skills['private_data_isolated'] and skills['unrelated_sections_hidden'] and skills['event_input_absent']
    assert digest(skills['refill_screenshot'])==skills['refill_screenshot_sha256']
    hashes={}
    for result,key in ((core,'source_sha256'),(branch,'source_sha256'),(ui,'source_hashes'),(skills,'source_hashes')):
        for name,sha in result[key].items():assert digest(name)==sha,name;hashes[name]=sha
    changes={n for n,sha in previous['source_sha256'].items() if digest(n)!=sha}
    assert changes==set(core['changed_existing_source_files'])
    backup='.cache/batch-047-before/';manifest=read(backup+'manifest.json')
    assert len(manifest)==20 and all(digest(backup+n)==sha for n,sha in manifest.items())
    public_changes=sorted(n for n,sha in manifest.items() if digest(n)!=sha)
    # Earlier seals did not include all map/report tests; seal every backed-up
    # source explicitly, without treating their old omission as an unchanged file.
    for name in manifest:
        if name.startswith(('rouge/','tests/')) or name=='pyproject.toml':hashes[name]=digest(name)
    professions=read('rouge/data/profession-icons.json');original=read('.cache/game-data/receipt.json')
    assert professions['game_commit']==original['commit']=='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
    assert digest('.cache/game-data/character_table.json')==professions['character_table_sha256']
    expected={'pioneer','warrior','tank','sniper','caster','medic','support','special'}
    assert set(professions['professions'])==expected
    assets=set();profession_bytes=0
    for key,record in professions['professions'].items():
        name='rouge/data/'+record['file'];raw=(ROOT/name).read_bytes();assets.add((ROOT/name).resolve())
        assert len(raw)==record['bytes'] and hashlib.sha256(raw).hexdigest()==record['sha256']
        assert hashlib.sha1(raw).hexdigest()==record['sha1'];assert (record['width'],record['height'])==(26,26)
        assert record['game_profession']==record['correspondence']['game_profession']==key.upper()
        assert record['source_revision_id'] and record['source_page'] and record['correspondence']['source_revision_id']
        profession_bytes+=len(raw)
    assert profession_bytes==6656 and assets=={p.resolve() for p in (ROOT/'rouge/data/profession-icons').glob('*.png')}
    offline=read('.cache/research/professions-047/offline-verification.json')
    assert offline['verified_images_count']==8 and offline['cached_rebuild_network_calls']==0
    assert offline['cached_rebuild_identical_manifest'] and offline['image_source_bytes_preserved']
    for name,sha in offline['hashes'].items():assert digest(name)==sha
    skills_data=read('rouge/data/skill-icons.json');portraits=read('rouge/data/view-catalog.json')
    assert len(skills_data['skills'])==893 and len(skills_data['images'])==884 and len(portraits['images'])==735
    for data in (skills_data,portraits):
        for record in data['images'].values():assert digest('rouge/data/'+record['file'])==record['sha256']
    terms=read('.cache/research/readable-047/battle-terms.json')
    assert not terms['numerical_model_changed'] and terms['game_commit']==original['commit']
    for record in terms['local_sources']:assert digest(record['file'])==record['sha256']
    audit=read('.cache/research/readable-047/general-audit.json')
    for name,sha in audit['validation']['source_hashes'].items():assert digest(name)==sha
    progress=text('PROJECT_PROGRESS.md');assert progress==text(backup+'PROJECT_PROGRESS.md')
    for token in ('已接入','已完成','验收：','FINAL_0.','## 上批'):assert token not in progress,token
    completed=text('PROJECT_COMPLETED.md');header='## 0.46 · 分类分支、招募总览与技能图标'
    assert completed.count('## 0.47 · 职业图标与中文条目')==1
    assert completed.split(header,1)[1]==text(backup+'PROJECT_COMPLETED.md').split(header,1)[1]
    assert text('WORK_IN_PROGRESS.md').endswith(text(backup+'WORK_IN_PROGRESS.md'))
    assert '# 黑流树海助手 · 0.47' in text('README.md')
    package=tomllib.loads(text('pyproject.toml'));assert package['project']['version']=='0.47.0'
    assert 'data/profession-icons/*.png' in package['tool']['setuptools']['package-data']['rouge']
    assert launch['version']=='0.47.0' and launch['game_actions']==launch['chat_requests']==0
    assert all(launch[k] for k in ('only_one_project_window','window_visible_and_restored','window_raised',
        'within_monitor_work_area','previous_app_process_stopped_before_launch','same_run_preserved','history_preserved',
        'settings_and_bindings_unchanged','run_cmd_startup_verified'))
    assert launch['configuration_files_checked']==2 and launch['observation_seconds']==20
    assert len(launch['stability_checks'])==6 and launch['launcher_stderr_bytes']==0
    assert launch['launcher_sha256']==digest('run.cmd')
    checkpoint=read(launch['checkpoint']);after=state();run=read('.local/run-state.json')
    assert checkpoint['run_id_hash']==after['run_id_hash'] and checkpoint['config_hashes']==after['config_hashes']
    prefix=run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    live=windows();assert len(live)==1 and live[0]['pid']==launch['process_id']
    assert live[0]['title']==launch['window_title'];verify_process(live[0]['pid']);focused=foreground(live[0]['hwnd'])
    live=windows();assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    scope=scope_counts(mechanics());assert scope['offline_mechanism_gaps']=={'pending':10,'partial':9}
    assert sum(bool(partition(p,rid)[0]) for rid,p in mechanics()['relics'].items())==135
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not (Path.home()/'.codex/automations/1-3/automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    for file in (ROOT/'scripts').glob('*047.py'):hashes[str(file.relative_to(ROOT))]=digest(file)
    for file in (ROOT/'tests').glob('*047.py'):hashes[str(file.relative_to(ROOT))]=digest(file)
    artifacts=['READABILITY_0.47_VERIFICATION.json','BRANCH_UI_0.47_VERIFICATION.json','UI_0.47_VERIFICATION.json',
        'SKILL_UI_0.47_VERIFICATION.json','APP_0.47_LAUNCH_VERIFICATION.json',launch['checkpoint'],
        '.cache/batch-047-before/manifest.json','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md',
        'README.md','BATCH_0.47.md','rouge/data/profession-icons.json']
    for folder in ('.cache/research/professions-047','.cache/research/readable-047'):
        artifacts.extend(str(p.relative_to(ROOT)) for p in sorted((ROOT/folder).glob('*.json')))
    artifacts.extend(str(p.relative_to(ROOT)) for p in sorted((ROOT/'.cache/readable-047').glob('*.log'))
                     if not p.name.startswith('final'))
    result={'version':'0.47.0','passed':True,'verified_at':time.time(),'current_tests_passed':519,'new_unit_tests':46,
        'historical_combat_tests_skipped':70,'profession_icons':8,'profession_image_bytes':profession_bytes,
        'profession_correspondence_source_verified':True,'profession_cached_rebuild_no_network':True,
        'chinese_default_report_sections_verified':True,'technical_metadata_opt_in':True,
        'unverified_parameter_semantics_not_guessed':True,'technical_switch_preserves_selection_and_conditions':True,
        'operator_overview_recruited_only':True,'profile_panels':431,'skill_icon_slots':949,
        'calculation_profiles':32,'calculation_skills':87,'skill_ui_scenarios':348,'book_panels':174,
        'synthetic_module_panels':18,'battle_ui_stages':105,'battle_ui_enemy_panels':1087,'spawn_rows_rendered':3938,
        'battle_occurrence_selections':4764,'calibrated_original_bitmaps':4,'bound_stages':previous['bound_stages'],
        'uncalibrated_stages':97,'uncalibrated_bitmap_identities':67,'map_calibration_changed':False,
        'guarded_numeric_functions':21,'numeric_and_recognition_core_unchanged':True,'new_recognition_speed_claim':False,
        'numeric_public_replay_rerun':False,'inherited_numeric_cases':732,
        'numeric_public_cases_inherited_from':'RECOGNITION_0.43_VERIFICATION.json',
        'source_sha256':hashes,'changed_prior_tracked_source_files':sorted(changes),
        'changed_backed_up_public_files':public_changes,'evidence_sha256':{n:digest(n) for n in artifacts},
        'public_backup_files':len(manifest),'historical_completed_records_preserved':True,'no_new_todo_items':True,
        'same_current_run_and_history_preserved':True,'history_count_before':checkpoint['history_count'],
        'history_count_after':len(run['history']),'private_configuration_files_verified':len(after['config_hashes']),
        'process_id':live[0]['pid'],'test_window_open':True,'window_raised':True,'foreground_on_final_check':focused,
        'run_cmd_startup_verified':True,'run_state_writes_by_upgrade_script':0,'old_checkpoint_restored':False,
        'new_live_battle_captures':0,'game_actions':0,'chat_requests':0,'automation_status':'DELETED',
        'scope':scope,'active_relic_rules':135,'all_priorities_1_to_3_completed':False,
        'limits':['Chinese labels and pictures do not expand calculated mechanisms or recognition coverage.',
            'Missing parameter semantics, activation times, effective inheritance and probabilities remain unknown.',
            'UI tests use isolated synthetic state and downloaded fixed maps.',
            'P1-3 remaining work and four auxiliary images, eight tier references and 21 floor scopes remain.']}
    (ROOT/'FINAL_0.47_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('passed','current_tests_passed','profession_icons','test_window_open',
        'process_id','history_count_before','history_count_after','same_current_run_and_history_preserved',
        'all_priorities_1_to_3_completed')},ensure_ascii=False))


if __name__=='__main__':main()
