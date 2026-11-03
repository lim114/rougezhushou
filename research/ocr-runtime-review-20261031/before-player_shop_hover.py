"""Shop names first: infer the current card grid from text, not fixed coordinates."""
import unicodedata
import time
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
    """Bind the exact name to its own price text; unread cards remain unknown.

    Positions come from this frame. Font-relative limits admit the observed
    card layout conservatively; they do not infer missing rows or columns.
    """
    height,width=shape[:2];records=[]
    for box,text,score in raw or[]:
        if float(score)<.85:continue
        xs=[float(p[0])for p in box];ys=[float(p[1])for p in box]
        if not np.isfinite(xs+ys).all():continue
        bounds=(min(xs),min(ys),max(xs),max(ys))
        if bounds[2]<=bounds[0] or bounds[3]<=bounds[1]:continue
        records.append({'text':canonical(text),'score':float(score),'bounds':bounds})
    words=[r['text']for r in records]
    is_shop=any('购买'in s for s in words)and any(any(w in s for w in('当前余额','前瞻性投资','刷新'))for s in words)
    if not is_shop:return None,False
    headers=[{**r,'ids':names[r['text']]}for r in records if r['score']>=.9 and r['text']in names]
    # Pointer over an exact name needs no inferred card extent at all.
    x,y=point
    covered=[r for r in headers if r['bounds'][0]<=x<r['bounds'][2]and r['bounds'][1]<=y<r['bounds'][3]]
    if len(covered)==1 and len(set(covered[0]['ids']))==1:
        selected=covered[0];identity=next(iter(set(selected['ids'])));left,top,right,bottom=selected['bounds']
        return {'id':identity,'name':selected['text'],'confirmed':True,'candidates':[identity],
            'name_bounds':tuple(round(v)for v in selected['bounds']),'price_label_bounds':None,
            'bounds':(round(left),round(top),round(right-left),round(bottom-top)),
            'source':'shop_exact_name_and_current_grid','card_evidence':'cursor_on_exact_name_text'},True
    prices=[r for r in records if r['text']=='价格']
    matches=[];x,y=point;pairs_by_header=[];measured=[]
    for header in headers:
        left,top,right,bottom=header['bounds'];font=max(4.,bottom-top);pairs=[]
        for price in prices:
            px,py,pu,pv=price['bounds'];dx,dy=px-left,py-top
            if font*2<=dx<=font*9 and font*2<=dy<=font*9 and .5<=dx/dy<=2:pairs.append(price)
        pairs_by_header.append(pairs)
        if len(pairs)==1:
            px,py,pu,pv=pairs[0]['bounds'];measured.append(((px-left)/font,(py-top)/font,(pu-px)/font,(pv-py)/font))
    layout=None
    if len(measured)>=2:
        values=np.asarray(measured);center=np.median(values,axis=0)
        if np.max(np.ptp(values[:,:2],axis=0))<=1.5:layout=center
    for header,pairs in zip(headers,pairs_by_header):
        left,top,right,bottom=header['bounds'];font=max(4.,bottom-top);pad=font*.65
        if len(pairs)==1:
            price=pairs[0];px,py,pu,pv=price['bounds'];evidence='exact_name_and_own_price_text'
        elif not pairs and layout is not None:
            dx,dy,pw,ph=layout;px=left+dx*font;py=top+dy*font;pu=px+pw*font;pv=py+ph*font
            # A cursor can cover one price label. Reuse a size measured on
            # multiple current cards only with BOTH current row/column anchors.
            columns=[r for r in prices if abs(r['bounds'][0]-px)<=font*.75]
            rows=[r for r in prices if abs(r['bounds'][1]-py)<=font*.75]
            if not columns or not rows:continue
            pu=min(r['bounds'][2]for r in columns);pv=min(r['bounds'][3]for r in rows)
            price=None;evidence='exact_name_and_current_text_layout'
        else:continue
        # Stay inside the actual name-to-price text span. Never extrapolate
        # padding to a missing neighbour or invent the rest of a card.
        bounds=(max(0.,left),max(0.,top),min(float(width),max(right,pu)),min(float(height),pv))
        # A neighbouring header is a hard edge, never a substitute identity.
        for other in headers:
            if other is header:continue
            ox,oy,ou,ov=other['bounds']
            if abs(oy-top)<=font and ox>left:bounds=(bounds[0],bounds[1],min(bounds[2],ox),bounds[3])
            if abs(ox-left)<=font and oy>top:bounds=(bounds[0],bounds[1],bounds[2],min(bounds[3],oy))
        if bounds[0]<=x<bounds[2] and bounds[1]<=y<bounds[3]:matches.append((header,price,bounds,evidence))
    if len(matches)!=1:return None,True
    selected,price,bounds,evidence=matches[0];identities=set(selected['ids'])
    if len(identities)!=1:return None,True
    identity=next(iter(identities));x0,y0,x1,y1=selected['bounds'];left,top,right,bottom=bounds
    return {'id':identity,'name':selected['text'],'confirmed':True,'candidates':[identity],
            'name_bounds':tuple(round(v)for v in(x0,y0,x1,y1)),
            'price_label_bounds':tuple(round(v)for v in price['bounds'])if price is not None else None,
            'bounds':(round(left),round(top),round(right-left),round(bottom-top)),
            # Keep the existing reader/verification route identifier compatible.
            'source':'shop_exact_name_and_current_grid','card_evidence':evidence},True

