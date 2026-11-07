"""Exact dirty-region OCR with full discovery on geometry/large changes.

Every changed pixel is covered. Previous text is retained only outside all dirty
regions; semantic readers always run against the current frame. No optical-flow
or approximate-image similarity is used to carry a numeric value forward.
"""
from copy import deepcopy
import cv2
import numpy as np

class DynamicOCR:
    def __init__(self, engine, *, discovery_engine=None):
        self.engine=engine;self.image=None;self.raw=[];self.age=0
        self.discovery_engine=discovery_engine if discovery_engine is not None else engine
        self.metrics={};self.regions=None

    def seed_full_frame(self, image, raw):
        """Accept only a caller-verified complete current-frame text result.

        This stores OCR records, never interpreted page/operator facts. A later
        call still covers every changed pixel and applies all discovery gates.
        """
        self.image=image.copy();self.raw=deepcopy(raw or [])
        self.regions=None;self.age=0

    def _read_regions(self,image,regions):
        for x0,y0,x1,y1 in regions:
            local,_=self.engine(image[y0:y1,x0:x1])
            for box,text,score in local or []:
                yield [[[float(x)+x0,float(y)+y0] for x,y in box],text,score]

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
            if image.dtype == np.uint8 and image.ndim == 3 and image.shape[2] in (3,4) and image.size:
                difference = cv2.absdiff(image, self.image)
                zero = (0, 0, 0, 0)
                dirty = cv2.inRange(difference, zero, zero) == 0
            else:
                dirty = np.any(image != self.image, axis=2)
            if domain is not None:
                relevant=np.zeros((h,w),bool)
                for x0,y0,x1,y1 in domain:relevant[y0:y1,x0:x1]=True
                outside_changed=guard_outside and bool(np.any(dirty & ~relevant))
                if outside_changed:
                    # A new popup may leave all known page controls unchanged.
                    # Discover it on this frame, rather than after the age limit.
                    domain=None
                else:dirty &= relevant
            boxes = (bounds(record[0]) for record in self.raw)
            covered_pixels = 0
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
                boxes = list(boxes)
                for _ in range(3):
                    expanded = []
                    for rect in rects:
                        for box in boxes:
                            if intersects(rect,box):
                                rect=[max(0,min(rect[0],int(box[0])-12)),max(0,min(rect[1],int(box[1])-12)),
                                         min(w,max(rect[2],int(box[2])+12)),min(h,max(rect[3],int(box[3])+12))]
                        expanded.append(rect)
                    merged = merge(expanded)
                    if merged == rects:
                        break
                    rects = merged
                if domain is not None:
                    rects=merge_rectangular([intersection(rect,area) for rect in rects for area in domain
                                 if positive_overlap(rect,area)])
                area=int(np.count_nonzero(relevant)) if domain else h*w
                if len(rects)>12 or (covered_pixels := union_area(rects))>area*.45:rects=None
        if rects is None:
            # A verified full seed is useful only for genuinely small changes.
            # Large changes are cheaper and more complete as one whole-frame
            # discovery than several page crops followed by semantic fallback.
            if seed_from_full and domain is not None:
                domain=None
            if domain is None:
                raw,_=self.discovery_engine(image);raw=raw or []
                self.metrics={'mode':'full_discovery','pixels':h*w,'regions':1}
                discovery_metrics=getattr(self.discovery_engine,'metrics',{})
                self.metrics.update({key:discovery_metrics[key] for key in
                    ('inferred_text_rows','reused_text_rows','detected_boxes','full_detection',
                     'complete_current_texts') if key in discovery_metrics})
            else:
                raw=list(self._read_regions(image,domain))
                self.metrics={'mode':'page_discovery',
                    'pixels':sum((r[2]-r[0])*(r[3]-r[1]) for r in domain),'regions':len(domain)}
            self.age=0
        else:
            if domain is not None or rects:
                raw = [record for record, box in zip(self.raw, boxes)
                       if (domain is None or any(contains(area, box) for area in domain))
                       and not any(intersects(box, rect) for rect in rects)]
                raw.extend(self._read_regions(image,rects))
            else:
                raw = self.raw
            self.age+=1
            self.metrics={'mode':'page_dirty_regions' if domain is not None else 'dirty_regions',
                          'pixels':covered_pixels,
                          'requested_pixels':sum((r[2]-r[0])*(r[3]-r[1]) for r in rects),
                          'regions':len(rects)}
        if outside_changed:self.metrics['outside_page_regions_changed']=True
        # A full-domain uint8 comparison with no dirty rectangle already proves
        # the stored image is current. A focused read still snapshots all pixels.
        if rects != [] or domain is not None or image.dtype != np.uint8:
            self.image=image.copy()
        if rects is None:
            # The discovery engine and its caller may retain this result.
            self.raw=deepcopy(raw)
        else:
            # Retained rows already belong to this reader. Detach the output once.
            self.raw=raw
            raw=[deepcopy(record) for record in raw]
        self.regions=domain
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
    def area(r):
        return max(0,r[2]-r[0])*max(0,r[3]-r[1])
    result=[]
    for rect in rects:
        rect=list(rect)
        while True:
            rect_area=area(rect)
            for index,candidate in enumerate(result):
                box=[min(rect[0],candidate[0]),min(rect[1],candidate[1]),
                     max(rect[2],candidate[2]),max(rect[3],candidate[3])]
                overlap=intersection(rect,candidate)
                if area(box)==rect_area+area(candidate)-area(overlap):
                    del result[index]
                    rect=box
                    break
            else:break
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
            for index,existing in enumerate(result):
                if intersects(existing,rect):
                    del result[index]
                    rect=[min(rect[0],existing[0]),min(rect[1],existing[1]),
                          max(rect[2],existing[2]),max(rect[3],existing[3])]
                    break
            else:break
        result.append(rect)
    return result
