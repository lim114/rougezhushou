"""Read labelled elite emblems from the small recruited-card emblem region."""
from functools import lru_cache
from pathlib import Path
import cv2
import numpy as np

@lru_cache(maxsize=1)
def references():
    folder=Path(__file__).parent/'data/ui-icons'
    return {elite:cv2.imdecode(np.fromfile(folder/f'elite-{elite}-s.png',dtype=np.uint8),cv2.IMREAD_UNCHANGED)
            for elite in range(3)}

def card_elite(image,x,y,space=(1,1)):
    ux,uy=space
    h,w=image.shape[:2]
    scores=[]
    for elite,original in references().items():
        best=0
        for scale in np.arange(.034,.051,.002):
            size=round(h*scale*uy)
            template=cv2.resize(original,(size,size),interpolation=cv2.INTER_AREA)
            mask=((cv2.cvtColor(template[:,:,:3],cv2.COLOR_BGR2GRAY)>150)&(template[:,:,3]>150)).astype(np.uint8)
            if np.count_nonzero(mask)<10:continue
            for dx in (-.003,0,.003):
                for dy in (-.003,0,.003):
                    cx=round((x+.016*ux+dx*ux)*w);cy=round((y-.052*uy+dy*uy)*h)
                    roi=image[cy-size//2:cy-size//2+size,cx-size//2:cx-size//2+size]
                    if roi.shape[:2]!=(size,size):continue
                    actual=(cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)>180).astype(np.uint8)
                    # Compare the entire silhouette: elite 1's blades are a subset of elite 2's.
                    denominator=float(np.sum(actual)+np.sum(mask))
                    score=2*float(np.sum(actual&mask))/denominator if denominator else 0
                    best=max(best,score)
        scores.append((best,elite))
    scores.sort(reverse=True)
    if scores[0][0]<.70 or scores[0][0]-scores[1][0]<.085:return None
    return {'value':scores[0][1],'score':scores[0][0],'margin':scores[0][0]-scores[1][0]}
