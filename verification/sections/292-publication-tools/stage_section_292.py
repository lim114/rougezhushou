from pathlib import Path
from hashlib import sha256
import json, subprocess

ROOT=Path(__file__).resolve().parents[1]
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
assert git(['branch','--show-current']).decode().strip()=='codex/p2-development'
assert git(['rev-parse','HEAD']).decode().strip()=='63ec130238dfff0a65b8b648518328834f815725'
assert not git(['diff','--cached','--name-only'])
archive=ROOT/'verification/sections/292-preparation/root-tools'
sources=['.cache/promote_section_292.py','.cache/apply_section_292_repair.py',
 '.cache/run_section_292_necessary.py','.cache/run_section_292_window.py',
 '.cache/record_root292_visual_review.py','.cache/restart_window_292.py','.cache/focus_window_292.py',
 '.cache/p3-292-repair-independent-review/review.json',
 '.cache/p3-292-closeout-independent-review/review.json',
 '.cache/p3-292-closeout/close_section_292.py','.cache/p3-292-closeout/CONTRACT.md',
 '.cache/p3-292-closeout/revision2/READY.json']
copies={}
for name in sources:
    key=name.removeprefix('.cache/').replace('/','--')
    copies[key]=(ROOT/name).read_bytes()
assert len(copies)==len(sources)
manifest={'kind':'SECTION292_REVIEWED_PUBLIC_ROOT_PRODUCERS_AND_PRIOR_CLOSEOUT',
 'files':{n:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)} for n,raw in copies.items()},
 'private_state_or_private_hash_lists_copied':False}
raw_manifest=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf8')
if archive.exists():
    assert (archive/'archive-manifest.json').read_bytes()==raw_manifest
    assert {p.name for p in archive.iterdir()}==set(copies)|{'archive-manifest.json'}
    for name,raw in copies.items():assert (archive/name).read_bytes()==raw
else:
    archive.mkdir()
    for name,raw in copies.items():(archive/name).write_bytes(raw)
    (archive/'archive-manifest.json').write_bytes(raw_manifest)
tracked=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json',
 'PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md',
 'rouge/node_catalog_view.py']
assert set(git(['diff','--name-only']).decode().splitlines())==set(tracked)
new=['scripts/verify_event_preview_filters_window_292.py','tests/test_event_preview_filters_292.py']
for entry in (ROOT/'verification/sections').iterdir():
    if not entry.name.startswith('292'):continue
    paths=[entry] if entry.is_file() else list(entry.rglob('*'))
    for path in paths:
        assert not path.is_symlink()
        if path.is_file():
            assert path.suffix in {'.json','.log','.md','.png','.py','.txt','.diff'}
            assert path.stat().st_size < 20_000_000
            new.append(path.relative_to(ROOT).as_posix())
names=sorted(tracked+new)
assert len(names)==len(set(names))
assert all(not p.startswith(('.cache/','.local/')) and p!='local-settings.json' for p in names)
section=json.loads((ROOT/'verification/sections/292.json').read_bytes())
for name,value in section['source_sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
listing=ROOT/'.cache/section292-stage-allowlist.txt';listing.write_bytes(('\n'.join(names)+'\n').encode('utf8'))
subprocess.check_call(['git','add','-f','--pathspec-from-file='+str(listing)],cwd=ROOT)
assert set(git(['diff','--cached','--name-only']).decode().splitlines())==set(names)
blobs=git(['cat-file','--batch'],input=(''.join(':'+p+'\n' for p in names)).encode('utf8'))
offset=0;expected={}
for name in names:
    end=blobs.index(b'\n',offset);header=blobs[offset:end].split();assert header[1]==b'blob'
    size=int(header[2]);offset=end+1;raw=blobs[offset:offset+size];offset+=size
    assert blobs[offset:offset+1]==b'\n';offset+=1
    assert raw==(ROOT/name).read_bytes(),name
    expected[name]=sha256(raw).hexdigest()
assert offset==len(blobs)
receipt={'section':292,'staged_public_files':len(names),'total_public_bytes':sum((ROOT/p).stat().st_size for p in names),
 'staged_and_disk_sha256':expected,'no_private_or_cache_paths_staged':True,'all_staged_blobs_match_disk_exactly':True}
target=ROOT/'.cache/section292-stage-readback.json';assert not target.exists()
target.write_bytes((json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({k:v for k,v in receipt.items() if k!='staged_and_disk_sha256'}))
