"""Independent public parameter/control comparison for the frozen draft only."""
import hashlib,json,subprocess,sys
from pathlib import Path
root=Path('/workspace/.continuation/p2-after-050/draft52')
base={'operator':'char_002_amiya','skill':1,'timing_mode':'continuous','base_attack':1000,'window_seconds':10}
cases=[]
mods=[{}, {'effects':[{'kind':'attack_pct','value':.3},{'kind':'damage_taken','damage_type':'magic','value':.2}], 'enemy_resistance':35}, {'potential':6,'effects':[{'kind':'sp_recovery','value':1}]}, {'elite':1,'skill_rank':7}, {'window_seconds':0}, {'window_seconds':.01}, {'effects':[{'kind':'attack_speed','value':50}]}, {'continuous_attacks':False}]
for i,mod in enumerate(mods):cases.append({'name':'unbound_'+str(i),'scenario':{**base,**mod,'timing':{'target_disappears_seconds':1}}})
for i,timing in enumerate([{}, {'target_disappears_seconds':0}, {'target_disappears_seconds':0,'target_windows':[[0,1]]}, {'target_disappears_seconds':0,'target_windows':[]}]):cases.append({'name':'control_'+str(i),'scenario':{**base,'timing':timing}})
for i,mod in enumerate([{'skill':2},{'skill':3},{'timing_mode':'frames'}, {'operator':'char_1037_amiya3'},{'operator':'char_298_susuro'},{'operator':'char_206_gnosis','skill':2}]):cases.append({'name':'scope_'+str(i),'scenario':{**base,**mod,'timing':{'target_disappears_seconds':1}}})
worker="""import json,sys\nfrom rouge.damage import calculate_damage\ncs=json.loads(sys.stdin.read())\nprint(json.dumps([calculate_damage(c['scenario']) for c in cs],ensure_ascii=False))\n"""
def run(path):
 return json.loads(subprocess.check_output([sys.executable,'-c',worker],input=json.dumps(cases),text=True,cwd=path,env={**__import__('os').environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(path)}))
before=run(root/'baseline');after=run(root/'draft');results=[]
clockkeys=['initial_seconds','duration_seconds','recharge_seconds','cycle_seconds','total_damage','phase_damage','cycle_damage','cycle_dps','cycle_healing','cycle_hps']
for case,b,a in zip(cases,before,after,strict=True):
 if case['name'].startswith('unbound_'):
  ref=a['amiya_continuous_reference'];clock=ref['parameter_clock_reference']
  comparisons={k:clock[k]==b['estimate']['skill'][k] for k in clockkeys}
  comparisons['window_damage']=clock['window_damage']==b['total_damage'];comparisons['window_dps']=clock['window_dps']==b['estimate']['skill']['window_dps']
  comparisons['cast_components']=ref['cast_reference']['conditional_components'][0]['per_hit']==b['estimate']['skill']['skill_attack']*(1-case['scenario'].get('enemy_resistance',0)/100)*(1+sum(e['value'] for e in case['scenario'].get('effects',[]) if e['kind']=='damage_taken' and e.get('damage_type')=='magic'))
  results.append({'name':case['name'],'comparison':comparisons,'passed':all(comparisons.values()),'clock':clock,'before_skill':b['estimate']['skill']})
 else:results.append({'name':case['name'],'all_fields_equal':b==a,'passed':b==a})
receipt={'public_cases':len(cases),'passed':all(r['passed'] for r in results),'results':results,'patch_sha256':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in ['code.patch','tests.patch','section52.patch']}}
(root/'review-public-probe.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'public_cases':len(cases),'passed':receipt['passed'],'failed':[r['name'] for r in results if not r['passed']]}))
