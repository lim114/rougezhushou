"""Identify resource labels/icons before accepting any numeric counter."""
from functools import lru_cache
from pathlib import Path
import re
import cv2
import numpy as np
from .operator_recognition import center
from .anchors import units

@lru_cache(maxsize=1)
def gold_template():
    return cv2.imdecode(np.fromfile(Path(__file__).with_name('data')/'ui-icons/gold-counter.png',dtype=np.uint8),cv2.IMREAD_GRAYSCALE)

def read_resources(image,texts,engine=None):
    h,w=image.shape[:2];resources={}
    if engine is not None:
        from .hud_resources import read_hud_resources
        resources.update(read_hud_resources(image,texts,engine))
    parts=next((t for t in texts if t['text']=='零件箱' and t['confidence']>=.9),None)
    if parts:
        x,y=center(parts);ux,uy=units(image,parts,29)
        ratios={tuple(map(int,m.groups())) for t in texts if t['confidence']>=.9 and
            (m:=re.fullmatch(r'(\d{1,3})/(\d{1,3})',t['text'])) and
            abs((position:=center(t))[0]-x)<.04*ux and 0<position[1]-y<.055*uy}
        if len(ratios)==1:
            count,capacity=next(iter(ratios))
            if count<=capacity:
                resources['parts_count']={'value':count,'capacity':capacity,'source':'零件箱数量/容量，取左值'}
    # Reject the appraisal number, hope and action-points counters even if OCR is confident.
    anchor=next((t for t in texts if t['text']=='目标生命值' and t['confidence']>=.9),None)
    if anchor is None:return resources
    numbers=[(int(t['text']),*center(t)) for t in texts if t['confidence']>=.95 and re.fullmatch(r'\d{1,4}',t['text'])]
    if not numbers:return resources
    ux,uy=units(image,anchor,27.9678)
    template=gold_template();gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    matches=[]
    icon_scale=h*uy/1127
    scales=(icon_scale*.85,icon_scale,icon_scale*1.15)
    templates=[cv2.resize(template,None,fx=scale,fy=scale) for scale in scales]
    for _,nx,ny in numbers:
        x0=max(0,round((nx-.18*ux)*w));x1=min(w,round((nx-.02*ux)*w))
        y0=max(0,round((ny-.05*uy)*h));y1=min(h,round((ny+.05*uy)*h))
        roi=gray[y0:y1,x0:x1]
        if not roi.size:continue
        for ref in templates:
            if ref.shape[0]>roi.shape[0] or ref.shape[1]>roi.shape[1]:continue
            score=cv2.matchTemplate(roi,ref,cv2.TM_CCOEFF_NORMED)
            _,best,_,point=cv2.minMaxLoc(score)
            if best>=.91:matches.append((best,(x0+point[0]+ref.shape[1]/2)/w,(y0+point[1]+ref.shape[0]/2)/h))
    if matches:
        score,x,y=max(matches)
        values={value for value,nx,ny in numbers if
            .035*ux<nx-x<.13*ux and abs(ny-y)<.027*uy}
        if len(values)==1:resources['gold']={'value':next(iter(values)),'source':'源石锭三角图标右侧数量','icon_score':float(score)}
    return resources
