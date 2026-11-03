from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[2]
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
assert git(['branch','--show-current']).decode().strip()=='codex/p2-development'
assert git(['rev-parse','HEAD']).decode().strip()=='bb4927a2a2760d48882f3945b750053d7a5617fc'
assert not git(['diff','--cached','--name-only'])
tracked=['AGENTS.md', 'CLOUD_HANDOFF.md', 'CLOUD_INDEX.json', 'DEVELOPMENT_CHECKPOINT.json', 'PROJECT_COMPLETED.md', 'PROJECT_REQUIREMENTS.md', 'WORK_IN_PROGRESS.md', 'rouge/event_planning.py', 'rouge/node_catalog.py', 'rouge/node_catalog_view.py', 'rouge/player_node_information.py', 'tests/test_node_catalog.py']
assert set(git(['diff','--name-only']).decode().splitlines())==set(tracked)
promotion_raw=(ROOT/'verification/sections/298-preparation/final-promotion.json').read_bytes()
assert sha256(promotion_raw).hexdigest()=='f03ac608e556e2c45b2e19b353d4ac4c07966eaa0e010d81a490f14b8c08de64'
promotion=json.loads(promotion_raw)
assert len(promotion['promoted'])==15 and set(promotion['existing_production_changes'])==set(['rouge/event_planning.py', 'rouge/node_catalog.py', 'rouge/node_catalog_view.py', 'rouge/player_node_information.py'])
maintenance_path='tests/test_node_catalog.py'
migration_raw=(ROOT/'verification/sections/298-preparation/historical-test-migration-final.json').read_bytes()
assert sha256(migration_raw).hexdigest()=='caad5f7ea9f1ac4ff29ae8a4230c11725ccd36cd508c18ada9d1a5b507b80d63'
migration=json.loads(migration_raw)
assert migration['new_source']==maintenance_path and migration['new_sha256']=='daebfe930079810c7d057699d8fc3bb4f0f8dee46309df3a624a9b087338436a'
assert sha256((ROOT/maintenance_path).read_bytes()).hexdigest()==migration['new_sha256']
assert migration['changed_methods']==['test_172','test_183'] and migration['unchanged_other_test_methods']==30
assert migration['first_actual_failures']==1 and migration['coverage_scope_reduced'] is False
raw_archived_logs={'verification/sections/298-preparation/author-source-model/first-real-pure-api-tests/stdout': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'verification/sections/298-preparation/author-source-model/first-real-pure-api-tests/stderr': 'ed8a620bd380b75702ccc414991838fed699830ff89255a5706fbeb64bcabc3d', 'verification/sections/298-preparation/author-source-model/first-real-source-build/stdout': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'verification/sections/298-preparation/author-source-model/first-real-source-build/stderr': '7f91cd47e4f2c410ce1f4523d5f82c9e5ed3e290110e4d437e910367cfff777e', 'verification/sections/298-preparation/author-source-model/known-floor-context-final-pure-api-tests/stdout': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'verification/sections/298-preparation/author-source-model/known-floor-context-final-pure-api-tests/stderr': 'd57f26b8c28ebc2bed9cd1e94f55d3e2903405fc80e8f2596a7036afb61b99d3', 'verification/sections/298-preparation/author-source-model/second-real-source-build/stdout': 'cb210c51323e3e052c676834ad15fd9aa6af6a373c16da85c0f7f81b9f02fe12', 'verification/sections/298-preparation/author-source-model/second-real-source-build/stderr': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}
pinned_research_exit={'verification/sections/298-preparation/map-camera-research/cfg.exit': '9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa'}
assert len(raw_archived_logs)==8 and len(pinned_research_exit)==1
raw_archived_logs.update(pinned_research_exit)
new=[name for name in {*promotion['promoted'],*promotion['existing_production_changes']} if name not in tracked]
for entry in (ROOT/'verification/sections').iterdir():
    if not entry.name.startswith('298'):continue
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
section=json.loads((ROOT/'verification/sections/298.json').read_bytes())
assert section['section']==298 and section['prior_commit']=='bb4927a2a2760d48882f3945b750053d7a5617fc'
assert section['cloud_published'] is False and section['next_section']==299
assert section['partial_direct_reference_scope_unchanged']==[10,18,58] and section['whole_map_gaps_unchanged']==[81,59]
assert section['only_existing_production_sources_changed']==['rouge/event_planning.py', 'rouge/node_catalog.py', 'rouge/node_catalog_view.py', 'rouge/player_node_information.py']
assert section['existing_source_changes_including_test_maintenance']==sorted(['rouge/event_planning.py', 'rouge/node_catalog.py', 'rouge/node_catalog_view.py', 'rouge/player_node_information.py']+[maintenance_path])
assert set(section['source_sha256'])==set(promotion['promoted'])|set(promotion['existing_production_changes'])|{maintenance_path}
assert len(section['source_sha256'])==20 and section['source_sha256'][maintenance_path]==migration['new_sha256']
assert section['historical_test_maintenance']['final_tested_sha256']==migration['new_sha256']
assert section['remaining_global_stage_floor_gaps_unchanged']==15 and section['unparsed_notes_unchanged']==10
assert section['actual_server_generation_or_inventory_verified'] is False
assert section['typed_named_grant_count_unchanged']==17 and section['original_entry_gaps_unchanged']==[25,57]
progress=(ROOT/'PROJECT_PROGRESS.md').read_bytes()
assert sha256(progress).hexdigest()==section['PROJECT_PROGRESS_unchanged_sha256']
assert git(['show','HEAD:PROJECT_PROGRESS.md'])==progress
assert section['full_validation']['after_section']==290 and section['full_validation']['full_suite_rerun'] is False
assert (ROOT/'verification/sections/298-preparation/closeout-tools/archive-manifest.json').is_file()
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
assert cp['completed_sections']==298 and cp['next_section']==299 and 'active_section'not in cp
assert cp['policy']['current_user_batch_target_section'] is None and cp['next_full_validation_after']==305
index=json.loads((ROOT/'CLOUD_INDEX.json').read_bytes())
assert index['completed_sections']==298 and index['next_section']==299
assert index['requirements']['sha256']==sha256((ROOT/'PROJECT_REQUIREMENTS.md').read_bytes()).hexdigest()
for name,value in index['public_pointers'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
assert not(ROOT/'.cache/section298-stage-readback.json').exists()
assert not(ROOT/'.cache/section298-stage-allowlist.txt').exists()
for name,value in section['source_sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
listing=ROOT/'.cache/section298-stage-allowlist.txt';listing.write_bytes(('\n'.join(names)+'\n').encode('utf8'))
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
row={'section':298,'prior_commit':'bb4927a2a2760d48882f3945b750053d7a5617fc','staged_public_files':len(names),'total_public_bytes':sum((ROOT/name).stat().st_size for name in names),
 'staged_and_disk_sha256':expected,'no_private_or_cache_paths_staged':True,'all_staged_blobs_match_disk_exactly':True}
dest=ROOT/'.cache/section298-stage-readback.json';assert not dest.exists()
dest.write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({k:v for k,v in row.items() if k!='staged_and_disk_sha256'}))
