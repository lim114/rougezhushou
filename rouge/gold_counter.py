"""Read the complete single-digit field attached to the current gold icon."""
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

from .anchors import header_span, units
from .operator_recognition import center


HUD_LABELS = ('目标生命值', '指挥等级', '零件箱', '收藏品')
ICON_SCALES = ((.85, 1., 1.15), (.925, 1.075))
ICON_THRESHOLD = .91


@lru_cache(maxsize=1)
def gold_template():
    return cv2.imdecode(np.fromfile(Path(__file__).with_name('data')/'ui-icons/gold-counter.png',dtype=np.uint8),cv2.IMREAD_GRAYSCALE)


def gold_reading(match, numbers, ux, uy):
    score,x,y = match
    values = {value for value,nx,ny in numbers if
              .035*ux < nx-x < .13*ux and abs(ny-y) < .027*uy}
    if len(values) == 1:
        return {'value': next(iter(values)), 'source': '源石锭三角图标右侧数量', 'icon_score': float(score)}
    return None


def digit_shapes(gray):
    """Split bright HUD glyphs at blank columns without resizing their strokes."""
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    columns = np.any(mask, axis=0)
    if columns[0] or columns[-1] or np.any(mask[[0, -1]]):
        return []
    edges = np.flatnonzero(np.diff(columns.astype(np.int8))) + 1
    shapes = []
    for left, right in edges.reshape(-1, 2):
        glyph = mask[:, left:right]
        rows = np.flatnonzero(glyph.any(axis=1))
        top, bottom = rows[0], rows[-1]+1
        shapes.append((left, top, right, bottom, glyph[top:bottom].tobytes()))
    return shapes


def _header_icon(gray, span, scale):
    """Find one physical icon; qualifying placements at all scales must overlap."""
    height, width = gray.shape
    common = None
    best = None
    for factors in ICON_SCALES:
        for factor in factors:
            ref = cv2.resize(gold_template(), None, fx=scale*factor, fy=scale*factor)
            th, tw = ref.shape
            top = max(0, int(np.ceil(span[0]*height - th/2)))
            bottom = min(height, int(np.floor(span[1]*height + th/2)) + 1)
            if bottom-top < th or width < tw:
                continue
            scores = cv2.matchTemplate(gray[top:bottom], ref, cv2.TM_CCOEFF_NORMED)
            _, score, _, (x, y) = cv2.minMaxLoc(scores)
            if score < ICON_THRESHOLD:
                continue
            bx, by, bw, bh = cv2.boundingRect((scores >= ICON_THRESHOLD).astype(np.uint8))
            overlap = (bx+bw-1, top+by+bh-1, bx+tw, top+by+th)
            if common is not None:
                overlap = (max(common[0], overlap[0]), max(common[1], overlap[1]),
                           min(common[2], overlap[2]), min(common[3], overlap[3]))
            if overlap[0] >= overlap[2] or overlap[1] >= overlap[3]:
                return None
            common = overlap
            if best is None or score > best[0]:
                best = (score, x+tw/2, top+y+th/2, tw, th)
    return best


def _visible_plate(image, icon):
    """Bind the current neutral rectangle to the packaged icon's native layout."""
    h, w = image.shape[:2]
    _, cx, cy, tw, th = icon
    left, right = max(0, round(cx+.5*tw)), min(w, round(cx+4.4*tw))
    top, bottom = max(0, round(cy-.65*th)), min(h, round(cy+.95*th))
    area = image[top:bottom, left:right]
    x, y = round(cx+tw)-left, round(cy+.22*th)-top
    if not (0 <= x < right-left and 0 <= y < bottom-top):
        return None
    background = tuple(int(channel) for channel in area[y, x])
    if max(background)-min(background) > 4:
        return None
    # Allow four byte levels of video ringing when locating the flat backing.
    mask = cv2.inRange(area, tuple(max(0, c-4) for c in background),
                       tuple(min(255, c+4) for c in background))
    _, _, _, (x, y, width, height) = cv2.floodFill(mask, None, (x, y), 127)
    if x == 0 or y == 0 or x+width >= right-left or y+height >= bottom-top:
        return None
    x += left
    y += top
    # gold-counter-source.json identifies the native reference: 58x51 icon,
    # 155x36 backing starting 71 px right and 19 px down from its top left.
    scale = height/36
    tolerance = max(1, round(2*scale))
    if (abs(width-155*scale) > tolerance or abs(x-cx-42*scale) > tolerance
            or abs(y-cy+6.5*scale) > tolerance):
        return None
    plate = image[y:y+height, x:x+width]
    return plate, x, y, scale, background


