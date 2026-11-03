"""Preserve documentary exchange phases and every exact original separately."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-reconstruction-344';DATA='rouge/data/current-reconstruction.json'
CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json';LEGACY='rouge/data/node-catalog.json';ICONS='rouge/data/relic-icon-receipt.json';MAIN='research/p3-future-region-effects-300/prts-main-433770.html';TITLE='回滚文明'
LABELS={1:'最初对话',3:'首次藏品转换后的对话',5:'领取藏品后是否继续',7:'首次零件转换后的对话',9:'领取零件后是否继续',11:'等待复原文明',13:'取得焚毁文明后的对话',15:'离开后的对话',17:'再次藏品转换后的对话',19:'再次领取藏品后的结束对话',21:'结束藏品交换后的对话',23:'再次零件转换后的对话',25:'再次领取零件后的结束对话',27:'结束零件交换后的对话'}

def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes']or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Exact complete table required')
    current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details'];all_scenes={k:deepcopy(v)for k,v in current['choiceScenes'].items()if v['title']==TITLE}
    tables=[n for n in Document(raw.decode()).root.walk()if n.tag=='table']
    if len(tables)!=1:raise ValueError('One complete reconstruction table required')
    scenes={};choices={};entry=None;active=None;pending=None;branch=None;literal_candidates={}
    for ri,tr in enumerate(n for n in tables[0].walk()if n.tag=='tr'):
        for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('th','td')):
            full=canonical(cell.text());loc={'file':receipt['selected_file'],'row':ri,'cell':ci,'cell_text_sha256':sha256(cell.text().encode()).hexdigest()}
            if not full or full=='主选项':continue
            if full in('选项一','选项二','选项三','选项四'):active=entry;continue
            if full in('选项一分支','选项二分支'):branch='relic'if full=='选项一分支'else'part';active='doc:5'if branch=='relic'else'doc:9';continue
            if full in('分支1','分支2'):
                if branch is None:raise ValueError('Branch before its documented heading')
                active='doc:5'if branch=='relic'else'doc:9';continue
            if cell.tag=='th':
                ids=[k for k,v in all_scenes.items()if canonical(v['description'])==full]
                if not ids or ri not in LABELS:raise ValueError('Every full narrative must match current originals')
                sid='doc:'+str(ri);scenes[sid]={'id':sid,'label':LABELS[ri],'description':cell.text().strip(),'source_scene_ids':ids,'choice_ids':[],'source':loc}
                if pending:choices[pending]['next_scene_id']=sid
                entry=entry or sid;active=sid;pending=None;continue
            text=full.split('◈')[0];hits={k:deepcopy(v)for k,v in current['choices'].items()if canonical(v['title']+(v['description']or''))==text and(v['nextSceneId']in all_scenes or(v['nextSceneId']is None and v['type']=='SACRIFICE'))}
            if not hits or active not in scenes:raise ValueError('Every complete documented option needs original candidates')
            signature={(v['title'],v['description'],v['type'])for v in hits.values()}
            if len(signature)!=1:raise ValueError('Do not merge distinct original wording/type')
            v=next(iter(hits.values()));title=v['title'];role={'复原藏品':'choose_relic','复原零件':'choose_part','复原“文明”':'restore','等待结果':'claim_civil','离开':'leave','接过藏品':'claim_relic','接过零件':'claim_part','有点可疑':'decline'}.get(title)
            if title=='继续赞助它':role='continue_'+branch
            if role is None:raise ValueError('Unknown documented role')
            cid='doc-choice:'+str(ri);choices[cid]={'id':cid,'title':title,'description':v['description'],'scene_id':active,'next_scene_id':None,'stage_ids':[],'role':role,'phase':2 if branch and role.startswith(('continue_','claim_','decline'))else 1,'variant_ids':list(hits),'source_only':False,'natural_cost_reference':2 if role=='restore'else None,'reward_quantity_reference':1 if role in('claim_relic','claim_part')else None,'actual_variant':None,'actual_received':None,'source':loc}
            scenes[active]['choice_ids'].append(cid);literal_candidates.update(hits);pending=cid
    if pending or(len(scenes),len(choices))!=(14,13):raise ValueError('Keep14 document contexts and13 option occurrences')
    for c in choices.values():
        after=canonical(scenes[c['next_scene_id']]['description']);ids=[k for k in c['variant_ids']if literal_candidates[k]['nextSceneId']is None or canonical(all_scenes.get(literal_candidates[k]['nextSceneId'],{}).get('description',''))==after]
        if not ids:raise ValueError('Document next narrative must agree with every retained explicit destination')
        c['variant_ids']=ids;c['document_next_is_original_next']=all(literal_candidates[k]['nextSceneId']is not None for k in ids)
    all_choices={k:deepcopy(v)for k,v in current['choices'].items()if v['nextSceneId']in all_scenes};all_choices.update({k:literal_candidates[k]for c in choices.values()for k in c['variant_ids']})
    association={k:'explicit_destination_scene'if v['nextSceneId']in all_scenes else'full_literal_sacrifice_candidate'for k,v in all_choices.items()}
    if(len(all_scenes),len(all_choices),sum(v=='full_literal_sacrifice_candidate'for v in association.values()))!=(46,44,8):raise ValueError('Preserve46 scenes,36 explicit choices and8 no-destination candidates')
    if set(all_scenes)!={k for s in scenes.values()for k in s['source_scene_ids']}:raise ValueError('Every original narrative must be accounted for')
    item_ids={v['displayData']['itemId']for v in all_choices.values()if v['title']=='等待结果'}
    if len(item_ids)!=1:raise ValueError('Unique named reward pointer required')
    item_id=next(iter(item_ids));item=deepcopy(current['items'][item_id])
    if item['name']!='焚毁“文明”':raise ValueError('Exact named reward required')
    icon=next(v for v in json.loads((root/ICONS).read_bytes())['icons']if v['id']==item_id);picture=(root/'rouge/data'/icon['file']).read_bytes()
    if sha256(picture).hexdigest()!=icon['sha256']:raise ValueError('Pinned reward picture required at build')
    main_text=Document((root/MAIN).read_text('utf8')).root.text();quotes=['在点亮【生命游戏】的“声带”节点后，还可以交换零件。','在点亮【生命游戏】的“手掌”节点后，交换次数+1，但只能交换和首次交换相同类型的物品。','※交换后可获得的物品/提供的选项受给出的物品稀有度影响。','※该节点不会在第I，VI层出现。']
    if any(t not in main_text for t in quotes):raise ValueError('Complete documented prerequisite wording required')
    legacy=next(v for v in json.loads((root/LEGACY).read_bytes())['events']if v['title']==TITLE);links=[]
    for s in legacy['scenes']:
        for sid in s['game_scene_ids']:
            if sid not in all_scenes:continue
            a=canonical(s['description']);b=canonical(all_scenes[sid]['description'])
            if a!=b and a.replace('……','......')!=b:raise ValueError('No fuzzy legacy narrative binding')
            links.append({'legacy_scene_key':s['key'],'current_original_scene_id':sid,'legacy_complete_description':s['description'],'current_complete_description':all_scenes[sid]['description']})
    if len(links)!=42:raise ValueError('All42 exact legacy links required')
    originals={'scenes':all_scenes,'choices':all_choices,'items':{item_id:item},'stages':{}}
    result={'schema':'current_reconstruction_344_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'reconstruction','title':TITLE,'entry_scene_id':entry,'scene_ids':list(scenes),'choice_ids':list(choices)},'scenes':scenes,'choices':choices,'originals':originals,'original_choice_association':association,'documented_conditions':{'source':MAIN,'quotes':quotes,'actual_unlocked':None,'complete_server_eligibility_known':False},'icon_reference':{**deepcopy(icon),'file':'rouge/data/'+icon['file'],'bytes':len(picture)},'complete_document_table':True,'complete_game_option_pool':False,'actual_eligible':None,'run_updated':False,'source':receipt,'catalogue_binding':{'expected_legacy_event':legacy,'expected_summary':{k:deepcopy(legacy[k])for k in('id','title','node_types','floors','natural','natural_reason','entry')},'exact_scene_links':links,'current_event_id':'reconstruction'},'complete_selected_record_comparison_to_baseline':{g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in values.items()}for g,values in originals.items()}}
    data=encoded(result);names=[CURRENT,BASELINE,LEGACY,ICONS,MAIN,PACK+'/source-receipt.json',PACK+'/source-notes.json',receipt['selected_file']]
    files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(data),'sha256':sha256(data).hexdigest()}
    return data,encoded({'schema':'current_reconstruction_344_manifest_v1','game_commit':result['game_commit'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();d,m=build()
    if a.check:
        if(ROOT/DATA).read_bytes()!=d or(ROOT/PACK/'runtime-manifest.json').read_bytes()!=m:raise ValueError('Build differs')
    else:(ROOT/DATA).write_bytes(d);(ROOT/PACK/'runtime-manifest.json').write_bytes(m)
    print(json.dumps({'original_scenes':46,'original_choices':44,'document_contexts':14,'document_options':13,'manifest_sha256':sha256(m).hexdigest()}))
