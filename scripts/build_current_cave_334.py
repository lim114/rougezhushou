"""Complete cave table and all matching fixed records, without inferred random scripts."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-cave-334';DATA='rouge/data/current-cave.json';CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json';LEGACY='rouge/data/node-catalog.json'
SIGNATURES={'dig':('树洞里肯定有好东西','掏一下'),'leave':('离开','多一事不如少一事'),'gold':('我的了！','获得5源石锭'),'relic':('我的了！','获得1件收藏品'),'empty':('怎么是空的！','继续掏'),'battle':('放开我！','遭遇一场艰难的战斗'),'again':('一定是错觉','继续掏'),'stop':('太诡异了','多一事不如少一事')}

def build(root=ROOT):
 root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
 if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes']or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Whole exact cave table required.')
 current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details'];legacy=next(e for e in json.loads((root/LEGACY).read_bytes())['events']if e['title']=='洞中宝');table=next(n for n in Document(raw.decode()).root.walk()if n.tag=='table');narratives=[];captions=[]
 for ri,tr in enumerate(n for n in table.walk()if n.tag=='tr'):
  for ci,cell in enumerate(n for n in tr.children if isinstance(n,Node)and n.tag in('td','th')):
   text=canonical(cell.text());loc={'file':receipt['selected_file'],'row':ri,'cell':ci,'attributes':cell.attrs,'text':cell.text(),'text_sha256':sha256(cell.text().encode()).hexdigest()}
   if not text:continue
   if cell.tag=='th':
    hits={k:v for k,v in current['choiceScenes'].items()if v['title']=='洞中宝'and canonical(v['description'])==text}
    if not hits:raise ValueError('Every narrative must match complete current records.')
    narratives.append({'text':text,'matches':hits,'source':loc});continue
   if text=='主选项'or re.fullmatch(r'选项[一二]（随机）|选项[一二]|情况[1234](?:后续)?|分支[12]',text):continue
   matches=[role for role,(title,desc)in SIGNATURES.items()if text.startswith(canonical(title+desc))]
   if len(matches)!=1:raise ValueError('Unknown full caption or note: '+text)
   captions.append({'role':matches[0],'source':loc})
 if len(narratives)!=11 or len(captions)!=13:raise ValueError('Do not lose duplicate document contexts.')
 # Two repeated-exit narrative cells have identical text; keep both original source locations.
 # The source sequence includes initial exit after the four random branches, then two repeated exits.
 expected_rows=[1,3,5,7,9,11,13,15,18,21,24]
 if [n['source']['row']for n in narratives]!=expected_rows:raise ValueError('Complete narrative table structure changed.')

 role_rows={'start':[1],'crow':[3],'low_gold':[5],'squirrel':[7],'end':[9],'empty':[11],'low_empty':[13],'danger':[15],'initial_exit':[18],'repeat_exit':[21,24]}
 labels={'start':'最初对话 · 洞中宝','crow':'文献结果：摸到乌鸦的宝贝','squirrel':'文献结果：摸到松鼠的宝贝','empty':'文献结果：一无所获','danger':'文献结果：树洞咬人','low_gold':'文献后续：拿到源石锭后听到低鸣','low_empty':'文献后续：空手后听到低鸣','end':'洞中似乎不剩什么，离开','initial_exit':'最初就离开','repeat_exit':'听到低鸣后离开'}
 parents={'start':['dig','leave'],'crow':['gold'],'squirrel':['relic'],'empty':['empty'],'danger':['battle'],'low_gold':['again','stop'],'low_empty':['again','stop']};scenes={};originals={g:{}for g in('scenes','choices','items','stages')}
 for role,rows in role_rows.items():
  ns=[n for n in narratives if n['source']['row']in rows];texts={n['text']for n in ns}
  if len(texts)!=1:raise ValueError('Only identical documented prose may share a context.')
  matches=ns[0]['matches'];originals['scenes'].update(deepcopy(matches));sid='cave-scene:'+role;scenes[sid]={'id':sid,'event_id':'cave','label':labels[role],'description':next(iter(matches.values()))['description'],'original_scene_ids':list(matches),'choice_ids':['cave-choice:'+v for v in parents.get(role,[])],'source_cells':[n['source']for n in ns]}
 if originals['scenes']!={k:v for k,v in current['choiceScenes'].items()if v['title']=='洞中宝'}:raise ValueError('Do not omit same-title current scene records.')
 legacy_ids={i for s in legacy['scenes']for c in s['choices']for i in c['game_choice_ids']};choices={}
 document_next={'leave':'initial_exit','gold':'low_gold','relic':'end','empty':'low_empty','stop':'repeat_exit'}
 for role,(title,desc)in SIGNATURES.items():
  matches={k:v for k,v in current['choices'].items()if v['title']==title and canonical(v['description'])==canonical(desc)and(v['nextSceneId']in originals['scenes']or(v['nextSceneId']is None and k in legacy_ids))}
  expected={'dig':2,'leave':2,'gold':8,'relic':8,'empty':8,'battle':8,'again':6,'stop':2}[role]
  if len(matches)!=expected:raise ValueError('Original variant set changed: '+role)
  original_next={};doc='cave-scene:'+document_next[role]if role in document_next else None
  for cid,v in matches.items():
   target=v['nextSceneId']
   if target is None:original_next[cid]=None;continue
   text=canonical(originals['scenes'][target]['description']);possible=[sid for sid,s in scenes.items()if canonical(s['description'])==text]
   if len(possible)>1:
    if doc not in possible:raise ValueError('Do not infer a parent from a repeated narrative.')
    possible=[doc]
   if len(possible)!=1:raise ValueError('Every exact current destination must be represented.')
   original_next[cid]=possible[0]
  targets=list(dict.fromkeys(original_next.values()));common=targets[0]if len(targets)==1 else None;cid='cave-choice:'+role
  source_cells=[r['source']for r in captions if r['role']==role]
  outcomes=[{'scene_id':'cave-scene:'+v,'basis':'documented_random_case','probability':None,'actual_outcome':None}for v in('crow','squirrel','empty','danger')]if role in('dig','again')else[]
  if role in('dig','again')and(any(v['type']!='NEXT_PROB'or v['nextSceneId']is not None for v in matches.values())):raise ValueError('Do not replace a random action with a chosen result.')
  choices[cid]={'id':cid,'event_id':'cave','role':role,'title':title,'description':next(iter(matches.values()))['description'],'scene_ids':[sid for sid,s in scenes.items()if cid in s['choice_ids']],'variant_ids':list(matches),'variant_next_scene_ids':original_next,'next_scene_id':common,'documented_next_scene_id':doc,'record_next_scene_ids':[x for x in targets if x is not None],'documented_outcomes':outcomes,'source_cells':source_cells,'stage_ids':[],'battle_hint_without_exact_stage':role=='battle','reward_reference':{'quantity':5,'kind':'源石锭','pool':None}if role=='gold'else{'quantity':1,'kind':'收藏品','pool':None}if role=='relic'else None,'actual_eligible':None,'actual_received':None,'actual_variant':None,'actual_parent_scene_id':None}
  originals['choices'].update(deepcopy(matches))
  for v in matches.values():
   item=(v.get('displayData')or{}).get('itemId')
   if item is not None:originals['items'][item]=deepcopy(current['items'][item])
 if '将再次进入随机组【随机组1】'not in canonical(table.text())or'选项一（随机）'not in canonical(table.text()):raise ValueError('Keep complete random and repetition notes.')
 links=[{'legacy_scene_key':s['key'],'current_original_scene_id':sid}for s in legacy['scenes']for sid in s['game_scene_ids']if sid in originals['scenes']and canonical(s['description'])==canonical(originals['scenes'][sid]['description'])]
 counts={'document_scenes':len(scenes),'document_choice_groups':len(choices),'original_scenes':len(originals['scenes']),'original_choices':len(originals['choices']),'caption_cells':len(captions),'documented_random_outcomes':4,'original_next_divergent_groups':sum(len(c['record_next_scene_ids'])>1 for c in choices.values()),'catalogue_exact_scene_links':len(links)}
 if counts!={'document_scenes':10,'document_choice_groups':8,'original_scenes':46,'original_choices':44,'caption_cells':13,'documented_random_outcomes':4,'original_next_divergent_groups':2,'catalogue_exact_scene_links':46}:raise ValueError('Whole cave coverage changed: '+str(counts))
 comparison={g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in records.items()}for g,records in originals.items()}
 data={'schema':'current_cave_334_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'cave','title':'洞中宝','entry_scene_id':'cave-scene:start','scene_ids':list(scenes),'choice_ids':list(choices)},'scenes':scenes,'choices':choices,'originals':originals,'counts':counts,'source':receipt,'complete_selected_record_comparison_to_baseline':comparison,'complete_game_option_pool':False,'game_parent_script_restored':False,'actual_probability':None,'actual_outcome':None,'actual_eligible':None,'actual_variant':None,'actual_received':None,'actual_max_attempts':None,'actual_stage':None,'run_updated':False,'catalogue_binding':{'expected_legacy_event':legacy,'expected_summary':{k:deepcopy(legacy[k])for k in('id','title','node_types','floors','natural','natural_reason','entry')},'exact_scene_links':links,'current_event_id':'cave'}}
 blob=encoded(data);names=[CURRENT,BASELINE,LEGACY,PACK+'/source-receipt.json',receipt['selected_file']];files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(blob),'sha256':sha256(blob).hexdigest()};return blob,encoded({'schema':'current_cave_334_manifest_v1','game_commit':data['game_commit'],'files':files})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);p.add_argument('--check',action='store_true');args=p.parse_args();d,m=build()
 if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=False);(args.output_dir/'current-cave.json').write_bytes(d);(args.output_dir/'runtime-manifest.json').write_bytes(m)
 if args.check:assert(ROOT/DATA).read_bytes()==d and(ROOT/PACK/'runtime-manifest.json').read_bytes()==m
 print(json.dumps({'counts':json.loads(d)['counts'],'manifest_sha256':sha256(m).hexdigest()}))
