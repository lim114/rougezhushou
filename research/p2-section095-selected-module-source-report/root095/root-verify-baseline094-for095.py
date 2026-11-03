"""Independently check saved actual94 Wine evidence; import no product code."""
from pathlib import Path
import gzip
import hashlib
import json
import math

ROOT = Path('/workspace')
LOCAL = ROOT / '.continuation'
OUT = ROOT / '.compat'
PACK = LOCAL / 'ui-095-module-report-pending/baseline094-v2'
REPORT = LOCAL / 'root-saved-baseline094-for095-review.json'
assert not REPORT.exists(), 'Preserve any earlier report'
report = {'format_version': 1, 'passed': False, 'validation_kind': 'SAVED_ONLY',
          'project_calls': 0, 'native_Windows_game_chat_verified': False,
          'completed_section_increment': 0, 'input_bindings': {},
          'snapshots_verified': 0, 'states_verified': 0}


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def bind(path, expected=None):
    data = path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if expected is not None:
        check(sha == expected, 'input hash: ' + str(path))
    report['input_bindings'][str(path)] = {'bytes': len(data), 'sha256': sha}
    return data


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


def scan(value):
    queue = [value]
    while queue:
        item = queue.pop()
        if type(item) is dict:
            if 'native' in item and 'native_inverse_verified' in item:
                check(item['native_inverse_verified'] is True, 'snapshot flag')
                restored = decode(item['native'])
                if item.get('schema') == 'raw-file-bytes-evidence-v1':
                    check('JSON_projection' not in item, 'no bytes JSON projection')
                    check(restored is None or type(restored) is bytes, 'raw bytes')
                    expected = {'file_exists': restored is not None,
                                'raw_hex': restored.hex() if restored is not None else None,
                                'byte_count': len(restored) if restored is not None else None,
                                'sha256': hashlib.sha256(restored).hexdigest()
                                if restored is not None else None}
                    check(item['JSON_safe_raw_bytes'] == expected, 'raw file bytes')
                else:
                    check('JSON_projection' in item, 'ordinary JSON projection')
                    check(encoded_json(restored) == encoded_json(item['JSON_projection']),
                          'complete ordered JSON projection')
                report['snapshots_verified'] += 1
            else:
                queue.extend(item.values())
        elif type(item) is list:
            queue.extend(item)


