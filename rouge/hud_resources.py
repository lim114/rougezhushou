"""Read current HUD quantities from labels/icons, never from game mechanics."""
from functools import lru_cache
from pathlib import Path
import re
import cv2
import numpy as np
from .anchors import crop, header_span
from .operator_recognition import center


def _number(image, candidates, box, engine, *, ratio=False, segmented=False, valuation_font=None):
    values = {text for text,x,y in candidates if box[0] <= x <= box[2] and box[1] <= y <= box[3]}
    if not values:
        current = crop(image, box)
        if not current.size:
            return None
        if valuation_font is not None:
            value = _valuation(current, valuation_font, engine)
            if value is not None:
                return value
        current = cv2.copyMakeBorder(current, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=0)
        raw, _ = engine(cv2.resize(current, None, fx=2, fy=2), use_cls=False, use_det=not segmented)
        pattern = r'\d+/\d+' if ratio else r'\d+'
        values = {digits for row in raw or []
                  if row[-1] >= .9 and re.fullmatch(pattern, digits := row[-2].replace(' ', ''))}
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


def _valuation(current, font, engine):
    """Read the green amount as one line, excluding grey icon highlights."""
    mask = cv2.inRange(cv2.cvtColor(current, cv2.COLOR_BGR2HSV),
                       (65, 120, 140), (100, 255, 255))
    _, groups, stats, _ = cv2.connectedComponentsWithStats(mask)
    selected = [(i, x, y, x+width, y+height)
                for i, (x, y, width, height, _) in enumerate(stats[1:], 1)
                if font*.55 <= height <= font*1.6]
    if not selected:
        return None
    ids, lefts, tops, rights, bottoms = zip(*selected)
    glyphs = np.isin(groups[min(tops):max(bottoms), min(lefts):max(rights)], ids).astype(np.uint8)*255
    digits = cv2.cvtColor(glyphs, cv2.COLOR_GRAY2BGR)
    return _number(digits, [], (0., 0., 1., 1.), engine, segmented=True)


def read_hud_resources(image, texts, engine):
    h, w = image.shape[:2]
    resources = {}
    labels = {}
    counts, ratios = [], []
    for record in texts:
        if record['confidence'] >= .9:
            text = record['text']
            labels[text] = record
            if re.fullmatch(r'\d+(?:/\d+)?', text):
                (ratios if '/' in text else counts).append((text, *center(record)))
    life_bounds = None
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
            life_bounds = y0, y1
            box = (x0 - .1*dx, y1, x1, y1 + 1.6*dy)
        elif key == 'command':
            box = (x0 - 2.2*dx, y0 + .6*dy, x0 - .2*dx, y1 + 1.2*dy)
        elif key == 'action':
            box = (x0 - .5*dx, y1, x1 + .8*dx, y1 + 4.5*dy)
        else:
            box = (x0 - .5*dx, y1, x1 + 1.2*dx, y1 + 2.4*dy)
        value = _number(image, ratios if key == 'life' else counts, box, engine, ratio=key == 'life',
                        valuation_font=dy*h if key == 'valuation' else None)
        if value is not None:
            resources[key] = {**value, 'source': label + '当前标签对应数值'}
    if life_bounds is None:
        return resources
    # Locate icons anywhere along the CURRENT header's vertical span, not a
    # remembered screen quadrant. Their own bounds locate their counter.
    y0, y1 = life_bounds
    font = (y1-y0)*h
    top_y, bottom_y = header_span(labels['目标生命值'], h)
    top, bottom = max(0, int(top_y)), min(h, int(bottom_y))
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
            value = _number(image, counts, box, engine)
        else:
            # The available hope is yellow; the grey neighbouring number is
            # its limit. Remove the short arrow and solid progress-bar strip.
            box = ((left+iw*1.55)/w, yy/h, min(1., (left+iw*4)/w), (yy+ih*1.2)/h)
            current = crop(image, box)
            if not current.size:
                continue
            hsv = cv2.cvtColor(current, cv2.COLOR_BGR2HSV)
            value = None
            available = None
            for field, lower, upper in (('value', (18, 90, 100), (40, 255, 255)),
                                         ('capacity', (0, 0, 70), (179, 65, 255))):
                if field == 'capacity':
                    if value is None:
                        break
                    right = box[0] + (available[0]+available[2]+4*font)/w
                    if right > 1 or box[3] > 1:
                        continue
                    current = crop(image, (box[0], box[1], right, box[3]))
                    hsv = cv2.cvtColor(current, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, lower, upper)
                _, groups, stats, _ = cv2.connectedComponentsWithStats(mask)
                eligible = [(i, x, y, x+width, y+height)
                            for i, (x, y, width, height, _) in enumerate(stats[1:], 1)
                            if font*.55 <= height <= font*1.6
                            and (field == 'value' or (x > available[0]+available[2]
                                 and abs(y+height/2-available[1]-available[3]/2) < font*.35))]
                if field == 'capacity' and any(right >= mask.shape[1] for _,_,_,right,_ in eligible):
                    continue
                selected = [row for row in eligible if row[1] > 0 and row[3] < mask.shape[1]]
                if not selected:
                    continue
                ids, lefts, tops, rights, bottoms = zip(*selected)
                gx, gy, right, bottom = min(lefts), min(tops), max(rights), max(bottoms)
                glyphs = np.isin(groups[gy:bottom, gx:right], ids).astype(np.uint8)*255
                digits = cv2.cvtColor(glyphs, cv2.COLOR_GRAY2BGR)
                reading = _number(digits, [], (0., 0., 1., 1.), engine, segmented=True)
                if field == 'value':
                    value = reading
                    available = (gx, gy, right-gx, bottom-gy)
                elif reading is not None and reading['value'] >= value['value']:
                    value['capacity'] = reading['value']
        if value is not None:
            resources[key] = {**value, 'source': ('护盾' if key == 'shield' else '希望') + '当前图标对应数值',
                              'icon_score': float(score)}
    return resources