class ShopNameReader:
    def __init__(self,engine=None):self.engine=engine;self.is_shop=False;self.cached=None
    def ocr(self,image):
        if self.engine is None:
            from rapidocr_onnxruntime import RapidOCR
            self.engine=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
        raw,_=self.engine(image,use_cls=False);return raw or[]
    def identify(self,image,point):
        packet=expansion_reference.packet()
        if packet is None:self.is_shop=False;return None
        names=name_catalog(packet);now=time.monotonic();cached=self.cached
        if cached and now-cached['at']<30 and cached['shape']==image.shape and all(sha256(image[y:v,x:u].tobytes()).digest()==digest for x,y,u,v,digest in cached['patches']):
            raw=cached['raw']
        else:
            raw=self.ocr(image);self.cached=None
            _,shop=shop_target(raw,names,point,image.shape)
            if shop:
                patches=[];h,w=image.shape[:2]
                for box,label,score in raw:
                    label=canonical(label)
                    if score<.85 or not(label in names or any(k in label for k in ('购买','当前余额','前瞻性投资','刷新','编队','价格'))):continue
                    x=max(0,int(min(p[0]for p in box))-2);y=max(0,int(min(p[1]for p in box))-2);u=min(w,int(max(p[0]for p in box))+2);v=min(h,int(max(p[1]for p in box))+2)
                    if x<u and y<v:patches.append((x,y,u,v,sha256(image[y:v,x:u].tobytes()).digest()))
                if patches:self.cached={'at':now,'shape':image.shape,'raw':raw,'patches':patches}
        item,self.is_shop=shop_target(raw,names,point,image.shape)
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
    def snapshot(self,image):
        cached=self.cached
        if not cached or time.monotonic()-cached['at']>=30 or cached['shape']!=image.shape:return None
        if not all(sha256(image[y:v,x:u].tobytes()).digest()==digest for x,y,u,v,digest in cached['patches']):return None
        packet=expansion_reference.packet()
        if packet is None:return None
        names=name_catalog(packet);items={}
        for box,name,score in cached['raw']:
            identities=names.get(canonical(name),[])
            if score>=.9 and len(identities)==1:
                identity=identities[0];items[identity]={'id':identity,'name':packet['current']['details']['items'][identity]['name']}
        return {'items':list(items.values()),'complete':False,'source':'fresh_shop_exact_names'}if items else None
