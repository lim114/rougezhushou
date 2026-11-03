"""Rebuild fixed named-item reading from complete public sources; no app import.

Read-only by default. --write explicitly regenerates data/selected authority/manifest.
The old38 reward-query shape is reconstructed without changing its query API.
"""
import argparse
from copy import deepcopy
from hashlib import sha256,sha1
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-named-reward-items-301'
CONFIG=PACK+'/fixed-build-inputs.json'
CONFIG_SHA='c222e72b69fc11e6d69b2788a52fe3038564703e967aaebae13fb5173771c435'
DATA='rouge/data/named-reward-items.json'
SELECTED=PACK+'/selected-authority-records.json'
MANIFEST=PACK+'/source-manifest.json'
ACTUAL=('actual_reward','actual_quantity','actual_claimed','actual_held','actual_effect','actual_eligible')
NOTICE='固定资料候选与原文引用；未知资格仍保留，不表示必然出现，不提供生成概率。'


def encoded(value):return(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def pin(raw):return{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def norm(value):return re.sub(r'[\W_]+','',value or'')


def prior_queries(catalog,rewards,supplement):
    """Pure structural reconstruction of the existing public reward query."""
    queries={}
    for event in catalog['events']:
        documented=event['id']==supplement['event_id']
        if documented:
            assert event==supplement['expected_event']
            assert all(rewards[k]==v for k,v in supplement['expected_existing_rewards'].items())
        rows=[]
        for scene in event['scenes']:
            for choice in scene['choices']:
                candidates=[];rejected=[]
                for identity in choice['game_choice_ids']:
                    reward=rewards.get(identity)
                    if not reward:continue
                    if reward['event_title']==event['title']and norm(reward['choice_title'])==norm(choice['title']):
                        candidates.append({'choice_id':identity,**deepcopy(reward)})
                    else:rejected.append({'choice_id':identity,'reason':'事件标题或选项标题不一致'})
                link=supplement['links'].get(choice['key'])if documented else None
                if link and link['original_choice_id']not in{r['choice_id']for r in candidates}:
                    identity=link['original_choice_id']
                    candidates.append({**deepcopy(rewards[identity]),'choice_id':identity,
                        'reference_kind':'documented_choice_content_link','content_link_verified':True,
                        'source_scene_link_verified':False,'actual_claim_eligible':None,'actual_reward':None,
                        'full_reward_pool_known':False,'documented_cost_reference':deepcopy(link['documented_cost_reference']),
                        'source_reference':deepcopy(link['source_reference'])})
                rows.append({'scene':scene['key'],'choice_id':choice['key'],'choice_title':choice['title'],
                    'role':choice['presentation_role'],'rewards':candidates,'rejected_reward_links':rejected,
                    'named_reward_found':bool(candidates),'full_reward_pool_known':False,'unknown_reward_pool':True,
                    'actual_claim_eligible':None,'source_scene_link_verified':False})
        extra={}if not documented else{'supplemental_reward_reference':{'status':'documented_reference',
            'notice':'两条选项的完整资料与原有笼控器记录相符；数量、实际领取和原生入口关系仍未知。',
            'source':deepcopy(supplement['sources'])}}
        queries[event['id']]={'rows':rows,'sources':deepcopy(catalog['sources']),
            'scope':deepcopy(catalog['completeness']),'notice':NOTICE,
            'event':{k:deepcopy(event[k])for k in('id','title','node_types','floors','natural','natural_reason','entry')},
            'inventory_updated':False,'named_grant_only':True,'full_reward_pool_known':False,**extra}
    return queries


def reconstruct():
    config_raw=(ROOT/CONFIG).read_bytes()
    assert sha256(config_raw).hexdigest()==CONFIG_SHA,'Fixed build configuration changed.'
    config=json.loads(config_raw);raws={}
    for name,expected in config['sources'].items():
        raw=(ROOT/name).read_bytes();assert pin(raw)==expected,'Fixed source mismatch: '+name
        raws[name]=raw
    def read(name):return json.loads(raws[name])
    game=read('research/p3-future-region-effects-300/game-topic-complete.json')['details']['rogue_6']
    catalog=read('rouge/data/node-catalog.json');reward_source=read('rouge/data/node-reward-reference.json')
    rewards=reward_source['event_rewards'];assert len(rewards)==17
    supplement=read('rouge/data/event-named-reward-links.json')
    queries=prior_queries(catalog,rewards,supplement)
    baseline=read(config['baseline_file'])
    assert len(queries)==38 and queries==baseline['queries'],'Complete existing38 query reconstruction differs.'
    resource_root=read(PACK+'/resource-root-original.json');resource_tree=read(PACK+'/resource-rogueitem-tree-original.json')
    assert resource_root['sha']=='d0b5af0b004b044d322397ce5ae79632b6d9fcdd'
    assert next(e for e in resource_root['tree']if e['path']=='rogueitem')['sha']==resource_tree['sha']
    events={};items={};relics={};primary_choices={};links=[]
    for event in catalog['events']:
        for row in queries[event['id']]['rows']:
            if not row['rewards']:continue
            assert len(row['rewards'])==1,'No implicit selection among multiple reward records.'
            reward=row['rewards'][0];original_id=reward['choice_id'];raw_reward=rewards[original_id]
            primary=game['choices'][original_id];item_id=reward['reward']['item_id'];item=game['items'][item_id]
            assert raw_reward['reward']['quantity']is None and item['type']in('RELIC','SCRAP')
            scene=next(s for s in event['scenes']if s['key']==row['scene'])
            choice=next(c for c in scene['choices']if c['key']==row['choice_id'])
            assert norm(primary['title'])==norm(choice['title'])and item.get('usage')and item.get('description')
            icon=config['icons'][item_id];assert icon['icon_id']==item['iconId']and Path(icon['file']).name==item['iconId']+'.png'
            tree_entry=next(e for e in resource_tree['tree']if e['path']==item['iconId']+'.png')
            assert tree_entry['sha']==icon['git_blob_sha1']
            image=raws[icon['file']]
            assert pin(image)=={'sha256':icon['sha256'],'bytes':icon['bytes']}
            assert sha1(b'blob '+str(len(image)).encode()+b'\0'+image).hexdigest()==tree_entry['sha']
            assert image[:8]==b'\x89PNG\r\n\x1a\n'
            events[event['id']]=event;items[item_id]=item;primary_choices[original_id]=primary
            if item['type']=='RELIC':relics[item_id]=game['relics'][item_id]
            links.append({'reference_id':choice['key'],'event_id':event['id'],'scene_key':scene['key'],'choice_key':choice['key'],
                'original_choice_id':original_id,'item_id':item_id,'name':item['name'],'item_kind':item['type'],
                'item_kind_name':'零件'if item['type']=='SCRAP'else'收藏品','choice_title':choice['title'],
                'choice_description':choice['description'],'condition_text':raw_reward['condition_text'],
                'conditions':raw_reward['conditions'],'quantity_reference':raw_reward['reward']['quantity'],
                'catalog_choice':choice,'original_choice':primary,'reward_reference':reward,
                **{k:None for k in ACTUAL}})
    assert(len(events),len(links),len(items),len(relics))==(10,16,13,12)
    assert'choice_ro6_rest_4'not in primary_choices
    assert len({(r['event_id'],r['scene_key'],r['choice_key'])for r in links})==16
    assert all(len(e['scenes'])>0 for e in events.values())
    source={'game':reward_source['source'],'game_commit':reward_source['commit'],
        'existing_reward_file':'rouge/data/node-reward-reference.json','existing_typed_count':17,
        'catalog_file':'rouge/data/node-catalog.json','complete_prior_queries_file':config['baseline_file'],
        'resource':{'repository':'fexli/ArknightsResource','commit':resource_root['sha'],
            'root_tree_file':PACK+'/resource-root-original.json','rogueitem_tree_file':PACK+'/resource-rogueitem-tree-original.json'},
        'community_named_link_file':'rouge/data/event-named-reward-links.json'}
    authority={'schema':'named_reward_selected_authority_v1','expected_events':events,
        'expected_original_rewards':rewards,'expected_reward_queries':{k:queries[k]for k in events},
        'complete_items':items,'complete_relics':relics,'complete_original_choices':primary_choices,'icons':config['icons'],'source':source}
    data={'schema':'named_reward_items_v1','expected_events':events,'expected_original_rewards':rewards,
        'expected_reward_queries':authority['expected_reward_queries'],'choices':links,
        'items':items,'relics':relics,'icons':config['icons'],'source':source,
        'notice':'这是选项资料中的具名物品说明，不表示本局已选择、领取、持有或生效；未知数量不按1件处理。',
        'unknowns':['本局能否选择与实际领取','具名奖励的数量及完整掉落池','本局是否持有、生效与当前服务器适用性'],
        'unlock_notice':'图鉴解锁说明只描述物品条目，不证明当前选项已解锁或本局能领取。',
        'current_server_verified':False,'inventory_updated':False,'original_entry_restored':False,
        'unbound_original_choice_ids_not_restored':['choice_ro6_rest_4']}
    result={DATA:encoded(data),SELECTED:encoded(authority)}
    files={**config['sources'],CONFIG:pin(config_raw)}
    for name in('README.md','SCHEMA.md'):
        relative=PACK+'/'+name;files[relative]=pin((ROOT/relative).read_bytes())
    files.update({n:pin(v)for n,v in result.items()})
    runtime={n:files[n]for n,role in config['roles'].items()if role=='runtime'}
    runtime.update({n:files[n]for n in(CONFIG,DATA,SELECTED,PACK+'/README.md',PACK+'/SCHEMA.md')})
    manifest={'schema':'named_reward_items_source_manifest_v1','data_file':DATA,'data_sha256':pin(result[DATA])['sha256'],
        'selected_authority_file':SELECTED,'fixed_build_inputs_sha256':CONFIG_SHA,
        'files':files,'runtime_files':runtime,'build_authority_files':{n:files[n]for n,role in config['roles'].items()if role=='build_only'},
        'runtime_reads_complete_primary_table':False,'runtime_verifies_complete_build_original_bytes':False,
        'all_package_runtime_members_required_for_each_target_query':True,'counts':{'original_typed':17,'bound_choices':16,'events':10,'items':13,'relics':12,'scraps':1},
        'source':source}
    result[MANIFEST]=encoded(manifest)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=reconstruct()
    for name,raw in result.items():
        path=ROOT/name
        if args.write:path.write_bytes(raw)
        else:assert path.read_bytes()==raw,'Rebuilt bytes differ: '+name
    manifest=json.loads(result[MANIFEST])
    print(json.dumps({'kind':'PUBLIC_SOURCE_BUILD_NOT_PRODUCT_ACCEPTANCE','write':args.write,'counts':manifest['counts'],
        'runtime_files':len(manifest['runtime_files']),'runtime_bytes_with_manifest':sum(v['bytes']for v in manifest['runtime_files'].values())+len(result[MANIFEST]),
        'data_sha256':manifest['data_sha256'],'manifest_sha256':sha256(result[MANIFEST]).hexdigest(),
        'prior38_query_values_reconstructed_unchanged':True,'original17_not_modified':True},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
