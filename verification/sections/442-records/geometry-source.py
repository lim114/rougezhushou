from pathlib import Path
import sys,json,cv2,numpy as np
R=Path.cwd();sys.path.insert(0,str(R))
from rouge.recognition import ScreenReader
out=R/'verification/sections/442-capacity-geometry-attempt2';out.mkdir(parents=True,exist_ok=False)
local=R/'.cache/capacity-geometry-private-442-attempt2';local.mkdir(exist_ok=False)
reader=ScreenReader();rows=[];private_details=[];private_case=json.loads((R/'.cache/hud-private-validation-input.json').read_bytes())
for public in(True,False):
    path=R/'.cache/vlm-public-reference-frames/60.png'if public else R/private_case['image_path']
    im=cv2.imdecode(np.frombuffer(path.read_bytes(),np.uint8),1)
    expected={'life':6,'shield':1,'command':1,'hope':7}if public else private_case['expected']
    variants=[('original',im),('scale065',cv2.resize(im,None,fx=.65,fy=.65)),('scale080',cv2.resize(im,None,fx=.8,fy=.8)),('scale125',cv2.resize(im,None,fx=1.25,fy=1.25)),('translated_padded',cv2.copyMakeBorder(im,31,47,29,51,cv2.BORDER_CONSTANT))]
    for kind,image in variants:
        v=reader.read(image);resources=(v.get('run')or{}).get('resources',{});checks={k:resources.get(k,{}).get('value')==x for k,x in expected.items()}
        row={'case':len(rows)+1,'public_reference':public,'variant':kind,'manually_checked_fields_equal':checks,'all_expected_equal':all(checks.values()),'life_capacity_correct':resources.get('life',{}).get('capacity')==(6 if public else private_case['life_capacity']),'hope_capacity_correct':resources.get('hope',{}).get('capacity')==(13 if public else private_case['hope_capacity']),'total_ms':v['performance']['total_ms']}
        rows.append(row)
        if not public:private_details.append({'variant':kind,'expected':expected,'actual':resources})
        print(json.dumps(row),flush=True)
        (out/'progress.json').write_text(json.dumps({'cases':rows},indent=2)+'\n','utf8')
(local/'actual-private-values.json').write_text(json.dumps(private_details,ensure_ascii=False,indent=2)+'\n','utf8')
result={'passed':all(r['all_expected_equal']and r['life_capacity_correct']and r['hope_capacity_correct']for r in rows),'cases':rows,'scope':'Geometric derivatives of one public video image and one manually reviewed existing local development image; not independent game sessions or arbitrary layout coverage. Private image/numeric values/identities/hashes remain local.'}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps({'passed':result['passed'],'cases':len(rows)}),flush=True)
raise SystemExit(0 if result['passed']else 1)
