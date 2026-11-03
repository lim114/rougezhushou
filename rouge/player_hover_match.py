"""Cursor-local masked artwork matching; scores are not recognition probabilities."""
import time
import numpy as np
import cv2
from . import relic_recognition as icons

def _locate(image,point,*,cancelled=lambda:False,difficulty=None):
    if image is None or image.ndim!=3 or image.shape[2]!=3:return None
    h,w=image.shape[:2];x,y=point
    if not 0<=x<w or not 0<=y<h:return None
    radius=max(32,round(h*.15));x0=max(0,int(x-radius));y0=max(0,int(y-radius));x1=min(w,int(x+radius+1));y1=min(h,int(y+radius+1))
    roi=np.ascontiguousarray(image[y0:y1,x0:x1]);px,py=x-x0,y-y0
    if not roi.size or not np.any(roi):return None
    pixels=roi.astype(np.float32);energy_image=np.sum(pixels*pixels,axis=2)
    energy=icons.EnergyScreen(pixels);projection=icons.ProjectionScreen(pixels,energy);candidates={};near={}
    def verify(rid,template,mask):
        th,tw=template.shape[:2]
        if th>roi.shape[0] or tw>roi.shape[1]:return
        values=cv2.matchTemplate(roi,template,cv2.TM_SQDIFF_NORMED,mask=mask)
        # Allow a bounded visual halo around the icon, scaled from its size.
        # A custom game cursor can visually overlap an icon while its OS hotspot is just outside.
        pad=max(2,min(round(h*.02),round(max(tw,th)*.25)))
        left=max(0,int(np.floor(px-tw-pad+1)));right=min(values.shape[1],int(np.floor(px+pad))+1)
        top=max(0,int(np.floor(py-th-pad+1)));bottom=min(values.shape[0],int(np.floor(py+pad))+1)
        if left>=right or top>=bottom:return
        local=np.nan_to_num(values[top:bottom,left:right],nan=10,posinf=10,neginf=10)
        minimum,_,where,_=cv2.minMaxLoc(local);score=1-float(minimum)
        if score<.88:return
        prior=candidates.get(rid)
        record={'id':rid,'score':score,'bounds':(x0+left+where[0],y0+top+where[1],tw,th)}
        if prior is None or score>prior['score']:candidates[rid]=record
        near.setdefault(rid,set()).add(max(tw,th))
    for virtual_height in sorted({max(32,round(h*factor))for factor in(.60,1.,1.60)}):
        for rid,template,mask,screen_template,screen_mask,norm,*projected in icons.prepared_templates(virtual_height):
            if cancelled():return None
            th,tw=template.shape[:2]
            if th>roi.shape[0]or tw>roi.shape[1]:continue
            if not energy.possible((th,tw),norm)or not projection.possible(screen_template,screen_mask,norm,*projected):continue
            if not icons._can_match(pixels,energy_image,screen_template,screen_mask,norm):continue
            verify(rid,template,mask)
    # Refine only plausible identities, with the same mask/colour verifier.
    for rid,sizes in list(near.items()):
        for size in sorted({s+delta for s in sizes for delta in range(-max(1,round(h*.006)),max(1,round(h*.006))+1)if s+delta>0}):
            if cancelled():return None
            prepared=icons._refined_template(rid,size)
            if prepared is not None:verify(rid,*prepared)
    ordered=sorted(candidates.values(),key=lambda r:r['score'],reverse=True)
    if not ordered or ordered[0]['score']<.94:return None
    best=dict(ordered[0]);eligible=[r['id']for r in ordered if best['score']-r['score']<.025]
    eligible=sorted({other for rid in eligible for other in icons.artwork_families().get(rid,[rid])})
    best.update(art_id=best['id'],candidates=eligible,confirmed=len(eligible)==1,source='cursor_local_artwork')
    best=icons.resolve_difficulty_icons([best],difficulty)[0]
    return best

