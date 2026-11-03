"""Saved-only focused095 verification. No project imports or runtime replay.

This file is an unexecuted source preparation. Root must supply a fresh exact
input spec and obtain independent source review before executing it.
"""
import argparse
import ast
import gzip
import hashlib
import json
import math
import struct
import zlib
from pathlib import Path, PureWindowsPath


REFERENCE_KEY = 'selected_module_source_reference'
SECTION_ID = 'selected_module_source'
SECTION_TITLE = '所选模组 · 原件资料与覆盖边界'
TAIL = '\n\n【所选模组原件追溯】\n'
BASELINE_SCHEMA = 'focused-module-report-baseline-v1'
PLAN_SHA = 'ce1e4f002d51f8f4d7fea7db1c95dce507ef260c5f90e02152a085ad959c6a8a'
BASELINE_GUARD_SHA = '259370708fe45e974511d1c1c010901d66981ee9dc2d53e7bce1ac978d463211'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def load_json(data):
    def bad_constant(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    return json.loads(data, object_pairs_hook=strict_object,
                      parse_constant=bad_constant)


def local_path(value):
    require(type(value) is str, 'File path must be a string')
    if value.startswith('/'):
        require(not value.startswith('//') and '\\' not in value, 'No UNC or mixed POSIX path')
        path = Path(value)
    else:
        windows = PureWindowsPath(value)
        require(windows.drive.upper() == 'Z:' and windows.root == '\\' and
                len(windows.parts) >= 2 and windows.parts[1].lower() == 'workspace' and
                '..' not in windows.parts, 'Only absolute Z drive workspace paths; no UNC/parent traversal')
        path = Path('/workspace').joinpath(*windows.parts[2:])
    require(path.is_absolute() and '..' not in path.parts, 'Explicit absolute path required')
    require(path.is_relative_to('/workspace'), 'Only public workspace inputs are permitted')
    return path


def pointer(value, path):
    require(type(path) is str and (not path or path.startswith('/')), 'JSON pointer')
    if not path:
        return value
    for token in path[1:].split('/'):
        token = token.replace('~1', '/').replace('~0', '~')
        if type(value) is list:
            require(token.isdigit() and str(int(token)) == token, 'Canonical list pointer')
            value = value[int(token)]
        else:
            require(type(value) is dict and token in value, 'Missing JSON pointer: ' + path)
            value = value[token]
    return value


def exact(left, right):
    """Flat encoding retains scalar types, float hex, key order and aliases."""
    return graph(left) == graph(right)


def graph(value):
    nodes, pending, aliases = [], [], {}

    def allocate(item):
        kind = type(item)
        if kind in (dict, list, tuple) and id(item) in aliases:
            return aliases[id(item)]
        index = len(nodes)
        nodes.append(None)
        pending.append((index, item))
        if kind in (dict, list, tuple):
            aliases[id(item)] = index
        return index

    root = allocate(value)
    while pending:
        index, item = pending.pop()
        kind = type(item)
        if kind in (type(None), bool, int, str):
            node = {'type': kind.__name__, 'value': item}
        elif kind is float:
            require(math.isfinite(item), 'Nonfinite native float')
            node = {'type': 'float', 'hex': item.hex()}
        elif kind is bytes:
            node = {'type': 'bytes', 'hex': item.hex()}
        elif kind is dict:
            node = {'type': 'dict', 'items': [[allocate(k), allocate(v)]
                                            for k, v in item.items()]}
        elif kind in (list, tuple):
            node = {'type': kind.__name__, 'items': [allocate(v) for v in item]}
        else:
            raise TypeError('Unsupported native type: ' + kind.__name__)
        nodes[index] = node
    return {'schema': 'flat-typed-graph-v1', 'root': root, 'nodes': nodes}


def decode(encoded):
    require(type(encoded) is dict and set(encoded) == {'schema', 'root', 'nodes'}
            and encoded['schema'] == 'flat-typed-graph-v1', 'Exact native graph schema')
    nodes = encoded['nodes']
    require(type(nodes) is list and nodes, 'Nonempty native graph')
    values, visiting = {}, set()
    stack = [(encoded['root'], False)]
    while stack:
        index, finish = stack.pop()
        require(type(index) is int and 0 <= index < len(nodes), 'Native node reference')
        if index in values:
            continue
        node = nodes[index]
        require(type(node) is dict, 'Native node')
        kind = node['type']
        if kind in ('NoneType', 'bool', 'int', 'str'):
            expected = {'NoneType': type(None), 'bool': bool, 'int': int, 'str': str}[kind]
            require(set(node) == {'type', 'value'} and type(node['value']) is expected,
                    'Exact native scalar type')
            values[index] = node['value']
        elif kind in ('float', 'bytes'):
            require(set(node) == {'type', 'hex'} and type(node['hex']) is str,
                    'Native hex schema')
            value = float.fromhex(node['hex']) if kind == 'float' else bytes.fromhex(node['hex'])
            require(value.hex() == node['hex'] and (kind != 'float' or math.isfinite(value)),
                    'Canonical finite float / bytes hex')
            values[index] = value
        else:
            require(kind in ('dict', 'list', 'tuple') and set(node) == {'type', 'items'}
                    and type(node['items']) is list, 'Native container schema')
            if kind == 'dict':
                require(all(type(pair) is list and len(pair) == 2 for pair in node['items']),
                        'Native dict pairs')
            if not finish:
                require(index not in visiting, 'Acyclic saved native graph required')
                visiting.add(index)
                stack.append((index, True))
                children = ([v for pair in node['items'] for v in pair]
                            if kind == 'dict' else node['items'])
                stack.extend((v, False) for v in reversed(children))
            else:
                visiting.remove(index)
                if kind == 'dict':
                    values[index] = {values[k]: values[v] for k, v in node['items']}
                else:
                    items = [values[v] for v in node['items']]
                    values[index] = tuple(items) if kind == 'tuple' else items
    restored = values[encoded['root']]
    require(graph(restored) == encoded, 'Complete native type/order/alias/hex roundtrip')
    return restored


def json_text(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def scan_snapshots(value):
    """Verify every saved snapshot, including raw-file bytes separately."""
    count, queue = 0, [value]
    while queue:
        item = queue.pop()
        if type(item) is dict:
            if 'native' in item and 'native_inverse_verified' in item:
                require(item['native_inverse_verified'] is True, 'Snapshot inverse flag')
                restored = decode(item['native'])
                if item.get('schema') == 'raw-file-bytes-evidence-v1':
                    require('JSON_projection' not in item and
                            (restored is None or type(restored) is bytes), 'Raw-byte snapshot')
                    expected = {'file_exists': restored is not None,
                                'raw_hex': restored.hex() if restored is not None else None,
                                'byte_count': len(restored) if restored is not None else None,
                                'sha256': sha(restored) if restored is not None else None}
                    require(exact(item['JSON_safe_raw_bytes'], expected), 'Full raw-byte projection')
                else:
                    require('JSON_projection' in item and
                            json_text(restored) == json_text(item['JSON_projection']),
                            'Complete ordered JSON projection')
                count += 1
            else:
                queue.extend(item.values())
        elif type(item) is list:
            queue.extend(item)
    return count


class Inputs:
    def __init__(self):
        self.refs = {}

    def read(self, row):
        require(type(row) is dict and {'path', 'bytes', 'sha256'} <= set(row), 'Explicit file ref')
        require(type(row['bytes']) is int and row['bytes'] >= 0 and
                type(row['sha256']) is str and len(row['sha256']) == 64, 'File ref types')
        path = local_path(row['path'])
        data = path.read_bytes()
        require(len(data) == row['bytes'] and sha(data) == row['sha256'], 'File bytes: ' + str(path))
        actual = {'path': str(path), 'bytes': len(data), 'sha256': sha(data)}
        if str(path) in self.refs:
            require(self.refs[str(path)] == actual, 'Conflicting file ref')
        self.refs[str(path)] = actual
        return data

    def json(self, row):
        return load_json(self.read(row))


def unpack_records(inputs, row, receipt):
    compressed = inputs.read(row)
    metadata = receipt['records']
    require(type(metadata['bytes']) is int and metadata['bytes'] == len(compressed)
            and metadata['sha256'] == sha(compressed)
            and local_path(row['path']).name == metadata['file'], 'Compressed native archive binding')
    raw = gzip.decompress(compressed)
    require(type(metadata['decoded_bytes']) is int and len(raw) == metadata['decoded_bytes']
            and sha(raw) == metadata['decoded_sha256'], 'Decoded native archive binding')
    return load_json(raw)


def reduce_result(value, raw):
    """Mutate only decoded evidence; retain all old aliases and ordering."""
    report = value['report']
    matches = [(i, b) for i, b in enumerate(report['sections']) if b['id'] == SECTION_ID]
    if not raw.get('module_id'):
        require(REFERENCE_KEY not in report and not matches, 'No-module result must be wholly unchanged')
        return None, None
    require(REFERENCE_KEY in report and len(matches) == 1 and
            matches[0][0] == len(report['sections']) - 1, 'One unique final source section')
    require(len({b['id'] for b in report['sections']}) == len(report['sections']), 'Unique section ids')
    ref = report[REFERENCE_KEY]
    block = report['sections'][-1]
    require(ref['module_id'] == raw['module_id'] and block['title'] == SECTION_TITLE
            and type(block['metrics']) is list and block['metrics'] == [], 'Exact notes-only addition')
    del report[REFERENCE_KEY]
    report['sections'].pop()
    return ref, block


def strip_text(full, old, reference, technical):
    require(type(full) is str and type(old) is str, 'Formatter strings')
    if reference is None:
        require(full == old, 'No-module formatter wholly unchanged')
        return {'added': False, 'full_old_text_exact': True}
    tail = None
    without_tail = full
    if technical:
        tail = TAIL + json.dumps(reference, ensure_ascii=False, indent=2)
        require(full.endswith(tail) and full.count(TAIL) == 1, 'Exact TWO-LF technical raw suffix')
        without_tail = full[:-len(tail)]
    else:
        require(TAIL not in full, 'No technical suffix in normal text')
    marker = '\n\n【' + SECTION_TITLE + '】\n'
    require(without_tail.count(marker) == 1, 'Unique new notes section marker')
    start, added = without_tail.index(marker), len(without_tail) - len(old)
    require(added > len(marker), 'Nonempty new notes block')
    block = without_tail[start:start + added]
    require(block.startswith(marker) and '\n• ' in block and
            without_tail[:start] + without_tail[start + added:] == old, 'Every old formatter character exact')
    return {'added': True, 'exact_new_block': block, 'exact_technical_tail': tail,
            'full_old_text_exact': True}


def durable_files(durable, require_saved_run=False):
    require(durable['operator_observations_alias_is_records'] is True, 'Actual account helper alias')
    rows = durable['files']
    require(len({r['path'] for r in rows}) == len(rows), 'Unique durable file paths')
    decoded = {}
    for row in rows:
        if row['kind'] == 'directory':
            continue
        require(row['kind'] == 'file', 'Durable entry kind')
        raw = bytes.fromhex(row['raw_hex'])
        require(raw.hex() == row['raw_hex'] and len(raw) == row['bytes'] and
                sha(raw) == row['sha256'], 'Complete durable raw file bytes')
        if 'decoded' in row:
            disk = load_json(raw)
            require(json_text(disk) == json_text(decode(row['decoded']['native'])), 'Disk JSON snapshot exact')
            decoded[row['path']] = disk
    account_raw = decode(durable['account_bytes']['native'])
    account_row = next(r for r in rows if r['path'] == 'account.json')
    require(type(account_raw) is bytes and account_raw.hex() == account_row['raw_hex'], 'Account raw bytes bind files')
    require(json_text(decode(durable['account_records']['native'])) == json_text(decoded['account.json']),
            'Whole account memory and persisted records')
    if require_saved_run:
        require(json_text(decode(durable['run']['native'])) == json_text(decoded['run.json']),
                'Whole RunState memory and disk after actual apply/save')


def check_reference(raw, result, reference, block, originals, interface, binding):
    """Independently check persisted original projections and truthful links."""
    battle, modules, catalog = originals
    require(list(reference) == ['schema_version', 'operator_id', 'module_id', 'module_name',
            'module_type', 'module_level', 'source', 'raw_metadata', 'raw_owner', 'raw_phase',
            'cultivation_qualification', 'candidate_qualifications', 'existing_coverage'],
            'Exact full reference key order')
    profile = catalog['operators'][raw['operator']]
    selected = next(m for m in profile['modules'] if m['id'] == raw['module_id'])
    mid, training = raw['module_id'], result['estimate']['training']
    stage = training['module_level']
    require(type(stage) is int and reference['schema_version'] == 1 and
            reference['module_id'] == mid and reference['module_level'] == stage and
            reference['operator_id'] == profile['id'] and
            reference['module_name'] == selected['name'] and reference['module_type'] == selected['type'],
            'Selected module effective identity')
    metadata = modules['equipDict'][mid]
    expected_metadata = {k: v for k, v in metadata.items()
                         if k in interface['raw_metadata_keys_in_original_order']}
    original = battle[mid]['phases'][stage - 1]
    expected_phase = {k: original[k] for k in interface['raw_phase_key_order']}
    require(exact(reference['raw_metadata'], expected_metadata) and
            exact(reference['raw_phase'], expected_phase), 'All ordered original metadata/parts/BB/nulls')
    owner = reference['raw_owner']
    membership = modules['charEquip'][owner['charEquip_owner_id']]
    require(type(owner['membership_index']) is int and
            exact(owner['charEquip'], membership) and membership[owner['membership_index']] == mid and
            owner['charEquip_owner_id'] == (metadata['tmplId'] or metadata['charId']), 'Original full ownership')
    source = reference['source']
    selector = 'battle_equip_table.' + mid + '.phases[' + str(stage - 1) + ']'
    require(source['commit'] == 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add' and
            source['files']['battle_equip_table']['sha256'] == binding['original_battle']['sha256'] and
            source['files']['uniequip_table']['sha256'] == binding['original_modules']['sha256'] and
            source['selectors']['phase'] == selector and
            source['selectors']['metadata'] == 'uniequip_table.equipDict.' + mid and
            source['selectors']['ownership'] == 'uniequip_table.charEquip.' + owner['charEquip_owner_id']
            + '[' + str(owner['membership_index']) + ']', 'Original source and selectors')
    q = reference['cultivation_qualification']
    require(exact(q['effective_training'], {k: training[k] for k in ('elite', 'level', 'potential')})
            and type(q['uses_unconfirmed_preview_conditions']) is bool and
            q['uses_unconfirmed_preview_conditions'] == bool(raw.get('unconfirmed_training')) and
            q['scope'] == 'supplied_cultivation_only' and
            all(q[k] is None for k in ('account_mission_unlock', 'actual_equipment',
                                      'mode_or_map_applicability', 'native_attachment')) and
            q['new_reference_adds_arithmetic'] is False, 'Complete qualification scope and unknowns')
    gate = training['elite'] >= int(metadata['unlockEvolvePhase'][-1]) and training['level'] >= metadata['unlockLevel']
    require(q['module_cultivation_gate_met'] is gate, 'Module cultivation gate from original metadata')
    candidates = {}
    for i, part in enumerate(original['parts']):
        for bundle in ('addOrOverrideTalentDataBundle', 'overrideTraitDataBundle'):
            for j, candidate in enumerate((part.get(bundle) or {}).get('candidates') or ()):
                key = selector + '.parts[' + str(i) + '].' + bundle + '.candidates[' + str(j) + ']'
                condition = candidate['unlockCondition']
                phase = int(condition['phase'][-1])
                phase_met = phase <= training['elite']
                level_met = phase < training['elite'] or condition['level'] <= training['level']
                potential_met = candidate.get('requiredPotentialRank', 0) <= training['potential'] - 1
                candidate_gate = phase_met and level_met and potential_met
                candidates[key] = {'phase_gate_met': phase_met, 'level_gate_met': level_met,
                    'potential_gate_met': potential_met, 'candidate_cultivation_gate_met': candidate_gate,
                    'module_cultivation_gate_met': gate,
                    'eligible_under_supplied_cultivation': gate and candidate_gate, 'actual_activation': None}
    require(exact(reference['candidate_qualifications'], candidates), 'Every unfiltered original candidate gate')
    existing = result['report']['sections'][:-1]
    section_ids = {'talents', 'summons', 'mei_airborne_module', 'drone_trait', 'drone_aura',
                   'drone_arrival', 'gnosis_isw_a', 'mizuki_amb_y', 'haruka_healing',
                   'wisdel_summon_qualification'}
    expected_links = [{'path': '/report/sections/' + str(i), 'section_id': b['id'], 'title': b['title']}
                      for i, b in enumerate(existing) if b['id'] in section_ids or
                      b['id'].startswith(('token_duration_', 'relic_token_'))]
    expected_native = ['/' + k for k in ('mei_airborne_module_reference', 'drone_trait_reference',
        'drone_lifecycle_reference', 'gnosis_isw_a_reference', 'mizuki_amb_y_reference',
        'haruka_healing_reference', 'wisdel_summon_qualification_reference', 'token_duration_references')
        if result.get(k)]
    for i, token in enumerate(result.get('relic_token_stats', ())):
        for k in ('module_reference', 'module_cost_reference'):
            if token.get(k):
                expected_native.append('/relic_token_stats/' + str(i) + '/' + k)
    require(exact(reference['existing_coverage'], {'report_sections': expected_links,
                'native_paths': expected_native}), 'Every coverage link exact, none omitted or invented')
    for link in expected_links:
        target = pointer(result, link['path'])
        require(target['id'] == link['section_id'] and target['title'] == link['title'], 'Actual report link target')
    for path in expected_native:
        require(bool(pointer(result, path)), 'Actual nonempty native link target')
    require(type(block['notes']) is list and len(block['notes']) >= 5 and
            any(reference['module_name'] in note for note in block['notes']) and
            any('原件培养门槛' in note for note in block['notes']), 'Visible source notes scope')


def counters(values):
    require(type(values) is dict and all(type(k) is str and type(v) is int and v >= 0
                                        for k, v in values.items()), 'Measured nonnegative counters')


def ledger(data, receipt):
    calls = data['targeted_calls']
    require([r['sequence'] for r in calls] == list(range(1, len(calls) + 1))
            and all(type(r['sequence']) is int for r in calls), 'Complete ordered actual call sequence')
    by_seq = {r['sequence']: r for r in calls}
    for key, name, outcome in [('API_entries', 'calculate_damage', 'returned_dict'),
                                ('prepared_entries', '_prepare_damage', 'returned_prepared_tuple')]:
        rows = data[key]
        require(exact(rows, [r for r in calls if r['key'] == name]), 'Whole actual ledger subsequence: ' + key)
        for row in rows:
            require(row['caller_unchanged'] is True and
                    row['caller_before']['native'] == row['caller_after']['native'] and
                    row['outcome'] == outcome and not row.get('exception_events'), 'Actual caller/outcome: ' + name)
            if key == 'prepared_entries':
                prepared = decode(row['returned']['native'])
                require(type(prepared) is tuple and len(prepared) == 4 and type(prepared[0]) is dict and
                        graph(prepared[0]) == row['local_prepared_scenario_at_exit']['native'],
                        'Complete returned prepared tuple and actual local scenario')
    measured = data['actual_python_entries']
    require(exact(measured, receipt['actual_function_entries']), 'Receipt and payload measured entry counters')
    counters(measured)
    for key in {'calculate_damage', '_prepare_damage', 'MainWindow.calculate', 'RunState.apply', 'AccountCache.observe'}:
        require(measured.get(key, 0) == sum(r['key'] == key for r in calls), 'Measured targeted entries: ' + key)
    all_entries = data['all_rouge_main_thread_entries']
    scopes = data['all_rouge_entries_by_phase_and_request']
    counters(all_entries)
    totals = {}
    for scope, entries in scopes.items():
        require(type(scope) is str and '/' in scope, 'Measured phase/request scope')
        counters(entries)
        for name, count in entries.items():
            totals[name] = totals.get(name, 0) + count
    require(totals == all_entries and exact(all_entries, receipt['all_rouge_main_thread_entries']) and
            exact(scopes, receipt['all_rouge_entries_by_phase_and_request']), 'Complete phase counters sum')
    forbidden = ('GameCapture.capture', 'GameCapture.next_frame', 'GameCapture.connect', 'MainWindow.connect_game',
                 'MainWindow.sample_now', 'MainWindow.sample_received', 'MainWindow.send_chat',
                 'MainWindow.desktop_request', 'MainWindow.bind_desktop')
    require(all(measured.get(k, 0) == 0 for k in forbidden), 'No actual game/chat/desktop side effects')
    require(len(data['API_entries']) == len(data['prepared_entries']) == receipt['prepared_entries'] == 113,
            '113 actual APIs and prepared entries')
    require(exact(receipt['actual_API_outcomes'], {'returned_dict': 113, 'raised_exception': 0,
              'returned_none_or_unobserved_unwind': 0}), 'Actual API outcomes, no failure reclassification')
    return by_seq


def validate_live_alias(proof, value, data, state, label, prior, order):
    applicable = value is not None and REFERENCE_KEY in value['result']['report']
    if not applicable:
        require(proof == {'applicable': False}, 'No-reference alias probe performs no rebuild')
        return prior, {}
    required_true = ('actual_live_reference_caller_old_native_catalog_mutable_id_sets_disjoint',
        'actual_live_cached_supplement_mutable_id_set_disjoint',
        'independent_fresh_report_reference_detached_and_exact',
        'live_value_cached_supplement_prepared_and_durable_unchanged')
    require(proof['applicable'] is True and all(proof[k] is True for k in required_true),
            'Actual source-bound live/cache/fresh witness flags')
    reference = value['result']['report'][REFERENCE_KEY]
    require(proof['independent_fresh_reference']['native'] == graph(reference),
            'Independent rebuilt reference complete native value')
    cache = data['live_cached_supplement_baseline_snapshot']
    require(type(cache) is dict, 'Actual live cache snapshot exists')
    cache_sha = sha(json.dumps(cache['native'], ensure_ascii=False, allow_nan=False).encode('utf-8'))
    require(proof['live_cached_supplement_native_before_sha256'] == cache_sha ==
            proof['live_cached_supplement_native_after_sha256'], 'Actual cache before/after graph bound')
    for key in ('prior_distinct_live_or_fresh_references_checked', 'same_cached_live_result_references_retained',
                'prepared_call_sequence', 'actual_additional_API_entries', 'actual_additional_prepared_entries'):
        require(type(proof[key]) is int and proof[key] >= 0, 'Measured alias proof integer: ' + key)
    require(proof['prior_distinct_live_or_fresh_references_checked'] +
            proof['same_cached_live_result_references_retained'] == 2 * prior,
            'Every retained earlier live/fresh reference accounted for')
    require(proof['actual_additional_API_entries'] == proof['actual_additional_prepared_entries'] == 0,
            'Read-only rebuild adds no numerical/prepared API')
    require(proof['phase'] == 'live_module_reference_alias_probe' and
            proof['request'] == 'actual_cache_and_independent_prepared_report_rebuild', 'Real alias probe phase')
    eligible = [r for r in data['prepared_entries'] if r['window'] == state['window_after'] and
                (order[r['step']] < order[state['id']] or
                 (r['step'] == state['id'] and (label == 'manual' or r['phase'] != 'manual_button')))]
    require(eligible and proof['prepared_call_sequence'] == eligible[-1]['sequence'],
            'Actual latest prepared call before this capture')
    row = eligible[-1]
    require(row['caller_before']['native'] == graph({'scenario': value['scenario']}) and
            type(decode(row['returned']['native'])) is tuple and
            len(decode(row['returned']['native'])) == 4, 'Real original caller and full four-part prepared tuple')
    counters(proof['actual_entries'])
    counters(proof['all_project_entries'])
    require(proof['actual_entries'].get('calculate_damage', 0) == 0 and
            proof['actual_entries'].get('_prepare_damage', 0) == 0 and
            proof['all_project_entries'].get('rouge/reporting.py:build_report') == 1,
            'Measured one independent report rebuild and zero numerical API')
    return prior + 1, proof['all_project_entries']


def compare_api_rows(actual, baseline, originals, interface, binding):
    require(len(actual) == len(baseline), 'Complete old API/prepared count')
    for row, old in zip(actual, baseline):
        for key in ('key', 'step', 'window', 'phase', 'request', 'outcome'):
            require(type(row[key]) is type(old[key]) and row[key] == old[key], 'Actual API phase/scope: ' + key)
        for key in ('caller_before', 'caller_after'):
            require(row[key]['native'] == old[key]['native'], 'Complete old caller native')
        require(exact(row.get('exception_events'), old.get('exception_events')), 'Whole old exception events')
        if row['key'] == '_prepare_damage':
            require(row['returned']['native'] == old['returned']['native'] and
                    row['local_prepared_scenario_at_exit']['native'] ==
                    old['local_prepared_scenario_at_exit']['native'], 'Whole old prepared tuple/local native')
        else:
            result = decode(row['returned']['native'])
            raw = decode(row['caller_before']['native'])['scenario']
            original_result = decode(row['returned']['native'])
            reference, block = reduce_result(result, raw)
            if reference is not None:
                check_reference(raw, original_result, reference, block, originals, interface, binding)
            require(graph(result) == old['returned']['native'], 'Whole old numerical API result except exact additions')


def compare_capture(actual, baseline, proof, originals, interface, binding):
    require(actual['damage_result']['native'] == actual['UI']['damage_result']['native'], 'UI/result snapshot binding')
    value = decode(actual['damage_result']['native'])
    old = decode(baseline['damage_result']['native'])
    if value is None:
        require(old is None and actual['visible_status'] == baseline['visible_status'] and
                exact(actual['three_texts'], baseline['three_texts']) and
                proof['full_native_exact'] is True and proof['applicable_texts'] is False,
                'Complete unchanged error/early return')
        require(actual['three_texts']['applicable'] is False, 'No formatter for absent result')
        count = 0
    else:
        original_value = decode(actual['damage_result']['native'])
        reference, block = reduce_result(value['result'], value['scenario'])
        if reference is not None:
            check_reference(value['scenario'], original_value['result'], reference, block, originals, interface, binding)
        require(graph(value) == baseline['damage_result']['native'], 'All old native result/scenario/type/order/alias')
        three = actual['three_texts']
        require(three['applicable'] is True and three['requests'] == 3 and
                three['full_native_preserved'] is True and
                list(three['strings']) == ['estimate', 'default', 'technical'], 'Three complete actual formatter requests')
        require(three['strings']['estimate'] == three['strings']['default'], 'Estimate/default texts exact')
        for key in ('estimate', 'default', 'technical'):
            extracted = strip_text(three['strings'][key], baseline['three_texts']['strings'][key], reference,
                                  key == 'technical')
            require(exact(extracted, proof['text_additions'][key]), 'Saved exact old text/addition proof: ' + key)
        require(proof['full_native_except_exact_report_additions'] is True, 'Whole old native comparison witness')
        counters(three['actual_entries'])
        expected = {'format_estimate': 1, 'format_report_default': 2, 'format_report_technical': 1}
        for key, n in expected.items():
            require(three['actual_entries'].get(key, 0) == n and
                    proof['actual_reduced_formatter_entries'].get(key, 0) == n,
                    'Three actual original/reduced formatter entries: ' + key)
        require(three['actual_entries'].get('calculate_damage', 0) == 0 and
                proof['actual_reduced_formatter_entries'].get('calculate_damage', 0) == 0,
                'Formatter/reduced comparison does not recalculate')
        displayed = (json.dumps(original_value, ensure_ascii=False, indent=2)
                     if actual['UI']['raw_damage'] else three['strings'][
                         'technical' if actual['UI']['technical'] else 'default'])
        require(actual['visible_status'] == actual['UI']['visible_text'] == displayed.replace(chr(160), ' '),
                'Complete actual visible text and established NBSP display policy')
        count = 3
    ui = {k: v for k, v in actual['UI'].items() if k not in ('damage_result', 'visible_text')}
    old_ui = {k: v for k, v in baseline['UI'].items() if k not in ('damage_result', 'visible_text')}
    require(exact(ui, old_ui) and actual['UI']['visible'] is True, 'Whole old UI selection/cultivation/status fields')
    return value, count


def state_group(data, baseline, receipt, plan, originals, interface, binding, by_seq):
    states, old_states = data['states'], baseline['states']
    ids = [s['id'] for s in plan['steps']]
    require(len(ids) == len(set(ids)) == len(states) == len(old_states) == 41 and
            receipt['states'] == 41 and
            [s['id'] for s in states] == [s['id'] for s in old_states] == ids, 'Exact complete ordered41 plan')
    order = {key: i for i, key in enumerate(ids)}
    old_by_seq = {r['sequence']: r for r in baseline['targeted_calls']}

    def complete_scope(item, old_item, state, phase, request, key, name):
        expected = [r['sequence'] for r in by_seq.values() if r['key'] == name and
                    r['step'] == state['id'] and r['window'] == state['window_after'] and
                    r['phase'] == phase and r['request'] == request]
        old_expected = [r['sequence'] for r in old_by_seq.values() if r['key'] == name and
                        r['step'] == state['id'] and r['window'] == state['window_after'] and
                        r['phase'] == phase and r['request'] == request]
        require(exact(item[key], expected) and exact(old_item[key], old_expected) and
                exact(item[key], old_item[key]), 'Whole current/baseline phase sequence, no subset: ' + key)

    buttons, texts, prior, windows, alias_entries, comparisons = 0, 0, 0, set(), {}, []
    for state, old, planned in zip(states, old_states, plan['steps']):
        require(state['passed'] is old['passed'] is True and
                state['planned']['native'] == old['planned']['native'] == graph(planned) and
                state['window_after'] == old['window_after'], 'Actual state and full planned input')
        windows.add(state['window_after'])
        is_fresh = planned['action'] == 'fresh_window'
        labels = ('automatic',) if is_fresh else ('automatic', 'manual')
        for label in labels:
            item = state[label]
            proof = state['baseline_equivalence'][label]
            value, added_texts = compare_capture(item, old[label], proof, originals, interface, binding)
            texts += added_texts
            comparisons.append({'step': state['id'], 'label': label, **proof})
            prior, measured = validate_live_alias(item['live_reference_alias_check'],
                                                   decode(item['damage_result']['native']),
                                                   data, state, label, prior, order)
            for key, count in measured.items():
                if count:
                    alias_entries[key] = alias_entries.get(key, 0) + count
            if not is_fresh:
                kind = planned.get('expected', {}).get('kind', 'numerical_result')
                require(item['outcome'] == kind, 'Actual outcome matches planned branch')
                if kind == 'JSON_error_before_numerical_API':
                    require(value is None and item['visible_status'] == planned['expected']['message'], 'Exact JSON branch')
                elif kind == 'natural_early_return':
                    require(value is None and planned['expected']['text_contains'] in item['visible_status'], 'Actual early branch')
                else:
                    require(type(value) is dict, 'Actual numerical branch')
                render = label == 'automatic' and planned['action'] in ('technical', 'raw')
                require(item['actual_entries'].get('MainWindow.calculate', 0) == 0 if render
                        else item['actual_entries'].get('MainWindow.calculate', 0) > 0, 'Real callback branch')
                if render:
                    require(not item['API_sequences'] and not item['prepared_sequences'] and
                            item['actual_entries'].get('MainWindow.render_damage', 0) > 0, 'Real cached rendering')
                elif kind == 'numerical_result':
                    require(bool(item['API_sequences']), 'Numerical callback actually enters API')
                else:
                    require(not item['API_sequences'] and not item['prepared_sequences'], 'Pre-API error/early branch')
                for key, actual_name in (('API_sequences', 'calculate_damage'), ('prepared_sequences', '_prepare_damage')):
                    complete_scope(item, old[label], state,
                                   'automatic_action' if label == 'automatic' else 'manual_button',
                                   planned['action'] if label == 'automatic' else 'actual_compute_button',
                                   key, actual_name)
                    sequences = item[key]
                    require(len(sequences) == len(set(sequences)), 'Unique branch sequences')
                    for seq in sequences:
                        row = by_seq[seq]
                        require(row['key'] == actual_name and row['step'] == state['id'] and
                                row['window'] == state['window_after'] and
                                row['phase'] == ('automatic_action' if label == 'automatic' else 'manual_button') and
                                row['request'] == (planned['action'] if label == 'automatic' else 'actual_compute_button'),
                                'Actual branch sequence/phase binding')
        if is_fresh:
            for key, name in (('API_sequences', 'calculate_damage'), ('prepared_sequences', '_prepare_damage')):
                complete_scope(state['startup'], old['startup'], state, 'startup', 'real_MainWindow_constructor', key, name)
                for seq in state['startup'][key]:
                    row = by_seq[seq]
                    require(row['key'] == name and row['step'] == state['id'] and row['window'] == state['window_after'] and
                            row['phase'] == 'startup' and row['request'] == 'real_MainWindow_constructor',
                            'Exact actual constructor key and request phase')
        else:
            buttons += 1
            auto, manual = state['automatic'], state['manual']
            require(auto['damage_result']['native'] == manual['damage_result']['native'] and
                    auto['visible_status'] == manual['visible_status'] and
                    exact(auto['three_texts'].get('strings'), manual['three_texts'].get('strings')) and
                    state['full_native_and_three_texts_equal'] is True,
                    'Automatic/manual complete native and three texts')
            require(exact(state['durable_after_automatic'], state['durable_after']), 'Manual preserves full state/disk')
            if planned['action'] not in ('account_observation', 'run_observation'):
                require(exact(state['durable_before'], state['durable_after']), 'Preview/render/manual preserves full state/disk')
        require(exact(state['durable_after'], old['durable_after']), 'Whole deterministic memory and raw disk against baseline')
        for key in ('durable_before', 'durable_after_automatic', 'durable_after'):
            if state.get(key) is not None:
                durable_files(state[key], require_saved_run=(planned['action'] == 'run_observation' and key != 'durable_before'))
        if 'before_UI' in state:
            require(exact(state['window_before'], old['window_before']), 'Window identity transitions unchanged')
    require(buttons == receipt['explicit_button_requests'] == data['explicit_buttons'] == 39 and
            texts == receipt['explicit_three_text_requests'] == data['explicit_three_text_requests'] == 228 and
            len(windows) == receipt['fresh_windows'] == data['fresh_windows'] == 2, 'Actual39 buttons/228texts/2windows')
    require(exact(data['baseline_equivalence_checks'], comparisons) and receipt['baseline_equivalence_checks'] == len(comparisons),
            'All actual baseline comparison records')
    scope = 'live_module_reference_alias_probe/actual_cache_and_independent_prepared_report_rebuild'
    require(alias_entries == data['all_rouge_entries_by_phase_and_request'][scope], 'Every measured alias rebuild scoped entry')
    return {'states': 41, 'fresh_MainWindows': 2, 'manual_buttons': buttons,
            'three_text_requests': texts, 'live_alias_checks': prior, 'baseline_comparisons': len(comparisons)}


def gate_file(inputs, row, required):
    value = inputs.json(row)
    gates = row['JSON_pointer_gates']
    require(len(gates) == len({g['pointer'] for g in gates}), 'No repeated source gate pointers')
    supplied = {g['pointer']: g['expected'] for g in gates}
    for path, expected in required.items():
        require(path in supplied and type(supplied[path]) is type(expected) and supplied[path] == expected,
                'Required success/hash source gate: ' + path)
    for gate in gates:
        actual = pointer(value, gate['pointer'])
        require(type(actual) is type(gate['expected']) and actual == gate['expected'], 'Source gate: ' + gate['pointer'])
    return value


def check_runtime_receipt(receipt, source, runner_sha, guard_sha):
    for field in ('completed_section_increment', 'game_capture_requests', 'chat_requests', 'states',
                  'fresh_windows', 'explicit_button_requests', 'explicit_three_text_requests', 'prepared_entries'):
        require(type(receipt[field]) is int and receipt[field] >= 0, 'Actual runtime integer: ' + field)
    require(receipt['passed'] is receipt['workflow_complete'] is True and
            type(receipt['completed_section_increment']) is int and receipt['completed_section_increment'] == 0,
            'Actual focused workflow PASS, no section completion')
    require(receipt['source_drift'] == [] and receipt['private_state_isolated'] is True and
            receipt['game_capture_requests'] == receipt['chat_requests'] == 0 and
            receipt['codec_preparation_executed'] is False and receipt['old94_matrix_replayed'] is False,
            'Zero actual drift/side effects or replay')
    require(receipt['runner_sha256'] == runner_sha and receipt['source_guard_sha256'] == guard_sha and
            receipt['plan_sha256'] == PLAN_SHA and
            receipt['source_sha256_before'] == receipt['source_sha256_after'] == source,
            'Receipt self runner/plan/guard and entire source before/after')
    require(not any(k in receipt for k in ('failure', 'close_error')), 'No hidden terminal runtime failure')


def validate_baseline(data, receipt, plan, saved):
    require(data['schema'] == BASELINE_SCHEMA and data['passed'] is True and
            data['Qt_slot_exceptions'] == [], 'Actual94 complete saved baseline')
    require(scan_snapshots(data) == saved['snapshots_verified'], 'Every preserved baseline native snapshot')
    by_seq = ledger(data, receipt)
    states = data['states']
    require(len(states) == receipt['states'] == saved['states_verified'] == 41 and
            [s['id'] for s in states] == [s['id'] for s in plan['steps']], 'Whole baseline41 ordered states')
    buttons, texts = 0, 0
    for state, planned in zip(states, plan['steps']):
        require(state['passed'] is True and state['planned']['native'] == graph(planned), 'Preserved baseline planned state')
        auto = state['automatic']
        require(auto['damage_result']['native'] == auto['UI']['damage_result']['native'], 'Baseline UI/result')
        if planned['action'] != 'fresh_window':
            buttons += 1
            manual = state['manual']
            require(auto['damage_result']['native'] == manual['damage_result']['native'] and
                    auto['visible_status'] == manual['visible_status'] and
                    exact(auto['three_texts'].get('strings'), manual['three_texts'].get('strings')) and
                    exact(state['durable_after_automatic'], state['durable_after']), 'Baseline automatic/manual/durable')
            if planned['action'] not in ('account_observation', 'run_observation'):
                require(exact(state['durable_before'], state['durable_after']), 'Baseline preview preserves state')
        for item in [auto] + ([state['manual']] if 'manual' in state else []):
            three = item['three_texts']
            if three['applicable']:
                require(three['requests'] == 3 and three['full_native_preserved'] is True and
                        three['strings']['estimate'] == three['strings']['default'], 'Baseline full3texts')
                texts += 3
    require(buttons == receipt['explicit_button_requests'] == data['explicit_buttons'] == 39 and
            texts == receipt['explicit_three_text_requests'] == data['explicit_three_text_requests'] == 228 and
            receipt['fresh_windows'] == data['fresh_windows'] == 2, 'Preserved baseline actual counts')
    return by_seq


def sources(inputs, spec):
    manifest = inputs.json(spec['final_manifest'])
    require(manifest['status'] == 'STOPWRITE_ROOT_SEALED_FINAL095_SOURCE_NOT_RUNTIME_PASS', 'Actual sealed FINAL source manifest')
    payload = manifest['payload']
    names = {local_path(r['path']).name: r for r in payload}
    required_names = {'binding-diagnostic095.json', 'wine-module-report-095-binding-final.json',
        'wine-module-report-095-final.py', 'wine-module-report-095-pending-original.py',
        'wine-module-report-095-source.json', 'wine-module-report-shared095-plan.json'}
    require(len(payload) == len(names) == 6 and set(names) == required_names, 'Exact6 FINAL source payload files')
    for row in payload:
        inputs.read(row)
    runner = inputs.read(spec['final_runner'])
    require(spec['final_runner'] == names['wine-module-report-095-final.py'], 'Explicit real FINAL runner argument')
    directory = local_path(spec['final_runner']['path']).parent
    require(all(local_path(r['path']).parent == directory for r in payload), 'One exact sealed FINAL directory')
    binding_row = names['wine-module-report-095-binding-final.json']
    guard_row = names['wine-module-report-095-source.json']
    binding, guard = inputs.json(binding_row), inputs.json(guard_row)
    plan = inputs.json(names['wine-module-report-shared095-plan.json'])
    require(binding['status'] == 'ROOT_SEALED_ACTUAL95_FOCUSED_BINDING' and
            binding['actual95_guard_sha256'] == guard_row['sha256'] and
            binding['technical_tail_exact_delimiter'] == TAIL and
            names['wine-module-report-shared095-plan.json']['sha256'] == PLAN_SHA, 'Exact binding/currentguard/sharedplan')
    text = runner.decode('utf-8')
    require(text.count('PENDING_PREPARATION = False') == 1 and
            text.count("EXPECTED_BINDING_SHA256='" + binding_row['sha256'] + "'") == 1, 'Executed FINAL has exact binding SHA')
    restored = text.replace('PENDING_PREPARATION = False', 'PENDING_PREPARATION = True', 1).replace(
        "EXPECTED_BINDING_SHA256='" + binding_row['sha256'] + "'",
        "EXPECTED_BINDING_SHA256='ROOT_FINAL_BINDING_SHA256_PENDING095'", 1).encode('utf-8')
    require(restored == inputs.read(names['wine-module-report-095-pending-original.py']) and
            sha(restored) == 'b006856e8c840d64f9d682a39910ee4829bf00a5d7285075dba00267be3212db',
            'Exact observed v2 source inverse, only two sealing substitutions')
    formal = inputs.json(spec['final_source_review'])
    require(formal['source_gate_passed'] is True and formal['runtime_pass'] is False, 'Fresh FINAL formal source gate')
    pointers = spec['final_review_hash_pointers']
    expected = {'runner': spec['final_runner']['sha256'], 'binding': binding_row['sha256'],
                'guard': guard_row['sha256'], 'plan': PLAN_SHA, 'manifest': spec['final_manifest']['sha256']}
    require(set(pointers) == set(expected) and len(set(pointers.values())) == 5, 'Five explicit real formal hash pointers')
    for role, target in expected.items():
        require(type(pointer(formal, pointers[role])) is str and pointer(formal, pointers[role]) == target,
                'Formal source binds exact FINAL artifact: ' + role)
    rows = binding['required_gate_files']
    require(len(rows) == len({r['role'] for r in rows}) == 2, 'Exactly2 unique source/baseline gate roles')
    roles = {r['role']: r for r in rows}
    require(set(roles) == {'baseline_saved_only_review', 'actual95_candidate_source_review'}, 'Exact source gate roles')
    saved = gate_file(inputs, roles['baseline_saved_only_review'], {'/passed': True,
        '/actual_runtime_receipt_sha256': binding['baseline_receipt']['sha256'],
        '/actual_native_archive_sha256': binding['baseline_records']['sha256']})
    gate_file(inputs, roles['actual95_candidate_source_review'], {'/source_gate_passed': True, '/runtime_pass': False,
        '/code_manifest_sha256': binding['candidate_code_manifest']['sha256'],
        '/base_source_guard_sha256': BASELINE_GUARD_SHA, '/interface_sha256': binding['candidate_interface_artifact']['sha256']})
    gate_file(inputs, binding['single_test_formal_review'], {'/source_gate_passed': True, '/runtime_pass': False,
        '/test_manifest_sha256': binding['single_test_supplement_manifest']['sha256'],
        '/before_test_sha256': 'cea16b4243c949fd1749c1cab4f323b2f5ea7267ad69928e715ea570ab27e199',
        '/after_test_sha256': 'ad4a6381e6ec6f1a6db08cb1df0339b614883c960a1db3865d019ac08b12b554',
        '/baseline95_guard_sha256': '57e80f30aa67384225c49fd16b58bd3289fe9df41e018feca242ce132d105b82'})
    for path, metadata in saved['input_bindings'].items():
        inputs.read({'path': path, **metadata})
    require(inputs.read(binding['baseline_shell_status']) == b'0\n' and
            inputs.read(spec['baseline_saved_primary_exit']) == b'0\n', 'Preserve real captured baseline and saved-checker shell0')
    oldguard_row = next({'path': p, **v} for p, v in saved['input_bindings'].items()
                       if local_path(p).name == 'wine-module-report-baseline094-source.json')
    oldguard = inputs.json(oldguard_row)
    require(oldguard_row['sha256'] == BASELINE_GUARD_SHA, 'Original actual94 source guard')
    old_source, source = oldguard['source_sha256_after'], guard['source_sha256_after']
    require(guard['passed'] is True and len(source) == binding['actual95_maintained_count'] == 735 and
            len(old_source) == 732 and set(old_source) <= set(source), 'Whole actual735-v2 source map')
    for rel, digest in source.items():
        path = Path('/workspace/rougezhushou') / rel
        require(type(rel) is str and not Path(rel).is_absolute() and '..' not in Path(rel).parts, 'Maintained relative path')
        data = path.read_bytes()
        inputs.read({'path': str(path), 'bytes': len(data), 'sha256': digest})
    initial = inputs.json(binding['initial_core095_guard'])
    require(binding['initial_core095_guard']['sha256'] == '57e80f30aa67384225c49fd16b58bd3289fe9df41e018feca242ce132d105b82'
            and set(initial['source_sha256_after']) == set(source) and
            [p for p in source if source[p] != initial['source_sha256_after'][p]] == ['tests/test_token_duration_reference.py'],
            'Only guarded single old-test change from original core735')
    core = inputs.json(binding['candidate_code_manifest'])
    supplement = inputs.json(binding['single_test_supplement_manifest'])
    require(len(core['files']) == 5 and len(supplement['files']) == 8 and len(supplement['code_files']) == 1,
            'Original5 core and precise1-test manifest')
    for row in core['files'] + supplement['files']:
        inputs.read({'path': row['source_path'], 'bytes': row['bytes'], 'sha256': row['sha256']})
    for row in core['files'] + supplement['code_files']:
        require(source[row['destination_repo_path']] == row['sha256'], 'Maintained source exact candidate row')
    added = set(source) - set(old_source)
    changed = {p for p in old_source if source[p] != old_source[p]}
    require(added == {'rouge/data/module-source-reference.json', 'rouge/module_source_reference.py',
                     'tests/test_selected_module_source_reference.py'} and
            changed == {'rouge/reporting.py', 'scripts/verify_cloud.py', 'tests/test_token_duration_reference.py'},
            'Exact6 source changes from completed94; no unrelated source drift')
    inverse = inputs.json(binding['single_test_inverse'])
    test = Path('/workspace/rougezhushou/tests/test_token_duration_reference.py').read_text(encoding='utf-8')
    for edit in reversed(inverse['edits']):
        require(test.count(edit['new']) == 1, 'Unique original-test inverse insertion')
        test = test.replace(edit['new'], edit['old'], 1)
    require(sha(test.encode('utf-8')) == old_source['tests/test_token_duration_reference.py'], 'Whole old test inverse byte identity')
    interface = inputs.json(binding['candidate_interface_artifact'])
    require(exact(interface, binding['candidate_interface']), 'Whole source-bound interface artifact')
    tail = inputs.json(binding['technical_tail_correction_artifact'])
    require(tail['actual_complete_append_tail_prefix'] == TAIL and
            tail['exact_code_product_manifest_sha256'] == binding['candidate_code_manifest']['sha256'], 'Observed two-LF tail correction')
    battle, modules = inputs.json(binding['original_battle']), inputs.json(binding['original_modules'])
    catalog = load_json(Path('/workspace/rougezhushou/rouge/data/catalog.json').read_bytes())
    return binding, guard, plan, saved, old_source, (battle, modules, catalog), interface, names


def pngs(inputs, data, receipt, plan, refs):
    rows = data['actual_PNGs']
    require(exact(rows, receipt['actual_PNGs']) and len(rows) == len(refs) == 3, 'All3 actual PNG records')
    expected = {s['PNG']: s for s in plan['steps'] if 'PNG' in s}
    declared = {local_path(r['path']).name: r for r in refs}
    require(len(declared) == len(expected) == 3 and set(declared) == set(expected) == {r['file'] for r in rows}, 'Exact planned PNG pathset')
    states = {s['id']: s for s in data['states']}
    for row in rows:
        file = inputs.read(declared[row['file']])
        require(len(file) == row['bytes'] and sha(file) == row['sha256'], 'Physical screenshot SHA/bytes')
        require(file.startswith(b'\x89PNG\r\n\x1a\n'), 'PNG signature')
        pos, chunks = 8, []
        while pos < len(file):
            size = struct.unpack('>I', file[pos:pos + 4])[0]
            kind, payload = file[pos + 4:pos + 8], file[pos + 8:pos + 8 + size]
            require(pos + 12 + size <= len(file) and len(kind) == 4 and
                    zlib.crc32(kind + payload) & 0xffffffff == struct.unpack('>I', file[pos + 8 + size:pos + 12 + size])[0],
                    'Complete physical PNG chunk/CRC')
            chunks.append((kind, payload))
            pos += 12 + size
        require(pos == len(file) and chunks[0][0] == b'IHDR' and len(chunks[0][1]) == 13 and
                chunks[-1] == (b'IEND', b'') and any(k == b'IDAT' for k, v in chunks), 'Complete PNG structure')
        width, height = struct.unpack('>II', chunks[0][1][:8])
        require(width > 0 and height > 0, 'Physical PNG dimensions')
        planned = expected[row['file']]
        state = states[planned['id']]
        require(row['step'] == state['id'] and row['window'] == state['window_after'] and
                exact(state['actual_PNG'], row) and
                row['UI']['damage_result']['native'] == state['manual']['damage_result']['native'] and
                row['visible_status'] == row['UI']['visible_text'] == state['manual']['visible_status'] and
                row['anchor'] == ('【所选模组原件追溯】' if 'technical' in row['file'] else '【' + SECTION_TITLE + '】'),
                'Actual PNG/window/step/fullresult/text/anchor binding')
    return [inputs.refs[str(local_path(r['path']))] for r in refs]


def verify(spec, inputs):
    require(spec['status'] == 'ROOT_ACTUAL_FOCUSED095_SAVED_INPUTS_READY', 'Actual input spec required; pending template cannot run')
    own = Path(__file__).read_bytes()
    require(sha(own) == spec['verifier_sha256'], 'Exact reviewed saved-only verifier source')
    binding, guard, plan, saved, old_source, originals, interface, names = sources(inputs, spec)
    receipt, baseline_receipt = inputs.json(spec['receipt']), inputs.json(binding['baseline_receipt'])
    require(inputs.read(spec['primary_exit']) == b'0\n', 'Actual physical focused primary shell exit0')
    launch = spec['root_launch']
    prelaunch = inputs.json(spec['root_prelaunch'])
    require(spec['root_prelaunch']['sha256'] == 'd30cb93bbf4072bc50cf5ccde9eb749e3b6605704368d86deaea1bbcf9d619d3',
            'Exact preserved actual root focused95 prelaunch')
    require(prelaunch['status'] == 'SOURCE_APPROVED_ACTUAL095_FOCUSED_PRELAUNCH_RUNTIME_UNRUN' and
            prelaunch['source_gate_passed'] is True and prelaunch['runtime_pass'] is False and
            prelaunch['primary_exit_code_captured'] is False and prelaunch['actual735_sources_exact'] is True and
            prelaunch['all_six_new_outputs_prelaunch_absent'] is True and prelaunch['only_root_executes_Wine'] is True and
            prelaunch['native_Windows_game_chat_verified'] is False and
            type(prelaunch['completed_section_increment']) is int and prelaunch['completed_section_increment'] == 0,
            'Actual prelaunch is source-approved but preserves runtime/captured-status false')
    for key in ('runner', 'source_guard', 'plan', 'binding', 'final_source_manifest', 'formal_review',
                'formal_source_manifest', 'wrapper'):
        inputs.read(prelaunch[key])
    require(prelaunch['runner'] == spec['final_runner'] and
            prelaunch['plan'] == names['wine-module-report-shared095-plan.json'] and
            prelaunch['binding'] == names['wine-module-report-095-binding-final.json'] and
            prelaunch['source_guard']['bytes'] == names['wine-module-report-095-source.json']['bytes'] and
            prelaunch['source_guard']['sha256'] == names['wine-module-report-095-source.json']['sha256'] and
            prelaunch['final_source_manifest'] == spec['final_manifest'] and
            prelaunch['formal_review'] == spec['final_source_review'], 'Actual prelaunch matches exact reviewed FINAL source')
    require(prelaunch['wrapper']['path'] == '/workspace/.compat/run-wine-python.sh' and
            prelaunch['wrapper']['sha256'] == '65dd3806511e037290291ac592246abe80f346b1004b88c81e798612db4d79c8',
            'Exact existing root Wine wrapper bytes')
    require(type(prelaunch['actual_argv']) is list and len(prelaunch['actual_argv']) == 2 and
            all(type(v) is str for v in prelaunch['actual_argv']) and
            local_path(prelaunch['actual_argv'][0]) == local_path(prelaunch['wrapper']['path']) and
            local_path(prelaunch['actual_argv'][1]) == local_path(spec['final_runner']['path']) and
            prelaunch['cwd'] == '/workspace/rougezhushou' and
            local_path(prelaunch['primary_exit_code_path']) == local_path(spec['primary_exit']['path']),
            'Actual wrapper argv, unique FINAL runner, exact cwd and physical status output')
    require(launch['actual_primary_exit_captured'] is True and
            type(launch['actual_primary_exit_code']) is int and launch['actual_primary_exit_code'] == 0 and
            launch['runner'] == spec['final_runner'] and launch['manifest'] == spec['final_manifest'] and
            launch['formal_review'] == spec['final_source_review'] and launch['primary_exit'] == spec['primary_exit'] and
            exact(launch['argv'], prelaunch['actual_argv']) and launch['cwd'] == prelaunch['cwd'],
            'Actual root FINAL parameters exactly match captured prelaunch; physical shell0 is separate')
    check_runtime_receipt(receipt, guard['source_sha256_after'], spec['final_runner']['sha256'], names['wine-module-report-095-source.json']['sha256'])
    baseline_runner_sha = next(v['sha256'] for p, v in saved['input_bindings'].items()
                               if local_path(p).name == 'wine-module-report-baseline-094-for095.py')
    check_runtime_receipt(baseline_receipt, old_source, baseline_runner_sha, BASELINE_GUARD_SHA)
    require(receipt['kind'] == 'FOCUSED_ACTUAL95_SELECTED_MODULE_REPORT_GROUP' and
            baseline_receipt['kind'] == 'FRESH_ACTUAL94_FOCUSED095_BASELINE_NOT_SECTION_COMPLETION', 'Actual focused/baseline purposes')
    for field, binding_key in (('actual94_baseline_receipt_sha256', 'baseline_receipt'),
            ('actual94_baseline_records_sha256', 'baseline_records'), ('candidate_code_manifest_sha256', 'candidate_code_manifest'),
            ('single_test_supplement_manifest_sha256', 'single_test_supplement_manifest'),
            ('single_test_formal_review_sha256', 'single_test_formal_review')):
        require(receipt[field] == binding[binding_key]['sha256'], 'Runtime binds actual source prerequisite: ' + field)
    for field, filename in (('actual94_receipt_sha256', '094.json'),
                            ('actual94_closure_sha256', 'section094-archived-working-tree-closure.json')):
        hashes = {v['sha256'] for p, v in saved['input_bindings'].items() if local_path(p).name == filename}
        require(hashes == {receipt[field]} == {baseline_receipt[field]}, 'Preserved completed94 actual archival binding')
    data = unpack_records(inputs, spec['records'], receipt)
    baseline = unpack_records(inputs, binding['baseline_records'], baseline_receipt)
    validate_baseline(baseline, baseline_receipt, plan, saved)
    require(data['schema'] == 'focused-module-report-095-v1' and data['passed'] is True and
            data['native_schema'] == 'flat-typed-graph-v1' and
            data['Qt_slot_exceptions'] == [] and data['current_step'] == plan['steps'][-1]['id'], 'Complete actual focused95 archive')
    snapshots = scan_snapshots(data)
    by_seq = ledger(data, receipt)
    for key in ('API_entries', 'prepared_entries'):
        compare_api_rows(data[key], baseline[key], originals, interface, binding)
    counts = state_group(data, baseline, receipt, plan, originals, interface, binding, by_seq)
    require(exact(data['checks'], receipt['checks']) and len(data['checks']) == 41 and
            [c['id'] for c in data['checks']] == [s['id'] for s in plan['steps']] and
            all(c['passed'] is True for c in data['checks']), 'All41 actual final checks')
    require(exact(decode(data['live_cached_supplement_baseline_snapshot']['native']),
            load_json(Path('/workspace/rougezhushou/rouge/data/module-source-reference.json').read_bytes())),
            'Complete actual cache snapshot equals source-bound public supplemental data')
    require(type(data['stdlib_checkpoint_pauses']) is int and data['stdlib_checkpoint_pauses'] >= 2,
            'Materialized stdlib-only checkpoint pause count')
    checked_pngs = pngs(inputs, data, receipt, plan, spec['PNGs'])
    return {'passed': True, 'status': 'PASS_SAVED_ONLY_ACTUAL_FOCUSED095_NOT_NATIVE_WINDOWS',
        'snapshots_verified': snapshots, 'states_verified': counts['states'], 'actual': counts,
        'actual_runtime_receipt': inputs.refs[str(local_path(spec['receipt']['path']))],
        'actual_native_archive': inputs.refs[str(local_path(spec['records']['path']))],
        'actual_final_runner': inputs.refs[str(local_path(spec['final_runner']['path']))],
        'actual_final_manifest': inputs.refs[str(local_path(spec['final_manifest']['path']))],
        'actual_source_guard': inputs.refs[str(local_path(names['wine-module-report-095-source.json']['path']))],
        'actual_primary_exit': inputs.refs[str(local_path(spec['primary_exit']['path']))],
        'actual_root_prelaunch': inputs.refs[str(local_path(spec['root_prelaunch']['path']))],
        'actual_Wine_wrapper': inputs.refs[str(local_path(prelaunch['wrapper']['path']))],
        'actual_PNGs': checked_pngs,
        'actual_PNGs_viewed_by_this_validator': 0,
        'native_identity_limits': 'All internal types/order/alias/float values and source-bound live-cache/fresh witnesses verified. External live object identity remains established by frozen source assertions and the actual root execution; saved JSON does not recreate external object identity.',
        'baseline_replayed': False, 'project_imports_or_calls': 0, 'native_Windows_game_chat_verified': False,
        'complete_full095_or_section_validation': False, 'completed_section_increment': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = local_path(args.output)
    require(not output.exists(), 'Preserve every earlier saved-verification receipt')
    inputs = Inputs()
    report = {'format_version': 1, 'validation_kind': 'SAVED_ONLY', 'passed': False,
              'status': 'FAIL_SAVED_ONLY_FOCUSED095', 'project_imports_or_calls': 0,
              'completed_section_increment': 0, 'native_Windows_game_chat_verified': False}
    try:
        spec_path = local_path(args.spec)
        spec_data = spec_path.read_bytes()
        report['verifier_source'] = {'path': str(Path(__file__).resolve()), 'bytes': Path(__file__).stat().st_size,
                                     'sha256': sha(Path(__file__).read_bytes())}
        report['input_spec'] = {'path': str(spec_path), 'bytes': len(spec_data), 'sha256': sha(spec_data)}
        report.update(verify(load_json(spec_data), inputs))
    except Exception as error:
        report.update(passed=False, status='FAIL_SAVED_ONLY_FOCUSED095',
                      error={'type': type(error).__name__, 'message': str(error)})
    report['checked_file_refs'] = list(inputs.refs.values())
    with output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write('\n')
    print(json.dumps({k: report.get(k) for k in ('passed', 'status', 'states_verified', 'snapshots_verified', 'error')}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
