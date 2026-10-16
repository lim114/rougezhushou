from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[2]
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
assert git(['branch','--show-current']).decode().strip()=='codex/p2-development'
assert git(['rev-parse','HEAD']).decode().strip()=='7706a982b84fe64148da87d6d073786704c188d1'
assert not git(['diff','--cached','--name-only'])
tracked=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json',
 'PROJECT_COMPLETED.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/node_catalog_view.py','rouge/player_node_information.py','tests/test_documented_item_integration_295.py']
assert set(git(['diff','--name-only']).decode().splitlines())==set(tracked)
promotion_raw=(ROOT/'verification/sections/297-preparation/promotion.json').read_bytes()
assert sha256(promotion_raw).hexdigest()=='09bf0ffe6c64bfa7aa056a7b77119b60f0ad9ccabf1a0bbac127fa9c0b175b36'
promotion=json.loads(promotion_raw)
assert len(promotion['promoted'])==18
assert set(promotion['existing_production_changes'])=={'rouge/node_catalog_view.py','rouge/player_node_information.py'}
maintenance_path='tests/test_documented_item_integration_295.py'
migration=json.loads((ROOT/'verification/sections/297-preparation/historical295-presentation-scope/migration.json').read_bytes())
assert migration['path']==maintenance_path and migration['after_sha256']=='4e946fd3579f37bc3f222f855f9c23811c1279c946a4345431161ed141fcc2f9'
assert sha256((ROOT/maintenance_path).read_bytes()).hexdigest()==migration['after_sha256']
assert migration['all_original_assertion_AST_preserved'] is True
assert migration['current_default37_nontarget_and190resource_hashes_covered_by']=='tests/test_expedition_integration_297.py'
raw_archived_logs={
 'verification/sections/297-preparation/'+name:row['sha256']
 for name,row in promotion['archived_inputs'].items()
 if name in {'backend/first-real-pure-api-tests/stderr','backend/first-real-pure-api-tests/stdout',
 'backend/first-real-source-build/stderr','backend/first-real-source-build/stdout'}}
assert len(raw_archived_logs)==4
new=[name for name in promotion['promoted'] if name not in tracked]
for entry in (ROOT/'verification/sections').iterdir():
    if not entry.name.startswith('297'):continue
    for path in [entry] if entry.is_file() else entry.rglob('*'):
        assert not path.is_symlink()
        if path.is_file():
            relative=path.relative_to(ROOT).as_posix()
            assert path.suffix in {'.json','.log','.md','.png','.py','.txt','.diff','.stderr','.stdout','.html'} or relative in raw_archived_logs
            if relative in raw_archived_logs:assert sha256(path.read_bytes()).hexdigest()==raw_archived_logs[relative]
            assert path.stat().st_size<20_000_000
            new.append(path.relative_to(ROOT).as_posix())
names=sorted(tracked+new);assert len(names)==len(set(names))
assert all(not p.startswith(('.local/','.cache/')) and p!='local-settings.json' for p in names)
section=json.loads((ROOT/'verification/sections/297.json').read_bytes())
assert section['section']==297 and section['prior_commit']=='7706a982b84fe64148da87d6d073786704c188d1'
assert section['cloud_published'] is False and section['next_section']==298
assert section['partial_direct_reference_scope_unchanged']==[10,18,58] and section['whole_map_gaps_unchanged']==[81,59]
assert section['only_existing_production_sources_changed']==['rouge/node_catalog_view.py','rouge/player_node_information.py']
assert section['existing_source_changes_including_test_maintenance']==sorted(['rouge/node_catalog_view.py','rouge/player_node_information.py',maintenance_path])
assert section['old_resource_query_count_unchanged']==190 and section['other_event_player_output_count_unchanged']==37
assert section['unparsed_notes_unchanged']==10
assert set(section['source_sha256'])==set(promotion['promoted'])|{maintenance_path}
assert len(section['source_sha256'])==19 and section['source_sha256'][maintenance_path]==migration['after_sha256']
assert section['remaining_global_stage_floor_gaps_unchanged']==15
assert section['existing_engine_or_typed_reward_qualification_or_run_state_changed'] is False
assert section['typed_named_grant_count_unchanged']==17 and section['original_entry_gaps_unchanged']==[25,57]
progress=(ROOT/'PROJECT_PROGRESS.md').read_bytes()
assert sha256(progress).hexdigest()==section['PROJECT_PROGRESS_unchanged_sha256']
assert git(['show','HEAD:PROJECT_PROGRESS.md'])==progress
assert section['full_validation']['after_section']==290 and section['full_validation']['full_suite_rerun'] is False
assert (ROOT/'verification/sections/297-preparation/closeout-tools/archive-manifest.json').is_file()
for label in ('necessary_validation','native_windows_validation'):
    source=section[label]
    assert sha256((ROOT/source['receipt']).read_bytes()).hexdigest()==source['sha256']
    actual=json.loads((ROOT/source['receipt']).read_bytes())
    assert actual['source_sha256_before']==actual['source_sha256_after']
    if label=='necessary_validation':assert actual['exit_code']==0
    else:assert actual['passed'] is True and actual['qt_exit_code']==0 and actual['verification_window_closed'] is True
    for name,value in actual['source_sha256_after'].items():
        assert not name.startswith(('.cache/','.local/')) and name!='local-settings.json'
        assert sha256((ROOT/name).read_bytes()).hexdigest()==value,name
cp=json.loads((ROOT/'DEVELOPMENT_CHECKPOINT.json').read_bytes())
assert cp['completed_sections']==297 and cp['next_section']==298 and 'active_section'not in cp
assert cp['policy']['current_user_batch_target_section'] is None and cp['next_full_validation_after']==305
index=json.loads((ROOT/'CLOUD_INDEX.json').read_bytes())
assert index['completed_sections']==297 and index['next_section']==298
assert index['requirements']['sha256']==sha256((ROOT/'PROJECT_REQUIREMENTS.md').read_bytes()).hexdigest()
for name,value in index['public_pointers'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
assert not(ROOT/'.cache/section297-stage-readback.json').exists()
assert not(ROOT/'.cache/section297-stage-allowlist.txt').exists()
for name,value in section['source_sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
listing=ROOT/'.cache/section297-stage-allowlist.txt';listing.write_bytes(('\n'.join(names)+'\n').encode('utf8'))
subprocess.check_call(['git','add','-f','--pathspec-from-file='+str(listing)],cwd=ROOT)
assert set(git(['diff','--cached','--name-only']).decode().splitlines())==set(names)
blobs=git(['cat-file','--batch'],input=(''.join(':'+name+'\n' for name in names)).encode('utf8'))
offset=0;expected={}
for name in names:
    end=blobs.index(b'\n',offset);header=blobs[offset:end].split();assert header[1]==b'blob'
    size=int(header[2]);offset=end+1;raw=blobs[offset:offset+size];offset+=size
    assert blobs[offset:offset+1]==b'\n';offset+=1
    assert raw==(ROOT/name).read_bytes(),name
    expected[name]=sha256(raw).hexdigest()
assert offset==len(blobs)
row={'section':297,'prior_commit':'7706a982b84fe64148da87d6d073786704c188d1','staged_public_files':len(names),'total_public_bytes':sum((ROOT/name).stat().st_size for name in names),
 'staged_and_disk_sha256':expected,'no_private_or_cache_paths_staged':True,'all_staged_blobs_match_disk_exactly':True}
dest=ROOT/'.cache/section297-stage-readback.json';assert not dest.exists()
dest.write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({k:v for k,v in row.items() if k!='staged_and_disk_sha256'}))
