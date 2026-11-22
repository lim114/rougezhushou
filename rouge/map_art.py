"""Packaged, source-bound map artwork shared by the view and recognition."""
from functools import lru_cache
import json
from pathlib import Path

ART = Path(__file__).with_name('data') / 'map-art'


@lru_cache(maxsize=1)
def art_manifest():
    return json.loads((ART / 'sources.json').read_text(encoding='utf-8'))


@lru_cache(maxsize=1)
def trader_patterns():
    import cv2
    import numpy as np

    sprite = art_manifest()['sprites']['rogue-trader']
    atlas = cv2.imdecode(np.fromfile(ART / 'nodes.png', dtype=np.uint8), cv2.IMREAD_COLOR)
    x, y, w, h = (sprite[key] for key in ('x', 'y', 'width', 'height'))
    # The opaque middle of the emblem is independent of the route, glow and label.
    core = atlas[y + round(h * .375):y + round(h * .625), x + round(w * .375):x + round(w * .625)]
    return tuple(cv2.resize(core, (width, height), interpolation=cv2.INTER_AREA)
                 for width in (60, 64, 56, 68, 52) for height in (54, 58, 50, 62))
