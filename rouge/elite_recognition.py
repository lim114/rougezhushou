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
    originals = references()
    best = dict.fromkeys(originals, 0)
    xs = dict.fromkeys(round((x+.016*ux+dx*ux)*w) for dx in (-.003,0,.003))
    ys = dict.fromkeys(round((y-.052*uy+dy*uy)*h) for dy in (-.003,0,.003))
    sizes = dict.fromkeys(round(h*scale*uy) for scale in np.arange(.034,.051,.002))
    for size in sizes:
        masks = []
        for elite, original in originals.items():
            template = cv2.resize(original, (size,size), interpolation=cv2.INTER_AREA)
            mask = (cv2.cvtColor(template[:,:,:3], cv2.COLOR_BGR2GRAY)>150) & (template[:,:,3]>150)
            mask_pixels = np.count_nonzero(mask)
            if mask_pixels >= 10:
                masks.append((elite, mask, mask_pixels))
        if not masks:
            continue
        for cx in xs:
            for cy in ys:
                roi = image[cy-size//2:cy-size//2+size, cx-size//2:cx-size//2+size]
                if roi.shape[:2] != (size,size):
                    continue
                actual = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)>180
                actual_pixels = np.count_nonzero(actual)
                # Each candidate compares its entire silhouette with the same current pixels.
                for elite, mask, mask_pixels in masks:
                    score = 2 * np.count_nonzero(actual & mask) / (actual_pixels + mask_pixels)
                    best[elite] = max(best[elite], score)
    scores = sorted(((score, elite) for elite, score in best.items()), reverse=True)
    score, elite = scores[0]
    if score < .70:
        return None
    margin = score - scores[1][0]
    if margin < .085:
        return None
    return {'value':elite,'score':score,'margin':margin}
