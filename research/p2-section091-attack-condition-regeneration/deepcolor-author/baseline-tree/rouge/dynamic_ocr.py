"""Exact dirty-region OCR with full discovery on geometry/large changes.

Every changed pixel is covered. Previous text is retained only outside all dirty
regions; semantic readers always run against the current frame. No optical-flow
or approximate-image similarity is used to carry a numeric value forward.
"""
from copy import deepcopy
import cv2
import numpy as np

class DynamicOCR:
    def __init__(self, engine):
        self.engine=engine;self.image=None;self.raw=[];self.age=0
        self.metrics={};self.regions=None

    def __call__(self, image, *, regions=None, seed_from_full=False, force_discovery=False,
                 guard_outside=False):
        """Optional current-frame visual regions never carry page facts.

        A verified page may seed its first focused read from the immediately
        preceding full-frame read. Only unchanged text fully inside the current
        domain survives. Other strategy/geometry changes rediscover the domain.
        """
        domain=normalize_regions(regions,image.shape[:2])
        h,w=image.shape[:2];rects=None;outside_changed=False
        full_seed=(seed_from_full and domain is not None and self.regions is None)
        if (not force_discovery and self.image is not None and self.image.shape==image.shape
                and self.image.dtype==image.dtype and (self.regions==domain or full_seed) and self.age<8):
            dirty=np.any(image!=self.image,axis=2)
            if domain is not None:
                relevant=np.zeros((h,w),bool)
                for x0,y0,x1,y1 in domain:relevant[y0:y1,x0:x1]=True
                outside_changed=guard_outside and bool(np.any(dirty & ~relevant))
                if outside_changed:
                    # A new popup may leave all known page controls unchanged.
                    # Discover it on this frame, rather than after the age limit.
                    domain=None
                else:dirty &= relevant
            if not outside_changed and not np.any(dirty):rects=[]
            elif not outside_changed:
                # Max pooling, rather than subsampling, preserves one-pixel changes.
                block=16;hh=(h+block-1)//block;ww=(w+block-1)//block
                padded=np.zeros((hh*block,ww*block),np.uint8);padded[:h,:w]=dirty
                pooled=padded.reshape(hh,block,ww,block).max(axis=(1,3))
                _,_,stats,_=cv2.connectedComponentsWithStats(pooled)
                rects=[[max(0,int(x*block)-48),max(0,int(y*block)-48),
                        min(w,int((x+rw)*block)+48),min(h,int((y+rh)*block)+48)]
                       for x,y,rw,rh,_ in stats[1:]]
                # Include complete previous text lines touched by any dirty area.
                boxes=[bounds(record[0]) for record in self.raw]
                for _ in range(3):
                    for rect in rects:
                        for box in boxes:
                            if intersects(rect,box):
                                rect[:]=[max(0,min(rect[0],int(box[0])-12)),max(0,min(rect[1],int(box[1])-12)),
                                         min(w,max(rect[2],int(box[2])+12)),min(h,max(rect[3],int(box[3])+12))]
                    rects=merge(rects)
                if domain is not None:
                    rects=merge_rectangular([intersection(rect,area) for rect in rects for area in domain
                                 if positive_overlap(rect,area)])
                area=int(np.count_nonzero(relevant)) if domain else h*w
                if len(rects)>12 or union_area(rects)>area*.45:rects=None
        if rects is None:
            # A verified full seed is useful only for genuinely small changes.
            # Large changes are cheaper and more complete as one whole-frame
            # discovery than several page crops followed by semantic fallback.
            if seed_from_full and domain is not None:
                domain=None
            if domain is None:
                raw,_=self.engine(image);raw=raw or []
                self.metrics={'mode':'full_discovery','pixels':h*w,'regions':1}
            else:
                raw=[]
                for x0,y0,x1,y1 in domain:
                    local,_=self.engine(image[y0:y1,x0:x1])
                    for box,text,score in local or []:
                        raw.append([[[float(x)+x0,float(y)+y0] for x,y in box],text,score])
                self.metrics={'mode':'page_discovery',
                    'pixels':sum((r[2]-r[0])*(r[3]-r[1]) for r in domain),'regions':len(domain)}
            self.age=0
        else:
            raw=[deepcopy(r) for r in self.raw
                 if (domain is None or any(contains(area,bounds(r[0])) for area in domain))
                 and not any(intersects(bounds(r[0]),b) for b in rects)]
            for x0,y0,x1,y1 in rects:
                local,_=self.engine(image[y0:y1,x0:x1])
                for box,text,score in local or []:
                    raw.append([[[float(x)+x0,float(y)+y0] for x,y in box],text,score])
            self.age+=1
            self.metrics={'mode':'page_dirty_regions' if domain is not None else 'dirty_regions',
                          'pixels':union_area(rects),
                          'requested_pixels':sum((r[2]-r[0])*(r[3]-r[1]) for r in rects),
                          'regions':len(rects)}
        if outside_changed:self.metrics['outside_page_regions_changed']=True
        self.image=image.copy();self.raw=deepcopy(raw);self.regions=domain
        return raw,None


