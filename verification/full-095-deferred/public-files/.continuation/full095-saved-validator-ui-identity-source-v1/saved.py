"""Independently verify saved full095 UI evidence; import no project code.

CLI: saved.py --spec ACTUAL_ROOT_SPEC.json --output FRESH_OUTPUT.json
The author does not execute this file. Null planning specs cannot validate.
"""
import argparse
import ast
import base64
import collections
import gzip
import hashlib
import json
import math
import re
import stat
import struct
import zlib
from pathlib import Path, PureWindowsPath

REPO = Path('/workspace/rougezhushou')
COMPAT = Path('/workspace/.compat')
EXPECTED_GUARD_SHA = '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
EXPECTED_UI_PENDING_MF_SHA = '20e2bcbe81232d7fac8082575b16a98c7219035948942f0cd297c8bf3316ac60'
EXPECTED_ORIGINAL_UI_SHA = '9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9'
EXPECTED_CODE_MF_SHA = '216d5c31a9bc89dbc51f0b875db073a4fe8ea8b85fb5c9b624f5d9d6f56a461a'
NATIVE_DIRECTORY = COMPAT / 'full095-ui-native-identity-retry-v1'
NATIVE_INDEX = NATIVE_DIRECTORY / 'wine-ui-full-native-index-095.json'
PNG_NAMES = ('wine-window-095-identity-retry-v1.png', 'wine-movement-reference-095-identity-retry-v1.png',
             'wine-sown-tile-control-095-identity-retry-v1.png', 'wine-medical-trait-095-identity-retry-v1.png')
REPORT = None
REGISTRY = {}
MAPPING = None


