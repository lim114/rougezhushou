"""Three derived popup boundary cases, separate from the frozen 23-case plan.

Preparation only creates lossless derivatives of public development samples.
Replay is an explicitly scheduled CPU operation. It delegates actual OCR to
the unchanged hybrid verifier and compares every public observation leaf.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys
import time

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
HYBRID=ROOT/'scripts/verify_hybrid_059.py'
SPEC=importlib.util.spec_from_file_location('hybrid_059_boundaries',HYBRID)
H=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(H)
FEATURE_TEST=ROOT/'tests/test_page_features_059.py'


def source_client(sample):
    path=ROOT/sample['image'];assert H.sha(path)==sample['sha256']
    image=cv2.imdecode(np.fromfile(path,dtype=np.uint8),cv2.IMREAD_COLOR)
    assert image is not None
    if sample['client_rect'] is not None:
        left,top,right,bottom=sample['client_rect']
        image=image[top:bottom,left:right].copy()
    return image


def prepare(epoch):
    """Exactly reproduce the two .5 and one padding feature-test inputs."""
    folder=epoch/'popup-boundaries';folder.mkdir(exist_ok=False)
    samples=H.read(H.OLD_INVENTORY)['samples'];cases=[];provenance=[]
    for name,recipe in (('kaltsit_owned','half_client'),
                        ('myrtle_owned','half_client'),
                        ('myrtle_owned','padded_35_45')):
        sample=next(s for s in samples if s['id']==name)
        original=source_client(sample)
        if recipe=='half_client':
            image=cv2.resize(original,None,fx=.5,fy=.5)
            transform={'factor':.5,'interpolation':'OpenCV default INTER_LINEAR'}
        else:
            height,width=original.shape[:2]
            image=np.zeros((height+95,width+125,3),np.uint8)
            image[35:35+height,45:45+width]=original
            transform={'added_height':95,'added_width':125,'left':45,'top':35,
                       'padding_bgr':[0,0,0]}
        file=folder/'images'/(name+'-'+recipe+'.png');file.parent.mkdir(exist_ok=True)
        success,encoded=cv2.imencode('.png',image);assert success
        with file.open('xb') as stream:stream.write(encoded.tobytes())
        restored=cv2.imdecode(np.fromfile(file,dtype=np.uint8),cv2.IMREAD_COLOR)
        assert np.array_equal(restored,image)
        case={'id':name+':'+recipe,'frames':[{'file':file.relative_to(ROOT).as_posix(),
            'sha256':H.sha(file),'client_rect':None,'variant':recipe}],
            'group':'boundary_derived','provenance':'derived feature-test boundary; not independent holdout'}
        cases.append(case)
        provenance.append({'case':case['id'],'source':{'file':sample['image'],
            'sha256':sample['sha256'],'client_rect':sample['client_rect']},
            'recipe':transform,'client_image_shape':list(original.shape),
            'derived_image_shape':list(image.shape),'lossless_roundtrip_equal':True,
            'screenreader_input':'whole derived frame; client_rect=None',
            'viewport_behavior':'existing prepare_frame remains active; contiguous black padding may be removed before classification'})
    H.write(folder/'inventory.json',{'cases':cases,'provenance':provenance,
        'source_sha256':H.public_seal(),'verifier_sha256':H.sha(__file__),
        'hybrid_verifier_sha256':H.sha(HYBRID),'feature_test_sha256':H.sha(FEATURE_TEST),
        'formal_cases_not_modified':23,'additional_derived_cases':3,
        'baseline_package_seal_sha256':H.sha(epoch/'baseline-package-seal.json'),
        'private_state_read':False,'game_actions':0,'chat_requests':0})
    print({'prepared':str(folder),'additional_derived_cases':3},flush=True)


def replay(epoch,budget):
    folder=epoch/'popup-boundaries';inventory=H.read(folder/'inventory.json')
    start=H.public_seal();verifier=H.sha(__file__);hybrid=H.sha(HYBRID)
    assert inventory['source_sha256']==start
    assert inventory['verifier_sha256']==verifier
    assert inventory['hybrid_verifier_sha256']==hybrid
    assert inventory['baseline_package_seal_sha256']==H.sha(epoch/'baseline-package-seal.json')
    stage=folder/('paired-'+str(time.time_ns()));stage.mkdir()
    present={}
    for path in folder.glob('paired-*/rows/*.json'):
        row=H.read(path)
        if (row['source_sha256']==start and row['verifier_sha256']==verifier
                and row['hybrid_verifier_sha256']==hybrid):present[row['case']]=row
    started=time.perf_counter();completed=0
    for index,case in enumerate(inventory['cases']):
        if case['id'] in present:continue
        if completed and time.perf_counter()-started>=budget:break
        slug=case['id'].replace(':','-');casepath=stage/'cases'/(slug+'.json')
        H.write(casepath,case);outputs={};workers={}
        for label in (('baseline','current') if index%2==0 else ('current','baseline')):
            package=epoch/'baseline-source' if label=='baseline' else ROOT
            destination=stage/'workers'/(slug+'-'+label+'.json')
            process=subprocess.run([sys.executable,str(HYBRID),'worker','--package',str(package),
                '--case',str(casepath),'--output',str(destination)],capture_output=True,
                text=True,encoding='utf-8')
            if process.returncode:
                H.write(stage/('failure-'+str(time.time_ns())+'.json'),{'case':case['id'],
                    'label':label,'exit':process.returncode,'stdout':process.stdout,'stderr':process.stderr})
                raise RuntimeError('Boundary actual OCR worker failed; full diagnostic preserved')
            outputs[label]=H.read(destination)
            workers[label]={'path':destination.relative_to(ROOT).as_posix(),'sha256':H.sha(destination)}
        before=outputs['baseline']['frames'][0]['observation']
        after=outputs['current']['frames'][0]['observation']
        diffs=H.differences(H.strict(before),H.strict(after),'/frames/0')
        route=outputs['current']['frames'][0]['performance'].get('routing',{})
        route_verified=(after['page']=='run_roster' and route.get('strategy')=='visual_region_ocr'
            and route.get('candidates')==['run_owned_popup'] and route.get('semantic_verified') is True)
        assert start==H.public_seal(),'Production changed during boundary replay'
        assert verifier==H.sha(__file__) and hybrid==H.sha(HYBRID),'Verifier changed during replay'
        row={'case':case['id'],'passed':not diffs and route_verified,'outputs':outputs,
            'strict_semantic_differences':diffs,'route_verified':route_verified,
            'source_sha256':start,'verifier_sha256':verifier,'hybrid_verifier_sha256':hybrid,
            'case_receipt':{'path':casepath.relative_to(ROOT).as_posix(),'sha256':H.sha(casepath)},
            'worker_receipts':workers,'all_fact_confidence_geometry_leaves_compared':True,
            'excluded_keys':['elapsed_ms'],'private_state_read':False,'game_actions':0,'chat_requests':0}
        H.write(stage/'rows'/(slug+'.json'),row);completed+=1
        print({'case':case['id'],'passed':row['passed'],'strict_differences':diffs,
            'route':route,'times_ms':{k:v['frames'][0]['performance']['total_ms'] for k,v in outputs.items()}},flush=True)
    H.write(stage/'segment.json',{'completed':completed,'seconds':time.perf_counter()-started,
        'source_sha256':start,'source_stable':start==H.public_seal(),
        'verifier_sha256':verifier,'hybrid_verifier_sha256':hybrid})


def summary(epoch):
    folder=epoch/'popup-boundaries';inventory=H.read(folder/'inventory.json')
    current=H.public_seal();verifier=H.sha(__file__);hybrid=H.sha(HYBRID);rows={}
    for path in sorted(folder.glob('paired-*/rows/*.json')):
        row=H.read(path)
        if (row['source_sha256']==current and row['verifier_sha256']==verifier
                and row['hybrid_verifier_sha256']==hybrid):rows[row['case']]=(path,row)
    expected={c['id'] for c in inventory['cases']};assert len(expected)==3
    receipt={'passed':expected==set(rows) and all(r['passed'] for _,r in rows.values()),
        'expected_cases':sorted(expected),'missing_cases':sorted(expected-set(rows)),
        'failed_cases':[name for name,(_,row) in rows.items() if not row['passed']],
        'strict_semantic_differences':[d for _,row in rows.values() for d in row['strict_semantic_differences']],
        'strict_equal_cases':sum(not row['strict_semantic_differences'] for _,row in rows.values()),
        'additional_derived_cases':3,'formal_case_count_unchanged':23,
        'source_sha256':current,'verifier_sha256':verifier,'hybrid_verifier_sha256':hybrid,
        'all_fact_confidence_geometry_leaves_compared':True,'excluded_keys':['elapsed_ms'],
        'inventory':{'path':(folder/'inventory.json').relative_to(ROOT).as_posix(),
                     'sha256':H.sha(folder/'inventory.json')},
        'replay_receipts':{p.relative_to(ROOT).as_posix():H.sha(p) for p,_ in rows.values()},
        'baseline_package_seal_sha256':H.sha(epoch/'baseline-package-seal.json'),
        'limits':['Three lossless derivatives of existing development samples, not new independent captures.',
            'Feature-test inputs are reproduced exactly; ScreenReader viewport preparation can remove black padding.',
            'All public observation leaves are compared; only elapsed_ms is excluded.'],
        'private_state_read':False,'game_actions':0,'chat_requests':0}
    destination=folder/('summary-'+str(time.time_ns())+'.json');H.write(destination,receipt)
    print({'receipt':str(destination),'passed':receipt['passed'],'missing':receipt['missing_cases'],
        'failed':receipt['failed_cases'],'strict_differences':receipt['strict_semantic_differences']},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('prepare','replay','summary'))
    parser.add_argument('--epoch',required=True);parser.add_argument('--budget-seconds',type=float,default=45)
    args=parser.parse_args();epoch=Path(args.epoch).resolve()
    if args.mode=='prepare':prepare(epoch)
    elif args.mode=='replay':replay(epoch,args.budget_seconds)
    else:summary(epoch)
