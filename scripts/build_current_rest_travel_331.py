"""Whole rest/travel documents; text aliases never restore actual parent scripts."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-rest-travel-331';DATA='rouge/data/current-rest-travel.json';CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json'
TITLES=('金色凝滞','三重身')
EFFECTS={
 '获得3目标生命值上限':{'quantity':3,'resource':'目标生命值上限'},
 '可携带干员+1':{'quantity':1,'resource':'可携带干员数'},
 '获得3希望':{'quantity':3,'resource':'希望'},
 '获得高级物资配给券':{'quantity':None,'resource':'高级物资配给券'},
 '获得2行动力':{'quantity':2,'resource':'行动力'},
 '零件箱容量+1':{'quantity':1,'resource':'零件箱容量'},
 '使用留存的招募券':{'quantity':None,'resource':'使用留存招募券'},
 '获得1件珍贵的加工品，保留目前行动力，直接进入下一区域':{'quantity':1,'resource':'加工品','quality':'珍贵','pool':None,'retain_ap_reference':True,'enter_next_region_reference':True},
 '多一事不如少一事':None,
 '保留行动力，进入下一区域':{'quantity':None,'resource':'进入下一区域','retain_ap_reference':True,'enter_next_region_reference':True}}

def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes']or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Two complete exact event tables required.')
    current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details'];nodes=list(Document(raw.decode()).root.walk());events={};scenes={};choices={};originals={g:{}for g in('scenes','choices','items','stages')};lookup={'scenes':{},'choices':{}}
    for title in TITLES:
        head=next(n for n in nodes if n.tag=='h3'and n.attrs.get('id')==title);table=next(n for n in nodes[nodes.index(head)+1:]if n.tag in('table','h3'));raw_scenes={k:v for k,v in current['choiceScenes'].items()if v['title']==title};by_text={}
        for sid,v in raw_scenes.items():by_text.setdefault(canonical(v['description']),[]).append(sid)
        def document_scene(text):return 'document-scene:'+sha256((title+'\0'+text).encode()).hexdigest()
        entry=None;active=None;pending=None;es=[];ec=[];notes=[]
        for ri,tr in enumerate(n for n in table.walk()if n.tag=='tr'):
            for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('td','th')):
                text=canonical(cell.text());loc={'file':receipt['selected_file'],'heading':title,'row':ri,'cell':ci,'attributes':cell.attrs,'text':cell.text(),'text_sha256':sha256(cell.text().encode()).hexdigest()}
                if not text:continue
                if text in('主选项','主选项（随机3个）')or text=='◈本事件有三张CG，随机出现':notes.append(loc);continue
                if re.fullmatch('选项[一二三四五六七]',text):
                    if entry is None:raise ValueError('Entry must precede root option label.')
                    active=entry;pending=None;continue
                if cell.tag=='th':
                    if text not in by_text:raise ValueError('Narrative must match all current exact aliases.')
                    group=document_scene(text)
                    if pending is not None and choices[pending]['next_scene_id']!=group:raise ValueError('Current explicit next conflicts with document prose.')
                    if group in scenes:raise ValueError('Repeated narrative needs explicit context handling.')
                    if entry is None:entry=group
                    active=group;pending=None;es.append(group);scenes[group]={'id':group,'event_id':title,'description':cell.text(),'original_scene_ids':by_text[text],'choice_ids':[],'source_cells':[loc]}
                    for sid in by_text[text]:originals['scenes'][sid]=deepcopy(raw_scenes[sid]);lookup['scenes'][sid]={'event_id':title,'scene_id':group,'choice_id':None}
                    continue
                matches={k:v for k,v in current['choices'].items()if v.get('title')and v.get('description')and text==canonical(v['title'])+canonical(v['description'])and(v['nextSceneId']in raw_scenes or v['nextSceneId']is None)}
                if not matches or active is None:raise ValueError('Every full caption needs exact candidates; no inferred ID parent.')
                signatures={(v['title'],v['description'],v['type'])for v in matches.values()}
                targets={document_scene(canonical(raw_scenes[v['nextSceneId']]['description']))if v['nextSceneId']is not None else None for v in matches.values()}
                if len(signatures)!=1 or len(targets)!=1:raise ValueError('Same-caption aliases must agree on processing and prose destination.')
                first=next(iter(matches.values()));description=canonical(first['description'])
                if description not in EFFECTS:raise ValueError('No unverified effect parser fallback.')
                gid='document-choice:'+sha256((title+'\0'+text).encode()).hexdigest();target=next(iter(targets));item_ids={(v.get('displayData')or{}).get('itemId')for v in matches.values()}
                for iid in item_ids:
                    if iid is not None:
                        if iid not in current['items']:raise ValueError('Referenced display item missing.')
                        originals['items'][iid]=deepcopy(current['items'][iid])
                row={'id':gid,'event_id':title,'title':first['title'],'description':first['description'],'scene_id':active,'next_scene_id':target,'next_is_document_narrative_only':True,'original_next_scene_ids':list(dict.fromkeys(v['nextSceneId']for v in matches.values())),'variant_ids':list(matches),'display_item_ids':sorted(i for i in item_ids if i is not None),'display_item_includes_none':None in item_ids,'stage_ids':[],'effect_reference':deepcopy(EFFECTS[description]),'processing_type':first['type'],'actual_variant_id':None,'actual_parent_scene_id':None,'actual_eligible':None,'actual_received':None,'actual_departed':None,'actual_consumed':None,'source_cells':[loc]};choices[gid]=row;scenes[active]['choice_ids'].append(gid);ec.append(gid);originals['choices'].update({k:deepcopy(v)for k,v in matches.items()})
                for cid in matches:lookup['choices'][cid]={'event_id':title,'scene_id':active,'choice_id':gid}
                pending=gid if target is not None else None
        if pending is not None:raise ValueError('Explicit narrative followup missing from full document.')
        if set(raw_scenes)!=set(sid for gid in es for sid in scenes[gid]['original_scene_ids']):raise ValueError('All current event scene aliases must remain available.')
        expected={k:v for k,v in current['choices'].items()if v['nextSceneId']in raw_scenes}
        if any(originals['choices'].get(k)!=v for k,v in expected.items()):raise ValueError('Every current same-title explicit-next choice must remain available.')
        events[title]={'id':title,'title':title,'entry_scene_id':entry,'scene_ids':es,'choice_ids':ec,'document_notes':notes,'documented_random_option_count':3 if title=='金色凝滞'else None,'random_menu_membership_complete':False,'stashed_ticket_shared_random_group_verified':False,'documented_picture_count':3 if title=='三重身'else None,'backgrounds':list(dict.fromkeys(v['background']for v in raw_scenes.values())),'actual_menu':None,'actual_background':None}
    counts={'events':len(events),'document_scenes':len(scenes),'original_scenes':len(originals['scenes']),'document_choices':len(choices),'original_choices':len(originals['choices']),'display_items':len(originals['items']),'travel_accept_variants':sum(len(c['variant_ids'])for c in choices.values()if c['title']=='接受它的提议'),'travel_exit_variants':sum(len(c['variant_ids'])for c in choices.values()if c['processing_type']=='ZONE_END')}
    if counts!={'events':2,'document_scenes':11,'original_scenes':17,'document_choices':10,'original_choices':19,'display_items':6,'travel_accept_variants':6,'travel_exit_variants':3}:raise ValueError('Incomplete rest/travel scope: '+str(counts))
    data={'schema':'current_rest_travel_331_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','events':events,'scenes':scenes,'choices':choices,'originals':originals,'lookup':lookup,'counts':counts,'source':receipt,'complete_selected_record_comparison_to_baseline':{g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in records.items()}for g,records in originals.items()},'complete_document_tables':True,'complete_game_option_pool':False,'game_parent_script_restored':False,'actual_eligible':None,'actual_random_menu':None,'run_updated':False}
    blob=encoded(data);names=[CURRENT,BASELINE,PACK+'/source-receipt.json',receipt['selected_file']];files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(blob),'sha256':sha256(blob).hexdigest()};return blob,encoded({'schema':'current_rest_travel_331_manifest_v1','game_commit':data['game_commit'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);p.add_argument('--check',action='store_true');args=p.parse_args();d,m=build()
    if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=False);(args.output_dir/'current-rest-travel.json').write_bytes(d);(args.output_dir/'runtime-manifest.json').write_bytes(m)
    if args.check:assert(ROOT/DATA).read_bytes()==d and(ROOT/PACK/'runtime-manifest.json').read_bytes()==m
    print(json.dumps({'counts':json.loads(d)['counts'],'manifest_sha256':sha256(m).hexdigest()}))