def positive_overlap(a,b):
    return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]


def union_area(rects):
    """Exact covered area without charging overlapping page domains twice."""
    if not rects:return 0
    xs=sorted({r[0] for r in rects}|{r[2] for r in rects})
    total=0
    for left,right in zip(xs,xs[1:]):
        spans=sorted((r[1],r[3]) for r in rects if r[0]<right and r[2]>left)
        height=0;end=None
        for top,bottom in spans:
            if end is None or top>end:
                height+=bottom-top
            elif bottom>end:height+=bottom-end
            end=bottom if end is None else max(end,bottom)
        total+=(right-left)*height
    return total


def contains(area,box):
    return area[0]<=box[0] and area[1]<=box[1] and area[2]>=box[2] and area[3]>=box[3]


def intersection(a,b):
    return [max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]


def normalize_regions(regions,shape):
    if regions is None:return None
    h,w=shape;clean=[]
    try:
        for region in regions:
            if len(region)!=4 or not all(np.isfinite(value) for value in region):return None
            x0,y0,x1,y1=region
            if x1<=x0 or y1<=y0:return None
            rect=[max(0,int(np.floor(x0))),max(0,int(np.floor(y0))),
                  min(w,int(np.ceil(x1))),min(h,int(np.ceil(y1)))]
            if rect[2]<=rect[0] or rect[3]<=rect[1]:return None
            clean.append(rect)
    except (ValueError,TypeError,OverflowError):return None
    return tuple(tuple(r) for r in sorted(merge_rectangular(clean))) if clean else None


def merge_rectangular(rects):
    """Merge only rectangular unions; never fill an L-shaped excluded corner."""
    result=[]
    for rect in rects:
        rect=list(rect)
        while True:
            found=None
            for candidate in result:
                box=[min(rect[0],candidate[0]),min(rect[1],candidate[1]),
                     max(rect[2],candidate[2]),max(rect[3],candidate[3])]
                overlap=intersection(rect,candidate)
                area=lambda r:max(0,r[2]-r[0])*max(0,r[3]-r[1])
                if area(box)==area(rect)+area(candidate)-area(overlap):
                    found=candidate;break
            if found is None:break
            result.remove(found);rect=box
        result.append(rect)
    return result

def bounds(box):
    return [min(p[0] for p in box),min(p[1] for p in box),max(p[0] for p in box),max(p[1] for p in box)]

def intersects(a,b):
    return a[0]<=b[2] and a[2]>=b[0] and a[1]<=b[3] and a[3]>=b[1]

def merge(rects):
    result=[]
    for rect in rects:
        while True:
            found=next((r for r in result if intersects(r,rect)),None)
            if found is None:break
            result.remove(found)
            rect=[min(rect[0],found[0]),min(rect[1],found[1]),max(rect[2],found[2]),max(rect[3],found[3])]
        result.append(rect)
    return result
