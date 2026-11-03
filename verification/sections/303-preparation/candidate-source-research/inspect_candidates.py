"""Cache-only metadata decision. No pixel measurements, fits, Qt, state or Git."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IDS = ('ro6_b_6', 'ro6_n_2_3')


def encoded(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def pin(path):
    raw = path.read_bytes()
    return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


def semantic_grid(stage):
    return [[{k: stage['tiles'][i].get(k) for k in ('tileKey', 'heightType', 'buildableType', 'passableMask')}
             for i in row] for row in stage['map']]


names = ('rouge/data/battle-previews.json', 'rouge/data/battle-map-projections.json',
         'rouge/data/fixed-landmark-references.json', 'research/p3-spawn-candidates-299/source-manifest.json',
         'rouge/map_projection.py', 'rouge/fixed_landmark_mapping.py',
         'research/p3-map-direct-checkpoints-294/README.md')
sources = {n: pin(ROOT / n) for n in names}
battle = json.loads((ROOT / names[0]).read_bytes())
stages = battle['stages']
regular = json.loads((ROOT / names[1]).read_bytes())
direct = json.loads((ROOT / names[2]).read_bytes())
levels = json.loads((ROOT / names[3]).read_bytes())
assert len(regular['calibrations']) == 12 and len(regular['stages']) == 24
assert len(direct['references']) == 10 and len(direct['stages']) == 18
assert sum(len(v['points']) for v in direct['references'].values()) == 58
rows = []
for identity in IDS:
    stage = stages[identity]
    assert identity not in regular['stages'] and identity not in direct['stages']
    image_path = 'rouge/data/' + stage['image']['file']
    image_pin = pin(ROOT / image_path)
    assert image_pin == {'sha256': stage['image']['sha256'], 'bytes': stage['image']['bytes']}
    level_path = levels['stage_files'][identity]
    level_pin = pin(ROOT / level_path)
    assert level_pin == {'sha256': stage['level_source']['sha256'], 'bytes': stage['level_source']['bytes']}
    raw_level = json.loads((ROOT / level_path).read_bytes())
    raw_map = raw_level['mapData']
    assert raw_map['map'] == stage['map'] and raw_map['tiles'] == stage['tiles']
    counts = Counter((stage['tiles'][i]['heightType'], stage['tiles'][i]['tileKey']) for r in stage['map'] for i in r)
    grid = semantic_grid(stage)
    grid_sha = sha256(json.dumps(grid, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    aliases = []
    for key, alias in stages.items():
        if alias['level_source']['sha256'] == level_pin['sha256'] and alias['image']['sha256'] == image_pin['sha256']:
            assert semantic_grid(alias) == grid
            aliases.append({'stage_id': key, 'name': alias['name'], 'difficulty': alias['difficulty'],
                            'image': alias['image'], 'level_source': alias['level_source']})
    sources[image_path] = image_pin
    sources[level_path] = level_pin
    rows.append({'stage_id': identity, 'name': stage['name'], 'rows': len(stage['map']), 'cols': len(stage['map'][0]),
                 'image_path': image_path, 'image': stage['image'], 'level_path': level_path,
                 'level_source': stage['level_source'], 'raw_level_top_keys': list(raw_level),
                 'original_mapData': raw_map, 'complete_grid_map': stage['map'], 'complete_tile_metadata': stage['tiles'],
                 'semantic_grid_sha256': grid_sha, 'aliases': aliases,
                 'tile_counts': {h + ':' + key: count for (h, key), count in sorted(counts.items())},
                 'lowland_floor_road_count': sum(count for (h, key), count in counts.items()
                                                if h == 'LOWLAND' and key in ('tile_floor', 'tile_road')),
                 'existing_whole_map_binding': False, 'existing_direct_center_binding': False,
                 'fit_or_pixel_observations_created': False})
report = {'kind': 'TWO_FIXED_MAP_CANDIDATES_METADATA_ONLY_NOT_SECTION303_COMPLETION',
          'at_utc': datetime.now(timezone.utc).isoformat(), 'source_after_section': 302,
          'current_regular_scope': {'images': 12, 'stage_ids': 24},
          'current_partial_direct_scope': {'images': 10, 'stage_ids': 18, 'centers': 58},
          'whole_map_gaps_unchanged': {'stage_ids': len(stages) - len(regular['stages']),
                                      'distinct_images': len({v['image']['sha256'] for v in stages.values()}) - len(regular['calibrations'])},
          'candidates': rows, 'source_pins': sources,
          'pixel_coordinates_or_other_reader_observations_read_or_generated': False,
          'matrix_projection_fit_or_numeric_accuracy_claimed': False,
          'Qt_tests_game_chat_Git_private_or_live_writes': False,
          'scope_decision': 'Prefer normal/urgent 本性难移 for an independently checked ground reference; assess 畸症 conservatively with direct ground centers if occlusion prevents a valid ground plane. No promise either passes.'}
for name, expected in sources.items(): assert pin(ROOT / name) == expected
(HERE / 'candidate-inventory.json').write_bytes(encoded(report))
print(json.dumps({'candidate_inventory_sha256': pin(HERE / 'candidate-inventory.json')['sha256'],
                  'current_scope': report['current_regular_scope'], 'partial_scope': report['current_partial_direct_scope'],
                  'whole_map_gaps_unchanged': report['whole_map_gaps_unchanged'],
                  'candidates': [{k: r[k] for k in ('stage_id', 'name', 'rows', 'cols', 'lowland_floor_road_count', 'level_path', 'image_path')}
                                 | {'aliases': [a['stage_id'] for a in r['aliases']]} for r in rows],
                  'pixel_measurements_or_fits': False}, ensure_ascii=False, indent=2))
