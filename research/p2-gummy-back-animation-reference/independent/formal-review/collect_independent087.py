"""Authorized once-only 12 pair sample / seven new tests, with actual entry ledgers."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import gzip
import hashlib
import importlib
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parent
AUTHOR = ROOT.parents[1] / 'p2-gummy-back-animation-reference-087-draft'
mode = sys.argv[1]
assert mode in ['baseline', 'draft', 'newtests']
tree = AUTHOR / ('draft' if mode == 'newtests' else mode)
sys.path.insert(0, str(tree))

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

freeze = json.loads((AUTHOR / 'author-freeze087.json').read_text())
for row in freeze['source_files']:
    raw = Path(row['draft_source_path']).read_bytes()
    assert len(raw) == row['draft_bytes'] and sha(raw) == row['draft_sha256']
for row in freeze['unchanged_author_consumer_sources']:
    raw = (tree / row['path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']

from rouge import damage, reporting, estimate, animation_reference, catalog

def native(value):
    cls = type(value)
    name = cls.__module__ + '.' + cls.__qualname__
    if isinstance(value, dict):
        return {'type': name, 'items': [{'key': native(k), 'value': native(v)} for k, v in value.items()]}
    if isinstance(value, (list, tuple)):
        return {'type': name, 'items': [native(v) for v in value]}
    if value is None:
        return {'type': name, 'value': None}
    if isinstance(value, bool):
        return {'type': name, 'value': value}
    if isinstance(value, int):
        return {'type': name, 'value_decimal': str(value)}
    if isinstance(value, float):
        return {'type': name, 'value_hex': float(value).hex()}
    if isinstance(value, str):
        return {'type': name, 'value': value}
    raise TypeError('Unaccounted native result type: ' + name)

type_root = ROOT / (mode + '-native-trees')
type_root.mkdir(exist_ok=True)
tree_inventory = {}
def preserve_native(value):
    raw = json.dumps(native(value), ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    digest = sha(raw)
    dst = type_root / (digest + '.json.gz')
    if not dst.exists():
        dst.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    assert gzip.decompress(dst.read_bytes()) == raw
    entry = {'source_path': str(dst), 'archive_path': str(dst.relative_to(ROOT)),
        'bytes': dst.stat().st_size, 'sha256': sha(dst.read_bytes()),
        'decoded_native_tree_bytes': len(raw), 'decoded_native_tree_sha256': digest}
    tree_inventory[digest] = entry
    return entry

entry_counts = {'calculate_damage': 0, 'format_estimate': 0, 'format_report_default': 0,
    'format_report_technical': 0, 'choices': 0, 'descriptor': 0, 'label': 0,
    'references_cache_miss_body': 0, 'catalog_cache_miss_body': 0, 'operator_profiles_cache_miss_body': 0}
codes = {damage.calculate_damage.__code__: 'calculate_damage',
    estimate.format_estimate.__code__: 'format_estimate', reporting.format_report.__code__: 'format_report',
    animation_reference.choices.__code__: 'choices', animation_reference.descriptor.__code__: 'descriptor',
    animation_reference.label.__code__: 'label', animation_reference.references.__wrapped__.__code__: 'references_cache_miss_body',
    catalog.catalog.__wrapped__.__code__: 'catalog_cache_miss_body',
    catalog.operator_profiles.__wrapped__.__code__: 'operator_profiles_cache_miss_body'}
def profiler(frame, event, arg):
    if event != 'call':
        return
    name = codes.get(frame.f_code)
    if name == 'format_report':
        name = 'format_report_technical' if frame.f_locals['technical'] is True else 'format_report_default'
    if name:
        entry_counts[name] += 1

sys.setprofile(profiler)
ledger = []
request_count = 0
limit = 11 if mode == 'newtests' else 12
real_damage = damage.calculate_damage
cached = None
cache_snapshot_helper_requests = 0
if mode != 'newtests':
    cached = {'catalog': catalog.catalog(), 'operator_profiles': catalog.operator_profiles(),
        'animation_references': animation_reference.references()}
    cache_snapshot_helper_requests += 3

def evaluate(scenario):
    global request_count
    if request_count >= limit:
        raise RuntimeError('Authorized new public-call budget exhausted before execution')
    request_count += 1
    row = {'actual_public_call_number': request_count, 'scenario': copy.deepcopy(scenario),
           'caller_before_native_tree': preserve_native(scenario)}
    if cached is not None:
        row['cached_data_before_native_trees'] = {key: preserve_native(value) for key, value in cached.items()}
    ledger.append(row)
    try:
        value = real_damage(scenario)
        row['native_result_tree_before_JSON'] = preserve_native(value)
        row.update({'accepted': True, 'result': value})
        return value
    except Exception as error:
        row.update({'accepted': False, 'error_type': type(error).__name__, 'error': str(error)})
        raise
    finally:
        row['caller_after_native_tree'] = preserve_native(scenario)
        row['caller_unchanged'] = row['caller_before_native_tree']['decoded_native_tree_sha256'] == row['caller_after_native_tree']['decoded_native_tree_sha256']
        if cached is not None:
            row['cached_data_after_native_trees'] = {key: preserve_native(value) for key, value in cached.items()}
            row['cached_data_unchanged'] = all(row['cached_data_before_native_trees'][key]['decoded_native_tree_sha256'] == row['cached_data_after_native_trees'][key]['decoded_native_tree_sha256'] for key in cached)

damage.calculate_damage = evaluate
text_requests = 0
test_summary = None
started_at = datetime.now(timezone.utc).isoformat()
try:
    if mode == 'newtests':
        suite = unittest.defaultTestLoader.loadTestsFromName('tests.test_gummy_back_animation_reference')
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        test_summary = {'tests_run': result.testsRun, 'passed': result.wasSuccessful(),
            'failure_count': len(result.failures), 'error_count': len(result.errors),
            'skipped_count': len(result.skipped)}
        assert result.testsRun == 7 and result.wasSuccessful() and request_count == 11
    else:
        cases = json.loads((ROOT / 'independent12-cases087.json').read_text())['cases']
        assert len(cases) == 12
        for case in cases:
            try:
                result = evaluate(copy.deepcopy(case['scenario']))
            except Exception:
                pass
            row = ledger[-1]
            row.update({'label': case['label'], 'expect': case['expect']})
            if row['accepted']:
                row['texts'] = {'plain': reporting.format_report(row['result']),
                    'technical': reporting.format_report(row['result'], technical=True),
                    'estimate': estimate.format_estimate(row['result'])}
                text_requests += 3
        assert request_count == 12
        returned_cached = {'catalog': catalog.catalog(), 'operator_profiles': catalog.operator_profiles(),
            'animation_references': animation_reference.references()}
        cache_snapshot_helper_requests += 3
        assert all(returned_cached[key] is cached[key] for key in cached)
    assert entry_counts['calculate_damage'] == request_count
finally:
    sys.setprofile(None)
    out = {'version': 1, 'mode': mode, 'tree_source_path': str(tree),
        'baseline_commit': freeze['author_baseline_commit'], 'source_freeze_sha256': sha((AUTHOR / 'author-freeze087.json').read_bytes()),
        'started_at_utc': started_at, 'finished_at_utc': datetime.now(timezone.utc).isoformat(),
        'actual_public_API_calls': request_count, 'public_entry_counts': entry_counts,
        'three_text_requests': text_requests,
        'direct_cache_snapshot_helper_requests_separate_from_production_body_entries': cache_snapshot_helper_requests,
        'native_before_JSON_saved': True, 'native_trees_content_addressed_complete': list(tree_inventory.values()),
        'test_summary': test_summary, 'items': ledger,
        'network_source_reader_compile_Qt_Wine_tracked_changes': 0,
        'caller_and_cached_trees_observation_scope': 'Actual same-process cached objects, type and scalar value trees before/after each public call; shared alias identities within trees are not inferred.'}
    raw = (json.dumps(out, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / ('independent-' + mode + '-results087.json.gz')
    path.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    assert gzip.decompress(path.read_bytes()) == raw
    summary = {key: out[key] for key in ['mode', 'actual_public_API_calls', 'public_entry_counts', 'three_text_requests',
        'direct_cache_snapshot_helper_requests_separate_from_production_body_entries', 'test_summary']}
    summary.update({'result_path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path.read_bytes()),
        'decompressed_result_bytes': len(raw), 'decompressed_result_sha256': sha(raw), 'native_tree_file_count': len(tree_inventory)})
    (ROOT / ('independent-' + mode + '-summary087.json')).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False))
