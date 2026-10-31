"""Squad artwork localization at measured UI scale, independent of screen position."""
from functools import lru_cache
import json
from pathlib import Path
import re

import cv2
import numpy as np

DATA = Path(__file__).with_name('data')


@lru_cache(maxsize=1)
def references():
    receipt = json.loads((DATA / 'run-badge-receipt.json').read_text(encoding='utf-8'))
    result = {}
    for item in receipt['icons']:
        if item['id'] != item['normal_id']:
            continue
        rgba = cv2.imdecode(np.fromfile(DATA / item['file'], np.uint8), cv2.IMREAD_UNCHANGED)
        alpha = rgba[:, :, 3:4].astype(np.float32) / 255
        # Include both bright artwork and its dark gaps. Matching only opaque
        # white strokes incorrectly gives blank backgrounds very high scores.
        rgb = rgba[:, :, :3] * alpha + 16 * (1 - alpha)
        result[item['id']] = (item, cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_BGR2GRAY))
    return result


@lru_cache(maxsize=512)
def scaled_reference(identity, width):
    reference = references()[identity][1]
    return cv2.resize(reference, (width, max(1, round(width * reference.shape[0] / reference.shape[1]))),
                      interpolation=cv2.INTER_AREA)


def _match(gray, identity, sizes):
    best = None
    for size in sizes:
        template = scaled_reference(identity, int(size))
        if template.shape[0] > gray.shape[0] or template.shape[1] > gray.shape[1]:
            continue
        scores = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        _, score, _, at = cv2.minMaxLoc(scores)
        if np.isfinite(score) and (best is None or score > best['score']):
            best = {'id': identity, 'score': float(score), 'at': at,
                    'width': template.shape[1], 'height': template.shape[0]}
    return best


def find_squad_badge(image, anchor=None):
    """Find one unambiguous badge; current text geometry only narrows the search.

    Without an anchor, use a coarse whole-frame search followed by local scale
    refinement. The returned rectangle is measured from this frame, never reused
    as a fixed region for a later frame or resolution.
    """
    height, width = image.shape[:2]
    factor = 1.
    if anchor:
        points = np.asarray(anchor['box']) * (width, height)
        font = float(np.ptp(points[:, 1]))
        if font < 5:
            return None
        left = float(points[:, 0].min())
        middle = float(points[:, 1].mean())
        x0, x1 = max(0, round(left - 7.5 * font)), min(width, round(left + .3 * font))
        y0, y1 = max(0, round(middle - 3.8 * font)), min(height, round(middle + 1.3 * font))
        sizes = sorted({max(12, round(font * ratio)) for ratio in np.arange(2., 5.01, .35)})
        area = image[y0:y1, x0:x1]
    else:
        x0 = y0 = 0
        factor = min(1., 720. / max(width, height))
        area = cv2.resize(image, None, fx=factor, fy=factor, interpolation=cv2.INTER_AREA)
        sizes = range(max(16, round(min(area.shape[:2]) * .035)),
                      max(20, round(min(area.shape[:2]) * .16)), 5)
    if not area.size:
        return None
    gray = cv2.cvtColor(area, cv2.COLOR_BGR2GRAY)
    if float(gray.std()) < 3:
        return None
    candidates = [_match(gray, identity, sizes) for identity in references()]
    candidates = sorted((item for item in candidates if item), key=lambda item: item['score'], reverse=True)
    if not candidates or candidates[0]['score'] < .70:
        return None
    refined = []
    for candidate in candidates[:3]:
        center = candidate['width']
        radius = max(3, round(center * .12))
        item = _match(gray, candidate['id'], range(max(12, center - radius), center + radius + 1))
        if item:
            refined.append(item)
    refined.sort(key=lambda item: item['score'], reverse=True)
    best = refined[0]
    runner_up = max([item['score'] for item in refined[1:]] + [item['score'] for item in candidates[3:]] + [0])
    if best['score'] < .86 or best['score'] - runner_up < .09:
        return None
    bx, by = best['at']
    left, top = (x0 + bx / factor) / width, (y0 + by / factor) / height
    right = (x0 + (bx + best['width']) / factor) / width
    bottom = (y0 + (by + best['height']) / factor) / height
    best['box'] = [[left, top], [right, top], [right, bottom], [left, bottom]]
    best['margin'] = best['score'] - runner_up
    best['name'] = references()[best['id']][0]['name']
    return {key: best[key] for key in ('id', 'name', 'score', 'margin', 'box')}


def read_badge_grade(image, badge, texts, engine=None):
    """Grade digits must belong to the located badge, not another map counter."""
    height, width = image.shape[:2]
    (x0, y0), _, (x1, y1), _ = badge['box']
    size = (x1 - x0) * width
    left = max(0, round(x0 * width - .40 * size))
    right = min(width, round(x0 * width + .32 * size))
    top = max(0, round(y0 * height + .50 * size))
    bottom = min(height, round(y0 * height + 1.04 * size))
    valid = set()
    for record in texts:
        if record['confidence'] < .94 or not re.fullmatch(r'\d{1,2}', record['text']):
            continue
        xx = np.mean([point[0] for point in record['box']]) * width
        yy = np.mean([point[1] for point in record['box']]) * height
        if left < xx < right and top < yy < bottom and 0 <= int(record['text']) <= 15:
            valid.add(int(record['text']))
    if len(valid) == 1:
        return next(iter(valid))
    if engine is None or valid or right <= left or bottom <= top:
        return None
    crop = image[top:bottom, left:right]
    enlarged = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    raw, _ = engine(enlarged)
    for _, text, confidence in raw or []:
        if confidence >= .94 and re.fullmatch(r'\d{1,2}', text) and 0 <= int(text) <= 15:
            valid.add(int(text))
    return next(iter(valid)) if len(valid) == 1 else None
