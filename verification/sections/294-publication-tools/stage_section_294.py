from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[2]
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
assert git(['branch','--show-current']).decode().strip()=='codex/p2-development'
assert git(['rev-parse','HEAD']).decode().strip()=='48eeb454e23fffee084fe7b6c7f9667b9216131d'
assert not git(['diff','--cached','--name-only'])
tracked=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json',
 'PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/data/fixed-landmark-references.json']
assert set(git(['diff','--name-only']).decode().splitlines())==set(tracked)
promotion=json.loads((ROOT/'verification/sections/294-preparation/promotion.json').read_bytes())
new=[name for name in promotion['promoted'] if name not in tracked]
for entry in (ROOT/'verification/sections').iterdir():
    if not entry.name.startswith('294'):continue
    for path in [entry] if entry.is_file() else entry.rglob('*'):
        assert not path.is_symlink()
        if path.is_file():
            assert path.suffix in {'.json','.log','.md','.png','.py','.txt','.diff','.stderr','.stdout'}
            assert path.stat().st_size<20_000_000
            new.append(path.relative_to(ROOT).as_posix())
names=sorted(tracked+new);assert len(names)==len(set(names))
assert all(not p.startswith(('.local/','.cache/')) and p!='local-settings.json' for p in names)
section=json.loads((ROOT/'verification/sections/294.json').read_bytes())
assert section['section']==294 and section['prior_commit']=='48eeb454e23fffee084fe7b6c7f9667b9216131d'
assert section['cloud_published'] is False and section['next_section']==295
assert section['partial_scope_after']==[10,18,58] and section['whole_map_stage_image_gaps_unchanged']==[81,59]
assert section['only_existing_production_file_changed']=='rouge/data/fixed-landmark-references.json'
assert section['full_validation']['after_section']==290 and section['full_validation']['full_suite_rerun'] is False
assert section['first_failed_native_validation']['not_counted_as_final_passed_checks'] is True
assert (ROOT/'verification/sections/294-preparation/root-execution-tools/archive-manifest.json').is_file()
for label in ('necessary_validation','native_windows_validation'):
    source=section[label]
    assert sha256((ROOT/source['receipt']).read_bytes()).hexdigest()==source['sha256']
    actual=json.loads((ROOT/source['receipt']).read_bytes())
    assert actual['source_sha256_before']==actual['source_sha256_after']
    for name,value in actual['source_sha256_after'].items():
        assert not name.startswith(('.cache/','.local/')) and name!='local-settings.json'
        assert sha256((ROOT/name).read_bytes()).hexdigest()==value,name
cp=json.loads((ROOT/'DEVELOPMENT_CHECKPOINT.json').read_bytes())
assert cp['completed_sections']==294 and cp['next_section']==295 and 'active_section'not in cp
assert cp['policy']['current_user_batch_target_section'] is None and cp['next_full_validation_after']==305
index=json.loads((ROOT/'CLOUD_INDEX.json').read_bytes())
assert index['completed_sections']==294 and index['next_section']==295
assert index['requirements']['sha256']==sha256((ROOT/'PROJECT_REQUIREMENTS.md').read_bytes()).hexdigest()
for name,value in index['public_pointers'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
assert not(ROOT/'.cache/section294-stage-readback.json').exists()
assert not(ROOT/'.cache/section294-stage-allowlist.txt').exists()
for name,value in section['source_sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
listing=ROOT/'.cache/section294-stage-allowlist.txt';listing.write_bytes(('\n'.join(names)+'\n').encode('utf8'))
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
row={'section':294,'prior_commit':'48eeb454e23fffee084fe7b6c7f9667b9216131d','staged_public_files':len(names),'total_public_bytes':sum((ROOT/name).stat().st_size for name in names),
 'staged_and_disk_sha256':expected,'no_private_or_cache_paths_staged':True,'all_staged_blobs_match_disk_exactly':True}
dest=ROOT/'.cache/section294-stage-readback.json';assert not dest.exists()
dest.write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({k:v for k,v in row.items() if k!='staged_and_disk_sha256'}))
