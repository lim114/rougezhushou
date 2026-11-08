"""Identify resource labels/icons before accepting any numeric counter."""
from functools import lru_cache
from pathlib import Path
import re
import cv2
import numpy as np
from .operator_recognition import center
from .anchors import units, header_span

@lru_cache(maxsize=1)
def gold_template():
    return cv2.imdecode(np.fromfile(Path(__file__).with_name('data')/'ui-icons/gold-counter.png',dtype=np.uint8),cv2.IMREAD_GRAYSCALE)

def read_resources(image,texts,engine=None, *, on_gold=None):
    resources={}
    gold = read_gold(image, texts)
    if gold is not None and on_gold is not None:
        on_gold(gold)
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
    if gold is not None:
        resources['gold'] = gold
    return resources


def read_gold(image, texts):
    # Reject the appraisal number, hope and action-points counters even if OCR is confident.
    anchor=next((t for t in texts if t['text']=='目标生命值' and t['confidence']>=.9),None)
    if anchor is None:return None
    numbers=[(int(t['text']),*center(t)) for t in texts if t['confidence']>=.95 and re.fullmatch(r'\d{1,4}',t['text'])]
    top, bottom = header_span(anchor)
    numbers = [(value, x, y) for value, x, y in numbers if top <= y <= bottom]
    if not numbers:return None
    ux,uy=units(image,anchor,27.9678)
    match=find_gold_icon(image, ((nx,ny) for _,nx,ny in numbers), ux, uy, header=(top, bottom))
    if match is not None:
        return gold_reading(match, numbers, ux, uy)
    return None


def gold_reading(match, numbers, ux, uy):
    score,x,y = match
    values = {value for value,nx,ny in numbers if
              .035*ux < nx-x < .13*ux and abs(ny-y) < .027*uy}
    if len(values) == 1:
        return {'value': next(iter(values)), 'source': '源石锭三角图标右侧数量', 'icon_score': float(score)}
    return None


def find_gold_icon(image, centers, ux, uy, *, header=None):
    h,w=image.shape[:2]
    template=gold_template();gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    regions = []
    for nx,ny in centers:
        x0=max(0,round((nx-.18*ux)*w));x1=min(w,round((nx-.02*ux)*w))
        y0=max(0,round((ny-.05*uy)*h));y1=min(h,round((ny+.05*uy)*h))
        roi=gray[y0:y1,x0:x1]
        if roi.size:
            regions.append((roi, x0, y0))

    icon_scale = h*uy/1127
    # Preserve all coarse matches first. If those miss, sample the middle of
    # each original scale interval with the same confidence requirement.
    for factors in ((.85, 1., 1.15), (.925, 1.075)):
        matches = []
        for factor in factors:
            ref = cv2.resize(template, None, fx=icon_scale*factor, fy=icon_scale*factor)
            th, tw = ref.shape
            for roi, x0, y0 in regions:
                if th > roi.shape[0] or tw > roi.shape[1]:
                    continue
                scores = cv2.matchTemplate(roi, ref, cv2.TM_CCOEFF_NORMED)
                _, best, _, point = cv2.minMaxLoc(scores)
                center_y = (y0+point[1]+th/2)/h
                if best >= .91 and (header is None or header[0] <= center_y <= header[1]):
                    matches.append((best, (x0+point[0]+tw/2)/w, center_y))
        if matches:
            return max(matches)
    return None
