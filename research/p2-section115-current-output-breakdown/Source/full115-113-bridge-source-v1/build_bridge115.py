"""Root-only activation. Author may run --source-audit (stdlib/compile; no project)."""
import argparse
import ast
import hashlib
import json
import shutil
from pathlib import Path
from bridge115 import Bridge, INDICES, METRICS, digest, encoded, require, scalar, validate_leaf

BASIS_SHA256 = '9b1e8d59986f92b76c222b0af8cdd834d4eb23852aedccde8bae3d05f6b5a07e'
BOOTSTRAP_ANCHOR = "OUT.mkdir(parents=True, exist_ok=False)\n"
BOOTSTRAP = '''# BEGIN ROOT115 COMPARISON-ONLY BRIDGE BOOTSTRAP
from importlib.util import spec_from_file_location as _bridge_spec115, module_from_spec as _bridge_module115
_bridge_source115 = Path(__file__).with_name('bridge115.py')
_bridge_map115 = Path(__file__).with_name('expected-map115.json')
_bridge_pins115 = _guard100['full115_113_bridge_sha256']
if set(_bridge_pins115) != {'bridge115.py', 'expected-map115.json'}:
    raise ValueError('Exact comparison bridge Source/map guard required')
for _bridge_file115 in (_bridge_source115, _bridge_map115):
    if _bridge_file115.is_symlink() or hashlib.sha256(_bridge_file115.read_bytes()).hexdigest() != _bridge_pins115[_bridge_file115.name]:
        raise AssertionError('Comparison bridge Source/map drift before project imports')
_bridge_spec_object115 = _bridge_spec115('_root_comparison_bridge115', _bridge_source115)
_bridge_module_object115 = _bridge_module115(_bridge_spec_object115)
_bridge_spec_object115.loader.exec_module(_bridge_module_object115)
_comparison_bridge115 = _bridge_module_object115.Bridge(_bridge_map115, _bridge_pins115['expected-map115.json'], OUT)
# END ROOT115 COMPARISON-ONLY BRIDGE BOOTSTRAP
'''
WRAPPER_ANCHOR = '# END FINAL090 PURE HELPERS\n'
WRAPPER = '''
# BEGIN ROOT115 EXPLICIT COMPARISON WRAPPER
_original_projection115 = projection090
projection090 = _comparison_bridge115.install(_original_projection115, native090,
    lambda: profile_case090, lambda: window.damage_result['scenario'])
# END ROOT115 EXPLICIT COMPARISON WRAPPER
'''


def segment(raw, node):
    return b''.join(raw.splitlines(keepends=True)[node.lineno-1:node.end_lineno])


def protected_try(tree):
    return max((node for node in ast.walk(tree) if isinstance(node, ast.Try)),
               key=lambda node: node.end_lineno-node.lineno)


def assignment(tree, name):
    return next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == name for target in node.targets))


