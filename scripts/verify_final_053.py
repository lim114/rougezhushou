"""Seal bounded 0.53 repairs, evidence, regressions and native delivery."""
import ast,compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_launch_053 import windows,verify_process,foreground,state
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts

def read(n):return json.loads((ROOT/n).read_text(encoding='utf-8-sig'))
def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def text(n):return (ROOT/n).read_text(encoding='utf-8')
def functions(n):
    return {f.name:ast.dump(f,include_attributes=False) for f in ast.parse(text(n)).body
            if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef))}

def main():
    core=read('RELICS_0.53_VERIFICATION.json');skill=read('SKILL_UI_0.53_VERIFICATION.json')
    ui=read('HEALING_UI_0.53_VERIFICATION.json');launch=read('APP_0.53_LAUNCH_VERIFICATION.json')
    hashes={}
    for receipt in (core,skill,ui):
        assert receipt['passed'] and receipt['version']=='0.53.0'
        assert receipt['game_actions']==receipt['chat_requests']==0
        for name,h in receipt.get('source_sha256',receipt.get('source_hashes',{})).items():
            assert sha(name)==h,name;hashes[name.replace('\\','/')]=h
    assert (core['tests_run'],core['current_tests_passed'],core['new_unit_tests'])==(740,670,28)
    assert core['historical_combat_tests_skipped']==70 and core['errors']==core['failures']==0
    assert sha(core['test_log'])==core['test_log_sha256']
    assert core['numeric_public_replay_rerun'] and core['exact_default_public_replays']==732
    assert core['default_public_outputs_unchanged'] and core['mechanic_data_unchanged']
    for key in ('baseline_file','baseline_receipt','prior_build_receipt'):
        assert sha(core[key])==core[key+'_sha256']
    assert not core['deterministic_build_rerun'] and core['data_status_counts_unchanged']
    assert (skill['skills_checked'],skill['panel_scenarios'],skill['book_panels'],skill['synthetic_module_panels'])==(87,348,174,18)
    assert skill['private_data_isolated'] and skill['event_input_absent']
    assert sha(skill['refill_screenshot'])==skill['refill_screenshot_sha256']
    assert ui['cases']=={'full_skill_cases':10,'cap_clamp_cases':2,'window_cases':20,
                         'unknown_combo_cases':5,'unrelated_panel_cases':9}
    assert sum(ui['cases'].values())==46
    assert ui['private_data_isolated'] and ui['game_captures']==0
    assert ui['ui_recipient_caps']=={'1':1,'3':2}
    for k in ('public_total_matches_window','rose_applied_once','known_zero_retained',
              'explicit_frames_and_delayed_boundary','unknown_combinations_not_guessed','inapplicable_panels_hidden'):
        assert ui[k]
    assert ui['source_hashes']==ui['source_hashes_after']
    assert sha(ui['screenshot'])==ui['screenshot_sha256']
    backup='.cache/batch-053-before/';manifest=read(backup+'manifest.json')
    assert len(manifest)==10 and all(sha(backup+n)==h for n,h in manifest.items())
    assert not any(n.startswith(('.local/','local-settings')) for n in manifest)
    for name,expected in (('rouge/damage.py',{'_evaluate_damage'}),('rouge/relic_recognition.py',{'_match_bar'})):
        before,after=functions(backup+name),functions(name)
        assert set(before)==set(after)
        assert {k for k in before if before[k]!=after[k]}==expected,name
    def methods(source):
        cls=next(c for c in ast.parse(source).body if isinstance(c,ast.ClassDef) and c.name=='MainWindow')
        return {m.name:ast.dump(m,include_attributes=False) for m in cls.body if isinstance(m,ast.FunctionDef)}
    before,after=methods(text(backup+'rouge/app.py')),methods(text('rouge/app.py'))
    assert set(before)==set(after) and {n for n in before if before[n]!=after[n]}=={'__init__'}
    research=('inventory-catalog-053','mechanism-audit-053','rune-sources-053')
    for folder in research:
        paths=[f'.cache/research/{folder}/manifest.json']
        if folder=='mechanism-audit-053':paths.append(f'.cache/research/{folder}/after-manifest.json')
        for path in paths:
            record=read(path)
            for entry in record['files']:
                data=(ROOT/entry['path']).read_bytes()
                assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'],entry['path']
            if 'original_manifest_preserved_sha256' in record:
                assert record['original_manifest_preserved_sha256']==sha(paths[0])
    inventory='.cache/research/inventory-catalog-053/'
    red=read(inventory+'before-final.json');after=read(inventory+'after.json')
    assert red['tests']['run']==11 and len(red['tests']['failures'])==3 and not red['tests']['errors']
    assert red['source_unchanged'] and red['test_sha256']==sha('tests/test_inventory_catalog_053.py')
    assert after['tests']['run']==after['tests']['passed']==45 and after['tests']['failed_methods']==after['tests']['errors']==0
    assert after['source_unchanged'] and after['test_sha256']==sha('tests/test_inventory_catalog_053.py')
    assert after['source_sha256']==after['source_after_sha256']
    for n,h in after['source_sha256'].items():assert sha(n)==h,n
    mechanism='.cache/research/mechanism-audit-053/'
    red=read(mechanism+'before.json');after=read(mechanism+'after.json')
    assert red['tests_run']==17 and red['failed_methods']==2 and red['failures']==6 and red['errors']==0
    assert red['source_unchanged'] and red['source_sha_before']==red['source_sha_after']
    assert after['passed'] and after['tests_run']==17 and after['failures']==after['errors']==0
    assert after['source_unchanged'] and after['only_changed_damage_function_vs_public_052_baseline']==['_evaluate_damage']
    for n,entry in after['source_sha_after'].items():assert sha(n)==entry['sha256'],n
    assert scope_counts(mechanics())['offline_mechanism_gaps']=={'pending':3,'partial':9}
    previous=read('FINAL_0.52_VERIFICATION.json')
    untouched=('rouge/estimate.py','rouge/operator_engine.py','rouge/timing.py','rouge/relics.py',
        'rouge/run_modifiers.py','rouge/reporting.py','rouge/run_state.py','rouge/recognition.py',
        'rouge/run_recognition.py','rouge/data/relic-mechanics.json','rouge/data/battle-map-projections.json',
        'rouge/map_projection.py','rouge/map_view.py','rouge/battle_view.py')
    assert all(sha(n)==previous['source_sha256'][n] for n in untouched)
    progress=text('PROJECT_PROGRESS.md')
    assert progress==text(backup+'PROJECT_PROGRESS.md')
    for token in ('已接入','已完成','验收：','FINAL_0.','## 上批'):assert token not in progress
    marker='## 0.52 · 已确认生命乘区组合与适用范围'
    assert text('PROJECT_COMPLETED.md').split(marker,1)[1]==text(backup+'PROJECT_COMPLETED.md').split(marker,1)[1]
    assert text('WORK_IN_PROGRESS.md').endswith(text(backup+'WORK_IN_PROGRESS.md'))
    assert '# 黑流树海助手 · 0.53' in text('README.md')
    assert tomllib.loads(text('pyproject.toml'))['project']['version']=='0.53.0'
    assert read('.cache/automation-ended-028.json')['app_delete_result']=='deleted'
    assert not (Path.home()/'.codex/automations/1-3/automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT/d),quiet=2) for d in ('rouge','scripts','tests'))
    assert launch['version']=='0.53.0' and launch['game_actions']==launch['chat_requests']==0
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
    assert live[0]['title']=='黑流树海助手 0.53 · 识别与计算测试版'
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    hashes['scripts/verify_final_053.py']=sha('scripts/verify_final_053.py')
    artifacts=['RELICS_0.53_VERIFICATION.json','SKILL_UI_0.53_VERIFICATION.json','HEALING_UI_0.53_VERIFICATION.json',
        'APP_0.53_LAUNCH_VERIFICATION.json','BATCH_0.53.md','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md',
        'WORK_IN_PROGRESS.md','README.md',backup+'manifest.json',launch['checkpoint']]
    for folder in ('.cache/relics-053','.cache/healing-ui-053','.cache/mechanisms-053',
                   *['.cache/research/'+n for n in research]):
        artifacts += [p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts]
    receipt={'version':'0.53.0','passed':True,'verified_at':time.time(),'current_tests_passed':670,
        'new_unit_tests':28,'historical_combat_tests_skipped':70,'exact_default_public_replays':732,
        'default_public_outputs_unchanged':True,'skills_checked':87,'skill_panel_scenarios':348,
        'book_panels':174,'module_panels':18,'healing_ui_cases':46,'independent_related_inventory_tests':45,
        'offline_mechanism_gaps':{'pending':3,'partial':9},'source_sha256':hashes,
        'artifact_sha256':{n:sha(n) for n in sorted(set(artifacts))},'untouched_prior_source_files':list(untouched),
        'prior_composition_ui_receipt':'RELIC_UI_0.52_VERIFICATION.json',
        'prior_composition_ui_receipt_sha256':sha('RELIC_UI_0.52_VERIFICATION.json'),
        'composition_ui_rerun':False,'recipient_ui_rerun':False,'map_ui_rerun':False,
        'all_priority_1_completed':False,'all_priorities_1_to_3_completed':False,
        'process_id':live[0]['pid'],'window_title':live[0]['title'],'test_window_open':True,
        'foreground_verified':focused,'history_count_before':checkpoint['history_count'],
        'history_count_after':current['history_count'],'same_current_run_and_history_preserved':True,
        'configuration_files_unchanged':2,'game_actions':0,'chat_requests':0,'live_measurements':0,
        'recognition_speed_claim':False,'new_formula_claim':False,
        'limits':['Only already eligible candidates expand existing artwork families; no live completeness or speed claim.',
            'Public Kaltsit S1/S3 window healing aligned; internal recipient/timing formulas unchanged.',
            'Missing rune creation chains, recipient reading, counters and multi-page inventory remain unknown.']}
    (ROOT/'FINAL_0.53_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','exact_default_public_replays',
        'healing_ui_cases','test_window_open','process_id','history_count_before','history_count_after')}))

if __name__=='__main__':main()