def verify_again(image,point,seed,*,difficulty=None,cancelled=lambda:False):
    """Verify the retrieved identities on fresh ORIGINAL-resolution pixels."""
    if cancelled():return None
    x,y,w,h=seed['bounds'];height,width=image.shape[:2]
    margin=max(6,round(max(w,h)*.10));x0=max(0,x-margin);y0=max(0,y-margin);x1=min(width,x+w+margin);y1=min(height,y+h+margin)
    roi=np.ascontiguousarray(image[y0:y1,x0:x1]);px,py=point[0]-x0,point[1]-y0
    scores={};ids=set(seed.get('candidates',[]))|{seed.get('art_id',seed['id'])}
    for rid in ids:
        for size in range(max(4,max(w,h)-margin),max(w,h)+margin+1):
            if cancelled():return None
            refined=icons._refined_template(rid,size)
            if refined is None:continue
            template,mask=refined;th,tw=template.shape[:2]
            if th>roi.shape[0]or tw>roi.shape[1]:continue
            values=cv2.matchTemplate(roi,template,cv2.TM_SQDIFF_NORMED,mask=mask)
            pad=max(2,min(round(height*.02),round(max(tw,th)*.25)))
            left=max(0,int(np.floor(px-tw-pad+1)));right=min(values.shape[1],int(np.floor(px+pad))+1)
            top=max(0,int(np.floor(py-th-pad+1)));bottom=min(values.shape[0],int(np.floor(py+pad))+1)
            if left>=right or top>=bottom:continue
            minimum,_,where,_=cv2.minMaxLoc(np.nan_to_num(values[top:bottom,left:right],nan=10,posinf=10,neginf=10));score=1-float(minimum)
            if rid not in scores or score>scores[rid]['score']:scores[rid]={'id':rid,'art_id':rid,'score':score,'bounds':(x0+left+where[0],y0+top+where[1],tw,th)}
    ordered=sorted(scores.values(),key=lambda r:r['score'],reverse=True)
    if not ordered or ordered[0]['score']<.94:return None
    best=ordered[0];candidates=[r['id']for r in ordered if best['score']-r['score']<.025]
    candidates=sorted({other for rid in candidates for other in icons.artwork_families().get(rid,[rid])})
    best.update(candidates=candidates,confirmed=len(candidates)==1,source='cursor_local_original_pixels')
    best=icons.resolve_difficulty_icons([best],difficulty)[0]
    return best if best.get('confirmed')else None

def hover_item(image,point,*,cancelled=lambda:False,difficulty=None):
    if image is None or image.ndim!=3 or image.shape[2]!=3:return None
    height,width=image.shape[:2];ratio=min(1.,240/height)
    small=cv2.resize(image,(max(1,round(width*ratio)),max(1,round(height*ratio))),interpolation=cv2.INTER_AREA)if ratio<1 else image
    seed=_locate(small,(point[0]*ratio,point[1]*ratio),cancelled=cancelled,difficulty=difficulty)
    if seed is None:return None
    seed['bounds']=tuple(round(value/ratio)for value in seed['bounds'])
    return verify_again(image,point,seed,difficulty=difficulty,cancelled=cancelled)


def client_image(frame,request,*,now=None,max_age=2.):
    """Physical client coordinates must describe this exact window frame."""
    if not isinstance(frame,dict):return None
    now=time.time()if now is None else now;stamp=frame.get('captured_at')
    if type(stamp)not in(int,float)or not 0<=now-stamp<=max_age:return None
    target=frame.get('target')or{}
    if (target.get('hwnd'),target.get('pid'))!=tuple(request['key']):return None
    image=frame.get('image');rect=frame.get('client_rect')
    if image is None or rect is None or len(rect)!=4:return None
    x0,y0,x1,y1=rect;h,w=image.shape[:2]
    if any(type(v)is not int for v in rect)or not 0<=x0<x1<=w or not 0<=y0<y1<=h:return None
    if (x1-x0,y1-y0)!=tuple(request['physical_client'][2:]):return None
    return image[y0:y1,x0:x1]
