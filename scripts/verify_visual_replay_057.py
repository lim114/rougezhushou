"""Real VisualReader replay; no OCR engine, game operation, or chat calls.

The archived 0.56 VisualReader module and the current module use the same pinned
public anchors and helper implementation in this process. This comparison tests
the VisualReader change, not a claim that all 0.56 helpers are independently run.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import sys
import time

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.visual_recognition import VisualReader


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')


def semantics(value):
    if isinstance(value,dict):
        return {key:semantics(item) for key,item in value.items()
                if key not in ('observed_at','performance','elapsed_ms')}
    if isinstance(value,list):return [semantics(item) for item in value]
    return value


def differences(before,after,path=''):
    if type(before) is not type(after):
        return [{'path':path,'before':before,'after':after,'reason':'type'}]
    if isinstance(before,dict):
        output=[]
        for key in sorted(set(before)|set(after)):
            sub=path+'/'+key
            if key not in before:output.append({'path':sub,'after':after[key],'reason':'added'})
            elif key not in after:output.append({'path':sub,'before':before[key],'reason':'removed'})
            else:output.extend(differences(before[key],after[key],sub))
        return output
    if isinstance(before,list):
        if len(before)!=len(after):return [{'path':path,'before':before,'after':after,'reason':'length'}]
        return [change for index,(old,new) in enumerate(zip(before,after))
                for change in differences(old,new,path+'/'+str(index))]
    return [] if before==after else [{'path':path,'before':before,'after':after,'reason':'value'}]


def load(path):
    image=cv2.imdecode(np.fromfile(path,np.uint8),1)
    if image is None:raise ValueError('Cannot decode '+str(path))
    return image


def public_cases():
    cases=[]
    for path in sorted((ROOT/'samples/native-client').glob('*.png')):
        cases.append({'name':path.stem,'image':load(path),'input_sha256':sha(path)})
    for name in ('operator-mechanist','operator-silverash','operator-kaltsit'):
        image=load(ROOT/'samples/native-client'/f'{name}.png')
        canvas=np.full((1800,3200,3),8,np.uint8);h,w=image.shape[:2]
        canvas[100:100+h,500:500+w]=image
        cases.append({'name':name+'-relocated','image':canvas})
        cases.append({'name':name+'-half-scale','image':cv2.resize(image,None,fx=.5,fy=.5)})
    original=load(ROOT/'samples/native-client/operator-mechanist.png')
    changed=original.copy();changed[100,100]=(255,255,255)
    cases.extend([
        {'name':'operator-mechanist-one-pixel','image':changed},
        {'name':'operator-mechanist-new-run','image':changed,'run_context':{
            'run_id':'public-run-b','config':{'difficulty':{'value':9,'captured_at':1.,'source':'public test'}}}},
        {'name':'operator-mechanist-new-rect','image':changed,
         'client_rect':(0,0,changed.shape[1],changed.shape[0])}])
    cases.extend([{'name':'same-gray-colour-a','image':np.full((720,1280,3),(10,20,30),np.uint8)},
                  {'name':'same-gray-colour-b','image':np.full((720,1280,3),(20,20,26),np.uint8)}])
    return cases


def percentile(values,q):
    ordered=sorted(values);position=(len(ordered)-1)*q;lower=int(position)
    return ordered[lower]+(ordered[min(lower+1,len(ordered)-1)]-ordered[lower])*(position-lower)


def summary(values):
    return {'count':len(values),'median_ms':statistics.median(values),
            'p95_ms':percentile(values,.95),'min_ms':min(values),'max_ms':max(values)}


def source_hashes():
    paths=list((ROOT/'rouge').rglob('*.py'))+list((ROOT/'rouge').rglob('*.json'))
    paths+=list((ROOT/'rouge/data/visual-anchors').glob('*.png'))
    return {str(path.relative_to(ROOT)).replace('\\','/'):sha(path) for path in sorted(paths)}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repeats',type=int,default=5)
    parser.add_argument('--live-manifest',type=Path)
    args=parser.parse_args()
    if args.repeats<1:parser.error('--repeats must be positive')
    output=ROOT/'.cache/research/visual-recognition-057'/f'epoch-{time.time_ns()}'
    output.mkdir(parents=True)
    archive=ROOT/'.cache/batch-057-before'
    old_path=archive/'rouge/visual_recognition.py'
    old_hash=json.loads((archive/'manifest.json').read_text(encoding='utf8'))['source_hashes']['rouge/visual_recognition.py']
    if sha(old_path)!=old_hash:raise AssertionError('Original VisualReader seal changed')
    spec=importlib.util.spec_from_file_location('rouge._visual_before_057',old_path)
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    # The code is sealed old code; asset location is the same immutable current
    # public anchor set for both modules. Its hashes are recorded below.
    old.__file__=str(ROOT/'rouge/visual_recognition.py')
    sources_before=source_hashes()
    write(output/'source-before.json',sources_before)
    before_reader=old.VisualReader();after_reader=VisualReader()
    original=[];current=[];rows=[];failed=[]
    cases=public_cases()
    live_cases=[]
    if args.live_manifest:
        manifest=json.loads(args.live_manifest.read_text(encoding='utf8'))
        for entry in manifest['frames']:
            path=args.live_manifest.parent/entry['file']
            if sha(path)!=entry['sha256']:raise AssertionError('Private live image seal changed')
            case={'name':'authorized-live-main-menu-'+str(entry['seq']),'image':load(path),
                  'client_rect':entry['client_rect'],'input_sha256':entry['sha256'],'private_negative':True}
            live_cases.append(case)
        cases+=live_cases
    for case in cases:
        kwargs={key:case[key] for key in ('client_rect','run_context') if key in case}
        times=[];results=[]
        for reader in (before_reader,after_reader):
            started=time.perf_counter();result=reader.read(case['image'],**deepcopy(kwargs))
            times.append((time.perf_counter()-started)*1000);results.append(result)
        before,after=map(semantics,results)
        changed=differences(before,after)
        if case.get('private_negative'):
            # Do not copy raw live screenshots or any account-identifying data.
            # VisualReader never returns recognized free text; retain only the
            # absence predicate and hashes for this private negative test.
            expected=all(result['operator'] is None and result['run'] is None and result['texts']==[] for result in results)
            if not expected:changed.append({'path':'/private_expected_absence','reason':'unexpected known page'})
            original.append({'case':case['name'],'input_sha256':case['input_sha256'],'expected_absence':expected})
            current.append({'case':case['name'],'input_sha256':case['input_sha256'],'expected_absence':expected})
        else:
            original.append({'case':case['name'],'result':results[0]})
            current.append({'case':case['name'],'result':results[1]})
        rows.append({'case':case['name'],'passed':not changed,'differences':changed,
                     'before_ms':times[0],'after_ms':times[1],'after_cache':results[1]['performance']})
        if changed:failed.extend({'case':case['name'],**change} for change in changed)
    write(output/'original-results.json',original)
    write(output/'current-results.json',current)
    write(output/'semantic-comparison.json',rows)
    write(output/'failed-stage.json',failed)
    if failed:
        write(output/'receipt.json',{'passed':False,'stage':'strict_semantics','cases':len(cases),'differences':len(failed)})
        print(json.dumps({'output':str(output),'passed':False,'stage':'strict_semantics','differences':len(failed)}))
        return 1
    benchmarks=[]
    for name in ('operator-mechanist','operator-kaltsit','run-map-closed'):
        image=load(ROOT/'samples/native-client'/f'{name}.png')
        old_reader=old.VisualReader();new_reader=VisualReader()
        old_reader.read(image);new_reader.read(image)
        old_times=[];new_times=[];reuses=[]
        for _ in range(args.repeats):
            results=[]
            for reader,timings in ((old_reader,old_times),(new_reader,new_times)):
                started=time.perf_counter();result=reader.read(image.copy())
                timings.append((time.perf_counter()-started)*1000);results.append(result)
            if differences(semantics(results[0]),semantics(results[1])):
                raise AssertionError('Exact-repeat semantic difference '+name)
            reuses.append(results[1]['performance']['reuse'])
        benchmarks.append({'case':name,'regime':'exact source/frame + rect/context',
                           'before':summary(old_times),'after':summary(new_times),'after_reuses':reuses})
    animated=None
    if live_cases:
        old_reader=old.VisualReader();new_reader=VisualReader()
        old_times=[];new_times=[];frame_hits=feature_hits=0
        for repeat in range(3):
            for case in live_cases:
                pair=[(old_reader,old_times),(new_reader,new_times)]
                if repeat%2:pair.reverse()
                current_pair={}
                for reader,timings in pair:
                    started=time.perf_counter();result=reader.read(case['image'],client_rect=case['client_rect'])
                    timings.append((time.perf_counter()-started)*1000)
                    current_pair['new' if reader is new_reader else 'old']=result
                    if reader is new_reader:
                        frame_hits+=result['performance']['reuse']=='exact_frame'
                        feature_hits+=result['performance']['feature_cache_hits']
                if differences(semantics(current_pair['old']),semantics(current_pair['new'])):
                    raise AssertionError('Real animation strict semantic difference')
                if any(result['operator'] is not None or result['run'] is not None
                       for result in current_pair.values()):
                    raise AssertionError('Real animation must remain unsupported')
        animated={'regime':'11 actual consecutive main-menu captures, 3 replay passes, paired order alternates',
                  'before':summary(old_times),'after':summary(new_times),
                  'whole_frame_hits':frame_hits,'feature_hits':feature_hits,'all_absence_and_semantics_passed':True}
    sources_after=source_hashes();write(output/'source-after.json',sources_after)
    source_changes=differences(sources_before,sources_after)
    if source_changes:write(output/'source-changes.json',source_changes)
    receipt={'passed':not source_changes,'cases':len(cases),'strict_semantic_differences':0,
             'archived_visual_sha256':old_hash,'production_visual_sha256':sha(ROOT/'rouge/visual_recognition.py'),
             'source_unchanged':not source_changes,'benchmarks':benchmarks,
             'cold_20_public_originals':{
                 'before':summary([row['before_ms'] for row in rows[:20]]),
                 'after':summary([row['after_ms'] for row in rows[:20]])},
             'actual_main_menu_nonexact_sequence':{
                 'count':len(live_cases),
                 'before':summary([row['before_ms'] for row in rows if row['case'].startswith('authorized-live-main-menu-')]) if live_cases else None,
                 'after':summary([row['after_ms'] for row in rows if row['case'].startswith('authorized-live-main-menu-')]) if live_cases else None,
                 'whole_frame_hits':sum(row['after_cache']['reuse']=='exact_frame' for row in rows if row['case'].startswith('authorized-live-main-menu-')),
                 'feature_hits':sum(row['after_cache']['feature_cache_hits'] for row in rows if row['case'].startswith('authorized-live-main-menu-'))},
             'actual_main_menu_nonexact_repeated':animated,
             'scope':'Original VisualReader code vs current code, same sealed public helpers/assets; no OCR or game/chat operation.',
             'omitted_semantic_fields':['observed_at','performance','elapsed_ms'],
             'limits':['Exact source frame reuse only, not approximate animation reuse.',
                       'Exact current gray features only; changed color/context still reruns matching/icons.',
                       'Only pre-existing three operator identities and current potential icons; unsupported numeric fields remain missing.',
                       'Live negatives remain private cache-only and contain no copied screenshots or user text.']}
    write(output/'receipt.json',receipt)
    print(json.dumps({'output':str(output),'passed':receipt['passed'],'cases':len(cases),
                      'strict_semantic_differences':0,'benchmarks':benchmarks},ensure_ascii=False))
    return 0 if receipt['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
