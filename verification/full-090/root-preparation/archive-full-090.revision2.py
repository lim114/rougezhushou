"""Root-only full090 archival; author prepares this script without executing it.

Run only after finished full_context090 and the exact UI/public packet are sealed.
The spec supplies final UI expectations and explicit public inputs. No runtime
glob, project import, test, API, GUI, Wine process, or source rewrite is performed.
An existing destination or a dirty index/worktree is a hard stop, including a
partially failed previous archive. Preserve diagnostics and diagnose before retry.
"""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
OUT = Path('/workspace/.compat')
BASE = ROOT / 'verification/full-090'
FROZEN = '5e2ff697402d06e78b239e01f0b4307b50dd5633'
SECTION = 90
SOURCE_COUNT = 730
BRANCH = 'codex/p2-development'
TAG = 'p2-validation-090'
DOCS = ('DEVELOPMENT_CHECKPOINT.json', 'WORK_IN_PROGRESS.md',
        'PROJECT_COMPLETED.md', 'BATCH_CONTINUOUS_P2.md')


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def git(*args, input=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, input=input)


def git_text(*args):
    return git(*args).decode('utf-8').strip()


def relative(name):
    require(isinstance(name, str) and '\\' not in name, 'Use explicit POSIX archive paths')
    path = PurePosixPath(name)
    require(name == path.as_posix() and path.parts and not path.is_absolute()
            and all(p not in ('.', '..', '.git') for p in path.parts), f'Unsafe path: {name}')
    return path.as_posix()


def read(path):
    path = Path(path)
    require(path.is_absolute() and path.is_file() and not path.is_symlink(),
            f'An explicit regular absolute source file is required: {path}')
    return path.read_bytes()


def load(path):
    return json.loads(read(path))


def sources():
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
            for folder in ('rouge', 'tests', 'scripts')
            for p in sorted((ROOT / folder).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}


def last_selected(path):
    for line in reversed(read(path).decode('utf-8', errors='replace').splitlines()):
        try:
            result = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(result, dict) and 'tests_run' in result:
            return result
    raise ValueError(f'No selected-test receipt in {path}')


