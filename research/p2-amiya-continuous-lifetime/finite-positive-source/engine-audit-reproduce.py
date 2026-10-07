"""Read-only public Amiya S1 audit; writes artifacts only beside this script."""
import hashlib,json,subprocess,sys
from pathlib import Path
repo=Path('/workspace/rougezhushou')
sys.path.insert(0,str(repo))
from rouge.damage import calculate_damage
from rouge.timing import phase_totals
base={'operator':'char_002_amiya','skill':1,'base_attack':1000,'enemy_resistance':0,
      'enemy_defense':0,'window_seconds':10,'timing_mode':'continuous'}
cases=[('baseline',{}),('positive_life_point1',{'target_disappears_seconds':.1}),
       ('positive_life_1',{'target_disappears_seconds':1}),
       ('range_0_to_1',{'target_windows':[[0,1]]}),
       ('zero_life_control',{'target_disappears_seconds':0}),
       ('empty_range_control',{'target_windows':[]})]
rows=[]
for label,timing in cases:
    scenario={**base,'timing':timing}
    result=calculate_damage(scenario)
    skill=result['estimate']['skill']
    rows.append({'case':label,'input':scenario,'complete':result['complete'],
        'estimate_complete':result['estimate']['complete'],
        'window_damage':result['total_damage'],
        'skill':{key:skill.get(key) for key in ('initial_seconds','duration_seconds','recharge_seconds',
            'cycle_seconds','total_damage','phase_damage','cycle_damage','cycle_dps','cycle_healing','cycle_hps','window_dps')},
        'components':result['components'],
        'timing':result['timing'],
        'public_report':[{k:section[k] for k in ('id','metrics')} for section in result['report']['sections']
                         if section['id'] in ('timing','damage')]})
artifact={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
    'source_sha256':{path:hashlib.sha256((repo/path).read_bytes()).hexdigest()
        for path in ('rouge/timing.py','rouge/operator_engine.py','rouge/uncertain_sources.py','rouge/reporting.py')},
    'cases':rows,
    'boundary_helper_probe':{'boundary_seconds':5,
      'placed_damage':phase_totals([{'name':'placed','damage_type':'magic','total':30,'times_seconds':[1,5,9]}],5)[0],
      'unplaced_damage':phase_totals([{'name':'unplaced','damage_type':'magic','total':30}],5)[0]}}
artifact['requested_baseline']='ab1a2f4'
artifact['source_identical_to_requested_baseline']={
    path:hashlib.sha256(subprocess.check_output(['git','show','ab1a2f4:'+path],cwd=repo)).hexdigest()==digest
    for path,digest in artifact['source_sha256'].items()}
output=Path(__file__).with_name('engine-audit-public.json')
output.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'artifact':str(output),'head':artifact['head'],
    'cases':[{ 'case':r['case'],'window_damage':r['window_damage'],**r['skill']} for r in rows],
    'boundary_helper_probe':artifact['boundary_helper_probe']},ensure_ascii=False,indent=2))
