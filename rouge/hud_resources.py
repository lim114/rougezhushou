"""Read current HUD quantities from labels/icons, never from game mechanics."""
from functools import lru_cache
from pathlib import Path
import re
import cv2
import numpy as np
from .anchors import crop
from .operator_recognition import center


def _number(image, texts, box, engine, *, ratio=False, segmented=False):
    pattern = r'(\d+)/(\d+)' if ratio else r'\d+'
    values = {t['text'] for t in texts if t['confidence'] >= .9
              and box[0] <= center(t)[0] <= box[2] and box[1] <= center(t)[1] <= box[3]
              and re.fullmatch(pattern, t['text'])}
    if not values:
        current = crop(image, box)
        if not current.size:
            return None
        current = cv2.copyMakeBorder(current, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=0)
        raw, _ = engine(cv2.resize(current, None, fx=2, fy=2), use_cls=False, use_det=not segmented)
        values = {row[-2].replace(' ', '') for row in raw or []
                  if row[-1] >= .9 and re.fullmatch(pattern, row[-2].replace(' ', ''))}
    if len(values) != 1:
        return None
    value = next(iter(values))
    if ratio:
        amount, capacity = map(int, value.split('/'))
        return {'value': amount, 'capacity': capacity} if amount <= capacity else None
    return {'value': int(value)}


@lru_cache(maxsize=1)
def _icons():
    root = Path(__file__).with_name('data') / 'ui-icons'
    return {name: cv2.imdecode(np.fromfile(root / ('hud-' + name + '.png'), dtype=np.uint8), 0)
            for name in ('shield', 'hope')}


def read_hud_resources(image, texts, engine):
    h, w = image.shape[:2]
    resources = {}
    labels = {t['text']: t for t in texts if t['confidence'] >= .9}
    for key, label in (('life', '目标生命值'), ('command', '指挥等级'),
                       ('action', '行动力'), ('valuation', '总估价')):
        anchor = labels.get(label)
        if anchor is None:
            continue
        x0, y0 = np.min(anchor['box'], axis=0)
        x1, y1 = np.max(anchor['box'], axis=0)
        dy = y1 - y0
        dx = dy * h / w
        if key == 'life':
            box = (x0 - .1*dx, y1, x1, y1 + 1.6*dy)
        elif key == 'command':
            box = (x0 - 2.2*dx, y0 + .6*dy, x0 - .2*dx, y1 + 1.2*dy)
        elif key == 'action':
            box = (x0 - .5*dx, y1, x1 + .8*dx, y1 + 4.5*dy)
        else:
            box = (x0 - .5*dx, y1, x1 + 1.2*dx, y1 + 2.4*dy)
        value = _number(image, texts, box, engine, ratio=key == 'life')
        if value is not None:
            resources[key] = {**value, 'source': label + '当前标签对应数值'}
    life = labels.get('目标生命值')
    if life is None:
        return resources
    # Locate icons anywhere along the CURRENT header's vertical span, not a
    # remembered screen quadrant. Their own bounds locate their counter.
    x0, y0 = np.min(life['box'], axis=0)
    x1, y1 = np.max(life['box'], axis=0)
    font = (y1-y0)*h
    top, bottom = max(0, int(y0*h-font)), min(h, int(y1*h+2*font))
    gray = cv2.cvtColor(image[top:bottom], cv2.COLOR_BGR2GRAY)
    for key, template in _icons().items():
        matches = []
        for factor in (.85, 1., 1.15):
            scale = font/25.78*factor
            ref = cv2.resize(template, None, fx=scale, fy=scale)
            if ref.shape[0] > gray.shape[0] or ref.shape[1] > gray.shape[1]:
                continue
            scores = cv2.matchTemplate(gray, ref, cv2.TM_CCOEFF_NORMED)
            _, score, _, point = cv2.minMaxLoc(scores)
            if score >= .91:
                matches.append((score, point, ref.shape))
        if not matches:
            continue
        score, (left, yy), (ih, iw) = max(matches)
        yy += top
        if key == 'shield':
            box = ((left+iw*1.15)/w, (yy-ih*.1)/h, (left+iw*4)/w, (yy+ih*1.1)/h)
            value = _number(image, texts, box, engine)
        else:
            # The available hope is yellow; the grey neighbouring number is
            # its limit. Remove the short arrow and solid progress-bar strip.
            box = ((left+iw*1.55)/w, yy/h, min(1., (left+iw*4)/w), (yy+ih*1.2)/h)
            current = crop(image, box)
            if not current.size:
                continue
            hsv = cv2.cvtColor(current, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, (18, 90, 100), (40, 255, 255))
            _, groups, stats, _ = cv2.connectedComponentsWithStats(mask)
            ids = [i for i, (xx, _, width, height, _) in enumerate(stats[1:], 1)
                   if xx > 0 and xx+width < mask.shape[1] and font*.55 <= height <= font*1.6]
            glyphs = (np.isin(groups, ids)*255).astype(np.uint8)
            points = cv2.findNonZero(glyphs)
            if points is None:
                continue
            gx, gy, gw, gh = cv2.boundingRect(points)
            digits = cv2.cvtColor(glyphs[gy:gy+gh, gx:gx+gw], cv2.COLOR_GRAY2BGR)
            value = _number(digits, [], (0., 0., 1., 1.), engine, segmented=True)
        if value is not None:
            resources[key] = {**value, 'source': ('护盾' if key == 'shield' else '希望') + '当前图标对应数值',
                              'icon_score': float(score)}
    return resources
