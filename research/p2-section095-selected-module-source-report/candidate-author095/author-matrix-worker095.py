"""Execute one frozen public calculation tree and retain complete typed records."""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time


def native_graph(value):
    """Preserve native types, float.hex, ordered dictionary keys and aliases."""
    nodes, identities = [], {}
    def encode(item):
        kind = type(item)
        if item is None:
            return {'type': 'NoneType'}
        if kind is bool:
            return {'type': 'bool', 'value': item}
        if kind is int:
            return {'type': 'int', 'value': str(item)}
        if kind is float:
            return {'type': 'float', 'hex': item.hex()}
        if kind is str:
            return {'type': 'str', 'value': item}
        if kind is bytes:
            return {'type': 'bytes', 'hex': item.hex()}
        if kind not in (dict, list, tuple):
            raise TypeError('unsupported native type: ' + str(kind))
        identity = id(item)
        if identity in identities:
            return {'ref': identities[identity]}
        index = len(nodes)
        identities[identity] = index
        node = {'type': kind.__name__, 'items': []}
        nodes.append(node)
        if kind is dict:
            node['items'] = [[encode(key), encode(child)] for key, child in item.items()]
        else:
            node['items'] = [encode(child) for child in item]
        return {'ref': index}
    root = encode(value)
    return {'schema': 'native-types-order-alias-v1', 'root': root, 'nodes': nodes}


def restored_graph(graph):
    """Independent inverse for the saved graph; tuples are acyclic in these results."""
    containers = {}
    def decode(token):
        if 'ref' not in token:
            kind = token['type']
            if kind == 'NoneType':
                return None
            if kind == 'bool':
                return token['value']
            if kind == 'int':
                return int(token['value'])
            if kind == 'float':
                return float.fromhex(token['hex'])
            if kind == 'str':
                return token['value']
            if kind == 'bytes':
                return bytes.fromhex(token['hex'])
            raise ValueError(kind)
        index = token['ref']
        if index in containers:
            return containers[index]
        node = graph['nodes'][index]
        kind = node['type']
        if kind == 'dict':
            value = {}
            containers[index] = value
            for key, child in node['items']:
                value[decode(key)] = decode(child)
        elif kind == 'list':
            value = []
            containers[index] = value
            value.extend(decode(child) for child in node['items'])
        elif kind == 'tuple':
            value = tuple(decode(child) for child in node['items'])
            containers[index] = value
        else:
            raise ValueError(kind)
        return value
    result = decode(graph['root'])
    if native_graph(result) != graph:
        raise AssertionError('saved native graph inverse not exact')
    return result


