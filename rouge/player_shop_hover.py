"""Shop names first: infer the current card grid from text, not fixed coordinates."""
import unicodedata
from hashlib import sha256
import numpy as np
from . import expansion_reference

def canonical(value):
    text=unicodedata.normalize('NFKC',str(value))
    for char in '“”‘’\"\'':text=text.replace(char,'')
    for char in '－—–−':text=text.replace(char,'-')
    return ''.join(text.split())

def name_catalog(packet):
    result={}
    for identity,item in packet['current']['details']['items'].items():
        name=canonical(item.get('name',''))
        if name:result.setdefault(name,[]).append(identity)
    return result

def shop_target(raw,names,point,shape):
    """A unique name on the inferred card is evidence; a nearby name alone is not."""
    height,width=shape[:2];records=[]
    for box,text,score in raw or[]:
        if float(score)<.85:continue
        xs=[float(p[0])for p in box];ys=[float(p[1])for p in box]
        records.append({'text':canonical(text),'score':float(score),'bounds':(min(xs),min(ys),max(xs),max(ys))})
    words=[r['text']for r in records]
    is_shop=any('购买'in s for s in words)and any(any(w in s for w in('当前余额','前瞻性投资','刷新'))for s in words)
    if not is_shop:return None,False
    headers=[{**r,'ids':names[r['text']]}for r in records if r['score']>=.9 and r['text']in names]
    if len(headers)<2:return None,True
    font=max(4.,float(np.median([r['bounds'][3]-r['bounds'][1]for r in headers])))
    columns=[]
    for row in sorted(headers,key=lambda r:r['bounds'][0]):
        left=row['bounds'][0]
        if not columns or left-columns[-1][-1]>font*1.5:columns.append([left])
        else:columns[-1].append(left)
    xs=[float(np.median(c))for c in columns]
    if len(xs)<2:return None,True
    gaps=np.diff(xs);pitch=float(np.median(gaps))
    if pitch<font*3 or max(gaps)>pitch*1.6 or min(gaps)<pitch*.6:return None,True
    rows=[]
    for header in sorted(headers,key=lambda r:r['bounds'][1]):
        top=header['bounds'][1]
        if not rows or top-rows[-1][-1]>font*.9:rows.append([top])
        else:rows[-1].append(top)
    ys=[float(np.median(r))for r in rows];x,y=point;pad=font*.65
    footer=min((r['bounds'][1]for r in records if r['text']in('收藏品','干员','编队','零件箱')and r['bounds'][1]>ys[-1]+font*2),default=float(height))
    col=next((i for i,left in enumerate(xs)if left-pad<=x<(xs[i+1]-pad if i+1<len(xs)else left+pitch-pad)),None)
    row=next((i for i,top in enumerate(ys)if top-pad<=y<(ys[i+1]-pad if i+1<len(ys)else footer)),None)
    if col is None or row is None:return None,True
    matches=[r for r in headers if abs(r['bounds'][0]-xs[col])<=font*1.5 and abs(r['bounds'][1]-ys[row])<=font*.9]
    identities={identity for r in matches for identity in r['ids']}
    if len(identities)!=1 or not matches:return None,True
    selected=max(matches,key=lambda r:r['score']);identity=next(iter(identities));x0,y0,x1,y1=selected['bounds']
    return {'id':identity,'name':selected['text'],'confirmed':True,'candidates':[identity],
            'name_bounds':tuple(round(v)for v in(x0,y0,x1,y1)),
            'bounds':(round(xs[col]-pad),round(ys[row]-pad),round(pitch),round((ys[row+1]-pad if row+1<len(ys)else footer)-(ys[row]-pad))),
            'source':'shop_exact_name_and_current_grid'},True

class ShopNameReader:
    def __init__(self,engine=None):self.engine=engine;self.is_shop=False
    def ocr(self,image):
        if self.engine is None:
            from rapidocr_onnxruntime import RapidOCR
            self.engine=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
        raw,_=self.engine(image,use_cls=False);return raw or[]
    def identify(self,image,point):
        packet=expansion_reference.packet()
        if packet is None:self.is_shop=False;return None
        item,self.is_shop=shop_target(self.ocr(image),name_catalog(packet),point,image.shape)
        if item is not None:
            x0,y0,x1,y1=item['name_bounds'];item['name_pixels_sha256']=sha256(image[y0:y1,x0:x1].tobytes()).hexdigest()
        return item
    def verify(self,image,item):
        x0,y0,x1,y1=item['name_bounds'];height,width=image.shape[:2];pad=max(2,round((y1-y0)*.25))
        if not 0<=x0<x1<=width or not 0<=y0<y1<=height:return None
        # Exact unchanged name pixels retain the original high-confidence read.
        # No threshold reduction or approximate image matching is involved.
        if item.get('name_pixels_sha256')==sha256(image[y0:y1,x0:x1].tobytes()).hexdigest():return dict(item)
        crop=image[max(0,y0-pad):min(height,y1+pad),max(0,x0-pad):min(width,x1+pad)]
        if self.engine is None:self.ocr(crop)
        # This is already one detected text line; running detection again can
        # cut off a character at the crop edge. Read the whole line directly.
        lines,_=self.engine(crop,use_det=False,use_cls=False)
        exact=[r for r in lines or[]if len(r)==2 and float(r[1])>=.9 and canonical(r[0])==item['name']]
        return dict(item)if exact else None
