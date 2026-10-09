#!/usr/bin/env python3
"""Validate saved account093 evidence. Stdlib only; never imports the product."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path, PurePosixPath, PureWindowsPath
import struct
import sys
import zlib

BOUND = {
    'wine-account-window-093-final.py': 'aab214ac2903d6023fb6e44f78593e06ebeda120bc9fcf2300b2ef2a88ef5053',
    'wine-account-window-093-source.json': '0fbfe28e2528ae9987f9f260bfed0068b1e16edf02274ea3349cd6d988aa2180',
    'wine-account-window-093-plan.json': '6ff61e9d3bf12ee822efecf627b38bbbe9e4a8e608d93eff8b108191c150e5e3',
}
RECEIPT_NAME = 'wine-account-window-093.json'
ARCHIVE_NAME = 'wine-account-window-093-records.json.gz'
FORMAL_REVIEW_SHA = '40b7bbdcc7d734bc07d310fca48d31c24d45c2e4434e3fe8aa1229efcc8b3ade'
RUN_METADATA = {'recruitment_kind', 'advanced', 'run_confirmed_fields', 'char_buff_ids',
                'char_buffs_complete', 'char_buff_absent_ids', 'char_buff_pending_ids'}
OUTCOMES = ('returned_dict', 'raised_exception', 'returned_non_dict_or_unobserved_unwind')
UNCHANGED_CALLERS = {'calculate_damage', 'AccountCache.observe', 'MainWindow.apply_operator_observation',
                     'MainWindow.apply_run_observation', 'RunState.apply', 'MainWindow.sample_received'}
PHASES = {'startup', 'probe_before', 'probe_startup', 'common_controls', 'action', 'probe_after',
          'explicit_three_texts', 'technical_view_signals', 'close'}
REQUESTS = {'explicit_probe', 'Qt_slot_or_internal', 'manual_button', 'explicit_formatter', 'window_close'}
context = 'initialization'
checked = []
snapshots_verified = 0


def require(condition, message):
    if not condition:
        raise ValueError(context + ': ' + message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_bound(path, report):
    raw = path.read_bytes()
    report['input_bindings'][str(path.resolve())] = {'bytes': len(raw), 'sha256': sha(raw)}
    return raw


def integer(value):
    return type(value) is int


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def bad_constant(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=bad_constant)


def encode_native(value):
    """Independent iterative canonical graph encoder, used only by root execution."""
    table = []
    work = []
    aliases = {}
    def ref(item):
        kind = type(item)
        if kind in (dict, list, tuple) and id(item) in aliases:
            return aliases[id(item)]
        index = len(table)
        table.append(None)
        work.append((index, item))
        if kind in (dict, list, tuple):
            aliases[id(item)] = index
        return index
    root = ref(value)
    while work:
        index, item = work.pop()
        kind = type(item)
        if kind in (type(None), bool, int, str):
            row = {'type': kind.__name__, 'value': item}
        elif kind is float:
            row = {'type': 'float', 'hex': item.hex()}
        elif kind is bytes:
            row = {'type': 'bytes', 'hex': item.hex()}
        elif kind in (list, tuple):
            row = {'type': kind.__name__, 'items': [ref(child) for child in item]}
        elif kind is dict:
            row = {'type': 'dict', 'items': [[ref(key), ref(child)] for key, child in item.items()]}
        else:
            raise ValueError('Unsupported native type: ' + kind.__name__)
        table[index] = row
    return {'schema': 'flat-typed-graph-v1', 'root': root, 'nodes': table}


def equal(left, right):
    return encode_native(left) == encode_native(right)


def inverse(graph):
    """Validate and invert an acyclic typed graph without recursion."""
    require(type(graph) is dict and set(graph) == {'schema', 'root', 'nodes'}, 'native graph fields')
    require(graph['schema'] == 'flat-typed-graph-v1', 'native schema')
    nodes = graph['nodes']
    require(type(nodes) is list and nodes, 'nonempty graph nodes')
    def index(value):
        require(integer(value) and 0 <= value < len(nodes), 'graph reference range/type')
        return value
    root = index(graph['root'])
    children = {}
    scalar = {}
    for number, row in enumerate(nodes):
        require(type(row) is dict and type(row.get('type')) is str, 'native node type')
        kind = row['type']
        if kind in ('NoneType', 'bool', 'int', 'str'):
            require(set(row) == {'type', 'value'}, 'scalar fields')
            expected = {'NoneType': type(None), 'bool': bool, 'int': int, 'str': str}[kind]
            require(type(row['value']) is expected, 'exact native scalar type')
            scalar[number] = row['value']
        elif kind in ('float', 'bytes'):
            require(set(row) == {'type', 'hex'} and type(row['hex']) is str, 'hex scalar fields')
            value = float.fromhex(row['hex']) if kind == 'float' else bytes.fromhex(row['hex'])
            require(value.hex() == row['hex'], 'canonical native hex')
            if kind == 'float':
                require(math.isfinite(value), 'finite native float for this workload')
            scalar[number] = value
        elif kind in ('dict', 'list', 'tuple'):
            require(set(row) == {'type', 'items'} and type(row['items']) is list, 'container fields')
            if kind == 'dict':
                require(all(type(pair) is list and len(pair) == 2 for pair in row['items']), 'dict key/value pairs')
                children[number] = [index(child) for pair in row['items'] for child in pair]
            else:
                children[number] = [index(child) for child in row['items']]
        else:
            raise ValueError('Unsupported native node type: ' + kind)
    values = dict(scalar)
    active = set()
    reached = set()
    stack = [(root, False)]
    while stack:
        number, finish = stack.pop()
        reached.add(number)
        if number in values:
            continue
        if not finish:
            require(number not in active, 'native graph cycle')
            active.add(number)
            stack.append((number, True))
            stack.extend((child, False) for child in reversed(children[number]))
        else:
            row = nodes[number]
            active.remove(number)
            kind = row['type']
            if kind == 'dict':
                value = {}
                for key_ref, value_ref in row['items']:
                    key = values[key_ref]
                    require(key not in value, 'duplicate native dictionary key')
                    value[key] = values[value_ref]
            else:
                value = [values[child] for child in row['items']]
                if kind == 'tuple':
                    value = tuple(value)
            values[number] = value
    require(reached == set(range(len(nodes))), 'native orphan nodes')
    restored = values[root]
    require(encode_native(restored) == graph, 'independent inverse/re-encode mismatch')
    return restored


def snapshot(value):
    global snapshots_verified
    require(type(value) is dict and set(value) == {'native', 'JSON_projection', 'native_inverse_verified'}, 'snapshot fields')
    require(value['native_inverse_verified'] is True, 'runner inverse verification flag')
    restored = inverse(value['native'])
    projected = strict_json(json.dumps(restored, ensure_ascii=False, allow_nan=False))
    require(equal(projected, value['JSON_projection']), 'native versus full JSON projection')
    snapshots_verified += 1
    return restored


def verify_all_snapshots(value):
    work = [value]
    while work:
        item = work.pop()
        if type(item) is dict:
            if set(item) == {'native', 'JSON_projection', 'native_inverse_verified'}:
                snapshot(item)
            work.extend(item.values())
        elif type(item) is list:
            work.extend(item)


def counters(value):
    require(type(value) is dict and all(type(k) is str and integer(v) and v >= 0 for k, v in value.items()), 'nonnegative integer counters')
    return {key: val for key, val in value.items() if val}


def files(rows):
    require(type(rows) is list, 'filesystem rows list')
    result = {}
    for row in rows:
        name = row.get('path')
        require(type(name) is str and name and '\\' not in name, 'public relative path')
        path = PurePosixPath(name)
        require(not path.is_absolute() and '..' not in path.parts and str(path) == name, 'safe normalized relative path')
        require(name not in result, 'duplicate filesystem path')
        require(row.get('kind') in ('file', 'directory'), 'filesystem kind')
        if row['kind'] == 'file':
            raw = bytes.fromhex(row['raw_hex'])
            require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'file raw bytes/hash')
            try:
                decoded = strict_json(raw.decode('utf-8'))
            except (UnicodeDecodeError, ValueError):
                require('decode_error' in row and 'decoded' not in row, 'malformed file decode evidence')
            else:
                require('decoded' in row and 'decode_error' not in row, 'decoded file snapshot evidence')
                require(equal(snapshot(row['decoded']), decoded), 'file decoded snapshot versus raw')
        result[name] = row
    require(list(result) == sorted(result), 'filesystem canonical row order')
    return result


def file_raw(rows, name):
    row = rows.get(name)
    return None if row is None else bytes.fromhex(row['raw_hex'])


def chain(value, label):
    for _ in range(500):
        require(type(value) is dict and list(value) == ['next'], 'exact500 opaque chain')
        value = value['next']
    require(equal(value, {'sentinel': 'public-093-' + label, 'values': [None, False, 0, '原值']}), 'opaque chain terminal')


def png(path, metadata, report):
    raw = read_bound(path, report)
    require(len(raw) == metadata['bytes'] and sha(raw) == metadata['sha256'], 'PNG bytes/hash')
    require(raw[:8] == b'\x89PNG\r\n\x1a\n', 'PNG signature')
    offset = 8
    dimensions = None
    ended = False
    while offset < len(raw):
        require(offset + 12 <= len(raw), 'PNG chunk bounds')
        size = struct.unpack('>I', raw[offset:offset + 4])[0]
        kind = raw[offset + 4:offset + 8]
        end = offset + 12 + size
        require(end <= len(raw), 'PNG data bounds')
        data = raw[offset + 8:offset + 8 + size]
        crc = struct.unpack('>I', raw[end - 4:end])[0]
        require(zlib.crc32(kind + data) & 0xffffffff == crc, 'PNG CRC')
        if dimensions is None:
            require(kind == b'IHDR' and size == 13, 'PNG IHDR first')
            dimensions = struct.unpack('>II', data[:8])
            require(all(x > 8 for x in dimensions), 'window PNG nontrivial dimensions')
        if kind == b'IEND':
            require(size == 0 and end == len(raw), 'PNG IEND/final length')
            ended = True
            break
        offset = end
    require(ended, 'PNG complete file')
    return {'file': path.name, 'bytes': len(raw), 'sha256': sha(raw), 'width': dimensions[0], 'height': dimensions[1]}


def verify(args, report):
    global context
    context = 'frozen source bindings'
    bound_bytes = {}
    for name, expected in BOUND.items():
        bound_bytes[name] = read_bound(args.final_dir / name, report)
        require(sha(bound_bytes[name]) == expected, 'bound file hash: ' + name)
    formal_raw = read_bound(args.formal_review, report)
    require(sha(formal_raw) == FORMAL_REVIEW_SHA, 'formal source review exact binding')
    formal = strict_json(formal_raw)
    require(formal['status'] == 'PASS_SOURCE_ONLY_ROOT_RUNTIME_PENDING' and formal['source_gate_passed'] is True and formal['runtime_pass'] is False, 'formal source-only gate scope')
    guard = strict_json(bound_bytes['wine-account-window-093-source.json'])
    plan = strict_json(bound_bytes['wine-account-window-093-plan.json'])
    source = guard['source_sha256_after']
    require(guard['passed'] is True and len(source) == 732, '732 source guard')
    require(all(sha((args.repo / name).read_bytes()) == expected for name, expected in source.items()), 'current732 source hashes')
    actual = {path.relative_to(args.repo).as_posix() for base in ('rouge', 'tests', 'scripts')
              for path in (args.repo / base).rglob('*') if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts}
    require(actual == set(source), 'current maintained source set')
    context = 'saved receipt/archive binding'
    receipt_bytes = read_bound(args.outputs_dir / RECEIPT_NAME, report)
    receipt = strict_json(receipt_bytes)
    report['input_receipt'] = {'file': RECEIPT_NAME, 'bytes': len(receipt_bytes), 'sha256': sha(receipt_bytes),
                               'runner_claimed_passed': receipt.get('passed'), 'runner_claimed_workflow_complete': receipt.get('workflow_complete')}
    require(receipt['records']['file'] == ARCHIVE_NAME, 'archive original filename')
    compressed = read_bound(args.outputs_dir / ARCHIVE_NAME, report)
    descriptor = receipt['records']
    require(len(compressed) == descriptor['bytes'] and sha(compressed) == descriptor['sha256'], 'archive compressed binding')
    raw = gzip.decompress(compressed)
    require(len(raw) == descriptor['decoded_bytes'] and sha(raw) == descriptor['decoded_sha256'], 'archive decoded binding')
    saved = strict_json(raw)
    report['saved_prefix'] = {'states': len(saved.get('states', [])), 'checks': len(saved.get('checks', [])),
                             'current_step': saved.get('current_step'), 'failure': receipt.get('failure')}
    require(receipt['format_version'] == saved['format_version'] == 1, 'receipt/archive format1')
    require(saved['native_schema'] == 'flat-typed-graph-v1', 'archive native schema')
    require(receipt['passed'] is True and receipt['workflow_complete'] is True and saved['passed'] is True and 'failure' not in receipt, 'runner completion (failure prefixes are retained, never passed)')
    require(receipt['source_guard_sha256'] == BOUND['wine-account-window-093-source.json'], 'receipt guard binding')
    require(receipt['source_sha256_before'] == receipt['source_sha256_after'] == source and receipt['source_drift'] == [], 'saved before/after732 guard')
    require(receipt['plan_counts'] == plan['counts'] and receipt['coverage_limits'] == plan['coverage_limits'], 'saved frozen plan declarations')
    require(receipt['private_state_isolated'] is True and receipt['native_game_clock_certified'] is False and receipt['old92_matrix_replayed'] is False, 'scope flags')
    require(receipt['game_capture_requests'] == receipt['chat_requests'] == 0, 'zero game/chat requests')
    require(saved['Qt_slot_exceptions'] == [], 'no Qt exceptions')
    context = 'all typed snapshots and JSON projections'
    verify_all_snapshots(saved)
    context = 'actual calls/API entries'
    calls = saved['all_targeted_calls']
    api = saved['API_entries']
    require(type(calls) is list and [call['sequence'] for call in calls] == list(range(1, len(calls) + 1)), 'targeted call sequence')
    filtered_api = [call for call in calls if call['key'] == 'calculate_damage']
    require(len(api) == len(filtered_api) and all(equal(left, right) for left, right in zip(api, filtered_api)), 'API full records equal targeted filtered records')
    expected = [(case, step, case['id'] + '/' + step['id']) for case in plan['cases'] for step in case['steps']]
    ids = [identifier for _, _, identifier in expected]
    require(len(expected) == plan['counts']['planned_states'] == 132 and len(plan['cases']) == 31, 'frozen matrix counts')
    require(len(ids) == len(set(ids)), 'unique planned state ids')
    by_step = {identifier: [] for identifier in ids}
    call_counts = Counter()
    for call in calls:
        require(call['step'] in by_step and call['case'] == call['step'].split('/', 1)[0], 'call same case/step')
        require(call['phase'] in PHASES and call['request'] in REQUESTS, 'call phase/request source enum')
        require(call['outcome'] != 'pending', 'no unfinished targeted call')
        by_step[call['step']].append(call)
        call_counts[call['key']] += 1
        if call['key'] in UNCHANGED_CALLERS:
            require(call.get('caller_unchanged') is True and 'caller_before' in call and 'caller_after' in call, 'mandatory caller pair/flag')
            require(call['caller_before']['native'] == call['caller_after']['native'], 'exact caller before/after')
        if call['key'] == 'calculate_damage':
            require(call['outcome'] in OUTCOMES, 'API outcome enum')
            if call['outcome'] == 'returned_dict':
                require(type(snapshot(call['returned'])) is dict, 'actual API dictionary return')
    actual_counts = counters(saved['actual_python_entries'])
    require(actual_counts == counters(receipt['actual_function_entries']), 'receipt/archive actual counts')
    for key, count in call_counts.items():
        require(actual_counts.get(key) == count, 'targeted actual count: ' + key)
    targeted = {key: count for key, count in actual_counts.items() if key == 'calculate_damage' or key.startswith(('AccountCache.', 'account_cache.', 'RunState.', 'MainWindow.'))}
    require(targeted == dict(call_counts), 'targeted counts have no missing call records')
    require(actual_counts.get('MainWindow.__init__') == actual_counts.get('RunState.__init__') == actual_counts.get('AccountCache.__init__') == 31, '31 actual window/run/account constructors')
    for key in ('GameCapture.capture', 'GameCapture.next_frame', 'MainWindow.sample_now', 'MainWindow.send_chat'):
        require(actual_counts.get(key, 0) == 0, 'forbidden request entry: ' + key)
    require(saved['all_rouge_main_thread_entries'] == receipt['all_rouge_main_thread_entries'], 'all-entry count archive binding')
    require(receipt['actual_API_outcomes'] == {name: sum(call['outcome'] == name for call in api) for name in OUTCOMES}, 'recomputed API outcomes')
    phase_counts = Counter(call['phase'] + '/' + call['request'] for call in api)
    require(receipt['actual_API_by_phase_and_request'] == dict(phase_counts), 'recomputed API phase/request counts')
    context = 'complete state/check plan order'
    states = saved['states']
    require([state['id'] for state in states] == ids and [check['id'] for check in saved['checks']] == ids, '132 states/checks exact plan order')
    require(saved['current_step'] == ids[-1] and receipt['checks'] == saved['checks'], 'final step and receipt checks')
    require(all(state['passed'] is True for state in states) and all(check['passed'] is True for check in saved['checks']), 'all planned states/checks passed')
    side_effects = saved['account_file_side_effects']
    for effect in side_effects:
        require(effect['step'] in by_step and effect['case'] == effect['step'].split('/', 1)[0], 'side effect same case/step')
        require(effect['method'] in ('Path.mkdir', 'Path.write_text', 'Path.replace'), 'side effect source method')
        require('public-account093-' in effect['path'].replace('\\', '/'), 'side effect isolated public path')
    numeric = errors = early = buttons = 0
    previous_case = None
    previous_ui = None
    previous_files = None
    previous_totals = {}
    latest_api = {}
    screenshot_rows = []
    api_bindings = []
    for (case, step, identifier), state, check in zip(expected, states, saved['checks']):
        context = identifier
        require(equal(snapshot(state['planned']), step), 'saved planned typed snapshot')
        ui = state['actual_ui']
        require(ui['visible'] is True, 'actual visible window flag')
        account = snapshot(ui['account_records'])
        issues = snapshot(ui['account_issues'])
        current = snapshot(ui['current_operator_state'])
        run = snapshot(ui['run_state'])
        result = snapshot(ui['result'])
        before_files = files(state['files_before'])
        after_files = files(state['files_after'])
        original_files = files(state['original_files'])
        if case.get('disk_missing'):
            original = None
        elif case.get('disk_raw') is not None:
            original = case['disk_raw'].encode('utf-8')
        else:
            original = json.dumps(case['disk_decoded'], ensure_ascii=False, allow_nan=False).encode('utf-8')
        require(state['original_account_hex'] == (None if original is None else original.hex()), 'original account exact fixture bytes')
        require(file_raw(original_files, 'account.json') == original, 'original filesystem account bytes')
        require(set(original_files) == ({'account.json'} if original is not None else set()), 'fresh original public filesystem')
        entries_before = counters(state['actual_entries_before'])
        entries_delta = counters(state['actual_entries'])
        require(entries_before == previous_totals, 'counter continuity before state')
        totals = dict(entries_before)
        for key, count in entries_delta.items():
            totals[key] = totals.get(key, 0) + count
        previous_totals = totals
        state_calls = by_step[identifier]
        state_api = [call for call in state_calls if call['key'] == 'calculate_damage']
        state_targeted_counts = dict(Counter(call['key'] for call in state_calls))
        state_targeted_delta = {key: count for key, count in entries_delta.items()
                                if key == 'calculate_damage' or key.startswith(('AccountCache.', 'account_cache.', 'RunState.', 'MainWindow.'))}
        require(state_targeted_counts == state_targeted_delta, 'each-state targeted calls equal measured delta')
        require(state['API_outcomes'] == {name: sum(call['outcome'] == name for call in state_api) for name in OUTCOMES}, 'state API outcomes same-step binding')
        require(equal(state['account_side_effects'], [effect for effect in side_effects if effect['step'] == identifier]), 'state side effect slice binding')
        require(all(signal['step'] == identifier for signal in state['signals']), 'state signal step binding')
        global_signals = [signal for signal in saved['signals'] if signal['step'] == identifier]
        require(len(state['signals']) == len(global_signals) and all(equal(left, right) for left, right in zip(state['signals'], global_signals)), 'state signal slice equals global same-step records')
        if step['action'] == 'startup':
            require(case['id'] != previous_case and state['before_run'] is None and state['before_account_records'] is None, 'fresh window startup before states')
            require(equal(before_files, original_files), 'startup pristine fixture files')
            require(sum(call['key'] == 'MainWindow.__init__' for call in state_calls) == 1, 'one actual constructor per case startup')
            require(sum(call['key'] == 'RunState.__init__' for call in state_calls) == 1, 'one real RunState constructor per case startup')
            constructor = next(call for call in state_calls if call['key'] == 'AccountCache.__init__')
            bound = constructor['source_bound_catalog_arguments']
            require(bound['profiles'] == 431 and bound['implemented_ids'] == 32 and PureWindowsPath(bound['path']).name == 'account.json', 'source-bound catalog/path arguments')
            require('public-account093-' in bound['path'].replace('\\', '/'), 'constructor public temporary path')
            start_ui = state['startup_ui_before_common']
            require(start_ui['visible'] is True and start_ui['run_state']['native'] == ui['run_state']['native'], 'startup/common actual run unchanged')
            require(counters(state['startup_actual_entries']).get('MainWindow.__init__') == 1, 'startup actual entry measurement')
            require(all(count <= state['actual_entries'].get(key, 0) for key, count in counters(state['startup_and_common_actual_entries']).items()), 'startup/common measured delta bounded by state delta')
        else:
            require(case['id'] == previous_case and equal(before_files, previous_files), 'same-case filesystem continuity')
            require(state['before_run']['native'] == previous_ui['run_state']['native'], 'same-case RunState continuity')
            require(state['before_account_records']['native'] == previous_ui['account_records']['native'], 'same-case account continuity')
        require(type(run) is dict and type(run.get('operators')) is dict and type(run.get('history')) is list and type(run.get('id')) is str, 'full saved real-run state shape')
        require(type(run.get('started_at')) in (int, float) and math.isfinite(run['started_at']), 'run started_at')
        if state['before_run'] is not None and not step.get('run_update'):
            require(state['before_run']['native'] == ui['run_state']['native'], 'non-run state unchanged native')
            require(equal(before_files.get('run.json'), after_files.get('run.json')), 'non-run disk state unchanged')
        if step.get('run_update'):
            incoming = snapshot(state['runtime_run_input'])
            require(equal(incoming['observed'], step['observed']), 'run input matches plan observation')
            applies = [call for call in state_calls if call['key'] == 'RunState.apply']
            require(len(applies) == 1 and applies[0]['outcome'] == 'returned_value' and snapshot(applies[0]['returned']) is True, 'actual RunState.apply true return')
            require(equal(snapshot(applies[0]['caller_before']), incoming), 'run actual caller matches recorded input')
            require('run.json' in after_files and equal(snapshot(after_files['run.json']['decoded']), run), 'real run save equals full memory')
            require(run['history'] and run['operators'] and run['last_read'] == incoming['captured_at'], 'actual run membership/history/time')
        if 'preserve' in step:
            require(ui['preserve_original'] is step['preserve'], 'preservation expectation')
        if case.get('protect_original_all_steps') or ui['preserve_original']:
            require(file_raw(after_files, 'account.json') == original and not state['account_side_effects'] and 'account.tmp' not in after_files, 'protected original/no mkdir-write-replace/tmp')
        if previous_ui is not None and case['id'] == previous_case and previous_ui['preserve_original']:
            require(ui['preserve_original'] is True, 'permanent session protection')
        if ui['preserve_original']:
            require('原账号档案文件已保留' in ui['training_status'], 'visible preservation notice text')
        if step.get('issue'):
            require(issues[step['issue_owner']] == step['issue'], 'per-id issue')
        if step.get('load_issue'):
            require(ui['load_issue'] == step['load_issue'], 'global load issue')
        if step.get('cleared_issue'):
            require(step['cleared_issue'] not in issues, 'per-id recovery issue cleared')
        for planned_key, actual_key in [('expected_owner', 'owner'), ('expected_level', 'level'), ('expected_override', 'level_override')]:
            if planned_key in step:
                require(equal(ui[actual_key], step[planned_key]), planned_key)
        if step['action'] == 'select':
            require(ui['owner'] == step['owner'], 'selected owner')
        if 'expected_fields' in step:
            require(equal(current.get('fields', {}), step['expected_fields']), 'expected fields')
        if step.get('unchanged_account'):
            require(ui['account_records']['native'] == state['before_account_records']['native'], 'unchanged account native')
        if step.get('unchanged_account') or step.get('unchanged_account_file'):
            require(file_raw(before_files, 'account.json') == file_raw(after_files, 'account.json'), 'unchanged account disk')
        if step.get('expect_account_changed'):
            require(file_raw(before_files, 'account.json') != file_raw(after_files, 'account.json'), 'ordinary save changes bytes')
        if step.get('expect_account_created'):
            require('account.json' not in before_files and 'account.json' in after_files, 'ordinary missing-file save')
        if case.get('unknown_id'):
            key = case['unknown_id']
            require(equal(account[key], case['disk_decoded'][key]), 'unknown id opaque record')
        if step.get('merge') == 'clean-first':
            item = account['silverash']
            expected_fields = {**case['disk_decoded']['silverash']['fields'], 'level': 65, 'trust': 55}
            require(equal(item['fields'], expected_fields) and item['skill_ranks'] == {'1': 7, '3': 10} and item['captured_at'] == 120, 'clean producer field/rank/time union')
            require(item['sources'] == {'level': 'public-synthetic-old-093', 'trust': 'public-new-093'} and item['field_times'] == {'level': 120, 'elite': 90, 'trust': 120} and item['skill_times'] == {'1': 100, '3': 120}, 'clean producer source/time maps')
            require('old_extra' not in item, 'original producer drops old extra')
        if step.get('incoming_only'):
            item = account['silverash']
            require(item['fields'] == {'elite': 2} and item['skill_ranks'] == {} and item['captured_at'] == 200, 'B2 incoming-only fields/ranks/time')
            require(item['sources'] == {'elite': 'new-public'} and item['field_times'] == {'elite': 200} and item['skill_times'] == {}, 'B2 incoming-only source/time maps')
            require('old_extra' not in item and 'invalid_skill_ranks' not in item and '未确认' in ui['trust'] and '未确认' in ui['rank'], 'B2 old discarded and preview labels')
        if step.get('chain_label'):
            chain(account['kaltsit']['extra_metadata'], step['chain_label'])
            chain(current['extra_metadata'], step['chain_label'])
        if step['action'] == 'view_top':
            require('public-view-only-093' not in account['kaltsit'], 'B1 top-level view mutation isolated')
        if step.get('deep_merge'):
            item = account['kaltsit']
            chain(item['sources']['opaque'], 'source-old')
            require(item['sources']['new'] == 'public' and 'old_extra' not in item, 'B1 producer source union/old extra drop')
            disk = snapshot(after_files['account.json']['decoded'])['kaltsit']
            chain(disk['extra_metadata'], 'new')
            chain(disk['sources']['opaque'], 'source-old')
        if step.get('sanitized'):
            require(not set(current) & RUN_METADATA and not run['operators'], 'account view has no operative run metadata/members')
            require('应急雇佣' not in ui['operator_summary'] and '本局进阶' not in ui['operator_summary'], 'sanitized summary')
        if step.get('run_precedence'):
            member = run['operators']['silverash']
            require(current['scope'] == 'run' and equal(current['fields'], member['fields']) and equal(current['skill_ranks'], member['skill_ranks']), 'real run fields/ranks precedence')
            require(current['captured_at'] == member['captured_at'] and equal(current['public_metadata'], member['public_metadata']) and '本局已确认培养' in ui['training_status'], 'real run metadata/visible confirmation')
        for call in state_api:
            if call['outcome'] == 'returned_dict':
                latest_api[case['id']] = call
        if step.get('shape'):
            early += 1
            require(check['outcome'] == 'natural_early_return' and result is None and not state_api, 'natural early return/API0')
            require(type(state['three_texts']) is str, 'early inapplicable text marker')
            if step['shape'] == 'overview':
                require(ui['owner'] is None and '本局总览暂无已确认招募干员' in ui['damage_text'], 'natural overview text')
            else:
                require('技能伤害规则尚未实现' in ui['damage_text'], 'natural unimplemented text')
                if step['shape'] == 'unimplemented-no-skill':
                    require(ui['skill'] is None and ui['rank'] == '无可用技能' and '无技能' in ui['damage_text'], 'natural no-skill profile')
        elif step.get('error'):
            errors += 1
            require(check['outcome'] == 'existing_error' and result is None and ui['damage_text'] == state['visible_error'] == step['error'], 'exact JSON error/None result')
            if step['numeric_error']:
                require(state_api and state_api[-1]['outcome'] == 'raised_exception', 'planned numeric exception')
            else:
                require(not state_api, 'preAPI JSON error has no API call')
        else:
            numeric += 1
            require(check['outcome'] == 'numerical_result' and type(result) is dict and result, 'actual numerical result')
            text = state['three_texts']
            require(type(text) is dict and set(text) == {'estimate', 'default', 'technical'} and all(type(v) is str and v for v in text.values()), 'three actual report strings')
            require(text['estimate'] == text['default'] and ui['damage_text'] == text['default'].replace(chr(160), ' '), 'default/estimate/UI report equality')
            candidate = latest_api.get(case['id'])
            require(candidate is not None, 'numerical state has an actual API provenance in this case')
            require(equal(snapshot(candidate['caller_before'])['scenario'], result['scenario']) and equal(snapshot(candidate['returned']), result['result']), 'latest same-case API binds actual scenario/result')
            api_bindings.append({'state': identifier, 'API_sequence': candidate['sequence'], 'API_step': candidate['step'], 'inherited': candidate['step'] != identifier})
            raw_scenario = result['scenario']
            if step.get('sanitized'):
                require(raw_scenario['recruitment_kind'] is None and raw_scenario['char_buff_ids'] == [] and raw_scenario['char_buffs_complete'] is False, 'sanitized numerical run fields')
            if 'expected_relic_context' in step:
                require(equal(raw_scenario['relic_context'], step['expected_relic_context']), 'needed/inactive relic context')
            if step.get('run_precedence'):
                require(raw_scenario['skill_rank'] == 7 and raw_scenario['level'] == ui['level'] and raw_scenario['elite'] == 1, 'real run scenario precedence')
        if step['action'] == 'button':
            buttons += 1
            require(any(call['key'] == 'MainWindow.calculate' and call['request'] == 'manual_button' for call in state_calls), 'actual explicit calculate button call')
        if step['action'] == 'sample':
            observation = snapshot(state['public_sample_input'])
            require(equal(observation['operator'], step['operator']) and observation['page'] == 'operator_detail' and observation['nodes'] == [], 'public synthetic observation plan binding')
            received = [call for call in state_calls if call['key'] == 'MainWindow.sample_received']
            require(len(received) == 1, 'actual sample_received slot')
            sample_input = snapshot(received[0]['caller_before'])
            require(equal(sample_input['observation'], observation), 'synthetic slot observation binding')
            require(sample_input['public_image'] == {'shape': [8, 8, 3], 'dtype': 'uint8', 'bytes_hex': '00' * (8 * 8 * 3)}, 'public synthetic8x8 zero image')
        if 'screenshot' in step:
            metadata = state['actual_screenshot']
            require(metadata['file'] == step['screenshot'] and metadata['training_status_visible'] is True and metadata['training_status'] == ui['training_status'], 'PNG exact state/name/visible status metadata')
            screenshot_rows.append({'state': identifier, **png(args.outputs_dir / step['screenshot'], metadata, report)})
        else:
            require('actual_screenshot' not in state, 'no unplanned screenshot state')
        previous_case, previous_ui, previous_files = case['id'], ui, after_files
        checked.append(identifier)
    context = 'recomputed final totals'
    require(previous_totals == actual_counts, 'state deltas recompute final entries')
    require(numeric == receipt['numeric_state_success_count'] and errors == receipt['actual_existing_error_count'] and early == receipt['actual_natural_early_return_count'], 'actual outcome totals recomputed')
    require(buttons == plan['counts']['manual_button_requests'] == saved['explicit_buttons'] == receipt['explicit_button_requests'] == 2, 'explicit button total')
    require(numeric * 3 == saved['explicit_three_text_requests'] == receipt['explicit_three_text_requests'], 'three actual text requests per numeric state')
    require(errors == sum('error' in step for _, step, _ in expected) == 7, 'declared preAPI JSON error states')
    require([row['file'] for row in screenshot_rows] == [step['screenshot'] for _, step, _ in expected if 'screenshot' in step], 'three PNG state order')
    require(set(row['file'] for row in screenshot_rows) == set(plan['expected_PNGs']) and len(screenshot_rows) == 3, 'exact planned PNG set')
    report.update(status='PASS_SAVED_ONLY_ACCOUNT093', passed=True,
                  actual={'states': len(states), 'fresh_MainWindows': actual_counts['MainWindow.__init__'], 'numerical_states': numeric,
                          'existing_error_states': errors, 'natural_early_return_states': early, 'manual_buttons': buttons,
                          'three_text_requests': numeric * 3, 'API_entries': len(api), 'targeted_calls': len(calls),
                          'snapshots_verified': snapshots_verified, 'source_hashes': len(source)},
                  numerical_API_bindings=api_bindings, PNGs=screenshot_rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outputs-dir', type=Path, default=Path('/workspace/.compat'))
    parser.add_argument('--final-dir', type=Path, default=Path('/workspace/.continuation/ui-093-account-cache-final'))
    parser.add_argument('--repo', type=Path, default=Path('/workspace/rougezhushou'))
    parser.add_argument('--formal-review', type=Path, default=Path('/workspace/.continuation/ui-093-account-cache-final-independent-review/source-only-final-review093.json'))
    parser.add_argument('--report', type=Path, required=True, help='new external output; never overwrite evidence')
    args = parser.parse_args()
    require(not args.report.exists(), 'report must be a new path')
    report_path = args.report.resolve()
    require(not any(report_path.is_relative_to(folder.resolve()) for folder in (args.repo, args.outputs_dir, args.final_dir)), 'report must be outside repository and input directories')
    inputs = [args.outputs_dir / RECEIPT_NAME, args.outputs_dir / ARCHIVE_NAME, args.formal_review] + [args.final_dir / name for name in BOUND]
    require(report_path not in {path.resolve() for path in inputs}, 'report must not be an input')
    report = {'format_version': 1, 'status': 'FAIL_SAVED_ONLY_ACCOUNT093', 'passed': False, 'project_calls': 0, 'input_bindings': {},
              'validation_kind': 'independent stdlib saved-only evidence consistency', 'product_imports': 0,
              'product_API_calls': 0, 'runner_calls': 0, 'Qt_calls': 0, 'Wine_calls': 0,
              'native_windows_verified': False, 'root_visual_review_required': True,
              'scope_limits': ['This validator does not execute or import the product or original runner/codec.',
                               'Receipt has no runner self hash or plan SHA: actual executed runner/plan provenance requires root process evidence.',
                               'Real Python RunState instance type and technical-view display transitions are runner assertions, not independently saved object/UI proofs.',
                               'PNG hash/CRC/metadata consistency does not prove visible pixel content; root must view three actual PNGs.',
                               'Existing Wine B2 covers masked old bad rank only; unmasked inert99 is outside this Wine matrix.',
                               'Failed runner prefixes are retained and never promoted to PASS.']}
    try:
        verify(args, report)
    except Exception as error:
        report['error'] = {'type': type(error).__name__, 'check': context, 'message': str(error)}
    report['completed_saved_state_checks'] = checked
    report['snapshots_verified_before_completion_or_failure'] = snapshots_verified
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open('x', encoding='utf-8') as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps({'status': report['status'], 'passed': report['passed'], 'report': str(args.report),
                      'completed_states': len(checked), 'error': report.get('error')}, ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
