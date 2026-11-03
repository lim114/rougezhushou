"""Archive exact public302 preparation members; root executes after reviewing READY."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache'
BASE = ROOT / 'verification/sections/302-preparation'
TARGET = BASE / 'preparation-archive-manifest.json'
STANDARD_SUFFIXES = {'.json', '.md', '.py', '.txt', '.log', '.png', '.html', '.diff'}
MAX_MEMBER_BYTES = 2_000_000

BACKEND_TOP = (
    'HANDOFF.json', 'HANDOFF_FINAL.json', 'SCOPE_CANDIDATE.json',
    'prepare_sources.py', 'run_author.py', 'preserve_first_backend.py', 'seal_backend.py',
    'correct_handoff_parent.py', 'first-test-premise-correction.json', 'first-test-premise-correction.diff')
BACKEND_RUNS = ('source-build-first', 'backend-first', 'backend-corrected')
BACKEND_LOGS = ('process.exit', 'process.json', 'stdout.txt', 'stderr.txt')
BACKEND_CODE = ('rouge/ritual_weakening.py', 'scripts/build_ritual_weakening_302.py',
                'tests/test_ritual_weakening_302.py')
VIEW_TOP = ('HANDOFF.json', 'README.md', 'PREPARATION_ERRORS.md', 'prepare_runner.py',
            'run_direct_dialog_checks.py', 'write_handoff.py')
VIEW_RUNS = ('first-real-direct-dialog', 'corrected-direct-dialog')
VIEW_LOGS = ('actual-result.json', 'process.json', 'child.py', 'runner.py', 'stdout', 'stderr')
VIEW_SNAPSHOTS = ('rouge/ritual_weakening.py', 'rouge/ritual_weakening_view.py',
                  'tests/test_ritual_weakening_view_302.py')
NATIVE_MEMBERS = ('READY.json', 'verify_ritual_weakening_window_302.py',
                  'run_section_302_window.py', 'run_section_302_necessary.py',
                  'NATIVE_PLAN.md', 'PREPARATION_NOTES.md', 'static-preparation.json')
PARENT_MEMBERS = ('parent-patch.json', 'initial-parent-preparation-failure.json',
                  'rouge/node_catalog_view.py', 'tests/test_ritual_weakening_integration_302.py')
ROOT_PRODUCERS = ('begin_section_302.py', 'prepare_parent_302.py', 'promote_section_302.py',
                  'archive_preparation_302.py')


def pin(raw):
    return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


def relative(value):
    if type(value) is not str:
        raise ValueError('Archive member path must be text.')
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or '..' in path.parts or '\\' in value or ':' in value:
        raise ValueError('Unsafe archive member path: ' + value)
    return path


def source_file(value):
    path = ROOT.joinpath(*relative(value).parts)
    if (not path.is_file() or path.is_symlink()
            or not path.resolve().is_relative_to(CACHE.resolve())):
        raise ValueError('Expected regular cache-only public source: ' + value)
    if any(parent.is_symlink() for parent in path.parents if parent.is_relative_to(CACHE)):
        raise ValueError('Symlink source ancestry is not allowed.')
    return path


def load_source(value):
    return json.loads(source_file(value).read_bytes())


def expect(raw, expected, description):
    if type(expected) is not dict or pin(raw) != {k: expected[k] for k in ('sha256', 'bytes')}:
        raise ValueError('Changed frozen public source: ' + description)


def make_plan():
    """Preflight all exact members before writing the first archive file."""
    members = {}
    def add(source, destination, expected=None, role='public_preparation'):
        path = source_file(source)
        raw = path.read_bytes()
        if len(raw) > MAX_MEMBER_BYTES:
            raise ValueError('Oversized member; never copy full game table or dependency clone: ' + source)
        if expected is not None:
            expect(raw, expected, source)
        destination = str(relative(destination))
        if destination in members:
            raise ValueError('Duplicate archive destination: ' + destination)
        members[destination] = {'source': source, 'role': role, 'raw': raw, **pin(raw)}

    backend_prefix = '.cache/p3-302-backend/'
    backend = load_source(backend_prefix + 'HANDOFF_FINAL.json')
    if backend['kind'] != 'SECTION302_CACHE_BACKEND_READY_NOT_FORMAL_PRODUCT_ACCEPTANCE':
        raise ValueError('Backend is not the frozen302 preparation handoff.')
    for name in BACKEND_TOP:
        add(backend_prefix + name, 'author-backend/' + name)
    for folder in BACKEND_RUNS:
        for name in BACKEND_LOGS:
            add(backend_prefix + folder + '/' + name, 'author-backend/' + folder + '/' + name,
                role='actual_author_raw_process_not_formal_acceptance')
    first_sources = load_source(backend_prefix + 'backend-first/source/source-manifest.json')
    if set(first_sources['files']) != set(backend['promotion_files']):
        raise ValueError('Exact original backend source scope changed.')
    add(backend_prefix + 'backend-first/source/source-manifest.json',
        'author-backend/backend-first/source/source-manifest.json')
    for name, expected in first_sources['files'].items():
        add(backend_prefix + 'backend-first/source/' + name,
            'author-backend/backend-first/source/' + name, expected,
            role='exact_first24_F1_source_before_test_premise_correction')
    for name in BACKEND_CODE:
        add(backend_prefix + 'candidate/' + name, 'author-backend/final-candidate/' + name,
            backend['promotion_files'][name], role='final_author_code_not_formal_acceptance')

    view_prefix = '.cache/p3-302-view/'
    view = load_source(view_prefix + 'HANDOFF.json')
    if view['kind'] != 'SECTION302_VIEW_CACHE_READY_NOT_FORMAL_PRODUCT_OR_NATIVE_ACCEPTANCE':
        raise ValueError('View is not the frozen302 preparation handoff.')
    for name in VIEW_TOP:
        expected = view['owned_files'].get(name) if name != 'HANDOFF.json' else None
        add(view_prefix + name, 'author-view/' + name, expected)
    for folder in VIEW_RUNS:
        for name in VIEW_LOGS:
            member = folder + '/' + name
            add(view_prefix + member, 'author-view/' + member, view['owned_files'][member],
                role='actual_author_raw_process_not_formal_acceptance')
        for name in VIEW_SNAPSHOTS:
            member = folder + '/source-before/' + name
            add(view_prefix + member, 'author-view/' + member, view['owned_files'][member],
                role='exact_first_or_corrected_author_source')
    for name, expected in view['promote_files'].items():
        add(view_prefix + 'candidate/' + name, 'author-view/final-candidate/' + name,
            expected, role='final_author_code_not_formal_acceptance')

    native_prefix = '.cache/p3-302-native-window/'
    native = load_source(native_prefix + 'READY.json')
    if native['section'] != 302 or set(native['pins']) != set(NATIVE_MEMBERS) - {'READY.json'}:
        raise ValueError('Native preparation READY scope changed; review before archiving.')
    for ref in ('backend_HANDOFF', 'view_HANDOFF', 'parent_candidate', 'root_integration_candidate'):
        expected = native[ref]
        expect(source_file(expected['path']).read_bytes(), expected, expected['path'])
    for name in NATIVE_MEMBERS:
        add(native_prefix + name, 'runtime-preparation/' + name,
            native['pins'].get(name), role='unexecuted_native_or_runner_preparation')
    for name in PARENT_MEMBERS:
        add('.cache/p3-302-parent/' + name, 'root-parent/' + name,
            role='parent_preparation_tool_summary_is_not_raw_failure_log')
    for name in ROOT_PRODUCERS:
        add('.cache/' + name, 'root-producers/' + name, role='root_producer_source')

    # These original public sources already exist in301. Only verify/reference them.
    references = dict(backend['prior_research_actual_failure_and_source_history'])
    prior_base = 'verification/sections/301-preparation/future-notes-and-ritual-research/'
    prior_ready = json.loads((ROOT / (prior_base + 'READY.json')).read_bytes())
    for name, expected in prior_ready['owned_files'].items():
        name = str(relative(name))
        reference_name = prior_base + name
        if reference_name in references and references[reference_name] != expected:
            raise ValueError('Conflicting prior research reference pin.')
        references[reference_name] = expected
    for name, expected in references.items():
        path = ROOT.joinpath(*relative(name).parts)
        if (not name.startswith('verification/sections/301-preparation/future-notes-and-ritual-research/')
                or not path.is_file() or path.is_symlink()):
            raise ValueError('Prior public301 reference missing or out of scope.')
        expect(path.read_bytes(), expected, name)
    return members, references


def main():
    if (BASE.is_symlink() or not BASE.resolve().is_relative_to(ROOT.resolve())
            or any(p.is_symlink() for p in BASE.parents if p.is_relative_to(ROOT))):
        raise ValueError('Public archive base must stay in the regular workspace tree.')
    if TARGET.exists() or TARGET.is_symlink():
        raise FileExistsError('Preserve existing archive manifest; do not overwrite.')
    members, references = make_plan()
    # Check every target before copying anything. Never include other BASE receipts.
    for name, row in members.items():
        path = BASE.joinpath(*relative(name).parts)
        if (not path.resolve().is_relative_to(BASE.resolve()) or path.is_symlink()
                or any(p.is_symlink() for p in path.parents if p.is_relative_to(BASE))):
            raise ValueError('Unsafe public archive destination.')
        if path.exists() and (not path.is_file() or path.read_bytes() != row['raw']):
            raise FileExistsError('Refuse to overwrite a different prior artifact: ' + name)
    for name, row in members.items():
        path = BASE.joinpath(*relative(name).parts)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(row['raw'])
        if pin(path.read_bytes()) != {k: row[k] for k in ('sha256', 'bytes')}:
            raise ValueError('Archive copy did not match original bytes: ' + name)
    files = {name: {k: row[k] for k in ('sha256', 'bytes', 'source', 'role')}
             for name, row in sorted(members.items())}
    nonstandard = [name for name in files if Path(name).suffix not in STANDARD_SUFFIXES]
    record = {'section': 302, 'kind': 'PUBLIC_PREPARATION_ARCHIVE_NOT_ADDITIONAL_ACCEPTANCE',
        'created_at': datetime.now(timezone.utc).isoformat(), 'files': files,
        'exact_member_count': len(files), 'nonstandard_exact_members': nonstandard,
        'prior301_research_references_not_copied': references,
        'private_state_or_private_hash_lists_copied': False,
        'full17MB_or_existing_dependency_source_before_copies_included': False,
        'full_source_hash_references_preserved_in_actual_process_receipts': True,
        'first_backend24_F1_and_view12_F5_preserved': True,
        'author_corrected24_and_view13_not_added_to_formal_pass_counts': True,
        'formal_necessary_and_native_receipts_not_in_this_archive': True,
        'parent_initial_failure_is_tool_summary_not_raw_subprocess_log': True}
    BASE.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'manifest': str(TARGET), 'sha256': pin(TARGET.read_bytes())['sha256'],
                      'files': len(files), 'bytes': sum(row['bytes'] for row in files.values()),
                      'nonstandard_exact_members': nonstandard}, ensure_ascii=False))


if __name__ == '__main__':
    main()
