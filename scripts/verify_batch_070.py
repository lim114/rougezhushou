"""Seal the bounded P2 batch, source evidence and the actual project window."""
import ast,hashlib,json,time
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))


def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    names=['CORE_0.70_VERIFICATION.json','NUMERIC_REPLAY_0.70_VERIFICATION.json',
        'NATIVE_UI_0.70_VERIFICATION.json','PACKAGE_0.70_VERIFICATION.json','APP_0.70_LAUNCH_VERIFICATION.json']
    receipts=[read(ROOT/n) for n in names]
    core,numeric,ui,package,app=receipts
    for proof in receipts[:4]:
        assert proof['passed'] and proof['version']=='0.70.0'
        for name,digest in proof['source_sha256'].items():assert sha(ROOT/name)==digest,name
    assert core['tests_run']==1253 and core['current_tests_passed']==1183
    assert core['historical_tests_skipped']==70 and core['failures']==core['errors']==0
    assert not core['source_drift_during_tests'] and len(core['test_modules'])==101
    assert numeric['cases']==732 and numeric['exact_structured_unchanged']==724
    assert numeric['single_cast_and_window_damage_unchanged']==732
    assert len(numeric['allowances'])==8 and not numeric['unexpected_changes'] and not numeric['source_drift']
    for key in ('baseline_output','current_output'):
        assert sha(ROOT/numeric[key])==numeric['baseline_sha256' if key=='baseline_output' else 'current_output_sha256']
    assert sha(ROOT/numeric['worker_receipt'])==numeric['worker_receipt_sha256']
    assert len(ui['checks'])==65 and ui['private_data_isolated'] and not ui['source_drift']
    assert package['assets_checked']==34 and not package['private_runtime_packaged'] and not package['source_drift']
    assert sha(ROOT/package['wheel'])==package['wheel_sha256']

    before=read(ROOT/'.cache/batch-070-before/manifest.json')
    changed=[name for name,digest in before['files'].items() if sha(ROOT/name)!=digest]
    assert set(changed)=={'pyproject.toml','rouge/app.py','rouge/operator_engine.py','rouge/reporting.py',
        'tests/test_damage.py','tests/test_neural_relic_034.py','tests/test_river_reporting_060.py',
        'WORK_IN_PROGRESS.md','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md'},changed
    for name,digest in before['files'].items():
        assert sha(ROOT/'.cache/batch-070-before'/name)==digest,name
    for name in ('rouge/app.py','pyproject.toml'):
        old=(ROOT/'.cache/batch-070-before'/name).read_text(encoding='utf-8')
        assert (ROOT/name).read_text(encoding='utf-8')==old.replace('0.69','0.70')
    assert not any(name.startswith('rouge/data/') for name in changed)
    def functions(path):
        tree=ast.parse(path.read_text(encoding='utf-8'))
        return {node.name:ast.dump(node,include_attributes=False) for node in tree.body
                if isinstance(node,(ast.FunctionDef,ast.ClassDef))}
    old=functions(ROOT/'.cache/batch-070-before/rouge/reporting.py')
    current=functions(ROOT/'rouge/reporting.py')
    assert {k for k in set(old)|set(current) if old.get(k)!=current.get(k)}=={'build_report'}

    research=ROOT/'.cache/research'
    first=read(research/'phatm2-first-event-070/proof.json')
    lifecycle=read(research/'phatm2-lifecycle-070/proof.json')
    actions=read(research/'phatm2-actions-070/proof.json')
    damage=read(research/'phatm2-damage-070/native-proof.json')
    assert first['passed'] and first['native_methods_verified']==43 and first['native_instructions_verified']==4751
    assert actions['passed'] and actions['native_methods_verified']==8 and actions['native_instructions_verified']==1330
    for proof in (first,actions):
        for name,digest in proof['source_sha256'].items():assert sha(ROOT/name)==digest,name
    assert lifecycle['all_instruction_bytes_match_original_file'] and len(lifecycle['new_cfgs'])==87
    assert lifecycle['instruction_count']==8509 and not lifecycle['hot_update_equivalence_verified']
    for row in lifecycle['reused_evidence']:
        assert sha(research/'phatm2-lifecycle-070'/row['file'])==row['sha256']
    assert damage['own_method_count']==52 and damage['own_instruction_count']==7221
    assert damage['method_count']==60 and damage['instruction_count']==8551
    assert not damage['current_hotfix_equivalence_proven']
    for name,digest in damage['inputs'].items():assert sha(research/name)==digest,name
    base=Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')
    for path in (research/'phatm2-first-event-070/art.json',research/'phatm2-s1-069/skill-prefabs.json'):
        config=read(path)
        assert sha(base/config['source_name'])==config['source_sha256']
    cfgs=[research/'phatm2-actions-070'/(s+'.json') for s in ('action-entry','run-actions','apply-actions')]
    for folder in ('phatm2-first-event-070','phatm2-lifecycle-070','phatm2-damage-070'):
        cfgs.extend(sorted((research/folder).glob('*-cfg.json')))
    cfgs=sorted(set(cfgs))
    dll=Path(read(cfgs[0])['source_game_dll']);dh=sha(dll)
    meta=dll.parent/'Arknights_Data/il2cpp_data/Metadata/global-metadata.dat';mh=sha(meta)
    assert dh==first['dll_sha256']==actions['dll_sha256']==lifecycle['source_game_dll_sha256']==damage['source_game_dll_sha256']
    assert mh==first['metadata_sha256']==actions['metadata_sha256']==lifecycle['source_metadata_sha256']==damage['source_metadata_sha256']
    methods=0;instructions=0;unique_methods=set();unique_instructions={}
    with dll.open('rb') as stream:
        for path in cfgs:
            data=read(path);assert data['dll_sha256']==dh and data['metadata_sha256']==mh
            for method in data['methods']:
                assert method['cfg_bounded_traversal_finished'] and not method['limits']
                methods+=1;unique_methods.add(method['method']['Address'])
                for row in method['instructions']:
                    binary=bytes.fromhex(row['bytes']);stream.seek(int(row['physical_offset'],16))
                    assert stream.read(len(binary))==binary
                    instructions+=1
                    assert row['address'] not in unique_instructions or unique_instructions[row['address']]==row['bytes']
                    unique_instructions[row['address']]=row['bytes']
    assert methods==190 and instructions==21811,(methods,instructions)

    from verify_launch_070 import windows,foreground,state,verify_process
    live=windows();assert len(live)==1
    w=live[0]
    assert w['pid']==app['process_id'] and w['title']==app['window_title'] and w['visible'] and not w['minimized'] and not w['hung']
    assert verify_process(w['pid'])==app['process_executable']
    raised=foreground(w['hwnd'])
    checkpoint=read(ROOT/app['checkpoint']);after=state()
    assert checkpoint['run_id_hash']==after['run_id_hash'] and checkpoint['config_hashes']==after['config_hashes']
    run=read(ROOT/'.local/run-state.json');prefix=run.get('history',[])[:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==checkpoint['history_prefix_hash']
    assert app['same_run_preserved'] and app['settings_and_bindings_unchanged'] and app['launcher_stderr_bytes']==0

    files=set(ROOT/name for name in before['files'])
    files.update((ROOT/'rouge').rglob('*.py'))
    files.update((ROOT/'tests').glob('test_multi_melee_070.py'))
    files.update((ROOT/'scripts').glob('*070.py'))
    files.update(ROOT/n for n in names)
    files.add(ROOT/'BATCH_0.70.md')
    files.update(cfgs)
    for folder in ('phatm2-first-event-070','phatm2-lifecycle-070','phatm2-actions-070','phatm2-damage-070'):
        files.update((research/folder).glob('*.py'));files.update((research/folder).glob('*.json'))
        files.add(research/folder/'REPORT.md')
    files.update(research/folder/name for folder,name in (
        ('phatm2-first-event-070','proof.json'),('phatm2-first-event-070','review.md'),
        ('phatm2-lifecycle-070','proof.json'),('phatm2-lifecycle-070','reproduction-manifest.json'),
        ('phatm2-actions-070','proof.json'),('phatm2-damage-070','native-proof.json')))
    progress=(ROOT/'PROJECT_PROGRESS.md').read_text(encoding='utf-8')
    assert '当前先推进P2' in progress and '段间等待的计算接入' not in progress
    assert progress.index('| 最后 | 藏品识别')>progress.index('| 5 | 界面与交付')
    assert '0.70' in (ROOT/'WORK_IN_PROGRESS.md').read_text(encoding='utf-8').split('---')[0]
    result={'version':'0.70.0','passed':True,'verified_at':time.time(),
        'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(files)},
        'new_native_cfg_method_entries':methods,'new_native_instruction_entries':instructions,
        'distinct_native_method_addresses':len(unique_methods),'distinct_instruction_addresses':len(unique_instructions),
        'game_dll_sha256':dh,'metadata_sha256':mh,'changed_existing_files':changed,
        'prior_public_snapshot_files':len(before['files']),'production_data_changed':False,
        'recognition_or_run_state_code_changed':False,'native_actual_absolute_phase_verified':False,
        'all_priority_1_completed':False,'all_priority_2_completed':False,
        'actual_window_pid':w['pid'],'actual_window_visible':True,'actual_window_responsive':True,
        'actual_window_foreground':raised,'same_current_run_preserved':True,'private_configs_preserved':True,
        'history_count_at_final':after['history_count'],'game_actions':0,'chat_requests':0,
        'private_state_copied':False,'research_agents_completed':True}
    (ROOT/'FINAL_0.70_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','changed_existing_files')},ensure_ascii=False))


if __name__=='__main__':main()