def check(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def is_sha(value):
    return type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def canonical(path):
    check(type(path) is str and Path(path).is_absolute() and '..' not in Path(path).parts,
          'Explicit absolute Linux path required')
    resolved = Path(path).resolve(strict=False)
    check(resolved.is_relative_to(Path('/workspace')), 'Only explicit public workspace files allowed')
    return str(resolved)


def metadata(path):
    path = Path(canonical(str(path)))
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': sha(data)}


def read_ref(reference):
    check(type(reference) is dict and {'path', 'bytes', 'sha256'} <= set(reference),
          'Actual full file reference required')
    check(integer(reference['bytes']) and is_sha(reference['sha256']), 'Actual bytes/digest types')
    path = Path(reference['path'])
    check(path.is_absolute() and not path.is_symlink() and path.is_file(), 'Actual regular file absent/symlinked')
    key = canonical(str(path))
    data = path.read_bytes()
    check(len(data) == reference['bytes'] and sha(data) == reference['sha256'], 'Exact input bytes/SHA: ' + key)
    full = {'path': key, 'bytes': len(data), 'sha256': sha(data)}
    prior = REPORT['checked_file_refs'].get(key)
    check(prior is None or prior == full, 'Same canonical input changed during validation')
    REPORT['checked_file_refs'][key] = full
    return data


def registered(reference):
    key = canonical(reference['path'])
    check(key in REGISTRY, 'UI binding input was not explicitly supplied by root: ' + key)
    full = REGISTRY[key]
    check(reference['sha256'] == full['sha256'] and ('bytes' not in reference or reference['bytes'] == full['bytes']),
          'Actual UI binding does not equal explicit root input ref')
    return read_ref(full)


def pointer(value, expression):
    check(type(expression) is str and (expression == '' or expression.startswith('/')), 'Explicit real JSON pointer required')
    if not expression:
        return value
    for token in expression[1:].split('/'):
        token = token.replace('~1', '/').replace('~0', '~')
        value = value[int(token)] if type(value) is list else value[token]
    return value


def literal(source, name):
    tree = ast.parse(source)
    found = [n for n in tree.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    check(len(found) == 1, 'Unique actual FINAL literal: ' + name)
    return ast.literal_eval(found[0].value)


def actual_wine_mapping(spec):
    row = spec['wine_path_mapping']
    check(row['drive'] == 'Z:' and row['drive_link'] == '/workspace/.compat/wine-prefix/dosdevices/z:',
          'Actual configured Wine mapping source binding required')
    link = Path(row['drive_link'])
    check(link.is_symlink(), 'Actual Wine drive link absent')
    actual = str(link.resolve(strict=True))
    check(Path(actual).is_absolute() and '..' not in Path(actual).parts and actual == row['linux_root'],
          'Actual Wine mapping target differs from root declared target')
    proof = json.loads(read_ref(row['proof']))
    p = row['pointers']
    check(pointer(proof, p['drive_link']) == row['drive_link']
          and pointer(proof, p['linux_root']) == actual
          and pointer(proof, p['wrapper_sha256']) == spec['wine_wrapper']['sha256'],
          'Actual mapping proof does not bind real drive target and wrapper bytes')
    return {'drive': 'Z:', 'linux_root': actual}


def linux_path(value):
    if type(value) is str and value.startswith('/'):
        return canonical(value)
    check(type(value) is str, 'Actual path must be a string')
    win = PureWindowsPath(value)
    check(win.drive == MAPPING['drive'] and win.root == '\\' and '..' not in win.parts,
          'Only actual configured absolute Z drive paths accepted; UNC/other drive/traversal rejected')
    # PureWindowsPath collapses repeated separators. Never test a guessed Z:\\workspace string prefix.
    target = Path(MAPPING['linux_root']).joinpath(*win.parts[1:])
    return canonical(str(target))


def normalized_record(row):
    result = dict(row)
    result['path'] = linux_path(row['path'])
    return result


def normalized_binding(binding):
    result = dict(binding)
    for key in ('source_guard', 'candidate_manifest', 'implementation_freeze',
                'technical_tail_correction_artifact', 'actual94_receipt', 'actual94_guard',
                'baseline_receipt', 'baseline_saved_verifier'):
        result[key] = normalized_record(binding[key])
    for key in ('baseline_files', 'qualified_reference_provenance'):
        result[key] = [normalized_record(row) for row in binding[key]]
    result['additional_formal_artifacts'] = [
        {**normalized_record(row), 'formal_review': normalized_record(row['formal_review'])}
        for row in binding.get('additional_formal_artifacts', [])]
    return result


def maintained():
    return {path.relative_to(REPO).as_posix(): sha(path.read_bytes())
            for folder in ('rouge', 'tests', 'scripts') for path in sorted((REPO / folder).rglob('*'))
            if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts}


def source_map(value):
    check(type(value) is dict and value, 'Nonempty actual maintained map required')
    for name, digest in value.items():
        check(type(name) is str and name and not Path(name).is_absolute() and '..' not in Path(name).parts
              and is_sha(digest), 'Actual safe string source key/digest required')
    return value

def graph(value):
    nodes, queue, aliases = [], [], {}

    def allocate(item):
        kind = type(item)
        if kind in (dict, list, tuple) and id(item) in aliases:
            return aliases[id(item)]
        index = len(nodes)
        nodes.append(None)
        queue.append((index, item))
        if kind in (dict, list, tuple):
            aliases[id(item)] = index
        return index

    root = allocate(value)
    while queue:
        index, item = queue.pop()
        kind = type(item)
        if kind in (type(None), bool, int, str):
            nodes[index] = {'type': kind.__name__, 'value': item}
        elif kind is float:
            nodes[index] = {'type': 'float', 'hex': item.hex()}
        elif kind is bytes:
            nodes[index] = {'type': 'bytes', 'hex': item.hex()}
        elif kind is dict:
            nodes[index] = {'type': 'dict', 'items': [
                [allocate(key), allocate(child)] for key, child in item.items()]}
        elif kind in (list, tuple):
            nodes[index] = {'type': kind.__name__, 'items': [
                allocate(child) for child in item]}
        else:
            raise TypeError(kind.__name__)
    return {'schema': 'flat-typed-graph-v1', 'root': root, 'nodes': nodes}

def decode(encoded):
    check(encoded['schema'] == 'flat-typed-graph-v1', 'native schema')
    nodes = encoded['nodes']
    values, visiting = {}, set()
    stack = [(encoded['root'], False)]
    while stack:
        index, finish = stack.pop()
        check(type(index) is int and 0 <= index < len(nodes), 'node reference')
        if index in values:
            continue
        node = nodes[index]
        kind = node['type']
        if kind in ('NoneType', 'bool', 'int', 'str'):
            types = {'NoneType': type(None), 'bool': bool, 'int': int, 'str': str}
            check(type(node['value']) is types[kind], 'native scalar type')
            values[index] = node['value']
        elif kind == 'float':
            value = float.fromhex(node['hex'])
            check(math.isfinite(value) and value.hex() == node['hex'], 'float hex')
            values[index] = value
        elif kind == 'bytes':
            values[index] = bytes.fromhex(node['hex'])
            check(values[index].hex() == node['hex'], 'bytes hex')
        else:
            check(kind in ('dict', 'list', 'tuple'), 'container type')
            if not finish:
                check(index not in visiting, 'acyclic native graph')
                visiting.add(index)
                stack.append((index, True))
                children = ([child for pair in node['items'] for child in pair]
                            if kind == 'dict' else node['items'])
                stack.extend((child, False) for child in reversed(children)
                             if child not in values)
            else:
                visiting.remove(index)
                if kind == 'dict':
                    values[index] = {values[key]: values[child]
                                     for key, child in node['items']}
                else:
                    items = [values[child] for child in node['items']]
                    values[index] = tuple(items) if kind == 'tuple' else items
    result = values[encoded['root']]
    check(graph(result) == encoded, 'complete type/order/alias roundtrip')
    return result

def encoded_json(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':'))


def snapshot_value(value, role='ordinary'):
    check(type(value) is dict and value.get('native_inverse_verified') is True,
          'Source-role snapshot is a complete wrapper with inverse flag True')
    if role == 'ordinary':
        check(list(value) == ['native', 'JSON_projection', 'native_inverse_verified'],
              'Ordinary snapshot has exactly the producer three keys; ordinary None cannot self-select raw')
        restored = decode(value['native'])
        check(encoded_json(restored) == encoded_json(value['JSON_projection']),
              'Complete ordinary ordered JSON projection equals full native inverse without scalar coercion')
    elif role == 'exception-args':
        check(list(value) == ['native', 'native_inverse_verified', 'JSON_projection_applicable']
              and value['JSON_projection_applicable'] is False,
              'Exact producer native-only exception args wrapper')
        restored = decode(value['native'])
        check(type(restored) is tuple, 'Actual exception args are a complete native tuple')
    elif role == 'account-file-bytes':
        check(list(value) == ['schema', 'native', 'native_inverse_verified', 'JSON_safe_raw_bytes']
              and value['schema'] == 'raw-file-bytes-evidence-v1', 'Exact producer raw account-file byte wrapper')
        restored = decode(value['native'])
        check(restored is None or type(restored) is bytes, 'Actual raw file bytes or explicit file absence')
        projection = value['JSON_safe_raw_bytes']
        check(type(projection) is dict and list(projection) == ['file_exists', 'raw_hex', 'byte_count', 'sha256']
              and type(projection['file_exists']) is bool, 'Complete raw projection has source order and exact bool')
        expected = {'file_exists': restored is not None, 'raw_hex': restored.hex() if restored is not None else None,
                    'byte_count': len(restored) if restored is not None else None,
                    'sha256': sha(restored) if restored is not None else None}
        if restored is None:
            check(all(projection[name] is None for name in ('raw_hex', 'byte_count', 'sha256')),
                  'Absent account file keeps exact None raw metadata')
        else:
            check(type(projection['raw_hex']) is str and integer(projection['byte_count'])
                  and is_sha(projection['sha256']), 'Existing raw file uses exact string/int/string metadata types')
        check(encoded_json(projection) == encoded_json(expected),
              'Exact ordered raw projection values reject bool/int/float coercion')
    else:
        raise ValueError('Unsupported source snapshot role: ' + str(role))
    REPORT['snapshots_verified'] += 1
    return restored


def source_counter(value, maintained_map):
    check(type(value) is dict, 'Actual source delta is a complete dictionary')
    for key, count in value.items():
        check(type(key) is str and key.startswith('rouge/') and ':' in key
              and key.partition(':')[0] in maintained_map and key.partition(':')[2]
              and integer(count), 'Actual source delta has true maintained function keys and exact nonnegative int counts')
    return value


def ui_capture(value, maintained_map, action_fields=False):
    required = {'damage_result', 'visible_status', 'UI', 'three_texts'}
    extra = {'actual_entries', 'API_sequences'} if action_fields else set()
    check(type(value) is dict and required <= set(value) and type(value['visible_status']) is str,
          'Complete source-defined UI capture base fields and exact status string')
    result = snapshot_value(value['damage_result'])
    check(result is None or (type(result) is dict and list(result) == ['scenario', 'result']
                            and type(result['scenario']) is dict and type(result['result']) is dict),
          'Ordinary UI damage_result is None or complete original scenario/result wrapper')
    ui = value['UI']
    check(type(ui) is dict and list(ui) == ['owner', 'skill', 'level', 'level_override', 'use_run_training',
                                         'raw_damage', 'technical', 'training_status', 'current_operator_state'],
          'All nine source-defined UI controls/state fields retained in order')
    check(ui['owner'] is None or type(ui['owner']) is str, 'Owner currentData is source string or actual empty None')
    check(ui['skill'] is None or type(ui['skill']) is int, 'Skill addItem userData is source integer or empty None')
    check(type(ui['level']) is int and all(type(ui[name]) is bool for name in
          ('level_override', 'use_run_training', 'raw_damage', 'technical'))
          and type(ui['training_status']) is str, 'Exact Qt source control/status scalar types')
    check(type(snapshot_value(ui['current_operator_state'])) is dict, 'Complete ordinary current operator state')
    texts = value['three_texts']
    if result is None:
        check(set(value) == required | extra and type(texts) is dict
              and list(texts) == ['applicable', 'reason', 'visible_status'] and texts['applicable'] is False
              and texts['reason'] == 'Existing error or natural early return'
              and type(texts['visible_status']) is str and texts['visible_status'] == value['visible_status'],
              'Actual None/error capture retains complete source reason/status and no fabricated formatter delta')
    else:
        check(set(value) == required | extra | {'actual_explicit_formatter_entries'}
              and type(texts) is dict and list(texts) == ['applicable', 'strings'] and texts['applicable'] is True,
              'Actual numerical capture retains its full three texts and formatter-entry delta')
        strings = texts['strings']
        check(type(strings) is dict and list(strings) == ['estimate', 'default', 'technical']
              and all(type(text) is str for text in strings.values()) and strings['estimate'] == strings['default'],
              'Exact complete numerical formatter strings with producer order')
        entries = source_counter(value['actual_explicit_formatter_entries'], maintained_map)
        check(entries.get('rouge/estimate.py:format_estimate') == 1
              and entries.get('rouge/reporting.py:format_report') == (3 if 'report' in result['result'] else 2),
              'Actual explicit three formatter calls and source format_estimate report delegation')
    if action_fields:
        source_counter(value['actual_entries'], maintained_map)
        ids = value['API_sequences']
        check(type(ids) is list and all(integer(sequence, 1) for sequence in ids) and ids == sorted(set(ids)),
              'Complete actual action API entry-ID slice')
    return result


def source_state_record(wrapper, case, stage, maintained_map):
    check(type(wrapper) is dict and list(wrapper) == ['id', 'record'] and type(wrapper['id']) is str,
          'Exact native state wrapper')
    row = wrapper['record']; step = case['step']
    base = {'id', 'planned', 'baseline_source', 'baseline_pointer', 'passed'}
    check(type(row) is dict and base <= set(row) and row['id'] == case['id']
          and type(row['passed']) is bool and snapshot_value(row['planned']) == step
          and row['planned']['native'] == graph(step), 'Complete source-plan state base fields and native exact step')
    check(row['baseline_source'] == case.get('baseline_file') and row['baseline_pointer'] == case.get('baseline_pointer')
          and (row['baseline_source'] is None or type(row['baseline_source']) is str)
          and (row['baseline_pointer'] is None or type(row['baseline_pointer']) is str),
          'Actual state retains exact baseline source/pointer metadata')
    callback = {'before_callback_damage_result'} if step['action'] == 'numeric_callback' else set()
    if callback:
        previous = snapshot_value(row['before_callback_damage_result'])
        check(previous is None or (type(previous) is dict and list(previous) == ['scenario', 'result']
              and type(previous['scenario']) is dict and type(previous['result']) is dict),
              'Source callback retains complete ordinary before-callback UI graph')
    if step['action'] == 'fresh_window':
        check(stage == 'final' and set(row) == base | {'automatic', 'durable_after',
              'all_actual_entries_including_probes', 'all_API_sequences'} and row['passed'] is True,
              'Exact complete source fresh-window final state fields')
        ui_capture(row['automatic'], maintained_map)
        durable(row['durable_after'])
    else:
        required = base | callback | {'durable_before'}
        durable(row['durable_before'])
        if stage in ('automatic', 'final'):
            required |= {'automatic', 'durable_after_automatic'}
            ui_capture(row['automatic'], maintained_map, True)
            durable(row['durable_after_automatic'])
        if stage == 'final':
            required |= {'manual', 'full_native_JSON_three_texts_auto_manual_equal',
                         'all_actual_entries_including_probes', 'all_API_sequences'}
            ui_capture(row['manual'], maintained_map, True)
            check(row['passed'] is True and row['full_native_JSON_three_texts_auto_manual_equal'] is True,
                  'Source final action retains actual full manual equality witness')
        else:
            check(row['passed'] is False and stage in ('before', 'automatic'), 'Actual intermediate state source stage')
        check(set(row) == required, 'Exact complete source-defined intermediate/final action fields')
    if stage == 'final':
        source_counter(row['all_actual_entries_including_probes'], maintained_map)
        ids = row['all_API_sequences']
        check(type(ids) is list and all(integer(sequence, 1) for sequence in ids) and ids == sorted(set(ids)),
              'Complete all-action API source entry-ID slice')
    return row


def scan_snapshots(value, native_only_paths=(), raw_byte_paths=()):
    exception_roles = set(native_only_paths); raw_roles = set(raw_byte_paths)
    check(not exception_roles & raw_roles, 'Snapshot source roles are disjoint')
    seen_exception = set(); seen_raw = set(); queue = [((), value)]
    while queue:
        path, item = queue.pop()
        if type(item) is dict:
            marker = (type(item.get('native')) is dict and item['native'].get('schema') == 'flat-typed-graph-v1')
            if (marker or 'native_inverse_verified' in item or 'JSON_projection_applicable' in item
                    or item.get('schema') == 'raw-file-bytes-evidence-v1'):
                if path in exception_roles:
                    snapshot_value(item, 'exception-args'); seen_exception.add(path)
                elif path in raw_roles:
                    snapshot_value(item, 'account-file-bytes'); seen_raw.add(path)
                else:
                    snapshot_value(item)
                # The full native inverse/projection covers the entire stored value.
                # Re-entering projection dictionaries would misclassify actual data keys as capture wrappers.
            else:
                queue.extend((path + (key,), child) for key, child in item.items())
        elif type(item) in (list, tuple):
            queue.extend((path + (index,), child) for index, child in enumerate(item))
    check(seen_exception == exception_roles and seen_raw == raw_roles,
          'Every source-qualified exception/raw role is physically present and completely verified')


def filesystem_rows(rows):
    check(type(rows) is list, 'Saved filesystem rows')
    seen = set(); files = {}
    for row in rows:
        check(type(row) is dict and type(row['path']) is str, 'Complete source filesystem row')
        name = row['path']
        check(name and not Path(name).is_absolute() and '..' not in Path(name).parts
              and not PureWindowsPath(name).anchor and '\\' not in name
              and Path(name).as_posix() == name and name not in seen, 'Unique safe saved relative file path')
        seen.add(name)
        check(type(row['kind']) is str and row['kind'] in ('directory', 'file'), 'Saved filesystem entry kind')
        if row['kind'] == 'directory':
            check(list(row) == ['path', 'kind'], 'Exact source directory row fields')
            continue
        base = ['path', 'kind', 'bytes', 'sha256', 'raw_hex']
        check(list(row) in (base + ['decoded'], base + ['decode_error'])
              and type(row['raw_hex']) is str and integer(row['bytes']) and is_sha(row['sha256']),
              'Exact source file row fields/types and one parse branch')
        raw = bytes.fromhex(row['raw_hex'])
        check(raw.hex() == row['raw_hex'] and row['bytes'] == len(raw) and row['sha256'] == sha(raw),
              'Exact saved raw file bytes')
        try:
            decoded = json.loads(raw.decode('utf-8'))
        except (UnicodeDecodeError, ValueError) as error:
            captured = row['decode_error']
            check(type(captured) is dict and list(captured) == ['type', 'message']
                  and type(captured['type']) is str and type(captured['message']) is str
                  and encoded_json(captured) == encoded_json({'type': type(error).__name__, 'message': str(error)}),
                  'Actual original raw-file decode error, never unavailable substitution')
        else:
            actual = snapshot_value(row['decoded'])
            check(graph(actual) == graph(decoded), 'Saved raw bytes exact complete ordinary decoded graph')
        files[name] = raw
        REPORT['raw_files_verified'] += 1
    return files


def durable(value, historical=False):
    keys = (['run', 'account_records', 'account_issues', 'preserve_original', 'account_bytes', 'files',
             'operator_observations_alias_is_records'] if historical else
            ['run', 'account', 'issues', 'preserve_original', 'alias_is_records', 'account_bytes', 'files'])
    check(type(value) is dict and list(value) == keys, 'All seven exact source-defined durable fields/order')
    alias = 'operator_observations_alias_is_records' if historical else 'alias_is_records'
    account = 'account_records' if historical else 'account'; issues = 'account_issues' if historical else 'issues'
    check(value[alias] is True and type(value['preserve_original']) is bool,
          'Source-qualified account-cache alias and exact preserve flag')
    for name in ('run', account, issues):
        check(type(snapshot_value(value[name])) is dict, 'Complete ordinary persisted run/account/issues dictionaries')
    raw = snapshot_value(value['account_bytes'], 'account-file-bytes')
    files = filesystem_rows(value['files'])
    if raw is None:
        check('account.json' not in files and not any(row['path'] == 'account.json' for row in value['files']),
              'Explicit absent account-file bytes agrees with same source filesystem')
    else:
        check('account.json' in files and files['account.json'] == raw,
              'Source account bytes equal same filesystem account.json raw bytes; no memory/disk equality assumed')


def manifest_payloads(reference):
    document = json.loads(read_ref(reference))
    check(type(document['artifacts']) is dict and document['artifacts'], 'Actual source manifest artifacts')
    parent = Path(reference['path']).parent
    result = {}
    for name, row in document['artifacts'].items():
        check(type(name) is str and name and not Path(name).is_absolute() and '..' not in Path(name).parts
              and Path(name).as_posix() == name, 'Canonical safe manifest member')
        full = {'path': str(parent / name), 'bytes': row['bytes'], 'sha256': row['sha256']}
        result[name] = read_ref(full)
    return document, result


def recover_original_final095(spec, runner_data, final_files):
    # Retry source first recovers exact reviewed cache source, then original FINAL.
    # The original two-binding and 79-operation checks below remain authoritative.
    retry = spec['ui_retry']
    check(type(retry) is dict and retry['runner'] == spec['final_UI']['runner']
          and retry['manifest'] == spec['final_UI']['manifest']
          and retry['source_review'] == spec['final_UI']['formal_source_review'],
          'Actual UI retry bundle must equal exact runner/manifest/formal inputs')
    contract_ref = retry['source_contract']
    contract_bytes = read_ref(contract_ref)
    contract_name = Path(contract_ref['path']).name
    check(contract_name == 'source-contract-identity-retry095.json'
          and final_files[contract_name] == contract_bytes, 'Actual retry contract belongs to sealed manifest')
    contract = json.loads(contract_bytes)
    check(contract['source_gate_passed'] is True and contract['runtime_pass'] is False
          and contract['execution_ready'] is False
          and contract['runner'] == retry['runner']
          and contract['source_guard'] == spec['actual_source_guard'],
          'Retry Source contract binds exact runner/guard without claiming runtime')
    check(read_ref(contract['binding']) == final_files['root-bound-input095.json']
          and graph(literal(runner_data.decode('utf-8'), 'BINDING095'))
          == graph(json.loads(final_files['root-bound-input095.json'])),
          'Retry actual runner literal equals complete sealed original binding')
    ui = retry['ui']
    plan = contract['output_plan']
    check(ui['runner'] == retry['runner'] and ui['receipt_path'] == plan['receipt']
          and ui['console_log_path'] == plan['console_log']
          and ui['required_saved_outputs'] == contract['required_saved_outputs']
          and ui['optional_output_paths'] == contract['optional_output_paths']
          and ui['fresh_evidence_directories'] == contract['fresh_evidence_directories']
          and ui['execution_contract']['argv'] == contract['exact_argv']
          and ui['execution_contract']['cwd'] == contract['cwd'],
          'Retry projected UI contract binds exact runner, entry and complete output roles')
    check(canonical(plan['receipt']) == canonical(spec['actual_UI_receipt']['path'])
          and canonical(plan['native_directory']) == str(NATIVE_DIRECTORY)
          and canonical(plan['native_index']) == str(NATIVE_INDEX)
          and canonical(plan['legacy_state_archive']) == canonical(spec['actual_legacy_state_archive']['path'])
          and type(plan['pngs']) is list and len(plan['pngs']) == len(PNG_NAMES)
          and {canonical(name) for name in plan['pngs']} == {str(COMPAT / name) for name in PNG_NAMES}
          and {canonical(row['path']) for row in spec['actual_PNGs']} == {canonical(name) for name in plan['pngs']}
          and canonical(plan['console_log']) == canonical(spec['actual_UI_primary']['console_log']['path'])
          and canonical(plan['exit_code_file']) == canonical(spec['actual_UI_primary']['exit_code_file']['path']),
          'Actual retry outputs equal exact Source contract and literal native/PNG namespace')
    check(contract['exact_argv'] == spec['actual_UI_primary']['argv'] and contract['cwd'] == str(REPO),
          'Retry contract binds exact trusted root launch argv/cwd')
    source_constants = {node.value for node in ast.walk(ast.parse(runner_data))
                        if isinstance(node, ast.Constant) and type(node.value) is str}
    check(all(Path(name).name in source_constants for name in
              [plan['receipt'], plan['legacy_state_archive'], plan['native_directory'], *plan['pngs']]),
          'Retry receipt/legacy/native/four PNG names are real source literals')
    inverse_contract = contract['inverse_recovery']
    check(inverse_contract['schema'] == 'full-ui095-identity-retry-exact-inverse-v1', 'Exact retry inverse schema')
    ledger_ref = inverse_contract['ledger']
    ledger_bytes = read_ref(ledger_ref)
    ledger_name = Path(ledger_ref['path']).name
    check(ledger_name == 'exact-inverse-identity-retry095.json' and final_files[ledger_name] == ledger_bytes,
          'Actual retry inverse belongs to exact sealed source manifest')
    inverse = json.loads(ledger_bytes)
    stages = inverse['reverse_stages']
    check(inverse['schema'] == inverse_contract['schema'] and type(stages) is list and len(stages) == 3,
          'Exactly three Source-qualified identity/cache/original retry inverse stages')
    prior = contract['prior_cache_retry_runner']
    cache = contract['cache_candidate']; original = contract['original_final']
    check(stages[0]['from'] == retry['runner'] and stages[0]['to'] == prior
          and stages[1]['from'] == prior and stages[1]['to'] == cache
          and stages[2]['from'] == cache and stages[2]['to'] == original
          and prior['sha256'] == 'e5dec2d704cecbde56762cf7c2f92016f5123b592633fae12840a892869e6bc5'
          and prior['bytes'] == 1184954
          and [len(stage['operations']) for stage in stages] == [31, 27, 3]
          and cache['sha256'] == '1a6ac7f0db3096de170a9e0d035148bfbad372cc58f704bb7ad39da6cb7cfb6d'
          and cache['bytes'] == 1184561
          and original['sha256'] == '83c412ce7e456109dc32a6415f7a61526955d48b01d25dbb72198870e6cf18ee'
          and original['bytes'] == 1184276,
          'Exact identity to old e5 to cache to archived original FINAL83c4 chain')
    recovered = runner_data
    for stage in stages:
        check(recovered == read_ref(stage['from']), 'Inverse stage starts from exact physical source bytes')
        operations = stage['operations']
        check(type(operations) is list and operations, 'Nonempty exact stage reverse operations')
        # Operations describe sequential forward replacements; each offset is
        # verified against its actual intermediate source during exact reversal.
        for operation in reversed(operations):
            check(type(operation) is dict, 'Explicit retry inverse operation dictionary')
            start = operation['pending_byte_start']; count = operation['pending_byte_count']
            end = start + count if integer(start) and integer(count) else -1
            check(integer(start) and integer(count) and end <= len(recovered)
                  and is_sha(operation['pending_sha256'])
                  and sha(recovered[start:end]) == operation['pending_sha256'],
                  'Sequential retry inverse operation exact current raw bytes')
            recovered = recovered[:start] + base64.b64decode(operation['before_base64'], validate=True) + recovered[end:]
        check(recovered == read_ref(stage['to']), 'Each inverse stage restores every archived source byte')
    check(recovered == read_ref(original), 'Entire original FINAL source recovered exactly before old two-binding inverse')
    REPORT['UI_retry_source_contract'] = contract_ref
    REPORT['UI_retry_source_inverse'] = ledger_ref
    REPORT['UI_retry_two_stage_inverse_exact'] = True
    REPORT['UI_identity_retry_three_stage_inverse_exact'] = True
    return recovered.decode('utf-8')


def source_and_binding(spec):
    pending_mf, pending_files = manifest_payloads(spec['pending_UI']['manifest'])
    check(spec['pending_UI']['manifest']['sha256'] == EXPECTED_UI_PENDING_MF_SHA and pending_mf['STOPWRITE'] is True,
          'Exact frozen v3 pending source manifest')
    final_mf, final_files = manifest_payloads(spec['final_UI']['manifest'])
    check(final_mf['root_source_guard_sha256'] == EXPECTED_GUARD_SHA and final_mf['runtime_calls'] == 0,
          'Actual FINAL source seal is not a runtime proof')
    runner_data = read_ref(spec['final_UI']['runner'])
    runner_name = Path(spec['final_UI']['runner']['path']).name
    check(runner_name in final_files and final_files[runner_name] == runner_data, 'Actual FINAL runner belongs to exact manifest')
    final_source = runner_data.decode('utf-8')
    check(literal(final_source, 'PENDING095') is False, 'Actual FINAL UI source is still PENDING')
    formal = json.loads(read_ref(spec['final_UI']['formal_source_review']))
    p = spec['final_UI']['formal_pointers']
    check(set(p) == {'source_gate', 'runtime', 'runner_sha256', 'manifest_sha256', 'guard_sha256'}, 'Five explicit actual formal pointers')
    check(pointer(formal, p['source_gate']) is True and pointer(formal, p['runtime']) is False
          and pointer(formal, p['runner_sha256']) == spec['final_UI']['runner']['sha256']
          and pointer(formal, p['manifest_sha256']) == spec['final_UI']['manifest']['sha256']
          and pointer(formal, p['guard_sha256']) == EXPECTED_GUARD_SHA, 'Actual FINAL five-value formal source gate before codec use')
    inverse_source = recover_original_final095(spec, runner_data, final_files)
    binding = literal(final_source, 'BINDING095')
    check(graph(binding) == graph(literal(inverse_source, 'BINDING095')), 'Actual retry binding equals exact recovered original FINAL binding')
    check(binding['status'] == 'ROOT_BOUND_ACTUAL095_AND_ACTUAL94_BASELINE', 'Actual bound UI source status')
    bound_input = json.loads(final_files['root-bound-input095.json'])
    check(graph(bound_input) == graph(binding), 'Actual FINAL runner literal differs from sealed root-bound input')
    pending = pending_files['wine-full-ui-095-pending.py']
    pending_binding = json.loads(pending_files['pending-binding095.json'])
    tree = ast.parse(inverse_source)
    assignment = next(n for n in tree.body if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'BINDING095' for t in n.targets))
    actual_assignment = ast.get_source_segment(inverse_source, assignment) + '\n'
    old_assignment = 'BINDING095 = ' + repr(pending_binding) + '\n'
    check(inverse_source.count(actual_assignment) == 1 and inverse_source.count('PENDING095 = False') == 1, 'Unique two FINAL bindings')
    reversed_final = inverse_source.replace(actual_assignment, old_assignment, 1).replace('PENDING095 = False', 'PENDING095 = True', 1).encode()
    check(reversed_final == pending, 'Actual FINAL inverse must restore every pending byte exactly')
    inverse = json.loads(pending_files['exact-inverse-ledger095.json'])
    recovered = pending
    for row in reversed(inverse['operations']):
        start = row['pending_byte_start']; end = start + row['pending_byte_count']
        check(integer(start) and integer(row['pending_byte_count']) and sha(recovered[start:end]) == row['pending_sha256'],
              'Actual pending inverse operation raw bytes')
        recovered = recovered[:start] + base64.b64decode(row['before_base64'], validate=True) + recovered[end:]
    check(len(recovered) == 729181 and sha(recovered) == EXPECTED_ORIGINAL_UI_SHA, 'Entire original UI 729181-byte inverse')
    classification = json.loads(pending_files['original-assertion-and-delta-classification095.json'])
    check(sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(recovered))) == classification['original_assert_count'],
          'Original assertion ledger is tied to exact recovered source')
    legacy = classification['original_legacy_check_count_contract']
    check(legacy['prefix085'] + legacy['additional090'] == legacy['total090'], 'Original source-qualified legacy counts')
    normalized = normalized_binding(binding)
    for key in ('source_guard', 'candidate_manifest', 'implementation_freeze', 'technical_tail_correction_artifact',
                'actual94_receipt', 'actual94_guard', 'baseline_receipt', 'baseline_saved_verifier'):
        registered(normalized[key])
    check(normalized['source_guard']['sha256'] == EXPECTED_GUARD_SHA, 'Actual root095-v2 guard binding')
    guard = json.loads(registered(normalized['source_guard']))
    check(guard['passed'] is True and guard['candidate_bytes_exact'] is True, 'Actual root source guard')
    expected = source_map(guard['source_sha256_after'])
    check(guard['current_maintained'] == len(expected) and maintained() == expected, 'Dynamic whole maintained scope, including additions/deletions')
    for name, expected_sha in expected.items():
        path = REPO / name
        read_ref({'path': str(path), 'bytes': path.stat().st_size, 'sha256': expected_sha})
    code_mf = json.loads(registered(normalized['candidate_manifest']))
    check(normalized['candidate_manifest']['sha256'] == EXPECTED_CODE_MF_SHA, 'Exact frozen five-product source manifest')
    for row in code_mf['files']:
        check(expected[row['destination_repo_path']] == row['sha256'], 'Product source target inside whole maintained guard')
        read_ref({'path': str(REPO / row['destination_repo_path']), 'bytes': row['bytes'], 'sha256': row['sha256']})
    for artifact in normalized['additional_formal_artifacts']:
        registered(artifact)
        review = json.loads(registered(artifact['formal_review']))
        check(pointer(review, artifact['formal_review_pass_pointer']) is True, 'Actual additional adaptation source review')
        for row in artifact['source_targets']:
            check(expected[row['destination_repo_path']] == row['sha256'], 'Additional adapted source exact current guard')
    report_contract = normalized['report_contract']
    correction = json.loads(registered(normalized['technical_tail_correction_artifact']))
    check(report_contract['reference_key'] == 'selected_module_source_reference'
          and report_contract['section_id'] == 'selected_module_source'
          and report_contract['technical_tail_prefix'] == correction['actual_complete_append_tail_prefix'] == '\n\n【所选模组原件追溯】\n',
          'Source-qualified report object/last notes-only section/double-LF technical tail')
    plan = json.loads(pending_files['full095-subgroup-plan.json'])
    check([c['id'] for c in normalized['cases']] == [c['id'] for c in plan['steps']]
          and all(graph(c['step']) == graph(p['step']) and c['comparison'] == p['comparison']
                  for c, p in zip(normalized['cases'], plan['steps'])), 'Exact source-qualified full095 subgroup plan')
    REPORT['actual_final_runner'] = metadata(Path(spec['final_UI']['runner']['path']))
    REPORT['actual_final_manifest'] = metadata(Path(spec['final_UI']['manifest']['path']))
    REPORT['actual_source_guard'] = metadata(Path(normalized['source_guard']['path']))
    REPORT['original_pending_and_final_inverse_exact'] = True
    REPORT['original_assertions_source_qualified'] = classification['original_assert_count']
    return normalized, expected, plan, legacy, final_source


