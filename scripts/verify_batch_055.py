"""Consolidate sealed checks without replaying private state or game inputs."""
import hashlib,json,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.offline_scope import scope_counts
from rouge.relics import mechanics


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def write(name,data):
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')


def main():
    core=read('CORE_0.55_VERIFICATION.json')
    assert core['passed'] and core['tests_run']>922 and core['current_tests_passed']>852
    assert core['historical_tests_skipped']==70 and core['failures']==core['errors']==0
    assert not core['source_drift_during_tests']
    assert all(sha(n)==h for n,h in core['source_sha256'].items())
    for name,key in (('SKILL_UI_0.55_VERIFICATION.json','source_hashes'),
                     ('NATIVE_UI_0.55_VERIFICATION.json','source_sha256')):
        ui=read(name);assert ui['passed']
        assert all(sha(n)==h for n,h in ui[key].items())
    launch=read('APP_0.55_LAUNCH_VERIFICATION.json')
    for key in ('only_one_project_window','window_visible_and_restored',
                'same_run_preserved','history_preserved','settings_and_bindings_unchanged',
                'run_cmd_startup_verified'):
        assert launch[key],key
    assert launch['chat_requests']==launch['game_actions']==0
    assert all(c['visible_and_responsive'] for c in launch['stability_checks'])

    directory='.cache/research/p1-live-recipient-055/'
    cases=[]
    for filename,oid,buffs in (
        ('receipt-1791126961478703800.json','kaltsit',['rogue_6_from_relic_6']),
        ('receipt-1791127302045231200.json','char_1050_chen3',['rogue_6_from_relic_14'])):
        name=directory+filename;receipt=read(name)
        assert receipt['foreground_unchanged'] and receipt['no_game_input_chat_or_actual_runstate_access']
        assert sha(receipt['image'])==receipt['image_sha256']
        run=receipt['run'];member=next(m for m in run['operators'] if m['id']==oid)
        assert run['selected_operator']==oid
        assert member['char_buff_ids']==buffs and member['char_buffs_complete'] is True
        restored=receipt['temporary_state_restored_buffs'][oid]
        assert restored['char_buff_ids']==buffs and restored['char_buffs_complete'] is True
        assert all(receipt['temporary_merge_preservation'].values())
        cases.append({'receipt':name,'sha256':sha(name),'operator_id':oid,
            'buff_ids':buffs,'complete':True,'temporary_save_restore_verified':True,
            'full_read_ms':receipt['elapsed_ms'],'stage_scope':'Original live stage retained; normal path covered by current regression.'})
    for filename,oid,buffs in (
        ('cached-pair-1791129741668048800-receipt.json','char_1043_leizi2',['rogue_6_from_relic_3']),
        ('cached-pair-1791132335648665700-receipt.json','char_151_myrtle',['rogue_6_from_relic_1','rogue_6_from_relic_13'])):
        name=directory+filename;receipt=read(name)
        assert receipt['foreground_unchanged'] and receipt['no_game_input_chat_or_actual_runstate_access']
        temporary=receipt['temporary_state']
        assert temporary['state_and_fixture_created_before_original_captures']
        assert temporary['apply_times_are_original_capture_times']
        assert all(row['accepted'] for row in temporary['applied'])
        assert temporary['prior_unselected_fixture_buff_preserved']
        assert temporary['prior_unobserved_fixture_gold_preserved']
        restored=temporary['selected_member']
        assert restored['char_buff_ids']==buffs and restored['char_buffs_complete'] is True
        for frame in receipt['frames']:
            assert sha(frame['image'])==frame['image_sha256']
            visible=frame['visible_result'];member=visible['member']
            assert visible['selected_operator']==oid
            assert member['char_buff_ids']==buffs and member['char_buffs_complete'] is True
        cases.append({'receipt':name,'sha256':sha(name),'operator_id':oid,
            'buff_ids':buffs,'complete':True,'temporary_save_restore_verified':True,
            'original_capture_times_accepted':True,'full_read_ms':[f['elapsed_ms'] for f in receipt['frames']],
            'stage_scope':'Two new actual WGC frames, exact current owner and full popup proof.'})
    freeze_name=directory+'snack-reading-freeze-1791132776362341800.json'
    freeze=read(freeze_name)
    assert freeze['source_stable_during_actual_pair']
    for name,digest in freeze['source_hashes'].items():
        if name=='rouge/run_state.py':
            assert sha('.cache/origin-discovery-055-before/'+name)==digest
        else:assert sha(name)==digest
    reading={'version':'0.55.0','passed':True,'live_positive_cases':cases,
        'latest_reading_freeze':freeze_name,'latest_reading_freeze_sha256':sha(freeze_name),
        'source_sha256':{n:sha(n) for n in freeze['source_hashes']},'live_reading_is_background_only':True,
        'same_wgc_readers_after_state_fix':True,
        'state_fix_scope':'Current CORE separately verifies origin discovery and strictly bounded same-run history recovery. Original WGC source freeze is retained.',
        'all_page_performance_verified':False,'gray_counter_independent_positive_verified':False,
        'zero_popup_layout_verified':False,'all_recipient_lifecycles_verified':False,
        'unknown_partial_reads_preserve_previous_memory':True,'private_state_writes_by_verifier':0,
        'game_actions':0,'chat_requests':0,'all_priority_1_completed':False,
        'scope':'Four actual recipient pages and strict layout contracts. Public training images/scales are not independent holdouts.'}
    write('READING_0.55_VERIFICATION.json',reading)

    origin_freeze_name='.cache/research/p1-origin-discovery-055/freeze.json'
    origin_freeze=read(origin_freeze_name)
    assert origin_freeze['tests']['final_new']['tests']==19
    assert origin_freeze['tests']['final_new']['passed']
    for name,digest in origin_freeze['source_sha256'].items():assert sha(name)==digest
    for name,digest in origin_freeze['receipt_sha256'].items():
        assert sha('.cache/research/p1-origin-discovery-055/'+name)==digest
    origin_review_name='.cache/research/p1-origin-independent-055/review.json'
    origin_review=read(origin_review_name)
    assert origin_review['result']=='pass' and origin_review['source_frozen']
    assert all(origin_review['static_findings'].values())
    for name,digest in origin_review['source_sha256_after'].items():assert sha(name)==digest

    # Inspect hashes/prefixes only. A newly started current run must never be
    # repopulated with the original live recipient case from a previous run.
    run=read('.local/run-state.json')
    initial=read('.cache/upgrade-0.55-checkpoint.json')
    checkpoint=read(launch['checkpoint'])
    current_id=hashlib.sha256(str(run.get('id')).encode()).hexdigest()
    same_patch_run=current_id==checkpoint['run_id_hash']
    changed_since_initial=current_id!=initial['run_id_hash']
    if same_patch_run:
        prefix=run.get('history',[])[:checkpoint['history_count']]
        assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    assert all(sha(n)==digest for n,digest in checkpoint['config_hashes'].items())
    historical_live='.cache/origin-discovery-055-before/LIVE_APP_0.55_RECIPIENT_VERIFICATION.json'
    original_case=read(historical_live)
    assert original_case['passed'] and original_case['complete']
    assert original_case['operator_id']=='char_151_myrtle'
    assert original_case['buff_ids']==['rogue_6_from_relic_1','rogue_6_from_relic_13']
    from scripts.verify_launch_055 import windows
    current_windows=windows()
    assert len(current_windows)==1 and current_windows[0]['pid']==launch['process_id']
    current_window=current_windows[0]
    assert current_window['visible'] and not current_window['minimized'] and not current_window['hung']
    live_app={'version':'0.55.0','passed':True,'verified_at':time.time(),
        'same_run_as_latest_restart_checkpoint':same_patch_run,
        'changed_since_initial_upgrade':changed_since_initial,
        'latest_checkpoint_history_prefix_preserved':True if same_patch_run else None,
        'current_history_count':len(run.get('history',[])),
        'settings_and_bindings_unchanged':True,'test_window_visible_and_responsive':True,
        'process_id':current_window['pid'],
        'historical_myrtle_live_case_receipt':historical_live,
        'historical_myrtle_live_case_sha256':sha(historical_live),
        'historical_myrtle_ownership_observed_at_original_stage':True,
        'actual_origin_bug_repair_on_original_run_verified':False,
        'origin_fix_isolated_and_independent_tests_pass':True,
        'verification_read_only':True,'verifier_state_writes':0,
        'prior_run_data_restored_by_verifier':False,
        'scope':'Current run and latest restart are checked separately from the original recipient stage. That earlier run changed before patch restart; original-run repair was not live-tested. No private runtime snapshot is copied.'}
    write('LIVE_APP_0.55_RUN_VERIFICATION.json',live_app)

    independent='.cache/research/p1-ammo-independent-055/epoch-4/receipt.json'
    audit=read(independent)
    assert audit['result']=='pass' and audit['source_frozen_through_metadata_audit_ammo_and_tests']
    assert audit['metadata_only_six_pending_string_changes']
    assert all(sha(n)==h for n,h in audit['production_sha256_after'].items())
    replay='PUBLIC_REPLAY_0.55_VERIFICATION.json';replayed=read(replay)
    assert replayed['passed'] and replayed['replays']==732
    assert replayed['exact_unchanged']==638 and replayed['changed_count']==94
    assert not replayed['unexpected_changed_cases']
    assert all(sha(n)==h for n,h in replayed['source_sha256'].items())
    counts=scope_counts(mechanics())
    assert counts=={'items':{'reference_only':75,'mixed':4,'offline':193},
                   'offline_mechanism_gaps':{'pending':1,'partial':4}}
    for data_name in ('rouge/data/ammo-refill-reference.json','rouge/data/native-relic-reference.json'):
        data=read(data_name)
        pairs=(('native_parameter_proof','native_parameter_proof_sha256'),
               ('first_batch_counter_proof','first_batch_counter_proof_sha256'),
               ('timer_book_native_proof','timer_book_native_proof_sha256'))
        for file_key,hash_key in pairs:
            if file_key in data:assert sha(data[file_key])==data[hash_key]
    entries=['CORE_0.55_VERIFICATION.json','READING_0.55_VERIFICATION.json',
        'LIVE_APP_0.55_RUN_VERIFICATION.json','SKILL_UI_0.55_VERIFICATION.json',
        'NATIVE_UI_0.55_VERIFICATION.json','APP_0.55_LAUNCH_VERIFICATION.json',
        independent,replay,'.cache/research/p1-deployment-clock-audit-055/FORMAL_AUDIT.json',
        directory+'SNACK_MULTIBUFF_PASSED_STAGE_1791132335648665700.md',
        directory+'SNACK_MULTIBUFF_FAILED_STAGE_1791131176463664300.md',
        '.cache/research/p1-ammo-independent-055/epoch-4/wording-audit.json',
        origin_freeze_name,origin_review_name,historical_live,
        '.cache/research/p1-origin-discovery-055/REPORT.md']
    public=set(core['source_sha256'])
    for folder in ('tests','scripts'):
        public|={p.relative_to(ROOT).as_posix() for p in (ROOT/folder).glob('*.py')}
    public|={'README.md','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md',
             'BATCH_0.55.md','pyproject.toml','run.cmd'}
    final={'version':'0.55.0','passed':True,'verified_at':time.time(),
        'tests_run':core['tests_run'],'current_tests_passed':core['current_tests_passed'],
        'historical_tests_skipped':70,
        'failures':0,'errors':0,'receipt_sha256':{n:sha(n) for n in entries},
        'source_sha256':{n:sha(n) for n in sorted(public)},'public_replay':{
            'total':732,'exact_unchanged':638,'documented_changed':94,'unexpected_changed':0},
        'independent_ammo_cases':audit['independent_cases'],'standalone_ammo_tests':4,
        'scope_counts':counts,'actual_test_window_verified':True,
        'historical_myrtle_live_case_verified':True,
        'current_run_changed_since_initial_upgrade':changed_since_initial,
        'current_run_same_as_patch_restart':same_patch_run,
        'actual_origin_bug_repair_on_original_run_verified':False,
        'origin_fix_isolated_and_independent_tests_pass':True,
        'settings_and_run_preserved_during_latest_restart':True,
        'page_first_visual_classifier_implemented':False,
        'new_page_routing_plan_saved_in_work_and_remaining_list':True,
        'all_priority_1_completed':False,'all_priority_1_to_3_completed':False,
        'automation_1_3_recreated':False,'game_actions':0,'chat_requests':0,
        'private_state_writes_by_verification':0,'private_runtime_copied_to_public_receipt':False,
        'historical_failed_stages_preserved':True,
        'scope':'Evidence-scoped 0.55 batch. Remaining tasks are PROJECT_PROGRESS.md; no missing mechanisms, lifecycle or general performance are declared complete.'}
    write('FINAL_0.55_VERIFICATION.json',final)
    print(json.dumps({k:final[k] for k in ('passed','current_tests_passed','historical_tests_skipped',
        'actual_test_window_verified','historical_myrtle_live_case_verified',
        'current_run_changed_since_initial_upgrade',
        'all_priority_1_completed','page_first_visual_classifier_implemented')}))


if __name__=='__main__':main()
