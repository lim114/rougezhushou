"""Compare the changed reader against its Git baseline on local-only frames.

Usage: python scripts/verify_text_row_sync.py PRIVATE_FRAME_DIR PUBLIC_RECEIPT_DIR
Frames and interpreted observations stay local. The receipt contains only timing,
equality results and product source identity. No game action or state file writes.
"""
from pathlib import Path
from hashlib import sha256
from types import ModuleType
import argparse,json,statistics,subprocess,sys,time
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('frames',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();args.output.mkdir(exist_ok=False,parents=True)
    paths=sorted(args.frames.glob('*.png'),key=lambda p:int(p.stem))
    assert len(paths)>=3
    from rouge.recognition import ScreenReader
    baseline=ModuleType('rouge._prior_text_row_reader');baseline.__package__='rouge'
    before=subprocess.check_output(['git','show','6f98c7fe7ea13f10f0164a23f9aec51f8d367fe3:rouge/recognition.py'],cwd=ROOT)
    exec(compile(before,'prior_recognition.py','exec'),baseline.__dict__)
    readers={'before':baseline.ScreenReader(),'after':ScreenReader()}
    paths+= [ROOT/'samples/native-client'/f'{name}.png' for name in
             ('run-map-closed','map-template-node-detail','run-mechanist-selected','module-mechanist','operator-mechanist')]
    frozen={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ('rouge/recognition.py','rouge/dynamic_ocr.py','rouge/page_ocr.py','tests/test_ocr_text_row_reuse.py')}
    rows=[];comparisons=[]
    def facts(x):
        if isinstance(x,dict):return {k:facts(v) for k,v in x.items() if k not in ('performance','observed_at')}
        if isinstance(x,list):return [facts(v) for v in x]
        return x
    for index,path in enumerate(paths):
        image=cv2.imdecode(np.fromfile(path,np.uint8),1);assert image is not None
        results={}
        for name in (('before','after') if index%2==0 else ('after','before')):
            started=time.perf_counter();results[name]=readers[name].read(image);ms=(time.perf_counter()-started)*1000
            row={'input':index,'mode':name,'total_ms':round(ms,3),
                 'ocr_ms':round(results[name]['performance']['stages_ms'].get('full_ocr',0),3),
                 'reused_rows':results[name]['performance'].get('ocr',{}).get('reused_text_rows',0),
                 'inferred_rows':results[name]['performance'].get('ocr',{}).get('inferred_text_rows',0)}
            rows.append(row);print(json.dumps(row),flush=True)
        a,b=facts(results['before']),facts(results['after'])
        differences=[k for k in sorted(a.keys()|b.keys()) if a.get(k)!=b.get(k)]
        comparisons.append({'input':index,'exact_observation_match':not differences,'different_fields':differences})
    count=len(paths)-5
    value={'passed':all(x['exact_observation_match'] for x in comparisons),'baseline_commit':'6f98c7fe7ea13f10f0164a23f9aec51f8d367fe3',
           'stream_frames':count,'other_existing_page_frames':5,'cold_first_frame_excluded_from_stream_timing':True,
           'stream_median_ms':{name:statistics.median(x['total_ms'] for x in rows if x['mode']==name and 0<x['input']<count) for name in readers},
           'comparisons':comparisons,'timings':rows,'source_sha256':frozen,
           'raw_images_observations_uploaded':False,'game_operated':False,'state_files_written':False,
           'scope':'Same local captured frames, alternate reader order, both warmed by first frame. Five existing page fixtures extend equality checks; this is not continuous short-page acceptance.'}
    assert frozen=={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in frozen}
    (args.output/'summary.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8',newline='\n')
    print(json.dumps({k:v for k,v in value.items() if k not in ('timings','source_sha256','comparisons')}),flush=True)
    return 0 if value['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
