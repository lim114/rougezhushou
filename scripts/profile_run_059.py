"""Profile an unchanged read_run seam against sealed actual 0.58 inputs.

No model/global function is patched. The injected OCR callable forwards every
crop unchanged to one real RapidOCR instance, with the existing exact cache.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import cProfile
import hashlib
import json
from pathlib import Path
import pstats
import sys
import time

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.recognition_cache import CachedOCR,ExactImageCache
from rouge.run_recognition import read_run
from rouge.viewport import prepare_frame,map_evidence


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def wire(value):
    return json.loads(json.dumps(value,ensure_ascii=False,
        default=lambda item:item.item() if isinstance(item,np.generic) else item.tolist()))


def strict(value):
    if isinstance(value,dict):return {k:strict(v) for k,v in value.items() if k!='elapsed_ms'}
    if isinstance(value,list):return [strict(v) for v in value]
    return value


def differences(before,after,path=''):
    if type(before) is not type(after):return [{'path':path,'before':before,'after':after}]
    if isinstance(before,dict):
        result=[]
        for key in sorted(set(before)|set(after)):
            if key not in before or key not in after:
                result.append({'path':path+'/'+key,'before':before.get(key),'after':after.get(key),'missing':True})
            else:result.extend(differences(before[key],after[key],path+'/'+key))
        return result
    if isinstance(before,list):
        result=[] if len(before)==len(after) else [{'path':path+'/length','before':len(before),'after':len(after)}]
        for i,(a,b) in enumerate(zip(before,after)):result.extend(differences(a,b,path+'/'+str(i)))
        return result
    return [] if before==after else [{'path':path,'before':before,'after':after}]


def sources():
    files=[*(ROOT/'rouge').rglob('*.py'),*(ROOT/'rouge/data').rglob('*.json'),Path(__file__)]
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(files))}


class TimedOCR:
    def __init__(self,engine):self.engine=engine;self.calls=[]

    def __call__(self,image,**kwargs):
        caller=sys._getframe(1)
        start=time.perf_counter();hits=self.engine.cache.hits
        result=self.engine(image,**kwargs)
        elapsed=(time.perf_counter()-start)*1000
        output=wire(result[0])
        self.calls.append({'caller':caller.f_code.co_name,
            'file':Path(caller.f_code.co_filename).relative_to(ROOT).as_posix(),
            'line':caller.f_lineno,'shape':list(image.shape),'dtype':image.dtype.str,
            'kwargs':kwargs,'image_sha256':hashlib.sha256(np.ascontiguousarray(image).tobytes()).hexdigest(),
            'elapsed_ms':elapsed,'exact_cache_hit':self.engine.cache.hits>hits,
            'output':output,'output_sha256':hashlib.sha256(json.dumps(output,sort_keys=True).encode()).hexdigest()})
        return result


def main(case_id):
    baseline=ROOT/'HYBRID_0.58_VERIFICATION.json'
    proof=json.loads(baseline.read_text(encoding='utf-8'));assert proof['passed']
    selected=[(ROOT/p,digest) for p,digest in proof['replay_receipts'].items()
              if json.loads((ROOT/p).read_text(encoding='utf-8'))['case']==case_id]
    assert len(selected)==1,case_id
    row_path,row_sha=selected[0];assert sha(row_path)==row_sha
    row=json.loads(row_path.read_text(encoding='utf-8'))
    frame=row['outputs']['current']['frames'][0]
    inventory=ROOT/'.cache/research/hybrid-058/epoch-current/inventory.json'
    cases=json.loads(inventory.read_text(encoding='utf-8'))['cases']
    case=next(c for c in cases if c['id']==case_id)
    assert len(case['frames'])==1 and case['frames'][0]['variant']=='native'
    sample=case['frames'][0];image_path=ROOT/sample['file'];assert sha(image_path)==sample['sha256']
    image=cv2.imdecode(np.fromfile(image_path,np.uint8),cv2.IMREAD_COLOR)
    image,viewport=prepare_frame(image,sample['client_rect'])
    assert viewport==frame['observation']['viewport']
    raw=frame['actual_raw_ocr']
    assert raw,'This profile requires retained actual original full raw OCR; no synthesized text.'
    h,w=image.shape[:2]
    texts=[{'text':text.replace(' ',''),'confidence':float(score),
            'box':[[float(x)/w,float(y)/h] for x,y in box]} for box,text,score in raw]
    epoch=ROOT/'.cache/research/run-performance-059'/f'profile-{time.time_ns()}'
    epoch.mkdir(parents=True,exist_ok=False)
    before=sources()
    provider=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
    timed=TimedOCR(CachedOCR(provider))
    profiler=cProfile.Profile()
    started=time.perf_counter();profiler.enable()
    actual=read_run(image,texts,timed,icon_cache=ExactImageCache(max_bytes=2*1024*1024,max_entries=8),run_context=None)
    profiler.disable();elapsed=(time.perf_counter()-started)*1000
    profile_path=epoch/'profile.pstats';profiler.dump_stats(profile_path)
    stats=pstats.Stats(profiler)
    rows=[]
    for (filename,line,name),(primitive,calls,self_time,total_time,callers) in stats.stats.items():
        if name=='<module>':continue
        rows.append({'file':filename,'line':line,'function':name,'primitive_calls':primitive,
                     'calls':calls,'self_ms':self_time*1000,'cumulative_ms':total_time*1000})
    rows.sort(key=lambda row:row['cumulative_ms'],reverse=True)
    mapped={'run':deepcopy(actual)};map_evidence(mapped,viewport)
    diff=differences(strict(wire(frame['observation']['run'])),strict(wire(mapped['run'])))
    after=sources();drift=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]
    receipt={'passed':not diff and not drift,'case':case_id,'scope':'Unchanged read_run seam with sealed actual full-frame OCR inputs.',
        'elapsed_ms':elapsed,'ocr_calls':timed.calls,'ocr_elapsed_ms':sum(c['elapsed_ms'] for c in timed.calls),
        'function_costs':rows,'strict_run_differences':diff,'excluded_keys':['elapsed_ms'],
        'actual_run':wire(actual),'expected_source_run':frame['observation']['run'],
        'profile_pstats':profile_path.relative_to(ROOT).as_posix(),'profile_pstats_sha256':sha(profile_path),
        'source_sha256':before,'source_sha256_after':after,'source_drift':drift,
        'baseline_receipt':baseline.relative_to(ROOT).as_posix(),'baseline_sha256':sha(baseline),
        'row':row_path.relative_to(ROOT).as_posix(),'row_sha256':row_sha,
        'sample':sample,'sample_sha256':sha(image_path),'analysis_shape':list(image.shape),
        'actual_text_input_sha256':hashlib.sha256(json.dumps(texts,sort_keys=True).encode()).hexdigest(),
        'actual_text_count':len(texts),'singleton_rapidocr':True,'provider_or_global_patches':0,
        'private_state_read':False,'game_actions':0,'chat_requests':0,
        'limits':['Existing public development sample; profiler overhead is included.',
                  'Original full OCR input is retained from 0.58, not recomputed or approximated.',
                  'cProfile reports aggregate matcher costs, not per-reference candidate timing.']}
    output=epoch/'receipt.json'
    with output.open('x',encoding='utf-8') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2)
    print(json.dumps({'passed':receipt['passed'],'receipt':str(output),'case':case_id,'elapsed_ms':elapsed,
        'ocr_calls':len(timed.calls),'ocr_elapsed_ms':receipt['ocr_elapsed_ms'],
        'strict_run_differences':diff,'top_functions':rows[:14]},ensure_ascii=False),flush=True)
    return 0 if receipt['passed'] else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--case',default='kaltsit_owned:native')
    raise SystemExit(main(parser.parse_args().case))
