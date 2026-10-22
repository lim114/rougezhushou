"""Full peace-guardian table and one-way movement exception, never its inverse."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-peace-343';DATA='rouge/data/current-peace.json'
CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json';LEGACY='rouge/data/node-catalog.json';ICONS='rouge/data/relic-icon-receipt.json'
EXCEPTION='rouge/data/peace-guardian-results.json'
EXCEPTION_FILES=[EXCEPTION,'research/p3-peace-guardian-results-291/prts-events-427904.html','research/p3-peace-guardian-results-291/prts-events-440271.html','research/p3-peace-guardian-results-291/original-records.json']
TITLE='和平守卫者'

def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes']or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Exact full table required')
    current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details'];tables=[n for n in Document(raw.decode()).root.walk()if n.tag=='table']
    if len(tables)!=1:raise ValueError('One full peace table required')
    scenes={};choices={};originals={g:{}for g in('scenes','choices','items','stages')};entry=None;active=None;pending=None;join=None
    roles={'加入队伍，接取悬赏':'join','离开队伍':'leave','守卫和平！':'move','从长计议':'mark'}
    for ri,tr in enumerate(n for n in tables[0].walk()if n.tag=='tr'):
        for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('th','td')):
            text=canonical(cell.text());loc={'file':receipt['selected_file'],'row':ri,'cell':ci,'cell_text_sha256':sha256(cell.text().encode()).hexdigest()}
            if not text or text=='主选项'or text in('分支1.1','分支1.2'):continue
            if text in('选项一','选项二'):active=entry;continue
            if text=='选项一分支':
                if join is None:raise ValueError('Branch before join')
                active=choices[join]['next_scene_id'];continue
            if cell.tag=='th':
                hits={k:v for k,v in current['choiceScenes'].items()if v['title']==TITLE and canonical(v['description'])==text}
                if len(hits)!=1:raise ValueError('Complete unique narrative required')
                sid,v=next(iter(hits.items()))
                if sid in scenes or(pending and choices[pending]['next_scene_id']!=sid):raise ValueError('Document followup differs')
                scenes[sid]={'id':sid,'choice_ids':[],'source':loc};originals['scenes'][sid]=deepcopy(v);entry=entry or sid;active=sid;pending=None;continue
            hits={k:v for k,v in current['choices'].items()if canonical(v['title']+(v['description']or''))==text}
            if len(hits)!=1 or active is None:raise ValueError('Complete unique choice required')
            cid,v=next(iter(hits.items()));role=roles[v['title']]
            if v['type']!={'join':'TRADE','leave':'NEXT','move':'MOVE','mark':'VISION'}[role]:raise ValueError('Choice type changed')
            if(role in('move','mark'))!=(v['nextSceneId']is None):raise ValueError('No fabricated next scene')
            choices[cid]={'id':cid,'title':v['title'],'description':v['description'],'scene_id':active,'next_scene_id':v['nextSceneId'],'role':role,'stage_ids':[],'actual_eligible':None,'actual_received':None,'actual_target':None,'actual_moved':None,'actual_marked':None,'source':loc}
            originals['choices'][cid]=deepcopy(v);scenes[active]['choice_ids'].append(cid);pending=cid if v['nextSceneId']else None
            if role=='join':join=cid
    if pending or(len(scenes),len(choices))!=(3,4)or len(scenes[entry]['choice_ids'])!=2:raise ValueError('Keep all3 scenes and4 options')
    joined=choices[join]['next_scene_id']
    if [choices[k]['role']for k in scenes[joined]['choice_ids']]!=['move','mark']:raise ValueError('Two documented post-join alternatives required')
    item_id=originals['choices'][join]['displayData']['itemId'];item=deepcopy(current['items'][item_id])
    if item['name']!='厄运火杆':raise ValueError('Exact named item required')
    originals['items'][item_id]=item;icon=next(v for v in json.loads((root/ICONS).read_bytes())['icons']if v['id']==item_id)
    picture=root/'rouge/data'/icon['file'];image=picture.read_bytes()
    if sha256(image).hexdigest()!=icon['sha256']:raise ValueError('Pinned item icon required at build')
    legacy=next(v for v in json.loads((root/LEGACY).read_bytes())['events']if v['title']==TITLE);links=[]
    for s in legacy['scenes']:
        for sid in s['game_scene_ids']:
            if sid not in originals['scenes']:continue
            if canonical(s['description'])!=canonical(originals['scenes'][sid]['description']):raise ValueError('No fuzzy scene binding')
            links.append({'legacy_scene_key':s['key'],'current_original_scene_id':sid,'legacy_complete_description':s['description'],'current_complete_description':originals['scenes'][sid]['description']})
    historical=json.loads((root/EXCEPTION).read_bytes());exception=historical['completion_exception_reference']
    if len(links)!=3 or exception['condition_text']!='若已完成当前层的【“居民”据点】作战则不会移动'or not exception['one_way_implication']or exception['converse_verified']or exception['negation_implies_successful_movement_verified']:raise ValueError('Only the documented one-way exception')
    move=next(v for v in originals['choices'].values()if v['type']=='MOVE')
    if canonical(historical['original_record']['title']+historical['original_record']['description'])!=canonical(move['title']+move['description']):raise ValueError('Exception must refer to this full current move option')
    result={'schema':'current_peace_343_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'peace','title':TITLE,'entry_scene_id':entry,'scene_ids':list(scenes),'choice_ids':list(choices)},'scenes':scenes,'choices':choices,'originals':originals,'joined_scene_id':joined,'movement_exception_reference':deepcopy(exception),'icon_reference':{**deepcopy(icon),'file':'rouge/data/'+icon['file'],'bytes':len(image)},'complete_document_table':True,'complete_game_option_pool':False,'actual_eligible':None,'actual_received':None,'run_updated':False,'source':receipt,'catalogue_binding':{'expected_legacy_event':legacy,'expected_summary':{k:deepcopy(legacy[k])for k in('id','title','node_types','floors','natural','natural_reason','entry')},'exact_scene_links':links,'current_event_id':'peace'},'complete_selected_record_comparison_to_baseline':{g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in values.items()}for g,values in originals.items()}}
    data=encoded(result);names=[CURRENT,BASELINE,LEGACY,ICONS,PACK+'/source-receipt.json',PACK+'/source-notes.json',receipt['selected_file'],*EXCEPTION_FILES]
    files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(data),'sha256':sha256(data).hexdigest()}
    return data,encoded({'schema':'current_peace_343_manifest_v1','game_commit':result['game_commit'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();d,m=build()
    if a.check:
        if(ROOT/DATA).read_bytes()!=d or(ROOT/PACK/'runtime-manifest.json').read_bytes()!=m:raise ValueError('Build differs')
    else:(ROOT/DATA).write_bytes(d);(ROOT/PACK/'runtime-manifest.json').write_bytes(m)
    print(json.dumps({'scenes':3,'choices':4,'manifest_sha256':sha256(m).hexdigest()}))