def primary_launch(spec):
    wrapper_data = read_ref(spec['wine_wrapper'])
    check(spec['wine_wrapper']['path'] == '/workspace/.compat/run-wine-python.sh'
          and sha(wrapper_data) == '65dd3806511e037290291ac592246abe80f346b1004b88c81e798612db4d79c8', 'Exact reviewed Wine launch wrapper')
    row = spec['actual_UI_primary']
    pre = json.loads(read_ref(row['prelaunch']))
    obs = json.loads(read_ref(row['root_observation']))
    pp = row['prelaunch_pointers']; op = row['observation_pointers']
    argv = row['argv']
    check(type(argv) is list and len(argv) >= 2 and all(type(x) is str for x in argv)
          and argv[0] == spec['wine_wrapper']['path']
          and linux_path(argv[1]) == canonical(spec['final_UI']['runner']['path']),
          'Actual wrapper argv[0]/executed runner argv[1], not any incidental later argument')
    check(pointer(pre, pp['source_gate']) is True and pointer(pre, pp['outputs_absent']) is True
          and pointer(pre, pp['argv']) == argv and pointer(pre, pp['cwd']) == str(REPO)
          and pointer(pre, pp['runner_sha256']) == spec['final_UI']['runner']['sha256']
          and pointer(pre, pp['guard_sha256']) == EXPECTED_GUARD_SHA, 'Actual root prelaunch admitted these exact sources, entry and fresh outputs')
    check(pointer(obs, op['observed']) is True and pointer(obs, op['captured']) is True
          and pointer(obs, op['argv']) == argv and pointer(obs, op['cwd']) == str(REPO)
          and type(pointer(obs, op['exit_code'])) is int and pointer(obs, op['exit_code']) == 0,
          'Actual trusted root process/tool observation, exact entry and primary integer0')
    physical = read_ref(row['exit_code_file'])
    check(physical in (b'0\n', b'0\r\n') and int(physical.strip()) == pointer(obs, op['exit_code']), 'Actual UI physical primary status equals root observation')
    check(pointer(obs, op['exit_code_file']) == row['exit_code_file'], 'Observed primary status file full_ref')
    check(pointer(obs, op['console_log']) == row['console_log']
          and pointer(obs, op['UI_receipt']) == spec['actual_UI_receipt'],
          'Trusted observed launch binds exact fresh console and actual UI receipt full_refs')
    read_ref(row['console_log'])
    REPORT['actual_primary_exit'] = metadata(Path(row['exit_code_file']['path']))
    REPORT['actual_prelaunch'] = metadata(Path(row['prelaunch']['path']))
    REPORT['actual_root_UI_observation'] = metadata(Path(row['root_observation']['path']))
    REPORT['actual_UI_primary_exit0_verified'] = True


