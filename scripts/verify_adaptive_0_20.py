"""Reproducible controlled comparisons; no window, chat, or game input."""
import hashlib,json,statistics,sys,time
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from rouge.recognition import ScreenReader
from rouge.visual_recognition import VisualReader

def load(name):
    return cv2.imdecode(np.fromfile(ROOT/f'samples/native-client/{name}.png',np.uint8),1)

def evidence(result):
    operator=result.get('operator');run=result.get('run') or {};graph=result.get('map') or {}
    return {'page':result['page'],'operator':None if operator is None else
        {'id':operator['id'],'fields':operator['fields'],'skill_ranks':operator['skill_ranks']},
        'relics':run.get('relics',{}).get('ids'),'count':run.get('relics',{}).get('count'),
        'crew':run.get('crew_count'),'template':graph.get('template_id'),'map_status':graph.get('status'),
        'resources':{k:v.get('value',v.get('capacity')) for k,v in run.get('resources',{}).items()}}

source_files=sorted((ROOT/'rouge').glob('*.py'))+[ROOT/'pyproject.toml',Path(__file__)]
source_files+=sorted((ROOT/'rouge/data/visual-anchors').glob('*'))+[ROOT/'rouge/data/ui-icons/module-selected-arrow.png']
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
receipt={'version':'0.20.0','verified_at':time.time(),'animation':[],'resolutions':[],'visual':[],
         'source_hashes':hashes,'limits':['Controlled replay, not all real animations or physical display configurations.',
            'Image-only backend covers reference identities/potential and partial held icons, not numeric or event text.']}
for name in ['run-map-closed','operator-mechanist','module-mechanist']:
    im=load(name);baseline=ScreenReader(cache_enabled=False);adaptive=ScreenReader()
    base=baseline.read(im);new=adaptive.read(im);assert evidence(base)==evidence(new)
    slow=[];fast=[];areas=[]
    for i in range(3):
        changed=im.copy();changed[400:408,40+i*10:48+i*10]=255-changed[400:408,40+i*10:48+i*10]
        a=baseline.read(changed);b=adaptive.read(changed)
        assert evidence(a)==evidence(b),(name,evidence(a),evidence(b))
        slow.append(a['performance']['total_ms']);fast.append(b['performance']['total_ms'])
        areas.append(b['performance']['ocr'])
    receipt['animation'].append({'sample':name,'full_median_ms':statistics.median(slow),
        'adaptive_median_ms':statistics.median(fast),'semantic_equality':True,'ocr_work':areas})
    print('controlled comparison',name,flush=True)
im=load('operator-mechanist')
for width in [1280,1600,2052,2560]:
    resized=cv2.resize(im,(width,round(im.shape[0]*width/im.shape[1])))
    r=ScreenReader().read(resized);o=r['operator'];assert o and o['id']=='mechanist'
    # Unknown is acceptable; a contradictory value is not.
    expected={'potential':6,'elite':2,'level':90,'module_level':3}
    for key,value in expected.items():assert key not in o['fields'] or o['fields'][key]==value
    receipt['resolutions'].append({'size':r['size'],'fields':o['fields'],'skill_ranks':o['skill_ranks'],
        'missing':o['missing_fields'],'contradictory_fields':0,'performance':r['performance']})
    print('resolution',width,flush=True)
visual=VisualReader()
for name,key,potential in [('operator-mechanist','mechanist',6),('operator-silverash','silverash',1),('operator-kaltsit','kaltsit',2)]:
    im=load(name)
    for width in [1600,2052]:
        image=cv2.resize(im,(width,round(im.shape[0]*width/im.shape[1])))
        r=visual.read(image);operator=r['operator']
        assert operator and operator['id']==key and operator['fields'].get('potential')==potential,(name,width,r)
        receipt['visual'].append({'sample':name,'size':r['size'],'fields':operator['fields'],
                                  'id':key,'performance':r['performance'],'landmarks':r['visual_landmarks']})
for p in source_files:assert hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p.relative_to(ROOT))]
(ROOT/'ADAPTIVE_0.20_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:receipt[k] for k in ('animation','resolutions')},ensure_ascii=False))
