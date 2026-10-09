"""Actual frozen candidate mutation checks; original product files remain frozen."""
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


BASE = Path(__file__).resolve().parent
OUT = BASE / 'author-verification095'
sys.path.insert(0, str(BASE / 'candidate'))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.module_source_reference import _reference_data
from rouge.reporting import format_report

spec = importlib.util.spec_from_file_location('mutation095_native_codec', BASE / 'author-matrix-worker095.py')
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)


def mutable_ids(value):
    result = set()
    def walk(item):
        if type(item) not in (dict, list):
            return
        if id(item) in result:
            return
        result.add(id(item))
        for child in item.values() if type(item) is dict else item:
            walk(child)
    walk(value)
    return result


def graph_hash(value):
    return hashlib.sha256(json.dumps(codec.native_graph(value), ensure_ascii=False).encode()).hexdigest()


def replace_scalar_leaves(value):
    """Mutate every curated nested value while retaining keys and list layout."""
    if type(value) is dict:
        for key in value:
            value[key] = replace_scalar_leaves(value[key])
        return value
    if type(value) is list:
        value[:] = [replace_scalar_leaves(child) for child in value]
        return value
    if value is None:
        return 'probe-null-leaf'
    if type(value) is bool:
        return not value
    if type(value) in (int, float):
        return value + 999
    if type(value) is str:
        return value + '/MUTATION-PROBE'
    raise TypeError(type(value).__name__)


