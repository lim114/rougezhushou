"""Independent 0.57/current real OCR replay for visual page scheduling.

Only public development samples and sealed source are read. No capture, game
input, chat requests or private state. Every changed confidence, box and fact is
recorded; no broad evidence-key exemption can hide a crop regression.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
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
BEFORE=ROOT/'.cache/batch-058-before'
RESEARCH=ROOT/'.cache/research/hybrid-058'
FIELDS=('page','run','operator','map','stage','nodes','node_content','viewport')
REPRESENTATIVE={'exploration-map','map-template-node-detail','module-mechanist',
    'operator-kaltsit','operator-mechanist','operator-silverash','run-emergency-mechanist',
    'run-mechanist-selected','run-relic-multicard','kaltsit_owned','chen_owned','leizi_owned','myrtle_owned'}
OLD_INVENTORY=ROOT/'.cache/research/page-routing-056/epoch-1791136902879484600/inventory.json'
MAIN_MENU=ROOT/'.cache/recognition-057-live/1791146635278884200'


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as handle:
        json.dump(value,handle,ensure_ascii=False,indent=2);handle.write('\n')


def public_seal():
    paths=set((ROOT/'rouge').rglob('*.py'))|set((ROOT/'rouge/data').rglob('*.json'))
    for name in ('page-features','visual-anchors'):
        paths|={p for p in (ROOT/'rouge/data'/name).rglob('*') if p.is_file()}
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}


def strict(value):
    if isinstance(value,dict):return {k:strict(v) for k,v in value.items() if k!='elapsed_ms'}
    if isinstance(value,list):return [strict(v) for v in value]
    return value


def differences(a,b,path=''):
    """All JSON leaves, including confidence and geometry; missing != null."""
    if type(a) is not type(b):return [{'path':path,'before':a,'after':b,'reason':'type_or_value'}]
    if isinstance(a,dict):
        result=[]
        for key in sorted(set(a)|set(b)):
            if key not in a or key not in b:
                result.append({'path':path+'/'+key,'before':a.get(key),'after':b.get(key),
                    'reason':'missing_before' if key not in a else 'missing_after'})
            else:result.extend(differences(a[key],b[key],path+'/'+key))
        return result
    if isinstance(a,list):
        result=[]
        if len(a)!=len(b):result.append({'path':path+'/length','before':len(a),'after':len(b),'reason':'length'})
        for index,(old,new) in enumerate(zip(a,b)):
            result.extend(differences(old,new,path+'/'+str(index)))
        return result
    return [] if a==b else [{'path':path,'before':a,'after':b,'reason':'value'}]


def frame(sample,variant='native'):
    path=sample['animation_image'] if variant=='animation' else sample['image']
    expected=sample['animation_sha256'] if variant=='animation' else sample['sha256']
    assert sha(ROOT/path)==expected
    return {'file':path,'sha256':expected,'client_rect':sample['client_rect'],'variant':variant}


def planned_cases():
    previous=read(OLD_INVENTORY)['samples']
    selected=[s for s in previous if s['id'] in REPRESENTATIVE]
    assert len(selected)==13
    result=[{'id':s['id']+':native','frames':[frame(s)],'group':'cold',
        'provenance':'preexisting public development sample; not independent holdout'} for s in selected]
    for sample in selected:
        if sample['id'] in {'operator-kaltsit','run-mechanist-selected','map-template-node-detail','myrtle_owned'}:
            result.append({'id':sample['id']+':scaled_translated','frames':[frame(sample,'scaled_translated')],
                'group':'cold','provenance':'derived resize/translation; not independent source'})
    kaltsit=deepcopy(next(s for s in selected if s['id']=='operator-kaltsit'))
    animated=next(s for s in previous if s['id']=='operator-kaltsit-animated')
    kaltsit.update(animation_image=animated['image'],animation_sha256=animated['sha256'])
    for sample in (kaltsit,next(s for s in selected if s['id']=='myrtle_owned')):
        result.append({'id':sample['id']+':animation','frames':[frame(sample),frame(sample,'animation')],
            'measure_from_frame':1,'group':'continuous',
            'provenance':('preexisting native pair; capture order not independently proven' if
                sample['id']=='operator-kaltsit' else 'previous ordered real owned-popup capture pair')})
    menu=read(MAIN_MENU/'capture.json')['frames'][:2]
    menus=[]
    for index,item in enumerate(menu):
        path=(MAIN_MENU/item['file']).relative_to(ROOT).as_posix();assert sha(ROOT/path)==item['sha256']
        item={'file':path,'sha256':item['sha256'],'client_rect':item['client_rect'],'variant':'native'}
        menus.append(item)
        result.append({'id':'main-menu-independent-'+str(index),'frames':[item],
            'negative_after_frame':0,'group':'negative','provenance':'actual 0.57 WGC main-menu capture'})
    mech=next(s for s in selected if s['id']=='operator-mechanist')
    result.append({'id':'operator-to-main-menu','frames':[frame(mech),*menus],
        'negative_after_frame':1,'measure_from_frame':1,'group':'transition',
        'provenance':'different actual pages concatenated; not a live transition capture'})
    assert len(result)==22
    return result


def make_package(folder):
    """Freeze the old source, supplement only immutable public media assets."""
    manifest=read(BEFORE/'manifest.json')['source_hashes'];package=folder/'baseline-source'
    originals={};supplement={}
    for path in (BEFORE/'rouge').rglob('*'):
        if not path.is_file() or '__pycache__' in path.parts:continue
        name=path.relative_to(BEFORE).as_posix();assert sha(path)==manifest[name]
        dest=package/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
        originals[name]=sha(dest)
    for path in (ROOT/'rouge/data').rglob('*'):
        if not path.is_file() or path.suffix=='.json' or '__pycache__' in path.parts:continue
        name=path.relative_to(ROOT).as_posix();dest=package/name
        if dest.exists():continue
        dest.parent.mkdir(parents=True,exist_ok=True)
        try:os.link(path,dest)
        except OSError:shutil.copyfile(path,dest)
        supplement[name]=sha(dest)
    write(folder/'baseline-package-seal.json',{'before_manifest_sha256':sha(BEFORE/'manifest.json'),
        'frozen_original_sources':originals,'supplemented_current_public_media':supplement,
        'private_state_read':False})


def inventory(folder):
    folder.mkdir(parents=True,exist_ok=False)
    make_package(folder)
    write(folder/'inventory.json',{'cases':planned_cases(),'source_sha256':public_seal(),
        'sample_inventory_sha256':sha(OLD_INVENTORY),'main_menu_capture_sha256':sha(MAIN_MENU/'capture.json'),
        'baseline_version':'0.57','verifier_sha256':sha(__file__),
        'private_state_read':False,'game_actions':0,'chat_requests':0})
    print(json.dumps({'epoch':str(folder),'cases':22}),flush=True)


def image_for(item):
    path=ROOT/item['file'];assert sha(path)==item['sha256']
    image=cv2.imdecode(np.fromfile(path,np.uint8),1);assert image is not None
    rect=deepcopy(item['client_rect'])
    if item['variant']=='scaled_translated':
        h,w=image.shape[:2];nw,nh=round(w*.83),round(h*.83)
        image=cv2.resize(image,(nw,nh),interpolation=cv2.INTER_AREA)
        image=cv2.copyMakeBorder(image,31,17,43,19,cv2.BORDER_CONSTANT,value=(170,170,170))
        rect=([43,31,nw+43,nh+31] if rect is None else
            [round(rect[0]*nw/w)+43,round(rect[1]*nh/h)+31,round(rect[2]*nw/w)+43,round(rect[3]*nh/h)+31])
    return image,rect


def worker(package,case,output):
    package=Path(package).resolve();sys.path.insert(0,str(package))
    from rouge.recognition import ScreenReader
    assert Path(sys.modules['rouge.recognition'].__file__).resolve()==package/'rouge/recognition.py'
    reader=ScreenReader();rows=[]
    for item in case['frames']:
        image,rect=image_for(item);result=reader.read(image,client_rect=rect)
        assert result['performance']['reuse']!='exact_frame'
        engine=getattr(reader._engine,'engine',reader._engine)
        assert type(engine).__module__.startswith('rapidocr_onnxruntime')
        rows.append({'observation':json.loads(json.dumps({k:result.get(k) for k in FIELDS},ensure_ascii=False)),
            'performance':result['performance'],'actual_raw_ocr':deepcopy(getattr(reader._frame_ocr,'raw',None)),
            'frame_ocr_metrics':deepcopy(getattr(reader._frame_ocr,'metrics',{})),
            'page_ocr_metrics':deepcopy(getattr(getattr(reader,'_page_ocr',None),'metrics',{}))})
    write(output,{'case':case['id'],'frames':rows,'actual_rapidocr_engine':True})


def replay(folder,budget,case_filter=None):
    data=read(folder/'inventory.json');start=public_seal();verifier=sha(__file__)
    stage=folder/('paired-'+str(time.time_ns()));stage.mkdir()
    present={}
    for path in folder.glob('paired-*/rows/*.json'):
        value=read(path)
        if value['source_sha256']==start and value['verifier_sha256']==verifier:present[value['case']]=value
    started=time.perf_counter();completed=0
    for index,case in enumerate(data['cases']):
        if case_filter and case_filter not in case['id']:continue
        if case['id'] in present:continue
        if completed and time.perf_counter()-started>=budget:break
        name=case['id'].replace(':','-');casepath=stage/'cases'/(name+'.json');write(casepath,case)
        outputs={};order=['baseline','current'] if index%2==0 else ['current','baseline']
        for label in order:
            destination=stage/'workers'/(name+'-'+label+'.json')
            package=folder/'baseline-source' if label=='baseline' else ROOT
            process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'worker','--package',str(package),
                '--case',str(casepath),'--output',str(destination)],capture_output=True,text=True,encoding='utf-8')
            if process.returncode:
                write(stage/('failure-'+str(time.time_ns())+'.json'),{'case':case['id'],'label':label,
                    'exit':process.returncode,'stdout':process.stdout,'stderr':process.stderr})
                raise RuntimeError('Real OCR worker failed; full diagnostic preserved')
            outputs[label]=read(destination)
        diffs=[]
        for i,(before,after) in enumerate(zip(outputs['baseline']['frames'],outputs['current']['frames'])):
            diffs.extend(differences(strict(before['observation']),strict(after['observation']),'/frames/'+str(i)))
        negative=True
        if 'negative_after_frame' in case:
            negative=all(r['observation']['page']=='unknown' and r['observation']['operator'] is None
                and r['observation']['run'] is None for r in outputs['current']['frames'][case['negative_after_frame']:])
        assert start==public_seal(),'public production source changed during replay'
        assert verifier==sha(__file__),'verifier changed during replay'
        row={'case':case['id'],'passed':not diffs and negative,'strict_semantic_differences':diffs,
            'negative_passed':negative,'group':case['group'],'measure_from_frame':case.get('measure_from_frame',0),
            'provenance':case['provenance'],'source_sha256':start,'verifier_sha256':verifier,
            'order':order,'outputs':outputs,'private_state_read':False,'game_actions':0,'chat_requests':0}
        write(stage/'rows'/(name+'.json'),row);completed+=1
        print(json.dumps({'case':case['id'],'passed':row['passed'],'differences':diffs[:8],
            'times_ms':{label:[r['performance']['total_ms'] for r in value['frames']] for label,value in outputs.items()},
            'strategies':[r['performance'].get('routing') for r in outputs['current']['frames']]},ensure_ascii=False),flush=True)
    write(stage/'segment.json',{'completed':completed,'seconds':time.perf_counter()-started,
        'source_stable':start==public_seal(),'source_sha256':start,'verifier_sha256':verifier})


def percentile(values,fraction):
    if not values:return None
    values=sorted(values);pos=(len(values)-1)*fraction;i=int(pos);j=min(len(values)-1,i+1)
    return values[i]+(values[j]-values[i])*(pos-i)


def summary(folder):
    current=public_seal();verifier=sha(__file__);chosen={}
    for path in sorted(folder.glob('paired-*/rows/*.json')):
        value=read(path)
        if value['source_sha256']==current and value['verifier_sha256']==verifier:chosen[value['case']]=(path,value)
    expected={c['id'] for c in read(folder/'inventory.json')['cases']};metrics={}
    for group in ('cold','continuous','negative','transition'):
        metrics[group]={}
        for label in ('baseline','current'):
            times=[r['performance']['total_ms'] for _,v in chosen.values() if v['group']==group
                for r in v['outputs'][label]['frames'][v['measure_from_frame']:]]
            metrics[group][label]={'count':len(times),'p50_ms':percentile(times,.5),'p95_ms':percentile(times,.95),'times_ms':times}
    receipt={'passed':expected==set(chosen) and all(v['passed'] for _,v in chosen.values()),
        'source_sha256':current,'verifier_sha256':verifier,'expected_cases':sorted(expected),
        'missing_cases':sorted(expected-set(chosen)),'failed_cases':[k for k,(_,v) in chosen.items() if not v['passed']],
        'strict_equal_cases':sum(v['passed'] for _,v in chosen.values()),'metrics':metrics,
        'replay_receipts':{p.relative_to(ROOT).as_posix():sha(p) for p,_ in chosen.values()},
        'all_fact_confidence_geometry_leaves_compared':True,'excluded_keys':['elapsed_ms'],
        'private_state_read':False,'game_actions':0,'chat_requests':0,
        'limits':['Existing development corpus; new classifier assets may be trained on these sources.',
            'Four resized/translated cold cases are derived, not independent holdout.',
            'Two real animation pairs; main-menu transition concatenates old actual captures.',
            'Local single-pair elapsed statistics are descriptive, not universal speed claims.',
            'Cold page scheduling retains all detected text; it does not prove page exclusivity.']}
    destination=folder/('summary-'+str(time.time_ns())+'.json');write(destination,receipt)
    print(json.dumps({'receipt':str(destination),'passed':receipt['passed'],'missing':receipt['missing_cases'],
        'failed':receipt['failed_cases'],'metrics':metrics},ensure_ascii=False),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('inventory','worker','replay','summary'))
    parser.add_argument('--epoch');parser.add_argument('--package');parser.add_argument('--case');parser.add_argument('--output')
    parser.add_argument('--budget-seconds',type=float,default=50);parser.add_argument('--case-filter')
    options=parser.parse_args()
    if options.mode=='worker':worker(options.package,read(options.case),options.output)
    else:
        folder=Path(options.epoch).resolve() if options.epoch else RESEARCH/('epoch-'+str(time.time_ns()))
        if options.mode=='inventory':inventory(folder)
        elif options.mode=='replay':replay(folder,options.budget_seconds,options.case_filter)
        else:summary(folder)
