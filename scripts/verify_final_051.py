"""Seal current evidence, bounded map calibration and visible native delivery."""
import ast,compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_launch_051 import windows,verify_process,foreground,state
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts
from rouge.map_projection import projection_data,grid_digest
from rouge.battle_preview import battle_data,DATA


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def text(name):return (ROOT/name).read_text(encoding='utf-8')
def verify_file(name,record):
    data=(ROOT/name).read_bytes()
    assert hashlib.sha256(data).hexdigest()==record['sha256'],name
    if 'bytes' in record:assert len(data)==record['bytes'],name


def main():
    core=read('INVENTORY_0.51_VERIFICATION.json');recipient=read('UI_0.51_VERIFICATION.json')
    maps=read('MAP_UI_0.51_VERIFICATION.json');launch=read('APP_0.51_LAUNCH_VERIFICATION.json')
    hashes={}
    for receipt in (core,recipient,maps):
        assert receipt['passed'] and receipt['version']=='0.51.0'
        assert receipt['game_actions']==receipt['chat_requests']==0
        for name,sha in receipt.get('source_sha256',receipt.get('source_hashes',{})).items():
            assert digest(name)==sha,name;hashes[name.replace('\\','/')]=sha
    assert core['historical_combat_tests_skipped']==70 and core['errors']==core['failures']==0
    assert core['tests_run']==693 and core['current_tests_passed']==623 and core['new_unit_tests']==31
    assert digest(core['test_log'])==core['test_log_sha256']
    assert not core['numeric_public_replay_rerun'] and core['inherited_exact_default_public_replays']==732
    assert digest(core['previous_numeric_replay_receipt'])==core['previous_numeric_replay_receipt_sha256']
    assert recipient['parents_checked']==7 and len(recipient['cases'])==29
    assert recipient['private_state_isolated'] and recipient['game_captures']==0
    assert all(row['passed'] for row in recipient['cases'])
    for name,sha in recipient['screenshots'].items():assert digest(name)==sha,name
    assert maps['private_data_isolated'] and maps['run_state_unchanged'] and not maps['live_battle_capture_performed']
    assert (maps['battle_stages_checked'],maps['battle_enemy_panels_checked'],maps['battle_occurrence_selections'])==(105,1087,4764)
    assert maps['calibrated_stage_clicks']==60 and maps['letterbox_sizes_checked']==4
    for key in ('battle_screenshot','enemy_skill_screenshot','fixed_map_screenshot','fixed_map_detail_screenshot'):
        assert digest(maps[key])==maps[key+'_sha256']
    backup='.cache/batch-051-before/';manifest=read(backup+'manifest.json')
    assert len(manifest)==8 and all(digest(backup+n)==sha for n,sha in manifest.items())
    assert not any(n.startswith(('.local/','local-settings')) for n in manifest)
    def methods(source):
        c=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='MainWindow')
        return {n.name:ast.dump(n,include_attributes=False) for n in c.body if isinstance(n,ast.FunctionDef)}
    before,after=methods(text(backup+'rouge/app.py')),methods(text('rouge/app.py'))
    assert set(before)==set(after) and 'calculate' in after
    assert {name for name in before if before[name]!=after[name]}=={'__init__','sync_target_buffs'}
    inventory='.cache/research/inventory-051/'
    im=read(inventory+'manifest.json')
    for item in im['files']:verify_file(item['path'],item)
    fixed=read(inventory+'sealed-current.json');prior=read(inventory+'sealed-before.json')
    assert fixed['tests_run']==54 and fixed['errors']==fixed['failures']==0
    assert fixed['run_state_sha256_before']==fixed['run_state_sha256_after']==digest('rouge/run_state.py')
    assert prior['tests_run']==19 and prior['failures']==11 and len(prior['failed_methods'])==9
    assert prior['run_state_sha256']==digest(backup+'rouge/run_state.py')
    assert prior['test_sha256']==fixed['test_sha256']==digest('tests/test_inventory_snapshot_051.py')
    version='.cache/research/p1-version-051/'
    vm=read(version+'manifest.json')
    for item in vm['files']:verify_file(version+item['file'],item)
    assert len(vm['files'])==23 and sum(i['bytes'] for i in vm['files'])==1021798
    ve=read(version+'evidence.json')
    assert len(ve['official_notice']['fix_facts'])==3
    assert ve['official_notice']['client_number_in_official_notice'] is None
    assert not ve['official_notice']['installed_client_version_verified'] and not ve['formula_changed']
    assert ve['no_newer_topic_or_buff_commit_found_in_two_default_branches'] and len(ve['current_path_checks'])==4
    assert ve['july_mirror_commit']['topic_change_is_event_display_only']
    assert ve['loss_hp_current_template']['product_scope']=='combat callback reference only; no numeric reintroduction'
    mp='.cache/research/map-projection-051/'
    mm=read(mp+'manifest.json')
    for name,item in mm['files'].items():verify_file(name,item)
    me=read(mp+'evidence.json');projection=projection_data();old=read(backup+'rouge/data/battle-map-projections.json')
    assert digest('rouge/data/battle-map-projections.json')==me['output_sha256']
    assert digest(me['candidate_file'])==me['output_sha256']
    assert len(projection['calibrations'])==10 and len(projection['stages'])==20
    assert sum(len(c['checks']) for c in projection['calibrations'].values())==78
    for kind in ('calibrations','stages'):assert all(projection[kind][k]==v for k,v in old[kind].items())
    assert me['new_independent_checks']==29 and me['max_new_independent_error_px']<=4
    assert me['remaining_stage_count_if_integrated']==85 and me['remaining_distinct_bitmap_count_if_integrated']==61
    for record in me['sources']:
        name='rouge/data/'+record['image']['file'];verify_file(name,record['image'])
        data=(ROOT/name).read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==record['image']['source_blob_sha1']
        verify_file(record['cached_level_file'],record['level'])
        assert grid_digest(battle_data()['stages'][record['stage']])==record['grid_sha256']
    for probe in me['rejected_probes_retained']:
        assert digest(probe['file'])==probe['sha256'] and not probe['accepted_for_runtime']
        assert probe['max_probe_error_px']>4
    assert scope_counts(mechanics())['offline_mechanism_gaps']=={'pending':3,'partial':9}
    progress=text('PROJECT_PROGRESS.md');assert '85个关卡、61张独立原图' in progress
    for token in ('已接入','已完成','验收：','FINAL_0.','## 上批'):assert token not in progress
    header='## 0.50 · 个人强化归属条件与库存完整性'
    assert text('PROJECT_COMPLETED.md').split(header,1)[1]==text(backup+'PROJECT_COMPLETED.md').split(header,1)[1]
    assert text('WORK_IN_PROGRESS.md').endswith(text(backup+'WORK_IN_PROGRESS.md'))
    assert '# 黑流树海助手 · 0.51' in text('README.md')
    assert tomllib.loads(text('pyproject.toml'))['project']['version']=='0.51.0'
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not (Path.home()/'.codex/automations/1-3/automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    assert launch['version']=='0.51.0' and launch['game_actions']==launch['chat_requests']==0
    assert all(launch[k] for k in ('only_one_project_window','window_visible_and_restored','window_raised',
        'within_monitor_work_area','previous_app_process_stopped_before_launch','same_run_preserved',
        'history_preserved','settings_and_bindings_unchanged','run_cmd_startup_verified'))
    assert launch['configuration_files_checked']==2 and launch['observation_seconds']==20
    assert len(launch['stability_checks'])==6 and launch['launcher_stderr_bytes']==0
    checkpoint=read(launch['checkpoint']);current=state();run=read('.local/run-state.json')
    assert checkpoint['run_id_hash']==current['run_id_hash'] and checkpoint['config_hashes']==current['config_hashes']
    prefix=run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    live=windows();assert len(live)==1 and live[0]['pid']==launch['process_id']
    verify_process(live[0]['pid']);focused=foreground(live[0]['hwnd'])
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    for path in (ROOT/'rouge').glob('*.py'):hashes[path.relative_to(ROOT).as_posix()]=digest(path.relative_to(ROOT))
    for base in ('scripts','tests'):
        for path in (ROOT/base).glob('*051.py'):hashes[path.relative_to(ROOT).as_posix()]=digest(path.relative_to(ROOT))
    artifacts=['INVENTORY_0.51_VERIFICATION.json','UI_0.51_VERIFICATION.json','MAP_UI_0.51_VERIFICATION.json',
        'APP_0.51_LAUNCH_VERIFICATION.json','BATCH_0.51.md','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md',
        'README.md','WORK_IN_PROGRESS.md',backup+'manifest.json']
    for directory in ('.cache/inventory-051','.cache/recipient-051','.cache/mechanisms-051',
        '.cache/research/inventory-051','.cache/research/p1-version-051','.cache/research/map-projection-051'):
        artifacts += [p.relative_to(ROOT).as_posix() for p in (ROOT/directory).rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts]
    result={'version':'0.51.0','passed':True,'verified_at':time.time(),'current_tests_passed':623,
        'new_unit_tests':31,'historical_combat_tests_skipped':70,'numeric_public_replay_rerun':False,
        'inherited_default_public_replays':732,'recipient_ui_cases':29,'inventory_new_tests':19,
        'prior_failed_inventory_methods':9,'offline_mechanism_gaps':{'pending':3,'partial':9},
        'calibrated_maps':10,'calibrated_stages':20,'independent_ground_landmarks':78,
        'new_independent_ground_landmarks':29,'remaining_uncalibrated_stages':85,
        'remaining_uncalibrated_unique_images':61,'source_sha256':hashes,
        'artifact_sha256':{n:digest(n) for n in sorted(set(artifacts))},
        'process_id':live[0]['pid'],'window_title':live[0]['title'],'test_window_open':True,'foreground_verified':focused,
        'history_count_before':checkpoint['history_count'],'history_count_after':current['history_count'],
        'same_current_run_and_history_preserved':True,'configuration_files_unchanged':2,
        'game_actions':0,'chat_requests':0,'recognition_speed_claim':False,
        'all_priorities_1_to_3_completed':False,'all_priority_1_completed':False,
        'limitations':['Inventory and personal contracts use synthetic observations; automatic layer/recipient reading remains absent.',
            'Ground holdouts do not prove unmeasured regions, elevated surfaces, portal/spawn offsets or live paths.',
            'Official repair notice and historical configuration changes do not supply missing offline formulas.']}
    (ROOT/'FINAL_0.51_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('passed','current_tests_passed','calibrated_maps','test_window_open',
        'process_id','history_count_before','history_count_after')},ensure_ascii=False))


if __name__=='__main__':main()
