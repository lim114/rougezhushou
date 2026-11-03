from pathlib import Path
import sys, time, json, statistics, subprocess
import cv2
import numpy as np

R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from rouge.page_features import _scene_features

def candidate(gray):
    h,w=gray.shape
    feature_image=cv2.Canny(gray,18,48)
    orb=cv2.ORB_create(nfeatures=1000,scaleFactor=1.15,nlevels=8,
        edgeThreshold=5,patchSize=19,fastThreshold=5)
    points,descriptions=[],[]
    for top in range(0,h,190):
        for left in range(0,w,260):
            right,bottom=min(w,left+260),min(h,top+190)
            x0,y0,x1,y1=max(0,left-36),max(0,top-36),min(w,right+36),min(h,bottom+36)
            kps,desc=orb.detectAndCompute(feature_image[y0:y1,x0:x1],None)
            if desc is None:continue
            xy=cv2.KeyPoint_convert(kps).astype(np.float64)+(x0,y0)
            keep=(xy[:,0]>=left)&(xy[:,0]<right)&(xy[:,1]>=top)&(xy[:,1]<bottom)
            points.append(xy[keep]);descriptions.append(desc[keep])
    if not descriptions:return np.asarray([],np.float32),None
    points=np.concatenate(points).astype(np.float32)
    return points,(np.concatenate(descriptions)if len(points)else None)

def timed(fn,gray):
    start=time.perf_counter();out=fn(gray)
    return out,(time.perf_counter()-start)*1000

def equal(a,b):
    return all((x is None and y is None)or(isinstance(x,np.ndarray)and isinstance(y,np.ndarray)
        and x.shape==y.shape and x.dtype==y.dtype and np.array_equal(x,y))for x,y in zip(a,b))

out=R/'.cache/page-feature-vector-experiment';out.mkdir(exist_ok=False)
rows=[]
paths=sorted((R/'samples/native-client').glob('*.png'))
for i,path in enumerate(paths):
    image=cv2.imdecode(np.fromfile(path,dtype=np.uint8),cv2.IMREAD_GRAYSCALE)
    scale=min(1.,1100/max(image.shape));gray=cv2.resize(image,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)if scale!=1 else image
    samples=[gray,cv2.resize(gray,None,fx=.8,fy=.8),np.pad(gray,((31,47),(29,51)))]
    for j,current in enumerate(samples):
        before=[];after=[];same=True
        for run in range(4):
            order=(_scene_features,candidate)if run%2==0 else(candidate,_scene_features)
            values={}
            for fn in order:values[fn]=timed(fn,current)
            a,old_ms=values[_scene_features];b,new_ms=values[candidate];same &= equal(a,b)
            if run:before.append(old_ms);after.append(new_ms)
        row={'case':len(rows)+1,'variant':j,'features_equal':same,'before_ms':before,'after_ms':after,'point_count':len(a[0])}
        rows.append(row);assert same,{'case':row['case']}
    print(json.dumps({'completed_inputs':i+1,'cases':len(rows)}),flush=True)
result={'baseline':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip(),'input_count':len(paths),'cases':rows,
    'passed':all(x['features_equal']for x in rows),'before_median_ms':statistics.median(statistics.median(x['before_ms'])for x in rows),
    'after_median_ms':statistics.median(statistics.median(x['after_ms'])for x in rows),
    'scope':'local existing sample images; no pixels, text, file identities or pixel hashes persisted; feature equality is not recognition ground truth'}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
print(json.dumps({k:v for k,v in result.items()if k!='cases'}),flush=True)