def png(reference):
    raw = read_ref(reference)
    check(raw[:8] == b'\x89PNG\r\n\x1a\n', 'Actual PNG signature')
    at = 8; first = True; ended = False
    while at < len(raw):
        check(at + 12 <= len(raw), 'Complete PNG chunk framing')
        count = struct.unpack('>I', raw[at:at + 4])[0]
        kind = raw[at + 4:at + 8]; end = at + 12 + count
        check(end <= len(raw), 'Complete PNG chunk bytes')
        payload = raw[at + 8:at + 8 + count]
        check(zlib.crc32(kind + payload) & 0xffffffff == struct.unpack('>I', raw[at + 8 + count:end])[0], 'Actual PNG CRC')
        if first:
            check(kind == b'IHDR' and count == 13 and struct.unpack('>II', payload[:8])[0] > 0
                  and struct.unpack('>II', payload[:8])[1] > 0, 'Actual PNG dimensions')
            first = False
        if kind == b'IEND':
            check(count == 0 and end == len(raw), 'Exact complete PNG ending')
            ended = True
        at = end
    check(ended, 'Actual PNG IEND present')


def ui_receipt(spec, maintained_map, legacy):
    value = json.loads(read_ref(spec['actual_UI_receipt']))
    check(value['passed'] is True and value['complete_ui_validation'] is True and 'failure' not in value,
          'Actual current fullUI receipt available scope fully passed')
    check(value['native_windows_verified'] is False and value['game_captures'] == value['chat_requests'] == 0
          and type(value['game_captures']) is int and type(value['chat_requests']) is int
          and value['private_state_isolated'] is True, 'No native/game/chat certification or private fixtures')
    g = value['source_guard095']
    check(linux_path(g['path']) == canonical(spec['actual_source_guard']['path'])
          and g['sha256'] == spec['actual_source_guard']['sha256'] == EXPECTED_GUARD_SHA
          and g['before'] == g['after'] == maintained_map and not g['source_drift'] and g['read_error'] is None,
          'Actual full maintained before/after guard, not legacy own selector')
    own_expected = {name: digest for name, digest in maintained_map.items() if name.startswith('rouge/')}
    source_map(value['source_sha256']); source_map(value['source_sha256_after'])
    check(value['source_sha256'] == value['source_sha256_after'] == own_expected and not value['source_drift'],
          'Actual original rouge-only source selector exact safe keys and true guard subset')
    failure = value['full095_evidence_failure']
    check(failure['pending_entry_sequences'] == failure['Qt_slot_exceptions'] == failure['capture_or_write_errors'] == [],
          'No missing live entry, Qt slot error or capture/write failure')
    checks = value['checks']
    check(type(checks) is list and checks and all(type(row) is dict and row.get('passed') is not False for row in checks),
          'Actual measured checks with no explicit failure; source old no_external_operations row preserved')
    check(value['preserved_full_085_checks'] == legacy['prefix085']
          and value['legacy_original4283_actual_checks'] == legacy['total090']
          and value['legacy085_prefix4217_and090_additional66_preserved'] is True
          and value['actual_total_checks095'] == value['total_actual_checks'] == len(checks),
          'Original live legacy closure and measured dynamic new total')
    check(all(integer(value[name], 1) for name in ('preserved_full_085_checks', 'legacy_original4283_actual_checks',
              'actual_total_checks095', 'total_actual_checks')), 'Actual legacy/new counts have integer types')
    scan_snapshots(value)
    REPORT['actual_runtime_receipt'] = metadata(Path(spec['actual_UI_receipt']['path']))
    REPORT['maintained_source_files'] = len(maintained_map)
    REPORT['actual_check_count'] = len(checks)
    REPORT['legacy_check_count'] = legacy['total090']
    return value


