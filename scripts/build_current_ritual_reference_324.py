"""Current complete documented ritual/tears flows and material references."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded,plain

ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-ritual-324';DATA='rouge/data/current-ritual-reference.json'
CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json'
TITLES={'调谐仪式':'ritual','泪之聚落':'tears'}


def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());docs={}
    for name,rev in(('bwiki',352356),('prts',433770)):
        source=receipt[name];raw=(root/source['selected_file']).read_bytes()
        if source['revision']!=rev or len(raw)!=source['selected_bytes']or sha256(raw).hexdigest()!=source['selected_sha256']:raise ValueError('Exact named source excerpts required.')
        docs[name]=raw
    current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details']
    nodes=list(Document(docs['bwiki'].decode()).root.walk());events=[];scenes={};choices={};originals={g:{}for g in('choices','scenes','items','stages')}
    for title,event_id in TITLES.items():
        head=[n for n in nodes if n.tag=='h3'and n.attrs.get('id')==title]
        if len(head)!=1:raise ValueError('One exact event heading required.')
        table=next(n for n in nodes[nodes.index(head[0])+1:]if n.tag=='table');cells=[]
        for ri,tr in enumerate(n for n in table.walk()if n.tag=='tr'):
            for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('td','th')):cells.append((ri,ci,cell))
        entry=None;active=None;root_label=None;root_choices={};event_scenes=[];event_choices=[]
        def scene_ids(text):return[k for k,v in current['choiceScenes'].items()if v['title']==title and canonical(v['description'])==text]
        for index,(ri,ci,cell)in enumerate(cells):
            text=canonical(cell.text());loc={'file':receipt['bwiki']['selected_file'],'heading':title,'row':ri,'cell':ci,'text_sha256':sha256(cell.text().encode()).hexdigest(),'attributes':cell.attrs}
            if not text or text=='主选项':continue
            if re.fullmatch('选项[一二]',text):root_label=text;active=entry;continue
            if text=='选项一分支':
                if '选项一'not in root_choices:raise ValueError('No documented parent for option-one branch.')
                active=choices[root_choices['选项一']]['next_scene_id'];root_label=None;continue
            if text in('选项1分支后续','选项1分支后续后续'):continue
            if cell.tag=='th':
                ids=scene_ids(text)
                if len(ids)!=1 or ids[0]in scenes:raise ValueError('Narrative must match one unrepeated current scene.')
                sid=ids[0];active=sid
                if entry is None:entry=sid
                scenes[sid]={'id':sid,'event_id':event_id,'choice_ids':[],'source':loc};event_scenes.append(sid);originals['scenes'][sid]=deepcopy(current['choiceScenes'][sid]);continue
            following=next((scene_ids(canonical(c.text()))for _,_,c in cells[index+1:]if c.tag=='th'),[])
            matches={k:v for k,v in current['choices'].items()if v.get('title')and v.get('description')and text.startswith(canonical(v['title'])+canonical(v['description']))}
            if len(matches)>1 and len(following)==1:matches={k:v for k,v in matches.items()if v['nextSceneId']==following[0]}
            if len(matches)!=1 or active is None:raise ValueError('Full caption plus explicit following narrative must distinguish choice.')
            cid,value=next(iter(matches.items()))
            if cid in choices:raise ValueError('A current choice was repeated across document parents.')
            if value['nextSceneId']is not None and following!=[value['nextSceneId']]:raise ValueError('Exact nextSceneId disagrees with document narrative.')
            row={'id':cid,'event_id':event_id,'scene_id':active,'next_scene_id':value['nextSceneId'],'stage_ids':[],'item_id':None,'source':loc,'offered_item_id':None,'offered_quantity':None,'weakening_id':None,'actual_consumed':None,'actual_effect':None,'actual_attached':None}
            if event_id=='ritual'and re.fullmatch('交出(.+)，灾厄之口.+',canonical(value['description'])):
                match=re.fullmatch('交出(.+)，灾厄之口.+',canonical(value['description']))
                item_ids=[k for k,v in current['items'].items()if match and v['name']==match[1]and v['type']=='RELIC']
                if len(item_ids)!=1:raise ValueError('One exactly named offered relic required.')
                feature=(value.get('displayData')or{}).get('itemId')
                if feature not in current['items']or current['items'][feature]['type']!='FEATURE':raise ValueError('Exact feature reference required; not a received relic.')
                row.update(offered_item_id=item_ids[0],weakening_id=feature);originals['items'][item_ids[0]]=deepcopy(current['items'][item_ids[0]]);originals['items'][feature]=deepcopy(current['items'][feature])
            choices[cid]=row;scenes[active]['choice_ids'].append(cid);event_choices.append(cid);originals['choices'][cid]=deepcopy(value)
            if active==entry and root_label:root_choices[root_label]=cid
        if any(choices[k]['next_scene_id']not in event_scenes for k in event_choices if choices[k]['next_scene_id']is not None):raise ValueError('Document branch escaped its event.')
        events.append({'id':event_id,'title':title,'entry_scene_id':entry,'scene_ids':event_scenes,'choice_ids':event_choices})
    if(len(events),len(scenes),len(choices))!=(2,9,13):raise ValueError('Keep all nine scenes and thirteen choices.')
    weak={}
    for cid,row in choices.items():
        if row['weakening_id']:weak.setdefault(row['weakening_id'],[]).append(cid)
    if sorted(len(v)for v in weak.values())!=[2,2,2]:raise ValueError('Three exact two-way effects required.')
    for feature,ids in weak.items():
        primary=[choices[c]for c in ids if current['items'][choices[c]['offered_item_id']]['name']!='源私钥'];keys=[c for c in ids if current['items'][choices[c]['offered_item_id']]['name']=='源私钥']
        if len(primary)!=1 or len(keys)!=1:raise ValueError('One named relic and one alternative per effect required.')
        effect_item=primary[0]['offered_item_id']
        for cid in ids:choices[cid].update(effect_item_id=effect_item,alternative_choice_id=next(x for x in ids if x!=cid))
    for name in('畸症','无效验尸'):
        ids=[k for k,v in current['stages'].items()if v['name']==name]
        if len(ids)!=1:raise ValueError('One exact current related stage required.')
        originals['stages'][ids[0]]=deepcopy(current['stages'][ids[0]])
    source_choices={}
    for iid in('rogue_6_relic_final_4','rogue_6_relic_final_6'):
        ids=[k for k,v in current['choices'].items()if(v.get('displayData')or{}).get('itemId')==iid]
        if len(ids)!=1:raise ValueError('Unique explicit named reward reference required.')
        source_choices[iid]=ids[0];originals['choices'][ids[0]]=deepcopy(current['choices'][ids[0]])
    recipe=[k for k,v in current['choices'].items()if v['title']=='复原“文明”'and canonical(v['description'])=='消耗随机2件自然物，帮助它复原“文明”']
    if len(recipe)!=1:raise ValueError('Exact current two-natural-object recipe required.')
    originals['choices'][recipe[0]]=deepcopy(current['choices'][recipe[0]])
    prts_text=canonical(Document(docs['prts'].decode()).root.text())
    for fragment in('首次释放的灾厄之口不会摧毁','灾厄之口释放时不会封锁待部署区','灾厄之口的伤害降低','可以作弊以替换上述任一需求','无效验尸','调谐仪式'):
        if fragment not in prts_text:raise ValueError('Preserve independent concrete weakening/source documentation.')
    acquisitions={
        'rogue_6_relic_final_4':{'kind':'event','event_id':'tears','source_choice_id':source_choices['rogue_6_relic_final_4'],'description':'泪之聚落：选择倾囊资助，原文写明消耗全部源石锭。具体出现条件、实际领取及件数仍未完整核验。'},
        'rogue_6_relic_final_6':{'kind':'exchange','source_choice_id':source_choices['rogue_6_relic_final_6'],'recipe_choice_id':recipe[0],'description':'失与得·回滚文明：复原“文明”写明随机消耗2件自然物，等待结果关联该藏品。实际前置、发放与独立件数仍未知。'},
        'rogue_6_relic_final_5':{'kind':'battle','stage_id':'ro6_t_12','description':'资料记载：在标记为光明之末的作战中完成无效验尸后，可以选择获得；不是所有普通作战都会提供，实际发放条件仍待核对。'},
    }
    compatibility={group:{k:old[table].get(k)==v for k,v in originals[group].items()}for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages'))}
    result={'schema':'current_ritual_324_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','events':events,'scenes':scenes,'choices':choices,'originals':originals,'acquisitions':acquisitions,'related_boss_stage_id':'ro6_b_6','source':receipt,'complete_selected_record_comparison_to_baseline':compatibility,'game_parent_script_restored':False,'actual_consumed':None,'actual_weakened':None,'calculation_applied':False,'run_updated':False,'delivery_quantities_verified':False,'one_key_satisfies_three_steps':None,'current_server_eligible':None}
    data=encoded(result);names=[CURRENT,BASELINE,PACK+'/source-receipt.json',receipt['bwiki']['selected_file'],receipt['prts']['selected_file']];files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(data),'sha256':sha256(data).hexdigest()}
    manifest=encoded({'schema':'current_ritual_324_manifest_v1','game_commit':result['game_commit'],'files':files});return data,manifest


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);p.add_argument('--check',action='store_true');args=p.parse_args();data,manifest=build()
    if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=False);(args.output_dir/'current-ritual-reference.json').write_bytes(data);(args.output_dir/'runtime-manifest.json').write_bytes(manifest)
    if args.check:assert(ROOT/DATA).read_bytes()==data and(ROOT/PACK/'runtime-manifest.json').read_bytes()==manifest
    print(json.dumps({'events':2,'flow_scenes':9,'flow_choices':13,'paired_weakening_effects':3,'related_stage_refs':2,'manifest_sha256':sha256(manifest).hexdigest()}))
