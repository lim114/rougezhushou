from pathlib import Path
from types import ModuleType
from hashlib import sha256
import sys,json
import cv2,numpy as np
R=Path.cwd();sys.path.insert(0,str(R));from rouge.page_features import _scene_features
old=ModuleType('rouge.before_page_features');old.__file__=str(R/'rouge/page_features.py');old.__package__='rouge'
exec(compile((R/'research/page-feature-vector-review-20261031/before-page_features.py').read_bytes(),'<baseline-page-features>','exec'),old.__dict__)
rows=[]
for p in sorted((R/'samples/native-client').glob('*.png')):
    im=cv2.imdecode(np.fromfile(p,dtype=np.uint8),cv2.IMREAD_GRAYSCALE);scale=min(1.,1100/max(im.shape));im=cv2.resize(im,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)if scale!=1 else im
    for variant,image in enumerate((im,cv2.resize(im,None,fx=.8,fy=.8),np.pad(im,((31,47),(29,51))))):
        a=old._scene_features(image);b=_scene_features(image)
        same=all((x is None and y is None)or(isinstance(x,np.ndarray)and isinstance(y,np.ndarray)and x.shape==y.shape and x.dtype==y.dtype and np.array_equal(x,y))for x,y in zip(a,b));assert same
        rows.append({'case':len(rows)+1,'variant':variant,'entire_points_and_descriptors_equal':same})
out=R/'verification/maintenance/page-feature-vector-review-20261031/final-feature-parity.json';out.write_text(json.dumps({'passed':True,'cases':rows,'source_sha256':sha256((R/'rouge/page_features.py').read_bytes()).hexdigest(),'no_sample_pixels_text_paths_or_pixel_hashes_persisted':True},indent=2)+'\n','utf8');print(json.dumps({'passed':True,'cases':len(rows)}))
