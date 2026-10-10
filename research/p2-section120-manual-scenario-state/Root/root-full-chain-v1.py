"""Root alone runs sequential real full gates; stops on the first real nonzero."""
import argparse, json, os, subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--section',type=int,choices=(120,125),required=True);a=p.parse_args()
n=a.section; B=Path('/workspace/.continuation'); R=Path('/workspace/rougezhushou')
P=B/f'full120-125-gates-source-v1/section{n}'; A=B/f'full{n}-activated-actual-v1'; G=B/f'full{n}-root-actual-guard-v1.json'
guard=json.loads(G.read_bytes());assert guard['section']==n
def win(x): return 'Z:'+str(x).replace('/','\\')
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['ROUGE_TEST_CJK_FONT']=r'Z:\usr\share\fonts\opentype\noto\NotoSansCJK-Regular.ttc'
def run(label,argv):
    prefix=B/f'full{n}-{label}-actual-v1'
    command=['python3',str(B/'root-run-primary-v1.py'),'--prefix',str(prefix),'--',*map(str,argv)]
    print(json.dumps({'starting_actual_gate':label,'section':n}),flush=True)
    subprocess.run(command,cwd=R,env=env,check=True)
    assert Path(str(prefix)+'.exit-code').read_bytes()==b'0\n'
wine='/workspace/.compat/run-wine-python.sh'
for label,name in [('wine','full'),('selected','selected')]:
    run(label,[wine,win(P/f'adapters/wine_{name}{n}.py'),'--root',win(R),'--guard',win(G),'--out',win(B/f'full{n}-{label}-actual-v1.json'),'--probe',win(B/f'full{n}-capability-actual-v1.json'),'--wine'])
run('linux-pip',[R/'.venv/bin/python','-m','pip','check'])
run('wine-pip',[wine,'-m','pip','check'])
run('window-supervisor',['python3',A/f'supervisor{n}.py','--status',B/f'full{n}-window-supervisor-actual-v1.json','--',wine,win(A/f'launcher{n}.py'),'--root',win(R),'--guard',win(G),'--out',win(B/f'full{n}-window-actual-v1')])
status=json.loads((B/f'full{n}-window-supervisor-actual-v1.json').read_bytes())
assert type(status['child_primary_exit']) is int and status['child_primary_exit']==0 and status['supervisor_exit']==0 and status['timed_out'] is False
with (B/f'full{n}-window-child-actual-v1.exit-code').open('x') as f:f.write(str(status['child_primary_exit'])+'\n')
run('saved',['python3',P/f'saved-audit/audit_full{n}.py','--out',B/f'full{n}-window-actual-v1','--runner',A/'window.py','--guard',G,'--primary',B/f'full{n}-window-child-actual-v1.exit-code','--supervisor',B/f'full{n}-window-supervisor-actual-v1.json','--supervisor-source',A/f'supervisor{n}.py','--receipt',B/f'full{n}-saved-actual-v1.json','--launcher',A/f'launcher{n}.py','--bridge-source',A/f'bridge{n}.py','--admission',A/f'expected-map{n}.json','--source-count',str(len(guard['source_sha256'])),'--root',R])
print(json.dumps({'actual_full_runtime_and_saved_closed':True,'section':n,'Root_visual_and_aggregate_still_pending':True}),flush=True)
