"""Reference from our verified empty-count native capture, not an OCR guess."""
import cv2,numpy as np,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'samples/native-client/run-map-empty.png'
image=cv2.imdecode(np.fromfile(source,dtype=np.uint8),1)
# Operator-independent glyph bounds checked against the full native image.
crop=image[1037:1077,225:265]
mask=cv2.threshold(cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY),205,255,cv2.THRESH_BINARY)[1]
count,labels,stats,_=cv2.connectedComponentsWithStats(mask)
components=[(i,s) for i,s in enumerate(stats[1:],1) if s[4]>=30]
assert len(components)==1
_,(x,y,w,h,area)=components[0]
glyph=mask[y:y+h,x:x+w]
path=ROOT/'rouge/data/ui-icons/collection-counter-zero.png'
cv2.imencode('.png',glyph)[1].tofile(path)
receipt={'source':'project native background capture; zero manually checked on full frame',
         'sample':str(source.relative_to(ROOT)), 'sample_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'crop':[225,1037,265,1077],'glyph_size':[int(w),int(h)],'threshold':205,
         'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(ROOT/'rouge/data/counter-reference.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(receipt['glyph_size'])
