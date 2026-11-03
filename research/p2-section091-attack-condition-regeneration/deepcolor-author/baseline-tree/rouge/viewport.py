"""Re-estimate the analysis viewport for each frame; no resolution profiles."""
import cv2
import numpy as np

def prepare_frame(image,client_rect=None):
    h,w=image.shape[:2]
    origin_x=origin_y=0
    if client_rect is not None:
        x0,y0,x1,y1=map(int,client_rect)
        if 0<=x0<x1<=w and 0<=y0<y1<=h and x1-x0>=320 and y1-y0>=180:
            image=image[y0:y1,x0:x1];origin_x,origin_y=x0,y0
    ch,cw=image.shape[:2]
    # Only contiguous, almost entirely black outer padding is removed. Dark
    # interior panels are not candidates. Thin game borders remain untouched.
    dark=np.max(image[:,:,:3],axis=2)<=3
    rows=np.mean(dark,axis=1)>=.999
    cols=np.mean(dark,axis=0)>=.999
    def edges(mask,length):
        visible=np.flatnonzero(~mask)
        if not len(visible):return 0,length
        a,b=int(visible[0]),int(visible[-1])+1
        return (a if a>=max(4,round(length*.005)) else 0,
                b if length-b>=max(4,round(length*.005)) else length)
    top,bottom=edges(rows,ch);left,right=edges(cols,cw)
    if right-left<320 or bottom-top<180:left,top,right,bottom=0,0,cw,ch
    content=image[top:bottom,left:right]
    # Continuous scale, recalculated after every resize. Give small text/pips
    # enough pixels for OCR and visual matching while bounding analysis cost.
    scale=max(1.,min(1127/content.shape[0],2400/content.shape[1]))
    analysis=cv2.resize(content,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC) if scale>1 else content
    return analysis,{'source_size':[w,h],'content_rect':[origin_x+left,origin_y+top,origin_x+right,origin_y+bottom],
                     'analysis_size':[analysis.shape[1],analysis.shape[0]],'scale':scale,
                     'coordinate_space':'source_frame_normalized'}

def map_evidence(value,viewport):
    """Keep externally exposed evidence coordinates on the original capture."""
    w,h=viewport['source_size'];left,top,right,bottom=viewport['content_rect']
    def point(p):return [(left+p[0]*(right-left))/w,(top+p[1]*(bottom-top))/h]
    if isinstance(value,dict):
        for key,item in value.items():
            if key in ('box','title_box') and isinstance(item,list):value[key]=[point(p) for p in item]
            elif key in ('center','card_position') and isinstance(item,(tuple,list)) and len(item)==2:value[key]=point(item)
            else:map_evidence(item,viewport)
    elif isinstance(value,list):
        for item in value:map_evidence(item,viewport)
    return value
