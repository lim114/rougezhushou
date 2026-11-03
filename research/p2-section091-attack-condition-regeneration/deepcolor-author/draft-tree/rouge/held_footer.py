"""Reconfirm one observed held-footer label without scanning the screen.

Only an exact, low-confidence ``零件箱`` candidate can enter this path.  Its
current OCR geometry must match a held panel established independently by a
complete card and strong ``收起`` / ``干员`` / ``编队`` controls.  One local
recognizer-only call checks that same candidate at the unchanged .9 threshold.
The original OCR list is never mutated and no inventory completeness is inferred.
"""
from copy import deepcopy
import math
import time

import cv2


LABEL = "零件箱"
MINIMUM_CONFIDENCE = .9
CROP_MARGIN_FONTS = .2
OCR_SCALE = 4.


def _bounds(record):
    points = record.get("box") or []
    try:
        if len(points) != 4:
            return None
        xs = [float(point[0]) for point in points]
        ys = [float(point[1]) for point in points]
    except (TypeError, ValueError, IndexError):
        return None
    if not all(math.isfinite(value) and 0 <= value <= 1 for value in xs+ys):
        return None
    result = [min(xs), min(ys), max(xs), max(ys)]
    return result if result[2] > result[0] and result[3] > result[1] else None


def _confidence(record):
    try:
        value = float(record.get("confidence", 0))
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) and 0 <= value <= 1 else None


def reconfirm_held_footer(image, texts, held, cards, engine):
    """Return ``(new_label_or_None, diagnostics)`` for this frame only.

    The caller may replace the one original ``零件箱`` record in a copied text
    list with the returned record.  Use that effective list both for page gating
    and for resource reading; replacing an anchor alone would lose the verified
    label when reading the adjacent parts ratio.  The copied box remains the
    original observed polygon, so viewport remapping is performed only once.
    """
    started = time.perf_counter()
    diagnostic = {"source": "observed_held_footer_local_reconfirm",
                  "label": LABEL, "local_ocr_calls": 0, "confirmed": False}

    def finish(reason, record=None):
        diagnostic["reason"] = reason
        diagnostic["elapsed_ms"] = (time.perf_counter()-started)*1000
        return record, diagnostic

    if image is None or image.ndim != 3 or not image.size:
        return finish("invalid_image")
    if (not held or held.get("text") != "收起"
            or (_confidence(held) or 0) < MINIMUM_CONFIDENCE
            or not any(card.get("confirmed") is True
                       and card.get("source") == "held_name_and_usage"
                       and card.get("id") and len(card.get("candidates", [])) == 1
                       for card in cards)):
        return finish("held_identity_context_missing")
    candidates = [record for record in texts if record.get("text") == LABEL]
    if len(candidates) != 1:
        return finish("label_missing_or_ambiguous")
    candidate = candidates[0]
    confidence = _confidence(candidate)
    if confidence is None or confidence >= MINIMUM_CONFIDENCE:
        return finish("label_invalid_or_already_confirmed")
    controls = []
    for name in ("干员", "编队"):
        records = [record for record in texts if record.get("text") == name
                   and (_confidence(record) or 0) >= MINIMUM_CONFIDENCE]
        if len(records) != 1:
            return finish("strong_controls_missing_or_ambiguous")
        controls.append(records[0])
    ordered = [held, candidate, *controls]
    boxes = [_bounds(record) for record in ordered]
    if not all(boxes):
        return finish("invalid_observed_geometry")
    centers = [((box[0]+box[2])/2, (box[1]+box[3])/2) for box in boxes]
    font = boxes[0][3]-boxes[0][1]
    hx, hy = centers[0]
    if (not hx < centers[1][0] < centers[2][0] < centers[3][0]
            or not all(.5*font <= box[3]-box[1] <= 2*font
                       and abs(center[1]-hy) <= 3*font
                       for box, center in zip(boxes[1:], centers[1:]))):
        return finish("footer_geometry_mismatch")
    h, w = image.shape[:2]
    bx0, by0, bx1, by1 = boxes[1]
    margin = (by1-by0)*h*CROP_MARGIN_FONTS
    crop_rect = [max(0, math.floor(bx0*w-margin)),
                 max(0, math.floor(by0*h-margin)),
                 min(w, math.ceil(bx1*w+margin)),
                 min(h, math.ceil(by1*h+margin))]
    x0, y0, x1, y1 = crop_rect
    crop = image[y0:y1, x0:x1]
    if not crop.size:
        return finish("empty_observed_crop")
    crop = cv2.resize(crop, None, fx=OCR_SCALE, fy=OCR_SCALE,
                      interpolation=cv2.INTER_LINEAR)
    diagnostic["crop_rect"] = crop_rect
    diagnostic["candidate_confidence"] = confidence
    diagnostic["local_ocr_calls"] = 1
    raw, _ = engine(crop, use_det=False, use_cls=False)
    diagnostic["recognized"] = deepcopy(raw)
    if not raw or len(raw) != 1 or len(raw[0]) != 2:
        return finish("local_label_ambiguous")
    name, score = raw[0]
    verified = _confidence({"confidence": score})
    if name != LABEL or verified is None or verified < MINIMUM_CONFIDENCE:
        return finish("local_label_unconfirmed")
    record = deepcopy(candidate)
    record["confidence"] = verified
    record["source"] = diagnostic["source"]
    record["reconfirm"] = {"original_confidence": confidence,
                           "crop": {"box": [[x0/w, y0/h], [x1/w, y0/h],
                                             [x1/w, y1/h], [x0/w, y1/h]]},
                           "threshold": MINIMUM_CONFIDENCE,
                           "recognizer_only": True}
    diagnostic["confirmed"] = True
    return finish("exact_label_reconfirmed", record)
