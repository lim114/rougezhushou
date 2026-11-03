from pathlib import Path
from types import ModuleType
from copy import deepcopy
from hashlib import sha256
import sys,json,time
import cv2
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from rouge.recognition import ScreenReader
old=ModuleType('rouge.before_page_features');old.__file__=str(R/'rouge/page_features.py');old.__package__='rouge'
exec(compile((R/'research/page-feature-vector-review-20261031/before-page_features.py').read_bytes(),'<baseline-page-features>','exec'),old.__dict__)
out=R/'verification/maintenance/page-feature-vector-review-20261031/pipeline';out.mkdir(parents=True,exist_ok=False)
readers={'before':ScreenReader(),'after':ScreenReader()};readers['before']._page_router=old.PageFeatureRouter()
rows=[]
for index,path in enumerate(sorted((R/'samples/native-client').glob('*.png'))):
    image=cv2.imdecode(np.fromfile(path,dtype=np.uint8),cv2.IMREAD_COLOR);values={};row={'case':index+1,'milliseconds':{},'strategy':{}}
    for name in ('before','after')if index%2==0 else('after','before'):
        cv2.setRNGSeed(17);value=readers[name].read(image)
        row['milliseconds'][name]=value['performance']['total_ms'];row['strategy'][name]=value['performance']['routing']['strategy']
        value=deepcopy(value);value.pop('observed_at',None);value.pop('performance',None);values[name]=value
    row['entire_interpreted_result_equal']=values['before']==values['after'];assert row['entire_interpreted_result_equal'],{'case':index+1}
    rows.append(row);print(json.dumps({'completed_pairs':len(rows)}),flush=True)
result={'passed':True,'rows':rows,'source_sha256':sha256((R/'rouge/page_features.py').read_bytes()).hexdigest(),
    'scope':'All outputs compared in RAM. Existing local development images; no pixels, actual interpreted values, sample identities or pixel hashes persisted. No game, runtime state, network or chat calls.',
    'not_independent_accuracy_or_fps':True,'startup_and_order_bias_not_general_speedup':True}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
print(json.dumps({'passed':True,'pairs':len(rows)}),flush=True)
