"""Locate held-card counters dynamically, then read only missing numeric glyphs.

No human pixel coordinate or diagnostic crop is accepted as an argument.  The
caller must verify the expanded held panel.  Returned badges have no relic ID;
complete name/usage card geometry is a separate binding check.
"""
from collections import defaultdict
import math
import re
from statistics import median

import cv2
import numpy as np

from .counter_badges import (_polygon, _reference, _shape_score, _white as _frozen_white,
                                  read_counter_badges)
from .held_cards import held_card_regions
from .digit_counters import read_gray_glyph_number


# Additional geometry uses the original train's observed title/counter scale.
# Glyph, color, score and OCR thresholds come unchanged from the frozen model.
GEOMETRY = {"counter_font_per_title_height": .8,
            "digit_gap_fonts": .75, "digit_margin_fonts": .2,
            "ocr_scale": 4., "maximum_digits": 3,
            "prefix_requires_column_titles": 2,
            "prefix_lookback_observed_row_steps": 1.}


def _white(image, settings):
    """Exactly the frozen mask; defer max/min to already-white pixels."""
    if image.dtype != np.uint8 or image.ndim == 2:
        return _frozen_white(image, settings)
    pixels = image[:, :, :3]
    minimum = settings["white_min"]
    mask = cv2.inRange(pixels, (minimum, minimum, minimum), (255, 255, 255)) > 0
    if not np.any(mask):
        return mask
    selected = pixels[mask]
    mask[mask] = (selected.max(axis=1).astype(np.int16)-selected.min(axis=1)
                  <= settings["chroma_max"])
    return mask


def _box(text):
    points = text.get("box") or []
    if not points:
        return None
    return [min(p[0] for p in points), min(p[1] for p in points),
            max(p[0] for p in points), max(p[1] for p in points)]


def dynamic_windows(texts, held):
    """Icon strips plus an observed preceding row when its title was clipped."""
    regions = held_card_regions(texts, held)
    if not any(region["confirmed"] for region in regions):
        return [], regions
    windows = []
    columns = defaultdict(list)
    for region in regions:
        columns[region["column"]].append(region)
        title = region["title_box"]
        windows.append({"bounds": region["icon_bounds"], "title_height": title[3]-title[1],
                        "kind": "named_card", "column": region["column"]})
    for column, cards in columns.items():
        if len(cards) < GEOMETRY["prefix_requires_column_titles"]:
            continue
        cards.sort(key=lambda card: card["title_box"][1])
        first = cards[0]
        title = first["title_box"]
        font = median(card["title_box"][3]-card["title_box"][1] for card in cards)
        step = median(b["title_box"][1]-a["title_box"][1] for a, b in zip(cards, cards[1:]))
        end = title[1] - .5 * font
        start = max(0., title[1] - GEOMETRY["prefix_lookback_observed_row_steps"]*step - .5*font)
        if end <= start or end-start < font:
            continue
        glyph = median((card["title_box"][2]-card["title_box"][0]) / max(len(card["title"]), 1)
                       for card in cards)
        aligned_text = [text for text in texts if text.get("confidence", 0) >= .85
                        and _box(text) and abs(_box(text)[0]-title[0]) <= 1.5*glyph
                        and start <= (_box(text)[1]+_box(text)[3])/2 < end
                        and not re.fullmatch(r"[0-9]+", text.get("text", ""))]
        if not aligned_text:
            continue
        x0, _, x1, _ = first["icon_bounds"]
        windows.append({"bounds": [x0, start, x1, end], "title_height": font,
                        "kind": "preceding_card_without_full_name", "column": column})
    return windows, regions


def locate_glyphs(image, texts, held):
    settings, reference = _reference()
    h, w = image.shape[:2]
    windows, regions = dynamic_windows(texts, held)
    found = {}
    pixels = 0
    for window in windows:
        x0, y0, x1, y1 = window["bounds"]
        x0, y0 = max(0, math.floor(x0*w)), max(0, math.floor(y0*h))
        x1, y1 = min(w, math.ceil(x1*w)), min(h, math.ceil(y1*h))
        roi = image[y0:y1, x0:x1]
        if not roi.size:
            continue
        pixels += roi.shape[0]*roi.shape[1]
        font = window["title_height"] * h * GEOMETRY["counter_font_per_title_height"]
        white = _white(roi, settings).astype(np.uint8)
        _, labels, stats, _ = cv2.connectedComponentsWithStats(white, connectivity=8)
        for label, (cx, cy, cw, ch, area) in enumerate(stats[1:], 1):
            # Same frozen shape/area limits as OCR-anchored glyph validation.
            if (not .32*font <= cw <= 1.15*font or not .35*font <= ch <= font
                    or not .8 <= cw/ch <= 1.35 or area < .04*font*font):
                continue
            score = _shape_score(labels[cy:cy+ch, cx:cx+cw] == label, reference)
            if score < settings["minimum_score"]:
                continue
            rect = (x0+int(cx), y0+int(cy), x0+int(cx+cw), y0+int(cy+ch))
            previous = found.get(rect)
            candidate = {"rect": rect, "score": score, "font": font,
                         "window_kind": window["kind"], "column": window["column"]}
            if previous is None or score > previous["score"]:
                found[rect] = candidate
    return list(found.values()), regions, {"window_count": len(windows), "scanned_pixels": pixels,
                                          "frame_pixels": h*w}


