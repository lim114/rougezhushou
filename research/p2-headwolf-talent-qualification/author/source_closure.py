import ast,hashlib,json,pathlib,sys
sys.dont_write_bytecode=True
p=pathlib.Path(__file__).resolve().parent; root=pathlib.Path('/workspace/rougezhushou'); frozen=p/'frozen70'
sys.path.insert(0,str(frozen))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
from rouge.operator_options import OPTIONS
freeze=json.loads((p/'freeze70.json').read_text()); assert all(hashlib.sha256((frozen/r).read_bytes()).hexdigest()==h for r,h in freeze['public_source_hashes'].items())
sources={};tables={}
for name,sha in [('character_table','68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),('skill_table','86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca')]:
 path=root/'.cache/p2-s1-binding'/(name+'.json');b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==sha;tables[name]=json.loads(b);sources[name]={'source_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add','path':str(path),'bytes':len(b),'sha256':sha,'actual_bytes_rehashed':True,'new_download':False,'native_verification':False}
op='char_1038_whitw2';profile=catalog()['operators'][op];raw=tables['character_table'][op];head=raw['talents'][0]['candidates'];assert len(head)==4
for t in head:
 assert t['name']=='头狼' and t['unlockCondition']['phase'] in ('PHASE_1','PHASE_2') and t['unlockCondition']['level']==1
 assert '每在场上停留' in t['description'] and '数量+1' in t['description']
for index,t in enumerate(head):
 n=profile['talents'][0][index]; assert n['name']==t['name'] and n['phase']==int(t['unlockCondition']['phase'][-1]) and n['level']==1 and n['potential_rank']==t['requiredPotentialRank']
 assert n['values']=={b['key']:b['value'] for b in t['blackboard']}
selection=[]
for elite,level in [(0,1),(0,50),(1,1),(1,80),(2,1),(2,59),(2,60),(2,90)]:
 for potential in range(1,7):
  for module_level in range(4):
   scenario={'operator':op,'elite':elite,'level':level,'potential':potential,'module_id':'uniequip_002_whitw2' if module_level else None,'module_level':module_level}
   ts,parts=selected_talents(profile,scenario);chosen=next((t for t in ts if t['name']=='头狼'),None)
   assert (chosen is not None)==(elite>=1)
   selection.append({'scenario':scenario,'selected_headwolf':chosen,'qualified_parts':len(parts)})
skills=[]
for number,entry in enumerate(raw['skills'],1):
 normalized=profile['skills'][number-1];assert normalized['id']==entry['skillId'];assert normalized['unlock_elite']==int(entry['unlockCond']['phase'][-1])
 for rank,lvl in enumerate(tables['skill_table'][entry['skillId']]['levels'],1):
  assert normalized['levels'][rank-1]['values']=={b['key']:b['value'] for b in lvl['blackboard']}
  skills.append({'skill':number,'rank':rank,'skill_id':entry['skillId'],'unlockCondition':entry['unlockCond'],'description':lvl['description'],'values':normalized['levels'][rank-1]['values']})
engine=(frozen/'rouge/operator_engine.py').read_text();tree=ast.parse(engine)
reads=[{'line':n.lineno,'source':ast.get_source_segment(engine,n)} for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='talent' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='头狼'];assert len(reads)==2
consumers={}
for rel in freeze['public_source_hashes']:
 if rel.startswith('rouge/') and rel.endswith('.py'):
  text=(frozen/rel).read_text();lines=[{'line':i,'text':l.strip()} for i,l in enumerate(text.splitlines(),1) if any(x in l for x in ('头狼','head_interval','drone_count'))]
  if lines:consumers[rel]=lines
assert list(consumers)==['rouge/operator_engine.py']
app=(frozen/'rouge/app.py').read_text();assert "'deployment_elapsed_seconds':self.deployment_elapsed.value()" in app
controls=[row for row in OPTIONS[op] if row[0] in ('drone_warmup_hits','deployment_elapsed_seconds')]
(p/'pinned-headwolf-selectors.json').write_text(json.dumps({'character_table.char_1038_whitw2.talents[0]':raw['talents'][0],'character_table.char_1038_whitw2.skills':raw['skills'],'all_skill_levels':skills},ensure_ascii=False,indent=2)+'\n')
receipt={'baseline_head':freeze['baseline_head'],'sources':sources,'talent_selection_192_cases':selection,'three_skill_30_rank_original_matches':True,'selected_headwolf_lowest_qualification':{'elite':1,'level':1},'raw_candidate_intervals':[{k:t[k] for k in ('unlockCondition','requiredPotentialRank','description','blackboard','prefabKey')} for t in head],'exact_talent_reads':reads,'all_numeric_count_metadata_consumers':consumers,'qt_controls':controls,'qt_elapsed_producer':'deployment_elapsed.value() (QDoubleSpinBox); no private state read','narrow_defect':'Missing selected headwolf still supplies fallback20, and original units expression grants +1 after age60 even at E0; qualification must guard existing ceiling/count reference.','existing_semantics_preserved':['owner attack clock reference only','age = declared deployment_elapsed_seconds + phase offset + existing reference event_time','original inclusive >= thresholds for eligible talents','all existing E1/E2 candidate selection and module qualification','API skill/rank qualification precedence','real independent drone acquisition/hit/same-target warmup/arrival and S3 aura first tick stay unverified'],'new_native_proof':False,'new_clock_or_probability_assumption':False,'private_state_copied':False,'production_edits':0}
(p/'source-closure.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'baseline':freeze['baseline_head'],'source_closure':True,'talent_selection_cases':len(selection),'skill_rank_matches':len(skills),'count_consumer_files':list(consumers)}))
