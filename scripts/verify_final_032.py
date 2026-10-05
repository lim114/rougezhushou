"""Check final 0.32 evidence, source provenance and the user's open test window."""
import compileall
import hashlib
import json
import sys
import time
import tomllib
from pathlib import Path

import win32gui
import win32process

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.offline_scope import partition,scope_counts
from rouge.relics import mechanics


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    recognition=read('RECOGNITION_0.32_VERIFICATION.json')
    ui=read('UI_0.32_VERIFICATION.json')
    launch=read('APP_0.32_LAUNCH_VERIFICATION.json')
    audit=read('RELIC_VERIFICATION.json')
    evidence=read('.cache/research/relics-032/evidence.json')
    assert all(r['version']=='0.32.0' for r in (recognition,ui,launch,audit,evidence))
    assert recognition['passed'] and recognition['failures']==recognition['errors']==0
    assert recognition['test_scope']=='current_source_targeted'
    assert recognition['tests_run']==recognition['current_tests_passed']==40
    assert recognition['new_tests']==26 and recognition['historical_combat_tests_skipped']==0
    assert digest(recognition['test_log'])==recognition['test_log_sha256']
    prior=recognition['full_regression_before_final_guards']
    full=read(prior['receipt']);assert full['passed'] and digest(prior['receipt'])==prior['sha256']
    assert full['tests_run']==404 and full['current_tests_passed']==334
    assert full['historical_combat_tests_skipped']==70 and full['failures']==full['errors']==0
    assert digest(full['test_log'])==full['test_log_sha256']
    changed=[n for n,h in full['source_hashes'].items() if digest(n)!=h]
    assert changed==prior['changed_source_files_since_full_suite']
    assert set(changed)=={'rouge/run_state.py','rouge/run_config.py','scripts/verify_relic_grade_sync_032.py'}
    for name,checksum in full['test_module_sha256'].items():
        assert digest(name.replace('.','/')+'.py')==checksum,name
    source_hashes={}
    for receipt in (recognition,ui,audit):
        for name,checksum in receipt['source_hashes'].items():
            assert digest(name)==checksum,name
            source_hashes[name]=checksum
    assert digest('.cache/game-data/roguelike_topic_table.json')==evidence['source_sha256']==audit['source_sha256']
    primary=read('.cache/game-data/roguelike_topic_table.json')['details']['rogue_6']
    config=read('rouge/data/run-config.json')
    assert primary['difficultyUpgradeRelicGroups']==evidence['groups']==config['difficulty_upgrade_relic_groups']
    assert digest('rouge/data/run-config.json')==evidence['derived_config_sha256']
    assert digest('rouge/data/relic-reference-equivalence.json')==evidence['artwork_equivalence_sha256']
    labels={k:v.split('：',1)[0] for k,v in primary['detailConst']['difficultyUpgradeRelicDescTable'].items()}
    assert labels==evidence['tier_labels']==config['difficulty_upgrade_relic_labels']
    assert len(evidence['groups'])==recognition['difficulty_groups']==13
    equivalents=read('rouge/data/relic-reference-equivalence.json')['families']
    for family in evidence['groups'].values():
        entries=sorted(family['relicData'],key=lambda r:r['equivalentGrade'])
        assert [r['equivalentGrade'] for r in entries]==[0,3,6,9]
        assert {r['relicId'] for r in entries}==set(equivalents[entries[0]['relicId']]['ids'])
    assert sum(len(g['relicData']) for g in evidence['groups'].values())==recognition['family_variants']==52
    assert recognition['grade_cases']==208 and evidence['extra_equivalent_variants']==39
    assert len(recognition['paired_replays'])==2
    for row in recognition['paired_replays']:
        assert row['trials']==3 and len(row['without_run_memory_ms'])==len(row['with_run_memory_ms'])==3
        assert row['semantic_equal'] and row['original_config_timestamps_preserved']
        assert row['badge_searches_before']==3 and row['badge_searches_after']==0
        assert min(row['without_run_memory_ms']+row['with_run_memory_ms'])>0
    assert recognition['explicit_visible_panel_overrides_memory']
    data=mechanics();previous=read('FINAL_0.31_VERIFICATION.json')
    assert digest('rouge/data/relic-mechanics.json')==previous['source_sha256']['rouge/data/relic-mechanics.json']
    assert digest('rouge/offline_scope.py')==previous['source_sha256']['rouge/offline_scope.py']
    expected_scope={'items':{'reference_only':75,'mixed':4,'offline':193},
        'offline_mechanism_gaps':{'pending':11,'partial':9}}
    assert scope_counts(data)==audit['offline_scope']==expected_scope
    assert data['counts']==audit['data_rule_counts']=={
        'numeric':118,'conditional':28,'partial':12,'pending':62,'non_output':52}
    active=[(rid,p) for rid,p in data['relics'].items() if partition(p,rid)[0]]
    assert len(active)==134 and sum(not partition(p,rid)[2] for rid,p in active)==125
    assert ui['passed'] and ui['skills_checked']==87
    for flag in ('late_grade_updates_ui_and_calculation','corrected_grade_replaces_tier_once',
        'tier_label_visible','history_preserved','reset_clears_run_context_and_icon_memory',
        'native_options_appropriate','event_input_absent','private_data_isolated'):
        assert ui[flag],flag
    assert audit['audit_count']==272 and audit['public_entry_cases']==8704
    assert audit['bound_recipient_cases']==609 and audit['forbidden_skill_cases']==87
    icons=read('TARGET_ICON_VERIFICATION.json');assert icons['count']==len(icons['icons'])==15
    for icon in icons['icons']:assert digest('rouge/data/'+icon['file'])==icon['sha256']
    for receipt in (recognition,ui,launch):
        assert receipt['chat_requests']==receipt['game_actions']==0
    for flag in ('only_one_project_window','window_visible_and_restored','same_run_preserved',
        'history_preserved','settings_and_bindings_unchanged','run_cmd_startup_verified'):
        assert launch[flag],flag
    assert launch['launcher_sha256']==digest('run.cmd')
    checkpoint=read('.cache/upgrade-0.32-checkpoint.json');run=read('.local/run-state.json')
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
    assert len(live)==1 and '0.32' in live[0]['title'] and live[0]['pid']==launch['process_id'],live
    assert live[0]['visible']
    assert tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']=='0.32.0'
    ended=read('.cache/automation-ended-028.json')
    assert ended['automation_id']=='1-3' and ended['app_delete_result']=='deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert read('.cache/kill-recovery-030-superseded/STATUS.json')['status']=='superseded_by_user_scope_change'
    assert all(compileall.compile_dir(str(ROOT/folder),quiet=2) for folder in ('rouge','scripts','tests'))
    names=('BATCH_0.32.md','PROJECT_PROGRESS.md','WORK_IN_PROGRESS.md','README.md',
        'OUTPUT_FORMAT.md','RELIC_MECHANICS.md','RELIC_COVERAGE.md','pyproject.toml',
        'scripts/verify_final_032.py','scripts/verify_launch_032.py',
        'RECOGNITION_0.32_VERIFICATION.json','UI_0.32_VERIFICATION.json',
        'APP_0.32_LAUNCH_VERIFICATION.json','RELIC_VERIFICATION.json','TARGET_ICON_VERIFICATION.json',
        '.cache/research/relics-032/evidence.json',full['test_log'],recognition['test_log'],
        prior['receipt'],'.cache/relic-032/guards-before.log','.cache/automation-ended-028.json')
    receipt={'version':'0.32.0','passed':True,'verified_at':time.time(),
        'calculation_scope':'offline_stable_effects','scope':expected_scope,'active_relic_rules':134,
        'full_regression_before_final_guards':{'current_tests_passed':334,'historical_skipped':70,
            'tests_run':404,'receipt':prior['receipt'],'changed_source_files':changed},
        'current_source_targeted_tests_passed':40,'new_tests':26,
        'difficulty_groups':13,'family_variants':52,'grade_cases':208,
        'paired_replays':recognition['paired_replays'],'explicit_visible_panel_overrides_memory':True,
        'skill_ui_cases':87,'public_entry_cases':8704,'bound_recipient_cases':609,
        'forbidden_skill_cases':87,'bound_icon_hashes':15,
        'mechanics_and_char_buffs_unchanged':True,'primary_source_unchanged':True,
        'process_id':live[0]['pid'],'test_window_open':True,'run_cmd_startup_verified':True,
        'same_run_and_history_preserved':True,'history_count_before':checkpoint['history_count'],
        'history_count_after':len(run['history']),'private_configuration_files_verified':len(checkpoint['config_hashes']),
        'automation_id':'1-3','automation_status':'DELETED','all_priorities_1_to_3_completed':False,
        'new_game_actions':0,'chat_requests':0,'new_live_capture_measurements':0,
        'checks':['13 pinned shared-art families with 4 grade tiers; late/corrected grade reaches UI and calculation',
            'Confirmed same-run settings reuse; fresh explicit evidence overrides; old-run results rejected',
            'Historical badge geometry omitted; exact-frame cache separated by run and meaningful config',
            '334 full passes before final guards, followed by 40 final-source targeted passes; totals not added',
            '87 isolated UI skills; 8704 entries, 609 bindings, 87 forbidden skills, 15 icon hashes and compileall',
            'Unique visible 0.32 run.cmd window, nonempty same-run history and private hashes',
            'Automation remains deleted; offline scope and priorities remaining are preserved'],
        'evidence_sha256':{name:digest(name) for name in names},'source_sha256':source_hashes,
        'limits':recognition['limits']+['11 offline pending and 9 partial items; priorities 1-3 remain incomplete.',
            'No new full-inventory accuracy or live-combat calibration.']}
    (ROOT/'FINAL_0.32_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_source_targeted_tests_passed',
        'skill_ui_cases','process_id','test_window_open','history_count_before','history_count_after',
        'automation_status','all_priorities_1_to_3_completed')},ensure_ascii=False))


if __name__=='__main__':main()
