"""Read-only inventory of existing named reward references and exact public assets."""
from datetime import datetime,timezone
from hashlib import sha256,sha1
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from rouge import node_catalog,documented_choice_items,expedition_results

FILES=('rouge/data/node-reward-reference.json','rouge/data/node-catalog.json','rouge/data/relic-icon-receipt.json',
 'rouge/data/tactical-icon-receipt.json','rouge/data/relic-mechanics.json','rouge/node_catalog.py','rouge/node_rewards.py',
 'rouge/player_node_information.py','rouge/node_catalog_view.py','rouge/documented_choice_items.py',
 'rouge/documented_choice_item_view.py','rouge/expedition_results.py','rouge/expedition_results_view.py',
 'research/p3-future-region-effects-300/game-topic-complete.json',
 '.cache/relic-resource-root.json','.cache/relic-resource-tree.json','rouge/app.py')
pins={name:{'sha256':sha256((ROOT/name).read_bytes()).hexdigest(),'bytes':(ROOT/name).stat().st_size} for name in FILES}
assert pins['research/p3-future-region-effects-300/game-topic-complete.json']['sha256']=='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
def read(name):return json.loads((ROOT/name).read_bytes())
rewards=read(FILES[0])['event_rewards'];catalog=read(FILES[1]);icons=read(FILES[2])
game=read('research/p3-future-region-effects-300/game-topic-complete.json');detail=game['details']['rogue_6']
matches={identity:[]for identity in rewards}
queries={}
for event in catalog['events']:
 packet=node_catalog.event_reward_options(event['id'])
 queries[event['id']]=packet
 for row in packet['rows']:
  for reference in row['rewards']:
   if reference['choice_id'] in matches:
    matches[reference['choice_id']].append({'event_id':event['id'],'event_title':event['title'],
     'scene_key':row['scene'],'choice_key':row['choice_id'],'choice_title':row['choice_title'],
     'binding_kind':reference.get('reference_kind','original_choice_id_with_event_and_title_match'),
     'actual_query_reference':reference})
rows=[]
for identity,reward in rewards.items():
 item_id=reward['reward']['item_id'];item=detail['items'][item_id]
 icon_id=item['iconId'];asset_rows=[]
 for reference in icons['icons']:
  if reference['id']!=item_id:continue
  file='rouge/data/'+reference['file'];path=ROOT/file
  blob=path.read_bytes()if path.is_file()else None
  asset_rows.append({'receipt':reference,'actual_file':file,'exists':blob is not None,
   'original_icon_id':icon_id,'file_basename_matches_original_icon_id':Path(file).name==icon_id+'.png',
   'sha256_matches_receipt':blob is not None and sha256(blob).hexdigest()==reference['sha256'],
   'git_blob_sha1_matches_receipt':blob is not None and sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()==reference['git_blob_sha1'],
   'actual_sha256':sha256(blob).hexdigest()if blob is not None else None,'bytes':len(blob)if blob is not None else None})
 if item_id=='rogue_6_scrap_G_12':
  http_path=HERE/'exact-scrap-icon-first/http-receipt.json';http=json.loads(http_path.read_bytes())
  icon_path=HERE/'exact-scrap-icon-first/rogue_6_scrap_G_12.png';blob=icon_path.read_bytes()
  assert http['exit_code']==0 and http['status']==200
  asset_rows.append({'receipt':http,'actual_file':icon_path.relative_to(ROOT).as_posix(),'exists':True,
   'original_icon_id':icon_id,'file_basename_matches_original_icon_id':icon_path.name==icon_id+'.png',
   'sha256_matches_receipt':sha256(blob).hexdigest()==http['sha256'],
   'git_blob_sha1_matches_receipt':sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()==http['complete_fixed_tree_entry']['sha'],
   'actual_sha256':sha256(blob).hexdigest(),'bytes':len(blob),'not_promoted':True})
 rows.append({'original_choice_id':identity,'existing_reward_reference':reward,
  'complete_primary_choice':detail['choices'][identity],'complete_primary_item':item,
  'complete_primary_relic':detail['relics'].get(item_id),'current_catalog_bindings':matches[identity],
  'exact_fixed_icon_candidates':asset_rows,
  'existing_manual_detail_reader':'none_in_event_panel',
  'item_usage_present':bool(item.get('usage')),'item_description_present':bool(item.get('description')),
  'current_account_eligibility_actual_claim_quantity_or_effect_verified':False})
result={'kind':'CACHE_ONLY_P3_CANDIDATE_RESEARCH_NOT_SECTION301_SCOPE_OR_ACCEPTANCE',
 'created_at':datetime.now(timezone.utc).isoformat(),'source_pins':pins,
 'fixed_game_commit':read(FILES[0])['commit'],'icon_source_repository':icons['repository'],'icon_source_commit':icons['commit'],
 'existing_typed_original_choices':len(rewards),'unique_reward_item_ids':len({r['reward']['item_id']for r in rewards.values()}),
 'currently_bound_typed_original_choices':sum(bool(matches[k])for k in matches),
 'current_catalog_reward_links':sum(len(v)for v in matches.values()),
 'unbound_typed_original_choice_ids':[k for k,v in matches.items()if not v],
 'rows':rows,'all38_current_reward_queries':queries,
 'unchanged_existing_readers_excluded_from_proposal':{
  'section295':{'event_id':documented_choice_items.EVENT,'item_id':documented_choice_items.ITEM,
   'name':detail['items'][documented_choice_items.ITEM]['name'],'not_in_existing_typed17':documented_choice_items.ITEM not in{r['reward']['item_id']for r in rewards.values()}},
  'section297':{'event_id':expedition_results.EVENT,'item_id':expedition_results.ITEM,
   'name':detail['items'][expedition_results.ITEM]['name'],'not_in_existing_typed17':expedition_results.ITEM not in{r['reward']['item_id']for r in rewards.values()}}},
 'initial_inventory_identity_correction':{'original_copy':'initial-inventory-before-identity-verification/named-reward-inventory.json',
  'field':'unchanged_existing_readers_excluded_from_proposal.section297.item_id',
  'original_unverified_placeholder':'rogue_6_relic_cargo_1','verified_module_ITEM':expedition_results.ITEM,
  'not_used_to_bind_proposed_rewards':True},
 'actual_actions':{'public_queries_only':True,'Qt_tests_Git_game_chat_private_or_production_edits':False}}
result['public_sources_after']={name:{'sha256':sha256((ROOT/name).read_bytes()).hexdigest(),'bytes':(ROOT/name).stat().st_size}for name in FILES}
result['public_source_before_after_unchanged']=result['source_pins']==result['public_sources_after']
out=HERE/'named-reward-inventory.json';out.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({k:v for k,v in result.items()if k in ('existing_typed_original_choices','unique_reward_item_ids',
 'currently_bound_typed_original_choices','current_catalog_reward_links','unbound_typed_original_choice_ids')},ensure_ascii=False,indent=2))
for row in rows:
 item=row['complete_primary_item'];good=[a for a in row['exact_fixed_icon_candidates']if a['exists']and a['file_basename_matches_original_icon_id']and a['sha256_matches_receipt']and a['git_blob_sha1_matches_receipt']]
 print(row['original_choice_id'],item['name'],'bindings='+str(len(row['current_catalog_bindings'])),'exact_icons='+str(len(good)),
  ' / '.join(x['event_id']+' '+x['choice_key']for x in row['current_catalog_bindings']))
