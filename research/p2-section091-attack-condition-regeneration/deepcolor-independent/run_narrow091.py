"""One frozen run per isolated mode:2 fresh public requests, counted formatting."""
import argparse
import copy
import functools
import json
from pathlib import Path
import sys
from review_common091 import canonical, decode, native, sha

OUT = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/p2-section091-deepcolor-regeneration-notes-author')
parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=('baseline', 'draft'))
mode = parser.parse_args().mode
target = OUT / f'narrow-{mode}091.json'
assert not target.exists(), 'Do not repeat or overwrite a public execution'
freeze = json.loads((OUT / 'narrow-preexecution-freeze091.json').read_text())
for row in freeze['files']:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
plan = json.loads((OUT / 'narrow-plan091.json').read_text())
author_public = json.loads((AUTHOR / f'public-{mode}.json').read_text())
tree = AUTHOR / (mode + '-tree')
def sources():
    return {p.relative_to(tree).as_posix(): sha(p.read_bytes()) for p in sorted(tree.rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json')}
before_sources = sources()
assert before_sources == author_public['source_before']
sys.dont_write_bytecode = True
sys.path.insert(0, str(tree))
import rouge.damage as damage
import rouge.reporting as reporting
import rouge.estimate as estimate
import rouge.catalog as catalog_module
assert Path(damage.__file__).resolve() == tree / 'rouge/damage.py'
counts = {'public_API_requests': 0, 'explicit_formatter_requests': 0,
          'estimate_function_entries': 0, 'report_function_entries': 0,
          'explicit_project_helper_requests': 0, 'tests': 0, 'Qt': 0, 'Wine': 0}
formatter_requests = []
original_report, original_estimate = reporting.format_report, estimate.format_estimate
def counted_report(*args, **kwargs):
    counts['report_function_entries'] += 1
    return original_report(*args, **kwargs)
def counted_estimate(*args, **kwargs):
    counts['estimate_function_entries'] += 1
    return original_estimate(*args, **kwargs)
reporting.format_report = counted_report
estimate.format_estimate = counted_estimate
cached_values = {}
cached_counts = {}
for name in ('catalog', 'operator_profiles'):
    original = getattr(catalog_module, name)
    def make_wrapper(original, name):
        @functools.wraps(original)
        def wrapper(*args, **kwargs):
            value = original(*args, **kwargs)
            cached_counts[name] = cached_counts.get(name, 0) + 1
            if name not in cached_values:
                cached_values[name] = {'value': value, 'first_native_sha256': sha(canonical(native(value)).encode())}
            return value
        return wrapper
    wrapped = make_wrapper(original, name)
    for module_name, module in list(sys.modules.items()):
        if module_name == 'rouge' or module_name.startswith('rouge.'):
            for attribute, value in list(vars(module).items()):
                if value is original:
                    setattr(module, attribute, wrapped)

receipt = {'status': 'RUNNING', 'mode': mode, 'source_before': before_sources,
           'counts': counts, 'fresh_records': [], 'saved_formatter_supplement': [],
           'formatter_requests': formatter_requests,
           'catalog_scope': 'Original cached helper first-return native hash versus post-call hash; raw native catalog tree is not separately archived. Forwarding wrappers return original value; no extra explicit helper call.'}
def save():
    target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
def catalog_checks():
    output = {}
    for name, item in cached_values.items():
        after = sha(canonical(native(item['value'])).encode())
        assert after == item['first_native_sha256'], name + ': cached public data mutated'
        output[name] = {'first_return_native_sha256': item['first_native_sha256'],
                        'after_native_sha256': after, 'observed_internal_entries': cached_counts[name]}
    return output
def texts(value, identity, modes):
    before = native(value)
    outputs = {}
    for presentation in modes:
        counts['explicit_formatter_requests'] += 1
        formatter_requests.append({'id': identity, 'mode': presentation})
        text = (estimate.format_estimate(value) if presentation == 'estimate'
                else reporting.format_report(value, technical=presentation == 'technical'))
        assert native(value) == before
        outputs[presentation] = text
        path = OUT / f'{mode}-{identity}-{presentation}.txt'
        with path.open('x') as handle: handle.write(text)
    return outputs

save()
for case in plan['cases']:
    assert all(canonical(case['input']) != canonical(old['input']) for old in author_public['records'])
    caller = copy.deepcopy(case['input']); caller_before = native(caller)
    record = {'id': case['id'], 'input': copy.deepcopy(caller), 'caller_native_before': caller_before}
    counts['public_API_requests'] += 1
    try:
        result = damage.calculate_damage(caller)
        record.update(status='returned', result_native=native(result), result_json=canonical(result), result=result)
        record['texts'] = texts(result, case['id'], ('estimate', 'default', 'technical'))
    except Exception as error:
        record.update(status='raised', exception={'type': type(error).__name__, 'message': str(error)})
    record['caller_native_after'] = native(caller)
    record['caller_preserved'] = record['caller_native_after'] == caller_before
    record['cached_catalog_profiles'] = catalog_checks()
    receipt['fresh_records'].append(record); receipt['source_after'] = sources(); save()
    assert record['status'] == 'returned', 'Stop after unexpected fresh failure; do not rerun'
    assert record['caller_preserved'] and receipt['source_after'] == before_sources
if mode == 'draft':
    for row in author_public['records']:
        value = decode(row['result_native'])
        assert canonical(value) == row['result_json']
        outputs = texts(value, 'saved-' + row['id'], ('estimate', 'technical'))
        assert outputs['estimate'] == row['formatted_text'], 'Estimate delegation differs from saved default'
        receipt['saved_formatter_supplement'].append({'id': row['id'], 'result_native_decode_exact': True,
            'result_native_preserved': native(value) == row['result_native'], 'texts': outputs,
            'historical_default_text_sha256': sha(row['formatted_text'].encode()),
            'cached_catalog_profiles': catalog_checks()})
        save()
receipt['source_after'] = sources()
assert receipt['source_after'] == before_sources
loaded = {}
for name, module in sys.modules.items():
    if name.startswith('rouge.') and getattr(module, '__file__', None):
        path = Path(module.__file__).resolve()
        assert path.is_relative_to(tree), 'Unexpected external project import: ' + str(path)
        loaded[name] = {'path': str(path), 'sha256': sha(path.read_bytes())}
receipt.update(status='NARROW_INDEPENDENT_EXECUTION_COMPLETE', source_unchanged=True,
               imported_project_modules=loaded, cached_catalog_profiles=catalog_checks())
save()
print(json.dumps({'mode': mode, 'status': receipt['status'], 'counts': counts,
                  'receipt_sha256': sha(target.read_bytes())}))
