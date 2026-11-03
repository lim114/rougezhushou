"""Read the full documented graph; its branch links do not recover server scripts."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_documented_event_flows_321 import Document,Node,canonical,encoded
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-shadow-346';DATA='rouge/data/current-shadow.json'
CURRENT='research/p3-expansion-313/current-topic.json';BASELINE='research/p3-expansion-313/baseline-topic.json';LEGACY='rouge/data/node-catalog.json';ICONS='rouge/data/relic-icon-receipt.json'
LABELS={1:'最初邀请 · 第一圈前',2:'第一圈结果 · 4源石锭',27:'第一圈结果 · 回复1生命',3:'第二圈前 · 缺嘴巴',4:'第二圈结果 · 2希望',26:'第二圈结果 · 回复1生命',5:'第三圈前 · 缺左前腿',6:'第三圈结果 · 1自然物',25:'第三圈结果 · 回复2生命',7:'第四圈前 · 缺右前腿',8:'第四圈结果 · 1加工品',23:'第四圈结果 · 12源石锭',24:'第四圈结果 · 回复2生命',9:'第五圈前 · 缺左后腿',10:'第五圈结果 · 1收藏品',22:'第五圈结果 · 5生命',11:'第六圈前 · 缺右后腿',12:'第六圈结果 · 8希望',20:'第六圈结果 · 携带干员+1',21:'第六圈结果 · 回复3生命',13:'第七圈前 · 缺肚子',14:'第七圈结果 · 3收藏品',15:'第八圈及以后 · 七条狗',16:'第八圈后结果 · 1行动力',17:'第八圈后结果 · 犬植浆',18:'犬植浆领取后的离开',19:'中途离开',28:'最初拒绝邀请'}
def build(root=ROOT):
 root=Path(root);receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());raw=(root/receipt['selected_file']).read_bytes()
 if receipt['revision']!=352356 or len(raw)!=receipt['selected_bytes']or sha256(raw).hexdigest()!=receipt['selected_sha256']:raise ValueError('Exact full interactive graph required')
 current=json.loads((root/CURRENT).read_bytes())['details'];old=json.loads((root/BASELINE).read_bytes())['details'];originals={g:{}for g in('scenes','choices','items','stages')};originals['scenes']={k:deepcopy(v)for k,v in current['choiceScenes'].items()if v['title']=='被歌颂的影子'}
 nodes=[n for n in Document(raw.decode()).root.walk()if n.tag=='section'and 'node'in n.attrs.get('class','').split()]
 if len(nodes)!=28 or {n.attrs['id']for n in nodes}!={'node-'+str(i)for i in LABELS}:raise ValueError('All28 complete documented nodes required')
 scenes={};choices={}
 def elements(n,cls):return[x for x in n.walk()if x.attrs.get('class')==cls]
 def one(n,cls):
  hit=elements(n,cls)
  if len(hit)!=1:raise ValueError('One '+cls+' required')
  return hit[0]
 for n in nodes:
  sid=n.attrs['id'];body=one(n,'body').text().strip();ids=[k for k,v in originals['scenes'].items()if canonical(v['description'])==canonical(body)]
  if not ids:raise ValueError('Every complete narrative must match current source')
  scenes[sid]={'id':sid,'label':LABELS[int(sid.split('-')[1])],'description':body,'source_scene_ids':ids,'choice_ids':[],'scope':'documented','source':{'file':receipt['selected_file'],'html_id':sid,'complete_body_sha256':sha256(body.encode()).hexdigest()}}
 for n in nodes:
  sid=n.attrs['id'];entries=[x for x in n.walk()if x.attrs.get('class')in('choice','choice choice-link')]
  for index,c in enumerate(entries):
   title=one(c,'choice-title').text().strip();desc=one(c,'choice-desc').text().strip();sub=elements(c,'subchoice');href=c.attrs.get('href');dest=href[1:]if href else None
   hits={k:deepcopy(v)for k,v in current['choices'].items()if canonical(v['title']+(v['description']or''))==canonical(title+desc)and(v['nextSceneId']in originals['scenes']or(v['nextSceneId']is None and v['type']=='NEXT_PROB'))}
   if title=='加入它们':hits={k:v for k,v in hits.items()if v['type']=='NEXT_PROB'}
   elif dest: hits={k:v for k,v in hits.items()if v['nextSceneId']in scenes[dest]['source_scene_ids']}
   if not hits:raise ValueError('Every full title/description needs source records')
   key=sid+':option:'+str(index);next_id=dest
   if sub:
    if href or title!='加入它们':raise ValueError('Only documented chance joining uses result directory')
    next_id=sid+':results';scenes[next_id]={'id':next_id,'label':scenes[sid]['label']+' · 结果参考','description':None,'choice_ids':[],'source_scene_ids':[],'scope':'results','source':deepcopy(scenes[sid]['source'])}
    for j,s in enumerate(sub):
     target=s.attrs['href'][1:];label=one(s,'subchoice-title').text().strip();rid=key+':result:'+str(j)
     if target not in scenes:raise ValueError('No external graph target')
     choices[rid]={'id':rid,'scene_id':next_id,'title':'查阅'+label+'结果','description':'仅文献列出的结果参考，不是可以自行挑选的游戏按钮。','next_scene_id':target,'variant_ids':[],'stage_ids':[],'presentation':'outcome_reference','actual_game_button':False,'scope':'documented','source':{'file':receipt['selected_file'],'parent_html_id':sid,'href':s.attrs['href']},'actual_received':None}
     scenes[next_id]['choice_ids'].append(rid)
   if next_id not in scenes:raise ValueError('Complete documentary destination required')
   choices[key]={'id':key,'scene_id':sid,'title':title,'description':desc,'next_scene_id':next_id,'variant_ids':list(hits),'stage_ids':[],'presentation':'option_reference','actual_game_button':None,'scope':'documented','source':{'file':receipt['selected_file'],'html_id':sid,'choice_index':index},'actual_received':None};scenes[sid]['choice_ids'].append(key);originals['choices'].update(hits)
 # Also retain the explicit alternate join item; its parent is not proved by this graph.
 alternate={k:v for k,v in current['choices'].items()if v['nextSceneId']in originals['scenes']and v['title']=='加入它们'}
 if len(alternate)!=1:raise ValueError('Exactly one explicit alternate joining record required')
 originals['choices'].update(deepcopy(alternate))
 if(len(originals['scenes']),len(originals['choices']),len(scenes),len(choices))!=(28,28,35,49):raise ValueError('Keep28/28 originals,35 contexts and49 references')
 if sum(v['nextSceneId']is None for v in originals['choices'].values())!=8:raise ValueError('Eight no-next candidates required')
 reward=[v for v in originals['choices'].values()if canonical(v['description'])=='获得收藏品犬植浆']
 if len(reward)!=1 or reward[0]['displayData']['itemId']!='rogue_6_relic_artifact_4':raise ValueError('Exact item pointer required')
 iid=reward[0]['displayData']['itemId'];item=current['items'][iid]
 if item['name']!='犬植浆'or item['type']!='RELIC'or canonical(item['usage'])!='干员攻击范围内的其他干员获得迷彩，攻击力+10%（可叠加）':raise ValueError('Do not use shifted numeric catalogue ordinal')
 originals['items'][iid]=deepcopy(item);icon=next(v for v in json.loads((root/ICONS).read_bytes())['icons']if v['id']==iid);picture=(root/'rouge/data'/icon['file']).read_bytes()
 if sha256(picture).hexdigest()!=icon['sha256']:raise ValueError('Exact current item picture required')
 legacy=next(v for v in json.loads((root/LEGACY).read_bytes())['events']if v['title']=='被歌颂的影子');links=[]
 for s in legacy['scenes']:
  for oid in s['game_scene_ids']:
   if oid not in originals['scenes']:continue
   a=canonical(s['description']);b=canonical(originals['scenes'][oid]['description'])
   if a!=b and a.replace('……','......')!=b:raise ValueError('No fuzzy legacy scene links')
   links.append({'legacy_scene_key':s['key'],'current_original_scene_id':oid,'legacy_complete_description':s['description'],'current_complete_description':originals['scenes'][oid]['description']})
 if len(links)!=21 or len({x['current_original_scene_id']for x in links})!=20:raise ValueError('Old20 contexts preserve21 links to20 unique originals')
 result={'schema':'current_shadow_346_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','event':{'id':'shadow','title':'被歌颂的影子','entry_scene_id':'node-1','scene_ids':list(scenes),'choice_ids':list(choices)},'scenes':scenes,'choices':choices,'originals':originals,'source':receipt,'complete_document_graph':True,'complete_game_option_pool':False,'actual_result':None,'run_updated':False,'icon_reference':{**deepcopy(icon),'file':'rouge/data/'+icon['file'],'bytes':len(picture)},'catalogue_binding':{'expected_legacy_event':legacy,'expected_summary':{k:deepcopy(legacy[k])for k in('id','title','node_types','floors','natural','natural_reason','entry')},'exact_scene_links':links,'current_event_id':'shadow'},'complete_selected_record_comparison_to_baseline':{g:{k:old['choiceScenes'if g=='scenes'else g].get(k)==v for k,v in rows.items()}for g,rows in originals.items()}}
 data=encoded(result);names=[CURRENT,BASELINE,LEGACY,ICONS,PACK+'/source-receipt.json',PACK+'/source-notes.json',receipt['selected_file']];files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(data),'sha256':sha256(data).hexdigest()}
 return data,encoded({'schema':'current_shadow_346_manifest_v1','game_commit':result['game_commit'],'files':files})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();d,m=build()
 if a.check:
  if(ROOT/DATA).read_bytes()!=d or(ROOT/PACK/'runtime-manifest.json').read_bytes()!=m:raise ValueError('Build differs')
 else:(ROOT/DATA).write_bytes(d);(ROOT/PACK/'runtime-manifest.json').write_bytes(m)
 print(json.dumps({'scenes':28,'choices':28,'contexts':35,'references':49,'manifest_sha256':sha256(m).hexdigest()}))
