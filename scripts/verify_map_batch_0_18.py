"""Audit sourced graph facts and replay captured maps at continuous sizes."""
import collections
import hashlib
import json
import sys
import time
from pathlib import Path
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.recognition import ScreenReader

data = json.loads((ROOT/'rouge/data/map-templates.json').read_text(encoding='utf-8'))
audits = []
for template in data['templates']:
    adj = {n['id']:set() for n in template['nodes']}
    for a,b in template['edges']: adj[a].add(b); adj[b].add(a)
    distance={template['start']:0};queue=collections.deque(distance)
    while queue:
        a=queue.popleft()
        for b in adj[a]:
            if b not in distance:distance[b]=distance[a]+1;queue.append(b)
    assert len(distance)==len(adj)
    assert all(n['distance']==distance[n['id']] for n in template['nodes'])
    assert all(0<=n['row']<template['rows'] and 0<=n['col']<template['cols'] for n in template['nodes'])
    audits.append({'template':template['id'],'zone':template['zone_id'],'nodes':len(adj),
                   'edges':len(template['edges']),'max_distance':max(distance.values())})
image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/exploration-map.png',dtype=np.uint8),1)
reader=ScreenReader();replays=[]
for width,height,pad_width in [(1596,1198,None),(960,720,1280),(1437,1079,None),(1918,1440,2560)]:
    sample=cv2.resize(image,(width,height),interpolation=cv2.INTER_AREA)
    if pad_width:
        padded=np.zeros((height,pad_width,3),np.uint8);left=(pad_width-width)//2
        padded[:,left:left+width]=sample;sample=padded
    observed=reader.read(sample);graph=observed['map']
    assert graph['status']=='matched' and graph['template_id']=='1b',(width,height,graph)
    assert graph['current_node']=='1,0'
    assert len(graph['nodes'])==12 and len(graph['edges'])==13
    assert next(n for n in graph['nodes'] if n['id']=='1,3')['prediction']['candidates']==['诡意行商']
    replays.append({'capture_size':observed['size'],'template':graph['template_id'],
                    'viewport':observed['viewport']})
    print('Passed map replay',observed['size'],flush=True)
wide=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/map-template-node-detail.png',dtype=np.uint8),1)
observed=reader.read(wide,client_rect=[2,45,2050,1125]);graph=observed['map']
assert graph['status']=='matched' and graph['template_id']=='1c'
assert graph['current_node']=='1,2' and len(graph['nodes'])==13 and len(graph['edges'])==12
replays.append({'capture_size':observed['size'],'template':graph['template_id'],'viewport':observed['viewport'],
                'native_detail_panel_sample':True})
files=['rouge/map_recognition.py','rouge/map_reporting.py','rouge/recognition.py','rouge/run_state.py',
       'rouge/app.py','rouge/map_view.py','rouge/data/map-templates.json','tests/test_map_templates.py','scripts/build_map_templates.py']
receipt={'version':'0.18.0','verified_at':time.time(),'templates_audited':len(audits),'rules':len(data['rules']),
    'source':data['source'],'graph_audits':audits,'replays':replays,'chat_requests':0,
    'source_hashes':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files},
    'limits':['43布局数据连通性/距离核验，不代表43布局均完成视觉实测。',
              '缩放回放使用第一层实际样本，含两个不同布局；隐藏候选没有概率或实战真值校准。']}
(ROOT/'MAP_0.18_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print('43 graphs audited; 5 map/resolution replays passed; no chats')
