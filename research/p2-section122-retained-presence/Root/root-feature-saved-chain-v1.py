"""Root alone audits fresh section outputs after actual Wine closure."""
import argparse, hashlib, json, os, subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--section',type=int,choices=range(121,126),required=True);p.add_argument('--window-version',type=int,choices=(1,2,3),default=1);a=p.parse_args()
n=a.section; B=Path('/workspace/.continuation');R=Path('/workspace/rougezhushou')
guard=B/f'section{n}-candidate-source-v1.json';original=B/f'section{n}-original-source-v1.json';window=B/f'section{n}-window-actual-v{a.window_version}'
assert (B/f'section{n}-window-actual-v{a.window_version}.exit-code').read_bytes()==b'0\n'
prefix=B/f'section{n}-saved-actual-v1';version=2 if n in (121,122,123,124) else 1
source=B/f'section{n}-saved-source-v{version}/audit_saved{n}.py'
if n==125:source=B/'section125-saved-final-source-v3/audit_saved125.py'
out=prefix if n==122 else Path(str(prefix)+'.json')
args=['python3',str(source),'--root',str(R),'--guard',str(guard),'--window',str(window),'--out',str(out)]
if n in (121,123,124):args+=['--original-guard',str(original),'--original-api',str(B/f'section{n}-original-api-actual-v1'),'--candidate-api',str(B/f'section{n}-candidate-api-actual-v1')]
if n==122:args+=['--window-exit',str(B/f'section{n}-window-actual-v{a.window_version}.exit-code'),'--runner',str(B/'section122-window-source-v2/window122.py'),'--source-count',str(len(json.loads(guard.read_bytes())['source_sha256']))]
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
subprocess.run(['python3',str(B/'root-run-primary-v1.py'),'--prefix',str(prefix),'--',*args],cwd=R,env=env,check=True)
v=json.loads((out/'receipt.json' if n==122 else out).read_bytes());assert v['passed'] is True and v['workflow_complete'] is True
if n==125:
 assert v['source_count']==len(json.loads(guard.read_bytes())['source_sha256'])
 assert v['source_guard_sha256']==hashlib.sha256(guard.read_bytes()).hexdigest()
else:assert v['source_drift']==[]
print(json.dumps({'actual_Saved_closed':True,'section':n,'Root_pixels_archive_commit_push_pending':True}),flush=True)
