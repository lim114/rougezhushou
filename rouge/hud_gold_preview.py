"""Read the current gold counter before whole-screen OCR on a familiar map HUD."""
import cv2
import numpy as np

from .anchors import header_span, units
from .operator_recognition import center
from .resource_recognition import find_gold_icon, gold_reading


LABELS = ('目标生命值', '指挥等级', '零件箱', '收藏品')


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


def read_gold_preview(image, prior_image, previous, viewport, engine):
    if previous.get('viewport') != viewport:
        return None
    run = previous.get('run') or {}
    gold = run.get('resources', {}).get('gold')
    if run.get('page') != 'run_map' or gold is None:
        return None
    number = str(gold['value'])
    wanted = (*LABELS, number)
    anchors = {}
    amounts = []
    # Previous observations have source-normalized boxes, including any
    # window border. Work entirely inside the current verified content rect.
    source_size = np.array(viewport['source_size'])
    x0, y0, x1, y1 = viewport['content_rect']
    frame = image[y0:y1, x0:x1]
    h, w = frame.shape[:2]
    for text in previous['texts']:
        name = text['text']
        if name not in wanted or text['confidence'] < (.95 if name == number else .9):
            continue
        points = (np.asarray(text['box']) * source_size - (x0, y0)) / (w, h)
        record = {**text, 'box': points.tolist()}
        if name == number:
            amounts.append(record)
        elif name in anchors:
            return None
        else:
            anchors[name] = record
    if len(anchors) != len(LABELS):
        return None
    header = header_span(anchors[LABELS[0]])
    slots = [row for row in amounts if header[0] <= center(row)[1] <= header[1]]
    if len(slots) != 1:
        return None
    amount = slots[0]

    ux, uy = units(frame, anchors[LABELS[0]], 27.9678)
    nx, ny = center(amount)
    icon = find_gold_icon(frame, [(nx, ny)], ux, uy, header=header)
    if icon is None:
        return None

    # Learn shapes from the complete read's actual number, then look across
    # the whole right-aligned four-digit field, including space for width changes.
    prior = prior_image[y0:y1, x0:x1]
    number_box = np.array(amount['box']) * (w, h)
    reading = match_digits(frame, prior, number_box, number, icon[1], ux)
    if reading is None:
        return None
    gold = gold_reading(icon, [reading], ux, uy)
    if gold is None:
        return None

    # These fixed labels must all still be readable in their own positions.
    # Identical label pixels retain the full reader's qualification.
    for name in LABELS:
        points = np.array(anchors[name]['box']) * (w, h)
        left, top = np.floor(points.min(axis=0)).astype(int)
        right, bottom = np.ceil(points.max(axis=0)).astype(int)
        if not (0 <= left < right <= w and 0 <= top < bottom <= h):
            return None
        line = frame[top:bottom, left:right]
        if np.array_equal(line, prior[top:bottom, left:right]):
            continue
        lines, _ = engine(line, use_det=False, use_cls=False)
        if not lines or len(lines) != 1:
            return None
        text, score = lines[0]
        if text.replace(' ', '') != name or score < .9:
            return None
    return gold


def match_digits(frame, prior, number_box, number, icon_x, ux):
    """Decode only complete masks learned from the last verified counter."""
    h, w = frame.shape[:2]
    left, top = np.floor(number_box.min(axis=0)).astype(int)
    right, bottom = np.ceil(number_box.max(axis=0)).astype(int)
    if not (0 <= left < right <= w and 0 <= top < bottom <= h):
        return None
    old_line = cv2.cvtColor(prior[top:bottom, left:right], cv2.COLOR_BGR2GRAY)
    known = digit_shapes(old_line)
    if len(known) != len(number):
        return None
    first_row = min(g[1] for g in known)
    last_row = max(g[3] for g in known)
    glyph_height = last_row - first_row
    end = left + known[-1][2]
    left = end - 5 * glyph_height
    right = end + glyph_height // 3
    bottom = top + last_row + 1
    top += first_row - 1
    if not (0 <= left < right <= w and 0 <= top < bottom <= h):
        return None
    old_field = cv2.cvtColor(prior[top:bottom, left:right], cv2.COLOR_BGR2GRAY)
    field = cv2.cvtColor(frame[top:bottom, left:right], cv2.COLOR_BGR2GRAY)
    # A separated new prefix or suffix can lie outside the old alignment.
    # Include space for up to four digits around every admissible center.
    search_left = max(0, int((icon_x + .035*ux)*w) - 2*glyph_height)
    search_right = min(w, int(np.ceil((icon_x + .13*ux)*w)) + 2*glyph_height)
    threshold, _ = cv2.threshold(old_line, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    for a, b in ((search_left, left), (right, search_right)):
        if a < b:
            before = cv2.cvtColor(prior[top:bottom, a:b], cv2.COLOR_BGR2GRAY)
            now = cv2.cvtColor(frame[top:bottom, a:b], cv2.COLOR_BGR2GRAY)
            if np.any((now > threshold) & (before <= threshold)):
                return None
    current = digit_shapes(field)
    if not 1 <= len(current) <= 4 or left+current[-1][2] != end or field.min() < old_field.min():
        return None
    # Include both dimensions: two flattened masks can have identical bytes.
    alphabet = {}
    for digit, (x, y, u, v, mask) in zip(number, known):
        alphabet.setdefault((u-x, v-y, mask), set()).add(digit)
    digits = []
    for x, y, u, v, mask in current:
        choices = alphabet.get((u-x, v-y, mask), ())
        if len(choices) != 1:
            return None
        digits.append(next(iter(choices)))
    cx = (left + (current[0][0] + current[-1][2]) / 2) / w
    cy = (top + (min(g[1] for g in current) + max(g[3] for g in current)) / 2) / h
    return int(''.join(digits)), cx, cy
