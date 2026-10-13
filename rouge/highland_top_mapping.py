"""Separate nominal upper surfaces; never ground, footpoints or spawn positions."""
from dataclasses import dataclass
from functools import lru_cache
import json
import math
from pathlib import Path

from .map_projection import grid_digest

DATA = Path(__file__).parent / "data"

@lru_cache(maxsize=1)
def highland_top_data():
    return json.loads((DATA / "highland-top-references.json").read_text(encoding="utf-8"))


def _pixel(value):
    return (isinstance(value, list) and len(value) == 2 and
            all(type(v) in (int, float) and math.isfinite(v) for v in value))


@dataclass(frozen=True)
class HighlandTopReference:
    points: tuple
    rows: int
    cols: int
    width: int
    height: int
    mapping_kind: str = 'highland_nominal_top_center'
    supports_segment_reference: bool = False
    supports_inverse_reference: bool = False
    supports_spawn_reference: bool = False

    def top_center(self, cell):
        """Read one explicitly observed integer cell; no projected intermediates."""
        if not isinstance(cell, dict):
            return None
        row, col = cell.get('row'), cell.get('col')
        if type(row) is not int or type(col) is not int:
            return None
        for r, c, x, y in self.points:
            if (row, col) == (r, c):
                return x, y
        return None


def highland_top_reference_for(stage, image_sha256, image_size, data=None):
    """Validate a separate surface schema without touching LOWLAND references."""
    if data is None:
        data = highland_top_data()
    if (not isinstance(data, dict) or type(data.get('format_version')) is not int or data.get('format_version') != 1 or
            data.get('reference_kind') != 'highland_nominal_top_center' or
            data.get('absolute_position_accuracy_verified') is not False):
        return None
    binding = data.get('stages', {}).get(stage['id'])
    if not binding:
        return None
    record = data.get('references', {}).get(binding.get('reference'))
    if not record:
        return None
    image = stage['image']
    if (record.get('surface_kind') != 'highland_nominal_top_center' or
            record.get('tile_kind') != 'tile_wall' or record.get('height_type') != 'HIGHLAND' or
            record.get('agreement_tolerance_px') != 4):
        return None
    if (binding.get('image_file') != image['file'] or
            binding.get('level_sha256') != stage['level_source']['sha256'] or
            image_sha256 != image['sha256'] or image_sha256 != record.get('bitmap_sha256') or
            tuple(image_size) != (record['width'], record['height']) or
            (image['width'], image['height']) != tuple(image_size) or
            (len(stage['map']), len(stage['map'][0])) != (record['rows'], record['cols']) or
            grid_digest(stage) != record.get('grid_sha256')):
        return None
    points, seen = [], set()
    for point in record.get('points', []):
        row, col = point.get('row'), point.get('col')
        one, two = point.get('observed_pixel'), point.get('independent_pixel')
        if (type(row) is not int or type(col) is not int or not _pixel(one) or not _pixel(two) or
                not 0 <= row < record['rows'] or not 0 <= col < record['cols'] or
                (row, col) in seen or math.dist(one, two) > 4):
            return None
        if not all(0 <= pixel[0] < record['width'] and 0 <= pixel[1] < record['height'] for pixel in (one, two)):
            return None
        tile = stage['tiles'][stage['map'][row][col]]
        if tile['tileKey'] != 'tile_wall' or tile['heightType'] != 'HIGHLAND':
            return None
        seen.add((row, col)); points.append((row, col, *one))
    if not points:
        return None
    return HighlandTopReference(tuple(points), record['rows'], record['cols'], record['width'], record['height'])
