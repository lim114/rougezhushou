"""Freeze the completed303 cache candidate without promoting any file."""
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANDIDATE = HERE / 'candidate'
PACK = CANDIDATE / 'research/p3-map-direct-ground-303'


def pin(path):
    raw = path.read_bytes()
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


receipt_source = HERE / 'build-first/build-receipt.json'
receipt_target = PACK / 'build-receipt.json'
assert not receipt_target.exists()
shutil.copyfile(receipt_source, receipt_target)
assert pin(receipt_source) == pin(receipt_target)
receipt = json.loads(receipt_source.read_bytes())
assert (receipt['new_requested_points'], receipt['new_accepted_points'], receipt['new_rejected_or_unknown_points']) == (89, 49, 40)
root_comparison = ROOT / '.cache/p3-303-root/first-reading-comparison.json'
assert pin(root_comparison)['sha256'] == '28e1f1953607bbff06331bea28674ebab86e3e09f79e07f1080cafdfc4f14683'
raw_root = json.loads(root_comparison.read_bytes())
manifest = json.loads((PACK / 'source-manifest.json').read_bytes())
source_members = [name for name in manifest['files'] if name.startswith('research/p3-map-direct-ground-303/')]
paths = ['rouge/data/fixed-landmark-references.json', 'scripts/extend_direct_landmark_303.py', 'tests/test_direct_landmark_303.py',
         *source_members, 'research/p3-map-direct-ground-303/source-manifest.json',
         'research/p3-map-direct-ground-303/build-receipt.json']
assert len(paths) == len(set(paths)) == 16
promote = {name: pin(CANDIDATE / name) for name in paths}
author = json.loads((HERE / 'author-tests-first/process.json').read_bytes())
assert author['actual_exit'] == 0 and author['source_before_after_equal'] is True
note = {
    'section': 303, 'status': 'CACHE_CANDIDATE_READY_NOT_PROMOTED_OR_PRODUCT_ACCEPTED',
    'candidate_root': str(CANDIDATE.relative_to(ROOT)).replace('\\', '/'),
    'promotion_files': promote,
    'existing_production_files': ['rouge/data/fixed-landmark-references.json'],
    'new_files': 15, 'old_tests_modified_here': False,
    'primary_sources': {'reader_A': pin(PACK / 'READER_A_ORIGINAL.json'), 'reader_B': pin(PACK / 'READER_B_ORIGINAL.json'),
                       'manifest': pin(PACK / 'source-manifest.json'), 'prior58': pin(PACK / 'prior-direct-references.json')},
    'reused_public_authority': {name: value for name, value in manifest['files'].items() if name not in source_members},
    'actual_author_build': {'stdout': '.cache/p3-303-backend/build-first.stdout.log',
                           'stderr': '.cache/p3-303-backend/build-first.stderr.log',
                           'process_exit': '.cache/p3-303-backend/build-first.process.exit',
                           'receipt': '.cache/p3-303-backend/build-first/build-receipt.json',
                           'receipt_pin': pin(receipt_source), 'actual_exit': 0},
    'actual_first_author_checks': {'process': '.cache/p3-303-backend/author-tests-first/process.json',
                                  'process_pin': pin(HERE / 'author-tests-first/process.json'),
                                  'methods': 16, 'actual_exit': 0, 'source_count': author['source_count'],
                                  'source_before_after_equal': True,
                                  'not_formal_product_or_native_acceptance': True},
    'independent_root_comparison': {'path': '.cache/p3-303-root/first-reading-comparison.json',
                                  **pin(root_comparison), 'not_a_data_source': True},
    'actual_build_scope': {key: receipt[key] for key in
       ('new_requested_points', 'new_accepted_points', 'new_rejected_or_unknown_points', 'new_partial_images',
        'new_partial_stage_bindings', 'total_partial_images', 'total_partial_stage_bindings', 'total_partial_points', 'per_image')},
    'all89_original_rows_retained': True, 'source_pixel_adjustments': 0,
    'runtime_parser_unchanged': True, 'supported_surface_unchanged': 'LOWLAND tile_floor or explicitly labelled tile_road',
    'inverse_or_segments': False, 'whole_map_gaps_unchanged': [81, 59],
    'source_rebuild': 'python scripts/extend_direct_landmark_303.py (read-only); --output-dir new-exclusive-dir',
    'source_manifest_files': len(manifest['files']),
    'no_cache_runtime_dependency': True,
    'public_original_reader_cache_paths_are_historical_strings_only': True,
    'root_owned_followup': ['promotion, necessary formal modules, native window, history294/048 fixture maintenance',
                            'docs/checkpoint/requirements/cloud index, ordinary Git publication'],
    'necessary_modules_suggested': ['tests.test_direct_landmark_303', 'tests.test_direct_landmark_294',
                                    'tests.test_direct_landmark_288', 'tests.test_fixed_landmark_mapping', 'tests.test_map_projection_048'],
    'Qt_game_chat_private_Git_or_live_production_operations': False,
}
(HERE / 'HANDOFF.json').write_bytes(encoded(note))
print(json.dumps({'HANDOFF': pin(HERE / 'HANDOFF.json'), 'promotion_files': len(promote),
                  'existing_production_files': 1, 'new_files': 15, 'builder': promote['scripts/extend_direct_landmark_303.py'],
                  'test': promote['tests/test_direct_landmark_303.py'],
                  'data': promote['rouge/data/fixed-landmark-references.json'],
                  'receipt': pin(receipt_target), 'author_actual_exit': 0}, ensure_ascii=False))
