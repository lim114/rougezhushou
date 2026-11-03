"""Retain strict marker pixels and read adjacent gray number ink separately."""
import math
import re

import cv2
import numpy as np

from .counter_badges import _polygon, _reference, _shape_score, _white


RULES = {"maximum_digits": 3, "roi_character_width_fonts": .95,
         "digit_gap_fonts": .75, "digit_margin_fonts": .2,
         "start_gap_fonts": .08, "minimum_digit_height_fonts": .25,
         "minimum_component_area_fonts_squared": .006,
         "maximum_baseline_difference_fonts": .25, "ocr_scale": 4.}


def read_gray_glyph_number(image, glyph, engine):
    """Read one number only after independently rechecking its actual marker.

    Otsu splits this bounded number ROI's two brightness classes; it does not
    change the marker's white color mask, template or score threshold.  Only
    near-neutral component ink in the expected line is retained.  The recognizer
    must return exactly one integer at the original >=.95 confidence threshold,
    and its character count, width, baseline and gap must match the real ink.
    """
    settings, reference = _reference()
    h, w = image.shape[:2]
    diagnostic = {"source": "dynamic_held_glyph_gray_numeric_ocr", "local_ocr_calls": 0}
    try:
        mx0, my0, mx1, my1 = glyph["rect"]
        font = float(glyph["font"])
    except (KeyError, TypeError, ValueError):
        return None, {**diagnostic, "reason": "invalid_glyph"}
    if (not math.isfinite(font) or font <= 0 or not 0 <= mx0 < mx1 <= w
            or not 0 <= my0 < my1 <= h):
        return None, {**diagnostic, "reason": "invalid_glyph"}
    marker = _white(image[my0:my1, mx0:mx1], settings)
    score = _shape_score(marker, reference)
    if (score < settings["minimum_score"] or
            not .32*font <= mx1-mx0 <= 1.15*font or
            not .35*font <= my1-my0 <= font or
            not .8 <= (mx1-mx0)/(my1-my0) <= 1.35 or
            marker.sum() < .04*font*font):
        return None, {**diagnostic, "reason": "strict_marker_unconfirmed", "marker_score": score}
    margin = RULES["digit_margin_fonts"]*font
    # Round away from the marker: flooring a subpixel gap admits its gray
    # antialiasing halo as an extra digit component at small font sizes.
    x0 = max(0, math.ceil(mx1+RULES["start_gap_fonts"]*font))
    x1 = min(w, math.ceil(mx1+(RULES["maximum_digits"]*RULES["roi_character_width_fonts"]+
                            RULES["digit_gap_fonts"])*font))
    y0 = max(0, math.floor(my0-margin))
    y1 = min(h, math.ceil(my1+margin))
    roi = image[y0:y1, x0:x1]
    if not roi.size:
        return None, {**diagnostic, "reason": "empty_digit_roi"}
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if roi.ndim == 3 else roi
    threshold, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    if roi.ndim == 3:
        pixels = roi[:, :, :3].astype(np.int16)
        mask[pixels.max(axis=2)-pixels.min(axis=2) > settings["chroma_max"]] = 0
    _, _, stats, _ = cv2.connectedComponentsWithStats((mask > 0).astype(np.uint8), connectivity=8)
    fragments = sorted((int(s[0]), int(s[1]), int(s[0]+s[2]), int(s[1]+s[3]))
                       for s in stats[1:] if s[4] >= max(3, RULES["minimum_component_area_fonts_squared"]*font*font))
    groups = []
    for fragment in fragments:
        if groups and fragment[0] < groups[-1][2]:
            old = groups[-1]
            groups[-1] = (old[0], min(old[1], fragment[1]), max(old[2], fragment[2]), max(old[3], fragment[3]))
        else:
            groups.append(fragment)
    groups = [group for group in groups if group[3]-group[1] >= RULES["minimum_digit_height_fonts"]*font]
    run = []
    for group in groups:
        if not run:
            if x0+group[0]-mx1 > RULES["digit_gap_fonts"]*font:
                return None, {**diagnostic, "reason": "digit_too_far", "otsu_threshold": threshold}
        elif group[0]-run[-1][2] > RULES["digit_gap_fonts"]*font:
            break
        run.append(group)
    if not run or len(run) > RULES["maximum_digits"]:
        return None, {**diagnostic, "reason": "digit_ink_unconfirmed", "otsu_threshold": threshold, "groups": groups}
    bx0, by0 = x0+min(g[0] for g in run), y0+min(g[1] for g in run)
    bx1, by1 = x0+max(g[2] for g in run), y0+max(g[3] for g in run)
    if (not 0 <= bx0-mx1 <= RULES["digit_gap_fonts"]*font
            or abs((my0+my1-by0-by1)/2) > RULES["maximum_baseline_difference_fonts"]*font
            or bx1-bx0 > len(run)*RULES["roi_character_width_fonts"]*font):
        return None, {**diagnostic, "reason": "digit_geometry_mismatch", "otsu_threshold": threshold}
    crop_rect = [max(0, math.floor(bx0-margin)), max(0, math.floor(by0-margin)),
                 min(w, math.ceil(bx1+margin)), min(h, math.ceil(by1+margin))]
    lx, ly, rx, ry = crop_rect
    crop = cv2.resize(image[ly:ry, lx:rx], None, fx=RULES["ocr_scale"], fy=RULES["ocr_scale"],
                      interpolation=cv2.INTER_LINEAR)
    raw, _ = engine(crop, use_det=False, use_cls=False)
    diagnostic.update({"local_ocr_calls": 1, "crop_rect": crop_rect, "ink_rect": [bx0, by0, bx1, by1],
                       "otsu_threshold": threshold, "raw": raw, "marker_score": score})
    if not raw or len(raw) != 1 or len(raw[0]) != 2:
        return None, {**diagnostic, "reason": "numeric_ocr_ambiguous"}
    value, confidence = raw[0]
    if (not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,3}", value)
            or not math.isfinite(confidence) or confidence < settings["ocr_min"]
            or len(value) != len(run)):
        return None, {**diagnostic, "reason": "numeric_ocr_unconfirmed"}
    badge = {"value": int(value), "box": _polygon((bx0, by0, bx1, by1), w, h),
             "marker_box": _polygon((mx0, my0, mx1, my1), w, h), "score": score,
             "confidence": float(confidence), "source": diagnostic["source"]}
    return badge, {**diagnostic, "reason": "verified_gray_number"}
