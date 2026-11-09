"""Read the complete amount field attached to the current gold icon."""
from functools import lru_cache
from math import ceil
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
    if abs(width-155*scale) > tolerance:
        # Losing one pixel from the 36 px edge moves the predicted far edge
        # by over four pixels. Check the longer ruler against the icon itself.
        scale = width/155
        if abs(height-36*scale) > 1 or abs(tw-58*scale) > 1:
            return None
        tolerance = ceil(2*scale)
    if abs(x-cx-42*scale) > tolerance or abs(y-cy+6.5*scale) > tolerance:
        return None
    plate = image[y:y+height, x:x+width]
    return plate, x, y, scale, background


def _matches_counter_glyph(binary, digit):
    """Check enclosed strokes in the verified counter font."""
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    holes = [cv2.boundingRect(contour) for contour, item in zip(contours, hierarchy[0])
             if item[3] >= 0]
    if digit in '1235':
        return not holes
    if digit in '46' and len(holes) == 1:
        _, y, _, height = holes[0]
        center_y = y + height/2
        return center_y < binary.shape[0]/2 if digit == '4' else center_y > binary.shape[0]/2
    if digit == '0' and len(holes) == 2:
        # The slash leaves two side-by-side cavities with overlapping heights.
        left, right = sorted(holes)
        return left[0] < right[0] and max(left[1], right[1]) < min(left[1]+left[3], right[1]+right[3])
    if digit == '8' and len(holes) == 2:
        upper, lower = sorted(holes, key=lambda rect: rect[1])
        # Contour boxes include the one-pixel ink boundary of each cavity.
        return upper[1] + upper[3] - 1 <= lower[1] + 1
    return False


def _upright_digits(engine, crop, background, length):
    height = crop.shape[0]
    pad_x, pad_y = max(1, round(height*.08)), max(1, round(height*.24))
    padded = cv2.copyMakeBorder(crop, pad_y, pad_y, pad_x, pad_x, cv2.BORDER_CONSTANT, value=background)
    rows, _ = engine(padded, use_det=False, use_cls=False)
    if rows and len(rows) == 1:
        value, score = rows[0]
        if len(value) == length and value.isascii() and value.isdigit() and score >= .95:
            return value
    return None


def read_plate_gold(image, life_label, engine, *, texts=(), include_pairs=False):
    """Read the natural amount together and check each segmented glyph separately."""
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
    if len(shapes) != 1 and not (include_pairs and len(shapes) == 2):
        return None
    tolerance = ceil(2*scale)
    right = shapes[-1][2]
    if abs(plate.shape[1]-right-1-23*scale) > tolerance:
        return None
    if len(shapes) == 2:
        # Fixed-pitch centers stay 19 native pixels apart, including narrow '1'.
        tens, ones = shapes
        pitch = (ones[0]+ones[2]-tens[0]-tens[2])/2
        if abs(pitch - 19*scale) > tolerance:
            return None
    backdrop = np.ones(gray.shape, dtype=bool)
    masks = []
    for l, t, r, b, pixels in shapes:
        if abs(t+1-7*scale) > tolerance or abs(b-t-25*scale) > tolerance:
            return None
        binary = np.frombuffer(pixels, np.uint8).reshape(b-t, r-l)
        if cv2.connectedComponents(binary)[0] != 2:
            return None
        masks.append(binary)
        backdrop[max(0, t-tolerance):b+tolerance, max(0, l-tolerance):r+tolerance] = False
    if (np.abs(gray[backdrop].astype(np.int16) - background_y) > 4).any():
        return None
    if len(shapes) == 2:
        # Green icon chroma bleeds into the leftmost backing column in video.
        # Its luminance was checked above; both glyph cells are farther right.
        backdrop[:, 0] = False
    if (np.abs(inner[backdrop].astype(np.int16) - background) > 8).any():
        return None
    left = shapes[0][0]
    top = min(s[1] for s in shapes)
    bottom = max(s[3] for s in shapes)
    amount = _upright_digits(engine, inner[top:bottom, left:right], background, len(shapes))
    if amount is None or (len(amount) == 2 and amount.startswith('0')):
        return None
    supported = '023456' if len(amount) == 1 else '01238'
    for digit, binary in zip(amount, masks):
        ocr_mask = binary
        if binary.shape[0] < 25:
            ratio = 25/binary.shape[0]
            ocr_mask = cv2.resize(binary, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_LINEAR)
        value = _upright_digits(engine, cv2.cvtColor(ocr_mask, cv2.COLOR_GRAY2BGR), 0, 1)
        if value != digit or digit not in supported or not _matches_counter_glyph(binary, digit):
            return None
        if len(amount) == 2:
            height, width = binary.shape
            if abs(width - (11 if digit == '1' else 17)*scale) > tolerance:
                return None
            # An erased left loop turns 8 into an OCR-confident 3. The
            # printed 3 has an inward diagonal across its upper third.
            if digit == '3':
                stroke = np.flatnonzero(binary[height//3])
                if not len(stroke) or stroke[0] < width//4 or stroke[-1] >= width-width//4:
                    return None

    for row in texts:
        x, y = center(row)
        if (row['confidence'] >= .95 and px <= x*w < px+plate.shape[1]
                and py <= y*h < py+plate.shape[0] and row['text'] != amount):
            return None
    score, cx, cy, _, _ = icon
    nx, ny = (px+1+(left+right)/2)/w, (py+1+(top+bottom)/2)/h
    return gold_reading((score, cx/w, cy/h), [(int(amount), nx, ny)], ux, uy)


# Existing complete-observation callers use the single-digit default.
read_single_gold = read_plate_gold