def _digit_ink(image, glyph, settings):
    h, w = image.shape[:2]
    mx0, my0, mx1, my1 = glyph["rect"]
    font = glyph["font"]
    margin = GEOMETRY["digit_margin_fonts"]*font
    x0 = max(0, math.floor(mx1+.08*font))
    x1 = min(w, math.ceil(mx1+(GEOMETRY["maximum_digits"]*.95+.75)*font))
    y0, y1 = max(0, math.floor(my0-margin)), min(h, math.ceil(my1+margin))
    roi = image[y0:y1, x0:x1]
    if not roi.size:
        return None
    _, _, stats, _ = cv2.connectedComponentsWithStats(_white(roi, settings).astype(np.uint8), connectivity=8)
    fragments = sorted((int(s[0]), int(s[1]), int(s[0]+s[2]), int(s[1]+s[3]))
                       for s in stats[1:] if s[4] >= max(3, .006*font*font))
    groups = []
    for fragment in fragments:
        if groups and fragment[0] < groups[-1][2]:
            previous = groups[-1]
            groups[-1] = (previous[0], min(previous[1], fragment[1]),
                          max(previous[2], fragment[2]), max(previous[3], fragment[3]))
        else:
            groups.append(fragment)
    groups = [group for group in groups if group[3]-group[1] >= .25*font]
    run = []
    for group in groups:
        if not run:
            if x0+group[0]-mx1 > GEOMETRY["digit_gap_fonts"]*font:
                return None
        elif group[0]-run[-1][2] > GEOMETRY["digit_gap_fonts"]*font:
            break
        run.append(group)
    if not run or len(run) > GEOMETRY["maximum_digits"]:
        return None
    return (x0+min(g[0] for g in run), y0+min(g[1] for g in run),
            x0+max(g[2] for g in run), y0+max(g[3] for g in run))


def read_local_counter_badges(image, texts, held, engine):
    """Read generic values; only current pixels and inferred dynamic ROIs enter."""
    settings, _ = _reference()
    h, w = image.shape[:2]
    glyphs, regions, performance = locate_glyphs(image, texts, held)
    def marker_key(badge):
        points = badge["marker_box"]
        return (round(points[0][0]*w), round(points[0][1]*h),
                round(points[2][0]*w), round(points[2][1]*h))
    glyph_keys = {glyph["rect"] for glyph in glyphs}
    existing = [badge for badge in read_counter_badges(image, texts)
                if marker_key(badge) in glyph_keys]
    found = list(existing)
    diagnostics = []
    calls = 0
    for glyph in glyphs:
        rect = glyph["rect"]
        if any(marker_key(badge) == rect for badge in existing):
            continue
        ink = _digit_ink(image, glyph, settings)
        detail = {"glyph_rect": list(rect), "glyph_score": glyph["score"],
                  "window_kind": glyph["window_kind"], "ink_rect": list(ink) if ink else None}
        diagnostics.append(detail)
        if ink is None:
            # A compressed frame may preserve the bright marker while its
            # numeric text is gray. Recheck the same marker strictly, then
            # independently read neutral digit ink in this bounded glyph ROI.
            badge, gray_detail = read_gray_glyph_number(image, glyph, engine)
            calls += gray_detail["local_ocr_calls"]
            detail["gray_number"] = gray_detail
            if badge:
                found.append(badge)
            continue
        margin = GEOMETRY["digit_margin_fonts"]*glyph["font"]
        x0, y0, x1, y1 = ink
        crop_rect = [max(0, math.floor(x0-margin)), max(0, math.floor(y0-margin)),
                     min(w, math.ceil(x1+margin)), min(h, math.ceil(y1+margin))]
        lx, ly, rx, ry = crop_rect
        crop = cv2.resize(image[ly:ry, lx:rx], None, fx=GEOMETRY["ocr_scale"],
                          fy=GEOMETRY["ocr_scale"], interpolation=cv2.INTER_LINEAR)
        raw, _ = engine(crop, use_det=False, use_cls=False)
        calls += 1
        detail.update({"crop_rect": crop_rect, "raw": raw})
        if len(raw or []) != 1:
            continue
        value, confidence = raw[0]
        if (not re.fullmatch(r"[0-9]{1,3}", value) or not math.isfinite(confidence)
                or confidence < settings["ocr_min"]):
            continue
        # OCR actually saw this automatically located padded crop.  Its bounds
        # retain the OCR font-height context required by the frozen verifier;
        # the verifier then refines the output back to real digit ink.  A tight
        # ink-only box loses that context after downsampling/rounding.
        record = {"text": value, "confidence": float(confidence), "box": _polygon(crop_rect, w, h)}
        verified = read_counter_badges(image, [record])
        for badge in verified:
            if badge["marker_box"] == _polygon(rect, w, h):
                badge["source"] = "dynamic_held_glyph_local_numeric_ocr"
                found.append(badge)
    performance["local_ocr_calls"] = calls
    return found, regions, performance, diagnostics

