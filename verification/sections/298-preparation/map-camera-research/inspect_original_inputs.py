"""Bounded static JSON/index inventory; does not fit points or load game code."""
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
pins = {}


def read(relative):
    path = ROOT / relative
    blob = path.read_bytes()
    pins[relative] = {'sha256': sha256(blob).hexdigest(), 'bytes': len(blob)}
    return json.loads(blob)


old = read('.cache/research/map-projection-044/evidence.json')
index = read('.cache/research/p2-native-current-263/script.json')['ScriptMethod']
regex = re.compile(r'MapPreview|MapReview|StagePreview|LevelPreview|PreviewMap|CameraController|VCamera|StageCamera|MapCamera|CameraData|CameraConfig|MapConfig|TilePos|GridToWorld|WorldToGrid|TileToWorld|ToWorldPos|WorldToScreen|MapGrid|CreateMapReview|RenderMap', re.I)
methods = [row for row in index if regex.search(row['Name']) and row['Name'].startswith(('Torappu.', 'UnityEngine.Camera$$'))]
readme = ROOT / '.cache/research/map-projection-044/resource-readme.md'
raw = readme.read_bytes()
pins[readme.relative_to(ROOT).as_posix()] = {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
maps = read('.cache/research/map-projection-044/resource-maps.json')
summary = read('.cache/research/map-projection-044/resource-summary.json')
data = read('rouge/data/battle-previews.json')
stages = data['stages']
stage_sample = list(stages.items())[:1] if type(stages) is dict else stages[:1]
level_rows = []
for path in sorted((ROOT / '.cache/game-data/levels/obt/roguelike/ro6').glob('*.json')):
    relative = path.relative_to(ROOT).as_posix()
    obj = read(relative)
    camera = {key: value for key, value in obj.items() if re.search('camera|view|projection', key, re.I)}
    md = obj.get('mapData', {})
    camera_map = {key: value for key, value in md.items() if re.search('camera|view|projection', key, re.I)}
    level_rows.append({'file': relative, 'top_keys': list(obj), 'camera_fields': camera,
        'mapData_camera_fields': camera_map, 'mapData_keys': list(md),
        'map_rows': len(md.get('map', [])), 'map_cols': len(md.get('map', [[]])[0]),
        'tile_count': len(md.get('tiles', []))})
native = {'kind': 'STATIC_NAME_INDEX_CANDIDATES_NOT_EXECUTION_EVIDENCE',
    'index_methods_total': len(index), 'matched': len(methods), 'methods': methods,
    'method_name_does_not_prove_preview_capture_path': True}
(OUT / 'native-name-candidates.json').write_bytes((json.dumps(native, ensure_ascii=False, indent=2)+'\n').encode())
result = {'kind': 'SECTION298_ORIGINAL_JSON_STATIC_INVENTORY_NOT_CALIBRATION',
    'level_count': len(level_rows), 'levels': level_rows, 'preview_top_keys': list(data),
    'sample_stage': stage_sample,
    'resource_maps_kind': type(maps).__name__, 'resource_maps_sample': list(maps.items())[:2] if type(maps) is dict else maps[:2],
    'resource_summary_kind': type(summary).__name__, 'resource_summary_sample': list(summary.items())[:2] if type(summary) is dict else summary[:2],
    'old_camera_remaining_unknown': old['remaining_unknown'], 'native_index_candidate_count': len(methods),
    'source_pins': pins, 'new_fit_executed': False, 'game_or_process_access': False,
    'Qt_or_test_execution': False, 'production_or_Git_changed': False}
(OUT / 'original-input-inventory.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2)+'\n').encode())
print(json.dumps({'original_ro6_levels': len(level_rows), 'native_name_candidates': len(methods),
    'first_stage_shape': type(stage_sample).__name__, 'resource_maps_kind': type(maps).__name__,
    'resource_summary_kind': type(summary).__name__, 'source_pin_count': len(pins),
    'level_camera_field_variants': sorted({json.dumps(r['camera_fields'], sort_keys=True) for r in level_rows})}, ensure_ascii=False))
