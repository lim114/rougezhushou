"""Only independently read bitmap ground centers; no plane, inverse, or path."""
import json
import math
from dataclasses import dataclass
from functools import lru_cache
from numbers import Real
from pathlib import Path

DATA = Path(__file__).parent / 'data'


def finite(value):
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


@lru_cache(maxsize=1)
def landmark_data():
    return json.loads((DATA / 'fixed-landmark-references.json').read_text(encoding='utf-8'))


@dataclass(frozen=True)
class FixedLandmarkReference:
    points: tuple
    rows: int
    cols: int
    width: int
    height: int
    agreement_tolerance_px: float
    mapping_mode: str = 'direct_verified_centers'
    supports_segment_reference: bool = False

    def project(self, cell):
        if not isinstance(cell, dict):
            return None
        row, col = cell.get('row'), cell.get('col')
        if not finite(row) or not finite(col) or int(row) != row or int(col) != col:
            return None
        for r, c, x, y in self.points:
            if (row, col) == (r, c):
                return x, y
        return None

    def cell_at(self, x, y):
        # A handful of center observations cannot establish pixel boundaries.
        # Even a point very near a landmark must not infer a logical cell.
        return None


def direct_reference_for(stage, image_sha256, image_size):
    from .map_projection import grid_digest
    data = landmark_data()
    binding = data['stages'].get(stage['id'])
    if not binding:
        return None
    record = data['references'][binding['reference']]
    image = stage['image']
    if binding['level_sha256'] != stage['level_source']['sha256']:
        return None
    if binding['image_file'] != image['file']:
        return None
    if image_sha256 != image['sha256'] or image_sha256 != record['bitmap_sha256']:
        return None
    if tuple(image_size) != (record['width'], record['height']):
        return None
    if (image['width'], image['height']) != tuple(image_size):
        return None
    if (len(stage['map']), len(stage['map'][0])) != (record['rows'], record['cols']):
        return None
    if grid_digest(stage) != record['grid_sha256'] or record['agreement_tolerance_px'] != 4:
        return None
    points, seen = [], set()
    for point in record['points']:
        row, col = point['row'], point['col']
        pixel, peer = point['observed_pixel'], point['independent_pixel']
        if not all(finite(v) for v in (row, col, *pixel, *peer)):
            return None
        if int(row) != row or int(col) != col or not (0 <= row < record['rows'] and 0 <= col < record['cols']):
            return None
        if (row, col) in seen or not (0 <= pixel[0] < record['width'] and 0 <= pixel[1] < record['height']):
            return None
        if not (0 <= peer[0] < record['width'] and 0 <= peer[1] < record['height']):
            return None
        if math.dist(pixel, peer) > 4:
            return None
        tile = stage['tiles'][stage['map'][row][col]]
        if tile['tileKey'] != 'tile_floor' or tile['heightType'] != 'LOWLAND':
            return None
        seen.add((row, col)); points.append((row, col, *pixel))
    if not points:
        return None
    return FixedLandmarkReference(tuple(points), record['rows'], record['cols'],
        record['width'], record['height'], record['agreement_tolerance_px'])
