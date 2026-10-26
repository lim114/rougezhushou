from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
import argparse,json,subprocess
ROOT=Path(__file__).resolve().parents[1]


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


def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['functional','metadata'],required=True);parser.add_argument('--attempt',type=int,default=1);args=parser.parse_args();phase=args.phase
assert git('branch','--show-current').decode().strip()=='codex/p2-development'and not git('status','--porcelain').strip()
head=git('rev-parse','HEAD').decode().strip();cp=read('DEVELOPMENT_CHECKPOINT.json');r=read('verification/sections/380.json');index=read('CLOUD_INDEX.json')
assert cp['completed_sections']==380 and cp['next_section']==381 and cp['policy']['wrap_up_below_usage_percent']==15
assert cp['policy']['new_functional_sections_paused']is (phase=='metadata') and cp['policy']['stop_after_section']==380
f=_verified_full380()
assert r['current_complete_available_full_validation']['sha256']==sha('verification/full-380/summary.json')
assert index['current_section_label']=='第380节 + '+r['title']and index['current_completed_change']==r['new_capability']
assert index['requirements']['sha256']==sha('PROJECT_REQUIREMENTS.md')
for n,h in index['public_pointers'].items():assert sha(n)==h,n
assert r['full_suite_rerun']is True and r['last_full_validation_sha256']==sha('verification/full-380/summary.json')
if phase=='functional':assert git('rev-parse','HEAD^').decode().strip()=='afab40c3bb4ea8b95118e8cbe34aa07204c1c615'
else:
 proof=read('verification/sections/380-publication.json');assert proof['passed']and proof['ordinary_push']and proof['push_primary_exit']==0
 assert git('rev-parse','HEAD^').decode().strip()==proof['commit']==cp['last_verified_cloud_save']['commit']
 assert cp['last_verified_cloud_save']['proof_sha256']==sha('verification/sections/380-publication.json')
for group in ('source_sha256','validated_source_sha256'):
 for n,h in r[group].items():assert sha(n)==h,n
out=ROOT/(f'.cache/section380-{phase}-publication'+(f'-attempt{args.attempt}'if args.attempt>1 else''));out.mkdir()
argv=['git','push','origin','HEAD:refs/heads/codex/p2-development'];start=datetime.now(timezone.utc).isoformat()
with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);code=p.wait()
actual={'argv':argv,'actual_retained_popen_pid':p.pid,'actual_observed_exit':code,'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'commit':head,'ordinary_push':True,'force_push':False}
(out/'process.json').write_bytes(enc(actual));(out/'process.exit').write_text(str(code)+'\n',encoding='ascii')
print(json.dumps({'phase':phase,'actual_push_exit':code,'stderr':(out/'stderr.txt').read_text('utf8',errors='replace')},ensure_ascii=False),flush=True);assert code==0
remote=git('ls-remote','origin','refs/heads/codex/p2-development');assert remote.decode().split()[0]==head;(out/'ls-remote.txt').write_bytes(remote)
fetch=subprocess.run(['git','fetch','origin','codex/p2-development'],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(out/'fetch-stdout.txt').write_bytes(fetch.stdout);(out/'fetch-stderr.txt').write_bytes(fetch.stderr)
assert fetch.returncode==0 and git('rev-parse','FETCH_HEAD').decode().strip()==head==git('rev-parse','origin/codex/p2-development').decode().strip()
tree={}
for row in git('ls-tree','-rz',head).split(b'\0'):
 if row:
  meta,name=row.split(b'\t',1);tree[name.decode('utf8')]=meta.decode().split()
assert not any(n.startswith('.local/')or n=='local-settings.json'for n in tree)
changed=set([n.decode('utf8') for n in git('diff-tree','--no-commit-id','--name-only','-z','-r',head).split(b'\0') if n]);assert not any(n.startswith(('.cache/','.local/'))or n=='local-settings.json'for n in changed)
names=changed|set(r['source_sha256'])|set(r['validated_source_sha256']);verified={}
for name in sorted(names):
 raw=(ROOT/name).read_bytes();mode,kind,blob=tree[name];digest=sha256(raw).hexdigest()
 assert mode=='100644'and kind=='blob'and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,name
 for key in('source_sha256','validated_source_sha256'):
  if name in r[key]:assert r[key][name]==digest,name
 verified[name]={'sha256':digest,'bytes':len(raw),'git_blob_sha1':blob}
assert git('rev-parse','HEAD').decode().strip()==head and not git('status','--porcelain').strip()
report={'section':380,'passed':True,'branch':'codex/p2-development','phase':phase,'commit':head,'local_HEAD':head,'remote_HEAD':head,'remote_branch':'origin/codex/p2-development','push_primary_exit':code,'push_evidence':actual,'fetch_exit':fetch.returncode,'ordinary_push':True,'force_push':False,'at_utc':datetime.now(timezone.utc).isoformat(),'verified_commit_tree_and_local_public_bytes':verified,'private_state_included':False,'next_section':381,'next_section_started':False,'source_drift':[],'full_validation_rerun':True,'last_full_receipt':'verification/full-380/summary.json','last_full_is_historical_for_current_changes':False,'current_section_label':index['current_section_label'],'worktree_clean_at_verification':True}
(out/'remote-proof.json').write_bytes(enc(report));(out/'execution-publisher.py').write_bytes(Path(__file__).read_bytes())
if phase=='functional':
 target=ROOT/'verification/sections/380-publication.json';assert not target.exists();target.write_bytes(enc(report))
 logs=ROOT/'verification/sections/380-publication-execution';logs.mkdir()
 for name in('stdout.txt','stderr.txt','process.json','process.exit','execution-publisher.py'):(logs/name).write_bytes((out/name).read_bytes())
print(json.dumps({'phase':phase,'actual_local_and_remote_commit':head,'verified_public_files':len(verified),'publication_passed':True},ensure_ascii=False))
