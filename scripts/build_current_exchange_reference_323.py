"""Current offer flags and documented outcomes; never a reward-pool generator."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded,plain

ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-exchange-323';DATA='rouge/data/current-exchange-reference.json'
CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json'
RARITIES={'NORMAL':'低稀有度','RARE':'中稀有度','SUPER_RARE':'高稀有度'}


def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or sha256(raw).hexdigest()!=receipt['selected_sha256']or len(raw)!=receipt['selected_bytes']:raise ValueError('Fixed complete exchange table required.')
    current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details'];items={k:v for k,v in current['items'].items()if v['type']=='RELIC'}
    previous={k:v for k,v in old['items'].items()if v['type']=='RELIC'};catalogue=[]
    for key,item in items.items():
        if type(item['canSacrifice'])is not bool or item['rarity']not in RARITIES:raise ValueError('Typed actual item offer flag and known rarity required.')
        before=previous.get(key);change='added'if before is None else'unchanged'if before==item else'changed'
        catalogue.append({'id':key,'name':item['name'],'rarity':item['rarity'],'can_offer':item['canSacrifice'],'change':change,'item':deepcopy(item),'before':deepcopy(before)})
    if(len(items),sum(v['canSacrifice']for v in items.values()),len(previous))!=(284,259,272):raise ValueError('Keep all current284 items,259 offer flags and the separate272-item baseline.')
    nodes=list(Document(raw.decode()).root.walk());tables=[n for n in nodes if n.tag=='table']
    if len(tables)!=1:raise ValueError('One complete documented exchange table required.')
    scenes={k:v for k,v in current['choiceScenes'].items()if v['title']=='回滚文明'};groups=[];positions={};original_choices={};unbound=[]
    for ri,tr in enumerate(n for n in tables[0].walk()if n.tag=='tr'):
        for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag=='td'):
            text=canonical(cell.text())
            matches={k:v for k,v in current['choices'].items()if v.get('title')and v.get('description')and text.startswith(canonical(v['title'])+canonical(v['description']))and(v['nextSceneId']is None or v['nextSceneId']in scenes)}
            if not matches:continue
            captions={(v['title'],v['description'])for v in matches.values()}
            if len(captions)!=1:raise ValueError('Do not merge differing current captions.')
            title,description=next(iter(captions));key=canonical(title)+canonical(description)
            loc={'file':receipt['selected_file'],'row':ri,'cell':ci,'cell_text_sha256':sha256(cell.text().encode()).hexdigest(),'attributes':cell.attrs,'document_text':cell.text().strip()}
            if key in positions:groups[positions[key]]['document_cells'].append(loc);continue
            ids=list(matches);quantity=None;resource=None;consumed=None
            p=canonical(description)
            if p=='获得1件收藏品':quantity=1;resource='收藏品'
            elif p=='获得1件零件':quantity=1;resource='零件'
            elif p=='消耗随机2件自然物，帮助它复原“文明”':consumed={'quantity':2,'resource':'自然物','random':True}
            associated=list(dict.fromkeys((v.get('displayData')or{}).get('itemId')for v in matches.values()if(v.get('displayData')or{}).get('itemId')in items))
            row={'id':str(len(groups)),'title':title,'description':description,'primary_candidate_ids':ids,'document_cells':[loc],'explicit_reward_quantity':quantity,'reward_resource':resource,'consumption_reference':consumed,'associated_relic_ids':associated,'actual_candidate_id':None,'actual_reward_pool':None,'actual_reward':None,'actual_quantity':None,'game_parent_scene_verified':False,'current_server_eligible':None}
            groups.append(row);positions[key]=len(groups)-1
            for cid,value in matches.items():
                original_choices[cid]=deepcopy(value)
                if value['nextSceneId']is None:unbound.append(cid)
    if(len(groups),sum(len(g['document_cells'])for g in groups),len(original_choices),len(scenes))!=(9,13,43,46):raise ValueError('Preserve every documented group, repeated cell and matching primary candidate.')
    if 'choice_leave'in original_choices:raise ValueError('An empty-description generic leave is not a full caption match.')
    result={'schema':'current_exchange_323_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','catalogue':catalogue,'document_groups':groups,'original_choices':original_choices,'related_scenes':deepcopy(scenes),'unbound_no_next_candidates':list(dict.fromkeys(unbound)),'source':receipt,'scope':{'current_relic_items':284,'can_offer':259,'cannot_offer':25,'baseline_relic_items':272,'added_items':sum(r['change']=='added'for r in catalogue),'effect_definition_rows':len(current['relics']),'offering_flags_are_reward_pool':False,'actual_inventory_known':False,'game_parents_restored':False,'current_server_verified':False},'actual_reward_pool':None,'actual_grant':None,'run_updated':False,'legacy_catalogue_replaced':False}
    data=encoded(result);names=[CURRENT,BASELINE,PACK+'/source-receipt.json',receipt['selected_file']];files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(data),'sha256':sha256(data).hexdigest()}
    manifest=encoded({'schema':'current_exchange_323_manifest_v1','game_commit':result['game_commit'],'files':files});return data,manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path);parser.add_argument('--check',action='store_true');args=parser.parse_args();data,manifest=build()
    if args.output_dir:
        args.output_dir.mkdir(parents=True,exist_ok=False);(args.output_dir/'current-exchange-reference.json').write_bytes(data);(args.output_dir/'runtime-manifest.json').write_bytes(manifest)
    if args.check:assert(ROOT/DATA).read_bytes()==data and(ROOT/PACK/'runtime-manifest.json').read_bytes()==manifest
    print(json.dumps({'items':284,'can_offer':259,'cannot_offer':25,'document_groups':9,'document_cells':13,'primary_text_candidates':43,'manifest_sha256':sha256(manifest).hexdigest()}))