def _matches_counter_glyph(binary, digit):
    """Check the enclosed strokes of the six verified single counter digits."""
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    holes = [cv2.boundingRect(contour) for contour, item in zip(contours, hierarchy[0])
             if item[3] >= 0]
    if digit in '235':
        return not holes
    if digit in '46' and len(holes) == 1:
        _, y, _, height = holes[0]
        center_y = y + height/2
        return center_y < binary.shape[0]/2 if digit == '4' else center_y > binary.shape[0]/2
    if digit == '0' and len(holes) == 2:
        # The slash leaves two side-by-side cavities with overlapping heights.
        left, right = sorted(holes)
        return left[0] < right[0] and max(left[1], right[1]) < min(left[1]+left[3], right[1]+right[3])
    return False


def read_single_gold(image, life_label, engine, *, texts=()):
    """Require a complete plate, one complete glyph and two agreeing .95 reads."""
    h, w = image.shape[:2]
    ux, uy = units(image, life_label, 27.9678)
    icon = _header_icon(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), header_span(life_label), h*uy/1127)
    if icon is None:
        return None
    located = _visible_plate(image, icon)
    if located is None:
        return None
    plate, px, py, scale, background = located
    inner = plate[1:-1, 1:-1]
    # This backing is neutral and its strokes are lighter. A dark occluder
    # can otherwise hide a leading digit while leaving a perfectly legible one.
    gray = cv2.cvtColor(inner, cv2.COLOR_BGR2GRAY)
    background_y = int(cv2.cvtColor(np.uint8([[background]]), cv2.COLOR_BGR2GRAY)[0, 0])
    if int(gray.min()) < background_y-4:
        return None
    shapes = digit_shapes(gray)
    if len(shapes) != 1:
        return None
    l, t, r, b, pixels = shapes[0]
    tolerance = max(1, round(2*scale))
    if (abs(t+1-7*scale) > tolerance or abs(plate.shape[1]-r-1-23*scale) > tolerance
            or abs(b-t-25*scale) > tolerance):
        return None
    binary = np.frombuffer(pixels, np.uint8).reshape(b-t, r-l)
    backdrop = np.ones(gray.shape, dtype=bool)
    margin = max(1, round(2*scale))
    backdrop[max(0, t-margin):b+margin, max(0, l-margin):r+margin] = False
    if ((np.abs(gray[backdrop].astype(np.int16) - background_y) > 4).any()
            or (np.abs(inner[backdrop].astype(np.int16) - background) > 8).any()):
        return None
    if cv2.connectedComponents(binary)[0] != 2:
        return None
    pad_x, pad_y = max(1, round((b-t)*.08)), max(1, round((b-t)*.24))
    digit = None
    for view, color in ((inner[t:b, l:r], background), (cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR), 0)):
        padded = cv2.copyMakeBorder(view, pad_y, pad_y, pad_x, pad_x, cv2.BORDER_CONSTANT, value=color)
        rows, _ = engine(padded, use_det=False, use_cls=False)
        if not rows or len(rows) != 1:
            return None
        value, score = rows[0]
        if len(value) != 1 or value not in '0123456789' or score < .95 or (digit is not None and value != digit):
            return None
        digit = value

    if not _matches_counter_glyph(binary, digit):
        return None

    for row in texts:
        x, y = center(row)
        if (row['confidence'] >= .95 and px <= x*w < px+plate.shape[1]
                and py <= y*h < py+plate.shape[0] and row['text'] != digit):
            return None
    score, cx, cy, _, _ = icon
    nx, ny = (px+1+(l+r)/2)/w, (py+1+(t+b)/2)/h
    return gold_reading((score, cx/w, cy/h), [(int(digit), nx, ny)], ux, uy)
