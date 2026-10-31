from pathlib import Path
from types import ModuleType
from hashlib import sha256
from copy import deepcopy
import sys,time,json,statistics
import cv2
import numpy as np

R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from rouge import page_features
from rouge.recognition import ScreenReader
old=ModuleType('rouge.before_page_features');old.__file__=str(R/'rouge/page_features.py');old.__package__='rouge'
exec(compile((R/'research/page-feature-vector-review-20261031/before-page_features.py').read_bytes(),'<baseline-page-features>','exec'),old.__dict__)
out=R/'verification/maintenance/page-feature-vector-review-20261031/paired';out.mkdir(parents=True,exist_ok=False)
rows=[]
for path in sorted((R/'samples/native-client').glob('*.png')):
    im=cv2.imdecode(np.fromfile(path,dtype=np.uint8),cv2.IMREAD_COLOR)
    for variant,image in enumerate((im,cv2.resize(im,None,fx=.8,fy=.8),cv2.copyMakeBorder(im,31,47,29,51,cv2.BORDER_CONSTANT))):
        inputs={};times={};before=old.PageFeatureRouter();after=page_features.PageFeatureRouter()
        for name,router in [('before',before),('after',after)]if len(rows)%2==0 else[('after',after),('before',before)]:
            cv2.setRNGSeed(17);start=time.perf_counter();value=router.classify(image);times[name]=(time.perf_counter()-start)*1000
            value.pop('elapsed_ms');inputs[name]=value
        same=inputs['before']==inputs['after'];assert same,{'case':len(rows)+1}
        rows.append({'case':len(rows)+1,'variant':variant,'entire_plan_equal_except_elapsed_ms':same,'specialized':inputs['after']['specialized'],
            'milliseconds':times,'facts_from_features':inputs['after']['facts_from_features']})
    print(json.dumps({'completed_plan_cases':len(rows)}),flush=True)
# Edge/empty behavior is checked directly against the actual prior implementation.
features=[]
for gray in (np.zeros((10,10),np.uint8),np.full((430,800),90,np.uint8),np.random.default_rng(2).integers(0,256,(197,267),np.uint8)):
    a=old._scene_features(gray);b=page_features._scene_features(gray)
    same=all((x is None and y is None)or(isinstance(x,np.ndarray)and isinstance(y,np.ndarray)and x.shape==y.shape and x.dtype==y.dtype and np.array_equal(x,y))for x,y in zip(a,b))
    assert same;features.append({'case':len(features)+1,'entire_arrays_and_empty_shape_equal':same})
result={'passed':True,'route_cases':rows,'synthetic_feature_cases':features,'scope':'Existing local development images and geometric derivatives; no images, text, file identities or pixel hashes persisted. Equal old/new plans are not accuracy ground truth.','no_private_runtime_state_accessed':True,
    'source_sha256':sha256((R/'rouge/page_features.py').read_bytes()).hexdigest(),'opencv_version':cv2.__version__}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
print(json.dumps({'passed':True,'route_cases':len(rows),'synthetic_feature_cases':len(features),'before_route_median_ms':statistics.median(r['milliseconds']['before']for r in rows),'after_route_median_ms':statistics.median(r['milliseconds']['after']for r in rows)}),flush=True)