def baseline_documents(binding, spec):
    actual94 = json.loads(registered(binding['actual94_receipt']))
    guard94 = json.loads(registered(binding['actual94_guard']))
    check(actual94['section'] == 94 and actual94['passed'] is True and actual94['workflow_complete'] is True
          and actual94['actual_window_verified_by_root'] is True, 'Actual94 completed baseline prerequisite')
    receipt = json.loads(registered(binding['baseline_receipt']))
    proof = json.loads(registered(binding['baseline_saved_verifier']))
    check(receipt['passed'] is receipt['workflow_complete'] is True and receipt['source_drift'] == []
          and receipt['source_sha256_before'] == receipt['source_sha256_after'] == guard94['source_sha256_after'],
          'Actual94 runtime receipt/guard unchanged at its historical run')
    check(proof['passed'] is True and proof['validation_kind'] == 'SAVED_ONLY'
          and proof['actual_runtime_receipt_sha256'] == binding['baseline_receipt']['sha256'],
          'Actual94 independently saved proof binds its actual runtime receipt')
    for prerequisite in spec['baseline_prerequisite_refs']:
        read_ref(prerequisite)
    physical_exit = read_ref(spec['actual_baseline_primary_exit'])
    check(physical_exit in (b'0\n', b'0\r\n'), 'Actual94 baseline physical primary0')
    check(receipt['game_capture_requests'] == receipt['chat_requests'] == 0 and receipt['private_state_isolated'] is True,
          'Actual94 public isolated source-compatible runtime')
    read_ref({'path': '/workspace/.continuation/ui-095-module-report-pending/baseline094-v2/wine-module-report-baseline-094-for095.py', 'bytes': 28235, 'sha256': '4740c8b9f6386a32cd78929f98c8265201ba5b891d1e6eddbbb812faebebd829'})
    documents = {}
    for row in binding['baseline_files']:
        check(row['encoding'] in ('json', 'gzip_json') and row['name'] not in documents, 'Actual unique baseline document encoding')
        compressed = registered(row)
        raw = gzip.decompress(compressed) if row['encoding'] == 'gzip_json' else compressed
        if row['name'] == 'actual94_baseline_records':
            meta = receipt['records']
            check(linux_path(str(COMPAT / meta['file'])) == row['path'] and len(compressed) == meta['bytes']
                  and sha(compressed) == meta['sha256'] and len(raw) == meta['decoded_bytes']
                  and sha(raw) == meta['decoded_sha256'], 'Complete actual94 compressed and decoded records binding')
        document = json.loads(raw)
        raw_paths = []
        if row['name'] == 'actual94_baseline_records':
            check(type(document) is dict and document['schema'] == 'focused-module-report-baseline-v1'
                  and type(document['states']) is list, 'Actual historical baseline producer state envelope')
            for index, state in enumerate(document['states']):
                check(type(state) is dict, 'Actual historical baseline state')
                for field in ('durable_before', 'durable_after_automatic', 'durable_after'):
                    if field in state and state[field] is not None:
                        durable(state[field], historical=True)
                        raw_paths.append(('states', index, field, 'account_bytes'))
        scan_snapshots(document, raw_byte_paths=raw_paths)
        documents[row['name']] = document
    data = documents['actual94_baseline_records']
    check(data['schema'] == 'focused-module-report-baseline-v1' and data['passed'] is True and data['Qt_slot_exceptions'] == [],
          'Actual94 baseline complete native archive')
    states = data['states']
    check(len(states) == receipt['states'] == proof['actual']['states'] == 41
          and len({row['id'] for row in states}) == len(states), 'Actual independently verified41 baseline states')
    plan = json.loads(read_ref(spec['actual_baseline_plan']))
    check([row['id'] for row in states] == [row['id'] for row in plan['steps']], 'Actual41 baseline ordered plan')
    calls = data['targeted_calls']
    check([row['sequence'] for row in calls] == list(range(1, len(calls) + 1)), 'Actual94 complete targeted ledger')
    for row in calls:
        if row['key'] in ('calculate_damage', '_prepare_damage'):
            check(row['caller_unchanged'] is True and row['caller_before']['native'] == row['caller_after']['native'],
                  'Actual94 original caller captured unchanged')
            returned = decode(row['returned']['native'])
            if row['key'] == '_prepare_damage':
                check(type(returned) is tuple and type(returned[0]) is dict
                      and graph(returned[0]) == row['local_prepared_scenario_at_exit']['native'], 'Actual94 complete prepared tuple')
    provenance = {}
    for row in binding['qualified_reference_provenance']:
        check(row['name'] not in provenance, 'Unique actual source-qualified delta provenance')
        provenance[row['name']] = json.loads(registered(row))
    check(provenance, 'Actual independent report additions and text spans source provenance required')
    for case in binding['cases']:
        if case['comparison'] != 'paired_actual094':
            continue
        baseline = pointer(documents[case['baseline_file']], case['baseline_pointer'])
        check(baseline['id'] == case['id'] and baseline['passed'] is True
              and baseline['planned']['native'] == graph(case['step']), 'Exact actual94 bridge state')
        delta = case['delta']
        check(type(delta['has_addition']) is bool, 'Real source-qualified addition/None flag')
        if delta['has_addition']:
            source = pointer(provenance[delta['provenance_file']], delta['provenance_pointer'])
            check(source['actual95_source_guard_sha256'] == EXPECTED_GUARD_SHA
                  and source['actual94_full_native_and_existing_report_exact'] is True
                  and source['independent_raw_source_qualified'] is True
                  and source['expected_reference_native'] == delta['expected_reference_native']
                  and source['expected_section_native'] == delta['expected_section_native']
                  and graph(source['text_insertions']) == graph(delta['text_insertions']), 'Exact independently source-qualified case delta')
    REPORT['actual_baseline_runtime_receipt'] = metadata(Path(binding['baseline_receipt']['path']))
    REPORT['actual_baseline_saved_proof'] = metadata(Path(binding['baseline_saved_verifier']['path']))
    REPORT['actual_baseline_states_verified'] = len(states)
    return documents