def compose(raw, guard_sha256=None, source_count=None):
    source = raw.decode('utf-8')
    edits = [(BOOTSTRAP_ANCHOR, BOOTSTRAP + BOOTSTRAP_ANCHOR),
             (WRAPPER_ANCHOR, WRAPPER_ANCHOR + WRAPPER)]
    if guard_sha256 is not None:
        edits.extend([('_SOURCE115_GUARD_SHA256 = None',
                       '_SOURCE115_GUARD_SHA256 = ' + repr(guard_sha256)),
                      ('_SOURCE115_MAINTAINED_COUNT = None',
                       '_SOURCE115_MAINTAINED_COUNT = ' + str(source_count))])
    for before, after in edits:
        require(source.count(before) == 1, 'Nonunique Source insertion anchor')
        source = source.replace(before, after)
    candidate = source.encode('utf-8')
    reverse = source
    for before, after in reversed(edits):
        require(reverse.count(after) == 1, 'Nonunique inverse Source anchor')
        reverse = reverse.replace(after, before)
    require(reverse.encode('utf-8') == raw, 'Source transport inverse drift')
    old, new = ast.parse(raw), ast.parse(candidate)
    old_assert = [ast.dump(node, include_attributes=False) for node in ast.walk(old)
                  if isinstance(node, ast.Assert)]
    new_assert = [ast.dump(node, include_attributes=False) for node in ast.walk(new)
                  if isinstance(node, ast.Assert)]
    require(len(old_assert) == 831 and old_assert == new_assert, 'Original Assert AST/order drift')
    old_try, new_try = protected_try(old), protected_try(new)
    require(segment(raw, old_try) == segment(candidate, new_try), 'Whole functional Try byte drift')
    for name in ('rows090', 'saved89_states090', 'expected89_contract090'):
        require(segment(raw, assignment(old, name)) == segment(candidate, assignment(new, name)),
                'Protected literal byte drift: ' + name)
    for name in ('projection090', 'native090'):
        first = next(node for node in old.body if isinstance(node, ast.FunctionDef) and node.name == name)
        second = next(node for node in new.body if isinstance(node, ast.FunctionDef) and node.name == name)
        require(segment(raw, first) == segment(candidate, second), 'Original pure helper byte drift')
    compile(candidate, '<Source-only future115-window>', 'exec')
    return candidate, {'original_831_Assert_AST_order_same': True,
        'whole_functional_Try_byte_same': True, 'functional_Try_bytes': len(segment(raw, old_try)),
        'functional_Try_sha256': hashlib.sha256(segment(raw, old_try)).hexdigest(),
        'three_large_public_literals_byte_same': True, 'original_projection_and_native_helpers_byte_same': True,
        'inverse_transport_byte_same': True, 'added_Assert_nodes': 0,
        'product_numerical_or_formatter_hook_added': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--basis', required=True)
    parser.add_argument('--source-audit', action='store_true')
    parser.add_argument('--admission-map')
    parser.add_argument('--guard')
    parser.add_argument('--out')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    basis = Path(args.basis)
    raw = (basis / 'window.py').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == BASIS_SHA256, 'Exact frozen metadata-only115 basis required')
    for file in ('bridge115.py', 'launcher115.py.in', 'build_bridge115.py'):
        compile((here / file).read_bytes(), str(here / file), 'exec')
    if args.source_audit:
        require(args.admission_map is None and args.guard is None and args.out is None,
                'Source-only audit cannot accept actual mapping/guard/output')
        candidate, check = compose(raw)
        print(json.dumps({'kind': 'SOURCE_ONLY_INACTIVE_BRIDGE115_AUTHOR_CHECK',
            'basis_sha256': BASIS_SHA256, 'candidate_in_memory_bytes': len(candidate),
            'future_guard_and_count_NULL': True, 'future_candidate_numeric_values': None,
            'runtime_executed': False, 'project_or_helper_or_codec_imported': False,
            'product_pass': False, 'ready': False, **check}, ensure_ascii=False))
        return
    require(args.admission_map is not None and args.guard is not None and args.out is not None,
            'Root actual admission/guard/fresh output required')
    map_path, guard_path, out = Path(args.admission_map), Path(args.guard), Path(args.out)
    require(not out.exists(), 'Fresh activation output required')
    map_raw, guard_raw = map_path.read_bytes(), guard_path.read_bytes()
    mapping, guard = json.loads(map_raw), json.loads(guard_raw)
    require(guard['section'] == 115 and type(guard['section']) is int, 'Actual final115 guard required')
    require(type(guard['source_sha256']) is dict and guard['source_sha256'], 'Actual complete Source map required')
    require('CORE_0.70_VERIFICATION.json' in guard['source_additional_sha256'], 'CORE guard required')
    source_pins = {'bridge115.py': hashlib.sha256((here/'bridge115.py').read_bytes()).hexdigest(),
                   'expected-map115.json': hashlib.sha256(map_raw).hexdigest()}
    require(guard['full115_113_bridge_sha256'] == source_pins, 'Guard must qualify exact bridge/map Source')
    require(mapping['old_window_source_sha256'] == BASIS_SHA256, 'Map historical basis mismatch')
    require(mapping['future_actual115_guard_sha256'] is None, 'Use guard-to-map binding; avoid cyclic hashes')
    Bridge(map_path, source_pins['expected-map115.json'], out)  # Stdlib proof validation only.
    rows = ast.literal_eval(assignment(ast.parse(raw), 'rows090').value)
    require(len(rows) == 52, 'Historical public row count changed')
    for admitted in mapping['rows']:
        row = rows[admitted['literal_index']]
        require(digest(row) == admitted['full_source_row_sha256_json_ordered'], 'Historical literal identity mismatch')
        require(digest(row['input']) == admitted['input_sha256_json_ordered'], 'Historical input identity mismatch')
        for name in ('section', 'pair_id', 'widget_checked'):
            require(type(row[name]) is type(admitted[name]) and row[name] == admitted[name], 'Historical identity changed')
        old_skill = row['expected_public_projection']['estimate']['skill']
        for name in METRICS:
            old, new = validate_leaf(admitted['metric_leaf_admission']['estimate.skill.' + name])
            require(encoded(scalar(name in old_skill, old_skill.get(name))) == encoded(old), 'Old metric not literal')
            if name == 'window_seconds':
                require(encoded(scalar(True, row['input']['window_seconds'])) == encoded(new),
                        'Measured new window disagrees with requested window')
    guard_sha = hashlib.sha256(guard_raw).hexdigest()
    candidate, check = compose(raw, guard_sha, len(guard['source_sha256']))
    launcher = (here / 'launcher115.py.in').read_text()
    for before, after in [('WINDOW_SHA256 = None', 'WINDOW_SHA256 = ' + repr(hashlib.sha256(candidate).hexdigest())),
                          ('SOURCE115_GUARD_SHA256 = None', 'SOURCE115_GUARD_SHA256 = ' + repr(guard_sha))]:
        require(launcher.count(before) == 1, 'Launcher activation anchor drift')
        launcher = launcher.replace(before, after)
    compile(launcher, '<Root-activated115-launcher>', 'exec')
    out.mkdir(parents=True, exist_ok=False)
    (out/'window.py').write_bytes(candidate)
    (out/'bridge115.py').write_bytes((here/'bridge115.py').read_bytes())
    (out/'expected-map115.json').write_bytes(map_raw)
    (out/'launcher115.py').write_text(launcher, encoding='utf-8')
    (out/'supervisor115.py').write_bytes((basis/'supervisor115.py').read_bytes())
    for pin in mapping['proof_files'].values():
        destination = out / pin['path']
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(map_path.parent / pin['path'], destination)
    activation = {'kind': 'ROOT_ACTUAL_PROOF_BOUND_FULL115_SOURCE_ACTIVATION',
        'Source_preparation_only': True, 'runtime_executed': False, 'product_pass': False,
        'guard_sha256': guard_sha, 'actual_maintained_Source_count': len(guard['source_sha256']),
        'Root_actual_pair_audit_sha256': mapping['proof_files']['pair_audit']['sha256'],
        'files': [{'path':name,'bytes':(out/name).stat().st_size,
                   'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest()}
                  for name in ('window.py','bridge115.py','expected-map115.json','launcher115.py','supervisor115.py')],
        'scope':'42 unchanged historical projections;10 protected projections with explicit proved113 window-metric exceptions',
        'requires_actual_runtime_then_Root_Saved_and_visual_validation': True, **check}
    (out/'ROOT_SOURCE_ACTIVATION.json').write_text(json.dumps(activation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(activation,ensure_ascii=False))


if __name__ == '__main__':
    main()
