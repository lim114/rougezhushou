"""Extract reference artwork from the existing authorized replay fixtures."""
import hashlib,json,sys
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from rouge.operator_recognition import identity_index,normalized_name
folder=ROOT/'rouge/data/visual-anchors';folder.mkdir(exist_ok=True);entries=[];sources={}
for file in ['operator-mechanist','operator-silverash','operator-kaltsit']:
    png=ROOT/f'samples/native-client/{file}.png';ocr=png.with_name(file+'-ocr.json')
    image=cv2.imdecode(np.fromfile(png,np.uint8),1);h,w=image.shape[:2]
    texts=json.loads(ocr.read_text(encoding='utf8'))['texts']
    for p in [png,ocr]:sources[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    for text in texts:
        ids=identity_index().get(normalized_name(text['text']),set())
        if len(ids)!=1:continue
        box=text['box'];x0=max(0,round(min(p[0] for p in box)*w)-6);x1=min(w,round(max(p[0] for p in box)*w)+6)
        y0=max(0,round(min(p[1] for p in box)*h)-6);y1=min(h,round(max(p[1] for p in box)*h)+6)
        cv2.imencode('.png',image[y0:y1,x0:x1])[1].tofile(folder/(file+'-name.png'))
        entries.append({'kind':'identity','id':next(iter(ids)),'file':file+'-name.png'});break
    x0,y0,x1,y1=1450,210,2048,1000
    anchor=next(t for t in texts if t['text']=='潜能')
    filename='training-panel.png' if file=='operator-mechanist' else file+'-training.png'
    cv2.imencode('.png',image[y0:y1,x0:x1])[1].tofile(folder/filename)
    entries.append({'kind':'training','file':filename,'potential_box':[[p[0]*w-x0,p[1]*h-y0] for p in anchor['box']]})
png=ROOT/'samples/native-client/run-map-closed.png';image=cv2.imdecode(np.fromfile(png,np.uint8),1)
texts=json.loads(png.with_name('run-map-closed-ocr.json').read_text(encoding='utf8'))['texts']
anchor=next(t for t in texts if t['text']=='收藏品');y0=1010
cv2.imencode('.png',image[y0:])[1].tofile(folder/'held-footer.png')
entries.append({'kind':'footer','file':'held-footer.png','held_box':[[p[0]*image.shape[1],p[1]*image.shape[0]-y0] for p in anchor['box']]})
sources[str(png.relative_to(ROOT))]=hashlib.sha256(png.read_bytes()).hexdigest()
(folder/'manifest.json').write_text(json.dumps({'source':'Existing authorized native-client replays; OCR boxes used offline only.',
    'source_hashes':sources,'entries':entries},ensure_ascii=False,indent=2),encoding='utf8')
