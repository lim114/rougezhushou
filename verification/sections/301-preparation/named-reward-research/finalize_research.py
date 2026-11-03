"""Read back the pure research inventory; not a product/API/UI test."""
from datetime import datetime,timezone
from hashlib import sha256,sha1
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def pin(path):
 raw=path.read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
inventory=json.loads((HERE/'named-reward-inventory.json').read_bytes())
assert inventory['existing_typed_original_choices']==17
assert inventory['currently_bound_typed_original_choices']==16 and inventory['current_catalog_reward_links']==16
assert inventory['unique_reward_item_ids']==14 and inventory['unbound_typed_original_choice_ids']==['choice_ro6_rest_4']
assert len(inventory['all38_current_reward_queries'])==38 and inventory['public_source_before_after_unchanged']is True
bound=[r for r in inventory['rows']if r['current_catalog_bindings']]
items={r['complete_primary_item']['id']:r['complete_primary_item']for r in bound}
assert len(bound)==16 and len(items)==13
assert all(v.get('usage')and v.get('description')for v in items.values())
events={b['event_id']for r in bound for b in r['current_catalog_bindings']}
assert len(events)==10
assets={}
for row in bound:
 assert len(row['current_catalog_bindings'])==1
 good=[r for r in row['exact_fixed_icon_candidates']if r['exists']and r['file_basename_matches_original_icon_id']
  and r['sha256_matches_receipt']and r['git_blob_sha1_matches_receipt']]
 assert len(good)==1
 reference=good[0];path=ROOT/reference['actual_file'];blob=path.read_bytes()
 assert sha256(blob).hexdigest()==reference['actual_sha256']
 assert len(blob)==reference['bytes']and blob[:8]==b'\x89PNG\r\n\x1a\n'
 assets[row['complete_primary_item']['id']]={'file':reference['actual_file'],**pin(path)}
assert len(assets)==13
for relative,expected in inventory['source_pins'].items():assert pin(ROOT/relative)==expected,relative
assert inventory['unchanged_existing_readers_excluded_from_proposal']['section297']['item_id']=='rogue_6_relic_final_3'
ready={'kind':'SECTION301_CACHE_ONLY_NAMED_REWARD_RESEARCH_NOT_IMPLEMENTATION_OR_ACCEPTANCE',
 'created_at':datetime.now(timezone.utc).isoformat(),'scope_proposed_not_yet_started':True,
 'current_remote_reported_by_root':'5607cbc46c9cf17a841939a778a247e6e1a2a371','Git_not_used_by_this_research':True,
 'inventory':'named-reward-inventory.json','proposal':'PROPOSAL.md',
 'facts':{'original_typed_records':17,'bound_exact_catalog_choices':16,'bound_unique_items':13,'bound_events':10,
  'bound_relic_items':12,'bound_scrap_items':1,'all13_complete_usage_and_description_from_fixed_original':True,
  'all13_icon_bytes_and_original_icon_id_verified':True,'existing_icons':12,'single_new_exact_scrap_icon_HTTP200':True,
  'unbound_original_choice_not_restored':'choice_ro6_rest_4','old17_remains17':True},
 'exact_item_asset_inventory':assets,
 'excluded_existing295_297':inventory['unchanged_existing_readers_excluded_from_proposal'],
 'all38_actual_reward_queries_preserved_in_inventory':True,
 'current_node_panel_has_no_exact_choice_reward_to_image_details_link':True,
 'global_relic_tooltip_is_separate_from_node_choice_identity_and_does_not_close_this_gap':True,
 'research_identity_placeholder_corrected_with_original_retained':inventory['initial_inventory_identity_correction'],
 'source_pins':inventory['source_pins'],
 'owned_files':{p.relative_to(HERE).as_posix():pin(p)for p in sorted(HERE.rglob('*'))if p.is_file()and p.name!='READY.json'},
 'actions':{'source_queries_only':True,'downloaded_one_exact_public_icon_no_retry':True,'Qt_tests_Git_game_chat_private_or_live_edits':False,
  'formal_product_or_native_checks_run':False,'section301_completed_claimed':False}}
target=HERE/'READY.json'
with target.open('xb')as stream:stream.write((json.dumps(ready,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'ready':str(target),'sha256':pin(target)['sha256'],'facts':ready['facts'],
 'no_implementation_or_tests_or_Git_or_private':True},ensure_ascii=False,indent=2))
