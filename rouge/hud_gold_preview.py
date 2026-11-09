"""Read a qualified current gold counter before whole-screen OCR."""
import cv2
import numpy as np

from .anchors import header_span, units
from .gold_counter import HUD_LABELS as LABELS, digit_shapes, read_plate_gold
from .operator_recognition import center
from .resource_recognition import find_gold_icon, gold_reading


def _reads_label(engine, line, name):
    rows, _ = engine(line, use_det=False, use_cls=False)
    return bool(rows and len(rows) == 1 and rows[0][0].replace(' ', '') == name and rows[0][1] >= .9)


def read_initial_gold(frame, engine):
    """Locate a candidate HUD from current icon ink, then read its four labels."""
    height, width = frame.shape[:2]
    mask = cv2.inRange(frame, (105, 140, 0), (225, 255, 55))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    location = None
    for contour in contours:
        x, y, ink_width, ink_height = cv2.boundingRect(contour)
        # The cyan part of gold-counter.png spans about 54 x 46 reference
        # pixels. Its right-side inset gives a longer ruler for label crops.
        scale = (width-x)/254
        tolerance = max(1.5, 2*scale)
        if ink_width >= 5 and abs(ink_width-54*scale) <= tolerance and abs(ink_height-46*scale) <= tolerance:
            if location is not None:
                return None
            location = y, scale
    if location is None:
        return None
    y, s = location
    # Reference label extents on the closed HUD. Top labels track icon Y,
    # parts tracks the bottom right corner, and collectibles the bottom left.
    boxes = ((238*s, y+2*s, 349*s, y+30*s), (482*s, y+s, 576*s, y+31*s),
             (width-720*s, height-92*s, width-644*s, height-60*s),
             (198*s, height-53*s, 293*s, height-14*s))
    for name, box in zip(LABELS, boxes):
        left, top, right, bottom = map(round, box)
        if not (0 <= left < right <= width and 0 <= top < bottom <= height):
            return None
        if not _reads_label(engine, frame[top:bottom, left:right], name):
            return None
        if name == '目标生命值':
            life = {'text': name, 'box': [[left/width, top/height], [right/width, top/height],
                                         [right/width, bottom/height], [left/width, bottom/height]]}
    return read_plate_gold(frame, life, engine, include_pairs=True)


def layout_across_partial_hud(previous, current):
    """Keep label locations across one frame where the parts box disappeared."""
    if current.get('run') is not None or previous.get('viewport') != current.get('viewport'):
        return None
    run = previous.get('run') or {}
    if run.get('page') != 'run_map' or run.get('resources', {}).get('gold') is None:
        return None
    visible = {r['text'] for r in current['texts'] if r['text'] in LABELS and r['confidence'] >= .9}
    if visible == set(LABELS) - {'零件箱'}:
        return {'viewport': previous['viewport'], 'texts': [r for r in previous['texts'] if r['text'] in LABELS]}
    return None


def read_gold_preview(image, prior_image, previous, viewport, engine):
    if previous.get('viewport') != viewport:
        return None
    number = None
    if prior_image is not None:
        run = previous.get('run') or {}
        gold = run.get('resources', {}).get('gold')
        if run.get('page') != 'run_map' or gold is None:
            return None
        number = str(gold['value'])
    wanted = LABELS if number is None else (*LABELS, number)
    anchors = {}
    amounts = []
    # Previous observations have source-normalized boxes, including any
    # window border. Work entirely inside the current verified content rect.
    source_size = np.array(viewport['source_size'])
    x0, y0, x1, y1 = viewport['content_rect']
    prior = None if prior_image is None else prior_image[y0:y1, x0:x1]
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
    gold = None
    # Only learn old digit masks from an unambiguous prior text box. The
    # current plate reader locates its own icon and never uses those boxes.
    if len(slots) == 1:
        amount = slots[0]
        ux, uy = units(frame, anchors[LABELS[0]], 27.9678)
        nx, ny = center(amount)
        icon = find_gold_icon(frame, [(nx, ny)], ux, uy, header=header)
        if icon is not None:
            number_box = np.array(amount['box']) * (w, h)
            reading = match_digits(frame, prior, number_box, number, icon[1], ux)
            if reading is not None:
                gold = gold_reading(icon, [reading], ux, uy)
    if gold is None:
        gold = read_plate_gold(frame, anchors[LABELS[0]], engine, include_pairs=True)
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
        if prior is not None and np.array_equal(line, prior[top:bottom, left:right]):
            continue
        if not _reads_label(engine, line, name):
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