def graph_sha(encoded):
    return sha(json.dumps(encoded, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode())


def entry_summary(row, source_lines, maintained_map):
    base = {'sequence', 'entry', 'scope', 'phase', 'case', 'origin', 'outcome'}
    check(type(row) is dict and base <= set(row) and integer(row['sequence'], 1)
          and all(type(row[name]) is str and row[name] for name in ('entry', 'scope', 'phase', 'outcome'))
          and (row['case'] is None or type(row['case']) is str and row['case']), 'Complete actual entry metadata types')
    key = row['entry']; source_path, _, function = key.partition(':')
    check(source_path.startswith('rouge/') and source_path in maintained_map and function,
          'Actual entry source key is a true whole maintained-map member')
    check(key in ('rouge/damage.py:calculate_damage', 'rouge/damage.py:_prepare_damage')
          or key.startswith(('rouge/app.py:MainWindow.calculate', 'rouge/run_state.py:RunState.',
                             'rouge/account_cache.py:AccountCache.')), 'Exact frozen targeted source selector')
    origin = row['origin']
    if origin is not None:
        check(type(origin) is dict and list(origin) == ['runner_line', 'function', 'source']
              and integer(origin['runner_line'], 1) and origin['runner_line'] <= len(source_lines)
              and type(origin['function']) is str and origin['function'] and type(origin['source']) is str
              and origin['source'] == source_lines[origin['runner_line'] - 1], 'Complete source-qualified live origin')
    events = row.get('exception_events', [])
    check(type(events) is list and ('exception_events' not in row or events), 'Actual absent-or-nonempty exception-events list')
    allowed = []
    for index, event in enumerate(events):
        check(type(event) is dict and list(event) == ['type', 'message', 'args']
              and type(event['type']) is str and event['type'] and type(event['message']) is str,
              'Exact source-qualified _trace_local095 exception event shape')
        allowed.append(('exception_events', index, 'args'))
    scan_snapshots(row, allowed)
    emitted = base | ({'exception_events'} if events else set())
    summary = {name: row[name] for name in ('sequence', 'entry', 'scope', 'phase', 'case', 'outcome')}
    rules = {'rouge/damage.py:calculate_damage': ['scenario'], 'rouge/damage.py:_prepare_damage': ['scenario'],
             'rouge/run_state.py:RunState.apply': ['observed', 'captured_at'],
             'rouge/account_cache.py:AccountCache.observe': ['operator', 'captured_at'],
             'rouge/account_cache.py:AccountCache.view': ['op']}
    caller_fields = {'caller_before', 'caller_after', 'caller_unchanged'}
    if key in rules:
        check(caller_fields <= set(row) and type(row['caller_unchanged']) is bool,
              'All five real _inputs095 selectors require complete caller before/after/unchanged')
        before = snapshot_value(row['caller_before']); after = snapshot_value(row['caller_after'])
        check(type(before) is dict and type(after) is dict and list(before) == rules[key] and list(after) == rules[key]
              and row['caller_unchanged'] is (row['caller_before']['native'] == row['caller_after']['native']),
              'Actual caller key order/value equality and exact bool; no invented immutability for cache/run calls')
        emitted |= caller_fields
        summary['caller_native_sha256'] = graph_sha(row['caller_before']['native'])
    else:
        check(not caller_fields & set(row), 'Real _inputs095 None branch emits no invented caller fields')
    if key in ('rouge/damage.py:calculate_damage', 'rouge/damage.py:_prepare_damage'):
        check(row['caller_unchanged'] is True and type(before['scenario']) is dict, 'Actual original numerical caller preserved')
        returned = snapshot_value(row['returned']); emitted.add('returned')
        expected_outcome = 'raised_exception' if returned is None and events else 'returned_' + type(returned).__name__
        check(row['outcome'] == expected_outcome, 'Explicit source numerical API dict/None/exception return outcome')
        if key.endswith(':_prepare_damage') and returned is not None:
            check(type(returned) is tuple and len(returned) == 4 and type(returned[0]) is dict,
                  'Complete source-qualified four-part prepared tuple')
        if key.endswith(':calculate_damage') and returned is not None:
            check(type(returned) is dict, 'Actual numerical API full returned dictionary')
        summary['returned_native_sha256'] = graph_sha(row['returned']['native'])
        summary['scenario_native_sha256'] = graph_sha(graph(before['scenario']))
    elif key == 'rouge/app.py:MainWindow.calculate':
        result = snapshot_value(row['returned_damage_result']); emitted |= {'returned_damage_result', 'visible_status'}
        check(result is None or (type(result) is dict and list(result) == ['scenario', 'result']
                                and type(result['scenario']) is dict and type(result['result']) is dict),
              'Actual MainWindow return is None or complete ordinary numerical wrapper')
        check(type(row['visible_status']) is str
              and row['outcome'] == ('numerical_result_available' if result is not None else 'no_numerical_result'),
              'Actual MainWindow source branch full visible status and numerical/None outcome')
        summary['UI_damage_result_native_sha256'] = graph_sha(row['returned_damage_result']['native'])
        summary['visible_status'] = row['visible_status']
    elif row['outcome'] == 'returned_non_evidence_object':
        check(type(row.get('returned_type')) is str and row['returned_type']
              and row['returned_type'] not in ('dict', 'list', 'tuple', 'bool', 'int', 'float', 'str', 'NoneType')
              and 'returned' not in row, 'Actual unsupported-value type-only fallback has nonempty real type and no invented snapshot')
        emitted.add('returned_type')
    else:
        returned = snapshot_value(row['returned']); emitted.add('returned')
        check(type(returned) in (dict, list, tuple, bool, int, float, str) or returned is None,
              'Actual generic targeted native-return source branch supports only literal producer types')
        expected_outcome = 'returned_none_with_exception_events' if returned is None and events else 'returned_' + type(returned).__name__
        check(row['outcome'] == expected_outcome, 'Actual generic None+events classification distinct from API raised_exception')
        summary['returned_native_sha256'] = graph_sha(row['returned']['native'])
    check(set(row) == emitted, 'Exact complete source-emitted entry fields for its caller and return branches')
    return summary


def native_archive(spec, receipt, source):
    ref = spec['actual_native_index']
    check(canonical(ref['path']) == str(NATIVE_INDEX), 'Source-qualified full .compat-relative index path')
    index_bytes = read_ref(ref); index = json.loads(index_bytes)
    meta = receipt['full_native095']
    check(meta['schema'] == index['schema'] == 'full-ui095-native-index-v1'
          and meta['directory'] == NATIVE_DIRECTORY.name
          and canonical(str(COMPAT / meta['file'])) == str(NATIVE_INDEX)
          and meta['index_bytes'] == len(index_bytes) and meta['index_sha256'] == sha(index_bytes), 'Actual current UI native index binding')
    fresh = receipt['fresh_evidence_directory095']
    check(linux_path(fresh['path']) == str(NATIVE_DIRECTORY) and fresh['relative_to_compat'] == NATIVE_DIRECTORY.name
          and fresh['existed_at_admission'] is False and fresh['created_before_project_imports'] is True,
          'Source-qualified fresh namespace admission and runtime source witness')
    check(NATIVE_DIRECTORY.is_dir() and not NATIVE_DIRECTORY.is_symlink(), 'Actual regular fresh native directory')
    physical = set()
    for path in NATIVE_DIRECTORY.rglob('*'):
        mode = path.lstat().st_mode
        check(not stat.S_ISLNK(mode) and (stat.S_ISDIR(mode) or stat.S_ISREG(mode)), 'Native namespace symlink/nonregular entry')
        if stat.S_ISREG(mode):
            physical.add(str(path.resolve()))
    files = meta['files']
    check(type(files) is list and files, 'Actual complete native physical file receipt')
    declared = {}
    for row in files:
        name = row['file']
        check(type(name) is str and Path(name).as_posix() == name and not Path(name).is_absolute()
              and '..' not in Path(name).parts and Path(name).parts[0] == NATIVE_DIRECTORY.name,
              'Complete safe .compat-relative native paths, not basenames')
        full = {'path': str(COMPAT / name), 'bytes': row['bytes'], 'sha256': row['sha256']}
        key = canonical(full['path'])
        check(key not in declared, 'Unique canonical native file')
        read_ref(full); declared[key] = full
    check(set(declared) == physical, 'Native receipt covers exact actual physical file set')
    chunks = index['chunks']
    check(type(chunks) is list and chunks and meta['chunks'] == len(chunks) and index['outcome'] == 'passed'
          and integer(meta['chunks'], 1) and integer(meta['targeted_call_records']) and integer(meta['states'])
          and index['source_guard_sha256'] == EXPECTED_GUARD_SHA and not index['source_drift']
          and index['pending_entry_sequences'] == [] and index['full095_evidence_failure'] == receipt['full095_evidence_failure'],
          'Actual native index complete and successful at current source')
    previous = '0' * 64; summaries = {}; states = []; chunk_paths = set()
    phase_counts = collections.Counter(); target_counts = collections.Counter()
    source_lines = source.splitlines()
    for number, row in enumerate(chunks, 1):
        path = canonical(str(COMPAT / row['file']))
        check(Path(path).parent == NATIVE_DIRECTORY and Path(path).name == 'wine-ui-full-native-095-%06d.json.gz' % number
              and path not in chunk_paths and path in declared, 'Ordered actual dynamic chunk path')
        chunk_paths.add(path)
        compressed = read_ref(declared[path])
        check(row['bytes'] == len(compressed) and row['sha256'] == sha(compressed), 'Exact compressed chunk metadata')
        raw = gzip.decompress(compressed)
        check(integer(row['decoded_bytes']) and len(raw) == row['decoded_bytes'] and sha(raw) == row['decoded_sha256'], 'Exact decoded chunk bytes/hash')
        previous = sha((previous + row['sha256'] + row['decoded_sha256']).encode('ascii'))
        check(row['chain_sha256'] == previous, 'Complete ordered native chunk hash chain')
        data = json.loads(raw)
        check(data['schema'] == 'full-ui095-native-chunk-v1' and data['sequence'] == number
              and integer(data['sequence'], 1)
              and data['source_guard_sha256'] == EXPECTED_GUARD_SHA, 'Actual chunk schema/order/source')
        entries = data['entries']; chunk_states = data['states']
        check(type(entries) is list and type(chunk_states) is list and row['entries'] == len(entries)
              and integer(row['entries'])
              and row['entry_sequences'] == [entry['sequence'] for entry in entries]
              and row['state_ids'] == [state['id'] for state in chunk_states], 'Exact whole chunk entry/state coverage')
        for entry in entries:
            summary = entry_summary(entry, source_lines, receipt['source_guard095']['before'])
            sequence = summary['sequence']
            check(sequence not in summaries, 'Targeted call sequence occurs exactly once')
            summaries[sequence] = summary
            target_counts[summary['entry']] += 1
            phase_counts[(summary['scope'] + '|' + summary['phase'], summary['entry'])] += 1
        # All state snapshots are validated by exact source roles in new_subgroup, including every intermediate record.
        states.extend(chunk_states)
    check(set(declared) == chunk_paths | {str(NATIVE_INDEX)}, 'Native physical files consist of exact index and all indexed chunks; no tmp/unlisted file')
    check(sorted(summaries) == list(range(1, len(summaries) + 1)) and index['records_completed'] == meta['targeted_call_records'] == len(summaries),
          'All call-entry sequences completed exactly once; completion order may differ for nested calls')
    check(index['states_committed'] == meta['states'] == len(states) and index['chain_sha256'] == meta['chain_sha256'] == previous,
          'Actual complete states and final chain')
    check(integer(index['records_completed']) and integer(index['states_committed']), 'Actual index aggregate integer types')
    totals = receipt['actual_all_rouge_main_thread_entries095']; phases = receipt['actual_phase_entries095']
    check(type(totals) is dict and type(phases) is dict and totals and all(integer(n, 1) for n in totals.values()), 'Actual all-Rouge main-thread counts')
    check(all(type(key) is str and key.partition(':')[0] in receipt['source_guard095']['before']
              and key.partition(':')[0].startswith('rouge/') and key.partition(':')[2] for key in totals),
          'All entry-ledger keys belong to actual maintained Rouge source, never foreign missing-key defaults')
    folded = collections.Counter()
    for phase, entries in phases.items():
        check(type(phase) is str and '|' in phase and type(entries) is dict and all(integer(n, 1) for n in entries.values()), 'Actual source phase ledger counts')
        folded.update(entries)
    check(dict(folded) == totals, 'All entry ledger equals phase-ledger sum, no fixed total-minus-count inference')
    targeted = {name: n for name, n in totals.items() if name in ('rouge/damage.py:calculate_damage', 'rouge/damage.py:_prepare_damage')
                or name.startswith(('rouge/app.py:MainWindow.calculate', 'rouge/run_state.py:RunState.', 'rouge/account_cache.py:AccountCache.'))}
    check(dict(target_counts) == targeted and all(phases[phase][name] == n for (phase, name), n in phase_counts.items()),
          'Every targeted entry agrees with source-qualified actual all/phase counts')
    REPORT['actual_native_index'] = metadata(Path(ref['path']))
    REPORT['actual_native_files'] = [declared[name] for name in sorted(declared)]
    REPORT['actual_native_chunks'] = len(chunks)
    REPORT['targeted_calls_verified'] = len(summaries)
    REPORT['actual_phase_ledger_verified'] = True
    return summaries, states


def strict_baseline(capture, baseline, case, report_contract):
    # Decode the entire damage_result root so scenario/result cross-root aliases survive.
    current = decode(capture['damage_result']['native']); old = decode(baseline['damage_result']['native'])
    delta = case['delta']
    if current is None or not delta['has_addition']:
        check(capture['damage_result']['native'] == baseline['damage_result']['native']
              and capture['three_texts']['applicable'] == baseline['three_texts']['applicable'], 'Whole actual94 native exact for None/no-addition case')
        if capture['three_texts']['applicable']:
            check(capture['three_texts']['strings'] == baseline['three_texts']['strings'], 'All actual94 texts unchanged')
        check(capture['visible_status'] == baseline['visible_status'], 'Actual94 visible status unchanged')
        return
    check(type(current) is dict and type(old) is dict and graph(current['scenario']) == graph(old['scenario']), 'Complete original caller matches actual94')
    check(delta['reference_path'] == ['result', 'report', report_contract['reference_key']]
          and delta['sections_path'] == ['result', 'report', 'sections']
          and delta['section_id_key'] == report_contract['section_id_key'] == 'id'
          and delta['section_id'] == report_contract['section_id'], 'Only exact qualified report addition paths')
    parent = current['result']['report']
    check(graph(parent[report_contract['reference_key']]) == delta['expected_reference_native'], 'Exact new reference object, complete contained keys')
    del parent[report_contract['reference_key']]
    sections = parent['sections']
    matches = [i for i, section in enumerate(sections) if section.get('id') == report_contract['section_id']]
    check(len(matches) == 1 and matches[0] == len(sections) - 1, 'Unique new notes-only section must be last')
    removed = sections.pop()
    check(removed['metrics'] == [] and graph(removed) == delta['expected_section_native'], 'Exact qualified final notes-only section')
    check(graph(current) == baseline['damage_result']['native'], 'Only two precise additions removed; whole old native types/order/aliases/content intact')
    check(capture['three_texts']['applicable'] is baseline['three_texts']['applicable'] is True, 'Three applicable actual texts')
    for mode in ('default', 'estimate', 'technical'):
        before = baseline['three_texts']['strings'][mode]; text = before
        insertions = delta['text_insertions'][mode]
        check(type(insertions) is list and insertions, 'Exact source-qualified insertion spans')
        previous = len(before) + 1
        for addition in sorted(insertions, key=lambda row: row['offset'], reverse=True):
            offset = addition['offset']; span = addition['text']
            check(integer(offset) and offset <= len(before) and offset < previous and type(span) is str and span
                  and sha(span.encode('utf-8')) == addition['sha256'], 'Exact original-offset UTF8 insertion')
            text = text[:offset] + span + text[offset:]; previous = offset
        check(text == capture['three_texts']['strings'][mode], 'Complete actual text, with all old spans/whitespace retained')
        tails = [row for row in insertions if row['text'].startswith(report_contract['technical_tail_prefix'])]
        if mode == 'technical':
            check(len(tails) == 1 and tails[0]['offset'] == len(before)
                  and not tails[0]['text'].endswith('\n'), 'Exact double-LF technical tail at original end, no rstrip/trailing LF')
        else:
            check(not tails and report_contract['technical_tail_prefix'] not in text, 'Technical full source tail stays out of default/estimate')

def native090(value):
    kind=type(value).__name__
    if value is None or type(value) in (bool,int,str):return {'type':kind,'value':value}
    if type(value) is float:return {'type':'float','hex':value.hex()}
    if type(value) in (list,tuple):return {'type':kind,'items':[native090(v) for v in value]}
    if type(value) is dict:return {'type':'dict','items':[[native090(k),native090(v)] for k,v in value.items()]}
    raise AssertionError(('unhandled native value',kind))

def projection090(result):
    keys=['attack','total_damage','components','attack_speed','base_attack_speed','interval_seconds','timing']
    if 'total_healing' in result:keys.append('total_healing')
    keys.extend(k for k in result if k.endswith('_reference'))
    out={key:result[key] for key in dict.fromkeys(keys)}
    out['estimate']={key:result['estimate'][key] for key in ('training','base_stats','skill')}
    return out


def legacy_inverse(value):
    kind = value['type']
    if kind in ('NoneType', 'bool', 'int', 'str'):
        types = {'NoneType': type(None), 'bool': bool, 'int': int, 'str': str}
        result = value['value']; check(type(result) is types[kind], 'Legacy original scalar type')
    elif kind == 'float':
        result = float.fromhex(value['hex'])
        check(math.isfinite(result) and result.hex() == value['hex'], 'Legacy original exact finite float hex')
    elif kind == 'dict':
        result = {legacy_inverse(k): legacy_inverse(v) for k, v in value['items']}
    elif kind in ('list', 'tuple'):
        items = [legacy_inverse(x) for x in value['items']]
        result = tuple(items) if kind == 'tuple' else items
    else:
        raise ValueError('Unknown original legacy native type: ' + str(kind))
    check(native090(result) == value, 'Original recursive native full type/order roundtrip')
    return result


def original52_archive(spec, receipt, source):
    reference = spec['actual_legacy_state_archive']; meta = receipt['new_state_archive090']
    check(canonical(reference['path']) == canonical(str(COMPAT / meta['file'])), 'Exact original legacy state archive path')
    compressed = read_ref(reference); raw = gzip.decompress(compressed)
    check(len(compressed) == meta['bytes'] and sha(compressed) == meta['sha256']
          and len(raw) == meta['decoded_bytes'] and sha(raw) == meta['decoded_sha256'], 'Complete original52 compressed/decoded archive')
    data = json.loads(raw)
    check(data['format_version'] == 1 and data['passed'] is True and data['actual_main_window_execution_only'] is True,
          'Actual original new-window state archive source/live witness')
    tree = ast.parse(source)
    planned_assignments = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                           and any(isinstance(t, ast.Name) and t.id == 'rows090' for t in n.targets)]
    check(len(planned_assignments) == 1, 'Unique frozen original52 plan literal')
    planned = ast.literal_eval(planned_assignments[0].value)
    states = data['actual_new_window_states']
    check(len(states) == meta['records'] == data['expected_UI_state_rows'] == len(planned), 'Actual state count bound to original source literal, not guessed')
    for row, expected in zip(states, planned):
        check(row['passed'] is True and row['section'] == expected['section'] and row['pair_id'] == expected['pair_id']
              and row['widget_checked'] is expected['widget_checked'], 'Exact original ordered live52 state')
        scenario = legacy_inverse(row['scenario_native']); result = legacy_inverse(row['result_native'])
        check(encoded_json(scenario) == encoded_json(row['scenario']) and encoded_json(result) == encoded_json(row['result']),
              'Original52 whole saved JSON projections match precise native types/order/float values')
        check(encoded_json(projection090(result)) == encoded_json(expected['expected_public_projection']), 'Complete source-qualified original52 public projection')
        for key, value in expected['input'].items():
            check(native090(scenario[key]) == native090(value), 'Original actual caller input preserves each requested type')
        check('base_attack' not in scenario and row['explicit_three_text_requests'] == 3
              and row['reports']['estimate'] == row['reports']['default'], 'Original caller and actual three text requests')
    REPORT['actual_legacy_state_archive'] = metadata(Path(reference['path']))
    REPORT['original52_saved_states_verified'] = len(states)


