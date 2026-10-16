from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[2]
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
assert git(['branch','--show-current']).decode().strip()=='codex/p2-development'
assert git(['rev-parse','HEAD']).decode().strip()=='b56cbf352cf5d171f52ba05839312950df462e8c'
assert not git(['diff','--cached','--name-only'])
tracked=['AGENTS.md', 'CLOUD_HANDOFF.md', 'CLOUD_INDEX.json', 'DEVELOPMENT_CHECKPOINT.json', 'PROJECT_COMPLETED.md', 'PROJECT_REQUIREMENTS.md', 'WORK_IN_PROGRESS.md', 'rouge/battle_event_references.py', 'rouge/battle_view.py']
assert set(git(['diff','--name-only']).decode().splitlines())==set(tracked)
promotion_raw=(ROOT/'verification/sections/299-preparation/final-promotion-repair.json').read_bytes()
assert sha256(promotion_raw).hexdigest()=='092d9c389e4a75dc9b9e209bb5726d4eb97856b5cc4b3e2f58149c9c9308d6dc'
promotion=json.loads(promotion_raw)
assert len(promotion['promoted'])==53 and set(promotion['existing_production_changes'])==set(['rouge/battle_event_references.py', 'rouge/battle_view.py'])
repair_raw=(ROOT/'verification/sections/299-preparation/entry-binding-repair.json').read_bytes()
assert sha256(repair_raw).hexdigest()=='2e5f640e39a3dab71fb1ed0ad67c355ab0fcead7e850bffcd5abe541bc8d931c'
repair=json.loads(repair_raw)
assert repair['all_existing_tests_preserved'] is True and repair['data_or_game_mechanics_changed'] is False
assert repair['only_controller_MANIFEST_and_MANIFEST_SHA_assignments_changed'] is True
raw_archived_logs={'verification/sections/299-preparation/author-backend/backend-after-import-correction/process.exit': '9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa', 'verification/sections/299-preparation/author-backend/backend-first/process.exit': '4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865', 'verification/sections/299-preparation/author-backend/revision2/new-guard-first/process.exit': '9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa', 'verification/sections/299-preparation/author-backend/revision2/original-counterexample/process.exit': '4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865', 'verification/sections/299-preparation/future-event-effects-research/prts-database-434599-HTTP-error-body.bin': '6e1c38d044037281bc69275855c2951880dcf534f456035d0276a244a4a8c81f'}
new=[name for name in {*promotion['promoted'],*promotion['existing_production_changes']} if name not in tracked]
for entry in (ROOT/'verification/sections').iterdir():
    if not entry.name.startswith('299'):continue
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
section=json.loads((ROOT/'verification/sections/299.json').read_bytes())
assert section['section']==299 and section['prior_commit']=='b56cbf352cf5d171f52ba05839312950df462e8c'
assert section['cloud_published'] is False and section['next_section']==300
assert section['partial_direct_reference_scope_unchanged']==[10,18,58] and section['whole_map_gaps_unchanged']==[81,59]
assert section['only_existing_production_sources_changed']==['rouge/battle_event_references.py', 'rouge/battle_view.py']
assert section['existing_source_changes_including_test_maintenance']==['rouge/battle_event_references.py', 'rouge/battle_view.py']
assert section['old_tracked_test_maintenance'] is False
assert set(section['source_sha256'])==set(promotion['promoted'])|set(promotion['existing_production_changes'])
assert len(section['source_sha256'])==55
compat=section['compatibility_maintenance']
assert compat['all_old_tests_preserved'] is True and compat['controller_only_constant_AST_change_verified'] is True
assert compat['data_or_game_mechanics_changed'] is False and compat['source_failure_still_unknown'] is True
assert compat['first_actual_methods']==135 and compat['first_actual_failures']==1 and compat['first_actual_errors']==5
assert compat['first_methods_not_added_to_final_pass_count'] is True
assert compat['changed_source_bindings']==['rouge/event_planning.py','rouge/node_catalog.py']
assert compat['current_manifest_sha256']==repair['new_manifest_sha256']
assert section['source_promotion']['receipt']=='verification/sections/299-preparation/final-promotion-repair.json'
assert section['source_promotion']['sha256']==sha256(promotion_raw).hexdigest()
assert section['source_reference']['fixed_source_inventory']=={'stages':69,'original_levels':38,'groups':285,'packages':215}
assert section['source_reference']['inventory_is_actual_enemy_or_selection_count'] is False
assert section['remaining_global_stage_floor_gaps_unchanged']==15 and section['unparsed_notes_unchanged']==10
assert section['actual_server_generation_or_inventory_verified'] is False
assert section['typed_named_grant_count_unchanged']==17 and section['original_entry_gaps_unchanged']==[25,57]
progress=(ROOT/'PROJECT_PROGRESS.md').read_bytes()
assert sha256(progress).hexdigest()==section['PROJECT_PROGRESS_unchanged_sha256']
assert git(['show','HEAD:PROJECT_PROGRESS.md'])==progress
assert section['full_validation']['after_section']==290 and section['full_validation']['full_suite_rerun'] is False
assert (ROOT/'verification/sections/299-preparation/closeout-tools/archive-manifest.json').is_file()
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
assert cp['completed_sections']==299 and cp['next_section']==300 and 'active_section'not in cp
assert cp['policy']['current_user_batch_target_section'] is None and cp['next_full_validation_after']==305
index=json.loads((ROOT/'CLOUD_INDEX.json').read_bytes())
assert index['completed_sections']==299 and index['next_section']==300
assert index['requirements']['sha256']==sha256((ROOT/'PROJECT_REQUIREMENTS.md').read_bytes()).hexdigest()
for name,value in index['public_pointers'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
assert not(ROOT/'.cache/section299-stage-readback.json').exists()
assert not(ROOT/'.cache/section299-stage-allowlist.txt').exists()
for name,value in section['source_sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
listing=ROOT/'.cache/section299-stage-allowlist.txt';listing.write_bytes(('\n'.join(names)+'\n').encode('utf8'))
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
row={'section':299,'prior_commit':'b56cbf352cf5d171f52ba05839312950df462e8c','staged_public_files':len(names),'total_public_bytes':sum((ROOT/name).stat().st_size for name in names),
 'staged_and_disk_sha256':expected,'no_private_or_cache_paths_staged':True,'all_staged_blobs_match_disk_exactly':True}
dest=ROOT/'.cache/section299-stage-readback.json';assert not dest.exists()
dest.write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({k:v for k,v in row.items() if k!='staged_and_disk_sha256'}))
