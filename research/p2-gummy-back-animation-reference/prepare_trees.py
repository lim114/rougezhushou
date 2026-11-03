import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = '9ef5a469673502754db3be320a8eece9a7fd18d4'
PROJECT = '/workspace/rougezhushou'
operations=[]
for name in ('baseline', 'draft'):
    dest=ROOT/name
    if dest.exists(): raise RuntimeError('Do not silently reuse a previous tree')
    for args in (['git','clone','--shared','--no-checkout',PROJECT,str(dest)], ['git','-C',str(dest),'checkout','--detach',BASE]):
        result=subprocess.run(args,text=True,capture_output=True)
        operations.append({'command':args,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        if result.returncode: raise RuntimeError(result.stderr)
    actual=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()
    assert actual==BASE
(ROOT/'tree-preparation-receipt.json').write_text(json.dumps({'version':1,'baseline_commit':BASE,'operations':operations,'network_calls':0,'root_tracked_edits':0},indent=2)+'\n')
print(json.dumps({'baseline_commit':BASE,'trees':['baseline','draft'],'network_calls':0}))