def new_subgroup(binding, plan, baseline, receipt, summaries, states):
    numerical_links = []

    def bind_numerical_capture(capture, ids, case_id, capture_kind):
        # _profile095 appends these IDs at actual API entry; each source-defined
        # action slice ends after _capture095, which invokes no numerical API.
        # Current source-bound calculate_damage is nonrecursive. Use the last
        # slice item, never a guessed maximum over the whole call ledger.
        whole = decode(capture['damage_result']['native'])
        check(type(whole) is dict and list(whole) == ['scenario', 'result']
              and type(whole['scenario']) is dict and type(whole['result']) is dict,
              'Whole actual UI numerical wrapper retains original scenario and postprocessed result')
        check(type(ids) is list and ids and all(integer(sequence, 1) for sequence in ids)
              and ids == sorted(set(ids)), 'Actual numerical capture API slice is complete ordered entry IDs')
        api = summaries[ids[-1]]
        check(api['entry'] == 'rouge/damage.py:calculate_damage'
              and api['scope'] == 'new095_behavior_subgroup' and api['case'] == case_id
              and api['outcome'] == 'returned_dict',
              'Final source-qualified numerical API actually returned a complete dictionary')
        if capture_kind == 'manual':
            check(len(ids) == 1 and api['phase'] == 'actual_manual_button',
                  'Numerical manual capture binds its single independent actual API')
        scenario_sha = graph_sha(graph(whole['scenario']))
        caller_sha = graph_sha(graph({'scenario': whole['scenario']}))
        check(api['scenario_native_sha256'] == scenario_sha and api['caller_native_sha256'] == caller_sha,
              'API original unchanged caller/scenario fingerprints equal scenario from whole decoded UI graph')
        matches = [entry for entry in summaries.values()
                   if entry['entry'] == 'rouge/app.py:MainWindow.calculate'
                   and entry['scope'] == 'new095_behavior_subgroup' and entry['case'] == case_id
                   and entry['phase'] == api['phase'] and entry['sequence'] < api['sequence']
                   and entry['outcome'] == 'numerical_result_available'
                   and entry['UI_damage_result_native_sha256'] == graph_sha(capture['damage_result']['native'])
                   and entry['visible_status'] == capture['visible_status']]
        check(matches, 'Actual same-action MainWindow return binds complete final numerical capture after real postprocessing')
        numerical_links.append({'case': case_id, 'capture': capture_kind,
                                'API_sequence': api['sequence'],
                                'matching_MainWindow_sequences': [entry['sequence'] for entry in matches],
                                'API_outcome': api['outcome'],
                                'caller_native_sha256': api['caller_native_sha256'],
                                'scenario_native_sha256': api['scenario_native_sha256'],
                                'API_returned_native_sha256': api['returned_native_sha256'],
                                'postprocessed_UI_damage_result_native_sha256': graph_sha(capture['damage_result']['native']),
                                'raw_API_result_equals_UI_postprocessed_result_claimed': False})

    expected_ids = []
    for case in binding['cases']:
        if case['step']['action'] != 'fresh_window':
            expected_ids.extend([case['id'] + '/before-action', case['id'] + '/automatic-before-manual'])
        expected_ids.append(case['id'])
    check([row['id'] for row in states] == expected_ids and len(set(expected_ids)) == len(expected_ids),
          'Complete ordered before/automatic-before-manual/final state sequence; no failure rows')
    state_cases = {}
    for case in binding['cases']:
        if case['step']['action'] != 'fresh_window':
            state_cases[case['id'] + '/before-action'] = (case, 'before')
            state_cases[case['id'] + '/automatic-before-manual'] = (case, 'automatic')
        state_cases[case['id']] = (case, 'final')
    for wrapper in states:
        case, stage = state_cases[wrapper['id']]
        source_state_record(wrapper, case, stage, receipt['source_guard095']['before'])
    final_rows = {row['id']: row['record'] for row in states if row['id'] in {case['id'] for case in binding['cases']}}
    state_records = {row['id']: row['record'] for row in states}
    actual_behavior = receipt['actual095_behavior_rows']
    check([row['id'] for row in actual_behavior] == [case['id'] for case in binding['cases']]
          and all(row['passed'] is True and row['action'] == case['step']['action'] for row, case in zip(actual_behavior, binding['cases'])),
          'Actual new behavior rows exactly match source-qualified plan, not old4283 count')
    actual_new_checks = [row for row in receipt['checks'] if row.get('scope') == 'actual_full095_source_bound_behavior']
    check(len(actual_new_checks) == len(binding['cases']) and [row['id'] for row in actual_new_checks] == [c['id'] for c in binding['cases']]
          and receipt['actual_total_checks095'] == receipt['legacy_original4283_actual_checks'] + len(actual_new_checks),
          'Original legacy closure plus actual measured new row count')
    manual_buttons = 0; texts = 0
    for case in binding['cases']:
        row = final_rows[case['id']]; step = case['step']
        check(row['passed'] is True and row['planned']['native'] == graph(step), 'Actual completed source-bound new state')
        auto = row['automatic']
        check(type(auto['visible_status']) is str and type(auto['UI']) is dict, 'Actual saved visible controls/status')
        if step['action'] == 'fresh_window':
            durable(row['durable_after'])
            if decode(auto['damage_result']['native']) is not None:
                bind_numerical_capture(auto, row['all_API_sequences'], case['id'], 'fresh_window_automatic')
        snapshots = [auto]
        if step['action'] != 'fresh_window':
            manual_buttons += 1
            manual = row['manual']; snapshots.append(manual)
            before_record = state_records[case['id'] + '/before-action']
            automatic_record = state_records[case['id'] + '/automatic-before-manual']
            check(before_record['id'] == automatic_record['id'] == row['id']
                  and before_record['passed'] is automatic_record['passed'] is False
                  and before_record['planned']['native'] == automatic_record['planned']['native'] == row['planned']['native']
                  and graph(before_record['durable_before']) == graph(automatic_record['durable_before']) == graph(row['durable_before'])
                  and graph(automatic_record['automatic']) == graph(auto)
                  and graph(automatic_record['durable_after_automatic']) == graph(row['durable_after_automatic']),
                  'Complete intermediate checkpoint snapshots match final state without invented temporal identity')
            durable(row['durable_before']); durable(row['durable_after_automatic'])
            check(row['full_native_JSON_three_texts_auto_manual_equal'] is True,
                  'Source-qualified actual manual full-state assertion completed')
            if step['action'] not in ('account_observation', 'run_observation'):
                check(graph(row['durable_before']) == graph(row['durable_after_automatic']), 'Preview calculation preserves complete RunState/account/files')
            check(auto['damage_result']['native'] == manual['damage_result']['native']
                  and graph(auto['three_texts']) == graph(manual['three_texts']) and auto['visible_status'] == manual['visible_status'],
                  'Automatic/manual complete native result, three texts and UI status equality')
            for name, item in [('automatic', auto), ('manual', manual)]:
                ids = item['API_sequences']
                check(type(ids) is list and len(ids) == len(set(ids)), 'Unique actual new state API sequences')
                for sequence in ids:
                    entry = summaries[sequence]
                    check(entry['entry'] == 'rouge/damage.py:calculate_damage' and entry['scope'] == 'new095_behavior_subgroup'
                          and entry['case'] == case['id'], 'Actual new state API entry scope/case')
                    if name == 'manual':
                        check(entry['phase'] == 'actual_manual_button', 'Actual independent real manual button call')
            expected_kind = step.get('expected', {}).get('kind', 'numerical_result')
            if expected_kind in ('JSON_error_before_numerical_API', 'natural_early_return'):
                check(decode(auto['damage_result']['native']) is None and not auto['API_sequences'] and not manual['API_sequences'],
                      'Actual explicit UI None/error branch before numerical API, not an unavailable classification')
                if expected_kind == 'JSON_error_before_numerical_API':
                    check(auto['visible_status'] == step['expected']['message'], 'Exact actual JSON error status')
                else:
                    check(step['expected']['text_contains'] in auto['visible_status'], 'Exact source natural early-return status')
            else:
                check(type(decode(auto['damage_result']['native'])) is dict and len(manual['API_sequences']) == 1, 'Actual complete numerical result and one independent manual API')
                bind_numerical_capture(manual, manual['API_sequences'], case['id'], 'manual')
                if auto['API_sequences']:
                    bind_numerical_capture(auto, auto['API_sequences'], case['id'], 'automatic')
                if step['action'] in ('technical', 'raw'):
                    check(not auto['API_sequences'] and auto['actual_entries'].get('rouge/app.py:MainWindow.calculate', 0) == 0
                          and auto['actual_entries'].get('rouge/app.py:MainWindow.render_damage', 0) > 0, 'Actual technical/raw render-only branch')
                else:
                    check(auto['API_sequences'], 'Actual automatic numerical API entry required')
            matching_manual = [entry for entry in summaries.values() if entry['entry'] == 'rouge/app.py:MainWindow.calculate'
                               and entry['scope'] == 'new095_behavior_subgroup' and entry['case'] == case['id'] and entry['phase'] == 'actual_manual_button']
            check(any(entry['UI_damage_result_native_sha256'] == graph_sha(manual['damage_result']['native'])
                      and entry['visible_status'] == manual['visible_status'] for entry in matching_manual),
                  'Actual MainWindow manual return snapshot binds complete UI capture after API/report processing')
            if case['comparison'] == 'same_action_auto_manual':
                check(step['action'] == 'numeric_callback' and auto['API_sequences'], 'Source-qualified extra callback behavior')
                before = decode(row['before_callback_damage_result']['native']); after = decode(auto['damage_result']['native'])
                key = binding['report_contract']['reference_key']
                check(graph(before['result']['report'][key]) == graph(after['result']['report'][key]), 'Extra callback preserves selected source reference exactly')
        for item in snapshots:
            result = decode(item['damage_result']['native'])
            if result is None:
                check(item['three_texts']['applicable'] is False and item['three_texts']['visible_status'] == item['visible_status'], 'Actual UI None retains explicit full status and no invented formatted result')
            else:
                check(item['three_texts']['applicable'] is True and type(item['three_texts']['strings']) is dict
                      and set(item['three_texts']['strings']) == {'default', 'estimate', 'technical'}
                      and all(type(text) is str for text in item['three_texts']['strings'].values())
                      and item['three_texts']['strings']['estimate'] == item['three_texts']['strings']['default'], 'All actual full three text strings, no partial/projection stripping')
                texts += 3
                strings = item['three_texts']['strings']
                display = json.dumps(result, ensure_ascii=False, indent=2) if item['UI']['raw_damage'] else strings['technical' if item['UI']['technical'] else 'default']
                check(item['visible_status'] == display.replace(chr(160), ' '), 'Exact actual QPlainTextEdit normal/raw/technical display normalization')
            if case['comparison'] == 'paired_actual094':
                old = pointer(baseline[case['baseline_file']], case['baseline_pointer'])
                which = 'manual' if item is row.get('manual') else 'automatic'
                strict_baseline(item, old[which], case, binding['report_contract'])
                if step['action'] != 'fresh_window':
                    check(item['UI']['current_operator_state']['native'] == old[which]['UI']['current_operator_state']['native'], 'Actual94 current owner/source precedence native state')
        REPORT['new_states_verified'] += 1
    check(receipt['actual_explicit_buttons095'] == manual_buttons
          and receipt['actual_explicit_three_text_requests095'] == texts, 'Actual explicit new button/text requests measured from complete saved states')
    REPORT['actual_new_manual_buttons'] = manual_buttons
    REPORT['actual_new_explicit_text_requests'] = texts
    REPORT['new095_whole_old_native_and_text_delta_verified'] = True
    REPORT['actual_numerical_API_UI_links'] = numerical_links
    REPORT['numerical_API_UI_link_scope'] = 'Actual source-defined ordered API slices, successful returned_dict and unchanged caller/scenario fingerprints bind whole UI capture; raw API result is not falsely equated to source-postprocessed UI result.'
    REPORT['manual_persistence_scope'] = 'Saved before/after-automatic full native/raw bytes plus exact frozen actual manual-persistence live assertion at trusted root launch; no separately stored after-manual durable snapshot is invented.'


