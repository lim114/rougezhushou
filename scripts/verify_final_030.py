"""Assemble observed offline-scope receipts; no capture, chat, or state writes."""
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
from rouge.offline_scope import scope_counts
from rouge.relics import mechanics


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    scope=read('SCOPE_0.30_VERIFICATION.json');ui=read('UI_0.30_VERIFICATION.json')
    launch=read('APP_0.30_LAUNCH_VERIFICATION.json');audit=read('RELIC_VERIFICATION.json')
    assert all(p['version']=='0.30.0' for p in (scope,ui,launch,audit))
    assert scope['tests_failed']==0 and scope['tests_passed']==162 and scope['historical_combat_tests_skipped']==70
    assert scope['numeric_non_interference_cases']==75*87*2 and scope['wine_callback_non_interference_cases']==87*2
    assert scope['scope']==scope_counts(mechanics())==audit['offline_scope']
    assert scope['raw_mechanics_unchanged'] and scope['recognition_unchanged_from_029']
    assert scope['raw_sha256']==digest('rouge/data/relic-mechanics.json')==digest('.cache/batch-030-before/rouge/data/relic-mechanics.json')
    assert scope['recognition_sha256']==digest('rouge/relic_recognition.py')
    assert ui['skills_checked']==87 and ui['reference_items_checked_together']==75
    for flag in ('event_input_removed','unrelated_native_options_hidden','native_defensive_skill_option_preserved',
                 'stable_count_option_preserved','mixed_cost_without_hp_loss','temporary_conditions_not_saved','private_data_isolated'):
        assert ui[flag],flag
    assert audit['audit_count']==272 and audit['public_entry_cases']==8704
    assert audit['bound_recipient_cases']==609 and audit['forbidden_skill_cases']==87
    assert read('TARGET_ICON_VERIFICATION.json')['count']==15
    for p in (scope,ui,audit):
        for name,checksum in p['source_hashes'].items():assert digest(name)==checksum,name
    for flag in ('only_one_project_window','same_run_preserved','history_preserved','settings_and_bindings_unchanged','run_cmd_startup_verified'):
        assert launch[flag],flag
    assert launch['launcher_sha256']==digest('run.cmd')
    checkpoint=read('.cache/upgrade-0.30-checkpoint.json');run=read('.local/run-state.json')
    assert hashlib.sha256(str(run.get('id')).encode()).hexdigest()==checkpoint['run_id_hash']
    assert checkpoint['history_count']==69
    prefix=run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    for name,checksum in checkpoint['config_hashes'].items():assert digest(name)==checksum,name
    live=[]
    def visit(hwnd,_):
        title=win32gui.GetWindowText(hwnd)
        if title.startswith('黑流树海助手'):live.append({'title':title,'pid':win32process.GetWindowThreadProcessId(hwnd)[1]})
    win32gui.EnumWindows(visit,None)
    assert len(live)==1 and '0.30' in live[0]['title'] and live[0]['pid']==launch['process_id'],live
    assert tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']=='0.30.0'
    ended=read('.cache/automation-ended-028.json')
    assert ended['automation_id']=='1-3' and ended['app_delete_result']=='deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert read('.cache/kill-recovery-030-superseded/STATUS.json')['status']=='superseded_by_user_scope_change'
    assert all(compileall.compile_dir(str(ROOT/folder),quiet=2) for folder in ('rouge','scripts','tests'))
    names=('BATCH_0.30.md','PROJECT_PROGRESS.md','WORK_IN_PROGRESS.md','README.md','OUTPUT_FORMAT.md',
           'RELIC_MECHANICS.md','RELIC_COVERAGE.md','SP_EVENT_MODEL.md','scripts/verify_offline_scope_030.py',
           'scripts/verify_offline_scope_ui_030.py','scripts/verify_final_030.py','tests/test_offline_scope_030.py',
           'tests/offline_scope_retirement.py','SCOPE_0.30_VERIFICATION.json','UI_0.30_VERIFICATION.json',
           'APP_0.30_LAUNCH_VERIFICATION.json','RELIC_VERIFICATION.json','TARGET_ICON_VERIFICATION.json',
           '.cache/offline-scope-030/verification.log','.cache/automation-ended-028.json')
    receipt={'version':'0.30.0','passed':True,'verified_at':time.time(),'calculation_scope':'offline_stable_effects',
        'scope':scope['scope'],'current_tests_passed':scope['tests_passed'],
        'historical_combat_tests_skipped':scope['historical_combat_tests_skipped'],
        'numeric_non_interference_cases':scope['numeric_non_interference_cases'],
        'wine_callback_non_interference_cases':scope['wine_callback_non_interference_cases'],
        'skill_ui_cases':87,'public_entry_cases':8704,'bound_recipient_cases':609,'forbidden_skill_cases':87,
        'raw_mechanics_unchanged':True,'recognition_unchanged':True,'process_id':live[0]['pid'],
        'run_cmd_startup_verified':True,'same_run_and_history_preserved':True,
        'history_count_before':checkpoint['history_count'],'history_count_after':len(run['history']),
        'private_configuration_files_verified':len(checkpoint['config_hashes']),
        'automation_id':'1-3','automation_status':'DELETED','all_priorities_1_to_3_completed':False,
        'new_game_actions':0,'chat_requests':0,'new_live_combat_measurements':0,
        'checks':['Public calculator excludes battle-dependent relic numbers and missing event requirements',
            'Mixed relic stable effects retained; scope shared with Qt condition/recipient controls',
            '162 current regressions, 70 explicitly historical skipped assertions not counted as passed',
            '13050 reference-only comparisons and 174 wine combinations',
            '87 isolated UI skills; 8704 public entries, 609 bindings, 87 forbidden skills and 15 icon hashes',
            'Pinned raw data and recognition hashes unchanged; compileall',
            'Actual unique 0.30 run.cmd window; same run, nonempty history and private hashes preserved',
            'Automation deletion and superseded kill-heal archive confirmed'],
        'evidence_sha256':{name:digest(name) for name in names},
        'limits':['Scope reduction is not verification of excluded battle mechanics.',
            '12 offline pending and 9 partial items; skills/environment/map/drop gaps still remain.',
            'No new full-inventory/live-combat/performance measurement; keep existing evidence boundaries.']}
    (ROOT/'FINAL_0.30_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','numeric_non_interference_cases',
        'process_id','history_count_before','history_count_after','automation_status','all_priorities_1_to_3_completed')},ensure_ascii=False))


if __name__=='__main__':main()
