from pathlib import Path
from hashlib import sha256
import json,subprocess,sys
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
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
functional=load('verification/sections/301-publication.json')['functional_commit']
assert git(['rev-parse',functional+'^']).decode().strip()=='5607cbc46c9cf17a841939a778a247e6e1a2a371'
proof=load('verification/sections/301-publication.json');assert proof['passed'] and proof['commit']==functional
cp=load('DEVELOPMENT_CHECKPOINT.json');index=load('CLOUD_INDEX.json')
assert cp['completed_sections']==index['completed_sections']==301
assert cp['next_section']==index['next_section']==302 and 'active_section' not in cp
assert cp['last_verified_cloud_save']['commit']==functional
assert cp['last_verified_cloud_save']['proof_sha256']==sha256((ROOT/'verification/sections/301-publication.json').read_bytes()).hexdigest()
assert index['requirements']['sha256']==sha256((ROOT/'PROJECT_REQUIREMENTS.md').read_bytes()).hexdigest()
for name,value in index['public_pointers'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
if mode=='stage':
    assert git(['rev-parse','HEAD']).decode().strip()==functional
    assert not git(['diff','--cached','--name-only'])
    archive=ROOT/'verification/sections/301-publication-tools';archive.mkdir(exist_ok=False)
    members=['stage_section_301.py','push_section_301.py','verify_publication_301.py','finish_publication_301.py']
    manifest={'kind':'SECTION301_PUBLIC_PUBLICATION_PRODUCERS','files':{}}
    for name in members:
        raw=(Path(__file__).resolve().parent/name).read_bytes();(archive/name).write_bytes(raw)
        manifest['files'][name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    for name in ('stage_section_301.py.txt','verify_publication_301.py.txt','READY.json','RUN_PLAN.md','BASELINE.json'):
        raw=(Path(__file__).resolve().parent/name).read_bytes()
        (archive/name).write_bytes(raw)
        manifest['files'][name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    (archive/'archive-manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode('utf8'))
    tracked=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md']
    assert set(git(['diff','--name-only']).decode().splitlines())==set(tracked)
    new=['verification/sections/301-publication.json','verification/sections/301-publication-push.json']
    new += [p.relative_to(ROOT).as_posix() for p in archive.iterdir()]
    names=sorted(tracked+new);assert len(names)==len(set(names))
    assert all(not p.startswith(('.local/','.cache/')) and p!='local-settings.json' for p in names)
    listing=ROOT/'.cache/section301-metadata-allowlist.txt';listing.write_bytes(('\n'.join(names)+'\n').encode('utf8'))
    subprocess.check_call(['git','add','-f','--pathspec-from-file='+str(listing)],cwd=ROOT)
    assert set(git(['diff','--cached','--name-only']).decode().splitlines())==set(names)
    expected=readback(names,'')
    assert not(ROOT/'.cache/section301-metadata-stage.json').exists()
    write('.cache/section301-metadata-stage.json',{'section':301,'exact_staged_and_disk':expected})
    print(json.dumps({'metadata_staged_public_files':len(names),'exact_bytes':True,'requirements_and_index_current':True}))
else:
    assert not git(['status','--porcelain'])
    head=git(['rev-parse','HEAD']).decode().strip();assert head!=functional
    assert git(['rev-parse','HEAD^']).decode().strip()==functional
    pushed=load('.cache/section301-metadata-push.json');assert pushed['section']==301 and pushed['kind']=='metadata' and pushed['ordinary_push']is True and pushed['timed_out']is False and pushed['commit']==head and pushed['exit_code']==0
    remote=git(['ls-remote','origin','refs/heads/codex/p2-development']).decode().strip();assert remote.split()[0]==head
    paths=git(['diff-tree','--no-commit-id','--name-only','-r',head]).decode().splitlines()
    staged=load('.cache/section301-metadata-stage.json')['exact_staged_and_disk'];assert set(paths)==set(staged)
    assert readback(paths,head)==staged
    row={'section':301,'status':'functional_and_metadata_ordinary_pushed_actual_remote_verified_clean',
     'functional_commit':functional,'metadata_commit':head,'actual_remote_commit':head,
     'current_requirements_and_index_verified':True,'public_metadata_files':len(paths),
     'latest_full_validation_is_historical290':True,'next_periodic_full':305,
     'next_section':302,'P3_complete':False,'P2_complete':False,
     'original_window_receipt':'verification/sections/301-main-window.json',
     'next_action':'Continue source-supported P3 gaps; next302 only after explicit new functional scope. Do not restart completed301 tests. Recognition last.'}
    assert not(ROOT/'.cache/current301-checkpoint.json').exists()
    write('.cache/current301-checkpoint.json',row)
    print(json.dumps(row,ensure_ascii=False))
