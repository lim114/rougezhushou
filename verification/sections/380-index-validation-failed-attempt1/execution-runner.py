from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,runpy,subprocess
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'verification/sections/380-index-validation';out.mkdir(exist_ok=True)


def _verified_full380():
    from pathlib import Path as _Path
    from hashlib import sha256 as _sha256
    import json as _json
    import subprocess as _subprocess
    def _read(name):
        path=ROOT/name
        assert path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(ROOT.resolve()),name
        return _json.loads(path.read_bytes())
    def _sha(name):return _sha256((ROOT/name).read_bytes()).hexdigest()
    f=_read('verification/full-380/summary.json')
    assert f['after_section']==380 and f['available_checks_passed']is True and f['scope_not_reduced']is True
    assert f['actual_root_controller_exit']==0 and f['single_available_scope_execution_all_green']is True
    assert f['current_worktree_validation_authority']is True and f['source_drift']==[]
    assert f['complete_repository_validation']is False and all(f[k]is False for k in('P3_complete','P2_complete','P1_complete'))
    assert f['native_windows_game_chat_verified']is False and f['historical_original_Windows_verified']is False
    freeze=f['source_freeze'];assert freeze.startswith('verification/full-380/source-freeze-attempt')and freeze.endswith('.json')
    assert _sha(freeze)==f['source_freeze_sha256']
    d=_read(freeze)
    assert d['section']==380 and d['root_declared']is True and d['parent_commit']==f['tested_worktree_parent_commit']
    assert d['actual_validation_attempt']==f['actual_validation_attempt']and type(d['actual_validation_attempt'])is int and d['actual_validation_attempt']>=1
    assert len(d['selectors'])==len(set(d['selectors']))==f['maintained_selectors']
    assert len(d['p3_scripts'])==f['native_supplements']and f['actual_required_components']==5+len(d['p3_scripts'])
    assert all(any(int(mode.split('_')[1])==n for mode in d['p3_scripts'])for n in range(286,381))
    for mode in('p3_304','p3_305'):assert d['p3_script_options'][mode]['explicit_current_source_freeze']is True
    assert d['p3_script_options']['p3_312']['visible_ms']==120000
    maps={}
    for group in('source_sha256','legacy_native_source_sha256','supplemental_public_inputs_sha256'):
        for name,pin in d[group].items():
            if name in maps:assert maps[name]==pin,name
            maps[name]=pin
    for name,pin in maps.items():
        path=ROOT/name
        assert path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(ROOT.resolve())and _sha(name)==pin,name

    _expected_canonical = [{'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/enemydata/enemy_database.json', 'public_path': 'verification/full-380/explicit-public-build-inputs/f8dd03997d0e3eae65cc4b77bcb6b5ef198488504f738defc31cad5e13c3680c.json', 'sha256': 'f8dd03997d0e3eae65cc4b77bcb6b5ef198488504f738defc31cad5e13c3680c', 'bytes': 15022043, 'origin_manifests': [{'path': 'research/p3-boss-phase-309/source-manifest.json', 'sha256': 'ae8448916f2b8355e0d946f95d4e6748fcaa2a74838e9949794e7485b18b036d', 'bytes': 4332, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1enemydata~1enemy_database.json'}, {'path': 'research/p3-boss-cycle-310/source-manifest.json', 'sha256': 'cddc4465769edd6e74a231838ea325a895562665bee5e2283f6c20880b1e8052', 'bytes': 6015, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1enemydata~1enemy_database.json'}, {'path': 'research/p3-boss-hunt-311/source-manifest.json', 'sha256': 'dc1024855751338d2b4b536c53c83e8cd56e75f548b12296dfa34d3b12335321', 'bytes': 5912, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1enemydata~1enemy_database.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-4-b.json', 'public_path': 'research/p3-auxiliary-mechanisms/level_rogue6_b-4-b.json', 'sha256': 'fc2f7ae7371829259bd445a45704d79f30f84094f8eedbfa74b026fe075c51ea', 'bytes': 202372, 'origin_manifests': [{'path': 'research/p3-boss-hunt-311/source-manifest.json', 'sha256': 'dc1024855751338d2b4b536c53c83e8cd56e75f548b12296dfa34d3b12335321', 'bytes': 5912, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-4-b.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-4.json', 'public_path': 'verification/full-380/explicit-public-build-inputs/1161795429a9dd4f36b6fcf4e6cf5b6300e2bcce6f04a860e9f7b31e6619d292.json', 'sha256': '1161795429a9dd4f36b6fcf4e6cf5b6300e2bcce6f04a860e9f7b31e6619d292', 'bytes': 207445, 'origin_manifests': [{'path': 'research/p3-boss-hunt-311/source-manifest.json', 'sha256': 'dc1024855751338d2b4b536c53c83e8cd56e75f548b12296dfa34d3b12335321', 'bytes': 5912, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-4.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-5.json', 'public_path': 'verification/full-380/explicit-public-build-inputs/aec26f5d1146281bdc50b73d0c88ce99c37c07c3bd6361ed2af8980ce53c1faf.json', 'sha256': 'aec26f5d1146281bdc50b73d0c88ce99c37c07c3bd6361ed2af8980ce53c1faf', 'bytes': 205518, 'origin_manifests': [{'path': 'research/p3-boss-cycle-310/source-manifest.json', 'sha256': 'cddc4465769edd6e74a231838ea325a895562665bee5e2283f6c20880b1e8052', 'bytes': 6015, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-5.json'}]}, {'mode': 'p3_369', 'canonical_script': 'scripts/verify_current_boss_documents_window_369.py', 'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-6.json', 'public_path': 'research/p3-spawn-candidates-299/levels/57db7782a27808e0187f1fbaf41c3886a85e7687d40dc451281846d4297efad9.json', 'sha256': '57db7782a27808e0187f1fbaf41c3886a85e7687d40dc451281846d4297efad9', 'bytes': 165191, 'origin_manifests': [{'path': 'research/p3-boss-phase-309/source-manifest.json', 'sha256': 'ae8448916f2b8355e0d946f95d4e6748fcaa2a74838e9949794e7485b18b036d', 'bytes': 4332, 'json_pointer': '/build_authority_files/.cache~1game-data~1levels~1obt~1roguelike~1ro6~1level_rogue6_b-6.json'}]}]
    assert d.get('canonical_local_public_input_bindings') == _expected_canonical
    _canonical_names = {row['local_path'] for row in _expected_canonical}
    assert {(mode,name) for mode,names in d['p3_script_selected_paths'].items() for name in names if name.startswith('.cache/')} == {('p3_369',name) for name in _canonical_names}
    assert d.get('canonical_local_public_input_sha256') == {row['local_path']:row['sha256'] for row in _expected_canonical}
    for row in _expected_canonical:
        assert row['mode']=='p3_369' and row['canonical_script']=='scripts/verify_current_boss_documents_window_369.py'
        for origin in row['origin_manifests']:
            authority=ROOT/origin['path']
            assert authority.is_file()and not authority.is_symlink()and authority.resolve().is_relative_to(ROOT.resolve())
            assert _sha(origin['path'])==origin['sha256']and authority.stat().st_size==origin['bytes']
            assert _read(origin['path'])['build_authority_files'][row['local_path']]=={'sha256':row['sha256'],'bytes':row['bytes']}
            assert origin['json_pointer']=='/build_authority_files/'+row['local_path'].replace('~','~0').replace('/','~1')
        _raws=[]
        for name in(row['local_path'],row['public_path']):
            path=ROOT/name
            assert path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(ROOT.resolve())
            for parent in path.parents:
                if parent==ROOT:break
                assert not parent.is_symlink()
            raw=path.read_bytes();assert len(raw)==row['bytes']and _sha256(raw).hexdigest()==row['sha256']
            _raws.append(raw)
        assert _raws[0]==_raws[1]
        assert d['supplemental_public_inputs_sha256'][row['public_path']]==row['sha256']
    manifest='verification/full-380/execution-attempt'+str(d['actual_validation_attempt'])+'/archive-manifest.json'
    assert f['archive_manifests_sha256'][manifest]==_sha(manifest)
    archive=_read(manifest)
    assert archive['section']==380 and archive['actual_validation_attempt']==d['actual_validation_attempt']
    assert archive['actual_root_controller_exit']==0 and archive['source_freeze_sha256']==f['source_freeze_sha256']
    assert archive['activation_sha256']==f['activation_sha256']and archive['required_component_positions']==f['actual_required_components']
    assert archive['all_executed_retained_Popen_and_assigned_jobs_terminal']is True
    assert archive['all_original_ordered_components_retained']is True and archive['automated_available_scope_passed']is True
    visual=f['root_PNG_visual_review'];assert visual['file']=='verification/full-380/root-visual-review.json'
    assert _sha(visual['file'])==visual['sha256']and visual['all_reviewed']is True
    pixels=_read(visual['file'])
    assert pixels['section']==380 and pixels['actual_validation_attempt']==d['actual_validation_attempt']
    assert pixels['source_freeze_sha256']==f['source_freeze_sha256']and pixels['archive_manifest_sha256']==_sha(manifest)
    assert pixels['all_reviewed']is True and pixels['pending_actual_view_rows']==0 and pixels['blocking_visual_issues']==[]
    assert visual['image_count']==pixels['image_count']==len(pixels['images'])
    _subprocess.run(['git','merge-base','--is-ancestor',d['parent_commit'],'HEAD'],cwd=ROOT,check=True,stdout=_subprocess.PIPE,stderr=_subprocess.PIPE)
    return f


def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
assert git('rev-parse','HEAD').decode().strip()=='afab40c3bb4ea8b95118e8cbe34aa07204c1c615'
prior=read('verification/sections/320-index-validation/process.json');assert prior['passed']and prior['tests_run']==25 and prior['script_sha256']==sha('scripts/update_cloud_index.py')
# Same unchanged index implementation: reuse the25 portable tests, execute its actual validation on current380 documents.
f=_verified_full380()
module=runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'));module['update'](ROOT)
cp=read('DEVELOPMENT_CHECKPOINT.json');delivery=module['validate_delivery'](ROOT,cp);index=read('CLOUD_INDEX.json');r=read('verification/sections/380.json')
assert index['current_section_label']=='第380节 + '+r['title']and index['completed_sections']==380 and index['next_section']==381
assert index['requirements']['sha256']==sha('PROJECT_REQUIREMENTS.md')and index['latest_full_receipt']=='verification/full-380/summary.json'
assert cp['policy']['wrap_up_below_usage_percent']==15 and cp['policy']['development_paused_by_latest_user_request']is False
for n,h in index['public_pointers'].items():assert sha(n)==h,n
for group in('source_sha256','validated_source_sha256'):
 for n,h in r[group].items():assert sha(n)==h,n
record={'section':380,'passed':True,'current_documents_actually_validated':delivery,'current_index_script_sha256':sha('scripts/update_cloud_index.py'),'unchanged_index_unit_tests_reused':{'receipt':'verification/sections/320-index-validation/process.json','sha256':sha('verification/sections/320-index-validation/process.json'),'tests_run_historically':25,'rerun_this_section':False},'public_pointer_SHA_checked':True,'full_validation_rerun':True,'at_utc':datetime.now(timezone.utc).isoformat()}
(out/'current-validation.json').write_bytes(enc(record));(out/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
r['index_validation']={'receipt':'verification/sections/380-index-validation/current-validation.json','sha256':sha('verification/sections/380-index-validation/current-validation.json'),'unchanged25_unit_tests_reused_not_rerun':True};(ROOT/'verification/sections/380.json').write_bytes(enc(r));module['update'](ROOT)
allowed=['AGENTS.md', 'CLOUD_HANDOFF.md', 'CLOUD_INDEX.json', 'DEVELOPMENT_CHECKPOINT.json', 'PROJECT_COMPLETED.md', 'PROJECT_PROGRESS.md', 'PROJECT_REQUIREMENTS.md', 'WORK_IN_PROGRESS.md', 'rouge/current_guest_material.py', 'rouge/current_guest_material_view.py', 'research/p3-current-guest-material-380/http-source-records.json', 'research/p3-current-guest-material-380/material-opponent-complete.html', 'research/p3-current-guest-material-380/reference-data.json', 'research/p3-current-guest-material-380/runtime-manifest.json', 'research/p3-current-guest-material-380/source-notes.json', 'scripts/build_current_guest_material_380.py', 'scripts/verify_current_guest_material_window_380.py', 'tests/test_current_guest_material_380.py', 'tests/test_current_guest_material_view_380.py', 'rouge/current_battle_view.py', 'scripts/verify_full_available.py']
allowed.append('verification/full-380')
allowed.extend(p.relative_to(ROOT).as_posix()for p in(ROOT/'verification/sections').glob('380*'))
subprocess.run(['git','add','-f','--',*allowed],cwd=ROOT,check=True)
check=subprocess.run(['git','-c','core.whitespace=cr-at-eol,-blank-at-eof','diff','--cached','--check','--','.',':(exclude)research/p3-current-guest-material-380/*.html'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(out/'git-diff-check.txt').write_bytes(check.stdout+check.stderr);assert check.returncode==0,(check.stdout+check.stderr).decode('utf8',errors='replace')[-3000:]
(out/'public-stage-review.json').write_bytes(enc({'section':380,'root_reviewed':True,'source_and_runtime_current':True,'private_or_cache_inclusion_allowed':False,'staged_diff_check_actual_exit':check.returncode,'parent_commit':git('rev-parse','HEAD').decode().strip(),'index_actual_current_validation':True,'local_necessary_methods_run':r['necessary_validation']['methods_run'],'local_native_checks':r['native_windows_validation']['unique_checks']}))
subprocess.run(['git','add','-f','--',out.relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
staged=git('diff','--cached','--name-only').decode('utf8').splitlines();assert not any(n.startswith(('.cache/','.local/'))or n=='local-settings.json'for n in staged)
assert not git('diff','--name-only').strip()and not git('ls-files','--others','--exclude-standard').strip()
print(json.dumps({'section':380,'staged_public_files':len(staged),'index_current_pointers_validated':True,'unchanged25_tests_reused_not_rerun':True,'ready_to_commit_not_published':True},ensure_ascii=False))
