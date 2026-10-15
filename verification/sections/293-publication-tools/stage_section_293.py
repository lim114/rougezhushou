from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
assert git(['branch','--show-current']).decode().strip()=='codex/p2-development'
assert git(['rev-parse','HEAD']).decode().strip()=='78b43ec3c4f69f410f7f290eb1048b755ad57b0e'
assert not git(['diff','--cached','--name-only'])
original=(ROOT/'rouge/resting_corner_view.py').read_bytes()
old=original.replace(b'_KEEP_CHOICE=object()\n',b'').replace(b'choice_key=_KEEP_CHOICE',b'choice_key=None')
old=old.decode('utf8').replace("        if choice.get('conditional'):lines+=['原注：'+_plain(choice['conditional'])]\n",
 "        for note in choice.get('conditional_texts',[]):lines+=['原注：'+_plain(note)]\n")
old=old.replace("        if choice_key is not _KEEP_CHOICE:\n            index=self.choice.findData(choice_key) if type(choice_key) is str else -1\n            self.choice.setCurrentIndex(index)\n",
 "        if type(choice_key) is str:\n            index=self.choice.findData(choice_key)\n            if index>=0:self.choice.setCurrentIndex(index)\n").encode('utf8')
assert sha256(old).hexdigest()=='8ca87b2c24e5b75213845e52e70ba2de8613374053d42208bc32db853cd07aab'
archive=ROOT/'verification/sections/293-preparation/root-tools';archive.mkdir(exist_ok=False)
sources=['.cache/start_section_293.py','.cache/promote_section_293.py','.cache/run_section_293_necessary.py',
 '.cache/prepare_root293_window_tools.py','.cache/run_section_293_window.py',
 '.cache/prepare_root293_original_window.py','.cache/restart_window_293.py','.cache/focus_window_293.py',
 '.cache/p3-293-root-ui/prepare_node_integration.py','.cache/p3-293-root-ui/UI_HANDOFF.json',
 '.cache/p3-293-root-ui/node_catalog_view.py.diff',
 '.cache/p3-293-ui-independent-review/review.json','.cache/p3-293-backend-independent-review/review.json',
 '.cache/p3-293-closeout/close_section_293.py','.cache/p3-293-closeout/CONTRACT.md',
 '.cache/p3-293-closeout/READY.json','.cache/p3-293-closeout/revision2/READY.json',
 '.cache/p3-293-closeout-independent-review/review.json']
copies={name.removeprefix('.cache/').replace('/','--'):(ROOT/name).read_bytes() for name in sources}
copies['first-statically-reviewed-resting_corner_view.py']=old
for name,raw in copies.items():(archive/name).write_bytes(raw)
manifest={'kind':'SECTION293_PUBLIC_ROOT_PRODUCERS_AND_STATIC_CORRECTION_ORIGINAL',
 'files':{name:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)} for name,raw in copies.items()},
 'static_first_not_executed_as_functional_pass':True,'private_state_copied':False}
(archive/'archive-manifest.json').write_bytes((json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
tracked=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json',
 'PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/node_catalog_view.py']
assert set(git(['diff','--name-only']).decode().splitlines())==set(tracked)
promotion=json.loads((ROOT/'verification/sections/293-preparation/promotion/application.json').read_bytes())
new=[name for name in promotion['files_promoted'] if name not in tracked]
for entry in (ROOT/'verification/sections').iterdir():
    if not entry.name.startswith('293'):continue
    for path in [entry] if entry.is_file() else entry.rglob('*'):
        assert not path.is_symlink()
        if path.is_file():
            assert path.suffix in {'.json','.log','.md','.png','.py','.txt','.diff','.stderr','.stdout'}
            assert path.stat().st_size<20_000_000
            new.append(path.relative_to(ROOT).as_posix())
names=sorted(tracked+new);assert len(names)==len(set(names))
assert all(not p.startswith(('.local/','.cache/')) and p!='local-settings.json' for p in names)
section=json.loads((ROOT/'verification/sections/293.json').read_bytes())
for name,value in section['source_sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
listing=ROOT/'.cache/section293-stage-allowlist.txt';listing.write_bytes(('\n'.join(names)+'\n').encode('utf8'))
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
row={'section':293,'staged_public_files':len(names),'total_public_bytes':sum((ROOT/name).stat().st_size for name in names),
 'staged_and_disk_sha256':expected,'no_private_or_cache_paths_staged':True,'all_staged_blobs_match_disk_exactly':True}
dest=ROOT/'.cache/section293-stage-readback.json';assert not dest.exists()
dest.write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({k:v for k,v in row.items() if k!='staged_and_disk_sha256'}))
