"""Public-reader timings and evidence parity; no game or chat interaction."""
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time
from copy import deepcopy
from datetime import datetime,timezone
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.recognition import ScreenReader


def evidence(result):
    result = deepcopy(result)
    for key in ('observed_at','performance'):
        result.pop(key,None)
    return result


def timed(reader,image,rect=None):
    before = time.perf_counter()
    result = reader.read(image,client_rect=rect)
    return result,round((time.perf_counter()-before)*1000,3)


def main():
    files = ['rouge/recognition.py','rouge/recognition_cache.py','rouge/run_recognition.py',
        'rouge/relic_recognition.py','rouge/operator_recognition.py','rouge/node_events.py',
        'rouge/map_recognition.py','rouge/viewport.py','rouge/data/node-generation.json',
        'rouge/data/node-events.json','scripts/verify_recognition_speed_0_19.py']
    hashes_before = {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files}
    uncached = ScreenReader(cache_enabled=False)
    cached = ScreenReader()
    cases = []
    samples = ['exploration-map.png','map-template-node-detail.png','operator-mechanist.png',
               'module-mechanist.png','run-roster.png','run-relic-multicard.png']
    for name in samples:
        image = cv2.imdecode(np.fromfile(ROOT/'samples/native-client'/name,dtype=np.uint8),1)
        baseline,base_ms = timed(uncached,image)
        cold,cold_ms = timed(cached,image)
        assert evidence(cold)==evidence(baseline),(name,'cold evidence differs')
        repeated_ms = []
        for _ in range(3):
            repeated,elapsed = timed(cached,image.copy())
            assert evidence(repeated)==evidence(baseline),(name,'repeated evidence differs')
            assert repeated['performance']['reuse']=='exact_frame'
            repeated_ms.append(elapsed)
        # Controlled background animation: no approximate whole-frame reuse.
        animated = image.copy()
        y,x = round(image.shape[0]*.35),round(image.shape[1]*.02)
        animated[y:y+8,x:x+8] = 255-animated[y:y+8,x:x+8]
        fresh_animation,fresh_ms = timed(uncached,animated)
        warm_animation,warm_ms = timed(cached,animated)
        assert evidence(fresh_animation)==evidence(warm_animation),(name,'animation evidence differs')
        assert warm_animation['performance']['reuse']=='none'
        row = {'sample':name,'page':cold['page'],'evidence_parity':True,
            'uncached_ms':base_ms,'cached_cold_ms':cold_ms,
            'exact_frame_ms_median':statistics.median(repeated_ms),
            'changed_frame_uncached_ms':fresh_ms,'changed_frame_cached_ms':warm_ms,
            'changed_frame_performance':warm_animation['performance']}
        cases.append(row)
        print(json.dumps(row,ensure_ascii=False),flush=True)
    geometry = []
    source = cv2.imdecode(np.fromfile(ROOT/'samples/native-client/module-mechanist.png',dtype=np.uint8),1)
    for label,image,rect in [('changed_client_rect',source,[2,45,source.shape[1]-2,source.shape[0]-2]),
            ('resized_with_black_padding',cv2.copyMakeBorder(cv2.resize(source,(1337,735)),71,37,43,19,cv2.BORDER_CONSTANT,value=0),None)]:
        baseline,_ = timed(uncached,image,rect)
        actual,elapsed = timed(cached,image,rect)
        assert evidence(actual)==evidence(baseline),(label,'geometry evidence differs')
        assert actual['performance']['reuse']=='none'
        geometry.append({'case':label,'evidence_parity':True,'viewport':actual['viewport'],'elapsed_ms':elapsed})
    hashes_after = {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files}
    assert hashes_before==hashes_after,'Runtime/data/benchmark source changed during measurement; rerun on stable sources.'
    receipt = {'version':'0.19.0','cases':cases,'geometry_cases':geometry,
        'verified_at':datetime.now(timezone.utc).isoformat(),'chat_requests':0,
        'all_evidence_parity':True,'cache_requires':'Exact pixels, shape, dtype and call geometry/parameters; digest followed by byte comparison.',
        'memory':'One frame <=32 MiB; OCR pixels <=8 MiB/24 entries; relic/potential ROI pixels <=2 MiB/8 entries; output snapshots additional.',
        'limitations':['Synthetic changed background only; real animation may change OCR crops/bar and miss cache.',
            'One measurement per full read, three exact repeats; CPU concurrency can affect timings.',
            'Full-suite and Qt validation may run concurrently; paired uncached/cached reads alternate in the same process. Timings are not isolated CPU benchmarks.',
            'No approximate reuse, lower confidence threshold or resolution degradation; cold-path workload remains.'],
        'source_hashes':hashes_after}
    (ROOT/'RECOGNITION_SPEED_0.19_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
    print('Verified six page types, exact repeats, changed backgrounds and two geometry changes.',flush=True)


if __name__=='__main__':main()
