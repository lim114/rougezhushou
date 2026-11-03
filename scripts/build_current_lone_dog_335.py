"""Complete lone-dog table; movement and vision remain different reference actions."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-lone-dog-335';DATA='rouge/data/current-lone-dog.json';CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json';LEGACY='rouge/data/node-catalog.json'
def build(root=ROOT):
 root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
 if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes']or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Whole exact lone-dog table required.')
 current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details'];table=next(n for n in Document(raw.decode()).root.walk()if n.tag=='table');scenes={};choices={};originals={g:{}for g in('scenes','choices','items','stages')};entry=None;active=None;pending=None;approach=None
 for ri,tr in enumerate(n for n in table.walk()if n.tag=='tr'):
  for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('td','th')):
   text=canonical(cell.text());loc={'file':receipt['selected_file'],'row':ri,'cell':ci,'attributes':cell.attrs,'text':cell.text(),'sha256':sha256(cell.text().encode()).hexdigest()}
   if not text or text=='主选项':continue
   if text=='选项一分支':
    if approach is None:raise ValueError('Explicit approach branch required.')
    active=current['choices'][approach]['nextSceneId'];pending=None;continue
   if re.fullmatch(r'选项[一二]',text):active=entry;pending=None;continue
   if re.fullmatch(r'分支1\.[12]',text):continue
   if cell.tag=='th':
    hits=[k for k,v in current['choiceScenes'].items()if v['title']=='独活'and canonical(v['description'])==text]
    if len(hits)!=1:raise ValueError('Unique complete original narrative required.')
    sid=hits[0]
    if pending is not None and current['choices'][pending]['nextSceneId']!=sid:raise ValueError('Document followup contradicts original.')
    if sid in scenes:raise ValueError('Duplicate narrative needs separate handling.')
    entry=entry or sid;active=sid;pending=None;scenes[sid]={'id':sid,'event_id':'dog','choice_ids':[],'source':loc};originals['scenes'][sid]=deepcopy(current['choiceScenes'][sid]);continue
   matches={k:v for k,v in current['choices'].items()if v['title']and v['description']and text==canonical(v['title']+v['description'])}
   if len(matches)!=1 or active is None:raise ValueError('Unique full caption required, no omitted branch.')
   cid,v=next(iter(matches.items()));target=v['nextSceneId'];role={'去看看小狗':'approach','小心为上':'leave','跟随小狗':'move','请小狗告知营地位置':'mark'}.get(v['title'])
   if role is None:raise ValueError('Unreviewed action.')
   if role=='approach':approach=cid
   if role in('move','mark')and(v['type']!=('MOVE'if role=='move'else'VISION')or target is not None):raise ValueError('Do not conflate movement, marking, or an invented next scene.')
   item=(v.get('displayData')or{}).get('itemId')
   if item:
    if current['items'][item]['name']!='同行者'or current['items'][item]['type']!='RELIC':raise ValueError('Exact named relic required.')
    originals['items'][item]=deepcopy(current['items'][item])
   choices[cid]={'id':cid,'event_id':'dog','scene_id':active,'title':v['title'],'description':v['description'],'role':role,'next_scene_id':target,'stage_ids':[],'item_id':item,'quantity_reference':None,'target_node_type':'应急助力'if role in('move','mark')else None,'actual_target_node_id':None,'actual_marked':None,'actual_moved':None,'actual_recruited':None,'actual_received':None,'actual_eligible':None,'source':loc};scenes[active]['choice_ids'].append(cid);originals['choices'][cid]=deepcopy(v);pending=cid if target else None
 if pending is not None or(len(scenes),len(choices),len(originals['items']))!=(3,4,1):raise ValueError('Preserve complete3 narratives and4 actions.')
 if any(c['next_scene_id']is not None and c['next_scene_id']not in scenes for c in choices.values()):raise ValueError('No cross-event inferred destination.')
 legacy=next(e for e in json.loads((root/LEGACY).read_bytes())['events']if e['title']=='独活');links=[{'legacy_scene_key':s['key'],'current_original_scene_id':sid}for s in legacy['scenes']for sid in s['game_scene_ids']if sid in scenes and canonical(s['description'])==canonical(originals['scenes'][sid]['description'])]
 if len(links)!=3:raise ValueError('All three exact source scene identities required.')
 comparison={g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in rows.items()}for g,rows in originals.items()};d={'schema':'current_lone_dog_335_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'dog','title':'独活','entry_scene_id':entry,'scene_ids':list(scenes),'choice_ids':list(choices)},'scenes':scenes,'choices':choices,'originals':originals,'source':receipt,'complete_selected_record_comparison_to_baseline':comparison,'catalogue_binding':{'expected_legacy_event':legacy,'expected_summary':{k:deepcopy(legacy[k])for k in('id','title','node_types','floors','natural','natural_reason','entry')},'exact_scene_links':links,'current_event_id':'dog'},'complete_game_option_pool':False,'game_parent_script_restored':False,'actual_eligible':None,'run_updated':False};blob=encoded(d);names=[CURRENT,BASELINE,LEGACY,PACK+'/source-receipt.json',receipt['selected_file']];files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(blob),'sha256':sha256(blob).hexdigest()};return blob,encoded({'schema':'current_lone_dog_335_manifest_v1','game_commit':d['game_commit'],'files':files})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);p.add_argument('--check',action='store_true');a=p.parse_args();d,m=build()
 if a.output_dir:a.output_dir.mkdir(parents=True,exist_ok=False);(a.output_dir/'current-lone-dog.json').write_bytes(d);(a.output_dir/'runtime-manifest.json').write_bytes(m)
 if a.check:assert(ROOT/DATA).read_bytes()==d and(ROOT/PACK/'runtime-manifest.json').read_bytes()==m
 print(json.dumps({'scenes':3,'choices':4,'items':1,'manifest_sha256':sha256(m).hexdigest()}))
