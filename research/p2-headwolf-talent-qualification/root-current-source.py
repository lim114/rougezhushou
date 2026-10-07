import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from rouge.catalog import catalog
from rouge.operator_options import OPTIONS
section,op=sys.argv[1:3]
expected={'character_table':'68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697','skill_table':'86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'}
raw={}
for name,sha in expected.items():
 b=(Path('.cache/p2-s1-binding')/(name+'.json')).read_bytes();assert hashlib.sha256(b).hexdigest()==sha;raw[name]=json.loads(b)
p=catalog()['operators'][op];source_id=p.get('id',op)
if source_id not in raw['character_table']:
 source_id=next(k for k,v in raw['character_table'].items() if v['name']==p['name'])
s=raw['character_table'][source_id];checks=0
for i,skill in enumerate(p['skills']):
 assert s['skills'][i]['skillId']==skill['id']
 for actual,original in zip(skill['levels'],raw['skill_table'][skill['id']]['levels']):
  assert actual['values']=={row['key']:row['value'] for row in original['blackboard']};checks+=1
phase={'PHASE_0':0,'PHASE_1':1,'PHASE_2':2};tc=0
for group,original in zip(p['talents'],s['talents']):
 named=[item for item in original['candidates'] if item['name']]
 assert len(group)==len(named)
 for actual,item in zip(group,named):
  assert actual['values']=={row['key']:row['value'] for row in item['blackboard']}
  assert (actual['phase'],actual['level'],actual['potential_rank'],actual['name'],actual['description'])==(phase[item['unlockCondition']['phase']],item['unlockCondition']['level'],item['requiredPotentialRank'],item['name'],item['description']);tc+=1
print(json.dumps({'section':int(section),'passed':True,'operator':op,'actual_original_source_id':source_id,'raw_hashes':expected,'skill_ranks_verified':checks,'talent_selectors_verified':tc,'controls':OPTIONS.get(op,[]),'native_validation':False},ensure_ascii=False))
