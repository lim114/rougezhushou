"""Whole documented encounter flows, retaining same-caption source variants."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json,argparse,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-vine-events-333';DATA='rouge/data/current-vine-events.json';CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json'
TITLES=['沉寂之屋','呼吸的红苔']

def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes']or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Keep both complete original tables with exact bytes.')
    current=json.loads((root/CURRENT).read_bytes())['details'];baseline=json.loads((root/BASELINE).read_bytes())['details'];nodes=list(Document(raw.decode()).root.walk());events={};scenes={};choices={};originals={g:{}for g in('scenes','choices','items','stages')}
    for title in TITLES:
        heads=[n for n in nodes if n.tag=='h3'and n.attrs.get('id')==title]
        if len(heads)!=1:raise ValueError('One full event table required.')
        table=next(n for n in nodes[nodes.index(heads[0])+1:]if n.tag in('table','h3'));entry=None;active=None;pending=None;es=[];ec=[]
        for ri,tr in enumerate(n for n in table.walk()if n.tag=='tr'):
            for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('td','th')):
                text=canonical(cell.text());loc={'file':receipt['selected_file'],'heading':title,'row':ri,'cell':ci,'cell_attributes':cell.attrs,'cell_text_sha256':sha256(cell.text().encode()).hexdigest()}
                if not text or text=='主选项':continue
                if re.fullmatch('选项[一二三四]',text):
                    if entry is None:raise ValueError('Root options precede event entry.')
                    active=entry;pending=None;continue
                if cell.tag=='th':
                    hits=[k for k,v in current['choiceScenes'].items()if v['title']==title and canonical(v['description'])==text]
                    if len(hits)!=1:raise ValueError('Narrative must match exactly one current scene.')
                    sid=hits[0]
                    if sid in scenes:raise ValueError('Duplicate narrative requires explicit branch handling; do not invent it.')
                    if pending is not None and choices[pending]['next_scene_id']!=sid:raise ValueError('Narrative conflicts with current nextSceneId.')
                    pending=None;active=sid
                    if entry is None:entry=sid
                    scenes[sid]={'id':sid,'event_id':title,'choice_ids':[],'source':loc};es.append(sid);originals['scenes'][sid]=deepcopy(current['choiceScenes'][sid]);continue
                matches={k:v for k,v in current['choices'].items()if v.get('title')and v.get('description')and v['nextSceneId'] in {k for k,w in current['choiceScenes'].items()if w['title']==title}and text.startswith(canonical(v['title'])+canonical(v['description']))}
                if not matches or active is None:raise ValueError('Unknown full caption; do not skip a documented option.')
                signatures={(v['title'],v['description'],v['nextSceneId'])for v in matches.values()}
                if len(signatures)!=1:raise ValueError('Same-caption variants disagree on narrative destination.')
                primary=next(iter(matches.values()));gid='document-choice:'+sha256((title+'\0'+str(ri)+'\0'+str(ci)+'\0'+text).encode()).hexdigest();target=primary['nextSceneId'];item_ids={(v.get('displayData')or{}).get('itemId')for v in matches.values()};item_id=next(iter(item_ids))if len(item_ids)==1 else None
                if item_id is not None:
                    if item_id not in current['items']:raise ValueError('Referenced item missing from current source.')
                    originals['items'][item_id]=deepcopy(current['items'][item_id])
                battle=any(a.tag=='a'and'ISW-'in a.text()for a in cell.walk())
                row={'id':gid,'title':primary['title'],'description':primary['description'],'event_id':title,'scene_id':active,'next_scene_id':target,'variant_ids':list(matches),'actual_variant_id':None,'item_id':item_id,'stage_ids':[],'has_documented_battle_link':battle,'source':loc,'required_item_id':None,'actual_consumed':None,'actual_received':None}
                description=canonical(primary['description'])
                if description.startswith('持有笼控器，'):
                    required=[k for k,v in current['items'].items()if v['name']=='笼控器'and v['type']=='SCRAP']
                    if len(required)!=1:raise ValueError('Exactly one full controller record required.')
                    row['required_item_id']=required[0];originals['items'][required[0]]=deepcopy(current['items'][required[0]])
                row['seed_cost_reference']=1 if description=='种下1枚种子，在下一区域生成“希望的沃土”'else None
                row['target_life_cost_reference']=2 if description=='消耗2目标生命值，获得笼控器'else None
                row['named_part_item_id']=item_id if item_id and current['items'][item_id]['type']=='SCRAP'else None
                row['named_part_quantity']=None
                row['future_region_reference']='希望的沃土'if description.endswith('在下一区域生成“希望的沃土”')else None
                if row['seed_cost_reference']and primary['displayData']['costHintType']!='SEED_COST':raise ValueError('Seed text and current hint disagree.')
                description=canonical(primary['description']);gold=re.match(r'^消耗(\d+)源石锭，',description);row['gold_cost_reference']=int(gold[1])if gold else None
                resource=re.search(r'获得(\d+)(希望|源石锭|目标生命值上限|护盾|行动力)',description);random=re.search(r'获得(\d+)件随机(加工品|概念体|自然物|收藏品)',description)
                row['resource_reward_reference']={'quantity':int(resource[1]),'resource':resource[2]}if resource else None
                row['random_reward_reference']={'quantity':int(random[1]),'kind':random[2],'pool':None}if random else None
                row['named_reward_item_id']=item_id if item_id and current['items'][item_id]['type']=='RELIC'else None
                row['named_reward_quantity']=None;row['half_life_cost_reference']='消耗一半目标生命值'in description;row['all_gold_cost_reference']='消耗全部源石锭'in description;row['actual_eligible']=None
                choices[gid]=row;scenes[active]['choice_ids'].append(gid);ec.append(gid);originals['choices'].update({k:deepcopy(v)for k,v in matches.items()});pending=gid if target is not None else None
        if pending is not None or any(choices[c]['next_scene_id']not in es for c in ec if choices[c]['next_scene_id']is not None):raise ValueError('Incomplete explicit narrative branch.')
        events[title]={'id':title,'title':title,'entry_scene_id':entry,'scene_ids':es,'choice_ids':ec}
    counts={'events':len(events),'scenes':len(scenes),'document_choices':len(choices),'original_choice_variants':len(originals['choices']),'named_battle_choices':sum(c['has_documented_battle_link']for c in choices.values()),'required_item_choices':sum(c['required_item_id']is not None for c in choices.values()),'items':len(originals['items'])}
    if counts!={'events':2,'scenes':8,'document_choices':6,'original_choice_variants':6,'named_battle_choices':0,'required_item_choices':1,'items':3}:raise ValueError('Do not drop full-table options or variants: '+str(counts))
    comparison={g:{k:baseline['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in records.items()}for g,records in originals.items()}
    result={'schema':'current_vine_events_333_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','events':events,'scenes':scenes,'choices':choices,'originals':originals,'counts':counts,'source':receipt,'complete_selected_record_comparison_to_baseline':comparison,'complete_document_tables':True,'complete_game_option_pool':False,'actual_eligible':None,'actual_variant':None,'run_updated':False,'game_parent_script_restored':False,'half_life_integer_rule_verified':False}
    legacy=json.loads((root/'rouge/data/node-catalog.json').read_bytes())['events'];result['catalogue_bindings']={}
    for title in TITLES:
        rows=[r for r in legacy if r['title']==title]
        if len(rows)!=1:raise ValueError('One complete legacy event row required.')
        row=rows[0];links=[{'legacy_scene_key':s['key'],'current_original_scene_id':sid}for s in row['scenes']for sid in s['game_scene_ids']if sid in originals['scenes']and originals['scenes'][sid]['title']==title and canonical(s['description'])==canonical(originals['scenes'][sid]['description'])]
        if len(links)!=4:raise ValueError('All four exact scene IDs and narratives must agree.')
        result['catalogue_bindings'][row['id']]={'expected_legacy_event':deepcopy(row),'expected_summary':{k:deepcopy(row[k])for k in('id','title','node_types','floors','natural','natural_reason','entry')},'exact_scene_links':links,'current_event_id':title}
    data=encoded(result);names=[CURRENT,BASELINE,'rouge/data/node-catalog.json',PACK+'/source-receipt.json',receipt['selected_file']];files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(data),'sha256':sha256(data).hexdigest()}
    return data,encoded({'schema':'current_vine_events_333_manifest_v1','game_commit':result['game_commit'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);p.add_argument('--check',action='store_true');args=p.parse_args();d,m=build()
    if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=False);(args.output_dir/'current-vine-events.json').write_bytes(d);(args.output_dir/'runtime-manifest.json').write_bytes(m)
    if args.check:assert(ROOT/DATA).read_bytes()==d and(ROOT/PACK/'runtime-manifest.json').read_bytes()==m
    print(json.dumps({'counts':json.loads(d)['counts'],'manifest_sha256':sha256(m).hexdigest()}))
