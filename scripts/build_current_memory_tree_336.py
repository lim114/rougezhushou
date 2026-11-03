"""Rebuild the complete documented memory-tree event, including its notice."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-memory-tree-336'
DATA='rouge/data/current-memory-tree.json'
CURRENT='research/p3-expansion-313/current-topic.json'
BASELINE='research/p3-expansion-313/baseline-topic.json'
LEGACY='rouge/data/node-catalog.json'
TITLE='愈创之心'
ROLES={'紧紧拥抱愈创木':'action_cost','让这里有一个秋千':'random_parts','比对像素小猫和树干刻痕':'key_cost','检测此地有无危险':'controller_held','闭上眼感受宁静':'rest'}

def build(root=ROOT):
    root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes())
    raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes'] or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Exact complete event section required.')
    current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details']
    tables=[n for n in Document(raw.decode()).root.walk()if n.tag=='table']
    if len(tables)!=2 or canonical(tables[0].text())!='调查中':raise ValueError('Preserve investigation notice separately from full table.')
    scenes={};choices={};originals={g:{}for g in('scenes','choices','items','stages')};entry=None;active=None;pending=None
    for ri,tr in enumerate(n for n in tables[1].walk()if n.tag=='tr'):
        for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('th','td')):
            text=canonical(cell.text());loc={'file':receipt['selected_file'],'row':ri,'cell':ci,'cell_text_sha256':sha256(cell.text().encode()).hexdigest()}
            if not text or text=='主选项':continue
            if text in ('选项一','选项二','选项三','选项四','选项五'):active=entry;pending=None;continue
            if cell.tag=='th':
                hits=[k for k,v in current['choiceScenes'].items()if v['title']==TITLE and canonical(v['description'])==text]
                if len(hits)!=1 or hits[0]in scenes:raise ValueError('Complete unique narrative required.')
                sid=hits[0]
                if pending and choices[pending]['next_scene_id']!=sid:raise ValueError('Document followup contradicts original.')
                entry=entry or sid;active=sid;pending=None
                scenes[sid]={'id':sid,'event_id':'memorytree','choice_ids':[],'source':loc};originals['scenes'][sid]=deepcopy(current['choiceScenes'][sid]);continue
            hits={k:v for k,v in current['choices'].items()if v.get('title')in ROLES and text==canonical(v['title']+(v.get('description')or''))}
            if len(hits)!=1 or active!=entry:raise ValueError('Every full documented root option must match uniquely.')
            cid,v=next(iter(hits.items()));role=ROLES[v['title']]
            if v['type']!='TRADE':raise ValueError('Current complete choice type changed.')
            item=(v.get('displayData')or{}).get('itemId')
            if item:originals['items'][item]=deepcopy(current['items'][item])
            choices[cid]={'id':cid,'event_id':'memorytree','scene_id':entry,'title':v['title'],'description':v['description'],'role':role,'next_scene_id':v['nextSceneId'],'stage_ids':[],'reward_item_id':item if role in ('action_cost','random_parts','key_cost')else None,'reward_quantity':None,'action_point_cost':3 if role=='action_cost'else None,'random_processed_parts_cost':2 if role=='random_parts'else None,'action_point_gain':5 if role=='controller_held'else 1 if role=='rest'else None,'key_consumed_reference':role=='key_cost','key_quantity':None,'controller_held_reference':role=='controller_held','controller_consumed':None,'actual_eligible':None,'actual_received':None,'actual_consumed':None,'actual_region_transition':None,'source':loc}
            scenes[entry]['choice_ids'].append(cid);originals['choices'][cid]=deepcopy(v);pending=cid
    if pending or(len(scenes),len(choices))!=(6,5):raise ValueError('Preserve all six scenes and five independent options.')
    for c in choices.values():
        if c['next_scene_id']not in scenes or len(scenes[c['next_scene_id']]['choice_ids'])!=0:raise ValueError('No inferred extra followup.')
    for name,kind in [('源私钥','RELIC'),('笼控器','SCRAP')]:
        hits={k:v for k,v in current['items'].items()if v['name']==name and v['type']==kind}
        if len(hits)!=1:raise ValueError('Exact contextual item identity required.')
        originals['items'].update(deepcopy(hits))
    if len(originals['items'])!=4:raise ValueError('Preserve named reward, action resource and both distinct contextual items.')
    legacy=next(e for e in json.loads((root/LEGACY).read_bytes())['events']if e['title']==TITLE)
    links=[]
    for scene in legacy['scenes']:
        for sid in scene['game_scene_ids']:
            if sid not in scenes:continue
            before=canonical(scene['description']);after=canonical(originals['scenes'][sid]['description'])
            if before==after:kind='exact_text'
            elif before.replace('……','......')==after:kind='document_ellipsis_only'
            else:raise ValueError('Neither exact narrative nor explicit ellipsis spelling; no fuzzy admission.')
            links.append({'legacy_scene_key':scene['key'],'current_original_scene_id':sid,'match_kind':kind,'legacy_complete_description':scene['description'],'current_complete_description':originals['scenes'][sid]['description']})
    if len(links)!=6:raise ValueError('All six exact old/current scene identities required.')
    comparison={g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in rows.items()}for g,rows in originals.items()}
    d={'schema':'current_memory_tree_336_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'memorytree','title':TITLE,'entry_scene_id':entry,'scene_ids':list(scenes),'choice_ids':list(choices)},'scenes':scenes,'choices':choices,'originals':originals,'source':receipt,'source_notes':json.loads((root/PACK/'source-notes.json').read_bytes()),'document_investigation_notice_retained':True,'complete_selected_record_comparison_to_baseline':comparison,'catalogue_binding':{'expected_legacy_event':legacy,'expected_summary':{k:deepcopy(legacy[k])for k in('id','title','node_types','floors','natural','natural_reason','entry')},'exact_scene_links':links,'current_event_id':'memorytree'},'complete_document_table':True,'complete_game_option_pool':False,'game_parent_script_restored':False,'actual_eligible':None,'run_updated':False}
    blob=encoded(d);names=[CURRENT,BASELINE,LEGACY,PACK+'/source-receipt.json',PACK+'/source-notes.json',receipt['selected_file']]
    files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(blob),'sha256':sha256(blob).hexdigest()}
    return blob,encoded({'schema':'current_memory_tree_336_manifest_v1','game_commit':d['game_commit'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);p.add_argument('--check',action='store_true');a=p.parse_args();d,m=build()
    if a.output_dir:a.output_dir.mkdir(parents=True,exist_ok=False);(a.output_dir/'current-memory-tree.json').write_bytes(d);(a.output_dir/'runtime-manifest.json').write_bytes(m)
    if a.check:assert(ROOT/DATA).read_bytes()==d and(ROOT/PACK/'runtime-manifest.json').read_bytes()==m
    print(json.dumps({'scenes':6,'choices':5,'items':4,'manifest_sha256':sha256(m).hexdigest()}))
