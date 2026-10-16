"""Archive only exact public303 preparation originals; root reviews and runs it.

No cache scan, application import, test, window, Git operation or private-state
read is performed. Missing final READY inputs fail before any public write.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache'
BASE = ROOT / 'verification/sections/303-preparation'
TARGET = BASE / 'preparation-archive-manifest.json'
STANDARD_SUFFIXES = {'.json', '.md', '.py', '.txt', '.log', '.diff'}
MAX_MEMBER_BYTES = 250_000
BACKEND_HANDOFF_SHA = '542ae38af9f39788310cd4d2c0bdfc7e3a99f1714fe4bf9f59be7363589fe8d2'
PACK = 'research/p3-map-direct-ground-303/'

BACKEND_TOP = (
    'HANDOFF.json', 'prepare_fixed_inputs.py', 'finalize_sources.py',
    'finalize_handoff.py', 'run_first_author_tests.py',
    'fixed-input-copy-receipt.json', 'final-source-preparation-receipt.json',
    'finalize-sources.stdout.log', 'finalize-sources.stderr.log', 'finalize-sources.process.exit',
    'build-first.stdout.log', 'build-first.stderr.log', 'build-first.process.exit',
    'finalize-handoff.stdout.log', 'finalize-handoff.stderr.log', 'finalize-handoff.process.exit')
AUTHOR_FIRST = ('stdout.log', 'stderr.log', 'process.exit', 'process.json',
                'source-before.json', 'source-after.json',
                'extend_direct_landmark_303.py', 'test_direct_landmark_303.py')
SOURCE_RESEARCH = ('candidate-inventory.json', 'DECISION.md', 'inspect_candidates.py',
                   'prepare_reader_packet.py', 'prepare_logical_requests.py', 'prepare_all_requests.py',
                   'logical-reader-requests.json', 'READY.json', 'ALL_LOWLAND_READY.json')
PARENT_MEMBERS = ('historical294-candidate.json', 'historical048-candidate.json',
                  'tests/test_direct_landmark_294.py', 'tests/test_map_projection_048.py')
RUNTIME_MEMBERS = ('READY.json', 'verify_direct_map_window_303.py',
                   'run_section_303_window.py', 'run_section_303_necessary.py',
                   'NATIVE_PLAN.md', 'PREPARATION_NOTES.md',
                   'static-preparation.json', 'historical-local-public-bindings.json')
ROOT_PRODUCERS = ('begin_section_303.py', 'compare_readers_303.py',
                  'prepare_historical_map_tests_303.py', 'prepare_historical_048_candidate_303.py',
                  'prepare_historical_294_candidate_303.py', 'promote_map_backend_303.py',
                  'promote_historical_inputs_303.py', 'record_root_map_source_review_303.py',
                  'promote_native_303.py',
                  'launch_native_303.py',
                  'prepare_tools_303.py', 'prepare_publication_303.py', 'seal_tools_303.py', 'archive_preparation_303.py')
PUBLICATION_MEMBERS = ('READY.json', 'RUN_PLAN.md', 'BASELINE.json', 'stage_section_303.py',
                       'push_section_303.py', 'verify_publication_303.py', 'finish_publication_303.py')
CLOSEOUT_MEMBERS = ('READY.json', 'CONTRACT.md', 'close_section_303.py', 'static-preparation.json')
PRE_SEAL_MEMBERS = ('finish_publication_303.py', 'prepare_publication_303.py',
                    'push_section_303.py', 'seal_tools_303.py', 'stage_section_303.py',
                    'verify_publication_303.py', 'tool-result-summary.json')
SEAL_RUN_MEMBERS = ('prepare_publication_303.diff', 'seal_tools_303.diff', 'verify_publication_303.diff',
                    'revisions.json', 'process.json', 'stdout.log', 'stderr.log')
EXACT_NONSTANDARD_DESTINATIONS = {
    'author-backend/finalize-sources.process.exit',
    'author-backend/build-first.process.exit',
    'author-backend/finalize-handoff.process.exit',
    'author-backend/author-tests-first/process.exit',
}


def pin(raw):
    return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


def relative(value):
    if type(value) is not str:
        raise ValueError('Exact public artifact path must be text.')
    pure = PurePosixPath(value)
    if (not pure.parts or pure.is_absolute() or '..' in pure.parts or '\\' in value or ':' in value):
        raise ValueError('Unsafe exact relative artifact path: ' + value)
    return pure


def regular(value, cache_only):
    pure = relative(value)
    # Reject forbidden input before stat/read/hash. The root comparison already
    # has its own exact public counterpart; no root cache directory is needed.
    if (value.startswith('.cache/p3-303-root/') or any(part in ('.local', '.private', '.git') for part in pure.parts)
            or 'baseline-local-only' in value):
        raise ValueError('Private/root-local inputs are forbidden: ' + value)
    path = ROOT.joinpath(*pure.parts)
    limit = CACHE if cache_only else ROOT
    if (not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(limit.resolve())
            or any(parent.is_symlink() for parent in path.parents if parent.is_relative_to(limit))):
        raise ValueError('Expected exact regular public source: ' + value)
    if not cache_only and '.cache' in pure.parts:
        raise ValueError('A public reference cannot point into cache.')
    return path


def load_cache(value):
    return json.loads(regular(value, True).read_bytes())


def expect(raw, expected, name):
    if type(expected) is not dict or pin(raw) != {key: expected[key] for key in ('sha256', 'bytes')}:
        raise ValueError('Frozen source changed: ' + name)


def make_plan():
    """Preflight all exact inputs/destinations before the first archive write."""
    members, references, aliases = {}, {}, []

    def add(source, destination, expected=None, role='public_preparation_not_product_acceptance'):
        path = regular(source, True)
        raw = path.read_bytes()
        if len(raw) > MAX_MEMBER_BYTES:
            raise ValueError('Never duplicate large original tables, clones or source-before trees: ' + source)
        if expected is not None:
            expect(raw, expected, source)
        destination = str(relative(destination))
        if destination in members:
            raise ValueError('Duplicate archive destination: ' + destination)
        if Path(destination).suffix not in STANDARD_SUFFIXES and destination not in EXACT_NONSTANDARD_DESTINATIONS:
            raise ValueError('Nonstandard member needs its own exact path whitelist: ' + destination)
        members[destination] = {'source': source, 'role': role, 'raw': raw, **pin(raw)}

    def reference(name, expected, role):
        path = regular(name, False)
        expect(path.read_bytes(), expected, name)
        value = {**{key: expected[key] for key in ('sha256', 'bytes')}, 'role': role}
        if name in references and references[name] != value:
            # Same exact immutable bytes may have several historical roles.
            if {k: references[name][k] for k in ('sha256', 'bytes')} != {k: value[k] for k in ('sha256', 'bytes')}:
                raise ValueError('Conflicting public reference pin: ' + name)
            return
        references[name] = value

    backend_prefix = '.cache/p3-303-backend/'
    backend_raw = regular(backend_prefix + 'HANDOFF.json', True).read_bytes()
    if pin(backend_raw)['sha256'] != BACKEND_HANDOFF_SHA:
        raise ValueError('Exact final backend HANDOFF changed.')
    backend = json.loads(backend_raw)
    if (backend['section'] != 303 or backend['status'] != 'CACHE_CANDIDATE_READY_NOT_PROMOTED_OR_PRODUCT_ACCEPTED'
            or len(backend['promotion_files']) != 16 or backend['old_tests_modified_here'] is not False):
        raise ValueError('Wrong303 backend preparation scope.')
    for name in BACKEND_TOP:
        add(backend_prefix + name, 'author-backend/' + name)
    for name in AUTHOR_FIRST:
        add(backend_prefix + 'author-tests-first/' + name, 'author-backend/author-tests-first/' + name,
            role='first_actual16_author_methods_not_additional_formal_acceptance')
    first = load_cache(backend_prefix + 'author-tests-first/process.json')
    expect(regular(backend_prefix + 'author-tests-first/process.json', True).read_bytes(),
           backend['actual_first_author_checks']['process_pin'], 'first actual author process')
    before = load_cache(backend_prefix + 'author-tests-first/source-before.json')
    after = load_cache(backend_prefix + 'author-tests-first/source-after.json')
    expected_first_sources = {backend['candidate_root'] + '/' + name for name in backend['promotion_files']
                              if name in ('rouge/data/fixed-landmark-references.json',
                                          'scripts/extend_direct_landmark_303.py', 'tests/test_direct_landmark_303.py')}
    source_manifest_path = PACK + 'source-manifest.json'
    source_manifest = json.loads(regular(source_manifest_path, False).read_bytes())
    expected_first_sources |= {backend['candidate_root'] + '/' + name for name in source_manifest['files']}
    expected_first_sources.add(backend['candidate_root'] + '/' + source_manifest_path)
    expected_first_sources |= {'rouge/fixed_landmark_mapping.py', 'rouge/map_projection.py', 'scripts/extend_direct_landmark_294.py'}
    if (set(before) != expected_first_sources or before != after or len(before) != 25
            or first['source_count'] != len(before)
            or first['source_before_after_equal'] is not True or first['actual_exit'] != 0):
        raise ValueError('Original25-public-source author run ledger changed or contains an unexpected source.')
    expected_first_values = {backend['candidate_root'] + '/' + name: value
                             for name, value in source_manifest['files'].items()}
    for name in ('rouge/data/fixed-landmark-references.json', 'scripts/extend_direct_landmark_303.py',
                 'tests/test_direct_landmark_303.py', source_manifest_path):
        expected_first_values[backend['candidate_root'] + '/' + name] = backend['promotion_files'][name]
    for name in ('rouge/fixed_landmark_mapping.py', 'rouge/map_projection.py', 'scripts/extend_direct_landmark_294.py'):
        expected_first_values[name] = pin(regular(name, False).read_bytes())
    if before != expected_first_values:
        raise ValueError('Original first25 hash/size values must equal the unchanged exact public sources.')
    for code in ('scripts/extend_direct_landmark_303.py', 'tests/test_direct_landmark_303.py'):
        name = Path(code).name
        expect(regular(backend_prefix + 'author-tests-first/' + name, True).read_bytes(), backend['promotion_files'][code], name)
    for name, expected in backend['promotion_files'].items():
        reference(name, expected, 'exact_promoted303_function_source_not_duplicated')
    for name, expected in source_manifest['files'].items():
        reference(name, expected, 'original_source_authority_already_public_not_duplicated')
    # Original first build outputs already have exact public counterparts.
    for cache_name, public_name in (
            ('build-first/build-receipt.json', PACK + 'build-receipt.json'),
            ('build-first/fixed-landmark-references.json', 'rouge/data/fixed-landmark-references.json')):
        raw = regular(backend_prefix + cache_name, True).read_bytes()
        if raw != regular(public_name, False).read_bytes():
            raise ValueError('Public303 original differs from the actual first build output.')
        aliases.append({'historical_cache_path': backend_prefix + cache_name, 'public_path': public_name, **pin(raw)})
    for name in SOURCE_RESEARCH:
        add('.cache/p3-303-map-candidates/' + name, 'candidate-source-research/' + name,
            role='logical_scope_research_initial24_then_all89_before_pixel_readings_not_failure')
    for cache_name, public_name in (
            ('logical-reader-requests-all.json', PACK + 'REQUEST_MANIFEST.json'),
            ('logical-reader-requests-all-lowland.json', PACK + 'REQUEST_MANIFEST.json'),
            ('reader-grid-ro6_b_6.json', PACK + 'reader-grid-ro6_b_6.json'),
            ('reader-grid-ro6_n_2_3.json', PACK + 'reader-grid-ro6_n_2_3.json')):
        raw = regular('.cache/p3-303-map-candidates/' + cache_name, True).read_bytes()
        if raw != regular(public_name, False).read_bytes():
            raise ValueError('Original logical packet changed relative to its exact public source.')
        aliases.append({'historical_cache_path': '.cache/p3-303-map-candidates/' + cache_name,
                        'public_path': public_name, **pin(raw)})
    # Raw A/B and READY are already in the public source pack: no reader cache
    # directory is scanned or copied, and no original reader is asked to revise.
    for name in ('READER_A_ORIGINAL.json', 'READER_B_ORIGINAL.json',
                 'READER_A_READY_ORIGINAL.json', 'READER_B_READY_ORIGINAL.json'):
        if PACK + name not in references:
            raise ValueError('Frozen reader originals must already have exact public references.')

    for name in ('analysis.json', 'FINDINGS.md'):
        add('.cache/p3-303-runtime-analysis/' + name, 'runtime-readonly-analysis/' + name,
            role='static_compatibility_findings_not_actual_test_failure_or_pass')
    for name in PARENT_MEMBERS:
        add('.cache/p3-303-parent/' + name, 'historical-test-candidates/' + name,
            role='exact_limited_history_fixture_or_assertion_maintenance_candidate')

    native_prefix = '.cache/p3-303-native-window/'
    native_raw = regular(native_prefix + 'READY.json', True).read_bytes()
    if sha256(native_raw).hexdigest() != '5f7efd45d47bea9d8fba086a38d7377b0869fbfd665b4f2761898b231bd2a049':
        raise ValueError('Exact final native preparation READY changed.')
    native = json.loads(native_raw)
    if (native['section'] != 303 or native['kind'] != 'SECTION303_CACHE_NATIVE_OWNED_AND_NECESSARY_READY_NOT_EXECUTED'
            or set(native['pins']) != set(RUNTIME_MEMBERS) - {'READY.json'}
            or native['functional_promotion_source_files'] != {
                **backend['promotion_files'],
                'scripts/verify_direct_map_window_303.py': native['pins']['verify_direct_map_window_303.py']}):
        raise ValueError('Final native preparation READY must be section303.')
    for name in RUNTIME_MEMBERS:
        add(native_prefix + name, 'runtime-preparation/' + name,
            native['pins'].get(name),
            role='runner_or_native_preparation_not_actual_native_acceptance')
    reference(native['canonical'], native['pins']['verify_direct_map_window_303.py'],
              'same_root_promoted_native_source_not_additional_execution')

    for name in ROOT_PRODUCERS:
        add('.cache/' + name, 'root-producers/' + name, role='root_producer_source_no_private_baseline_read')
    close_prefix = '.cache/p3-303-closeout/'
    close_raw = regular(close_prefix + 'READY.json', True).read_bytes()
    if sha256(close_raw).hexdigest() != '68d2649fa8dbdfca2a95dd4a94d23a3e3479662348e52378679df5793e419964':
        raise ValueError('Exact final closeout preparation READY changed.')
    close = json.loads(close_raw)
    if (close['section'] != 303 or close['kind'] != 'SECTION303_CLOSEOUT_READY_CACHE_PREPARATION_ONLY'
            or set(close['files']) != set(CLOSEOUT_MEMBERS) - {'READY.json'}):
        raise ValueError('Wrong303 closeout preparation scope.')
    for reference_key in ('backend_HANDOFF', 'native_READY'):
        ref = close[reference_key]
        expect(regular(ref['path'], True).read_bytes(), ref, reference_key)
    for name in CLOSEOUT_MEMBERS:
        add(close_prefix + name, 'closeout-preparation/' + name, close['files'].get(name))
    publication_prefix = '.cache/p3-303-publication-prep/'
    publication_raw = regular(publication_prefix + 'READY.json', True).read_bytes()
    if sha256(publication_raw).hexdigest() != '497b14b1d9606f545d2ab92c97b2ba1d4ae1792253278527d5e877aa6dcd6e69':
        raise ValueError('Exact final publication preparation READY changed.')
    publication = json.loads(publication_raw)
    required_publication_pins = set(PUBLICATION_MEMBERS) - {'READY.json'}
    required_publication_pins |= {'stage_section_303.py.txt', 'verify_publication_303.py.txt'}
    if (publication['section'] != 303 or publication['kind'] != 'SECTION303_PUBLICATION_READY_CACHE_PREPARATION_ONLY'
            or set(publication['files']) != required_publication_pins):
        raise ValueError('Wrong303 publication preparation scope.')
    expect(close_raw, publication['closeout_READY'], 'publication closeout reference')
    for name in required_publication_pins:
        expect(regular(publication_prefix + name, True).read_bytes(), publication['files'][name], name)
    for name in PUBLICATION_MEMBERS:
        add(publication_prefix + name, 'publication-preparation/' + name, publication['files'].get(name))
    # Keep the actual preparation failure summary as a summary; no missing raw
    # stdout/stderr is reenacted. The metadata anchor correction was unexecuted.
    summary = load_cache(close_prefix + 'pre-seal-original/tool-result-summary.json')
    if (summary['kind'] != 'PREPARATION_TOOL_ACTUAL_FAILURE_TOOL_RESULT_SUMMARY_NOT_RAW_CAPTURE'
            or summary['actual_exit_code'] != 1 or summary['publication_tool_execution'] is not False
            or set(summary['files']) != set(PRE_SEAL_MEMBERS) - {'tool-result-summary.json'}):
        raise ValueError('Original static sealing tool failure summary changed.')
    for name in PRE_SEAL_MEMBERS:
        add(close_prefix + 'pre-seal-original/' + name, 'closeout-preparation/pre-seal-original/' + name,
            summary['files'].get(name), role='preparation_original_or_honest_tool_summary_not_product_failure')
    revisions = load_cache(close_prefix + 'seal-final-run/revisions.json')
    for name, row in revisions['changes'].items():
        original_name = Path(name).name
        if (original_name not in summary['files'] or summary['files'][original_name]['sha256'] != row['before_sha256']
                or pin(regular(name, True).read_bytes())['sha256'] != row['after_sha256']):
            raise ValueError('Exact original-to-final preparation revision changed.')
    seal_process = load_cache(close_prefix + 'seal-final-run/process.json')
    if (seal_process['kind'] != 'ACTUAL_STATIC_PREPARATION_TOOL_RUN_NOT_PRODUCT_ACCEPTANCE'
            or seal_process['exit_code'] != 0 or seal_process['producer_Qt_tests_Git_executed'] is not False):
        raise ValueError('Final static preparation run is not actual0/static-only.')
    for stream in ('stdout', 'stderr'):
        if sha256(regular(close_prefix + 'seal-final-run/' + stream + '.log', True).read_bytes()).hexdigest() != seal_process[stream + '_sha256']:
            raise ValueError('Actual final static preparation raw output changed.')
    for name in SEAL_RUN_MEMBERS:
        add(close_prefix + 'seal-final-run/' + name, 'closeout-preparation/seal-final-run/' + name,
            role='actual_static_preparation_source_revision_and_raw_process_not_acceptance')
    root_comparison = 'verification/sections/303-preparation/root-independent-reading-comparison.json'
    reference(root_comparison, {'sha256': '28e1f1953607bbff06331bea28674ebab86e3e09f79e07f1080cafdfc4f14683', 'bytes': 30404},
              'independent_root89_comparison_already_public_not_a_data_source')
    return members, references, aliases


def main():
    if (BASE.is_symlink() or not BASE.resolve().is_relative_to(ROOT.resolve())
            or any(parent.is_symlink() for parent in BASE.parents if parent.is_relative_to(ROOT))):
        raise ValueError('Archive output must remain in the regular public workspace.')
    if TARGET.exists() or TARGET.is_symlink():
        raise FileExistsError('Preserve existing sealed preparation archive; never overwrite.')
    members, references, aliases = make_plan()
    for name, row in members.items():
        target = BASE.joinpath(*relative(name).parts)
        if (not target.resolve().is_relative_to(BASE.resolve()) or target.is_symlink()
                or any(parent.is_symlink() for parent in target.parents if parent.is_relative_to(BASE))):
            raise ValueError('Unsafe exact archive target.')
        if target.exists() and (not target.is_file() or target.read_bytes() != row['raw']):
            raise FileExistsError('Never overwrite a different prior public original: ' + name)
    for name, row in members.items():
        target = BASE.joinpath(*relative(name).parts)
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(row['raw'])
        if pin(target.read_bytes()) != {key: row[key] for key in ('sha256', 'bytes')}:
            raise ValueError('Archive bytes differ from the actual source: ' + name)
    files = {name: {key: row[key] for key in ('sha256', 'bytes', 'source', 'role')}
             for name, row in sorted(members.items())}
    unusual = {name: {key: row[key] for key in ('sha256', 'bytes')} for name, row in files.items()
               if Path(name).suffix not in STANDARD_SUFFIXES}
    if set(unusual) != EXACT_NONSTANDARD_DESTINATIONS:
        raise ValueError('All and only four real process.exit files must be explicitly whitelisted.')
    record = {'section': 303, 'kind': 'PUBLIC_PREPARATION_ARCHIVE_NOT_ADDITIONAL_ACCEPTANCE',
              'created_at': datetime.now(timezone.utc).isoformat(), 'files': files,
              'exact_member_count': len(files), 'nonstandard_exact_members': unusual,
              'public_source_references_not_copied': references, 'exact_cache_aliases_not_copied': aliases,
              'private_state_or_private_hash_lists_read_or_copied': False,
              'root_private_baseline_input_forbidden_before_read': True,
              'full_original_tables_level_images_or_source_before_trees_copied': False,
              'first_actual16_author_methods_not_added_to_formal_pass_count': True,
              'two_reader_observations_are_not_additional_test_methods': True,
              'runtime_statistical_print_error_is_only_original_fact_summary_not_raw_process_log': True,
              'static_sealing_failure_original_sources_and_summary_preserved_without_fabricated_raw_log': True,
              'metadata_document_anchor_correction_unexecuted_before_ready': True,
              'initial24_to_all89_scope_expansion_not_a_failed_observation': True,
              'actual_formal_necessary_native_main_visual_receipts_not_in_this_archive': True,
              'whole_map_gaps_unchanged': [81, 59]}
    BASE.mkdir(parents=True, exist_ok=True)
    with TARGET.open('xb') as stream:
        stream.write((json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8'))
    print(json.dumps({'manifest': str(TARGET), **pin(TARGET.read_bytes()), 'files': len(files),
                      'source_bytes_copied': sum(row['bytes'] for row in files.values()),
                      'nonstandard_exact_members': unusual}, ensure_ascii=False))


if __name__ == '__main__':
    main()
