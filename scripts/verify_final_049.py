"""Seal this batch's evidence, public changes and actual native delivery."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_launch_049 import windows,verify_process,foreground,state
from rouge.map_projection import projection_data,grid_digest
from rouge.battle_preview import battle_data,DATA
from rouge.map_recognition import map_data
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts,partition


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def text(name):return (ROOT/name).read_text(encoding='utf-8')


def main():
    core=read('ROUTES_0.49_VERIFICATION.json');route=read('EXPLORATION_UI_0.49_VERIFICATION.json')
    ui=read('UI_0.49_VERIFICATION.json');launch=read('APP_0.49_LAUNCH_VERIFICATION.json')
    hashes={}
    for receipt in (core,route,ui):
        assert receipt['passed'] and receipt['version']=='0.49.0'
        assert receipt['game_actions']==receipt['chat_requests']==0
        for name,sha in receipt.get('source_sha256',receipt.get('source_hashes',{})).items():
            assert digest(name)==sha,name;hashes[name]=sha
    assert (core['tests_run'],core['current_tests_passed'],core['new_unit_tests'])==(640,570,26)
    assert core['historical_combat_tests_skipped']==70 and core['errors']==core['failures']==0
    assert core['numeric_and_recognition_core_sources_unchanged'] and not core['numeric_public_replay_rerun']
    assert digest(core['test_log'])==core['test_log_sha256']
    assert digest(core['previous_numeric_replay_receipt'])==core['previous_numeric_replay_receipt_sha256']
    assert route['spatial_clicks']==route['window_sizes']==3 and route['private_data_isolated']
    assert all(route[k] for k in ('actual_corridor_and_topology_paint_verified','selection_and_cursor_preserved',
        'technical_switch_preserved','missing_marker_no_stale_route','historical_and_restart_no_current_route'))
    for name,sha in route['screenshots'].items():assert digest(name)==sha
    assert (ui['battle_stages_checked'],ui['battle_enemy_panels_checked'],ui['battle_occurrence_selections'])==(105,1087,4764)
    assert (ui['calibrated_stage_clicks'],ui['projected_row_selection_checks'],ui['letterbox_sizes_checked'])==(48,498,4)
    assert ui['private_data_isolated'] and ui['run_state_unchanged'] and not ui['live_battle_capture_performed']
    for key in ('battle_screenshot','enemy_skill_screenshot','fixed_map_screenshot','fixed_map_detail_screenshot'):
        assert digest(ui[key])==ui[key+'_sha256']
    backup='.cache/batch-049-before/';manifest=read(backup+'manifest.json')
    assert len(manifest)==10 and all(digest(backup+n)==sha for n,sha in manifest.items())
    assert not any(n.startswith(('.local/','local-settings')) for n in manifest)
    for name in manifest:
        if name.startswith('rouge/') or name=='pyproject.toml':hashes[name]=digest(name)
    projection=projection_data();old=read(backup+'rouge/data/battle-map-projections.json')
    assert len(projection['calibrations'])==8 and len(projection['stages'])==16
    assert sum(len(c['checks']) for c in projection['calibrations'].values())==49
    for kind in ('calibrations','stages'):
        assert all(projection[kind][key]==value for key,value in old[kind].items())
    added=[c for key,c in projection['calibrations'].items() if key not in old['calibrations']]
    assert sum(len(c['checks']) for c in added)==15 and all(c['tolerance_px']==4 for c in added)
    assert max(c['error_px'] for p in added for c in p['checks'])<=4
    me=read('.cache/research/map-projection-049/evidence.json')
    mv=read('.cache/research/map-projection-049/verification.json')
    assert digest('rouge/data/battle-map-projections.json')==me['output_sha256']
    assert digest(backup+'rouge/data/battle-map-projections.json')==me['prior_file_sha256']
    assert mv['tests_run']==mv['passed']==34 and mv['failed']==mv['errors']==0
    assert digest(mv['log_file'])==mv['log_sha256']
    assert mv['remaining_stage_count']==89 and mv['remaining_distinct_bitmap_count']==63
    for record in me['sources']:
        image=ROOT/'rouge/data'/record['image']['file'];data=image.read_bytes()
        assert hashlib.sha256(data).hexdigest()==record['image']['sha256']
        assert len(data)==record['image']['bytes']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==record['image']['source_blob_sha1']
        assert digest(record['cached_level_file'])==record['level']['sha256']
        assert grid_digest(battle_data()['stages'][record['stage']])==record['grid_sha256']
    for probe in me['rejected_probes_retained']:
        assert digest(probe['file'])==probe['sha256'] and not probe['accepted_for_runtime'] and probe['max_probe_error_px']>4
    re=read('.cache/research/routes-049/evidence.json')
    assert len(re['facts'])==8 and all(f['verified'] for f in re['facts'])
    assert re['current_page']['declared_revision']==433770 and not re['current_page']['revision_body_retrieved']
    for record in re['artifacts']:assert digest(record['path'])==record['sha256']
    for record in (re['original_topic'],re['reused_previous_page']):assert digest(record['path'])==record['sha256']
    he=read('.cache/research/relic-hotfix-049/evidence.json');hm=read('.cache/research/relic-hotfix-049/manifest.json')
    assert he['file_count']==29 and he['total_source_bytes']==229386 and he['lua_file_count']==28
    assert he['numeric_model_changes_allowed']==he['todo_removal_allowed']==[]
    assert not he['foreign_runtime_executed'] and not he['private_files_read_or_copied']
    assert digest('.cache/research/relic-hotfix-049/manifest.json')==he['source_manifest_sha256']
    assert digest(hm['source_tree']['file'])==hm['source_tree']['sha256']
    for record in hm['files']:
        data=(ROOT/'.cache/research/relic-hotfix-049'/record['file']).read_bytes()
        assert len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==record['git_blob']
    audit=read('.cache/research/relic-hotfix-049/route-audit.json')
    assert audit['finding_count']==0 and audit['final_review']['open_findings']==[]
    assert audit['final_review']['projection_caption_binding_count']==16
    for record in audit['reviewed_files']:assert digest(record['path'])==record['sha256']
    assert sum(len(t['nodes'])**2 for t in map_data()['templates'])==40514
    assert scope_counts(mechanics())['offline_mechanism_gaps']=={'pending':10,'partial':9}
    assert sum(bool(partition(p,rid)[0]) for rid,p in mechanics()['relics'].items())==135
    progress=text('PROJECT_PROGRESS.md');assert '89个关卡、63张独立原图' in progress
    for token in ('已接入','已完成','验收：','FINAL_0.','## 上批'):assert token not in progress
    header='## 0.48 · 原版动作参考、诱饵保护与固定地图扩展'
    assert text('PROJECT_COMPLETED.md').split(header,1)[1]==text(backup+'PROJECT_COMPLETED.md').split(header,1)[1]
    assert text('WORK_IN_PROGRESS.md').endswith(text(backup+'WORK_IN_PROGRESS.md'))
    assert '# 黑流树海助手 · 0.49' in text('README.md')
    assert tomllib.loads(text('pyproject.toml'))['project']['version']=='0.49.0'
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not (Path.home()/'.codex/automations/1-3/automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    assert launch['version']=='0.49.0' and launch['game_actions']==launch['chat_requests']==0
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
    verify_process(live[0]['pid']);focused=foreground(live[0]['hwnd'])
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    for path in (ROOT/'rouge').glob('*.py'):hashes[str(path.relative_to(ROOT))]=digest(str(path.relative_to(ROOT)))
    for base in ('scripts','tests'):
        for path in (ROOT/base).glob('*049.py'):hashes[str(path.relative_to(ROOT))]=digest(str(path.relative_to(ROOT)))
    artifacts=['ROUTES_0.49_VERIFICATION.json','EXPLORATION_UI_0.49_VERIFICATION.json','UI_0.49_VERIFICATION.json',
        'APP_0.49_LAUNCH_VERIFICATION.json','BATCH_0.49.md','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md',
        'README.md','WORK_IN_PROGRESS.md',backup+'manifest.json']
    artifacts+=list(route['screenshots'])+[ui[k] for k in ('battle_screenshot','enemy_skill_screenshot',
        'fixed_map_screenshot','fixed_map_detail_screenshot')]
    for directory in ('.cache/routes-049','.cache/research/routes-049',
                      '.cache/research/map-projection-049','.cache/research/relic-hotfix-049'):
        artifacts += [str(p.relative_to(ROOT)) for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    result={'version':'0.49.0','passed':True,'verified_at':time.time(),'current_tests_passed':570,
        'new_unit_tests':26,'historical_combat_tests_skipped':70,'template_count':43,'template_node_pairs_checked':40514,
        'numeric_public_replay_rerun':False,'inherited_default_public_replays':732,
        'calibrated_maps':8,'calibrated_stages':16,'independent_ground_landmarks':49,
        'new_independent_ground_landmarks':15,'remaining_uncalibrated_stages':89,'remaining_uncalibrated_unique_images':63,
        'source_sha256':hashes,'artifact_sha256':{n:digest(n) for n in sorted(set(artifacts))},
        'process_id':live[0]['pid'],'window_title':live[0]['title'],'test_window_open':True,'foreground_verified':focused,
        'history_count_before':checkpoint['history_count'],'history_count_after':after['history_count'],
        'same_current_run_and_history_preserved':True,'configuration_files_unchanged':2,
        'game_actions':0,'chat_requests':0,'recognition_speed_claim':False,'all_priorities_1_to_3_completed':False,
        'limitations':['Route references do not prove entry, AP affordability, yield or optimality.',
            'Declared PRTS revision body was unavailable; current page bytes are preserved.',
            'Ground holdouts, including a single column, do not verify lateral/elevated/spawn precision.',
            'Unregistered hotfixes do not prove actual activation; relic/timing unknowns remain.']}
    (ROOT/'FINAL_0.49_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('passed','current_tests_passed','calibrated_maps',
        'test_window_open','process_id','history_count_before','history_count_after')},ensure_ascii=False))


if __name__=='__main__':main()
