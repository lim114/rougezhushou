"""Seal bounded relic implementation and current visible native delivery."""
import ast,compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_launch_052 import windows,verify_process,foreground,state
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts

def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def text(name):return (ROOT/name).read_text(encoding='utf-8')
def verify_file(name,record):
    raw=(ROOT/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==record['sha256'],name
    if 'bytes' in record:assert len(raw)==record['bytes'],name

def main():
    core=read('RELICS_0.52_VERIFICATION.json');ui=read('RELIC_UI_0.52_VERIFICATION.json')
    recipient=read('UI_0.52_VERIFICATION.json');skill=read('SKILL_UI_0.52_VERIFICATION.json')
    launch=read('APP_0.52_LAUNCH_VERIFICATION.json');hashes={}
    for r in (core,ui,recipient,skill):
        assert r['passed'] and r['version']=='0.52.0' and r['game_actions']==r['chat_requests']==0
        for name,h in r.get('source_sha256',r.get('source_hashes',{})).items():
            assert sha(name)==h,name;hashes[name.replace('\\','/')]=h
    assert (core['tests_run'],core['current_tests_passed'],core['new_unit_tests'])==(712,642,19)
    assert core['historical_combat_tests_skipped']==70 and core['errors']==core['failures']==0
    assert sha(core['test_log'])==core['test_log_sha256']
    assert core['numeric_public_replay_rerun'] and core['exact_default_public_replays']==732
    assert core['default_public_outputs_unchanged'] and core['deterministic_builds']==2
    assert sha(core['baseline_file'])==core['baseline_file_sha256']
    assert sha(core['baseline_receipt'])==core['baseline_receipt_sha256']
    assert core['char_buff_formulas_unchanged'] and core['data_status_counts_unchanged']
    assert len(ui['cases'])==39 and all(c['passed'] for c in ui['cases'])
    assert ui['private_state_isolated'] and ui['game_captures']==0 and ui['no_automatic_counter_reading_claim']
    assert len(recipient['cases'])==29 and recipient['parents_checked']==7
    assert recipient['private_state_isolated'] and recipient['game_captures']==0
    assert all(c['passed'] for c in recipient['cases'])
    for receipt in (ui,recipient):
        for name,h in receipt['screenshots'].items():assert sha(name)==h,name
    assert (skill['skills_checked'],skill['panel_scenarios'],skill['book_panels'],skill['synthetic_module_panels'])==(87,348,174,18)
    assert skill['private_data_isolated'] and skill['event_input_absent']
    assert sha(skill['refill_screenshot'])==skill['refill_screenshot_sha256']
    backup='.cache/batch-052-before/';manifest=read(backup+'manifest.json')
    assert len(manifest)==11 and all(sha(backup+n)==h for n,h in manifest.items())
    assert not any(n.startswith(('.local/','local-settings')) for n in manifest)
    def methods(src):
        cls=next(c for c in ast.parse(src).body if isinstance(c,ast.ClassDef) and c.name=='MainWindow')
        return {m.name:ast.dump(m,include_attributes=False) for m in cls.body if isinstance(m,ast.FunctionDef)}
    before,after=methods(text(backup+'rouge/app.py')),methods(text('rouge/app.py'))
    assert set(before)==set(after)
    assert {n for n in before if before[n]!=after[n]}=={'__init__'}
    previous=read('FINAL_0.51_VERIFICATION.json')
    untouched=('rouge/run_state.py','rouge/recognition.py','rouge/run_recognition.py','rouge/relic_recognition.py',
        'rouge/damage.py','rouge/estimate.py','rouge/operator_engine.py','rouge/timing.py',
        'rouge/data/battle-map-projections.json','rouge/map_projection.py','rouge/battle_view.py','rouge/map_view.py')
    assert all(sha(n)==previous['source_sha256'][n] for n in untouched)
    research=['relic-creation-052','relic-stack-052','relic-resolution-052','relic-integration-audit-052']
    for name in research:
        folder='.cache/research/'+name+'/'
        m=read(folder+'manifest.json')
        if isinstance(m['files'],dict):
            for n,record in m['files'].items():verify_file(folder+n,record)
        else:
            for record in m['files']:verify_file(record['path'],record)
    stack='.cache/research/relic-stack-052/'
    evidence=read(stack+'evidence.json')
    for record in evidence['original_sources']:verify_file(record['path'],record)
    full=read(evidence['original_sources'][0]['path']);excerpt=read(stack+'template-excerpts.json')
    assert excerpt=={key:full[key] for key in excerpt}
    child={key:next(a['_buff'] for a in value['eventToActions']['ON_BUFF_START'] if 'CreateBuff' in a['$type'])
           for key,value in excerpt.items()}
    assert len({c['buffKey'] for c in child.values()})==3
    assert child['rogue_6_enemy_prob_max_hp']['attributes']['attributeModifiers'][0]['formulaItem']=='MULTIPLIER'
    for key in ('rogue_6_start_3','rogue_6_enemy_layer_multi'):
        assert all(m['formulaItem']=='FINAL_SCALER' for m in child[key]['attributes']['attributeModifiers'])
    failed=read(stack+'before-verification.json')
    assert failed['tests_run']==9 and failed['failing_methods']==6 and failed['failure_records']==12 and failed['errors']==0
    assert failed['source_sha_before']==failed['source_sha_after']
    contract=read('.cache/research/relic-resolution-052/before.json')
    assert contract['tests_run']==7 and contract['failures']==2 and contract['errors']==0
    assert contract['before_sha256']==contract['after_sha256']
    staged=read('.cache/research/relic-resolution-052/current.json')
    assert staged['tests_run']==38 and staged['errors']==staged['failures']==0
    audit=read('.cache/research/relic-integration-audit-052/verification.json')
    assert audit['check_count']==47 and all(c['passed'] for c in audit['checks'])
    assert audit['failures']==audit['errors']==audit['production_writes']==0
    assert audit['source_sha_before']==audit['source_sha_after']
    assert all(sha(n)==h for n,h in audit['source_sha_after'].items())
    assert scope_counts(mechanics())['offline_mechanism_gaps']=={'pending':3,'partial':9}
    progress=text('PROJECT_PROGRESS.md')
    assert '咖啡与未核验生命脚本' in progress and '85个关卡、61张独立原图' in progress
    for token in ('已接入','已完成','验收：','FINAL_0.','## 上批'):assert token not in progress
    old_header='## 0.51 · 库存快照一致性与固定地图扩展'
    assert text('PROJECT_COMPLETED.md').split(old_header,1)[1]==text(backup+'PROJECT_COMPLETED.md').split(old_header,1)[1]
    assert text('WORK_IN_PROGRESS.md').endswith(text(backup+'WORK_IN_PROGRESS.md'))
    assert '# 黑流树海助手 · 0.52' in text('README.md')
    assert tomllib.loads(text('pyproject.toml'))['project']['version']=='0.52.0'
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not (Path.home()/'.codex/automations/1-3/automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/d),quiet=2) for d in ('rouge','scripts','tests'))
    assert launch['version']=='0.52.0' and launch['game_actions']==launch['chat_requests']==0
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
    assert live[0]['title']=='黑流树海助手 0.52 · 识别与计算测试版'
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    hashes['scripts/verify_final_052.py']=sha('scripts/verify_final_052.py')
    artifacts=['RELICS_0.52_VERIFICATION.json','RELIC_UI_0.52_VERIFICATION.json','UI_0.52_VERIFICATION.json',
        'SKILL_UI_0.52_VERIFICATION.json','APP_0.52_LAUNCH_VERIFICATION.json','BATCH_0.52.md',
        'PROJECT_PROGRESS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','README.md',backup+'manifest.json']
    for folder in ['.cache/relics-052','.cache/recipient-052','.cache/relic-composition-052','.cache/mechanisms-052',
                   *['.cache/research/'+n for n in research]]:
        artifacts += [p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    result={'version':'0.52.0','passed':True,'verified_at':time.time(),'current_tests_passed':642,
        'new_unit_tests':19,'historical_combat_tests_skipped':70,'exact_default_public_replays':732,
        'default_public_outputs_unchanged':True,'deterministic_builds':2,'composition_ui_cases':39,
        'recipient_ui_cases':29,'skills_checked':87,'skill_panel_scenarios':348,'book_panels':174,'module_panels':18,
        'independent_adversarial_audit_checks':47,'changed_relic_entries':core['changed_relic_entries'],
        'offline_mechanism_gaps':{'pending':3,'partial':9},'source_sha256':hashes,
        'artifact_sha256':{n:sha(n) for n in sorted(set(artifacts))},'untouched_prior_source_files':list(untouched),
        'prior_map_ui_receipt':'MAP_UI_0.51_VERIFICATION.json','prior_map_ui_receipt_sha256':sha('MAP_UI_0.51_VERIFICATION.json'),
        'map_ui_rerun':False,'all_priority_1_completed':False,'all_priorities_1_to_3_completed':False,
        'process_id':live[0]['pid'],'window_title':live[0]['title'],'test_window_open':True,'foreground_verified':focused,
        'history_count_before':checkpoint['history_count'],'history_count_after':current['history_count'],
        'same_current_run_and_history_preserved':True,'configuration_files_unchanged':2,
        'game_actions':0,'chat_requests':0,'live_measurements':0,'recognition_speed_claim':False,
        'limits':['HP combinations require explicitly confirmed counters and existing static enemy references.',
            'No complete parent lifecycle, automatic counter/recipient reading or current coffee outcome was verified.',
            'Unknown HP scripts, residents, combat triggers and native dynamic phases remain excluded or unknown.']}
    (ROOT/'FINAL_0.52_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('passed','current_tests_passed','exact_default_public_replays',
        'test_window_open','process_id','history_count_before','history_count_after')},ensure_ascii=False))

if __name__=='__main__':main()
