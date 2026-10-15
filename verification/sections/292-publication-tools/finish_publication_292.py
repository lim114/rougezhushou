from pathlib import Path
from hashlib import sha256
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
def load(p):return json.loads((ROOT/p).read_bytes())
def write(p,v):(ROOT/p).write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
def readback(paths,ref):
    blobs=git(['cat-file','--batch'],input=(''.join(ref+':'+p+'\n' for p in paths)).encode('utf8'));offset=0;result={}
    for name in paths:
        end=blobs.index(b'\n',offset);header=blobs[offset:end].split();assert header[1]==b'blob'
        size=int(header[2]);offset=end+1;raw=blobs[offset:offset+size];offset+=size
        assert blobs[offset:offset+1]==b'\n';offset+=1
        assert raw==(ROOT/name).read_bytes(),name
        result[name]=sha256(raw).hexdigest()
    assert offset==len(blobs)
    return result
mode=sys.argv[1];assert mode in ('stage','final')
assert git(['branch','--show-current']).decode().strip()=='codex/p2-development'
functional='fd275b7a2175d7176e2e6f111c8e9979fa9c5faf'
proof=load('verification/sections/292-publication.json');assert proof['passed'] and proof['commit']==functional
cp=load('DEVELOPMENT_CHECKPOINT.json');index=load('CLOUD_INDEX.json')
assert cp['completed_sections']==index['completed_sections']==292
assert cp['next_section']==index['next_section']==293 and 'active_section' not in cp
assert cp['last_verified_cloud_save']['commit']==functional
assert cp['last_verified_cloud_save']['proof_sha256']==sha256((ROOT/'verification/sections/292-publication.json').read_bytes()).hexdigest()
assert index['requirements']['sha256']==sha256((ROOT/'PROJECT_REQUIREMENTS.md').read_bytes()).hexdigest()
for name,value in index['public_pointers'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
if mode=='stage':
    assert git(['rev-parse','HEAD']).decode().strip()==functional
    assert not git(['diff','--cached','--name-only'])
    archive=ROOT/'verification/sections/292-publication-tools';archive.mkdir(exist_ok=False)
    members=['stage_section_292.py','push_section_292.py','verify_publication_292.py','finish_publication_292.py']
    manifest={'kind':'SECTION292_PUBLIC_PUBLICATION_PRODUCERS','files':{}}
    for name in members:
        raw=(ROOT/'.cache'/name).read_bytes();(archive/name).write_bytes(raw)
        manifest['files'][name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    (archive/'archive-manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode('utf8'))
    tracked=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md']
    assert set(git(['diff','--name-only']).decode().splitlines())==set(tracked)
    new=['verification/sections/292-publication.json','verification/sections/292-publication-push.json']
    new += [p.relative_to(ROOT).as_posix() for p in archive.iterdir()]
    names=sorted(tracked+new);assert len(names)==len(set(names))
    assert all(not p.startswith(('.local/','.cache/')) and p!='local-settings.json' for p in names)
    listing=ROOT/'.cache/section292-metadata-allowlist.txt';listing.write_bytes(('\n'.join(names)+'\n').encode('utf8'))
    subprocess.check_call(['git','add','-f','--pathspec-from-file='+str(listing)],cwd=ROOT)
    assert set(git(['diff','--cached','--name-only']).decode().splitlines())==set(names)
    expected=readback(names,'')
    write('.cache/section292-metadata-stage.json',{'section':292,'exact_staged_and_disk':expected})
    print(json.dumps({'metadata_staged_public_files':len(names),'exact_bytes':True,'requirements_and_index_current':True}))
else:
    assert not git(['status','--porcelain'])
    head=git(['rev-parse','HEAD']).decode().strip();assert head!=functional
    assert git(['rev-parse','HEAD^']).decode().strip()==functional
    pushed=load('.cache/section292-metadata-push.json');assert pushed['commit']==head and pushed['exit_code']==0
    remote=git(['ls-remote','origin','refs/heads/codex/p2-development']).decode().strip();assert remote.split()[0]==head
    paths=git(['diff-tree','--no-commit-id','--name-only','-r',head]).decode().splitlines()
    staged=load('.cache/section292-metadata-stage.json')['exact_staged_and_disk'];assert set(paths)==set(staged)
    assert readback(paths,head)==staged
    row={'section':292,'status':'functional_and_metadata_ordinary_pushed_actual_remote_verified_clean',
     'functional_commit':functional,'metadata_commit':head,'actual_remote_commit':head,
     'current_requirements_and_index_verified':True,'public_metadata_files':len(paths),
     'latest_full_validation_is_historical290':True,'next_periodic_full':305,
     'next_section':293,'P3_complete':False,'P2_complete':False,
     'original_window_receipt':'verification/sections/292-main-window.json',
     'next_action':'Continue source-supported P3 gaps; draft only .cache/p3-resting-result-card-design. Do not restart completed292 tests. Recognition last.'}
    write('.cache/current292-checkpoint.json',row)
    print(json.dumps(row,ensure_ascii=False))
