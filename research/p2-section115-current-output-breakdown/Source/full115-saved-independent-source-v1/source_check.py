"""Independent Source-only checks. No target module is imported or executed."""
import ast
import datetime
import hashlib
import json
from pathlib import Path

BASE = Path('/workspace/.continuation')
DEST = Path(__file__).parent

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def pin(path):
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}

def packed(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode()

def span(raw, node):
    lines = raw.splitlines(keepends=True)
    return (lines[node.lineno-1][node.col_offset:] + b''.join(lines[node.lineno:node.end_lineno-1])
            + lines[node.end_lineno-1][:node.end_col_offset]) if node.lineno != node.end_lineno else lines[node.lineno-1][node.col_offset:node.end_col_offset]

def manifest(folder, name, key):
    path = BASE / folder / name
    doc = json.loads(path.read_bytes())
    for row in doc[key]:
        actual = pin(path.parent / row['path'])
        assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
    return {'manifest': pin(path), 'payload_count': len(doc[key]), 'all_byte_pins_equal': True}

def main():
    checked = [manifest('full115-saved-audit-source-v1', 'SOURCE_MANIFEST.json', 'payloads'),
               manifest('full115-bounded-window-source-draft-v1', 'SOURCE_MANIFEST.json', 'files'),
               manifest('full115-113-bridge-source-v2', 'SOURCE_MANIFEST.json', 'files'),
               manifest('full115-root-activated-source-v1', 'ROOT_SOURCE_ACTIVATION.json', 'files'),
               manifest('full115-saved-try-peer-source-v1', 'SOURCE_MANIFEST.json', 'payloads')]
    auditor = BASE / 'full115-saved-audit-source-v1/audit_full115.py'
    audit_raw = auditor.read_bytes()
    audit_tree = ast.parse(audit_raw)
    compile(audit_raw, str(auditor), 'exec')  # Code object only. Never executed.
    constants = {t.id: ast.literal_eval(n.value) for n in audit_tree.body if isinstance(n, ast.Assign)
                 for t in n.targets if isinstance(t, ast.Name)}
    paths = [BASE / name / 'window.py' for name in ('full110-bounded-window-source-draft-v1',
              'full115-bounded-window-source-draft-v1', 'full115-root-activated-source-v1')]
    raws = [p.read_bytes() for p in paths]
    trees = [ast.parse(raw) for raw in raws]
    measured = []
    blocks = []
    matrices = []
    helpers = {}
    for path, raw, tree in zip(paths, raws, trees):
        all_asserts = [ast.dump(n, include_attributes=False) for n in ast.walk(tree) if isinstance(n, ast.Assert)]
        assert len(all_asserts) == 831
        encoded_asserts = json.dumps(all_asserts, separators=(',', ':')).encode()
        assert sha(encoded_asserts) == constants['ASSERT_AST_SHA']
        functional = max((n for n in ast.walk(tree) if isinstance(n, ast.Try)), key=lambda n: n.end_lineno-n.lineno)
        exact = span(raw, functional)
        lines = b''.join(raw.splitlines(keepends=True)[functional.lineno-1:functional.end_lineno])
        assert len(exact) == 593858 and sha(exact) == constants['FUNCTIONAL_TRY_SHA']
        assert lines == exact + b'\n' and len(lines) == 593859
        assert sha(lines) == '6e6ef4725e9c6fbf2fbb4c42e16260399a1bdc0faaa481ef2688cd2b359d0f09'
        blocks.append(exact)
        matrix_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == 'rows090' for t in n.targets)]
        assert len(matrix_nodes) == 1
        matrix = ast.literal_eval(matrix_nodes[0].value)
        assert len(matrix) == 52
        matrices.append(matrix)
        measured.append({'source': pin(path), 'whole_file_Assert_count': 831,
            'functional_Try_Assert_count': sum(isinstance(n, ast.Assert) for n in ast.walk(functional)),
            'AST_walk_compact_JSON_Assert_sha256': sha(encoded_asserts),
            'exact_AST_segment_bytes': len(exact), 'exact_AST_segment_sha256': sha(exact),
            'whole_line_segment_bytes': len(lines), 'whole_line_segment_sha256': sha(lines),
            'only_added_terminal_byte_hex': '0a'})
    assert blocks[0] == blocks[1] == blocks[2]
    assert packed(matrices[0]) == packed(matrices[1]) == packed(matrices[2])
    for name in ('projection090', 'native090'):
        parts = [span(raw, next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name))
                 for raw, tree in zip(raws, trees)]
        assert parts[0] == parts[1] == parts[2]
        helpers[name] = {'bytes': len(parts[0]), 'sha256': sha(parts[0]), 'unchanged': True}
    large = [[span(raw, n) for n in ast.walk(tree) if isinstance(n, ast.Assign) and len(span(raw, n)) > 10000]
             for raw, tree in zip(raws, trees)]
    assert len(large[0]) == 3 and large[0] == large[1] == large[2]
    activated = BASE / 'full115-root-activated-source-v1'
    admission_path = activated / 'expected-map115.json'
    admission_raw = admission_path.read_bytes()
    assert sha(admission_raw) == constants['ADMISSION_SHA113']
    assert admission_raw == (BASE / 'root-section113-api-admission-actual-v2/expected-map115.json').read_bytes()
    admission = json.loads(admission_raw)
    indices = (18, 19, 20, 21, 38, 39, 40, 41, 44, 45)
    assert tuple(row['literal_index'] for row in admission['rows']) == indices
    assert admission['future_actual115_guard_sha256'] is None
    proof_pins = []
    for name, expected in admission['proof_files'].items():
        path = activated / expected['path']; observed = pin(path)
        assert observed['bytes'] == expected['bytes'] and observed['sha256'] == expected['sha256']
        proof_pins.append({'name': name, **observed})
    assert len(proof_pins) == 7
    pair_path = activated / admission['proof_files']['pair_audit']['path']
    pair = json.loads(pair_path.read_bytes())  # Allowed ordinary Root JSON; no native/gzip decode.
    assert pair['passed'] is True and pair['literal_indices'] == list(indices)
    seams = ['external_event_reference.parameter_rows.0', 'external_event_reference.window_reference.parameter_rows.0']
    rows = []
    for row, proved in zip(admission['rows'], pair['rows']):
        index = row['literal_index']; literal = matrices[0][index]
        assert sha(packed(literal)) == row['full_source_row_sha256_json_ordered']
        assert sha(packed(literal['input'])) == row['input_sha256_json_ordered']
        assert row['original_caller_native090_sha256'] == row['candidate_caller_native090_sha256']
        assert proved['qualified_historical_JSON_tuple_list_paths'] == (seams if index == 21 else [])
        assert sha(packed(row['metric_leaf_admission'])) == proved['metric_leaf_admission_sha256']
        for key in ('literal_index', 'full_source_row_sha256_json_ordered', 'input_sha256_json_ordered',
                    'original_projection_native090_sha256', 'candidate_projection_native090_sha256',
                    'original_caller_native090_sha256', 'candidate_caller_native090_sha256'):
            assert type(row[key]) is type(proved[key]) and row[key] == proved[key]
        changed = [key for key, leaf in row['metric_leaf_admission'].items() if leaf['actual_changed']]
        assert changed and set(changed) <= {'estimate.skill.window_seconds', 'estimate.skill.window_dps'}
        assert not row['metric_leaf_admission']['estimate.skill.window_hps']['actual_changed']
        rows.append({'literal_index': index, 'Source_row_and_input_identity_pin_equal': True,
                     'same_measured_original_candidate_caller_pin': True, 'only_allowed_changed_paths': changed,
                     'qualified_historical_JSON_tuple_list_paths': seams if index == 21 else []})
    guard_path = BASE / 'resume115-final-source-v1.json'; guard_raw = guard_path.read_bytes(); guard = json.loads(guard_raw)
    root = Path('/workspace/rougezhushou'); current = {}
    for name in ('rouge', 'tests', 'scripts'):
        for path in sorted((root / name).rglob('*')):
            if '__pycache__' in path.relative_to(root).parts or path.suffix not in ('.py', '.json'):
                continue
            assert not path.is_symlink()
            if path.is_file(): current[path.relative_to(root).as_posix()] = sha(path.read_bytes())
    assert dict(sorted(current.items())) == guard['source_sha256'] and len(current) == 758
    assert 'CORE_0.70_VERIFICATION.json' in guard['source_additional_sha256']
    assert all(sha((root / name).read_bytes()) == value for name, value in guard['source_additional_sha256'].items())
    activation = json.loads((activated / 'ROOT_SOURCE_ACTIVATION.json').read_bytes())
    assert activation['guard_sha256'] == sha(guard_raw)
    launcher_raw = (activated / 'launcher115.py').read_bytes(); launcher = launcher_raw.decode()
    for name, value in (('WINDOW_SHA256', sha(raws[-1])), ('SOURCE115_GUARD_SHA256', sha(guard_raw))):
        active = name + ' = ' + repr(value); assert launcher.count(active) == 1
        launcher = launcher.replace(active, name + ' = None')
    assert sha(launcher.encode()) == constants['LAUNCHER_TEMPLATE_SHA']
    assert sha((activated / 'bridge115.py').read_bytes()) == constants['BRIDGE_SHA']
    assert sha((activated / 'supervisor115.py').read_bytes()) == constants['SUPERVISOR_SHA']
    return {'kind': 'INDEPENDENT_SOURCE_ONLY_FULL115_SAVED_AUDITOR_REVIEW',
        'recorded_at_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_review_passed': True, 'blocking_findings': [],
        'runtime_executed': False, 'runtime_pass_claimed': False,
        'project_API_tests_Qt_Wine_helper_codec_native_gzip_Git_executed': False,
        'actual_window_output_native_or_gzip_opened_or_decoded': False, 'tracked_written': False,
        'auditor_compiled_codeobject_only_not_executed': True,
        'auditor': pin(auditor), 'reference_Root110_auditor': pin(BASE / 'root-full110-saved-audit-v1.py'),
        'byte_verified_manifests': checked, 'window_Source_measurements': measured,
        'whole_Try_and_52_Source_matrix_literals_unchanged': True,
        'three_large_public_Source_literal_sha256': [sha(raw) for raw in large[0]],
        'unchanged_original_projection_native_helpers': helpers,
        'LF_difference_explanation': 'The 593858-byte exact AST Source span excludes the final LF. The 593859-byte whole-line span includes precisely one LF (0a). Both spans are independently byte-equal across Source110, inactive115 and activated115. Whole window has831 Assert nodes; maximum Try has552.',
        'seven_Root113_ordinary_JSON_proof_pins': proof_pins,
        'admission_map': pin(admission_path), 'independent_Source_literal_admission_rows': rows,
        'current_frozen_Source_snapshot_only': {'guard': pin(guard_path), 'maintained_source_count': len(current),
            'whole_maintained_map_equal': True, 'explicit_CORE_map_equal': True, 'not_a_runtime_outcome': True},
        'manual_Source_contract_findings': [
          {'audit_lines': [220,249], 'finding': 'Requires exact primary0, child0 and supervisor0, completed/non-timeout, no-live owned session and no global wineserver cleanup. Every retained member must be Z; absence equals zero retained members; reaped is False. Requires full4283-check receipt,52 explicit requests156 texts, Source and CORE before/after frozen equality.'},
          {'audit_lines': [250,283], 'finding': 'Binds activated Source hashes, inverse launcher template, exact831 Assert AST and exact maximum functional Try,52 immutable Source rows, seven pinned actual113 artifacts,10 exact ledger admissions and closure hashes. No runtime/PASS follows from this Source review.'},
          {'audit_lines': [284,351], 'finding': 'Retains original full110 compressed and decoded archive bytes/SHA, all52 unique identities, all complete tagged result/caller scalar types/order/floatbits, original42 strict_json projections and all three full texts. Ten rows require measured full typed candidate projection/caller SHA, exact old/new metric type/presence/floatbits and unchanged HPS. Only changed seconds/DPS restored in isolated copies; restored whole typed digest must equal measured original, then untouched Source Gold.'},
          {'audit_lines': [320,332], 'finding': 'For row21 only, exact two qualified historical tuple/list paths: actual tuple vs literal list, length3, ordered(str,float,str), equal complete item trees. Only comparison-copy tag kind changes; candidate/original measured hashes and actual graphs remain exact. Other9 have no tuple/list exception.'},
          {'audit_lines': [336,379], 'finding': 'Correlates every saved state with one exact actual UI check and three-text match; checks all4 PNG byte/header/hash. Rescans Source/CORE and frozen evidence. Output discloses no independent saved after-formatter graph, no full old result Gold, no alias/cycle identity, no old095 vector, no native Windows/game/chat or pixel inspection.'}],
        'nonblocking_scope_notes': [
          'Retain Root before-launch ROOT_SOURCE_ACTIVATION byte-pin proof as the external chain. Auditor binds runner through actual receipt/closure plus immutable Try/Assert/helper review but does not independently open the activation manifest.',
          'Child peer46f6... sorts all831 Assert nodes by (lineno,col_offset), dumps each AST without attributes and serializes compact JSON with ensure_ascii=False. Auditor39e4... retains ast.walk order and compact JSON default ensure_ascii=True. Each independently confirms old/new equality under its own traversal and encoding; hashes do not describe identical serialized bytes. This report directly verifies the actual auditor39e4... constant.',
          'README593858 and bridge593859 describe different valid LF spans. This is explanatory scope, no runtime error or hidden functional change.'],
        'Root_required_next': 'Only Root executes fresh Saved audit after actual full115 primary/closure; separately inspect four actual legacy PNGs and specialized115 feature screenshots. Preserve deferred95/109 and unavailable native Windows/game/chat coverage.'}

if __name__ == '__main__':
    report = main()
    with (DEST / 'review.json').open('x', encoding='utf-8') as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2); handle.write('\n')
    print(json.dumps({'Source_review_passed': True, 'runtime_pass_claimed': False, 'report': str(DEST / 'review.json')}))
