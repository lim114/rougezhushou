"""Full unattended-shop table, preserving same-text current scene aliases."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-unattended-shop-330';DATA='rouge/data/current-unattended-shop.json';CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json'

def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes']or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Whole exact unattended-shop table required.')
    current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details'];originals={g:{}for g in('scenes','choices','items','stages')};table=next(n for n in Document(raw.decode()).root.walk()if n.tag=='table');cells=[];captions=[];scene_sources={};entry=None
    event_scenes={k:v for k,v in current['choiceScenes'].items()if v['title']=='无人商店'}
    for ri,tr in enumerate(n for n in table.walk()if n.tag=='tr'):
        for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('th','td')):
            text=canonical(cell.text());loc={'file':receipt['selected_file'],'row':ri,'cell':ci,'attributes':cell.attrs,'text':cell.text(),'text_sha256':sha256(cell.text().encode()).hexdigest()};cells.append((cell,text,loc))
            if not text:continue
            if cell.tag=='th':
                matches=[k for k,v in event_scenes.items()if canonical(v['description'])==text]
                if not matches:raise ValueError('Every narrative must match current exact text; do not drop aliases.')
                if entry is None:
                    if len(matches)!=1:raise ValueError('Entry narrative must be unique.')
                    entry=matches[0]
                for sid in matches:scene_sources.setdefault(sid,[]).append(loc);originals['scenes'][sid]=deepcopy(event_scenes[sid])
            elif text=='主选项'or re.fullmatch('选项[一二三四]',text):continue
            else:captions.append((cell,text,loc))
    if set(originals['scenes'])!=set(event_scenes):raise ValueError('Do not omit same-title original scene records.')
    ids=[k for k,v in current['items'].items()if v['name']=='四叶草化石'and v['type']=='RELIC']
    if len(ids)!=1:raise ValueError('Exact named held relic required.')
    fossil=ids[0];originals['items'][fossil]=deepcopy(current['items'][fossil]);choices={};targets=set()
    for cell,text,loc in captions:
        ix=next(i for i,(n,_,_)in enumerate(cells)if n is cell);next_text=next((t for n,t,_ in cells[ix+1:]if n.tag=='th'),None)
        matches={k:v for k,v in current['choices'].items()if v.get('title')and v.get('description')and text==canonical(v['title'])+canonical(v['description'])and v['nextSceneId']in event_scenes and canonical(event_scenes[v['nextSceneId']]['description'])==next_text}
        if not matches:raise ValueError('Every complete caption needs exact current variants and documented next narrative.')
        signatures={(v['title'],v['description'],v['type'])for v in matches.values()}
        if len(signatures)!=1:raise ValueError('Do not collapse records with different captions or processing types.')
        first=next(iter(matches.values()));destinations=list(dict.fromkeys(v['nextSceneId']for v in matches.values()));targets.update(destinations);gid='shop-choice:'+sha256(text.encode()).hexdigest();cost=canonical(first['description'])=='消耗4源石锭，换一批更高级的收藏品';held=canonical(first['description'])=='持有四叶草化石，获得1件收藏品'
        if not(cost or held or canonical(first['description'])=='获得1件收藏品'):raise ValueError('Unexpected documented reward/cost, do not guess parsing.')
        choices[gid]={'id':gid,'event_id':'shop','title':first['title'],'description':first['description'],'scene_id':entry,'variant_ids':list(matches),'actual_variant_id':None,'next_scene_ids':destinations,'next_scene_id':destinations[0]if len(destinations)==1 else None,'stage_ids':[],'source_cells':[loc],'gold_cost_reference':4 if cost else None,'required_relic_id':fossil if held else None,'reward_quantity_reference':None if cost else 1,'complete_reward_pool':None,'actual_eligible':None,'actual_consumed':None,'actual_received':None,'actual_parent_scene_id':None};originals['choices'].update({k:deepcopy(v)for k,v in matches.items()})
    all_choices={k:v for k,v in current['choices'].items()if v['nextSceneId']in event_scenes}
    if originals['choices']!=all_choices:raise ValueError('Every current original choice must remain available as reference.')
    labels={entry:'最初对话 · 无人商店'};reward=next(c for c in choices.values()if c['title']=='搬一个大桶')['next_scene_id'];labels[reward]='搬运后领取报酬的对话'
    ambiguous=next(c for c in choices.values()if c['gold_cost_reference']is not None)['next_scene_ids']
    if len(ambiguous)!=2:raise ValueError('Two distinct same-text opening records must stay separate.')
    for label,sid in zip(('A','B'),ambiguous):labels[sid]='开桶后续记录'+label+'（文案相同，顺序未确认）'
    scenes={sid:{'id':sid,'event_id':'shop','label':labels[sid],'choice_ids':list(choices)if sid==entry else[],'source_cells':sources}for sid,sources in scene_sources.items()};counts={'events':1,'scenes':len(scenes),'document_choices':len(choices),'original_choices':len(originals['choices']),'held_relic_choices':sum(c['required_relic_id']is not None for c in choices.values()),'fixed_gold_choices':sum(c['gold_cost_reference']is not None for c in choices.values()),'same_text_followup_records':len(ambiguous),'items':len(originals['items'])}
    if counts!={'events':1,'scenes':4,'document_choices':4,'original_choices':11,'held_relic_choices':1,'fixed_gold_choices':1,'same_text_followup_records':2,'items':1}:raise ValueError('Incomplete shop scope: '+str(counts))
    data={'schema':'current_unattended_shop_330_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'shop','title':'无人商店','entry_scene_id':entry,'scene_ids':list(scenes),'choice_ids':list(choices)},'scenes':scenes,'choices':choices,'originals':originals,'counts':counts,'source':receipt,'complete_selected_record_comparison_to_baseline':{g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in records.items()}for g,records in originals.items()},'complete_document_table':True,'complete_game_option_pool':False,'game_parent_script_restored':False,'upgrade_order_verified':False,'reward_pool_verified':False,'actual_variant':None,'actual_eligible':None,'run_updated':False}
    blob=encoded(data);names=[CURRENT,BASELINE,PACK+'/source-receipt.json',receipt['selected_file']];files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(blob),'sha256':sha256(blob).hexdigest()};return blob,encoded({'schema':'current_unattended_shop_330_manifest_v1','game_commit':data['game_commit'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);p.add_argument('--check',action='store_true');args=p.parse_args();d,m=build()
    if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=False);(args.output_dir/'current-unattended-shop.json').write_bytes(d);(args.output_dir/'runtime-manifest.json').write_bytes(m)
    if args.check:assert(ROOT/DATA).read_bytes()==d and(ROOT/PACK/'runtime-manifest.json').read_bytes()==m
    print(json.dumps({'counts':json.loads(d)['counts'],'manifest_sha256':sha256(m).hexdigest()}))
