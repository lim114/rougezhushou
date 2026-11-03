#!/usr/bin/env python3
"""Independent saved-only focused-inputs094 verifier; stdlib and read-only inputs."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import struct
import sys
import zlib

PENDING_SHA = '0b2a41da79fb3e158c8dc933d92f046b4260cf6146068012ba6ed2cda4feb908'
PLAN_SHA = 'a61c11b82d35536c0fe9f31e5481aac9ac09cff803b945641763426a73ea5f5b'
RECEIPT_NAME = 'wine-focused-inputs-094.json'
ARCHIVE_NAME = 'wine-focused-inputs-094-records.json.gz'
FINAL_FILES = ('wine-focused-inputs-094-final.py', 'wine-focused-inputs-094-pending-original.py',
               'wine-focused-inputs-094-plan.json', 'wine-focused-inputs-094-source.json',
               'source-preflight094.json', 'source-correction-byte-evidence094.json', 'binding-diagnostic094.json')
OUTCOMES = ('returned_dict', 'raised_exception', 'returned_non_dict_or_unobserved_unwind')
TARGETED = {'calculate_damage', 'MainWindow.calculate', 'RunState.apply', 'MainWindow.apply_run_observation'}
TARGET_PATHS = {'calculate_damage': 'rouge/damage.py:calculate_damage',
                'MainWindow.calculate': 'rouge/app.py:MainWindow.calculate',
                'RunState.apply': 'rouge/run_state.py:RunState.apply',
                'MainWindow.apply_run_observation': 'rouge/app.py:MainWindow.apply_run_observation'}
FORBIDDEN = ('GameCapture.capture','GameCapture.next_frame','GameCapture.connect','MainWindow.connect_game',
             'MainWindow.sample_now','MainWindow.sample_received','MainWindow.send_chat',
             'MainWindow.desktop_request','MainWindow.bind_desktop')
PHASE_REQUESTS = {
 'runtime_project_imports':'root_sole_Wine_imports', 'probe_before':'explicit_probe',
 'public_fixture':'stdlib_public_fixture', 'startup':'real_MainWindow_constructor',
 'probe_startup':'explicit_probe', 'real_RunState_setup':'actual_apply_run_observation',
 'common_controls':'existing_context_setup', 'existing_context_setup':'existing_Qt_controls',
 'control_automatic':'affected_control_signal', 'automatic_result_probe':'explicit_probe',
 'manual_button':'actual_compute_button', 'manual_result_probe':'explicit_probe',
 'explicit_three_texts':'explicit_formatter', 'probe_after':'explicit_probe',
 'PNG_UI_probe':'actual_Qt_screenshot', 'close':'window_close'}
DIRECT_FIELDS = {'deployment_elapsed':'deployment_elapsed_seconds','healing_targets':'healing_targets',
 'defense':'enemy_defense','resistance':'enemy_resistance','cooperative':'cooperative',
 'fragile':'preexisting_fragile','charge_count':'charge_count','shield_breaks':'shield_break_count',
 'activation_count':'activation_count','companion_attack':'companion_attack','stacks':'deployment_stacks'}
context = 'initialization'
checked = []
snapshots_verified = 0
formatter_entry_sum = {}
formatter_all_entry_sum = {}


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
                continue
            if item.get('schema') == 'raw-file-bytes-evidence-v1':
                bytes_evidence(item)
                continue
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


def pointer(value, path):
    require(type(path) is str and path.startswith('/'), 'explicit actual-schema JSON pointer')
    for key in path[1:].split('/'):
        key = key.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if type(value) is list else value[key]
    return value


def safe_name(value):
    require(type(value) is str and value and '\\' not in value, 'relative artifact path')
    path = PurePosixPath(value)
    require(not path.is_absolute() and '..' not in path.parts and str(path) == value, 'normalized artifact path')
    return value


def tally(rows):
    return {name: sum(row['outcome'] == name for row in rows) for name in OUTCOMES}


def add_counts(left, right):
    result = dict(counters(left))
    for key, value in counters(right).items():
        result[key] = result.get(key, 0) + value
    return result


def bounded_counts(part, whole):
    require(all(value <= counters(whole).get(key, 0) for key, value in counters(part).items()), 'measured subphase bounded by state totals')


def expanded_plan(plan):
    result = []
    for group in plan['planned_workflow_groups']:
        for index, step in enumerate(group['steps'], 1):
            prefix = group['id'] + '/' + str(index)
            if step['kind'] == 'affected_control_edit':
                for number, value in enumerate(step['values_in_order'], 1):
                    result.append((group, step, prefix + '/value-' + str(number), value))
            else:
                result.append((group, step, prefix, None))
    require(len(result) == 90 and len(plan['planned_workflow_groups']) == 8, 'frozen expanded workflow counts')
    require(len({row[2] for row in result}) == len(result), 'unique expanded state IDs')
    require(sum(row[1]['kind'] == 'affected_control_edit' for row in result) == 62, 'frozen expanded input changes')
    return result


def controls(value, rows):
    require(type(value) is dict and list(value) == [row['widget'] for row in rows], 'complete ordered 13 controls')
    integers = {'healing_targets', 'charge_count', 'shield_breaks', 'activation_count', 'stacks'}
    for row in rows:
        name = row['widget']
        actual = value[name]
        number = snapshot(actual['value'])
        require(all(type(actual[key]) is bool for key in ('enabled', 'visible', 'hidden')), 'control flags')
        bounds = row['numeric_bounds_default_decimals']
        if bounds is None:
            require(type(number) is bool and set(actual) == {'value', 'enabled', 'visible', 'hidden'}, 'boolean control evidence')
        else:
            expected_type = int if name in integers else float
            require(type(number) is expected_type, 'actual widget exact scalar type: ' + name)
            low = snapshot(actual['minimum'])
            high = snapshot(actual['maximum'])
            require(type(low) is type(high) is expected_type and low == bounds[0], 'numeric control minimum/type')
            if name == 'healing_targets':
                require(high in (1, 2, 100), 'existing dynamic healing cap')
            else:
                require(high == bounds[1], 'numeric control original maximum')
            require(low <= number <= high, 'actual control legal value')
            if expected_type is float:
                require(actual['decimals'] == bounds[3], 'original double decimals')
            else:
                require('decimals' not in actual, 'integer spinbox has no double decimals')
    return {key: snapshot(item['value']) for key, item in value.items()}


def ui(value, rows):
    require(type(value) is dict and value['visible'] is True, 'actual visible MainWindow flag')
    require(type(value['level']) is int and type(value['level_override']) is bool, 'cultivation UI types')
    require(all(type(value[key]) is str for key in ('training_status', 'elite', 'trust', 'potential', 'module', 'rank',
        'damage_text', 'timing_text', 'relic_context_text')), 'actual UI strings')
    require(all(type(value[key]) is bool for key in ('use_run_training', 'preserve_original', 'frame_timing',
        'limit_window', 'auto_relics', 'raw_damage', 'damage_technical')), 'actual UI bools')
    require(type(snapshot(value['account_records'])) is dict and type(snapshot(value['account_issues'])) is dict, 'complete account memory evidence')
    run = snapshot(value['run_state'])
    require(type(run) is dict and type(run['id']) is str and type(run['operators']) is dict and type(run['history']) is list, 'saved full real-run shape')
    require(type(run['started_at']) in (int, float) and math.isfinite(run['started_at']), 'saved real-run start time')
    snapshot(value['current_operator_state'])
    result = snapshot(value['damage_result'])
    require(result is None or type(result) is dict, 'UI full damage-result shape')
    snapshot(value['selected_target'])
    return controls(value['controls'], rows)


def durable(value):
    require(type(value) is dict and value['operator_observations_alias_is_records'] is True, 'saved account alias flag')
    run = snapshot(value['run'])
    account = snapshot(value['account_records'])
    disk = files(value['files'])
    raw = bytes_evidence(value['account_bytes'])
    require(raw == file_raw(disk, 'account.json'), 'account byte evidence equals every saved original byte')
    require(type(run) is dict and type(account) is dict, 'full durable maps')
    if 'run.json' in disk:
        require(equal(snapshot(disk['run.json']['decoded']), run), 'real run disk/memory complete equality')
    require(not any(name == 'chat' or name.startswith('chat/') for name in disk), 'public fixture has no chat artifacts')
    return disk


def bytes_evidence(value):
    global snapshots_verified
    require(type(value) is dict and set(value) == {'schema', 'native', 'native_inverse_verified', 'JSON_safe_raw_bytes'}, 'distinct complete original-byte evidence fields; no normal JSON_projection')
    require(value['schema'] == 'raw-file-bytes-evidence-v1' and value['native_inverse_verified'] is True, 'raw byte evidence schema/inverse flag')
    restored = inverse(value['native'])
    require(restored is None or type(restored) is bytes, 'original file exact native bytes/None')
    metadata = value['JSON_safe_raw_bytes']
    require(type(metadata) is dict and set(metadata) == {'file_exists', 'raw_hex', 'byte_count', 'sha256'} and type(metadata['file_exists']) is bool, 'JSON-safe original-byte metadata fields')
    if restored is None:
        require(metadata['file_exists'] is False and metadata['raw_hex'] is metadata['byte_count'] is metadata['sha256'] is None, 'absent file represented distinctly from empty existing file')
    else:
        require(metadata['file_exists'] is True and type(metadata['raw_hex']) is str and type(metadata['byte_count']) is int and metadata['byte_count'] >= 0, 'existing byte string metadata types')
        require(restored.hex() == metadata['raw_hex'] and bytes.fromhex(metadata['raw_hex']) == restored and len(restored) == metadata['byte_count'] and sha(restored) == metadata['sha256'], 'original complete bytes independently reconstructed versus raw hex/count/SHA')
    snapshots_verified += 1
    return restored


def preserve(left, right):
    require(left['run']['native'] == right['run']['native'], 'complete RunState retained during preview')
    require(left['account_records']['native'] == right['account_records']['native'], 'complete account memory retained during preview')
    require(equal(left['account_bytes'], right['account_bytes']), 'complete original account bytes retained during preview')
    require(equal(left['files'], right['files']), 'all saved names/kinds/raw bytes retained during preview')
    require(left['operator_observations_alias_is_records'] is right['operator_observations_alias_is_records'] is True, 'storage alias retained')


def texts(value, result, visible, totals):
    global formatter_entry_sum, formatter_all_entry_sum
    require(type(value) is dict and type(value['applicable']) is bool, 'text applicability declaration')
    if result is None:
        require(value['applicable'] is False and value['visible_status'] == visible and 'strings' not in value, 'error/early result formatters inapplicable')
        return 0
    require(value['applicable'] is True and value['requests'] == 3 and value['native_preserved'] is True, 'three actual text requests and preservation')
    strings = value['strings']
    require(type(strings) is dict and set(strings) == {'estimate', 'default', 'technical'} and all(type(item) is str and item for item in strings.values()), 'complete actual three text strings')
    require(strings['estimate'] == strings['default'] and visible == strings['default'].replace(chr(160), ' '), 'three-text default/UI consistency')
    entries = counters(value['actual_entries'])
    require(entries.get('format_estimate') == 1 and entries.get('format_report_default') == 2 and entries.get('format_report_technical') == 1, 'measured explicit formatter entries including estimate delegation')
    require(all(entries.get(key, 0) == 0 for key in TARGETED | set(FORBIDDEN)), 'formatter phase has no targeted calculation/state/external requests')
    bounded_counts(entries, totals)
    project = counters(value['all_project_entries'])
    require(project.get('rouge/estimate.py:format_estimate') == 1 and project.get('rouge/reporting.py:format_report') == 3, 'formatter complete qualified entry map')
    formatter_entry_sum = add_counts(formatter_entry_sum, entries)
    formatter_all_entry_sum = add_counts(formatter_all_entry_sum, project)
    return 3


def assembly(result, actual_ui, values):
    raw = result['scenario']
    require(type(raw) is dict and type(result['result']) is dict, 'complete app scenario and post-app result')
    require(raw['operator'] == actual_ui['owner'] and raw['skill'] == actual_ui['skill'], 'raw selected owner/skill')
    # The three lawful numerical owners in this plan have no OPTIONS entries
    # shadowing these direct names. Other owners/OPTIONS are outside this test.
    require(raw['operator'] in ('silverash', 'mechanist', 'kaltsit'), 'qualified numerical owners')
    for name, field in DIRECT_FIELDS.items():
        require(equal(raw[field], values[name]), 'full source-existing direct assembly: ' + field)
    included = raw['operator'] == 'mechanist' and raw['skill'] == 2 and values['shield_duration_known'] is True
    require(('skill_duration_seconds' in raw) is included, 'duration gate source-existing inclusion')
    if included:
        require(type(raw['skill_duration_seconds']) is float and equal(raw['skill_duration_seconds'], values['shield_duration']), 'exact gated duration float')
    require(('window_seconds' in raw) is actual_ui['limit_window'], 'existing observation-window inclusion')
    if actual_ui['limit_window']:
        require(equal(raw['window_seconds'], actual_ui['window_seconds']), 'exact existing observation-window value')
    target = snapshot(actual_ui['selected_target'])
    require(('target_enemy' in raw) is bool(target), 'existing selected target inclusion')
    if target:
        require(equal(raw['target_enemy'], target), 'exact selected target identity')
        enemy = result['result']['run_resolution']['enemy']
        require(all(equal(enemy[key], target[key]) for key in ('stage_id', 'enemy_id', 'level')), 'resolved enemy identity')
        require(enemy['reference_stats']['def'] == enemy['stats']['def'] == 100 and
                enemy['reference_stats']['magicResistance'] == enemy['stats']['magicResistance'] == 20.0, 'pinned existing enemy statistics')
    calculated = result['result']
    if raw['operator'] == 'mechanist' and raw['skill'] == 2:
        reference = calculated['shield_break_reference']
        require(reference['hits_requested'] == raw['shield_break_count'] and equal(reference['manual_duration_parameter_seconds'], raw.get('skill_duration_seconds')), 'existing shield requested count/manual parameter')
        require(all(reference[key] is None for key in ('actual_break_times_seconds', 'actual_collision_times_seconds', 'actual_end_seconds', 'actual_ammunition_consumption_times_seconds')), 'unknown shield clocks stay unknown')
        require(reference['events_scheduled'] is False and reference['owner_and_structure_count_mapping_verified'] is False, 'no invented shield schedule/ownership certification')
    if raw['operator'] == 'mechanist' and raw['skill'] == 3:
        if raw['charge_count']:
            reference = calculated['charge_reference']
            require(reference['hits_requested'] == raw['charge_count'] and reference['collision_times_seconds'] is None and reference['events_scheduled'] is False and reference['full_cast_count_verified'] is False, 'existing declared charge boundary')
            require(all(calculated['estimate']['skill'][key] is None for key in ('total_damage', 'phase_damage', 'cycle_damage', 'cycle_dps')), 'unknown charge totals remain unknown')
        else:
            require('charge_reference' not in calculated, 'zero count has no charge reference')
    if raw['operator'] == 'kaltsit':
        require(calculated['estimate']['skill']['healing_targets'] == raw['healing_targets'], 'existing healing target count')
        if raw['skill'] == 2:
            require(any('治疗量为满额潜在治疗' in note for note in calculated['estimate']['notes']), 'existing potential-healing note')
        else:
            require(any('真实友方获取时钟未核验' in note for note in calculated['timing']['target_scope_notes']), 'existing unknown friendly clock note')


def selected(value, expected, rows, state_delta, selected_calls, inherited, api_bindings, state_id, label):
    actual_ui = value['UI']
    values = ui(actual_ui, rows)
    result = snapshot(value['damage_result'])
    require(value['damage_result']['native'] == actual_ui['damage_result']['native'] and value['visible_status'] == actual_ui['damage_text'], 'selected full result/UI equality')
    entries = counters(value['actual_entries'])
    require(entries.get('MainWindow.calculate', 0) > 0, 'actual MainWindow callback/button entry before result probe')
    bounded_counts(entries, state_delta)
    require(value['API_sequences'] == [row['sequence'] for row in selected_calls] and value['API_outcomes'] == tally(selected_calls), 'auto/manual exact same-phase API sequence/outcome ledger')
    wanted = expected.get('kind', 'numerical_result')
    if wanted == 'numerical_result':
        require(type(result) is dict and selected_calls and all(row['outcome'] == 'returned_dict' for row in selected_calls), 'actual automatic/manual numerical result')
        latest = selected_calls[-1]
        require(equal(snapshot(latest['caller_before'])['scenario'], result['scenario']), 'latest same-phase API caller binds complete selected scenario')
        require(equal(snapshot(latest['returned']), result['result']), 'latest same-phase API return binds complete post-app result')
        assembly(result, actual_ui, values)
        api_bindings.append({'state': state_id, 'branch': label, 'API_sequence': latest['sequence'], 'inherited': False})
    elif wanted == 'numerical_API_exception':
        require(result is None and selected_calls and all(row['outcome'] == 'raised_exception' for row in selected_calls), 'actual existing API exception/None result')
        require(value['visible_status'] == expected['message'], 'existing API exception exact visible text')
        for row in selected_calls:
            require(any(event['type'] == expected['type'] and event['message'] == expected['message'] for event in row.get('exception_events', [])), 'actual original API exception type/message')
    elif wanted in ('JSON_error_before_numerical_API', 'natural_early_return'):
        require(result is None and not selected_calls, 'existing preAPI/early None and actual API0')
        if wanted == 'JSON_error_before_numerical_API':
            require(value['visible_status'] == expected['message'], 'existing JSON gate exact visible text')
        else:
            require(expected['text_contains'] in value['visible_status'], 'natural existing early-return text')
    else:
        raise ValueError('Unknown source-qualified expected outcome: ' + wanted)
    return result, values, texts(value['three_texts'], result, value['visible_status'], state_delta), wanted


def verify_bindings(args, report):
    global context
    context = 'actual FINAL and formal source-only bindings'
    loaded = {}
    for name in FINAL_FILES:
        loaded[name] = read_bound(args.final_dir / name, report)
    require(sha(loaded[FINAL_FILES[0]]) == args.expected_final_runner_sha256, 'root-supplied exact FINAL runner SHA')
    require(sha(loaded[FINAL_FILES[1]]) == PENDING_SHA, 'qualified revised PENDING byte identity')
    require(sha(loaded[FINAL_FILES[2]]) == PLAN_SHA, 'qualified fixed plan identity')
    require(sha(loaded[FINAL_FILES[3]]) == args.expected_guard_sha256, 'actual applied094 guard SHA')
    expected_manifest = 'public-artifacts-manifest-focused-inputs094.json'
    manifest_raw = read_bound(args.final_dir / expected_manifest, report)
    manifest = strict_json(manifest_raw)
    require(set(manifest['artifacts']) == set(FINAL_FILES), 'exact announced FINAL artifact set')
    require(manifest['artifact_count_excluding_manifest_and_handoff'] == len(FINAL_FILES) and manifest['total_artifact_bytes_excluding_manifest_and_handoff'] == sum(len(data) for data in loaded.values()), 'exact announced FINAL artifact count/total bytes')
    for name, metadata in manifest['artifacts'].items():
        require(len(loaded[name]) == metadata['bytes'] and sha(loaded[name]) == metadata['sha256'], 'every sealed FINAL artifact bytes/SHA: ' + name)
    require(manifest['actual094_guard_sha256'] == args.expected_guard_sha256 and manifest['runtime_passes'] == 0 and manifest['section094_completed'] is False, 'source packet is not a runtime receipt')
    handoff = strict_json(read_bound(args.final_dir / 'handoff-focused-inputs094.json', report))
    require(handoff['manifest']['path'] == expected_manifest and handoff['manifest']['bytes'] == len(manifest_raw) and handoff['manifest']['sha256'] == sha(manifest_raw), 'FINAL manifest/handoff binding')
    for key, name in (('runner', FINAL_FILES[0]), ('source', FINAL_FILES[3])):
        require(handoff[key]['path'] == name and handoff[key]['bytes'] == len(loaded[name]) and handoff[key]['sha256'] == sha(loaded[name]), 'FINAL handoff source binding')
    require(sha(loaded['source-preflight094.json']) == 'b668c96ac4fda3c545503fb11a5b1ea0e2047de35e0dc74e89c62857e7a20254', 'qualified revised v2 source preflight')
    require(sha(loaded['source-correction-byte-evidence094.json']) == '9fe3cc7ceb3b64c74a6ca5b861e65f9d2e90df2bc52f5d2836f18e474c1e6400', 'original static v1 blocker/correction provenance retained')
    diagnostic = strict_json(loaded['binding-diagnostic094.json'])
    require(diagnostic['pending_runner_sha256'] == PENDING_SHA and diagnostic['final_runner_sha256'] == args.expected_final_runner_sha256 and diagnostic['inverse_restores_pending_byteexact'] is True and diagnostic['replacement_count'] == 3, 'exact three bindings diagnostic')
    substitutions = [
        ('PENDING_PREPARATION = True', 'PENDING_PREPARATION = False'),
        ("EXPECTED_GUARD_SHA256='PENDING_ROOT_ACTUAL_094_SOURCE_GUARD'", "EXPECTED_GUARD_SHA256='" + args.expected_guard_sha256 + "'"),
        ("GUARD=Path(__file__).with_name('wine-focused-inputs-094-pending-source.json')", "GUARD=Path(__file__).with_name('wine-focused-inputs-094-source.json')")]
    require(diagnostic['changes'] == [{'before': old, 'after': new} for old, new in substitutions], 'only declared three binding changes')
    restored = loaded[FINAL_FILES[0]].decode('utf-8')
    for old, new in reversed(substitutions):
        require(restored.count(new) == 1, 'unique FINAL binding occurrence')
        restored = restored.replace(new, old, 1)
    require(restored.encode('utf-8') == loaded[FINAL_FILES[1]], 'independent byte-exact FINAL-to-PENDING inverse')
    for key in ('project_imports', 'project_API_calls', 'helper_calls', 'formatter_calls', 'codec_executions', 'Qt_calls', 'Wine_calls', 'tests_executed', 'tracked_writes'):
        require(diagnostic[key] == 0, 'sealing did not execute product/runtime')
    actual_guard = diagnostic['actual094_guard']
    require(actual_guard['sha256'] == args.expected_guard_sha256 and actual_guard['bytes'] == len(loaded[FINAL_FILES[3]]), 'root actual guard diagnostic')
    guard_original = read_bound(Path(actual_guard['path']), report)
    require(guard_original == loaded[FINAL_FILES[3]], 'copied source guard equals root actual original')
    completion = diagnostic['completed093_receipt']
    completion_raw = read_bound(Path(completion['path']), report)
    require(len(completion_raw) == completion['bytes'] and sha(completion_raw) == completion['sha256'], 'actual completed093 receipt exact bytes/SHA')
    completion_json = strict_json(completion_raw)
    require(pointer(completion_json, completion['success_pointer']) is True and pointer(completion_json, completion['workflow_complete_pointer']) is True, 'actual completed093 source prerequisite')
    require(handoff['completed093_receipt'] == completion, 'handoff/diagnostic completed093 receipt chain')
    formal_raw = read_bound(args.formal_review, report)
    require(sha(formal_raw) == args.expected_formal_review_sha256, 'root-supplied actual fresh formal-review SHA')
    formal = strict_json(formal_raw)
    require(pointer(formal, args.review_success_pointer) is True and pointer(formal, args.review_runtime_pass_pointer) is False, 'fresh formal source gate passed without runtime claim')
    for path, expected in ((args.review_runner_sha_pointer, args.expected_final_runner_sha256),
                           (args.review_guard_sha_pointer, args.expected_guard_sha256),
                           (args.review_plan_sha_pointer, PLAN_SHA)):
        require(pointer(formal, path) == expected, 'formal reviewer explicitly bound the actual FINAL inputs')
    guard = strict_json(loaded[FINAL_FILES[3]])
    require(guard['passed'] is True and len(guard['source_sha256_after']) == 732, 'actual732 applied source guard')
    source = guard['source_sha256_after']
    require(all(sha((args.repo / safe_name(name)).read_bytes()) == expected for name, expected in source.items()), 'all actual current732 source bytes')
    maintained = {path.relative_to(args.repo).as_posix() for base in ('rouge', 'tests', 'scripts')
                  for path in (args.repo / base).rglob('*') if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts}
    require(maintained == set(source), 'actual maintained file set exact')
    return guard, strict_json(loaded[FINAL_FILES[2]])


def verify(args, report):
    global context
    guard, plan = verify_bindings(args, report)
    source = guard['source_sha256_after']
    expected = expanded_plan(plan)
    ids = [row[2] for row in expected]
    context = 'actual saved receipt and compressed transport'
    receipt_raw = read_bound(args.outputs_dir / RECEIPT_NAME, report)
    receipt = strict_json(receipt_raw)
    report['input_receipt'] = {'file': RECEIPT_NAME, 'bytes': len(receipt_raw), 'sha256': sha(receipt_raw),
        'runner_claimed_passed': receipt.get('passed'), 'runner_claimed_workflow_complete': receipt.get('workflow_complete')}
    descriptor = receipt['records']
    require(descriptor['file'] == ARCHIVE_NAME, 'actual original archive name')
    compressed = read_bound(args.outputs_dir / ARCHIVE_NAME, report)
    require(len(compressed) == descriptor['bytes'] and sha(compressed) == descriptor['sha256'], 'actual gzip exact bytes/SHA')
    raw = gzip.decompress(compressed)
    require(len(raw) == descriptor['decoded_bytes'] and sha(raw) == descriptor['decoded_sha256'], 'actual decoded gzip exact bytes/SHA')
    saved = strict_json(raw)
    report['saved_prefix'] = {'states': len(saved.get('states', [])), 'checks': len(saved.get('checks', [])),
        'current_step': saved.get('current_step'), 'failure': receipt.get('failure')}
    require(receipt['format_version'] == saved['format_version'] == 1 and saved['native_schema'] == 'flat-typed-graph-v1', 'actual saved format1')
    require(receipt['passed'] is receipt['workflow_complete'] is saved['passed'] is True and all(key not in receipt for key in ('failure', 'close_error', 'failure_screenshot')), 'complete real run; failure prefixes never promoted')
    require(not (args.outputs_dir / 'wine-focused-inputs-failure-094.png').exists(), 'unplanned actual failure screenshot absent on PASS')
    require(receipt['source_guard_sha256'] == args.expected_guard_sha256 and receipt['source_sha256_before'] == receipt['source_sha256_after'] == source and receipt['source_drift'] == [], 'saved guard and complete source before/after exact')
    require(receipt['plan_counts'] == plan['counts'] and receipt['coverage_limits'] == plan['scope_limits'], 'frozen historical plan declarations retained')
    require(receipt['private_state_isolated'] is True and receipt['native_game_clock_certified'] is False and receipt['old92_matrix_replayed'] is False and receipt['old93_corruption_matrix_replayed'] is False and receipt['codec_preparation_executed'] is False, 'actual scope flags')
    require(receipt['game_capture_requests'] == receipt['chat_requests'] == 0 and saved['Qt_slot_exceptions'] == [], 'no declared game/chat requests or Qt exceptions')
    require('Only stdlib' in receipt['checkpoint_pause_scope'] and 'no UI' in receipt['checkpoint_pause_scope'], 'source-bound checkpoint pause scope declaration')
    context = 'independent full typed snapshots and JSON projections'
    verify_all_snapshots(saved)
    context = 'actual global profile ledgers'
    calls = saved['targeted_calls']
    api = saved['API_entries']
    require(type(calls) is list and [row['sequence'] for row in calls] == list(range(1, len(calls) + 1)), 'targeted call continuous sequence')
    filtered = [row for row in calls if row['key'] == 'calculate_damage']
    require(equal(api, filtered), 'API complete rows equal targeted subset; gaps are lawful')
    call_counts = Counter()
    by_step = {name: [] for name in ids}
    kind_by_id = {row[2]: row[1]['kind'] for row in expected}
    for call in calls:
        require(call['key'] in TARGETED and call['step'] in by_step and call['group'] == call['step'].split('/', 1)[0], 'call same planned step/group and qualified key')
        require(PHASE_REQUESTS.get(call['phase']) == call['request'], 'call actual source phase/request enum')
        require(call['outcome'] != 'pending' and call['window'] in ('public-focused094-window-1', 'public-focused094-window-2'), 'finished call/public window identity')
        by_step[call['step']].append(call)
        call_counts[call['key']] += 1
        if call['key'] != 'MainWindow.calculate':
            require(call['caller_unchanged'] is True and call['caller_before']['native'] == call['caller_after']['native'], 'complete original caller before/after exact')
            if call['key'] in ('RunState.apply', 'MainWindow.apply_run_observation'):
                require(kind_by_id[call['step']] == 'public_real_RunState_setup' and call['phase'] == 'real_RunState_setup' and call['request'] == 'actual_apply_run_observation', 'real apply has no preview/context callback attribution')
        else:
            require(call['all_outputs_and_affected_controls_exist'] is True and call['outcome'] in ('returned_none', 'returned_none_with_exception_events'), 'actual calculate enters with all constructed output/control objects')
            snapshot(call['assembled_scenario_at_exit'])
            require(type(call['numerical_result_available']) is bool, 'actual calculate result availability')
        if call['key'] == 'calculate_damage':
            require(call['outcome'] in OUTCOMES, 'API outcome enum')
            require(type(snapshot(call['caller_before'])) is dict and list(snapshot(call['caller_before'])) == ['scenario'], 'full original API scenario caller')
            if call['outcome'] == 'returned_dict':
                require(type(snapshot(call['returned'])) is dict, 'actual API returned dictionary')
    entries = counters(saved['actual_python_entries'])
    require(entries == counters(receipt['actual_function_entries']), 'receipt/archive selected-entry exact binding')
    require({key: entries.get(key, 0) for key in TARGETED} == {key: call_counts.get(key, 0) for key in TARGETED}, 'actual targeted profile counts equal full saved records')
    require(entries.get('MainWindow.__init__') == entries.get('RunState.__init__') == entries.get('AccountCache.__init__') == 2, 'two actual profile-observed fresh constructors')
    require(all(entries.get(key, 0) == 0 for key in FORBIDDEN), 'no profiled forbidden game/chat entry')
    all_entries = counters(saved['all_rouge_main_thread_entries'])
    require(all_entries == counters(receipt['all_rouge_main_thread_entries']), 'receipt/archive all qualified-entry binding')
    scopes = saved['all_rouge_entries_by_phase_and_request']
    require(equal(scopes, receipt['all_rouge_entries_by_phase_and_request']), 'all phase/request-entry binding')
    aggregate = {}
    for scope, values in scopes.items():
        phase, request = scope.split('/', 1)
        require(PHASE_REQUESTS.get(phase) == request, 'qualified all-entry phase/request enum')
        aggregate = add_counts(aggregate, values)
    require(aggregate == all_entries, 'phase/request sums reconstruct every main-thread project entry')
    for key, full in TARGET_PATHS.items():
        require(all_entries.get(full, 0) == call_counts.get(key, 0), 'qualified all-entry target equals saved call ledger')
    require(receipt['actual_API_outcomes'] == tally(api), 'actual API outcome totals recomputed')
    require(receipt['actual_API_by_phase_and_request'] == dict(Counter(row['phase'] + '/' + row['request'] for row in api)), 'actual API phase/request totals recomputed')
    states = saved['states']
    require([row['id'] for row in states] == [row['id'] for row in saved['checks']] == ids, 'all90 states/checks exact expanded plan order')
    require(saved['current_step'] == ids[-1] and equal(receipt['checks'], saved['checks']), 'actual final step/check receipt binding')
    require(all(row['passed'] is True for row in states) and all(row['passed'] is True for row in saved['checks']), 'every expanded state really finished')
    require(equal(receipt['actual_PNGs'], saved['actual_PNGs']), 'actual image receipt/archive binding')
    global_signals = saved['signals']
    signal_widgets = {row['widget'] for row in plan['controls']} | {'skill', 'operator', 'timing_scenario', 'relic_context'}
    for signal in global_signals:
        require(signal['step'] in by_step and signal['group'] == signal['step'].split('/', 1)[0] and PHASE_REQUESTS.get(signal['phase']) == signal['request'], 'signal same planned source phase/group')
        require(signal['window'] in ('public-focused094-window-1', 'public-focused094-window-2') and signal['widget'] in signal_widgets, 'signal actual public window/source-observed widget identity')
        snapshot(signal['value'])
    numeric_changes = exception_changes = json_error_changes = early_changes = requests = buttons = 0
    previous = None
    previous_totals = None
    latest = {}
    screenshot_rows = []
    api_bindings = []
    off_gate = None
    elapsed_defense = None
    last_window = None
    branch_entry_sums = {'automatic': {}, 'manual': {}}
    branch_all_entry_sums = {'automatic': {}, 'manual': {}}
    context_all_entry_sum = {}
    for (group, step, identifier, requested), state, check in zip(expected, states, saved['checks']):
        context = identifier
        require(state['group'] == check['group'] == group['id'] and check['kind'] == step['kind'], 'state/check actual group/kind')
        require(equal(snapshot(state['planned']), step), 'complete original plan typed snapshot')
        before_counts = counters(state['counter_before_probe'])
        delta_counts = counters(state['actual_entries_including_probes_and_formatters'])
        if previous_totals is not None:
            require(before_counts == previous_totals, 'adjacent state counter continuity')
        previous_totals = add_counts(before_counts, delta_counts)
        require(all(value <= entries.get(key, 0) for key, value in previous_totals.items()), 'state cumulative counters bounded by final actual counts')
        state_calls = by_step[identifier]
        for key in TARGETED:
            require(delta_counts.get(key, 0) == sum(row['key'] == key and row['phase'] != 'close' for row in state_calls), 'state measured targeted delta exact (separate final close tail)')
        after_values = ui(state['after'], plan['controls'])
        after_files = durable(state['durable_after'])
        require(state['after']['run_state']['native'] == state['durable_after']['run']['native'] and state['after']['account_records']['native'] == state['durable_after']['account_records']['native'], 'after UI/durable full memory binding')
        if state['before'] is not None:
            ui(state['before'], plan['controls'])
            durable(state['durable_before'])
            require(state['before']['run_state']['native'] == state['durable_before']['run']['native'] and state['before']['account_records']['native'] == state['durable_before']['account_records']['native'], 'before UI/durable full memory binding')
        if previous is None:
            require(state['window'] is None and state['before'] is state['durable_before'] is None and step['kind'] == 'startup', 'initial fresh window pre-state genuinely absent')
        else:
            require(state['window'] == previous['window_after'] and equal(state['before'], previous['after']) and equal(state['durable_before'], previous['durable_after']), 'adjacent UI/durable/window continuity before action')
        transition = step['kind'] in ('startup', 'public_real_RunState_setup') or step.get('action') == 'fresh-independent-public-window'
        if not transition:
            require(state['window_after'] == state['window'], 'ordinary preview uses same real window')
            preserve(state['durable_before'], state['durable_after'])
        require(state['window_after'] in ('public-focused094-window-1', 'public-focused094-window-2'), 'actual after window identity')
        for call in state_calls:
            expected_window = state['window'] if call['phase'] == 'close' and step.get('action') == 'fresh-independent-public-window' else state['window_after']
            require(call['window'] == expected_window, 'actual call belongs to the correct pre/post transition window')
            if call['key'] == 'calculate_damage' and call['outcome'] == 'returned_dict':
                latest[call['window']] = call
        for signal in global_signals:
            if signal['step'] == identifier:
                expected_window = state['window'] if signal['phase'] == 'close' and step.get('action') == 'fresh-independent-public-window' else state['window_after']
                require(signal['window'] == expected_window, 'actual signal belongs to the correct transition/ordinary window')
        if step['kind'] == 'affected_control_edit':
            auto = state['automatic_before_any_manual']
            manual = state['explicit_manual_after_automatic']
            before_values = controls(state['before']['controls'], plan['controls'])
            name = step['widget']
            require(equal(snapshot(state['requested_value']), requested) and equal(snapshot(state['actual_old_value']), before_values[name]) and before_values[name] != requested, 'actual changed stimulus binds plan and previous widget value')
            require(after_values[name] == requested and type(after_values[name]) is type(before_values[name]), 'widget value actually changed without type drift')
            require(state['constructed_compatibility_stimulus'] is (not state['before']['controls'][name]['enabled'] or not state['before']['controls'][name]['visible']), 'constructed hidden/disabled stimulus declaration')
            auto_api = [row for row in state_calls if row['key'] == 'calculate_damage' and row['phase'] == 'control_automatic' and row['request'] == 'affected_control_signal']
            manual_api = [row for row in state_calls if row['key'] == 'calculate_damage' and row['phase'] == 'manual_button' and row['request'] == 'actual_compute_button']
            for selected_row, phase, request in ((auto, 'control_automatic', 'affected_control_signal'), (manual, 'manual_button', 'actual_compute_button')):
                phase_calls = [row for row in state_calls if row['phase'] == phase and row['request'] == request]
                require(counters(selected_row['actual_entries']).get('MainWindow.calculate', 0) == sum(row['key'] == 'MainWindow.calculate' for row in phase_calls), 'branch actual calculate entries equal phase-ledger rows')
                require(counters(selected_row['actual_entries']).get('calculate_damage', 0) == sum(row['key'] == 'calculate_damage' for row in phase_calls), 'branch actual API entries equal phase-ledger rows')
                bounded_counts(selected_row['actual_all_project_entries'], all_entries)
                wanted_signals = [row for row in global_signals if row['step'] == identifier and row['phase'] == phase and row['request'] == request]
                require(equal(selected_row['signals'], wanted_signals), 'branch signal slice equals exact global phase records')
                branch_name = 'automatic' if phase == 'control_automatic' else 'manual'
                branch_entry_sums[branch_name] = add_counts(branch_entry_sums[branch_name], selected_row['actual_entries'])
                branch_all_entry_sums[branch_name] = add_counts(branch_all_entry_sums[branch_name], selected_row['actual_all_project_entries'])
            auto_result, auto_values, auto_texts, kind = selected(auto, step.get('expected', {}), plan['controls'], delta_counts, auto_api, latest, api_bindings, identifier, 'automatic')
            manual_result, manual_values, manual_texts, manual_kind = selected(manual, step.get('expected', {}), plan['controls'], delta_counts, manual_api, latest, api_bindings, identifier, 'manual')
            for branch, branch_result, phase in ((auto, auto_result, 'control_automatic'), (manual, manual_result, 'manual_button')):
                calculates = [row for row in state_calls if row['key'] == 'MainWindow.calculate' and row['phase'] == phase]
                require(calculates and calculates[-1]['numerical_result_available'] is (branch_result is not None), 'actual branch final calculate availability binds selected full result')
                if branch_result is not None:
                    require(equal(snapshot(calculates[-1]['assembled_scenario_at_exit']), branch_result['scenario']), 'actual branch final calculate complete assembly binds selected scenario')
            require(kind == manual_kind == state['actual_outcome'] and state['complete_native_and_three_texts_equal'] is True, 'recorded auto/manual complete native equality declaration')
            require(auto['damage_result']['native'] == manual['damage_result']['native'] == state['after']['damage_result']['native'], 'auto/manual/after complete native scenario/result equality')
            require(equal(auto['UI'], state['after']) and equal(manual['UI'], state['after']), 'branch full recorded UI/current-state/run/account/settings/controls bind unchanged completed-state UI')
            for branch in (auto, manual):
                require(branch['UI']['run_state']['native'] == state['durable_after']['run']['native'] and branch['UI']['account_records']['native'] == state['durable_after']['account_records']['native'], 'branch complete run/account memory binds durable baseline')
            require(auto['visible_status'] == manual['visible_status'] == state['after']['damage_text'] and equal(auto['three_texts'].get('strings'), manual['three_texts'].get('strings')), 'exact auto/manual/after text equality')
            require(auto_values[name] == manual_values[name] == requested and any(row['widget'] == name and equal(snapshot(row['value']), auto_values[name]) for row in auto['signals']), 'actual affected signal carries changed widget value')
            if auto_api:
                require(auto_api[-1]['caller_before']['native'] == manual_api[-1]['caller_before']['native'], 'complete auto/manual native API caller equality')
                if kind == 'numerical_result':
                    require(auto_api[-1]['returned']['native'] == manual_api[-1]['returned']['native'], 'complete auto/manual native API return equality')
            requests += auto_texts + manual_texts
            buttons += 1
            if kind == 'numerical_result':
                numeric_changes += 1
                result = auto_result['result']
                if name == 'deployment_elapsed' and requested == 14.99:
                    elapsed_defense = result['estimate']['base_stats']['defense']
                if name == 'deployment_elapsed' and requested == 15:
                    require(elapsed_defense is not None and result['estimate']['base_stats']['defense'] == elapsed_defense + 60 and state['source_existing_15_second_defense_increment'] == 60, 'existing 15-second source defense boundary')
                if name == 'shield_duration_known' and requested is False and auto['UI']['owner'] == 'mechanist' and auto['UI']['skill'] == 2:
                    off_gate = auto['damage_result']['native']
                if name == 'shield_duration' and auto_values['shield_duration_known'] is False:
                    require(off_gate is not None and auto['damage_result']['native'] == off_gate, 'disabled retained duration omits parameter and leaves complete result unchanged')
            elif kind == 'numerical_API_exception':
                exception_changes += 1
            elif kind == 'JSON_error_before_numerical_API':
                json_error_changes += 1
            else:
                early_changes += 1
            require('context_three_texts' not in state, 'affected changes have two branches, not context formatter credit')
        else:
            result = snapshot(state['after']['damage_result'])
            requests += texts(state['context_three_texts'], result, state['after']['damage_text'], delta_counts)
            if result is not None:
                candidate = latest.get(state['window_after'])
                require(candidate is not None and equal(snapshot(candidate['caller_before'])['scenario'], result['scenario']) and equal(snapshot(candidate['returned']), result['result']), 'context full cached result binds latest actual same-window API')
                api_bindings.append({'state': identifier, 'branch': 'context', 'API_sequence': candidate['sequence'], 'API_step': candidate['step'], 'inherited': candidate['step'] != identifier})
            if 'startup' in state:
                start = state['startup']
                require(start['window'] == state['window_after'] and state['window_after'] != last_window, 'genuinely distinct real startup window identity')
                original = files(start['original_public_files'])
                fixture = plan['fixtures']['lawful_account_owners'] if step['kind'] == 'startup' else {}
                original_raw = json.dumps(fixture, ensure_ascii=False, allow_nan=False).encode('utf-8')
                require(set(original) == {'account.json'} and file_raw(original, 'account.json') == original_raw, 'fresh public fixtures exact original names/bytes')
                startup_entries = counters(start['actual_startup_entries'])
                require(startup_entries.get('MainWindow.__init__') == startup_entries.get('RunState.__init__') == startup_entries.get('AccountCache.__init__') == 1, 'one measured real constructor per startup')
                bounded_counts(startup_entries, delta_counts)
                startup_api = [row for row in state_calls if row['key'] == 'calculate_damage' and row['phase'] == 'startup']
                require(start['startup_API_outcomes'] == tally(startup_api), 'exact startup API outcomes')
                for key in TARGETED:
                    require(startup_entries.get(key, 0) == sum(row['key'] == key and row['phase'] == 'startup' for row in state_calls), 'startup selected target counts equal exact phase call rows')
                start_values = ui(start['actual_UI_after_startup'], plan['controls'])
                require(start_values['shield_duration_known'] is False and start['actual_UI_after_startup']['controls']['shield_duration']['enabled'] is False, 'startup original duration gate/disabled property')
                for row in plan['controls']:
                    default = row['boolean_default'] if row['numeric_bounds_default_decimals'] is None else row['numeric_bounds_default_decimals'][2]
                    require(start_values[row['widget']] == default, 'original startup control default unchanged')
                last_window = state['window_after']
            if step['kind'] == 'public_real_RunState_setup':
                incoming = snapshot(state['real_apply_input'])
                observed = incoming['observed']
                require(observed['selected_operator'] == 'silverash' and observed['crew_count'] is None and len(observed['operators']) == 3, 'public real apply input shape')
                members = []
                for owner in step['account_fixture_owners']:
                    member = dict(plan['fixtures']['lawful_account_owners'][owner])
                    member['scope'] = 'run'
                    members.append(member)
                require(equal(observed['operators'], members), 'actual apply uses lawful original fixture fields/ranks/scope')
                applies = [row for row in state_calls if row['key'] == 'RunState.apply']
                outer = [row for row in state_calls if row['key'] == 'MainWindow.apply_run_observation']
                require(len(applies) == len(outer) == 1 and all(row['outcome'] == 'returned_value' and snapshot(row['returned']) is True and equal(snapshot(row['caller_before']), incoming) for row in applies + outer), 'actual real apply true return and full caller input')
                run = snapshot(state['durable_after']['run'])
                require(set(run['operators']) == set(step['account_fixture_owners']) and all(member['scope'] == 'run' for member in run['operators'].values()) and run['history'] and run['last_read'] == incoming['captured_at'] and incoming['captured_at'] >= run['started_at'], 'real saved membership/history/time')
                require('run.json' in after_files and equal(snapshot(after_files['run.json']['decoded']), run), 'actual real-run save equals complete memory')
                setup_api = [row for row in state_calls if row['key'] == 'calculate_damage' and row['phase'] == 'real_RunState_setup']
                require(state['setup_API_outcomes'] == tally(setup_api), 'real setup API phase outcomes')
                bounded_counts(state['actual_setup_entries'], delta_counts)
                for key in TARGETED:
                    require(counters(state['actual_setup_entries']).get(key, 0) == sum(row['key'] == key and row['phase'] == 'real_RunState_setup' for row in state_calls), 'real setup selected target counts equal exact phase call rows')
            if 'context_actual' in state:
                context_actual = state['context_actual']
                require(context_actual['affected_input_callback_credit'] is False, 'existing context has no new-input credit')
                context_api = [row for row in state_calls if row['key'] == 'calculate_damage' and row['phase'] == 'existing_context_setup']
                require(context_actual['action_API_outcomes'] == tally(context_api), 'existing context exact action-phase outcomes')
                bounded_counts(context_actual['actual_action_entries'], delta_counts)
                for key in TARGETED:
                    require(counters(context_actual['actual_action_entries']).get(key, 0) == sum(row['key'] == key and row['phase'] == 'existing_context_setup' for row in state_calls), 'existing context selected target counts equal exact phase call rows')
                bounded_counts(context_actual['actual_all_project_action_entries'], all_entries)
                context_all_entry_sum = add_counts(context_all_entry_sum, context_actual['actual_all_project_action_entries'])
                wanted = [row for row in global_signals if row['step'] == identifier and row['phase'] == 'existing_context_setup']
                require(equal(context_actual['signals'], wanted), 'existing context global signal exact slice')
            if 'expected_maximum' in step:
                require(snapshot(state['after']['controls']['healing_targets']['maximum']) == step['expected_maximum'], 'existing healing cap switch')
            if 'expected_value' in step:
                require(after_values['healing_targets'] == step['expected_value'] and not any(row['widget'] == 'healing_targets' for row in global_signals if row['step'] == identifier), 'existing clamp retains blocked healing signal')
            if step.get('action') in ('select-owner-and-skill', 'return-to-supported-public-preview', 'select-natural-unimplemented-with-skill', 'select-natural-no-skill-profile'):
                require(state['after']['owner'] == step['owner'] and ('skill' not in step or state['after']['skill'] == step['skill']), 'source-qualified actual owner/skill selection')
            if step.get('action') == 'select-natural-no-skill-profile':
                require(state['after']['skill'] is None and state['after']['rank'] == '无可用技能', 'natural unimplemented no-skill shape')
            if step.get('action') == 'natural-empty-overview':
                require(state['after']['owner'] is None and result is None, 'genuine empty overview')
            if step['kind'] in ('planned_success_PNG', 'planned_error_PNG'):
                metadata = state['actual_screenshot']
                require(metadata['file'] == step['name'] and metadata['window'] == state['window_after'] and metadata['step'] == identifier and metadata['focus_visible'] is True and metadata['actual_view_by_root_pending'] is True, 'planned actual PNG filename/state/focus metadata')
                require(metadata['visible_status'] == state['after']['damage_text'] and equal(metadata['actual_controls'], state['after']['controls']), 'actual PNG saved status/control state')
                if step['kind'] == 'planned_success_PNG':
                    require(result is not None, 'success PNG context has actual numerical dictionary')
                else:
                    require(result is None and metadata['visible_status'] == '零长度观察窗口不能声明冲锋命中。', 'planned error PNG is exact existing exception context')
                require(len([row for row in saved['actual_PNGs'] if row['file'] == metadata['file']]) == 1 and equal(metadata, next(row for row in saved['actual_PNGs'] if row['file'] == metadata['file'])), 'state actual PNG complete metadata binds receipt/archive image ledger')
                screenshot_rows.append({'state': identifier, 'context_kind': step['kind'], **png(args.outputs_dir / safe_name(step['name']), metadata, report)})
        previous = state
        checked.append(identifier)
    context = 'recomputed actual final totals and immutable inputs'
    require(numeric_changes + exception_changes + json_error_changes + early_changes == 62, 'all actual affected outcomes accounted')
    require(buttons == saved['explicit_buttons'] == receipt['explicit_button_requests'] == 62, '62 actual recorded manual compute buttons')
    require(saved['affected_value_change_requests'] == receipt['affected_value_change_requests'] == 62 and saved['fresh_windows'] == receipt['fresh_windows'] == 2, 'actual request/window totals')
    require(requests == saved['explicit_three_text_requests'] == receipt['explicit_three_text_requests'], 'all actual applicable context/branch text requests recomputed')
    require(saved['stdlib_checkpoint_pauses'] == receipt['stdlib_checkpoint_pauses'] == len(states) + buttons + 1, 'actual pure-stdlib checkpoint count')
    for branch_name, scope in (('automatic', 'control_automatic/affected_control_signal'), ('manual', 'manual_button/actual_compute_button')):
        require(branch_all_entry_sums[branch_name] == counters(scopes.get(scope, {})), 'all branch entry maps exactly reconstruct global phase/request scope')
        for key, full in TARGET_PATHS.items():
            require(branch_entry_sums[branch_name].get(key, 0) == branch_all_entry_sums[branch_name].get(full, 0), 'branch selected counts match qualified all-entry counts')
    require(context_all_entry_sum == counters(scopes.get('existing_context_setup/existing_Qt_controls', {})), 'all existing context action maps reconstruct global action scope')
    require(formatter_all_entry_sum == counters(scopes.get('explicit_three_texts/explicit_formatter', {})), 'all explicit formatter maps reconstruct global formatter scope')
    require(formatter_entry_sum.get('format_estimate', 0) == requests // 3 and formatter_entry_sum.get('format_report_default', 0) == 2 * (requests // 3) and formatter_entry_sum.get('format_report_technical', 0) == requests // 3, 'measured complete explicit formatter request/delegation totals')
    require([row['file'] for row in screenshot_rows] == [row['file'] for row in saved['actual_PNGs']] and len(screenshot_rows) == 3, 'exact three planned image order')
    for metadata, saved_metadata in zip(screenshot_rows, saved['actual_PNGs']):
        require(metadata['bytes'] == saved_metadata['bytes'] and metadata['sha256'] == saved_metadata['sha256'], 'saved receipt PNG exact physical bindings')
    # Initial import/probe counts and the close tail are intentionally not
    # promoted to control callbacks or forced into state-delta sums.
    tail = {key: value - previous_totals.get(key, 0) for key, value in entries.items() if value != previous_totals.get(key, 0)}
    close_scope = counters(scopes.get('close/window_close', {}))
    require(all(value >= 0 for value in tail.values()) and tail.get('MainWindow.closeEvent', 0) > 0 and all(tail.get(key, 0) == 0 for key in TARGETED), 'separate actual final close tail without callback credit')
    require(entries.get('MainWindow.closeEvent', 0) == close_scope.get('rouge/app.py:MainWindow.closeEvent', 0) and tail['MainWindow.closeEvent'] <= close_scope.get('rouge/app.py:MainWindow.closeEvent', 0), 'actual closing counts bind measured close scope; no fixed helper/API totals')
    require(all(sha((args.repo / name).read_bytes()) == expected_hash for name, expected_hash in source.items()), 'current maintained source still exact after saved validation')
    for path, info in report['input_bindings'].items():
        data = Path(path).read_bytes()
        require(len(data) == info['bytes'] and sha(data) == info['sha256'], 'every bound input still byte-exact')
    report.update(status='PASS_SAVED_ONLY_FOCUSED_INPUTS094', passed=True,
        actual={'states': len(states), 'fresh_MainWindows': entries['MainWindow.__init__'],
                'affected_value_changes': 62, 'manual_buttons': buttons,
                'numerical_affected_changes': numeric_changes, 'existing_API_exception_changes': exception_changes,
                'existing_preAPI_JSON_error_changes': json_error_changes, 'natural_early_return_changes': early_changes,
                'three_text_requests': requests, 'API_entries': len(api), 'targeted_calls': len(calls),
                'source_hashes': len(source), 'snapshots_verified': snapshots_verified},
        numerical_API_bindings=api_bindings, PNGs=screenshot_rows, final_close_tail=tail,
        initial_counter_before_first_probe=states[0]['counter_before_probe'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outputs-dir', type=Path, default=Path('/workspace/.compat'))
    parser.add_argument('--final-dir', type=Path, required=True, help='actual announced sealed FINAL directory')
    parser.add_argument('--repo', type=Path, default=Path('/workspace/rougezhushou'))
    parser.add_argument('--expected-final-runner-sha256', required=True, help='root actual prelaunch/postlaunch FINAL source hash')
    parser.add_argument('--expected-guard-sha256', required=True, help='root actual applied094 guard, not predicted preparation')
    parser.add_argument('--formal-review', type=Path, required=True, help='actual announced fresh final source-only review')
    parser.add_argument('--expected-formal-review-sha256', required=True)
    parser.add_argument('--review-success-pointer', required=True, help='exact actual-schema pointer whose value is true')
    parser.add_argument('--review-runtime-pass-pointer', required=True, help='exact actual-schema pointer whose value is false')
    parser.add_argument('--review-runner-sha-pointer', required=True, help='exact actual-schema pointer to reviewed FINAL runner SHA string')
    parser.add_argument('--review-guard-sha-pointer', required=True, help='exact actual-schema pointer to reviewed actual guard SHA string')
    parser.add_argument('--review-plan-sha-pointer', required=True, help='exact actual-schema pointer to reviewed fixed plan SHA string')
    parser.add_argument('--report', type=Path, required=True, help='new external result path; never overwrite inputs/evidence')
    args = parser.parse_args()
    require(not args.report.exists(), 'new saved-validation report path')
    report_path = args.report.resolve()
    forbidden = (args.repo, args.outputs_dir, args.final_dir, Path(__file__).parent)
    require(not any(report_path.is_relative_to(folder.resolve()) for folder in forbidden) and report_path != args.formal_review.resolve(), 'report is outside repository, sealed source/runtime inputs and this frozen validator package')
    for value in (args.expected_final_runner_sha256, args.expected_guard_sha256, args.expected_formal_review_sha256):
        require(len(value) == 64 and all(char in '0123456789abcdef' for char in value), 'explicit lowercase SHA256')
    report = {'format_version': 1, 'status': 'FAIL_SAVED_ONLY_FOCUSED_INPUTS094', 'passed': False,
        'validation_kind': 'independent stdlib saved-only evidence consistency', 'input_bindings': {},
        'project_calls': 0, 'product_imports': 0, 'product_API_calls': 0,
        'runner_calls': 0, 'Qt_calls': 0, 'Wine_calls': 0, 'native_windows_verified': False,
        'root_visual_review_required': True,
        'scope_limits': [
            'This validator reads saved evidence without executing or importing the product, original runner or runner codec.',
            'The receipt does not self-identify executed runner or plan SHA; root actual launch and source pre/post hashes remain required execution provenance.',
            'Complete saved native graphs, JSON projections and separate original-byte evidence are checked independently; no normal JSON projection is claimed for bytes.',
            'Real RunState class type, button origin, checkpoint instrumentation pause scope and Python-thread boundaries remain assertions of exact reviewed source, not object/pixel proofs.',
            'Durable saved before/after equality proves all recorded bytes/names unchanged at those boundaries; it does not observe every transient system write.',
            'All-project profile ledgers cover the main Python thread, not every thread or operating-system action.',
            'The fixed plan historical source-preparation wording is retained exactly and does not itself certify current execution.',
            'The two success PNGs and one planned existing-error PNG all require root actual visual inspection; hashes/CRC/metadata do not prove visible content.',
            'Failed or unfinished saved prefixes remain failures and cannot be promoted to completed94.',
            'Compatibility validation does not certify native Windows, game timing, live game sampling or desktop chat.']}
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
