from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def git(args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def load(name):return json.loads((ROOT/name).read_bytes())
kind=sys.argv[1];assert kind in ('functional','metadata')
assert git(['branch','--show-current'])=='codex/p2-development'
assert not git(['status','--porcelain'])
head=git(['rev-parse','HEAD']);parent=git(['rev-parse','HEAD^'])
if kind=='functional':
    stage=load('.cache/section299-stage-readback.json')
    assert parent==stage['prior_commit']=='b56cbf352cf5d171f52ba05839312950df462e8c'
    assert set(git(['diff-tree','--no-commit-id','--name-only','-r',head]).splitlines())==set(stage['staged_and_disk_sha256'])
    expected=stage['staged_and_disk_sha256']
else:
    proof=load('verification/sections/299-publication.json')
    assert proof['passed']is True and parent==proof['functional_commit']==proof['commit']
    assert set(git(['diff-tree','--no-commit-id','--name-only','-r',head]).splitlines())==set(load('.cache/section299-metadata-stage.json')['exact_staged_and_disk'])
    expected=load('.cache/section299-metadata-stage.json')['exact_staged_and_disk']
names=sorted(expected)
blobs=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=(''.join(head+':'+p+'\n'for p in names)).encode('utf8'))
offset=0
for name in names:
    end=blobs.index(b'\n',offset);header=blobs[offset:end].split();assert header[1]==b'blob'
    size=int(header[2]);offset=end+1;raw=blobs[offset:offset+size];offset+=size
    assert blobs[offset:offset+1]==b'\n';offset+=1
    assert sha256(raw).hexdigest()==expected[name] and raw==(ROOT/name).read_bytes(),name
assert offset==len(blobs)
dest=ROOT/f'.cache/section299-{kind}-push.json';assert not dest.exists()
argv=['git','push','origin','HEAD:refs/heads/codex/p2-development']
started=datetime.now(timezone.utc).isoformat()
try:
    actual=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
    code=actual.returncode;stdout=actual.stdout;stderr=actual.stderr;timed_out=False
except subprocess.TimeoutExpired as exc:
    code=124;stdout=exc.stdout or b'';stderr=exc.stderr or b'';timed_out=True
row={'section':299,'kind':kind,'commit':head,'prior_commit':parent,'argv':argv,'exit_code':code,
 'stdout':stdout.decode('utf8',errors='replace'),'stderr':stderr.decode('utf8',errors='replace'),
 'started_utc':started,'at_utc':datetime.now(timezone.utc).isoformat(),'ordinary_push':True,
 'timed_out':timed_out,'remote_ref_verified_by_this_push_only':False}
with dest.open('xb')as f:f.write((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'section':299,'kind':kind,'commit':head,'actual_push_exit':code,'timed_out':timed_out}))
raise SystemExit(code)