def main():
    records = OUT / 'mutation-isolation095-records.json.gz'
    receipt_path = OUT / 'mutation-isolation095.json'
    assert not records.exists() and not receipt_path.exists()
    manifest = json.loads((BASE / 'public-code-artifacts-manifest095.json').read_text())
    for row in manifest['files']:
        assert hashlib.sha256(Path(row['source_path']).read_bytes()).hexdigest() == row['sha256']
    rows, calls = [], Counter()
    def profile(frame, event, argument):
        if event == 'call' and frame.f_globals.get('__name__', '').startswith('rouge.'):
            calls[frame.f_globals['__name__'] + '.' + frame.f_code.co_name] += 1
    sys.setprofile(profile)
    cache = _reference_data()
    initial_catalog = graph_hash(catalog())
    initial_cache = graph_hash(cache)
    cases = [('char_151_myrtle', 'uniequip_002_myrtle'),
        ('mechanist', 'uniequip_002_mcnist'), ('char_133_mm', 'uniequip_002_mm'),
        ('char_328_cammou', 'uniequip_002_cammou'), ('char_1038_whitw2', 'uniequip_002_whitw2'),
        ('char_206_gnosis', 'uniequip_004_gnosis'), ('char_437_mizuki', 'uniequip_003_mizuki'),
        ('char_4202_haruka', 'uniequip_002_haruka'), ('char_110_deepcl', 'uniequip_002_deepcl'),
        ('char_2027_wang', 'uniequip_002_wang'), ('char_1001_amiya2', 'uniequip_002_amiya2'),
        ('char_1037_amiya3', 'uniequip_002_amiya3')]
    try:
        for operator, module in cases:
            caller = {'operator': operator, 'skill': 1, 'module_id': module, 'module_level': 3,
                'unconfirmed_training': ['等级'], 'effects': [{'kind': 'attack_pct', 'value': .2}]}
            before = codec.native_graph(caller)
            first = calculate_damage(caller)
            original_native = codec.native_graph(first)
            original_texts = {'normal': format_report(first), 'technical': format_report(first, technical=True),
                'structured': json.dumps({'scenario': caller, 'result': first}, ensure_ascii=False, indent=2)}
            reference = first['report'].pop('selected_module_source_reference')
            existing_native_before = codec.native_graph(first)
            ref_ids = mutable_ids(reference)
            # Check actual live object identities, not identities of copied results.
            assert not ref_ids & mutable_ids(first), 'new source aliases a live old result object'
            assert not ref_ids & mutable_ids(caller), 'new source aliases caller objects'
            assert not ref_ids & mutable_ids(catalog()), 'new source aliases cached catalog objects'
            assert not ref_ids & mutable_ids(cache), 'new source aliases supplemental source cache'
            first['report']['selected_module_source_reference'] = reference
            assert codec.native_graph(first) == original_native
            replace_scalar_leaves(reference)
            mutated_native = codec.native_graph(first)
            first['report'].pop('selected_module_source_reference')
            assert codec.native_graph(first) == existing_native_before
            first['report']['selected_module_source_reference'] = reference
            assert graph_hash(catalog()) == initial_catalog
            assert graph_hash(cache) == initial_cache
            assert codec.native_graph(caller) == before
            fresh = calculate_damage(caller)
            assert codec.native_graph(fresh) == original_native
            fresh_texts = {'normal': format_report(fresh), 'technical': format_report(fresh, technical=True),
                'structured': json.dumps({'scenario': caller, 'result': fresh}, ensure_ascii=False, indent=2)}
            assert fresh_texts == original_texts
            assert not mutable_ids(fresh['report']['selected_module_source_reference']) & ref_ids
            stage_one_caller = {**deepcopy(caller), 'module_level': 1}
            stage_one = calculate_damage(stage_one_caller)
            assert stage_one['report']['selected_module_source_reference']['raw_phase']['equipLevel'] == 1
            assert not mutable_ids(stage_one['report']['selected_module_source_reference']) & ref_ids
            assert codec.native_graph(caller) == before
            rows.append({'operator': operator, 'module_id': module, 'caller_before': before,
                'caller_after': codec.native_graph(caller), 'original_native': original_native,
                'original_three_texts': original_texts, 'mutated_source_only_native': mutated_native,
                'old_native_after_mutation': existing_native_before,
                'fresh_native': codec.native_graph(fresh), 'fresh_three_texts': fresh_texts,
                'stage_one_native': codec.native_graph(stage_one),
                'actual_live_mutable_id_intersections': {'old_result': 0, 'caller': 0, 'catalog': 0,
                    'source_cache': 0, 'fresh_reference': 0, 'stage_one_reference': 0},
                'catalog_native_graph_hash_after': graph_hash(catalog()),
                'source_cache_native_graph_hash_after': graph_hash(cache)})
    finally:
        sys.setprofile(None)
    assert calls['rouge.damage.calculate_damage'] == 36
    for row in manifest['files']:
        assert hashlib.sha256(Path(row['source_path']).read_bytes()).hexdigest() == row['sha256']
    with gzip.open(records, 'wt', encoding='utf-8', compresslevel=6) as stream:
        json.dump({'schema': 'actual-candidate-nested-mutation-isolation095', 'rows': rows}, stream, ensure_ascii=False)
    receipt = {'format_version': 1, 'status': 'PASS_ACTUAL_NESTED_MUTATION_ISOLATION095', 'passed': True,
        'completed_section_increment': 0, 'operator_module_contexts': 12,
        'actual_API_entries': 36, 'actual_three_text_requests': 72,
        'actual_project_calls': dict(calls), 'caller_unchanged': True,
        'live_mutable_intersections_all_zero': True, 'catalog_cache_unchanged': True,
        'full_old_native_unchanged_after_new_reference_mutation': True,
        'full_fresh_native_and_three_texts_exact': True,
        'source_product_five_payloads_unchanged': True,
        'catalog_native_graph_hash_before': initial_catalog, 'source_cache_native_graph_hash_before': initial_cache,
        'records': str(records), 'records_bytes': records.stat().st_size,
        'records_sha256': hashlib.sha256(records.read_bytes()).hexdigest(),
        'scope': 'Actual frozen candidate Linux, 12 specialized/patch/token contexts; no UI/Wine/network/private state. All scalar leaves in the report-owned reference mutated; actual live identities checked against untouched original result/caller/cache/catalog and fresh/stage-one results.'}
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ('status', 'passed', 'operator_module_contexts', 'actual_API_entries',
        'actual_three_text_requests', 'records_bytes', 'records_sha256')}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