try:
    rc = bind(LOCAL / 'root-baseline094-for095.exit-code')
    check(rc == b'0\n', 'actual captured primary shell exit0')
    prelaunch = json.loads(bind(LOCAL / 'root-baseline094-for095-prelaunch.json'))
    check(prelaunch['source_gate_passed'] is True and
          prelaunch['all_new_outputs_absent'] is True, 'root prelaunch')
    receipt_path = OUT / 'wine-module-report-baseline-094-for095.json'
    receipt = json.loads(bind(receipt_path))
    check(receipt['passed'] is receipt['workflow_complete'] is True, 'runtime PASS')
    check(receipt['completed_section_increment'] == 0, 'baseline not completion')
    check(receipt['source_drift'] == [], 'runtime zero source drift')
    check(receipt['private_state_isolated'] is True, 'public isolated fixtures')
    check(receipt['game_capture_requests'] == receipt['chat_requests'] == 0, 'no side effects')
    for key, name in [('runner_sha256', 'wine-module-report-baseline-094-for095.py'),
                      ('plan_sha256', 'wine-module-report-shared095-plan.json'),
                      ('source_guard_sha256', 'wine-module-report-baseline094-source.json')]:
        bind(PACK / name, receipt[key])
    plan = json.loads((PACK / 'wine-module-report-shared095-plan.json').read_bytes())
    guard = json.loads((PACK / 'wine-module-report-baseline094-source.json').read_bytes())
    check(receipt['source_sha256_before'] == receipt['source_sha256_after'] ==
          guard['source_sha256_after'], 'actual94 source map binding')
    check(len(guard['source_sha256_after']) == 732, 'actual94 source count')
    for name, expected in guard['source_sha256_after'].items():
        check(hashlib.sha256((ROOT / 'rougezhushou' / name).read_bytes()).hexdigest()
              == expected, 'current source: ' + name)
    bind(ROOT / 'rougezhushou/verification/sections/094.json',
         receipt['actual94_receipt_sha256'])
    bind(LOCAL / 'section094-archived-working-tree-closure.json',
         receipt['actual94_closure_sha256'])
    meta = receipt['records']
    compressed = bind(OUT / meta['file'], meta['sha256'])
    raw = gzip.decompress(compressed)
    check(len(compressed) == meta['bytes'] and len(raw) == meta['decoded_bytes']
          and hashlib.sha256(raw).hexdigest() == meta['decoded_sha256'], 'native archive')
    data = json.loads(raw)
    check(data['schema'] == 'focused-module-report-baseline-v1' and
          data['passed'] is True and data['Qt_slot_exceptions'] == [], 'complete archive')
    scan(data)
    calls = data['targeted_calls']
    check([row['sequence'] for row in calls] == list(range(1, len(calls) + 1)),
          'complete actual call ledger')
    by_sequence = {row['sequence']: row for row in calls}
    for key, kind in [('API_entries', 'calculate_damage'),
                      ('prepared_entries', '_prepare_damage')]:
        rows = data[key]
        check(rows == [row for row in calls if row['key'] == kind], key + ' complete ledger')
        for row in rows:
            check(row['caller_unchanged'] is True and
                  row['caller_before']['native'] == row['caller_after']['native'],
                  'actual original caller preserved')
            expected_outcome = 'returned_dict' if kind == 'calculate_damage' else 'returned_prepared_tuple'
            check(row['outcome'] == expected_outcome, 'actual outcome')
            if kind == '_prepare_damage':
                prepared = decode(row['returned']['native'])
                check(type(prepared) is tuple and type(prepared[0]) is dict and
                      graph(prepared[0]) == row['local_prepared_scenario_at_exit']['native'],
                      'actual prepared tuple first scenario')
    states = data['states']
    check(len(states) == receipt['states'] == plan['counts']['states_planned'] == 41,
          'complete41 states')
    check([row['id'] for row in states] == [row['id'] for row in plan['steps']] and
          len({row['id'] for row in states}) == 41, 'exact ordered plan')
    buttons, texts, windows = 0, 0, set()
    for state, planned in zip(states, plan['steps']):
        check(state['passed'] is True and
              graph(planned) == state['planned']['native'], 'planned actual state')
        windows.add(state['window_after'])
        auto = state['automatic']
        check(auto['damage_result']['native'] == auto['UI']['damage_result']['native'],
              'captured UI result binding')
        if planned['action'] != 'fresh_window':
            manual = state['manual']
            buttons += 1
            for item in (auto, manual):
                check(item['outcome'] == planned.get('expected', {}).get('kind', 'numerical_result'),
                      'actual expected branch')
                for key in ('API_sequences', 'prepared_sequences'):
                    check(len(item[key]) == len(set(item[key])), 'unique scope sequences')
                    for seq in item[key]:
                        row = by_sequence[seq]
                        check(row['step'] == state['id'] and row['window'] == state['window_after'],
                              'scope sequence binding')
                check(item['damage_result']['native'] == item['UI']['damage_result']['native'],
                      'automatic/manual UI result')
            check(auto['damage_result']['native'] == manual['damage_result']['native']
                  and auto['visible_status'] == manual['visible_status']
                  and auto['three_texts'].get('strings') == manual['three_texts'].get('strings'),
                  'automatic/manual complete native and three texts')
            check(state['durable_after_automatic'] == state['durable_after'],
                  'manual persistent state exact')
            if planned['action'] not in ('account_observation', 'run_observation'):
                check(state['durable_before'] == state['durable_after'], 'preview state exact')
        for item in [auto] + ([state['manual']] if 'manual' in state else []):
            three = item['three_texts']
            if three['applicable']:
                check(three['requests'] == 3 and three['full_native_preserved'] is True,
                      'three actual texts')
                check(three['strings']['estimate'] == three['strings']['default'],
                      'actual estimate/default text')
                texts += 3
        report['states_verified'] += 1
    check(buttons == receipt['explicit_button_requests'] == data['explicit_buttons'] == 39,
          '39 real button checks')
    check(texts == receipt['explicit_three_text_requests'] == data['explicit_three_text_requests'] == 228,
          '228 actual explicit texts')
    check(len(windows) == receipt['fresh_windows'] == data['fresh_windows'] == 2, '2 actual windows')
    check(len(data['API_entries']) == 113 and len(data['prepared_entries']) == receipt['prepared_entries'] == 113,
          '113 actual API and prepared entries')
    check(receipt['actual_API_outcomes'] == {'returned_dict': 113, 'raised_exception': 0,
          'returned_none_or_unobserved_unwind': 0}, 'actual API totals')
    check(len(data['checks']) == 41 and all(x['passed'] is True for x in data['checks']),
          'all actual checks')
    report.update(passed=True, status='PASS_SAVED_ONLY_ACTUAL94_BASELINE_FOR095',
                  actual={'states': 41, 'fresh_MainWindows': 2, 'manual_buttons': buttons,
                          'three_text_requests': texts, 'API_entries': 113,
                          'prepared_entries': 113, 'targeted_calls': len(calls),
                          'source_hashes': 732},
                  actual_runtime_receipt_sha256=report['input_bindings'][str(receipt_path)]['sha256'],
                  actual_native_archive_sha256=meta['sha256'],
                  native_identity_limits='Saved native alias/order/type verification; real classes/button callbacks require frozen formal source and actual root launch.',
                  actual_PNGs_viewed=0, scope='Baseline has no PNG and is not section completion.')
except BaseException as error:
    report.update(passed=False, status='FAIL_SAVED_ONLY_ACTUAL94_BASELINE_FOR095',
                  error={'type': type(error).__name__, 'message': str(error)})
with REPORT.open('x', encoding='utf-8') as stream:
    json.dump(report, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({key: report.get(key) for key in
                 ('passed', 'status', 'states_verified', 'snapshots_verified', 'error')}))
raise SystemExit(0 if report['passed'] else 1)
