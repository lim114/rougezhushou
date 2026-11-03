"""Read the emergency-hire marker independently of portrait and elite emblem."""
from functools import lru_cache
from pathlib import Path
import cv2
import numpy as np

@lru_cache(maxsize=2)
def reference(kind):
    image=cv2.imdecode(np.fromfile(Path(__file__).parent/f'data/ui-icons/{kind}-marker.png',dtype=np.uint8),1)
    return cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

def promotion_marker(image,x,y,space=(1,1)):
    ux,uy=space
    h,w=image.shape[:2]
    x0=max(0,round((x-.038*ux)*w));x1=min(w,round((x+.005*ux)*w))
    y0=max(0,round((y-.073*uy)*h));y1=min(h,round((y-.018*uy)*h))
    crop=image[y0:y1,x0:x1]
    if not crop.size:return None
    gray=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
    best=None
    for scale in (.038,.041,.044,.047):
        size=round(h*scale*uy)
        if size>min(gray.shape):continue
        scores=cv2.matchTemplate(gray,cv2.resize(reference('advanced'),(size,size)),cv2.TM_CCOEFF_NORMED)
        _,score,_,location=cv2.minMaxLoc(scores)
        if best is None or score>best[0]:best=(float(score),location,size)
    if best is None or best[0]<.65:return None
    score,(dx,dy),size=best
    roi=crop[dy:dy+size,dx:dx+size]
    hsv=cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    gold=float(np.count_nonzero(cv2.inRange(hsv,np.array([10,130,140]),np.array([40,255,255]))))/hsv.shape[0]/hsv.shape[1]
    if gold>=.15:return {'advanced':True,'score':score,'gold_fraction':gold,'source':'已进阶金色标记'}
    if gold<=.02:return {'advanced':False,'score':score,'gold_fraction':gold,'source':'未点亮的进阶标记'}
    return None


def recruitment_marker(image,x,y,space=(1,1)):
    """Emergency is the person-and-clock silhouette beside the level, not the gold diamond."""
    ux,uy=space
    h,w=image.shape[:2];best=0;minimum_white=None
    for scale in (.042,.045,.048):
        height=round(h*scale*uy);width=round(height*49/51)
        mask=cv2.resize(reference('emergency'),(width,height))>210
        expected=float(np.sum(mask))
        for dx in (-.002,0,.002):
            for dy in (-.002,0,.002):
                cx=round((x-.023*ux+dx*ux)*w);cy=round((y-.002*uy+dy*uy)*h)
                roi=image[cy-height//2:cy-height//2+height,cx-width//2:cx-width//2+width]
                if roi.shape[:2]!=(height,width):continue
                actual=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)>210
                white=float(np.sum(actual));denominator=expected+white
                score=2*float(np.sum(actual&mask))/denominator if denominator else 0
                best=max(best,score)
                minimum_white=white/expected if minimum_white is None else min(minimum_white,white/expected)
    if best>=.70:return {'kind':'emergency_hire','score':best,'version':2,'source':'等级左侧人形与时钟应急标识'}
    if minimum_white is not None and minimum_white<.05:
        return {'kind':'non_emergency','score':best,'version':2,'source':'等级左侧区域未显示应急人形/时钟标识'}
    return None
