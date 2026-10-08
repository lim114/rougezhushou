"""Read a white upward counter glyph adjacent to an existing OCR integer.

The glyph identifies a counter candidate, never its relic. Callers must bind the
returned boxes to current, dynamically observed card bounds. Missing candidates
mean unknown, not zero. This module performs no OCR and no full-frame template
search; only a font-sized neighborhood of each high-confidence integer is read.
"""
from functools import lru_cache
from pathlib import Path
import json
import math
import re

import cv2
import numpy as np

DATA = Path(__file__).with_name('data')


@lru_cache(maxsize=1)
def _reference():
    settings = json.loads((DATA / 'counter-badge-reference.json').read_text(encoding='utf-8'))
    raw = cv2.imdecode(np.fromfile(DATA / settings['template_file'], np.uint8), cv2.IMREAD_GRAYSCALE)
    if raw is None or not np.any(raw):
        raise ValueError('计数箭头参考模板无效。')
    return settings, raw > 0


def _white(image, settings):
    if image.ndim == 2:
        return image >= settings['white_min']
    pixels = image[:, :, :3]
    return ((pixels.min(axis=2) >= settings['white_min']) &
            (pixels.max(axis=2).astype(np.int16) - pixels.min(axis=2) <= settings['chroma_max']))


def _polygon(rect, width, height):
    x0, y0, x1, y1 = rect
    return [[x0 / width, y0 / height], [x1 / width, y0 / height],
            [x1 / width, y1 / height], [x0 / width, y1 / height]]


def _bounds(text, width, height):
    points = text.get('box')
    if not isinstance(points, (list, tuple)) or len(points) < 2:
        return None
    try:
        xs = [float(p[0]) for p in points]
        ys = [float(p[1]) for p in points]
    except (ValueError, TypeError, IndexError):
        return None
    if not all(math.isfinite(p) and 0 <= p <= 1 for p in xs + ys):
        return None
    x0, x1 = min(xs) * width, max(xs) * width
    y0, y1 = min(ys) * height, max(ys) * height
    if x1 <= x0 or y1 <= y0:
        return None
    return x0, y0, x1, y1


def _shape_score(component, reference):
    resized = cv2.resize(component.astype(np.uint8), (reference.shape[1], reference.shape[0]),
                         interpolation=cv2.INTER_NEAREST) > 0
    union = np.count_nonzero(resized | reference)
    return float(np.count_nonzero(resized & reference) / union) if union else 0.


