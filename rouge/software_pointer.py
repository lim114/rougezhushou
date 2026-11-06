"""Locate a game-rendered pointer, including one frozen under an assistant window.

Uses OpenCV connected components and masked template matching. The template is
learned in memory at the native pointer position, never saved with private pixels.
An unconfirmed pointer supplies no exclusion region.
"""
import cv2
import numpy as np


class SoftwarePointer:
    def __init__(self):
        self.template=None;self.mask=None;self.box=None

    def locate(self,image,point,*,may_learn=True):
        height,width=image.shape[:2]
        if may_learn and point is not None and self.template is None:
            px,py=point;x=max(0,px-6);y=max(0,py-6);u=min(width,px+100);v=min(height,py+110)
            if x<u and y<v:
                crop=image[y:v,x:u]
                minimum=crop.min(2)
                white=((minimum>120)&(crop.max(2)-minimum<45)).astype(np.uint8)
                _,labels,stats,_=cv2.connectedComponentsWithStats(white)
                candidates=[]
                for i,(left,top,w,h,area)in enumerate(stats[1:],1):
                    # The pointed tip must be at the sampled native position;
                    # letters and broad bright backgrounds are not cursor seeds.
                    if not(20<=w<=90 and 25<=h<=100 and .5<=w/h<=1.3 and area>=150):continue
                    if abs(x+int(left)-px)>4 or abs(y+int(top)-py)>4:continue
                    tip=labels[top:min(top+5,top+h),left:left+w]==i
                    if np.count_nonzero(tip)>40:continue
                    candidates.append((i,int(left),int(top),int(w),int(h)))
                if len(candidates)==1:
                    i,left,top,w,h=candidates[0]
                    self.template=crop[top:top+h,left:left+w].copy()
                    self.mask=((labels[top:top+h,left:left+w]==i)*255).astype(np.uint8)
                    self.box=(x+left,y+top,x+left+w,y+top+h)
                    return [max(0,self.box[0]-2),max(0,self.box[1]-2),min(width,self.box[2]+2),min(height,self.box[3]+2)]
        if self.box is None:return None
        # Crossing onto the assistant may leave the software cursor frozen in
        # the game's last frame. Find its learned pixels, not today's OS cursor.
        h,w=self.template.shape[:2]
        origins=([point]if point is not None else[])+[self.box[:2]]
        for px,py in origins:
            x=max(0,px-64);y=max(0,py-64);u=min(width,px+w+64);v=min(height,py+h+64)
            if u-x<w or v-y<h:continue
            scores=cv2.matchTemplate(image[y:v,x:u],self.template,cv2.TM_SQDIFF_NORMED,mask=self.mask)
            # Zero-energy background locations have undefined normalized scores.
            scores=np.where(np.isfinite(scores),scores,np.inf)
            score,_,where,_=cv2.minMaxLoc(scores)
            if not np.isfinite(score)or score>.001:continue
            x+=where[0];y+=where[1];self.box=(x,y,x+w,y+h)
            return [max(0,x-2),max(0,y-2),min(width,x+w+2),min(height,y+h+2)]
        return None
