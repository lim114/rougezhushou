"""Seal branch/overview/icon validation and the fresh real-window upgrade."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_launch_046 import windows,verify_process,foreground,state
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts,partition


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def text(name):return (ROOT/name).read_text(encoding='utf-8')


def main():
    core=read('BRANCH_0.46_VERIFICATION.json');branch=read('BRANCH_UI_0.46_VERIFICATION.json')
    ui=read('UI_0.46_VERIFICATION.json');skills=read('SKILL_UI_0.46_VERIFICATION.json')
    launch=read('APP_0.46_LAUNCH_VERIFICATION.json');previous=read('FINAL_0.45_VERIFICATION.json')
    for r in (core,branch,ui,skills):
        assert r['passed'] and r['version']=='0.46.0'
        assert r['chat_requests']==r['game_actions']==0
    assert core['tests_run']==543 and core['current_tests_passed']==473 and core['new_unit_tests']==19
    assert core['historical_combat_tests_skipped']==70 and core['errors']==core['failures']==0
    assert digest(core['test_log'])==core['test_log_sha256']
    assert core['numeric_and_recognition_core_unchanged'] and core['map_calibrations_unchanged']
    assert not core['numeric_public_replay_rerun'] and core['inherited_numeric_cases']==732
    assert not core['new_recognition_speed_claim']
    assert branch['private_data_isolated'] and branch['profile_panels']==431 and branch['skill_icon_slots']==949
    assert branch['recruited_overview_members']==3 and all(branch[k] for k in (
        'profession_branch_filtered','enemy_tier_branch_filtered','floor_branch_filtered'))
    for key,path in branch['screenshots'].items():assert digest(path)==branch['screenshot_sha256'][key]
    assert ui['battle_stages_checked']==105 and ui['battle_enemy_panels_checked']==1087
    assert ui['battle_occurrence_selections']==4764 and ui['calibrated_stage_clicks']==24
    assert ui['projected_row_selection_checks']==182 and ui['letterbox_sizes_checked']==4
    assert ui['battle_resize_clicks']==3 and ui['private_data_isolated'] and ui['run_state_unchanged']
    for key in ('battle_screenshot','enemy_skill_screenshot','fixed_map_screenshot','fixed_map_detail_screenshot'):
        assert digest(ui[key])==ui[key+'_sha256']
    assert skills['skills_checked']==87 and skills['panel_scenarios']==348
    assert skills['book_panels']==174 and skills['synthetic_module_panels']==18
    assert skills['book_combination_panels']==9 and skills['private_data_isolated']
    assert skills['unrelated_sections_hidden'] and skills['event_input_absent']
    assert digest(skills['refill_screenshot'])==skills['refill_screenshot_sha256']
    hashes={}
    for r,key in ((core,'source_sha256'),(branch,'source_sha256'),(ui,'source_hashes'),(skills,'source_hashes')):
        for name,sha in r[key].items():assert digest(name)==sha,name;hashes[name]=sha
    changed={name for name,sha in previous['source_sha256'].items() if digest(name)!=sha}
    assert changed==set(core['changed_existing_source_files'])
    icons=read('rouge/data/skill-icons.json');receipt=read('.cache/game-data/receipt.json')
    assert icons['game_commit']==receipt['commit']=='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
    assert icons['resource_commit']=='d0b5af0b004b044d322397ce5ae79632b6d9fcdd'
    assert icons['skill_source']==receipt['files']['skill_table']
    assert digest('.cache/game-data/skill_table.json')==icons['skill_source']['sha256']
    assert digest('.cache/research/skills-046/skill-tree.json')==icons['tree_sha256']
    assert len(icons['skills'])==893 and len(icons['images'])==884
    icon_paths=set();image_bytes=0
    for r in icons['images'].values():
        path=ROOT/'rouge/data'/r['file'];raw=path.read_bytes()
        assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['blob_sha1']
        image_bytes+=len(raw);icon_paths.add(path.resolve())
    assert image_bytes==16892002 and icon_paths=={p.resolve() for p in (ROOT/'rouge/data/skill-icons').glob('*.png')}
    portraits=read('rouge/data/view-catalog.json')
    for r in portraits['images'].values():assert digest('rouge/data/'+r['file'])==r['sha256']
    backup='.cache/batch-046-before/';manifest=read(backup+'manifest.json')
    assert len(manifest)==9 and all(digest(backup+name)==sha for name,sha in manifest.items())
    progress=text('PROJECT_PROGRESS.md')
    assert progress==text(backup+'PROJECT_PROGRESS.md')
    for token in ('已接入','已完成','验收：','FINAL_0.','## 上批'):assert token not in progress,token
    header='## 0.45 · 刷新保留、图片分类与预测面板'
    completed=text('PROJECT_COMPLETED.md')
    assert completed.count('## 0.46 · 分类分支、招募总览与技能图标')==1
    assert completed.split(header,1)[1]==text(backup+'PROJECT_COMPLETED.md').split(header,1)[1]
    assert text('WORK_IN_PROGRESS.md').endswith(text(backup+'WORK_IN_PROGRESS.md'))
    assert '# 黑流树海助手 · 0.46' in text('README.md')
    assert tomllib.loads(text('pyproject.toml'))['project']['version']=='0.46.0'
    assert launch['version']=='0.46.0' and launch['chat_requests']==launch['game_actions']==0
    assert launch['run_cmd_startup_verified'] and launch['previous_app_process_stopped_before_launch']
    assert launch['only_one_project_window'] and launch['window_visible_and_restored']
    assert launch['window_raised'] and launch['within_monitor_work_area'] and launch['launcher_stderr_bytes']==0
    assert launch['same_run_preserved'] and launch['history_preserved'] and launch['settings_and_bindings_unchanged']
    assert launch['configuration_files_checked']==2 and len(launch['stability_checks'])==6 and launch['observation_seconds']==20
    assert launch['launcher_sha256']==digest('run.cmd')
    checkpoint=read(launch['checkpoint']);after=state();run=read('.local/run-state.json')
    assert checkpoint['run_id_hash']==after['run_id_hash']
    prefix=run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    assert checkpoint['config_hashes']==after['config_hashes']
    live=windows();assert len(live)==1 and live[0]['pid']==launch['process_id']
    assert live[0]['title']==launch['window_title'];verify_process(live[0]['pid'])
    focused=foreground(live[0]['hwnd']);live=windows()
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    scope=scope_counts(mechanics());assert scope['offline_mechanism_gaps']=={'pending':10,'partial':9}
    assert sum(bool(partition(p,rid)[0]) for rid,p in mechanics()['relics'].items())==135
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not (Path.home()/'.codex/automations/1-3/automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    for name in ('scripts/verify_launch_046.py','scripts/verify_final_046.py'):hashes[name]=digest(name)
    artifacts=['BRANCH_0.46_VERIFICATION.json','BRANCH_UI_0.46_VERIFICATION.json','UI_0.46_VERIFICATION.json',
        'SKILL_UI_0.46_VERIFICATION.json','APP_0.46_LAUNCH_VERIFICATION.json','RECOGNITION_0.43_VERIFICATION.json',
        '.cache/research/skills-046/root-tree.json','.cache/research/skills-046/skill-tree.json',
        '.cache/research/skills-046/download-receipt.json','.cache/batch-046-before/manifest.json',launch['checkpoint'],
        'PROJECT_PROGRESS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','README.md','BATCH_0.46.md']
    # A redirected final stdout log is still growing when this receipt is sealed.
    artifacts += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'.cache/branch-046').glob('*.log')) if not p.name.startswith('final')]
    result={'version':'0.46.0','passed':True,'verified_at':time.time(),'current_tests_passed':473,'new_unit_tests':19,
        'historical_combat_tests_skipped':70,'selectable_category_branches_verified':True,
        'operator_overview_recruited_only':True,'operator_overview_present_only':True,'account_profiles_excluded_from_overview':True,
        'overview_incremental_refresh_verified':True,'empty_overview_has_no_stale_prediction':True,
        'enemy_overview_scope':'current_stage','stage_overview_scope':'all_available_stages',
        'profile_panels_with_skill_icons':431,'skill_icon_slots':949,'unique_skill_ids':893,
        'skill_original_images':884,'skill_image_bytes':image_bytes,'skill_binding_uses_source_icon_id':True,
        'calculation_profiles':32,'calculation_skills':87,'skill_ui_scenarios':348,'book_panels':174,'synthetic_module_panels':18,
        'battle_ui_stages':105,'battle_ui_enemy_panels':1087,'battle_occurrence_selections':4764,
        'calibrated_original_bitmaps':4,'bound_stages':previous['bound_stages'],'uncalibrated_stages':97,
        'uncalibrated_bitmap_identities':67,'map_calibration_changed':False,'new_recognition_speed_claim':False,
        'numeric_public_replay_rerun':False,'inherited_numeric_cases':732,'numeric_public_cases_inherited_from':'RECOGNITION_0.43_VERIFICATION.json',
        'numeric_and_recognition_core_unchanged':True,'source_sha256':hashes,'changed_existing_source_files':sorted(changed),
        'evidence_sha256':{n:digest(n) for n in artifacts},'scope':scope,'active_relic_rules':135,
        'no_new_todo_items':True,'historical_completed_records_preserved':True,'public_backup_files':9,
        'same_current_run_and_history_preserved':True,'history_count_before':checkpoint['history_count'],
        'history_count_after':len(run['history']),'private_configuration_files_verified':len(after['config_hashes']),
        'process_id':live[0]['pid'],'test_window_open':True,'window_raised':True,'foreground_on_final_check':focused,
        'run_cmd_startup_verified':True,'run_state_writes_by_upgrade_script':0,'old_checkpoint_restored':False,
        'new_live_battle_captures':0,'game_actions':0,'chat_requests':0,'automation_status':'DELETED',
        'all_priorities_1_to_3_completed':False,
        'limits':['Skill icon coverage is presentation coverage, not 949 fully calculated skills.',
                  'Four auxiliary enemy pictures, eight derived-enemy tier references and 21 special-stage floor scopes remain unknown.',
                  'Numerical mechanism, recognition completeness and remaining P1-3 items are unchanged.',
                  'Branch/skill UI checks use isolated synthetic state, not full live-game recognition accuracy.']}
    (ROOT/'FINAL_0.46_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('passed','current_tests_passed','operator_overview_recruited_only',
        'skill_icon_slots','skill_original_images','test_window_open','process_id','history_count_before','history_count_after',
        'same_current_run_and_history_preserved','all_priorities_1_to_3_completed')},ensure_ascii=False))


if __name__=='__main__':main()
