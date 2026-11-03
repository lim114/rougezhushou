"""Local UI geometry measured from current OCR, independent of frame dimensions.

Offsets describe a control's internal layout in reference font units. They never
select a screen quadrant. Every invocation uses the current label and its size.
"""
import numpy as np
import cv2

def units(image, anchor, reference_font):
    h, w = image.shape[:2]
    height = (max(p[1] for p in anchor['box']) - min(p[1] for p in anchor['box'])) * h
    # Detector boxes expand after coarse whole-frame downsampling. Glyph height
    # is stable for the same rendered label, including a moved panel.
    ink_reference = {24.9: (17, False), 23.8: (16, False), 18.6: (8, False),
                     35.2: (26, True)}.get(reference_font)
    text=anchor.get('text','').upper()
    if ink_reference and (text.startswith('RANK') or text.endswith('LV') or text in ('EXP','信赖值')):
        x0=min(p[0] for p in anchor['box']);x1=max(p[0] for p in anchor['box'])
        y0=min(p[1] for p in anchor['box']);y1=max(p[1] for p in anchor['box'])
        roi=crop(image,(x0,y0,x1,y1))
        if roi.size:
            gray=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
            ink,dark=ink_reference
            mask=(gray<100 if dark else gray>170).astype(np.uint8)
            _,_,stats,_=cv2.connectedComponentsWithStats(mask)
            candidates=[float(s[3]) for s in stats[1:] if s[4]>3 and s[2]>2
                        and s[2]<roi.shape[1]*.5 and s[3]>=height*.3 and s[3]<height*.95]
            if candidates:height=max(candidates)*reference_font/ink
    scale = height / reference_font
    return scale * 2052 / w, scale * 1127 / h

def crop(image, bounds):
    h, w = image.shape[:2]
    x0, y0, x1, y1 = bounds
    return image[max(0, round(y0*h)):min(h, round(y1*h)),
                 max(0, round(x0*w)):min(w, round(x1*w))]
