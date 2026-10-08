"""Seal saved section092 evidence. Stdlib only; never execute project code."""
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
COMMIT = '59961ec3d633ac91b01014fb06b357d45e5979f7'
OLD_ARCHIVE = REPO / 'research/p2-section091-attack-condition-regeneration/future092-source-and-unexecuted-candidate'
MANIFEST = HERE / 'FINAL-manifest092.json'
HANDOFF = HERE / 'author-handoff092.json'
DIAGNOSTIC = HERE / 'seal-diagnostic092.json'
ZERO = dict.fromkeys(('imports', 'API', 'helper', 'formatter', 'tests', 'Qt', 'Wine'), 0)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, ('duplicate JSON key', key)
        result[key] = value
    return result


def parse(raw):
    return json.loads(raw, object_pairs_hook=no_duplicates,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def load(name):
    return parse((HERE / name).read_bytes())


def encode(value):
    kind = type(value)
    if value is None: return ['none']
    if kind is bool: return ['bool', value]
    if kind is int: return ['int', str(value)]
    if kind is float: return ['float', value.hex()]
    if kind is str: return ['str', value]
    if kind is bytes: return ['bytes', value.hex()]
    if kind in (list, tuple): return [kind.__name__, [encode(v) for v in value]]
    if kind is dict: return ['dict', [[encode(k), encode(v)] for k, v in value.items()]]
    if kind in (set, frozenset):
        return [kind.__name__, sorted([encode(v) for v in value], key=canonical)]
    raise TypeError(kind.__name__)


def decode(tree):
    assert type(tree) is list and tree and type(tree[0]) is str
    tag = tree[0]
    assert len(tree) == (1 if tag == 'none' else 2), ('native length', tag)
    if tag == 'none': return None
    payload = tree[1]
    if tag == 'bool':
        assert type(payload) is bool
        return payload
    if tag in ('int', 'float', 'str', 'bytes'):
        assert type(payload) is str
        if tag == 'str': return payload
        value = int(payload) if tag == 'int' else float.fromhex(payload) if tag == 'float' else bytes.fromhex(payload)
        assert encode(value)[1] == payload, ('noncanonical scalar', tag)
        return value
    assert tag in ('dict', 'list', 'tuple', 'set', 'frozenset') and type(payload) is list
    if tag == 'dict':
        result = {}
        for pair in payload:
            assert type(pair) is list and len(pair) == 2
            key, value = decode(pair[0]), decode(pair[1])
            assert key not in result, 'duplicate/colliding native dictionary key'
            result[key] = value
        return result
    values = [decode(v) for v in payload]
    result = values if tag == 'list' else tuple(values) if tag == 'tuple' else set(values) if tag == 'set' else frozenset(values)
    assert len(result) == len(values), 'duplicate native set member'
    return result


def native(tree):
    value = decode(tree)
    assert canonical(encode(value)) == canonical(tree), 'native roundtrip differs'
    return value


def fingerprint(path):
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}


def bound(item, path=None, bytes_key='bytes', sha_key='sha256'):
    path = Path(path or item.get('source_path') or item['path'])
    raw = path.read_bytes()
    assert (len(raw), sha(raw)) == (item[bytes_key], item[sha_key]), str(path)
    return raw


