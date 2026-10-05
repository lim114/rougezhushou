"""Sequential real-OCR 0.56/current replay; no capture, game input or private state."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BEFORE=ROOT/'.cache/batch-057-before'
RESEARCH=ROOT/'.cache/research/ocr-pipeline-057'
OWNED=('rouge/recognition.py','rouge/dynamic_ocr.py','rouge/page_features.py')
FIELDS=('page','run','operator','map','stage','nodes','node_content','viewport')


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def owned_seal():return {name:sha(ROOT/name) for name in OWNED}


def strict(value):
    if isinstance(value,dict):return {k:strict(v) for k,v in value.items() if k!='elapsed_ms'}
    if isinstance(value,list):return [strict(v) for v in value]
    return value


def differences(a,b,path=''):
    if type(a) is not type(b):return [{'path':path,'before':a,'after':b}]
    if isinstance(a,dict):
        out=[]
        for key in sorted(set(a)|set(b)):
            if key not in a or key not in b:out.append({'path':path+'/'+key,'before':a.get(key),'after':b.get(key)})
            else:out.extend(differences(a[key],b[key],path+'/'+key))
        return out
    if isinstance(a,list):
        if len(a)!=len(b):return [{'path':path+'/length','before':len(a),'after':len(b)}]
        return [x for i,(av,bv) in enumerate(zip(a,b)) for x in differences(av,bv,path+'/'+str(i))]
    return [] if a==b else [{'path':path,'before':a,'after':b}]


def source_frame(path,rect=None,**extra):
    path=Path(path)
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'client_rect':rect,**extra}


def inventory(live):
    native=ROOT/'samples/native-client'
    base=source_frame(native/'operator-kaltsit.png')
    mechanic=source_frame(native/'operator-mechanist.png')
    old=ROOT/'.cache/research/p1-live-recipient-055/cached-pair-1791132335648665700-receipt.json'
    previous=read(old)
    myrtle=[source_frame(ROOT/f['image'],f['client_rect']) for f in previous['frames'][:2]]
    current=read(live/'capture.json')
    main=[source_frame(live/f['file'],f['client_rect']) for f in current['frames'][:2]]
    return [
        {'id':'kaltsit_existing_animation','frames':[base,source_frame(native/'operator-kaltsit-animated.png')],
         'provenance':'existing native frame pair; capture order not independently proven'},
        {'id':'mechanist_exact_control_local_pixel','frames':[mechanic,{**mechanic,'xor_pixel':[500,700,0]}],
         'provenance':'derived one-bit change in current verified domain; not an independent animation'},
        {'id':'myrtle_existing_owned_pair','frames':myrtle,'provenance':'previous ordered actual owned-popup pair'},
        {'id':'operator_to_independent_main_menu','frames':[mechanic,*main],
         'negative_after_frame':1,'provenance':'old operator then two newly recorded WGC main-menu frames; no copied images'}
    ]


def worker(source,case,output,package):
    package=Path(package) if source=='before' else ROOT
    sys.path.insert(0,str(package))
    from rouge.recognition import ScreenReader
    cls_path=Path(sys.modules['rouge.recognition'].__file__).resolve()
    assert cls_path==(package/'rouge/recognition.py').resolve()
    reader=ScreenReader();results=[]
    for frame in case['frames']:
        path=ROOT/frame['file'];assert sha(path)==frame['sha256']
        image=cv2.imdecode(np.fromfile(path,np.uint8),1);assert image is not None
        if 'xor_pixel' in frame:
            x,y,c=frame['xor_pixel'];image[y,x,c]^=1
        result=reader.read(image,client_rect=frame['client_rect'])
        assert result['performance']['reuse']!='exact_frame'
        engine=getattr(reader._engine,'engine',reader._engine)
        assert type(engine).__module__.startswith('rapidocr_onnxruntime')
        observed=json.loads(json.dumps({field:result.get(field) for field in FIELDS},ensure_ascii=False))
        results.append({'observation':observed,'performance':result['performance']})
    write(output,{'source':source,'case':case['id'],'frames':results,'actual_rapidocr_engine':True})


def before_package(folder):
    package=folder/'baseline-source'
    if (folder/'baseline-package-seal.json').exists():return package
    original=read(BEFORE/'manifest.json')['source_hashes'];assets={}
    for path in (BEFORE/'rouge').rglob('*'):
        if not path.is_file() or '__pycache__' in path.parts:continue
        relative=path.relative_to(BEFORE)
        expected=original.get(relative.as_posix())
        if expected is not None:assert sha(path)==expected
        dest=package/relative;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,dest)
    # The root's code/JSON seal omits UI icon PNGs needed by the unchanged
    # readers. Fill only public reference assets; never runtime or source PNGs.
    for path in (ROOT/'rouge/data').rglob('*'):
        if not path.is_file() or path.suffix=='.json' or '__pycache__' in path.parts:continue
        relative=path.relative_to(ROOT);dest=package/relative
        if not dest.exists():
            dest.parent.mkdir(parents=True,exist_ok=True)
            try:os.link(path,dest)
            except OSError:shutil.copyfile(path,dest)
        assets[relative.as_posix()]=sha(path)
        assert sha(dest)==assets[relative.as_posix()]
    write(folder/'baseline-package-seal.json',{'before_manifest':sha(BEFORE/'manifest.json'),
        'owned_before_hashes':{name:sha(package/name) for name in OWNED},
        'supplemented_current_public_non_json_assets':assets,'private_state_read':False})
    return package


def replay(epoch,live,budget):
    folder=RESEARCH/epoch
    if not folder.exists():
        cases=inventory(live)
        before_manifest=read(BEFORE/'manifest.json')
        for name in OWNED:assert sha(BEFORE/name)==before_manifest['source_hashes'][name]
        write(folder/'inventory.json',{'cases':cases,'owned_source_hashes':owned_seal(),
             'before_source_hashes':{name:sha(BEFORE/name) for name in OWNED},'private_state_read':False})
    package=before_package(folder)
    cases=read(folder/'inventory.json')['cases'];start=owned_seal();started=time.perf_counter();completed=0
    for index,case in enumerate(cases):
        existing=folder/'rows'/(case['id']+'.json')
        if existing.exists() and read(existing)['owned_source_hashes']==start:continue
        if completed and time.perf_counter()-started>=budget:break
        outputs={}
        order=['before','current'] if index%2==0 else ['current','before']
        for source in order:
            case_path=folder/'cases'/(case['id']+'.json');write(case_path,case)
            destination=folder/'workers'/(case['id']+'-'+source+'.json')
            p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'worker','--source',source,
                '--case',str(case_path),'--output',str(destination),'--package',str(package)],
                capture_output=True,text=True,encoding='utf-8')
            if p.returncode:
                write(folder/('worker-failure-'+str(time.time_ns())+'.json'),
                      {'case':case['id'],'source':source,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
                raise RuntimeError(f'{case["id"]}: {source} worker failed; preserved diagnostic')
            outputs[source]=read(destination)
        diffs=[]
        for i,(old,new) in enumerate(zip(outputs['before']['frames'],outputs['current']['frames'])):
            diffs.extend(differences(strict(old['observation']),strict(new['observation']),str(i)))
        negative=True
        if 'negative_after_frame' in case:
            negative=all(frame['observation']['operator'] is None and frame['observation']['run'] is None
                and frame['observation']['page']=='unknown'
                for frame in outputs['current']['frames'][case['negative_after_frame']:])
        row={'case':case['id'],'passed':not diffs and negative,'strict_differences':diffs,
             'new_main_menu_negative_passed':negative,'order':order,'owned_source_hashes':start,
             'frames':case['frames'],'outputs':outputs,'provenance':case['provenance'],
             'private_state_read':False,'game_actions':0,'chat_requests':0}
        write(existing,row);completed+=1
        print(json.dumps({'case':case['id'],'passed':row['passed'],'differences':diffs[:8],
            'negative_passed':negative,'times_ms':{s:[f['performance']['total_ms'] for f in o['frames']]
                                                for s,o in outputs.items()}},ensure_ascii=False),flush=True)
        if not row['passed']:break
    write(folder/('segment-'+str(time.time_ns())+'.json'),{'completed':completed,
        'elapsed_seconds':time.perf_counter()-started,'owned_source_stable':start==owned_seal(),
        'owned_source_hashes':start})
    assert start==owned_seal(),'owned OCR sources changed during replay'


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['worker','replay'])
    p.add_argument('--source',choices=['before','current']);p.add_argument('--case');p.add_argument('--output')
    p.add_argument('--package')
    p.add_argument('--epoch',default='epoch-'+str(time.time_ns()))
    p.add_argument('--live',default='.cache/recognition-057-live/1791146635278884200')
    p.add_argument('--budget-seconds',type=float,default=100.)
    a=p.parse_args()
    if a.command=='worker':worker(a.source,read(a.case),a.output,a.package)
    else:replay(a.epoch,ROOT/a.live,a.budget_seconds)
