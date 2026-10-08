"""Visible content identities are separate from node-type generation budgets."""
import copy
import json
import re
from functools import lru_cache
from pathlib import Path
import cv2
import numpy as np


@lru_cache(maxsize=1)
def event_data():
    return json.loads((Path(__file__).with_name('data')/'node-events.json').read_text(encoding='utf-8'))


def normalized(text):
    return re.sub(r'[\W_]+','',text or '')


def content_identity(content):
    if not content:return None
    return json.dumps({k:content.get(k) for k in ('kind','title','node_type','node_type_candidates',
        'variant_id','variants','scene_candidates','visible_options','identity_status')},sort_keys=True,ensure_ascii=False)


def read_node_content(image,texts,page,stage,nodes):
    if page in ('operator_detail','operator_module','run_roster','run_relics'):return None
    if page=='node_detail' and stage:
        title=next((t for t in texts if t['text']==stage['name'] and t['confidence']>=.8),None)
        if not title:return None
        variant=next((v for v in stage['variants'] if v['id']==stage.get('visible_variant_id')),None)
        return {'kind':'battle','title':stage['name'],'title_box':title['box'],
            'identity_status':'visible_title','variant_id':stage.get('visible_variant_id'),
            'node_type':('紧急作战' if variant['difficulty']=='FOUR_STAR' else '作战') if variant and not variant.get('isBoss') else None,
            'variants':[{'id':v['id'],'difficulty':v['difficulty']} for v in stage['variants']],
            'source':'visible_detail_panel','probability':None}
    data=event_data();titles={s['title'] for s in data['scenes'].values()}
    seen=[t for t in texts if t['confidence']>=.9 and t['text'] in titles]
    if len({t['text'] for t in seen})!=1:return None
    title=seen[0];candidates={key:s for key,s in data['scenes'].items() if s['title']==title['text']}
    prose=[normalized(t['text']) for t in texts if t['confidence']>=.85 and len(normalized(t['text']))>=10
           and t['text']!=title['text']]
    scores={key:sum(len(p) for p in prose if p in normalized(s['description'])) for key,s in candidates.items()}
    if not scores or max(scores.values())<12:return None
    best=max(scores.values());scene_ids=[key for key,value in scores.items() if value==best]
    visible_options=[]
    for t in texts:
        if t['confidence']<.9 or len(t['text'])<3:continue
        ids=[key for key,c in data['choices'].items() if normalized(c['title'])==normalized(t['text'])]
        if ids:visible_options.append({'title':t['text'],'choice_candidates':ids})
    classes=data['title_classes'].get(title['text'],{}).get('node_types',[])
    # Only an actually visible type label can count as a revealed generation slot.
    height=max(p[1] for p in title['box'])-min(p[1] for p in title['box'])
    width=max(p[0] for p in title['box'])-min(p[0] for p in title['box'])
    tx=sum(p[0] for p in title['box'])/4;ty=sum(p[1] for p in title['box'])/4
    labels={n['type'] for n in nodes if not n['type'].startswith('未知')
        and abs(sum(p[0] for p in n['box'])/4-tx)<max(width, height*4)
        and 0<ty-sum(p[1] for p in n['box'])/4<height*4}
    actual_type=next(iter(labels)) if len(labels)==1 else None
    return {'kind':'event','title':title['text'],'title_box':title['box'],'node_type':actual_type,
        'node_type_candidates':classes,'classification_evidence':'community_event_catalog',
        'scene_candidates':scene_ids,'identity_status':'visible_scene' if len(scene_ids)==1 else 'ambiguous_scene',
        'visible_options':visible_options,'source':'visible_event_text','probability':None,
        'limitations':data['limits']}


def annotate_map_content(graph,content):
    if not graph or graph.get('status')!='matched' or not content:return
    # Panel title confirms content, but not the selected grid location. That needs
    # independent same-frame selection-ring evidence. Never borrow current_node.
    selection=graph.get('selected_node')
    if selection:
        node=next((n for n in graph['nodes'] if n['id']==selection),None)
        if node:
            node['content']=copy.deepcopy(content)
            node['content']['source']='same_frame_selected_node'
            graph['content_binding']='same_frame_selected_node'


def mark_selected_node(image,graph):
    """Conservative bright selection rim; uncertain/animated rims remain unbound."""
    if not graph or graph.get('status')!='matched':return
    h,w=image.shape[:2];scale=min(1.,1400/w)
    small=cv2.resize(image,None,fx=scale,fy=scale) if scale<1 else image
    sh,sw=small.shape[:2];gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
    hsv=cv2.cvtColor(small,cv2.COLOR_BGR2HSV)
    bright=(gray>160)&(hsv[:,:,1]<90)
    angles=np.linspace(0,2*np.pi,96,endpoint=False)
    hits=[]
    for node in graph['nodes']:
        if not node.get('visible'):continue
        x,y=node['center'][0]*sw,node['center'][1]*sh
        best=0
        for radius in np.linspace(sh*.045,sh*.09,16):
            # A real selection is a broad arc, not the thin route or icon edge.
            sectors=np.zeros(len(angles),dtype=bool)
            for offset in (-1,0,1):
                xx=np.rint(x+(radius+offset)*np.cos(angles)).astype(int)
                yy=np.rint(y+(radius+offset)*np.sin(angles)).astype(int)
                valid=(xx>=0)&(xx<sw)&(yy>=0)&(yy<sh)
                sectors[valid]|=bright[yy[valid],xx[valid]]
            best=max(best,float(sectors.mean()))
        if best>=.65:hits.append((best,node['id']))
    graph['selected_node']=hits[0][1] if len(hits)==1 else None
    graph['selection_evidence']='same_frame_bright_rim' if len(hits)==1 else 'unconfirmed'
    if graph['selected_node'] or hits:return
    current=graph.get('current_node');nodes={n['id']:n for n in graph['nodes']}
    if current not in nodes:return
    beams=[]
    start=np.array(nodes[current]['center'])*[sw,sh]
    for a,b in graph['edges']:
        if current not in (a,b):continue
        target=b if a==current else a
        if not nodes[target].get('visible'):continue
        end=np.array(nodes[target]['center'])*[sw,sh];direction=end-start
        normal=np.array([-direction[1],direction[0]])/max(1,np.linalg.norm(direction))
        path=start[None,:]+np.linspace(.32,.68,80)[:,None]*direction[None,:]
        samples=[]
        for offset in (-4,-2,0,2,4):
            xy=np.rint(path+normal[None,:]*offset).astype(int)
            xx=np.clip(xy[:,0],0,sw-1);yy=np.clip(xy[:,1],0,sh-1)
            samples.append((gray[yy,xx]>210)&(hsv[yy,xx,1]<60))
        if np.any(samples,axis=0).mean()>=.9:beams.append(target)
    if len(beams)==1:
        graph['selected_node']=beams[0];graph['selection_evidence']='same_frame_unique_highlighted_edge'


def content_catalog(node):
    content=node.get('content') or node.get('remembered_content')
    if content:return None
    prediction=node.get('prediction') or {}
    types=([node['remembered_type']] if node.get('remembered_type') else
           [node['observed_type']] if node.get('observed_type') and not node['observed_type'].startswith('未知') else
           prediction.get('candidates',[]))
    titles=[title for title,record in event_data()['title_classes'].items() if set(record['node_types'])&set(types)]
    if not titles:return None
    return {'titles':titles,'evidence':'community_event_catalog','probability':None,
            'notice':'同类节点的资料事件目录；出场条件/权重未核验，不表示这些事件均能在当前层生成。'}
