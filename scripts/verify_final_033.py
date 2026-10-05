"""Final 0.33 checks: bounded spawn branches, unchanged clocks and open app."""
import compileall,hashlib,json,sys,time,tomllib
from pathlib import Path
import win32gui,win32process

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts,partition


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    calculation=read('RELIC_0.33_VERIFICATION.json');ui=read('UI_0.33_VERIFICATION.json')
    launch=read('APP_0.33_LAUNCH_VERIFICATION.json');audit=read('RELIC_VERIFICATION.json')
    evidence=read('.cache/research/relics-033/evidence.json');data=mechanics()
    assert all(p['version']=='0.33.0' for p in (calculation,ui,launch,audit,evidence))
    assert calculation['passed'] and calculation['failures']==calculation['errors']==0
    assert calculation['current_tests_passed']==230 and calculation['new_tests']==17
    assert calculation['tests_run']==300 and calculation['historical_combat_tests_skipped']==len(calculation['skipped_tests'])==70
    assert calculation['skill_environment_cases']==1044 and calculation['hp_combination_cases']==870
    assert digest(calculation['test_log'])==calculation['test_log_sha256']
    expected_scope={'items':{'reference_only':75,'mixed':4,'offline':193},
        'offline_mechanism_gaps':{'pending':11,'partial':8}}
    assert scope_counts(data)==calculation['offline_scope']==audit['offline_scope']==expected_scope
    assert data['counts']==calculation['data_rule_counts']==audit['data_rule_counts']=={
        'numeric':119,'conditional':28,'partial':11,'pending':62,'non_output':52}
    active=[(r,p) for r,p in data['relics'].items() if partition(p,r)[0]]
    assert len(active)==134 and sum(not partition(p,r)[2] for r,p in active)==126
    before=read('.cache/batch-033-before/rouge/data/relic-mechanics.json')
    changed=[r for r in before['relics'] if before['relics'][r]!=data['relics'][r]]
    assert set(before['relics'])==set(data['relics'])
    assert changed==calculation['changed_relic_ids']==evidence['changed_relic_ids']==['rogue_6_relic_fight_25']
    assert before['char_buffs']==data['char_buffs']
    assert all(before['relics'][r]['raw_buffs']==data['relics'][r]['raw_buffs'] for r in data['relics'])
    assert digest('.cache/game-data/roguelike_topic_table.json')==data['source_sha256']==evidence['source_sha256']==audit['source_sha256']
    assert data['commit']==evidence['source_commit']==audit['source_commit']
    assert evidence['decoded_spawn_parameters']=={'key':'rogue_6_enemy_prob_max_hp','prob':.03,'max_hp':1}
    previous=read('FINAL_0.32_VERIFICATION.json')
    recognition_names=('rouge/relic_recognition.py','rouge/run_state.py','rouge/run_config.py',
        'rouge/run_recognition.py','rouge/recognition.py','rouge/visual_recognition.py',
        'rouge/data/run-config.json','rouge/data/relic-reference-equivalence.json')
    for name in recognition_names:assert digest(name)==previous['source_sha256'][name],name
    previous_audit=read('.cache/batch-033-before/RELIC_VERIFICATION.json')
    clock_names=('rouge/timing.py','rouge/sp_events.py','rouge/damage.py','rouge/operator_engine.py',
        'rouge/estimate.py','rouge/deployment.py','rouge/offline_scope.py','rouge/catalog.py')
    for name in clock_names:assert digest(name)==previous_audit['source_hashes'][name],name
    app_before=(ROOT/'.cache/batch-033-before/rouge/app.py').read_text(encoding='utf-8')
    assert (ROOT/'rouge/app.py').read_text(encoding='utf-8')==app_before.replace(
        '黑流树海助手 0.32 · 识别与计算测试版','黑流树海助手 0.33 · 识别与计算测试版')
    assert ui['passed'] and ui['skills_checked']==ui['spawn_variant_sections']==ui['hp_combination_unknown_sections']==87
    for flag in ('unrelated_sections_hidden','native_options_appropriate','no_spawn_input_or_sampling',
        'event_input_absent','private_data_isolated'):assert ui[flag],flag
    assert audit['audit_count']==272 and audit['public_entry_cases']==8704
    assert audit['bound_recipient_cases']==609 and audit['forbidden_skill_cases']==87
    icons=read('TARGET_ICON_VERIFICATION.json');assert icons['count']==len(icons['icons'])==15
    for icon in icons['icons']:assert digest('rouge/data/'+icon['file'])==icon['sha256']
    source_hashes={}
    for receipt in (calculation,ui,audit):
        for name,checksum in receipt['source_hashes'].items():
            assert digest(name)==checksum,name
            source_hashes[name]=checksum
    for name in recognition_names+clock_names:source_hashes[name]=digest(name)
    for name in ('scripts/verify_relic_mechanics.py','scripts/verify_final_033.py',
        'scripts/verify_launch_033.py','pyproject.toml'):source_hashes[name]=digest(name)
    for receipt in (calculation,ui,launch):assert receipt['game_actions']==receipt['chat_requests']==0
    for flag in ('only_one_project_window','window_visible_and_restored','same_run_preserved',
        'history_preserved','settings_and_bindings_unchanged','run_cmd_startup_verified'):assert launch[flag],flag
    assert launch['launcher_sha256']==digest('run.cmd')
    checkpoint=read('.cache/upgrade-0.33-checkpoint.json');run=read('.local/run-state.json')
    assert hashlib.sha256(str(run.get('id')).encode()).hexdigest()==checkpoint['run_id_hash']
    assert checkpoint['history_count']>0
    prefix=run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    for name,checksum in checkpoint['config_hashes'].items():assert digest(name)==checksum,name
    live=[]
    def visit(hwnd,_):
        title=win32gui.GetWindowText(hwnd)
        if title.startswith('黑流树海助手'):
            live.append({'title':title,'pid':win32process.GetWindowThreadProcessId(hwnd)[1],
                'visible':win32gui.IsWindowVisible(hwnd)})
    win32gui.EnumWindows(visit,None)
    assert len(live)==1 and '0.33' in live[0]['title'] and live[0]['pid']==launch['process_id'] and live[0]['visible'],live
    assert tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']=='0.33.0'
    ended=read('.cache/automation-ended-028.json')
    assert ended['automation_id']=='1-3' and ended['app_delete_result']=='deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert read('.cache/kill-recovery-030-superseded/STATUS.json')['status']=='superseded_by_user_scope_change'
    assert all(compileall.compile_dir(str(ROOT/f),quiet=2) for f in ('rouge','scripts','tests'))
    names=('BATCH_0.33.md','PROJECT_PROGRESS.md','WORK_IN_PROGRESS.md','README.md','RELIC_COVERAGE.md',
        'RELIC_0.33_VERIFICATION.json','UI_0.33_VERIFICATION.json','APP_0.33_LAUNCH_VERIFICATION.json',
        'RELIC_VERIFICATION.json','TARGET_ICON_VERIFICATION.json','.cache/research/relics-033/evidence.json',
        calculation['test_log'],'.cache/relic-033-before.log','.cache/automation-ended-028.json')
    receipt={'version':'0.33.0','passed':True,'verified_at':time.time(),
        'calculation_scope':'offline_stable_effects','scope':expected_scope,'active_relic_rules':134,
        'current_tests_passed':230,'new_tests':17,'historical_combat_tests_skipped':70,
        'skill_environment_cases':1044,'hp_combination_cases':870,'skill_ui_cases':87,
        'public_entry_cases':8704,'bound_recipient_cases':609,'forbidden_skill_cases':87,'bound_icon_hashes':15,
        'changed_relic_ids':changed,'raw_buffs_and_char_buffs_unchanged':True,
        'recognition_unchanged_from_032':True,'attack_and_sp_clocks_unchanged':True,
        'process_id':live[0]['pid'],'test_window_open':True,'run_cmd_startup_verified':True,
        'same_run_and_history_preserved':True,'history_count_before':checkpoint['history_count'],
        'history_count_after':len(run['history']),'private_configuration_files_verified':len(checkpoint['config_hashes']),
        'automation_id':'1-3','automation_status':'DELETED','all_priorities_1_to_3_completed':False,
        'new_game_actions':0,'chat_requests':0,'new_live_combat_measurements':0,
        'checks':['Pinned 3% per-enemy source probability and isolated 2x HP branch',
            'Unobserved current spawn; no averaged actual HP, independent-draw or death-time assumptions',
            'Unknown other-HP combinations, inapplicable selectors and resident HP cross-key guard',
            '230 related regressions, 1044 output references, 870 HP combinations and 87 isolated UI skills',
            '8704 entries, 609 bindings, 87 forbidden skills, 15 icon hashes and compileall',
            'Unchanged 0.32 recognition/attack-SP clocks, same nonempty run history and private settings',
            'Unique visible 0.33 run.cmd test window; automation remains deleted'],
        'source_sha256':source_hashes,'evidence_sha256':{n:digest(n) for n in names},
        'limits':calculation['limits']+['11 offline pending and 8 data-partial items; priorities 1-3 remain incomplete.',
            'No new recognition performance, full-inventory accuracy or live-combat calibration.']}
    (ROOT/'FINAL_0.33_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','skill_ui_cases','process_id',
        'test_window_open','history_count_before','history_count_after','automation_status',
        'all_priorities_1_to_3_completed')},ensure_ascii=False))


if __name__=='__main__':main()