def hashes(tree, names):
    return {name: hashlib.sha256((tree / name).read_bytes()).hexdigest() for name in names}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tree', required=True)
    parser.add_argument('--plan', required=True)
    parser.add_argument('--guard', required=True)
    parser.add_argument('--records', required=True)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--checkpoint', required=True)
    args = parser.parse_args()
    tree, plan_path, guard_path = Path(args.tree), Path(args.plan), Path(args.guard)
    expected = json.loads(guard_path.read_text())['source_sha256_after']
    assert hashes(tree, expected) == expected, 'frozen tree guard mismatch before imports'
    for name in (args.records, args.receipt, args.checkpoint):
        assert not Path(name).exists(), 'refuse to overwrite actual evidence: ' + name
    sys.path.insert(0, str(tree))
    from rouge.damage import calculate_damage
    from rouge.reporting import format_report
    plan = json.loads(plan_path.read_text())
    calls = Counter()
    current = None
    def profile(frame, event, argument):
        if event == 'call' and frame.f_globals.get('__name__', '').startswith('rouge.'):
            key = frame.f_globals['__name__'] + '.' + frame.f_code.co_name
            calls[key] += 1
        if frame.f_code is calculate_damage.__code__:
            if event == 'call':
                current['entry_calls'] += 1
                current['entry_caller'] = native_graph(frame.f_locals['scenario'])
            elif event == 'return':
                current['return_events'] += 1
                current['return_event_native'] = native_graph(argument)
    started = time.monotonic()
    successes = failures = planned_errors = 0
    text_requests = 0
    completed = 0
    header = {'kind': 'header', 'status': 'REAL_EXTERNAL_LINUX_CALCULATION_MATRIX',
              'tree': str(tree), 'maintained_sources': len(expected),
              'guard_path': str(guard_path), 'guard_sha256': hashlib.sha256(guard_path.read_bytes()).hexdigest(),
              'plan_sha256': hashlib.sha256(plan_path.read_bytes()).hexdigest(),
              'source_sha256_before': expected, 'native_schema': 'native-types-order-alias-v1',
              'API_classification': 'observed outer return or caught original exception; total_damage=None is legitimate dict',
              'scope': 'public isolated calculation + real format_report normal/technical and JSON debug wrapper; no UI/Wine/private/network'}
    output = Path(args.records)
    with gzip.open(output, 'wt', encoding='utf-8', compresslevel=6) as archive:
        archive.write(json.dumps(header, ensure_ascii=False) + '\n')
        for index, case in enumerate(plan['cases']):
            caller = deepcopy(case['scenario'])
            before = native_graph(caller)
            current = {'entry_calls': 0, 'return_events': 0}
            call_counts_before = calls.copy()
            row = {'kind': 'state', 'index': index, 'id': case['id'], 'group': case['group'],
                   'scenario': case['scenario'], 'caller_before': before,
                   'expected_error': case.get('expected_error', False)}
            sys.setprofile(profile)
            try:
                result = calculate_damage(caller)
            except Exception as error:
                row['outcome'] = 'original_API_exception'
                row['error'] = {'class_module': type(error).__module__, 'class_name': type(error).__qualname__,
                                'args': native_graph(error.args), 'message': str(error)}
                planned_errors += 1
                if not case.get('expected_error'):
                    failures += 1
            else:
                assert type(result) is dict, 'actual API returned non-dict'
                row['outcome'] = 'returned_dict'
                row['native_result'] = native_graph(result)
                row['three_texts'] = {
                    'normal': format_report(result),
                    'technical': format_report(result, technical=True),
                    'structured': json.dumps({'scenario': caller, 'result': result}, ensure_ascii=False, indent=2),
                }
                text_requests += 3
                assert native_graph(result) == row['native_result'], 'actual formatter mutated native result'
                assert current['return_event_native'] == row['native_result'], 'API return event differs from saved result'
                restored_graph(row['native_result'])
                successes += 1
                if case.get('expected_error'):
                    failures += 1
            finally:
                sys.setprofile(None)
            row['caller_after'] = native_graph(caller)
            row['actual_API_entry_return'] = current
            row['actual_project_calls'] = dict(calls - call_counts_before)
            assert current['entry_calls'] == 1 and current['return_events'] == 1
            assert current['entry_caller'] == before == row['caller_after'], 'caller changed or entry snapshot stale'
            restored_graph(before)
            archive.write(json.dumps(row, ensure_ascii=False) + '\n')
            completed += 1
            if completed % 100 == 0:
                archive.flush()
                Path(args.checkpoint).write_text(json.dumps({'status': 'RUNNING', 'completed': completed,
                    'total': len(plan['cases']), 'last_completed_id': case['id'], 'errors_observed': planned_errors,
                    'unexpected_outcomes': failures, 'API_entries': calls['rouge.damage.calculate_damage']}, indent=2) + '\n')
        after = hashes(tree, expected)
        assert after == expected, 'frozen tree guard mismatch after matrix'
        receipt = {'format_version': 1, 'status': 'REAL_EXTERNAL_LINUX_MATRIX_COMPLETE',
            'passed': failures == 0, 'workflow_complete': completed == len(plan['cases']),
            'states': completed, 'returned_dict_states': successes, 'original_API_exception_states': planned_errors,
            'unexpected_outcomes': failures, 'actual_API_entries': calls['rouge.damage.calculate_damage'],
            'actual_three_text_requests': text_requests, 'actual_project_calls': dict(calls),
            'source_hashes': len(expected), 'source_sha256_after': after,
            'source_drift': [], 'elapsed_seconds': time.monotonic()-started,
            'plan_sha256': header['plan_sha256'], 'native_records': str(output),
            'genuine_native_windows_game_chat': False, 'UI_executed': False,
            'actual_primary_shell_status': 'root shell launcher captures separate exit-code artifact',
            'no_source_only_checks_counted_as_runtime_states': True}
        archive.write(json.dumps({'kind': 'tail', 'receipt': receipt}, ensure_ascii=False) + '\n')
    receipt['native_records_bytes'] = output.stat().st_size
    receipt['native_records_sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
    Path(args.receipt).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    Path(args.checkpoint).write_text(json.dumps({'status': 'COMPLETE', 'completed': completed,
        'total': len(plan['cases']), 'passed': receipt['passed']}, indent=2) + '\n')
    print(json.dumps({key: receipt[key] for key in ('status', 'passed', 'states', 'returned_dict_states',
        'original_API_exception_states', 'unexpected_outcomes', 'actual_API_entries',
        'actual_three_text_requests', 'native_records_bytes', 'native_records_sha256')}, ensure_ascii=False))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