def validate(spec, spec_ref, output_path):
    global MAPPING, REGISTRY
    check(spec['format_version'] == 1 and spec['section'] == 95
          and spec['status'] == 'ROOT_BOUND_ACTUAL_FULL095_SAVED_INPUTS', 'PENDING/null input plan is not actual fullUI data')
    check(spec['actual_source_guard']['sha256'] == EXPECTED_GUARD_SHA
          and canonical(spec['actual_source_guard']['path']) == '/workspace/.continuation/root-source-095-v2.json', 'Exact actual root095-v2 SOURCE guard')
    read_ref(spec['actual_source_guard'])
    wrapper = read_ref(spec['wine_wrapper'])
    check(sha(wrapper) == '65dd3806511e037290291ac592246abe80f346b1004b88c81e798612db4d79c8', 'Exact actual Wine wrapper')
    MAPPING = actual_wine_mapping(spec)
    inputs = spec['ui_binding_input_refs']
    check(type(inputs) is list and inputs, 'Explicit root-owned actual binding input reference list')
    for row in inputs:
        key = canonical(row['path'])
        check(key not in REGISTRY, 'Root input refs cannot alias one another')
        read_ref(row); REGISTRY[key] = row
    # Outputs cannot overwrite any current source/contract/evidence even on failed validation.
    all_refs = [spec_ref, spec['actual_source_guard'], spec['actual_UI_receipt'], spec['actual_native_index'],
                spec['actual_legacy_state_archive'], spec['wine_wrapper'], spec['actual_baseline_plan'],
                spec['actual_baseline_primary_exit'], spec['saved_source_review']['file'],
                spec['final_UI']['runner'], spec['final_UI']['manifest'], spec['final_UI']['formal_source_review'],
                spec['pending_UI']['manifest'], spec['actual_UI_primary']['prelaunch'],
                spec['actual_UI_primary']['root_observation'], spec['actual_UI_primary']['exit_code_file'],
                spec['actual_UI_primary']['console_log'], spec['ui_retry']['source_contract'],
                *inputs, *spec['actual_PNGs'], *spec['baseline_prerequisite_refs']]
    check(all(canonical(row['path']) != output_path for row in all_refs)
          and not Path(output_path).is_relative_to(NATIVE_DIRECTORY)
          and not REPO.is_relative_to(Path(output_path)), 'Fresh saved proof cannot alias/contain any explicit source or evidence input')
    own = metadata(Path(__file__))
    read_ref(own)
    saved_review = spec['saved_source_review']
    review = json.loads(read_ref(saved_review['file'])); p = saved_review['pointers']
    actual_argv = [str(REPO / '.venv/bin/python'), own['path'], '--spec', spec_ref['path'], '--output', output_path]
    check(pointer(review, p['source_gate']) is True and pointer(review, p['runtime']) is False
          and pointer(review, p['runner_sha256']) == own['sha256'] and pointer(review, p['argv']) == actual_argv,
          'Actual saved helper independent source gate binds full future execution argv and immutable source bytes')
    binding, mapping, plan, legacy, source = source_and_binding(spec)
    primary_launch(spec)
    receipt = ui_receipt(spec, mapping, legacy)
    baseline = baseline_documents(binding, spec)
    summaries, states = native_archive(spec, receipt, source)
    original52_archive(spec, receipt, source)
    new_subgroup(binding, plan, baseline, receipt, summaries, states)
    image_refs = spec['actual_PNGs']
    check(type(image_refs) is list and {canonical(row['path']) for row in image_refs} == {str(COMPAT / name) for name in PNG_NAMES}
          and len(image_refs) == len(PNG_NAMES), 'Exact four actual successful fullUI PNG paths from frozen source')
    for reference in image_refs:
        png(reference)
    check(maintained() == mapping, 'Whole maintained source unchanged during independent saved review')
    for row in list(REPORT['checked_file_refs'].values()):
        read_ref(row)
    REPORT.update(passed=True, status='PASS_SAVED_ONLY_ACTUAL_FULL095_UI_EVIDENCE',
                  validation_kind='SAVED_ONLY', actual_PNGs=[metadata(Path(row['path'])) for row in image_refs],
                  actual_PNGs_viewed_by_this_validator=0,
                  verifier_source=own, input_spec=spec_ref,
                  native_Windows_game_chat_verified=False, complete_full095_or_section_validation=False,
                  completed_section_increment=0, project_calls=0,
                  actual_fullUI_saved_evidence_verified=True,
                  runtime_class_identity_reconstructed=False,
                  native_identity_limits='Saved verifier validates complete within-snapshot type/order/alias/float-hex/raw-byte graphs and caller value preservation. Actual Qt class, button and cross-time object identity are source-qualified live assertions bound to the exact FINAL runner and trusted root prelaunch/process observation; JSON cannot reconstruct Python identity across time.',
                  count_qualification='Actual measured source/entry/state/check counts; no fixed native chunk count, no global total-minus52 calculation, no unavailable rows classified as successful tests.',
                  primary_status_qualification='Actual UI primary status read physically and matched to trusted root observations. This helper does not claim its own shell exit; root independently captures the eighth saved-review primary status.')


def main():
    global REPORT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = canonical(str(args.output))
    check(Path(output).is_relative_to(Path('/workspace/.continuation')),
          'Saved-only proof output must remain outside the repository in public continuation')
    check(not Path(output).exists() and not Path(output).is_symlink(), 'Preserve every earlier saved-proof attempt')
    spec_path = Path(canonical(str(args.spec)))
    check(output != str(spec_path) and output != canonical(str(Path(__file__))), 'Output cannot overwrite helper/spec')
    REPORT = {'format_version': 1, 'section': 95, 'passed': False, 'validation_kind': 'SAVED_ONLY',
              'status': 'SAVED_ONLY_VALIDATION_IN_PROGRESS_NOT_PASSED', 'checked_file_refs': {},
              'snapshots_verified': 0, 'raw_files_verified': 0, 'new_states_verified': 0,
              'native_Windows_game_chat_verified': False, 'complete_full095_or_section_validation': False,
              'completed_section_increment': 0, 'project_calls': 0, 'actual_PNGs_viewed_by_this_validator': 0}
    # Planning/null specs fail before evidence decoding, never generate a PASS fixture.
    spec_ref = metadata(spec_path)
    spec = json.loads(read_ref(spec_ref))
    try:
        validate(spec, spec_ref, output)
    except Exception as error:
        REPORT.update(passed=False, status='FAIL_SAVED_ONLY_ACTUAL_FULL095_UI_EVIDENCE',
                      error={'type': type(error).__name__, 'message': str(error)})
    REPORT['checked_file_refs'] = dict(sorted(REPORT['checked_file_refs'].items()))
    with Path(output).open('x', encoding='utf-8') as handle:
        json.dump(REPORT, handle, ensure_ascii=False, allow_nan=False, indent=2); handle.write('\n')
    print(json.dumps({key: REPORT.get(key) for key in ('passed', 'status', 'snapshots_verified', 'new_states_verified', 'error')}, ensure_ascii=False))
    return 0 if REPORT['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