def git(*args):
    return subprocess.run(['git', *args], cwd=REPO, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def write_new(path, data):
    raw = (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    with path.open('xb') as target:
        assert target.write(raw) == len(raw)
    assert path.read_bytes() == raw


def verify():
    assert git('rev-parse', 'HEAD').decode().strip() == COMMIT
    assert git('rev-parse', 'p2-section-091').decode().strip() == COMMIT
    assert git('branch', '--show-current').decode().strip() == 'codex/p2-development'
    assert git('status', '--porcelain') == b''
    original = {str(p.relative_to(HERE)): fingerprint(p) for p in HERE.rglob('*')
                if p.is_file() and p != Path(__file__).resolve()}
    inventory = load('maintained730-git-and-current-hashes092.json')
    assert inventory['actual_root_commit'] == COMMIT and inventory['file_count'] == len(inventory['files']) == 730
    assert sum(v['bytes'] for v in inventory['files']) == inventory['total_bytes'] == 26071424
    assert len({v['source_path'] for v in inventory['files']}) == 730
    for item in inventory['files']:
        assert item['git_ref'] == COMMIT
        raw = bound(item)
        assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == item['git_blob']
    freeze = load('pre-public-freeze092.json')
    assert freeze['actual_root_commit'] == COMMIT and freeze['file_count'] == len(freeze['files']) == 14
    for item in freeze['files']: bound(item)
    old = load('old49-manifest-immutable.json')
    assert old['file_count'] == len(old['files']) == 49 and old['stopwrite'] and old['manifest_itself_excluded']
    assert sum(v['bytes'] for v in old['files']) == old['total_bytes'] == 1048120
    assert len({v['archive_path'] for v in old['files']}) == 49
    assert (OLD_ARCHIVE / 'public-candidate-manifest.json').read_bytes() == (HERE / 'old49-manifest-immutable.json').read_bytes()
    assert sha((HERE / 'old49-manifest-immutable.json').read_bytes()) == '285a6ae53be573b6323f3144fd2a9ed26237162abe211faff7b0a5a1b772fece'
    for item in old['files']: bound(item, OLD_ARCHIVE / item['archive_path'])
    proof = load('static-product-proof092.json')
    assert sha((HERE / 'static-product-proof092.json').read_bytes()) == '3e7aab848761b3d7793801c50c547c77ca8612cedba612cffe5ee4bcb5a4d040'
    assert proof['fixed_git_commit'] == COMMIT and proof['status'] == 'PASS_STATIC_ONLY_NOT_FORMAL_REVIEW'
    assert all(value == 0 for value in proof['project_calls'].values())
    for group in proof['files'].values():
        for item in group.values(): bound(item)
    for item in proof['bindings'].values(): bound(item)
    assert proof['checks']['app_inverse_bytes_equal'] and proof['checks']['report_inverse_bytes_equal']
    assert proof['checks']['patch_exactly_regenerated_from_baseline'] and proof['checks']['patch_hunks'] == 4
    assert all(v['all_other_AST_including_signatures_equal'] for v in proof['checks']['AST'].values())
    for path in (HERE / 'actual91-leaves').rglob('*'):
        if path.is_file():
            assert path.read_bytes() == git('show', COMMIT + ':' + path.relative_to(HERE / 'actual91-leaves').as_posix())
    inputs = load('public-inputs092.json')
    cases = {v['id']: v['input'] for v in inputs['cases']}
    case_ids = ['damage-zero', 'finite-healing-zero', 'friendly-healing-enemy-zero', 'finite-healing-long']
    assert list(cases) == case_ids
    summary = load('saved-comparison-summary092.json')
    assert summary['status'] == 'PASS_SAVED_ONLY_STRICT_INVERSE' and summary['fixed_root_commit'] == COMMIT
    assert [p['case_id'] for p in summary['pairs']] == case_ids
    cache_raws, cache_hashes, results, receipts, ledgers = [], {}, {}, [], {}
    entries, requests = Counter(), Counter()
    for variant in ('baseline', 'draft'):
        ledger = load(variant + '-actual-ledger092.json')
        ledgers[variant] = ledger
        assert ledger['variant'] == variant and ledger['status'] == 'PASS' and ledger['actual_public_entries'] == 4
        assert all(ledger[k] == 0 for k in ('explicit_external_project_helper_calls', 'Qt', 'Wine', 'tests'))
        assert ledger['source_current_730_verified_before_run'] and ledger['no_actual_Qt_or_app_import']
        assert ledger['public_entry_trace'] == [{'case_id': cid, 'phase': 'public'} for cid in case_ids]
        expected_requests = [{'case_id': cid, 'mode': mode} for cid in case_ids for mode in ('estimate', 'default', 'technical')]
        assert ledger['external_formatter_requests'] == expected_requests
        expected_entries = []
        for cid in case_ids:
            for request, module, function, technical in (
                ('estimate', 'rouge.estimate', 'format_estimate', None),
                ('estimate', 'rouge.reporting', 'format_report', False),
                ('default', 'rouge.reporting', 'format_report', False),
                ('technical', 'rouge.reporting', 'format_report', True)):
                expected_entries.append(dict(case_id=cid, request=request, module=module, function=function, technical=technical))
        assert canonical(ledger['actual_formatter_entries']) == canonical(expected_entries)
        for item in ledger['external_formatter_requests']: requests[item['mode']] += 1
        for item in ledger['actual_formatter_entries']:
            entries[item['function'] + ('_technical' if item['technical'] else '_default') if item['function'] == 'format_report' else item['function']] += 1
        assert len(ledger['saved_records']) == 4
        results[variant] = {}
        for index, item in enumerate(ledger['saved_records'] + [ledger['saved_cache']]):
            raw = bound(item, bytes_key='compressed_bytes', sha_key='compressed_sha256')
            decoded = gzip.decompress(raw)
            assert (len(decoded), sha(decoded)) == (item['decoded_bytes'], item['decoded_sha256'])
            receipts.append(item)
            if index == 4:
                cache_raws.append(decoded)
                continue
            record = parse(decoded)
            cid = case_ids[index]
            assert record['variant'] == variant and record['case_id'] == cid and record['error'] is None
            assert canonical(record['input_before']) == canonical(encode(cases[cid])) == canonical(record['input_after'])
            native(record['input_before']); native(record['input_after'])
            assert record['input_JSON_before'] == canonical(cases[cid]) == record['input_JSON_after']
            value = native(record['result_native_tree'])
            assert canonical(record['result_native_tree']) == canonical(record['result_after_formatters_native_tree'])
            assert record['result_JSON'] == canonical(value) and record['caller_unchanged'] is True
            assert set(record['texts']) == {'estimate', 'default', 'technical'}
            assert all(type(text) is str and text for text in record['texts'].values())
            assert record['texts']['estimate'] == record['texts']['default']
            assert record['ledger_after_call'] == dict(actual_public_entries=index+1, external_formatter_requests=3*(index+1), actual_formatter_entries=4*(index+1))
            results[variant][cid] = (record, value)
    assert cache_raws[0] == cache_raws[1]
    cache = parse(cache_raws[0])
    assert len(cache) == 9
    for name, value in cache.items():
        assert value['equal_complete_native_tree'] is True
        assert canonical(value['first_native_tree']) == canonical(value['final_native_tree'])
        native(value['first_native_tree'])
        cache_hashes[name] = sha(canonical(value['first_native_tree']).encode())
    for variant, ledger in ledgers.items():
        assert ledger['observed_cached_function_returns'] == [dict(cache=name, case_id=case_ids[0], phase='public') for name in cache]
        for record, _ in results[variant].values():
            assert set(record['observed_cache_state_after_call']) == set(cache)
            for name, state in record['observed_cache_state_after_call'].items():
                assert state == {'native_tree_sha256': cache_hashes[name], 'equal_first_native_tree': True}
    for pair in summary['pairs']:
        cid = pair['case_id']
        before_record, before = results['baseline'][cid]
        after_record, after = results['draft'][cid]
        inverse = deepcopy(after)
        section = pair['qualified_section']
        assert section == ('damage' if cid == 'damage-zero' else 'healing')
        expected = pair['removed_qualified_rows']
        assert len(expected) == 1 and expected[0]['section_id'] == section
        row = expected[0]['row']
        effective = before['estimate']['skill']['window_seconds']
        assert canonical(encode(row)) == canonical(encode(dict(key='window_seconds', label='伤害观察窗口' if section=='damage' else '治疗观察窗口', value=effective, unit='秒')))
        assert effective is not None and canonical(expected[0]['native_value']) == canonical(encode(effective))
        metrics = next(block['metrics'] for block in inverse['report']['sections'] if block['id'] == section)
        matches = [i for i, candidate in enumerate(metrics) if canonical(encode(candidate)) == canonical(encode(row))]
        assert len(matches) == 1
        del metrics[matches[0]]
        assert canonical(encode(inverse)) == canonical(before_record['result_native_tree'])
        assert canonical(inverse) == before_record['result_JSON']
        assert pair['whole_native_inverse_exact'] and pair['whole_JSON_inverse_exact']
        for mode in ('estimate', 'default', 'technical'):
            binding = pair['three_saved_text_inverses'][mode]
            old_text, new_text = before_record['texts'][mode], after_record['texts'][mode]
            assert sha(old_text.encode()) == binding['baseline_sha256'] and sha(new_text.encode()) == binding['draft_sha256']
            assert binding['remaining_saved_text_exact'] and len(binding['removed_lines']) == 1
            line = binding['removed_lines'][0]
            assert line == row['label'] + '：' + format(effective, '.2f') + ' 秒'
            pieces = new_text.splitlines(keepends=True)
            matches = [i for i, piece in enumerate(pieces) if piece.rstrip('\r\n') == line]
            assert len(matches) == 1 and line not in old_text.splitlines()
            del pieces[matches[0]]
            assert ''.join(pieces) == old_text
        assert pair['caller_unchanged_both'] and pair['result_unchanged_by_formatters_both']
        assert canonical(pair['requested_window_native']) == canonical(encode(cases[cid]['window_seconds']))
        assert canonical(pair['effective_window_native']) == canonical(encode(effective))
    assert dict(requests) == summary['external_request_modes_actual'] == {'estimate': 8, 'default': 8, 'technical': 8}
    assert dict(entries) == summary['actual_internal_formatter_entries_by_function'] == {'format_estimate': 8, 'format_report_default': 16, 'format_report_technical': 8}
    assert summary['actual_public_entries'] == summary['saved_public_results'] == 8
    assert summary['external_formatter_requests'] == 24 and summary['actual_internal_formatter_entries'] == 32
    assert summary['pair_count'] == 4 and summary['comparison_process_project_imports_API_helpers_formatters_tests_Qt_Wine'] == 0
    assert summary['complete_observed_cache_first_final_and_across_variants_exact'] is True
    for name, item in original.items(): assert fingerprint(HERE / name) == item
    assert git('status', '--porcelain') == b'' and git('rev-parse', 'HEAD').decode().strip() == COMMIT
    return {'original_file_count': len(original), 'frozen_files_verified': 14,
            'old49_archived_payload_files_verified': 49, 'old49_archived_payload_bytes': 1048120,
            'maintained_current_files_verified': 730, 'maintained_current_bytes': 26071424,
            'saved_gzip_files_verified': 10, 'saved_records': 8, 'saved_cache_packets': 2,
            'cache_complete_objects_per_variant': 9, 'saved_pair_inverse_count': 4,
            'saved_text_inverse_count': 12, 'strict_native_and_JSON_bindings': 'PASS',
            'original_files_unchanged': True, 'source_static_proof_binding': fingerprint(HERE / 'static-product-proof092.json'),
            'saved_gzip_receipts': receipts, 'project_calls_this_seal': ZERO,
            'root_clean_before_and_after_verification': True}


def main():
    assert not any(p.exists() for p in (MANIFEST, HANDOFF, DIAGNOSTIC)), 'Append-only seal; never overwrite or rerun after FINALSTOPWRITE.'
    diagnostic = {'format_version': 1, 'complete_goal': 'section092 saved-result author packet sealing',
        'complete_goal_attempts': 2, 'known_prior_transport_failures': 1,
        'prior_failure': {'attempt': 1, 'stage': 'write seal_final092.py', 'wall_seconds': 363.2,
            'exit_code': 1, 'message': 'Failed to write', 'artifact_produced': False,
            'evidence_origin': 'Parent root task message quotes prior tool transport result; original tool result is not present in this packet.',
            'resumed_inventory_confirmed_script_and_final_metadata_absent_before_this_attempt': True},
        'historical_early_no_primary_failure_statement': 'Retained unchanged; describes its earlier recording time, before this later transport failure.',
        'older_preparation_failure_record': 'root-attempt-boundary091-immutable.json remains unchanged.',
        'three_attempt_rule': 'Count the same complete goal across error names; defer if three attempts leave it incomplete. Do not reset by exception label.',
        'project_calls_this_seal': ZERO}
    try:
        result = verify()
    except Exception as error:
        diagnostic.update(status='FAILED_SAVED_ONLY_SEAL_VERIFICATION', current_attempt_result='incomplete',
                          current_failure=dict(type=type(error).__name__, message=str(error)))
        write_new(DIAGNOSTIC, diagnostic)
        raise
    diagnostic.update(status='PASS_SAVED_ONLY_SEAL_VERIFICATION', current_attempt_result='completed', verification=result)
    write_new(DIAGNOSTIC, diagnostic)
    excluded = {MANIFEST.name, HANDOFF.name}
    files = []
    for path in sorted(p for p in HERE.rglob('*') if p.is_file() and p.name not in excluded):
        item = fingerprint(path)
        files.append(dict(source_path=item['path'], archive_path=path.relative_to(HERE).as_posix(), bytes=item['bytes'], sha256=item['sha256']))
    manifest = {'format_version': 1, 'status': 'FINAL_SAVED_AUTHOR_PACKET_PENDING_INDEPENDENT_REVIEW_AND_ROOT_RUNTIME',
        'fixed_root_commit': COMMIT, 'fixed_root_tag': 'p2-section-091', 'files': files,
        'file_count': len(files), 'total_bytes': sum(item['bytes'] for item in files),
        'excluded_metadata': [MANIFEST.name, HANDOFF.name],
        'manifest_and_handoff_excluded_to_avoid_circular_bindings': True,
        'root_archive_must_also_include_excluded_metadata': True,
        'recorded_original_execution': dict(public_API_entries=8, external_formatter_requests=24, actual_formatter_entries=32),
        'new_project_calls_this_seal': ZERO, 'tracked_changes_this_seal': 0,
        'whole_source_tree_copies_this_seal': 0, 'original_packets_unchanged': True,
        'finalstopwrite': True}
    write_new(MANIFEST, manifest)
    handoff = {'format_version': 1, 'status': manifest['status'], 'fixed_root_commit': COMMIT,
        'author_directory': str(HERE), 'manifest': fingerprint(MANIFEST), 'diagnostic': fingerprint(DIAGNOSTIC),
        'payload_file_count': manifest['file_count'], 'payload_total_bytes': manifest['total_bytes'],
        'payload_file_schema': ['source_path', 'archive_path', 'bytes', 'sha256'],
        'saved_result_ledger_paths': [str(HERE / (v + '-actual-ledger092.json')) for v in ('baseline', 'draft')],
        'saved_record_receipt_schema': ['path', 'compressed_bytes', 'compressed_sha256', 'decoded_bytes', 'decoded_sha256'],
        'candidate_products': {name: fingerprint(HERE / 'candidate' / 'rouge' / name) for name in ('app.py', 'reporting.py')},
        'source_static_proof': result['source_static_proof_binding'],
        'prior49_archive': {'path': str(OLD_ARCHIVE), 'manifest': fingerprint(OLD_ARCHIVE / 'public-candidate-manifest.json'),
                            'verified_files': 49, 'verified_payload_bytes': 1048120, 'not_copied_here': True},
        'product_scope': 'App make_damage_tab: observation-window toggled/valueChanged calculate signals and window/timing tooltip text. Reporting build_report: damage/healing effective window_seconds rows when metric is not None, including zero; existing positive average guards preserved.',
        'saved_comparison_scope': 'Four saved pairs: remove only one qualified window_seconds row and its one saved line per text mode; all other whole typed-native/JSON/text results, caller inputs, formatter-post-result and complete observed cache trees remain exact.',
        'execution': manifest['recorded_original_execution'], 'new_project_calls_this_seal': ZERO,
        'tracked_changes_this_seal': 0, 'same_complete_goal_attempts': 2, 'later_transport_failures': 1,
        'limitations': 'Saved evidence only. Not an independent formal review or completed section. No actual Qt/Wine/native Windows/game clock checks in this author packet; signal delivery and actual app acceptance belong to root. Cache-hit entry counts and all cache functions were not measured.',
        'root_next_actions': ['Independent saved-only review; do not rerun calculate or formatters for this packet.',
                              'Root owns tracked application, appropriate regression, actual project window and archive acceptance.',
                              'Archive every manifest payload member plus FINAL-manifest092.json and author-handoff092.json with a separate root container/member binding.'],
        'excluded_metadata_to_include_in_root_archive': [str(MANIFEST), str(HANDOFF)],
        'finalstopwrite': True}
    write_new(HANDOFF, handoff)
    for item in files: bound(item)
    assert parse(MANIFEST.read_bytes()) == manifest and parse(HANDOFF.read_bytes()) == handoff
    assert git('status', '--porcelain') == b'' and git('rev-parse', 'HEAD').decode().strip() == COMMIT
    print(canonical(dict(status='FINALSTOPWRITE', manifest=fingerprint(MANIFEST), handoff=fingerprint(HANDOFF),
                         diagnostic=fingerprint(DIAGNOSTIC), payload_files=len(files), payload_bytes=manifest['total_bytes'],
                         new_project_calls=ZERO, tracked_changes=0)))


if __name__ == '__main__':
    main()
