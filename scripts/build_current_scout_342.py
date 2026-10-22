"""Bind the full scout table; departure, confirmation and return stay distinct."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-scout-342';DATA='rouge/data/current-scout.json'
CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json';LEGACY='rouge/data/node-catalog.json'
RETURN_DATA='rouge/data/expedition-results.json'
RETURN_FILES=[RETURN_DATA,'research/p3-expedition-results-297/source-manifest.json','research/p3-expedition-results-297/prts-events-427904.html','research/p3-expedition-results-297/prts-events-440271.html','research/p3-expedition-results-297/prts-main-433770.html','research/p3-expedition-results-297/original-records.json','research/p3-expedition-results-297/dom-bindings.json']
TITLE='未涉足之树'

def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes'] or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Full exact table required')
    current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details'];tables=[n for n in Document(raw.decode()).root.walk()if n.tag=='table']
    if len(tables)!=1:raise ValueError('One complete scout table required')
    scenes={};choices={};originals={g:{}for g in('scenes','choices','items','stages')};entry=None;active=None;pending=None
    roles={'尝试探索树的内部':'inside','尝试探索树的源头':'origin','休息':'rest','你们约好了会合的地点':'confirm'}
    for ri,tr in enumerate(n for n in tables[0].walk()if n.tag=='tr'):
        for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('th','td')):
            text=canonical(cell.text());loc={'file':receipt['selected_file'],'row':ri,'cell':ci,'cell_text_sha256':sha256(cell.text().encode()).hexdigest()}
            if not text or text=='主选项':continue
            if text in('选项一','选项二','选项三'):active=entry;continue
            if cell.tag=='th':
                hits={k:v for k,v in current['choiceScenes'].items()if v['title']==TITLE and canonical(v['description'])==text}
                if len(hits)!=1:raise ValueError('Unique complete narrative required')
                sid,v=next(iter(hits.items()))
                if sid in scenes or (pending and choices[pending]['next_scene_id']!=sid):raise ValueError('Document/current followup mismatch')
                scenes[sid]={'id':sid,'choice_ids':[],'source':loc};originals['scenes'][sid]=deepcopy(v);entry=entry or sid;active=sid;pending=None;continue
            hits={k:v for k,v in current['choices'].items()if canonical(v['title']+(v['description']or''))==text}
            if len(hits)!=1 or active is None:raise ValueError('Every full choice must match uniquely')
            cid,v=next(iter(hits.items()));role=roles[v['title']]
            if (role=='confirm')!=(v['nextSceneId']is None)or v['type']!=('EXPEDITION'if role in('inside','origin')else'TRADE'):raise ValueError('Original choice role changed')
            choices[cid]={'id':cid,'title':v['title'],'description':v['description'],'scene_id':active,'role':role,'next_scene_id':v['nextSceneId'],'stage_ids':[],'hope_reference':2 if role=='rest'else None,'effect_phase_reference':'on_choice'if role=='rest'else'on_return'if role in('inside','origin')else'confirmation_only','actual_received':None,'actual_selectable':None,'source':loc}
            scenes[active]['choice_ids'].append(cid);originals['choices'][cid]=deepcopy(v);pending=cid if v['nextSceneId']else None
    if pending or (len(scenes),len(choices))!=(4,4)or len(scenes[entry]['choice_ids'])!=3:raise ValueError('All four scenes and choices required')
    origin=next(c for c in choices.values()if c['role']=='origin');confirm=next(c for c in choices.values()if c['role']=='confirm')
    if confirm['scene_id']!=origin['next_scene_id']:raise ValueError('Confirm belongs only to source exploration in this document')
    historical=json.loads((root/RETURN_DATA).read_bytes());item=historical['item'];item_id=current['gameConst']['expedEndingRelic']
    if item_id!=item['id']or current['items'][item_id]!=item:raise ValueError('Current return item must match the documented reference')
    originals['items'][item_id]=deepcopy(item)
    returns={}
    for row in historical['rows']:
        cid=row['original_choice_id']
        if cid not in choices or canonical(row['choice_title']+row['choice_description'])!=canonical(originals['choices'][cid]['title']+originals['choices'][cid]['description']):raise ValueError('Old return reference must match complete current option')
        returns[cid]=deepcopy(row)
    if len(returns)!=3:raise ValueError('Three separate return references required')
    legacy=next(v for v in json.loads((root/LEGACY).read_bytes())['events']if v['title']==TITLE);links=[]
    for s in legacy['scenes']:
        for sid in s['game_scene_ids']:
            if sid not in originals['scenes']:continue
            a=canonical(s['description']);b=canonical(originals['scenes'][sid]['description'])
            if a!=b and a.replace('……','......')!=b:raise ValueError('No fuzzy legacy link')
            links.append({'legacy_scene_key':s['key'],'current_original_scene_id':sid,'legacy_complete_description':s['description'],'current_complete_description':originals['scenes'][sid]['description']})
    if len(links)!=4:raise ValueError('All four legacy scenes required')
    const={k:current['gameConst'][k]for k in('charSelectExpeditionConflictToast','expeditionSelectDescFormat','expedEndingRelic','expedEndingRelicDesc')}
    main_file='research/p3-expedition-results-297/prts-main-433770.html';main_text=Document((root/main_file).read_text('utf8')).root.text()
    unlock='完成游戏结局【强制重启】，解锁本结局的相关选项和收藏品。'
    origin_line='于第Ⅱ层到第IV层进入【先行一步】，选择【尝试探索树的源头】，并送出一名干员。'
    blocked_line='※该节点不会在第I，V，VI层出现。'
    if unlock+'\n'+origin_line not in main_text or blocked_line not in main_text:raise ValueError('Exact documented eligibility excerpts required')
    conditions={'source':main_file,'origin_prerequisite_quote':unlock,'origin_floor_and_dispatch_quote':origin_line,'node_excluded_floors_quote':blocked_line,'documented_regular_floors':[2,3,4],'origin_requires_first_ending_reference':True,'actual_account_unlocked':None,'complete_server_eligibility_known':False}
    result={'schema':'current_scout_342_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'scout','title':TITLE,'entry_scene_id':entry,'scene_ids':list(scenes),'choice_ids':list(choices)},'scenes':scenes,'choices':choices,'originals':originals,'current_game_const':const,'documented_return_references':returns,'return_explanation':deepcopy(historical['return_explanatory_reference']),'icon_reference':deepcopy(historical['icon_reference']),'complete_document_table':True,'complete_game_option_pool':False,'actual_eligible':None,'actual_returned':None,'run_updated':False,'source':receipt,'catalogue_binding':{'expected_legacy_event':legacy,'expected_summary':{k:deepcopy(legacy[k])for k in('id','title','node_types','floors','natural','natural_reason','entry')},'exact_scene_links':links,'current_event_id':'scout'},'complete_selected_record_comparison_to_baseline':{g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in values.items()}for g,values in originals.items()}}
    result['documented_conditions']=conditions
    data=encoded(result);names=[CURRENT,BASELINE,LEGACY,PACK+'/source-receipt.json',PACK+'/source-notes.json',receipt['selected_file'],*RETURN_FILES]
    files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(data),'sha256':sha256(data).hexdigest()}
    return data,encoded({'schema':'current_scout_342_manifest_v1','game_commit':result['game_commit'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();d,m=build()
    if a.check:
        if(ROOT/DATA).read_bytes()!=d or(ROOT/PACK/'runtime-manifest.json').read_bytes()!=m:raise ValueError('Build differs')
    else:(ROOT/DATA).write_bytes(d);(ROOT/PACK/'runtime-manifest.json').write_bytes(m)
    print(json.dumps({'scenes':4,'choices':4,'manifest_sha256':sha256(m).hexdigest()}))
