from pathlib import Path
import ast, hashlib, json, sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.battle_preview import battle_data
from rouge.map_projection import projection_data, projection_for
from rouge.fixed_landmark_mapping import landmark_data
from rouge.map_reporting import format_node
from tests.test_readable_map_047 import graph

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def functions(path):
    return {x.name: ast.dump(x, include_attributes=False)
            for x in ast.parse(path.read_text(encoding='utf8')).body
            if isinstance(x, ast.FunctionDef)}

manifest = json.loads((ROOT / 'research/presentation-source-guard/source-manifest.json').read_text(encoding='utf8'))
pre047 = []
for name, expected in manifest['pre047_original_required_sha256'].items():
    path = ROOT / '.cache/batch-047-before' / name
    pre047.append({'path': path.relative_to(ROOT).as_posix(), 'exists': path.is_file(),
                  'actual_sha256': sha(path) if path.is_file() else None,
                  'required_sha256': expected, 'exact_original_matches': path.is_file() and sha(path) == expected})
current_guard = []
for row in manifest['functions']:
    path = ROOT / 'research/presentation-source-guard' / row['archive_path']
    before = functions(path)[row['function']]
    after = functions(ROOT / row['source_path'])[row['function']]
    current_guard.append({'source': row['source_path'], 'function': row['function'], 'scope': row['scope'],
                          'manifest_ast_matches': hashlib.sha256(before.encode()).hexdigest() == row['target_ast_sha256'],
                          'current_ast_matches_approved_original': after == before})
old060 = ROOT / '.cache/research/river-effects-060/integration-before.json'
original060 = {'path': old060.relative_to(ROOT).as_posix(), 'exists': old060.is_file(),
               'actual_sha256': sha(old060) if old060.is_file() else None,
               'required_sha256': '66e5babd5d88eeef681472958780822e6717617c1b403dbe1bdf75e1fc6e0326'}
original060['exact_original_matches'] = original060['actual_sha256'] == original060['required_sha256']
if old060.is_file():
    original060['case_names'] = list(json.loads(old060.read_text(encoding='utf8'))['cases'])

probes = []
for batch, names in [('048', ('ro6_n_2_3', 'ro6_n_2_4', 'ro6_t_1', 'ro6_n_3_5')),
                     ('049', None)]:
    base = ROOT / '.cache/research' / ('map-projection-' + batch)
    if names is None:
        records = json.loads((base / 'calibration-input.json').read_text(encoding='utf8'))['rejected_probes']
        probe_paths = [ROOT / rec['file'] for rec in records]
    else:
        probe_paths = [base / (sid + '-fit.json') for sid in names]
    for probe_path in probe_paths:
        raw = json.loads(probe_path.read_text(encoding='utf8'))
        sid = raw['input']['id']
        stage = battle_data()['stages'][sid]
        image = stage['image']
        args = (stage, image['sha256'], (image['width'], image['height']))
        actual = projection_for(*args)
        with patch('rouge.fixed_landmark_mapping.direct_reference_for', return_value=None):
            regular_only = projection_for(*args)
        binding = landmark_data()['stages'].get(sid)
        probes.append({'batch': batch, 'stage': sid, 'probe_path': probe_path.relative_to(ROOT).as_posix(),
                       'probe_sha256': sha(probe_path), 'original_rejected': not raw['accepted'],
                       'original_max_error_px': max(c['error_px'] for c in raw['checks']),
                       'regular_binding_absent': sid not in projection_data()['stages'],
                       'regular_projection_remains_none': regular_only is None,
                       'current_mapping_type': type(actual).__name__ if actual else None,
                       'direct_reference_binding': binding,
                       'current_direct_points': len(actual.points) if actual and hasattr(actual, 'points') else None,
                       'supports_segment_reference': getattr(actual, 'supports_segment_reference', None),
                       'inverse_mapping_none': actual is None or actual.cell_at(100, 100) is None})

default = format_node(graph(), '2,3')
diagnostic = format_node(graph(), '2,3', include_historical_route_diagnostics=True)
output = {
    'kind': 'READONLY_HISTORICAL_CONTRACT_AND_CURRENT_MAPPING_TRIAGE',
    'production_or_tests_modified': False, 'runtime_state_read': False,
    'original_pre047_sources': pre047, 'approved_current_047_ast_guard': current_guard,
    'original_060_archive': original060, 'map_projection_rejected_probe_controls': probes,
    'node_scope': {'default': default, 'explicit_historical_diagnostic': diagnostic,
                   'default_old_route_sentence_absent': '不是从当前位置出发' not in default,
                   'historical_old_route_sentence_retained': '不是从当前位置出发' in diagnostic,
                   'default_adjacency_information_present': '【模板相邻节点】' in default,
                   'default_no_automatic_selection_boundary_present': '不自动选路' in default},
}
path = ROOT / '.cache/full275-regression-triage-readonly.json'
with path.open('x', encoding='utf8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(json.dumps({'receipt': path.as_posix(), 'original_pre047_exact': [x['exact_original_matches'] for x in pre047],
                  'original060_exact': original060['exact_original_matches'],
                  'current_guard_16_pass': all(x['manifest_ast_matches'] and x['current_ast_matches_approved_original'] for x in current_guard),
                  'regular_rejections_all_preserved': all(x['regular_projection_remains_none'] for x in probes),
                  'direct_coverage': [(x['stage'], x['current_mapping_type'], x['current_direct_points']) for x in probes]}, ensure_ascii=False))
