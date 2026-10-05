"""Seal current evidence, behavior tests, public history and native delivery."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_launch_048 import windows,verify_process,foreground,state
from build_animation_selection_048 import build
from rouge.map_projection import projection_data
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts,partition


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def text(name):return (ROOT/name).read_text(encoding='utf-8')


def main():
    core=read('MECHANISMS_0.48_VERIFICATION.json');motion=read('ANIMATION_UI_0.48_VERIFICATION.json')
    branch=read('BRANCH_UI_0.48_VERIFICATION.json');ui=read('UI_0.48_VERIFICATION.json')
    skill=read('SKILL_UI_0.48_VERIFICATION.json');launch=read('APP_0.48_LAUNCH_VERIFICATION.json')
    previous=read('FINAL_0.47_VERIFICATION.json')
    for receipt in (core,motion,branch,ui,skill):
        assert receipt['passed'] and receipt['version']=='0.48.0'
        assert receipt['chat_requests']==receipt['game_actions']==0
    assert (core['tests_run'],core['current_tests_passed'],core['new_unit_tests'])==(614,544,25)
    assert core['historical_combat_tests_skipped']==70 and core['failures']==core['errors']==0
    assert core['numeric_public_replay_rerun'] and core['default_public_outputs_unchanged']
    assert core['exact_default_public_replays']==732
    for key in ('test_log','fresh_previous_public_baseline'):assert digest(core[key])==core[key+'_sha256']
    assert motion['reference_option_visits']==544 and motion['unique_references_visited']==144
    assert motion['catalog_counts']['selectable_references']==160
    assert all(motion[k] for k in ('choice_preserved_on_recalculation_and_return',
        'reference_controls_hidden_when_not_applicable','bait_section_only_on_affected_skill','unknown_damage_is_not_zero'))
    assert branch['profile_panels']==431 and branch['skill_icon_slots']==949
    assert skill['skills_checked']==87 and skill['panel_scenarios']==348 and skill['book_panels']==174
    assert skill['synthetic_module_panels']==18 and skill['book_combination_panels']==9
    assert (ui['battle_stages_checked'],ui['battle_enemy_panels_checked'],ui['battle_occurrence_selections'])==(105,1087,4764)
    assert ui['calibrated_stage_clicks']==36 and ui['projected_row_selection_checks']==318
    assert ui['letterbox_sizes_checked']==4 and ui['run_state_unchanged'] and not ui['live_battle_capture_performed']
    hashes={}
    for receipt in (core,motion,branch,ui,skill):
        assert receipt.get('private_data_isolated',True)
        for name,sha in receipt.get('source_sha256',receipt.get('source_hashes',{})).items():
            assert digest(name)==sha,name;hashes[name]=sha
    for name,sha in motion['screenshots'].items():assert digest(name)==sha
    screenshot=read('ANIMATION_SCREENSHOT_0.48_VERIFICATION.json')
    assert screenshot['passed'] and screenshot['private_data_isolated']
    assert screenshot['game_actions']==screenshot['chat_requests']==0
    for name,sha in screenshot['screenshots'].items():assert digest(name)==sha
    for key,name in branch['screenshots'].items():assert digest(name)==branch['screenshot_sha256'][key]
    for key in ('battle_screenshot','enemy_skill_screenshot','fixed_map_screenshot','fixed_map_detail_screenshot'):
        assert digest(ui[key])==ui[key+'_sha256']
    assert digest(skill['refill_screenshot'])==skill['refill_screenshot_sha256']
    changed={name for name,sha in previous['source_sha256'].items() if digest(name)!=sha}
    assert changed==set(core['changed_existing_source_files'])
    backup='.cache/batch-048-before/';manifest=read(backup+'manifest.json')
    assert len(manifest)==11 and all(digest(backup+n)==sha for n,sha in manifest.items())
    for name in manifest:
        if name.startswith(('rouge/','tests/')) or name=='pyproject.toml':hashes[name]=digest(name)
    production=read('rouge/data/original-animation-references.json')
    assert production==build(ROOT/'.cache/research/timing-048/original-animation-references.json')
    assert production['counts']=={'operators':32,'source_skeletons':64,'animations':923,
        'selectable_references':160,'unverified_or_transition_references':763,'missing_skeletons':1}
    assert len(production['selection_derivation']['excluded_deployment_motions'])==2
    animation=read('.cache/research/timing-048/evidence.json')
    assert animation['resource_commit']==production['source_commit']=='d0b5af0b004b044d322397ce5ae79632b6d9fcdd'
    assert animation['skeleton_bytes']==36095110 and animation['game_actions']==animation['chat_requests']==0
    for name,sha in animation['artifact_sha256'].items():assert digest(name)==sha,name
    assert digest(animation['builder']['path'])==animation['builder']['sha256']
    map_receipt=read('.cache/research/map-projection-048/verification.json')
    assert map_receipt['tests_run']==map_receipt['tests_passed']==26 and map_receipt['new_tests']==8
    for record in map_receipt['source_hashes']:assert digest(record['file'])==record['sha256']
    projection=projection_data();old=read(backup+'rouge/data/battle-map-projections.json')
    assert len(projection['calibrations'])==6 and len(projection['stages'])==12
    for kind in ('calibrations','stages'):
        assert all(projection[kind][key]==value for key,value in old[kind].items())
    added=[value for key,value in projection['calibrations'].items() if key not in old['calibrations']]
    assert sum(len(c['checks']) for c in added)==14
    assert all(c['tolerance_px']==4 for c in added)
    public_artifacts=['MECHANISMS_0.48_VERIFICATION.json','ANIMATION_UI_0.48_VERIFICATION.json',
        'BRANCH_UI_0.48_VERIFICATION.json','SKILL_UI_0.48_VERIFICATION.json','UI_0.48_VERIFICATION.json',
        'APP_0.48_LAUNCH_VERIFICATION.json',core['test_log'],core['fresh_previous_public_baseline'],
        '.cache/mechanisms-048/fresh-before.log',backup+'manifest.json','BATCH_0.48.md',
        'WORK_IN_PROGRESS.md','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md','README.md',
        '.cache/research/timing-048/evidence.json','.cache/research/relics-048/evidence.json',
        '.cache/research/relics-048/REPORT.md','.cache/research/relics-048/manifest.json',
        '.cache/research/map-projection-048/evidence.json','.cache/research/map-projection-048/verification.json',
        '.cache/research/map-projection-048/ro6_n_3_4-numbered-ground-landmarks.png',
        '.cache/research/map-projection-048/ro6_n_3_6-numbered-ground-landmarks.png',
        '.cache/research/mechanisms-audit-048/receipt.json','.cache/research/mechanisms-audit-048/REPORT.md']
    public_artifacts+=list(motion['screenshots'])+list(branch['screenshots'].values())+list(screenshot['screenshots'])
    public_artifacts+=['ANIMATION_SCREENSHOT_0.48_VERIFICATION.json','.cache/mechanisms-048/initial-verification-findings.json']
    public_artifacts+=[ui[k] for k in ('battle_screenshot','enemy_skill_screenshot','fixed_map_screenshot','fixed_map_detail_screenshot')]
    public_artifacts.append(skill['refill_screenshot'])
    progress=text('PROJECT_PROGRESS.md')
    assert '93个关卡、65张独立原图' in progress and '97个关卡' not in progress
    for token in ('已接入','已完成','验收：','FINAL_0.','## 上批'):assert token not in progress
    header='## 0.47 · 职业图标与中文条目'
    assert text('PROJECT_COMPLETED.md').split(header,1)[1]==text(backup+'PROJECT_COMPLETED.md').split(header,1)[1]
    assert text('WORK_IN_PROGRESS.md').endswith(text(backup+'WORK_IN_PROGRESS.md'))
    assert '# 黑流树海助手 · 0.48' in text('README.md')
    assert tomllib.loads(text('pyproject.toml'))['project']['version']=='0.48.0'
    assert scope_counts(mechanics())['offline_mechanism_gaps']=={'pending':10,'partial':9}
    assert sum(bool(partition(p,rid)[0]) for rid,p in mechanics()['relics'].items())==135
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not (Path.home()/'.codex/automations/1-3/automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    assert launch['version']=='0.48.0' and launch['chat_requests']==launch['game_actions']==0
    assert all(launch[k] for k in ('only_one_project_window','window_visible_and_restored','window_raised',
        'within_monitor_work_area','previous_app_process_stopped_before_launch','same_run_preserved',
        'history_preserved','settings_and_bindings_unchanged','run_cmd_startup_verified'))
    assert launch['configuration_files_checked']==2 and launch['observation_seconds']==20
    assert len(launch['stability_checks'])==6 and launch['launcher_stderr_bytes']==0
    assert digest('run.cmd')==launch['launcher_sha256']
    checkpoint=read(launch['checkpoint']);after=state();run=read('.local/run-state.json')
    assert checkpoint['run_id_hash']==after['run_id_hash'] and checkpoint['config_hashes']==after['config_hashes']
    prefix=run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    live=windows();assert len(live)==1 and live[0]['pid']==launch['process_id']
    assert live[0]['title']==launch['window_title'];verify_process(live[0]['pid']);focused=foreground(live[0]['hwnd'])
    live=windows();assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    for base in ('scripts','tests'):
        for path in (ROOT/base).glob('*048.py'):hashes[str(path.relative_to(ROOT))]=digest(str(path.relative_to(ROOT)))
    result={'version':'0.48.0','passed':True,'verified_at':time.time(),'current_tests_passed':544,
        'new_unit_tests':25,'historical_combat_tests_skipped':70,'default_public_outputs_exact_cases':732,
        'production_animation_references':160,'ui_animation_references':144,'animation_option_visits':544,
        'calibrated_maps':6,'calibrated_stages':12,'new_independent_ground_landmarks':14,
        'remaining_uncalibrated_stages':93,'remaining_uncalibrated_unique_images':65,
        'source_sha256':hashes,'artifact_sha256':{n:digest(n) for n in sorted(set(public_artifacts))},
        'process_id':live[0]['pid'],'window_title':live[0]['title'],'test_window_open':True,'foreground_verified':focused,
        'history_count_before':checkpoint['history_count'],'history_count_after':after['history_count'],
        'same_current_run_and_history_preserved':True,'configuration_files_unchanged':2,
        'game_actions':0,'chat_requests':0,'recognition_speed_claim':False,'all_priorities_1_to_3_completed':False,
        'limitations':['Animation selection is an explicit offline reference, not verified client binding.',
            'Bait snapshot/timing, relic stacking and other P1-3 mechanisms remain unresolved.',
            'Ground fit does not verify raised portal artwork, spawn offsets, high ground or pathfinding.']}
    (ROOT/'FINAL_0.48_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('passed','current_tests_passed','default_public_outputs_exact_cases',
        'calibrated_maps','test_window_open','process_id','history_count_before','history_count_after')},ensure_ascii=False))


if __name__=='__main__':main()
