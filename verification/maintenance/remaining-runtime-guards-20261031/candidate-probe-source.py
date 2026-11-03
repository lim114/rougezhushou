from pathlib import Path
from hashlib import sha256
from contextlib import ExitStack
from unittest.mock import patch
import json,sys
R=Path.cwd();sys.path.insert(0,str(R))
from rouge import choice_recruitment_results as recruit,current_reward_reference as current,event_named_reward_links as links,moving_reward_reference as moving,peace_guardian_results as peace,resting_corner_results as resting,stage_entry_reference as entry,node_catalog as catalog,node_rewards
from rouge import current_event_directory,current_event_resources,current_event_item_uses
from tests.test_runtime_reference_review import outputs,battle,items,ritual

MODELS=[(recruit,'recruitment'),(current,'current-rewards'),(links,'event-named-links'),(moving,'moving-rewards'),(peace,'peace-guardian'),(resting,'resting-corner'),(entry,'stage-entry')]
old={m.__name__:{'path':m.MANIFEST,'sha256':m.MANIFEST_SHA256}for m,_ in MODELS}
new={m.__name__:{'path':'research/runtime-reference-loaders-20261031/'+tag+'/source-manifest.json'}for m,tag in MODELS}
for row in new.values():row['sha256']=sha256((R/row['path']).read_bytes()).hexdigest()
code_paths=set()
for m,_ in MODELS:
 data=json.loads((R/m.MANIFEST).read_bytes());code_paths.update(p for p in data.get('runtime_files',data['files'])if p.endswith('.py'))

def packets():return {m.__name__:(m.packet()if m is current else m.source_data())for m,_ in MODELS}
def cases():
 result={};data=packets();assert all(v is not None for v in data.values())
 result['source_packets']=data
 event=catalog._event(recruit.EVENT);result['recruitment']=[recruit.choice_reference(recruit.EVENT,event['scenes'][0]['choices'][1])]
 event=catalog._event(peace.EVENT);scene=event['scenes'][1];result['peace']=[peace.choice_result_reference(event,scene,scene['choices'][0])]
 result['event_named_links']=[links.event_named_reward_links(catalog._event(links.TARGET),node_rewards._reference()['event_rewards'])]
 result['resting']=[resting.resting_result_cards(resting.EVENT)]
 for card in data[resting.__name__]['cards']:
  for branch in card['branches']:result['resting'].append(resting.resting_result_scene(resting.EVENT,card['choice_key'],branch['branch_id']))
 result['stage_entry']=[entry.stage_entry_reference(entry.STAGE_ID)]
 result['moving']=[]
 for grade in [0,1,2,3,False]:result['moving'].append(moving.moving_reward_rule([{'raw':{'id':moving.ENTITY,'useDb':True,'level':grade,'overwrittenData':None}}]))
 result['moving'].append(moving.moving_reward_rule([]))
 ref=data[current.__name__];result['current_rewards']=[]
 with patch.object(current,'packet',return_value=ref):
  for sid in ref['current']['version']['current']['details']['stages']:result['current_rewards'].append(current.stage_rewards(sid))
 result['previously_restored']=sum((outputs(m)for m in [battle,items,ritual]),[])
 assert len(result['previously_restored'])==41 and all(v['source_valid']for v in result['previously_restored'])
 result['dependent_directory']=[m.packet()for m in [current_event_directory,current_event_resources,current_event_item_uses]];assert all(result['dependent_directory'])
 return result

def normalize(value):
 text=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
 for key in old:
  for field in ['path','sha256']:text=text.replace(new[key][field],old[key][field])
 return text.encode('utf8')

def counted():
 counts={p:0 for p in code_paths};original=Path.read_bytes
 def read(path):
  if path.is_relative_to(R):
   key=path.relative_to(R).as_posix()
   if key in counts:counts[key]+=1
  return original(path)
 with patch.object(Path,'read_bytes',read):data=packets()
 assert all(data.values());return counts

before_reads=counted();before=cases()
with ExitStack()as stack:
 for m,_ in MODELS:
  stack.enter_context(patch.object(m,'MANIFEST',new[m.__name__]['path']));stack.enter_context(patch.object(m,'MANIFEST_SHA256',new[m.__name__]['sha256']))
 after_reads=counted();after=cases()
equal={key:normalize(value)==normalize(after[key])for key,value in before.items()};assert all(equal.values()),equal
out=R/'verification/maintenance/remaining-runtime-guards-20261031';out.mkdir(parents=True,exist_ok=False)
record={'passed':True,'baseline_commit':'40bb988899546f5175add0ed49f2cd26e14c5402','old_bindings':old,'new_bindings':new,'all_semantic_groups_equal_except_manifest_identity_and_path':equal,
 'case_counts':{key:len(value)for key,value in before.items()},'public_builder_reads_before':before_reads,'public_builder_reads_after':after_reads,
 'normalized_output_sha256':{key:sha256(normalize(value)).hexdigest()for key,value in before.items()},'actual_game_or_private_data_used':False,'frozen_mechanism_inputs_changed':False,'ordinary_source_functions_executed_under_explicit_temporary_manifest_bindings':True}
(out/'candidate-probe.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8');(out/'candidate-probe-source.py').write_bytes(Path(__file__).read_bytes())
baseline=R/'research/remaining-runtime-guards-20261031/baseline';baseline.mkdir(parents=True,exist_ok=False)
for m,_ in MODELS:(baseline/Path(m.__file__).name).write_bytes(Path(m.__file__).read_bytes())
print(json.dumps({'passed':True,'case_counts':record['case_counts'],'builder_reads_before':sum(before_reads.values()),'builder_reads_after':sum(after_reads.values()),'production_constants_changed':False}))
