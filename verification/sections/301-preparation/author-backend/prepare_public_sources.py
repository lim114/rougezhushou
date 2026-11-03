"""Prepare fixed public inputs only; no live product or personal state changes."""
from hashlib import sha256
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CANDIDATE=HERE/'candidate'
PACK='research/p3-named-reward-items-301'
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def pin(raw):return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def copy_public(source,destination):
 raw=(ROOT/source).read_bytes();target=CANDIDATE/destination;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 return pin(raw)
inventory=json.loads((ROOT/'.cache/p3-301-named-reward-research/named-reward-inventory.json').read_bytes())
sources={};roles={}
for relative in ('rouge/data/node-catalog.json','rouge/data/node-reward-reference.json','rouge/data/relic-icon-receipt.json',
 'rouge/node_catalog.py','rouge/node_rewards.py','rouge/event_named_reward_links.py',
 'rouge/data/event-named-reward-links.json','research/p3-event-named-rewards-289/source-manifest.json',
 'research/p3-future-region-effects-300/game-topic-complete.json'):
 sources[relative]=copy_public(relative,relative)
 roles[relative]='build_only'if relative.endswith('game-topic-complete.json')or relative.endswith('relic-icon-receipt.json')else'runtime'
for source,name in (('.cache/relic-resource-root.json','resource-root-original.json'),
 ('.cache/relic-resource-tree.json','resource-rogueitem-tree-original.json'),
 ('.cache/p3-301-named-reward-research/exact-scrap-icon-first/http-receipt.json','scrap-icon-http-original.json')):
 target=PACK+'/'+name;sources[target]=copy_public(source,target);roles[target]='build_only'
old_manifest=json.loads((ROOT/'research/p3-event-named-rewards-289/source-manifest.json').read_bytes())
for relative in old_manifest['files']:
 if relative in sources:continue
 sources[relative]=copy_public(relative,relative);roles[relative]='build_only'
icons={}
for row in inventory['rows']:
 if not row['current_catalog_bindings']:continue
 item=row['complete_primary_item'];item_id=item['id']
 if item_id in icons:continue
 selected=[v for v in row['exact_fixed_icon_candidates']if v['exists']and v['file_basename_matches_original_icon_id']and v['sha256_matches_receipt']and v['git_blob_sha1_matches_receipt']]
 assert len(selected)==1;asset=selected[0];receipt=asset['receipt']
 destination=PACK+'/icons/'+item['iconId']+'.png'if item['type']=='SCRAP'else asset['actual_file']
 sources[destination]=copy_public(asset['actual_file'],destination);roles[destination]='runtime'
 icons[item_id]={'file':destination,'item_id':item_id,'icon_id':item['iconId'],**sources[destination],
  'git_blob_sha1':receipt['complete_fixed_tree_entry']['sha']if item['type']=='SCRAP'else receipt['git_blob_sha1'],
  'source':{'repository':inventory['icon_source_repository'],'commit':inventory['icon_source_commit'],
    'url':receipt['requested_url']if item['type']=='SCRAP'else receipt['url']}}
baseline={'kind':'FIXED_PRIOR_38_EVENT_REWARD_QUERY_OBSERVATION','existing_typed_count':17,
 'queries':inventory['all38_current_reward_queries'],
 'origin_research_receipt_sha256':sha256((ROOT/'.cache/p3-301-named-reward-research/named-reward-inventory.json').read_bytes()).hexdigest(),
 'source_observation_before_after_unchanged':inventory['public_source_before_after_unchanged'],
 'source_pins':{n:p for n,p in inventory['source_pins'].items()if n in sources}}
baseline_path=PACK+'/prior-38-reward-query-baseline.json';raw=encoded(baseline)
(CANDIDATE/baseline_path).write_bytes(raw);sources[baseline_path]=pin(raw);roles[baseline_path]='runtime'
config={'schema':'named_reward_items_build_input_v1','sources':sources,'roles':roles,'icons':icons,
 'baseline_file':baseline_path,'research_ready_sha256':'2244a8f70a72f290d7b3e3ab180fd49e3abf885bed3186e0b06eca8177435fcd'}
config_path=PACK+'/fixed-build-inputs.json';(CANDIDATE/config_path).write_bytes(encoded(config))
(HERE/'public-dependencies.json').write_bytes(encoded({'files':sources,'roles':roles,'config_file':config_path,
 'config_sha256':sha256((CANDIDATE/config_path).read_bytes()).hexdigest(),'all_paths_public':True}))
print(json.dumps({'source_files':len(sources),'runtime_inputs':sum(v=='runtime'for v in roles.values()),
 'icons':len(icons),'config_sha256':sha256((CANDIDATE/config_path).read_bytes()).hexdigest()},ensure_ascii=False))
