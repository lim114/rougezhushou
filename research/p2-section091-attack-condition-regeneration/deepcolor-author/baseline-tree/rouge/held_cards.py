"""Read complete held-card text using observed two-dimensional typography.

The caller must first verify an expanded *held* panel.  A title and usage on a
reward, shop or account page are not ownership evidence.  This module does not
estimate inventory completeness, recipient assignment or item counters.

Bounds are normalized OCR coordinates.  Icon bounds are a search envelope,
not an icon identification: a counter reader must independently verify its
actual marker and must not bind a crop without a confirmed full card identity.
"""
from functools import lru_cache
import math
import re
from statistics import median

from .catalog import catalog, tactical_tools


def _canonical(value):
    value = re.sub(r"<[^>]*>", "", value)
    return re.sub(r'[\s，,。；;：:“”"（）()]', "", value)


def _bounds(text):
    points = text.get("box") or []
    if len(points) < 4:
        return None
    try:
        xs = [float(point[0]) for point in points]
        ys = [float(point[1]) for point in points]
    except (TypeError, ValueError, IndexError):
        return None
    if not all(math.isfinite(v) for v in xs + ys):
        return None
    box = (min(xs), min(ys), max(xs), max(ys))
    return box if box[2] > box[0] and box[3] > box[1] else None


@lru_cache(maxsize=1)
def _inventory():
    items = {**catalog()["relics"], **tactical_tools()}
    names = {}
    for rid, item in items.items():
        names.setdefault(item["name"], []).append(rid)
    return items, names


def _observed_lines(texts):
    result = []
    for text in texts:
        box = _bounds(text)
        if box is not None and isinstance(text.get("text"), str):
            try:
                confidence = float(text.get("confidence", 0))
            except (TypeError, ValueError):
                continue
            if math.isfinite(confidence):
                result.append({"text": text["text"], "confidence": confidence,
                               "box": box})
    return result


def held_card_regions(texts, held):
    """Return dynamically grouped full-name regions on a verified held panel.

    High-confidence, exact catalog titles establish columns.  A column's next
    title closes the preceding card; discontinuous text closes a body even if
    the next title was unreadable.  This avoids borrowing an unrecognized next
    card's usage.  A single isolated full usage preserves the existing single
    card contract, which does not assume a particular title-to-body distance.

    The 5.5-character icon search envelope covers the actually inspected title
    / icon relationship in the public multirow screenshot and the independent
    native-client three-card screenshot.  It moves/scales with current OCR
    typography and is deliberately not sufficient to confirm a counter.
    """
    held_box = _bounds(held or {})
    if held_box is None or (held or {}).get("text") != "收起":
        return []
    try:
        held_confidence = float(held.get("confidence", 0))
        if not math.isfinite(held_confidence) or held_confidence < .9:
            return []
    except (TypeError, ValueError):
        return []
    items, names = _inventory()
    lines = _observed_lines(texts)
    footer_y = (held_box[1] + held_box[3]) / 2
    titles = [line for line in lines if line["confidence"] >= .9
              and line["text"] in names and line["box"][3] < footer_y]
    if not titles:
        return []

    # Character width comes from the detected title, never from a preset
    # resolution or viewport location.  Grouping tolerates quotes/antialiasing.
    glyph_width = median((line["box"][2] - line["box"][0]) /
                         max(len(line["text"]), 1) for line in titles)
    columns = []
    for title in sorted(titles, key=lambda line: line["box"][0]):
        left = title["box"][0]
        column = next((column for column in columns
                       if abs(left - median(t["box"][0] for t in column))
                       <= 1.5 * glyph_width), None)
        if column is None:
            columns.append([title])
        else:
            column.append(title)
    columns.sort(key=lambda column: median(t["box"][0] for t in column))
    regions = []
    title_ids = {id(title) for title in titles}
    for column_index, column in enumerate(columns):
        column.sort(key=lambda line: (line["box"][1], line["box"][0]))
        left = min(title["box"][0] for title in column)
        right = (min(t["box"][0] for t in columns[column_index + 1])
                 - .5 * glyph_width if column_index + 1 < len(columns) else 1.)
        for row_index, title in enumerate(column):
            title_box = title["box"]
            font = title_box[3] - title_box[1]
            end = (column[row_index + 1]["box"][1] - .2 * font
                   if row_index + 1 < len(column)
                   else footer_y - 2 * (held_box[3] - held_box[1]))
            body_candidates = sorted([
                line for line in lines if id(line) not in title_ids
                and line["confidence"] >= .85
                and left - .75 * glyph_width <= line["box"][0]
                <= min(left + 1.5 * glyph_width, right)
                and title_box[3] - .2 * font <
                (line["box"][1] + line["box"][3]) / 2 < end
            ], key=lambda line: (line["box"][1], line["box"][0]))
            body = []
            for line in body_candidates:
                height = line["box"][3] - line["box"][1]
                if body:
                    prev = body[-1]["box"]
                    # Normal wrapped lines may overlap after OCR detection;
                    # the blank gap between two cards is much larger than a
                    # line.  Never jump over such a gap to finish a usage.
                    if line["box"][1] - prev[3] > .75 * max(height, prev[3]-prev[1]):
                        break
                elif line["box"][1] - title_box[3] > 1.25 * max(font, height):
                    # Legacy single-card callers may supply one whole usage
                    # line far below its title.  Exact full usage is still
                    # required, and multirow columns never take this path.
                    if len(column) != 1 or len(body_candidates) != 1:
                        break
                body.append(line)
            description = "".join(line["text"] for line in body)
            canonical = _canonical(description)
            candidates = [rid for rid in names[title["text"]]
                          if _canonical(items[rid].get("usage") or "")
                          and _canonical(items[rid]["usage"]) in canonical]
            body_end = max([title_box[3]] + [line["box"][3] for line in body])
            own_glyph = (title_box[2] - title_box[0]) / max(len(title["text"]), 1)
            # The counter may sit below the icon/body (real +15 example).
            # Close before the next row when it exists.  No image identity or
            # numeric semantics is inferred by this search envelope.
            icon_end = min(end, body_end + font)
            icon_box = [max(0., title_box[0] - 5.5 * own_glyph),
                        max(0., title_box[1] - .5 * font),
                        max(0., title_box[0] - .3 * own_glyph), icon_end]
            regions.append({
                "title": title["text"], "title_box": list(title_box),
                "column": column_index, "row": row_index,
                "description_text": description,
                "description_line_boxes": [list(line["box"]) for line in body],
                "description_bounds": [left - .75 * glyph_width, title_box[3],
                                       right, body_end],
                "icon_bounds": icon_box,
                "icon_geometry_source": "observed_title_font_search_envelope",
                "candidates": candidates,
                "confirmed": len(candidates) == 1,
            })
    return sorted(regions, key=lambda region: (region["title_box"][1],
                                               region["title_box"][0]))


def read_held_cards(texts, held):
    """Return the existing five-field identity contract, without geometry."""
    return [{"id": region["candidates"][0] if region["confirmed"] else None,
             "candidates": region["candidates"], "confirmed": region["confirmed"],
             "source": "held_name_and_usage", "title": region["title"]}
            for region in held_card_regions(texts, held) if region["candidates"]]
