"""Complete current agency table; four random profession results remain alternatives."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse, json, re, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document, Node, canonical, encoded
ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-agency-340'; DATA = 'rouge/data/current-agency.json'
CURRENT = 'research/p3-expansion-313/current-topic.json'; BASELINE = 'research/p3-expansion-313/baseline-topic.json'
LEGACY = 'rouge/data/node-catalog.json'; ICONS = 'rouge/data/profession-icons.json'; TITLE = '临时中介所'
PAIRS = (('先锋','近卫'),('重装','辅助'),('医疗','狙击'),('术师','特种'))

def build(root=ROOT):
    root=Path(root); receipt=json.loads((root/PACK/'source-receipt.json').read_bytes()); raw=(root/receipt['selected_file']).read_bytes()
    if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes'] or sha256(raw).hexdigest()!=receipt['selected_sha256']: raise ValueError('Complete exact document required')
    current=json.loads((root/CURRENT).read_bytes())['details']; old=json.loads((root/BASELINE).read_bytes())['details']
    tables=[n for n in Document(raw.decode()).root.walk()if n.tag=='table']
    if len(tables)!=1: raise ValueError('One full agency table required')
    scenes={}; choices={}; originals={g:{}for g in('scenes','choices','items','stages')}; entry=None; active=None; pending=[]; random_loc=None
    for ri,tr in enumerate(n for n in tables[0].walk()if n.tag=='tr'):
        for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('th','td')):
            text=canonical(cell.text()); loc={'file':receipt['selected_file'],'row':ri,'cell':ci,'cell_text_sha256':sha256(cell.text().encode()).hexdigest()}
            if not text or text=='主选项': continue
            if text in('选项一（随机）','选项二','选项三'):
                if entry is None: raise ValueError('Options before entry')
                if pending: raise ValueError('Documented preceding options have no narrative')
                active=entry
                if text=='选项一（随机）': random_loc={**loc,'text':cell.text()}
                continue
            if cell.tag=='th':
                hits=[k for k,v in current['choiceScenes'].items()if v['title']==TITLE and canonical(v['description'])==text]
                if len(hits)!=1 or hits[0]in scenes: raise ValueError('Unique complete narrative required')
                sid=hits[0]
                if any(choices[cid]['next_scene_id']!=sid for cid in pending): raise ValueError('Narrative differs from complete nextSceneId')
                pending=[]; entry=entry or sid; active=sid; scenes[sid]={'id':sid,'event_id':'agency','choice_ids':[],'source':loc}; originals['scenes'][sid]=deepcopy(current['choiceScenes'][sid]); continue
            hits={k:v for k,v in current['choices'].items()if text==canonical(v['title']+(v.get('description')or'')) and current['choiceScenes'].get(v['nextSceneId'],{}).get('title')==TITLE}
            if len(hits)!=1 or active!=entry: raise ValueError('Every full root option must match uniquely')
            cid,v=next(iter(hits.items())); description=canonical(v['description']); pair=None
            if v['title']=='可靠的中介值得信任':
                match=re.fullmatch(r'获得(\d+)希望，招募(\d+)名直升的(\d+)星及以下(.+)或(.+)干员',description)
                if not match or tuple(map(int,match.group(1,2,3)))!=(2,1,5) or tuple(match.group(4,5))not in PAIRS: raise ValueError('Exact profession result required')
                role='promoted';pair=list(match.group(4,5))
            elif v['title']=='合格的帮手应当仔细挑选'and description=='随机获得一名6星临时招募干员':role='temporary_six'
            elif v['title']=='前行的速度更重要'and description=='多一事不如少一事':role='leave'
            else: raise ValueError('Unrecognized full choice')
            if v['type']!=('NEXT'if role=='leave'else'TRADE'): raise ValueError('Original type differs')
            title=v['title']+(' · '+'或'.join(pair) if pair else '')
            choices[cid]={'id':cid,'title':title,'description':v['description'],'event_id':'agency','scene_id':entry,'next_scene_id':v['nextSceneId'],'stage_ids':[],
                          'role':role,'profession_pair':pair,'hope_gain_reference':2 if pair else None,'recruit_count_reference':1 if role!='leave'else None,
                          'rarity_ceiling_reference':5 if pair else None,'exact_rarity_reference':6 if role=='temporary_six'else None,
                          'promoted_on_first_recruit_reference':True if pair else None,'actual_profession_offer':None,'actual_recruited':None,'actual_cultivation':None,
                          'actual_cost':None,'actual_received':None,'actual_eligible':None,'source':loc}
            scenes[entry]['choice_ids'].append(cid);choices[cid]['source_original_choice_id']=cid;originals['choices'][cid]=deepcopy(v);pending.append(cid)
    if pending or random_loc is None or (len(scenes),len(choices))!=(4,6):raise ValueError('Keep four scenes and all six options')
    if [tuple(c['profession_pair'])for c in choices.values()if c['role']=='promoted']!=list(PAIRS):raise ValueError('Keep all four alternatives in document order')
    for sid,s in scenes.items():
        if sid!=entry and s['choice_ids']:raise ValueError('No inferred extra recruit loop')
    catalogue=json.loads((root/LEGACY).read_bytes());legacy=next(v for v in catalogue['events']if v['title']==TITLE);links=[]
    for s in legacy['scenes']:
        for sid in s['game_scene_ids']:
            if sid not in originals['scenes']:continue
            before=canonical(s['description']);after=canonical(originals['scenes'][sid]['description'])
            if before==after:kind='exact_text'
            elif before.replace('……','......')==after:kind='document_ellipsis_only'
            else:raise ValueError('No fuzzy legacy/current link')
            links.append({'legacy_scene_key':s['key'],'current_original_scene_id':sid,'match_kind':kind,'legacy_complete_description':s['description'],'current_complete_description':originals['scenes'][sid]['description']})
    if len(links)!=4:raise ValueError('All four complete legacy scenes required')
    icon_catalogue=json.loads((root/ICONS).read_bytes());icons={}
    for pair in PAIRS:
        for label in pair:
            hits=[(k,v)for k,v in icon_catalogue['professions'].items()if v['label']==label]
            if len(hits)!=1:raise ValueError('Exact profession icon name required')
            key,record=hits[0];icons[label]={'key':key,**deepcopy(record)}
    result={'schema':'current_agency_340_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'agency','title':TITLE,'entry_scene_id':entry,'scene_ids':list(scenes),'choice_ids':list(choices)},
            'scenes':scenes,'choices':choices,'originals':originals,'profession_icons':icons,'random_profession_document_source':random_loc,
            'complete_document_table':True,'complete_game_option_pool':False,'actual_eligible':None,'actual_profession_offer':None,'run_updated':False,'source':receipt,
            'catalogue_binding':{'expected_legacy_event':legacy,'expected_summary':{k:deepcopy(legacy[k])for k in('id','title','node_types','floors','natural','natural_reason','entry')},'exact_scene_links':links,'current_event_id':'agency'},
            'complete_selected_record_comparison_to_baseline':{g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in rows.items()}for g,rows in originals.items()}}
    data=encoded(result);names=[CURRENT,BASELINE,LEGACY,ICONS,PACK+'/source-receipt.json',PACK+'/source-notes.json',receipt['selected_file']]
    files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(data),'sha256':sha256(data).hexdigest()}
    return data,encoded({'schema':'current_agency_340_manifest_v1','game_commit':result['game_commit'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();d,m=build()
    if a.check:
        if (ROOT/DATA).read_bytes()!=d or (ROOT/PACK/'runtime-manifest.json').read_bytes()!=m:raise ValueError('Build differs')
    else:(ROOT/DATA).write_bytes(d);(ROOT/PACK/'runtime-manifest.json').write_bytes(m)
    print(json.dumps({'scenes':4,'choices':6,'profession_pairs':4,'profession_icons':8,'manifest_sha256':sha256(m).hexdigest()}))