def _candidate_matches(image, texts, settings, reference):
    """Internal training seam: scored geometry-valid candidates, no threshold."""
    height, width = image.shape[:2]
    found = []
    for text in texts:
        value_text = text.get('text', '')
        if not isinstance(value_text, str) or not re.fullmatch(r'[0-9]{1,3}', value_text):
            continue
        try:
            confidence = float(text.get('confidence', 0))
        except (ValueError, TypeError):
            continue
        if not math.isfinite(confidence) or confidence < settings['ocr_min']:
            continue
        bounds = _bounds(text, width, height)
        if bounds is None:
            continue
        nx0, ny0, nx1, ny1 = bounds
        font = ny1 - ny0
        # OCR may include the adjacent icon. Numeric ink is refined below.
        if font < 6 or font > 180 or nx1 - nx0 > font * (len(value_text) * 1.1 + 1.5):
            continue
        x0 = max(0, math.floor(nx0 - font * settings['left_search_fonts']))
        x1 = min(width, math.ceil(min(nx1, nx0 + font * settings['right_search_fonts'])))
        y0 = max(0, math.floor(ny0 - font * .4))
        y1 = min(height, math.ceil(ny1 + font * .35))
        roi = image[y0:y1, x0:x1]
        if not roi.size:
            continue
        white = _white(roi, settings).astype(np.uint8)
        _, labels, stats, _ = cv2.connectedComponentsWithStats(white, connectivity=8)
        for label, (cx, cy, cw, ch, area) in enumerate(stats[1:], 1):
            if (not .32 * font <= cw <= 1.15 * font or
                    not .35 * font <= ch <= font or not .8 <= cw / ch <= 1.35 or
                    area < .04 * font * font):
                continue
            mx0, my0 = x0 + int(cx), y0 + int(cy)
            mx1, my1 = mx0 + int(cw), my0 + int(ch)
            if abs((my0 + my1 - ny0 - ny1) / 2) > .3 * font:
                continue
            component = labels[cy:cy + ch, cx:cx + cw] == label
            score = _shape_score(component, reference)
            # Keep only actual white digit ink inside the supplied OCR box and
            # to the right of the marker. A percentage/prose line is never an
            # integer candidate and a bare resource count lacks the glyph.
            dx0 = max(0, math.floor(max(nx0, mx1 + .08 * font)))
            dx1 = min(width, math.ceil(nx1))
            dy0 = max(0, math.floor(ny0))
            dy1 = min(height, math.ceil(ny1))
            digits = image[dy0:dy1, dx0:dx1]
            if not digits.size:
                continue
            _, _, ds, _ = cv2.connectedComponentsWithStats(_white(digits, settings).astype(np.uint8), connectivity=8)
            # Anti-aliasing may disconnect a digit's top/bottom at some scales.
            # Merge overlapping horizontal extents before counting digit groups;
            # do not mistake these fragments for an additional OCR digit.
            fragments = sorted((int(s[0]), int(s[1]), int(s[0] + s[2]), int(s[1] + s[3]))
                               for s in ds[1:] if s[4] >= max(3, .006 * font * font))
            groups = []
            for fragment in fragments:
                if groups and fragment[0] < groups[-1][2]:
                    old = groups[-1]
                    groups[-1] = (old[0], min(old[1], fragment[1]),
                                  max(old[2], fragment[2]), max(old[3], fragment[3]))
                else:
                    groups.append(fragment)
            ink = [group for group in groups if group[3] - group[1] >= .25 * font]
            if len(ink) != len(value_text):
                continue
            bx0 = dx0 + min(s[0] for s in ink)
            bx1 = dx0 + max(s[2] for s in ink)
            by0 = dy0 + min(s[1] for s in ink)
            by1 = dy0 + max(s[3] for s in ink)
            if (not 0 <= bx0 - mx1 <= .75 * font or
                    abs((my0 + my1 - by0 - by1) / 2) > .25 * font or
                    bx1 - bx0 > len(value_text) * .95 * font):
                continue
            found.append({'value': int(value_text), 'box': _polygon((bx0, by0, bx1, by1), width, height),
                          'marker_box': _polygon((mx0, my0, mx1, my1), width, height),
                          'score': score, 'confidence': confidence,
                          'source': 'white_up_counter_glyph_and_ocr'})
    return found


def read_counter_badges(image, texts):
    """Return verified-glyph integer candidates (0..999), with normalized boxes.

    ``image`` is a BGR/gray ndarray; ``texts`` use the project's normalized OCR
    polygon format. No item ID, ownership, used state or inventory completeness
    is inferred. Conflicting OCR values at the same marker are discarded.
    """
    if not isinstance(image, np.ndarray) or image.size == 0 or image.ndim not in (2, 3):
        return []
    if image.ndim == 3 and image.shape[2] < 3:
        return []
    settings, reference = _reference()
    candidates = _candidate_matches(image, texts, settings, reference)
    grouped = {}
    height, width = image.shape[:2]
    for candidate in candidates:
        if candidate['score'] < settings['minimum_score']:
            continue
        key = tuple(round(point[axis] * (width if axis == 0 else height))
                    for point in candidate['marker_box'] for axis in (0, 1))
        grouped.setdefault(key, []).append(candidate)
    result = []
    for group in grouped.values():
        if len({candidate['value'] for candidate in group}) != 1:
            continue
        result.append(max(group, key=lambda candidate: (candidate['score'], candidate['confidence'])))
    return sorted(result, key=lambda candidate: (candidate['box'][0][1], candidate['box'][0][0]))
