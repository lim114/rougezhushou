from pathlib import Path
from hashlib import sha256
from types import ModuleType
from copy import deepcopy
import sys,json,time,cv2,numpy as np
R=Path.cwd();sys.path.insert(0,str(R))
from rouge.recognition import ScreenReader
from rouge import player_shop_hover as current,expansion_reference
out=R/'verification/sections/443-public-images';out.mkdir(parents=True,exist_ok=False)
old=ModuleType('rouge._shop_before443');old.__package__='rouge';old.__file__=str(R/'rouge/player_shop_hover.py')
exec(compile((R/'research/shop-price-443/before-player_shop_hover.py').read_bytes(),'<before-shop443>','exec'),old.__dict__)
reader=ScreenReader();cases=[]
for second in (148,158,164):
    file=R/'.cache/video414'/f'{second}.png';im=cv2.imdecode(np.fromfile(file,np.uint8),1)
    variants=[('original',im)]if second==148 else [('original',im),('scale065',cv2.resize(im,None,fx=.65,fy=.65)),('scale137_padded',cv2.copyMakeBorder(cv2.resize(im,None,fx=1.37,fy=1.37),17,29,31,43,cv2.BORDER_CONSTANT))]
    for name,image in variants:
        result=reader.read(image);snapshot=(result.get('run')or{}).get('shop');prices={row['name']:row.get('price')for row in(snapshot or{}).get('items',[])}
        expected={'浪花':6 if second==164 else None,'悲伤的红':12,'“老妈的鼓励”':12,'伪翅':None}
        correct=snapshot is None if second==148 else prices==expected and result['page']=='shop'
        cases.append({'public_reference_seconds':second,'variant':name,'page':result['page'],'prices':prices,'expected_visible_prices_match':correct,'total_ms':result['performance']['total_ms']})
        print(json.dumps(cases[-1],ensure_ascii=False),flush=True)
baseline=[]
for second in (158,164):
    frame=json.loads((R/f'research/shop-price-443/public-{second}-ocr.json').read_bytes())
    baseline.append({'public_reference_seconds':second,'old_page_is_shop':old.shop_target(frame['raw'],current.name_catalog(expansion_reference.packet()),(-1,-1),frame['shape'])[1]})
result={'passed':all(c['expected_visible_prices_match']for c in cases),'cases':cases,'baseline_old_gate':baseline,'public_originals_sha256':{str(s):sha256((R/'.cache/video414'/f'{s}.png').read_bytes()).hexdigest()for s in(148,158,164)},'scope':'Actual complete ScreenReader pipeline and existing OCR on public video frames/derivatives. Seven derived cases are not independent real game sessions or a throughput/FPS benchmark.'}
(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');(out/'source.py').write_bytes(Path(__file__).read_bytes())
raise SystemExit(0 if result['passed']else 1)
