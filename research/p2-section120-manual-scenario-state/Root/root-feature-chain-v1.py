"""Root sequential section execution, after Source review and prior publication."""
import argparse, hashlib, json, os, subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--section',type=int,choices=range(121,126),required=True);a=p.parse_args()
n=a.section;B=Path('/workspace/.continuation');R=Path('/workspace/rougezhushou')
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['ROUGE_TEST_CJK_FONT']=r'Z:\usr\share\fonts\opentype\noto\NotoSansCJK-Regular.ttc'
def win(x):return 'Z:'+str(x).replace('/','\\')
def run(label,argv):
 prefix=B/f'section{n}-{label}-actual-v1'
 print(json.dumps({'starting_actual_step':label,'section':n}),flush=True)
 subprocess.run(['python3',str(B/'root-run-primary-v1.py'),'--prefix',str(prefix),'--',*map(str,argv)],cwd=R,env=env,check=True)
 assert Path(str(prefix)+'.exit-code').read_bytes()==b'0\n'
original=B/f'section{n}-original-source-v1.json';candidate=B/f'section{n}-candidate-source-v1.json'
run('original-guard',['python3',B/'root-new-section-guard-v1.py','--section',str(n),'--out',original])
fixtures={121:('p2-next-attack-ready-source-v1/public-inputs.json','8b38f4901ac9afb8a21cdcb0c3e0d23550aab2408fdf5aa4211cc32cf622c42d'),123:('section123-saved-api-source-v1/api-cases.json','3c84d38ef7cb101e4af6b1bbc57d5a09d8b31d06ef414fa1913d4e4378992085')}
def api(phase,guard):
 if n in fixtures:
  filename,digest=fixtures[n];f=B/filename;assert hashlib.sha256(f.read_bytes()).hexdigest()==digest
  run(phase+'-api',[R/'.venv/bin/python',B/'root-public-probe-v2.py','--root',R,'--guard',guard,'--fixture',f,'--fixture-sha256',digest,'--out',B/f'section{n}-{phase}-api-actual-v1','--phase',phase])
 elif n==124:
  count=len(json.loads(guard.read_bytes())['source_sha256'])
  run(phase+'-api',[R/'.venv/bin/python',B/'p2-amiya-recovery-eligibility-source-v5/api124.py','--root',R,'--guard',guard,'--out',B/f'section{n}-{phase}-api-actual-v1','--phase','baseline' if phase=='original' else 'candidate','--source-count',str(count)])
api('original',original)
run('apply',['python3',B/'root-local-overlay-v1.py','--guard',original,'--plan',B/f'section{n}-root-local-plan-v1.json','--out',candidate])
modules={
121:['test_next_attack_ready_stage','test_timing','test_wine_timing','test_next_attack_healing_reference','test_report'],
122:['test_retained_presence_122','test_run_state_reliability','test_training_input_types','test_training_view_100','test_cache_consumers_101','test_counter_semantics_054','test_recipient_binding_050'],
123:['test_last_accepted_cadence','test_next_attack_ready_stage','test_timing','test_wine_timing','test_report'],
124:['test_amiya_recovery_eligibility','test_amiya_continuous_lifetime','test_amiya_regeneration_talent_qualification','test_amiya_input_qualification','test_amiya_phase_reference','test_timing','test_last_accepted_cadence','test_report'],
125:['test_healing_preview','test_haruka_healing_targets','test_myrtle_healing_targets','test_healing_subtotal_scaling','test_susuro_recipient_factor','test_next_attack_healing_reference','test_manual_scenario_120','test_skill_cultivation_118','test_report']}[n]
for name in modules:assert (R/'tests'/(name+'.py')).is_file()
for platform in ('linux','wine'):
 rootarg,guardarg,outarg=(str(R),str(candidate),str(B/f'section{n}-related-{platform}-actual-v1.json'))
 command=[str(R/'.venv/bin/python'),str(B/'root-related-available-v1.py')]
 if platform=='wine':
  command=['/workspace/.compat/run-wine-python.sh',win(B/'root-related-available-v1.py')];rootarg,guardarg,outarg=map(win,(R,candidate,B/f'section{n}-related-{platform}-actual-v1.json'))
 run('related-'+platform,[*command,'--root',rootarg,'--guard',guardarg,'--out',outarg,*('tests.'+name for name in modules)])
api('candidate',candidate)
version={121:3,122:1,123:3,124:5,125:2}[n];writer=B/f'section{n}-window-source-v{version}/window{n}.py'
count=len(json.loads(candidate.read_bytes())['source_sha256'])
args=['/workspace/.compat/run-wine-python.sh',win(writer),'--root',win(R),'--guard',win(candidate),'--out',win(B/f'section{n}-window-actual-v1'),'--source-count',str(count)]
if n==125:args+=['--section','125']
run('window',args)
print(json.dumps({'actual_feature_runtime_closed':True,'section':n,'Saved_Root_visual_archive_publication_pending':True}),flush=True)