def selected_pass(result):
    require(result['passed'] is True and result['failures'] == result['errors'] == 0,
            'Selected tests must have passed without failures/errors')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--execute', action='store_true',
                        help='Root-authorized archive writes, commit and tag; absent means read-only preflight')
    args = parser.parse_args()
    spec_raw = read(args.spec)
    spec = json.loads(spec_raw)
    require(spec['format_version'] == 1 and spec['section'] == SECTION, 'Wrong spec contract')
    require(spec['expected_product_commit'] == FROZEN
            and spec['expected_source_count'] == SOURCE_COUNT, 'Wrong product baseline')
    require(git_text('branch', '--show-current') == BRANCH, 'Wrong branch')
    require(git_text('rev-parse', 'HEAD') == FROZEN, 'HEAD must equal actual full090 product commit')
    require(not git_text('status', '--porcelain'), 'Require clean worktree/index')
    require(not BASE.exists(), 'Never overwrite a completed/partial full090 archive')
    require(not git_text('tag', '--list', TAG), 'Validation tag already exists')
    closure_output = Path(spec['committed_closure_output'])
    require(closure_output.is_absolute() and closure_output.parent == LOCAL
            and not closure_output.exists(), 'Use a new external committed-closure receipt')

    files = {}
    origins = {}

    def add(name, data, origin):
        name = relative(name)
        require(name not in ('archive-manifest.json', 'git-index-payload-closure.json'),
                f'Input must not occupy a generated top-level archive name: {name}')
        if name in files:
            require(files[name] == data, f'Archive collision: {name}')
            return
        files[name], origins[name] = data, str(origin)

    def copy(path, name):
        add(name, read(path), path)

    def packet(info):
        prefix = relative(info['archive_prefix'])
        path = Path(info['manifest_path'])
        raw = read(path)
        require(sha(raw) == info['manifest_sha256'], f'Manifest hash: {path}')
        manifest = json.loads(raw)
        require(manifest['format_version'] == 1 and len(manifest['files']) == info['files'],
                f'Wrong explicit v1 packet: {path}')
        seen = set()
        for row in manifest['files']:
            name = relative(row['archive_path'])
            require(name not in seen, f'Duplicate row in {path}: {name}')
            seen.add(name)
            raw_file = read(row['source_path'])
            require(len(raw_file) == row['bytes'] and sha(raw_file) == row['sha256'],
                    f'Public attachment hash/size: {row["source_path"]}')
            add(f'{prefix}/{name}', raw_file, row['source_path'])
        add(f'{prefix}/{path.name}', raw, path)
        return manifest

    ctx_path = OUT / 'wine-validation-090-context.json'
    ctx = load(ctx_path)
    frozen_sources = ctx['source_sha256']
    require(ctx['section'] == SECTION and ctx['commit'] == FROZEN and ctx['branch'] == BRANCH,
            'Finished full context must bind the exact product commit/branch')
    require(ctx['source_snapshot_before_execution'] is True and ctx['native_windows'] is False,
            'Expected Wine compatibility context, not a native Windows certification')
    require(ctx['available_checks_passed'] is True and not ctx['source_drift']
            and ctx.get('completed_at') and ctx['source_sha256_after'] == frozen_sources,
            'Full context must be finished successfully with no drift')
    require(len(frozen_sources) == SOURCE_COUNT and sources() == frozen_sources,
            'Every maintained source must match actual full090 context')
    for name, digest in frozen_sources.items():
        relative(name)
        require(sha(git('show', f'{FROZEN}:{name}')) == digest, f'Frozen Git source differs: {name}')

    linux_path = LOCAL / 'linux-full-090.json'
    wine_path = OUT / 'wine-available-full-090.json'
    linux, wine = load(linux_path), load(wine_path)
    # This reproduces the frozen verify_full_available.source_hashes selector,
    # whose receipt scope is337, while full_context covers all730 maintained files.
    full_runner_paths = sorted(set([
        *ROOT.glob('rouge/**/*.py'), *ROOT.glob('rouge/data/**/*.json'),
        *ROOT.glob('tests/test_*.py'), ROOT / 'scripts/verify_full_available.py',
    ]))
    full_runner_scope = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in full_runner_paths}
    require(len(full_runner_scope) == 337 and set(full_runner_scope) <= set(frozen_sources)
            and all(frozen_sources[name] == digest for name, digest in full_runner_scope.items()),
            'Exact337 full-runner selector must match730 context subset')
    for receipt in (linux, wine):
        require(receipt['available_checks_passed'] is True and not receipt['source_drift']
                and receipt['failures'] == receipt['errors'] == 0,
                'Available full tests must pass, unavailable records remain separate')
        require(receipt['source_sha256'] == full_runner_scope,
                'Full receipt must match exact337 selector keyset and all values, not merely any subset')
        require(receipt['native_windows_integration_verified'] is False, 'Unexpected native scope')
    require(linux['wine_compatibility'] is False and wine['wine_compatibility'] is True,
            'Linux/Wine receipts must retain their actual platforms')
    require(ctx['complete_repository_validation'] == (
        linux['complete_repository_validation'] and wine['complete_repository_validation']),
        'Context repository-completeness mismatch')

    snapshot_path = LOCAL / 'root-selected-source-snapshot090.json'
    proof_path = LOCAL / 'linux-selected-090-byte-identity.json'
    original_selected_path = LOCAL / 'root-selected-090.log'
    selected_path = LOCAL / 'selected-090.log'
    snapshot, proof = load(snapshot_path), load(proof_path)
    require(snapshot['section'] == SECTION
            and snapshot['source_sha256_after_completed_selected_checks'] == frozen_sources
            and snapshot['new_selected_execution_in_this_snapshot'] is False,
            'Selected snapshot must match all730 source bytes')
    selected_pass(snapshot['selected_checks_completed'])
    require(sha(read(original_selected_path)) == snapshot['selected_log_sha256']
            and read(original_selected_path) == read(selected_path), 'Selected reused console differs')
    require(proof['passed'] is True and proof['source_files_verified'] == SOURCE_COUNT
            and proof['full_frozen_commit'] == FROZEN
            and proof['reused_completed_root_selected_section'] == SECTION
            and proof['fresh_selected_tests_executed_for_full'] is False
            and proof['reused_selected_log_sha256'] == snapshot['selected_log_sha256'],
            'Selected reuse proof does not establish exact byte identity')
    linux_selected = last_selected(selected_path)
    selected_pass(linux_selected)
    require(linux_selected == snapshot['selected_checks_completed'], 'Selected result mismatch')
    wine_selected_path = OUT / 'wine-cloud-090.json'
    wine_selected = load(wine_selected_path)
    selected_pass(wine_selected)
    require(last_selected(OUT / 'wine-cloud-090.log') == wine_selected, 'Wine selected console differs')
    for path in (LOCAL / 'linux-pipcheck-090.log', OUT / 'wine-pipcheck-090.log'):
        require('No broken requirements found.' in read(path).decode('utf-8', errors='replace'),
                f'Dependency check did not pass: {path}')

    ui_packet = spec['ui_packet']
    packet(ui_packet)
    preflight_path = Path(spec['ui_preflight_path'])
    preflight = load(preflight_path)
    require(sha(read(preflight_path)) == spec['ui_preflight_sha256'], 'UI preflight hash differs')
    require(preflight['passed'] is True and preflight['source_commit'] == FROZEN
            and preflight['source_files_verified'] == SOURCE_COUNT, 'UI preflight source mismatch')
    require(preflight['public_attachments_verified_before_actual_execution'] == ui_packet['files'],
            'Preflight/public packet count mismatch')
    require(preflight['public_manifest_name'] == Path(ui_packet['manifest_path']).name,
            'Preflight/public packet identity differs')
    design_root = Path(ui_packet['manifest_path']).parent
    for name, digest in preflight['fixed_hashes'].items():
        require(sha(read(design_root / relative(name))) == digest, f'UI fixed file differs: {name}')
    require(preflight['fixed_hashes'][Path(ui_packet['manifest_path']).name]
            == ui_packet['manifest_sha256'], 'Preflight must bind final public manifest SHA')
    ui_path, runner_path = Path(spec['ui_json_path']), Path(spec['ui_runner_path'])
    ui = load(ui_path)
    require(ui['passed'] is True and ui['complete_ui_validation'] is True
            and not ui['source_drift'] and ui['private_state_isolated'] is True
            and ui['native_windows_verified'] is False and ui['game_captures'] == ui['chat_requests'] == 0,
            'Actual Wine window must pass in its isolated offline scope')
    require(ui['source_sha256'] == ui['source_sha256_after'] == frozen_sources, 'Actual UI source drift')
    require(len(ui['checks']) == spec['expected_actual_ui_records'] == ctx['ui_checks']
            == preflight['planned_actual_UI_records'], 'Actual/planned UI record counts differ')
    require(ui['total_actual_checks'] == len(ui['checks']), 'UI actual total differs')
    require(ui['preserved_full_085_checks'] == 4217, 'Old4217 actual checks must remain preserved')
    require(ctx['complete_ui_validation'] is True, 'Finished context lacks complete available UI')
    for key, value in spec['ui_contract'].items():
        require(ui[key] == value, f'Final UI contract differs: {key}')
    require(sha(read(runner_path)) == spec['expected_ui_runner_sha256']
            == preflight['fixed_hashes'][spec['ui_runner_packet_name']], 'Runtime runner differs from seal')
    inspection_path = Path(spec['ui_inspection_path'])
    inspection = load(inspection_path)
    require(sha(read(inspection_path)) == spec['ui_inspection_sha256']
            and inspection['passed'] is True and len(inspection['root_viewed_actual_pngs']) == 4,
            'Root must view and seal four actual public PNGs')
    for name, row in inspection['root_viewed_actual_pngs'].items():
        require('/' not in relative(name) and name.endswith('.png'), 'Expected explicit OUT screenshot basename')
        raw = read(OUT / name)
        require(sha(raw) == row['sha256'] and raw.startswith(b'\x89PNG\r\n\x1a\n'),
                f'Viewed screenshot changed: {name}')
        add(name, raw, OUT / name)

    for info in spec.get('additional_public_packets', []):
        require(info['numbered_section_completed'] is False, 'Source leads are not completed product sections')
        packet(info)
    copy(linux_path, 'linux.json')
    copy(wine_path, 'wine.json')
    copy(ctx_path, 'wine-context.json')
    copy(wine_selected_path, 'wine-selected.json')
    copy(ui_path, 'wine-ui.json')
    copy(runner_path, 'wine-ui-runner.py')
    copy(preflight_path, 'root-ui-preflight.json')
    copy(inspection_path, 'root-window-inspection.json')
    fixed = (
        (LOCAL / 'linux-full-090-console.log', 'linux-full-console.log'),
        (LOCAL / 'linux-full-090.log', 'linux-full.log'),
        (OUT / 'wine-available-full-090-console.log', 'wine-full-console.log'),
        (OUT / 'wine-available-full-090.log', 'wine-full.log'),
        (selected_path, 'linux-selected.log'), (original_selected_path, 'root-selected-original.log'),
        (OUT / 'wine-cloud-090.log', 'wine-selected.log'),
        (LOCAL / 'linux-pipcheck-090.log', 'linux-pipcheck.log'),
        (OUT / 'wine-pipcheck-090.log', 'wine-pipcheck.log'),
        (proof_path, 'linux-selected-byte-identity.json'),
        (snapshot_path, 'root-selected-source-snapshot.json'),
        (Path(spec['ui_process_console']), 'wine-ui-process.log'),
        (LOCAL / 'full_context.py', 'full_context.py'),
        (LOCAL / 'selected_snapshot_full.py', 'selected_snapshot_full.py'),
    )
    for path, name in fixed:
        copy(path, name)
    copy(Path(__file__).resolve(), 'archive-full-090.py')
    add('archive-spec.json', spec_raw, args.spec)
    for row in spec.get('additional_public_files', []):
        raw = read(row['source_path'])
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'Additional public file differs')
        add(row['archive_path'], raw, row['source_path'])

    next_action = spec['next_action']
    require(isinstance(next_action, str) and next_action.strip(), 'Provide concrete next action')
    cp = load(ROOT / DOCS[0])
    require(cp['completed_sections'] == SECTION, 'Checkpoint has not completed section90')
    summary = (
        f'第90节后全量可用检验：Linux {linux["tests_run"]}运行/{linux["tests_passed"]}通过/'
        f'{linux["historical_or_declared_skips"]}历史跳过/{linux["unavailable_records"]}缺失记录；'
        f'Wine {wine["tests_run"]}运行/{wine["tests_passed"]}通过/'
        f'{wine["historical_or_declared_skips"]}历史跳过/{wine["unavailable_records"]}缺失记录。'
        f'均无失败/错误/源码漂移，实际窗口{len(ui["checks"])}条检查通过并保留旧4217；'
        f'{SOURCE_COUNT}源码与{FROZEN[:8]}一致。Linux精选仅按全源码字节复用，Wine精选和两侧依赖检查通过。'
        '缺失记录不计通过，可能含子测试、不与运行数一一互斥；Wine不代表原生Windows/game/desktop验收。'
    )
    limits = {
        'product_commit': FROZEN, 'maintained_source_files': SOURCE_COUNT,
        'full_runner_receipt_source_files': len(full_runner_scope),
        'context_files_outside_full_runner_scope': len(set(frozen_sources) - set(full_runner_scope)),
        'actual_ui_records': len(ui['checks']), 'preserved_full085_ui_records': 4217,
        'all_available_checks_passed': True,
        'complete_repository_validation': ctx['complete_repository_validation'],
        'complete_available_ui_validation': True, 'native_windows_verified': False,
        'game_capture_account_desktop_multiple_machine_delivery_verified': False,
        'linux_selected_reused_only_at_exact_source_bytes': True,
        'fresh_tests_API_helpers_Qt_Wine_started_by_archive_script': 0,
        'additional_packets': [{k: p[k] for k in ('archive_prefix', 'manifest_sha256', 'files',
                               'numbered_section_completed', 'scope')} for p in spec.get('additional_public_packets', [])],
        'limits': 'Unknown native clock/attachment/composition remain unknown. Missing/private fixtures are not reconstructed. UI visible PNG evidence is bounded by root inspection; assertions and measured call ledgers retain their own scope.',
    }
    add('LIMITS.md', (summary + '\n\n' + limits['limits'] + '\n').encode(), 'generated scope text')
    add('validation-scope.json', encoded(limits), 'generated bounded summary')
    cp.update(full_validation_due=False, next_action=next_action)
    cp['last_full_validation'] = {
        'after_section': SECTION, 'completed_at': ctx['completed_at'], 'completion_ref': TAG,
        'product_commit': FROZEN, 'linux': 'verification/full-090/linux.json',
        'wine': 'verification/full-090/wine.json', 'ui': 'verification/full-090/wine-ui.json',
        'complete_repository_validation': ctx['complete_repository_validation'],
        'ui_available_checks_passed': True, 'complete_ui_validation': True, 'limits': limits['limits'],
    }
    cp['wine_validation'] = summary
    doc_files = {DOCS[0]: encoded(cp)}
    transforms = {
        DOCS[1]: lambda s: '# 连续开发断点 · 第90节后全量可用检验完成\n\n' + summary
                           + f' 下一步：{next_action}。自动继续。见 `verification/full-090`。\n\n---\n\n' + s,
        DOCS[2]: lambda s: '# 连续开发全量检验 090\n\n' + summary
                           + ' 见 `verification/full-090`。\n\n---\n\n' + s,
        DOCS[3]: lambda s: s + '\n## 第90节后全量可用检验\n\n' + summary
                           + ' 见 `verification/full-090`。自动继续下一组。\n',
    }
    for name, transform in transforms.items():
        original = read(ROOT / name)
        text = transform(original.decode('utf-8').replace('\r\n', '\n'))
        doc_files[name] = (text.replace('\n', '\r\n') if b'\r\n' in original else text).encode('utf-8')
    require(sources() == frozen_sources and git_text('rev-parse', 'HEAD') == FROZEN
            and not git_text('status', '--porcelain'), 'Input drift during preflight')
    if not args.execute:
        print(json.dumps({'read_only_preflight_passed': True, 'product_commit': FROZEN,
                          'maintained_sources': SOURCE_COUNT, 'planned_payloads': len(files),
                          'actual_ui_records': len(ui['checks']), 'writes_commit_tag_performed': False}))
        return

    # All required inputs are in memory and validated before the first mutation.
    BASE.mkdir()
    for name, raw in files.items():
        target = BASE / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as handle:
            handle.write(raw)
        require(target.read_bytes() == raw, f'Archive write changed bytes: {name}')
    for name, raw in doc_files.items():
        (ROOT / name).write_bytes(raw)
    tracked = {'verification/full-090/' + name: raw for name, raw in files.items()}
    tracked.update(doc_files)

    def stage_verify(expected):
        paths = sorted(expected)
        for start in range(0, len(paths), 80):
            git('add', '-f', '--', *paths[start:start + 80])
        staged = {p.decode() for p in git('diff', '--cached', '--name-only', '-z').split(b'\0') if p}
        require(staged == set(expected), 'Unexpected/missing staged files; do not commit')
        for name, raw in expected.items():
            require(git('show', f':{name}') == raw, f'Index Git blob differs: {name}')

    stage_verify(tracked)
    closure = {
        'format_version': 1, 'product_commit': FROZEN, 'passed': True,
        'scope': 'Actual index-byte verification for payloads and metadata before closure receipt/final manifest. Full final index and committed blobs are checked by this script before tag; their exact committed result is emitted in the new external receipt.',
        'verified_payload_paths': len(tracked), 'all_paths_force_staged': True,
        'excluded_self_and_final_manifest': ['git-index-payload-closure.json', 'archive-manifest.json'],
        'files': [{'path': name, 'sha256': sha(raw), 'bytes': len(raw),
                   'git_index_blob': git_text('rev-parse', f':{name}')} for name, raw in sorted(tracked.items())],
    }
    raw = encoded(closure)
    (BASE / 'git-index-payload-closure.json').write_bytes(raw)
    files['git-index-payload-closure.json'] = raw
    origins['git-index-payload-closure.json'] = 'generated after actual payload index verification'
    manifest = {'format_version': 1, 'section': SECTION, 'product_commit': FROZEN,
                'files': [{'source_path': str(BASE / name), 'archive_path': name,
                           'sha256': sha(raw), 'bytes': len(raw), 'original_source_path': origins[name]}
                          for name, raw in sorted(files.items())]}
    manifest_raw = encoded(manifest)
    (BASE / 'archive-manifest.json').write_bytes(manifest_raw)
    tracked.update({'verification/full-090/git-index-payload-closure.json': files['git-index-payload-closure.json'],
                    'verification/full-090/archive-manifest.json': manifest_raw})
    stage_verify(tracked)
    require(sources() == frozen_sources and git_text('rev-parse', 'HEAD') == FROZEN,
            'Maintained source or product HEAD changed during archival')
    # Preserved original public sources may contain historical whitespace; check
    # authored metadata, and preserve archival bytes without reformatting them.
    git('-c', 'core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol',
        'diff', '--cached', '--check', '--', *DOCS)
    git('commit', '--quiet', '-m', f'存档第90节Linux与Wine全量及{len(ui["checks"])}条真实窗口检验')
    commit = git_text('rev-parse', 'HEAD')
    require(git_text('rev-parse', 'HEAD^') == FROZEN, 'Unexpected archive commit parent')
    require(sources() == frozen_sources, 'Maintained sources changed after archival commit')
    for name, raw in tracked.items():
        require(git('show', f'{commit}:{name}') == raw, f'Committed Git blob differs: {name}')
    require(not git_text('status', '--porcelain'), 'Archive commit left a dirty worktree')
    result = {'passed': True, 'section': SECTION, 'product_commit': FROZEN,
              'archive_commit': commit, 'archive_manifest_sha256': sha(manifest_raw),
              'maintained_source_files': SOURCE_COUNT, 'archive_payload_files': len(manifest['files']),
              'actual_ui_records': len(ui['checks']), 'all_final_index_and_commit_blob_files_verified': len(tracked),
              'all_public_files_force_staged_including_ignored_build_leaves': True,
              'native_windows_verified': False, 'completion_ref': TAG,
              'tagging_waits_for_this_verified_external_receipt': True}
    # Exact archive commit cannot be embedded into its own immutable Git tree.
    # Preserve the truthful post-commit closure externally; never rewrite full085/full090.
    with closure_output.open('xb') as handle:
        handle.write(encoded(result))
    git('tag', TAG)
    require(git_text('rev-parse', TAG) == commit, 'Validation tag does not target verified commit')
    print(json.dumps({**result, 'validation_tag_verified': True,
                      'external_committed_closure_sha256': sha(read(closure_output))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
