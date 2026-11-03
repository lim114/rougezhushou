"""PENDING source-only draft; root must supply actual final bindings and formal review.

This prepares/archive-stages explicit public evidence and a batch-save-ready tree.
It never runs tests, imports the product, starts Wine, commits, tags, or pushes.
The pending template cannot pass: future artifacts, SHA values and JSON pointers
must be bound from their actual announced final source/receipts by root.
"""
import argparse
import hashlib
import json
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
HEAD92 = 'f509d186e501bfcfd042e45b46e398ec756840ec'
FULL_CLASSIFIER_SHA = 'ea4481c9cd95fb9438f673b76c14c9386263469e12b2855fa04e9a47d7c63dcc'
BRANCH = 'codex/p2-development'
PREFIX = 'verification/full-095'
DOCS = ('DEVELOPMENT_CHECKPOINT.json', 'WORK_IN_PROGRESS.md',
        'PROJECT_COMPLETED.md', 'BATCH_CONTINUOUS_P2.md')
JOBS = ('linux_full', 'wine_full', 'linux_selected', 'wine_selected',
        'linux_pip', 'wine_pip', 'wine_ui', 'saved_review')
REQUIRED = ('source095_guard', 'context_start', 'context_final', 'linux_full',
            'wine_full', 'linux_selected', 'wine_selected', 'linux_pip_log',
            'wine_pip_log', 'root_primary_exits', 'ui_receipt', 'ui_extra_acceptance',
            'ui_saved_review', 'ui_saved_review_exit', 'ui_visual_review',
            'ui_final_runner', 'ui_preflight', 'publication_authorization',
            'context_final_runner', 'context_source_binding')


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def relative(name):
    require(type(name) is str and '\\' not in name, 'Explicit POSIX path required')
    p = PurePosixPath(name)
    require(name == p.as_posix() and p.parts and not p.is_absolute()
            and all(part not in ('.', '..', '.git') for part in p.parts), 'Unsafe path: ' + str(name))
    return name


def read(path):
    p = Path(path)
    require(p.is_absolute() and p.is_file() and not p.is_symlink(), 'Explicit regular absolute input: ' + str(p))
    return p.read_bytes()


def new(path, raw):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as stream:
        stream.write(raw)
    require(p.read_bytes() == raw, 'Written bytes differ: ' + str(p))


def pointer(value, path):
    require(type(path) is str and path.startswith('/'), 'Actual JSON pointer must be supplied')
    for token in path[1:].split('/'):
        key = token.replace('~1', '/').replace('~0', '~')
        if type(value) is list:
            require(key.isdecimal(), 'List pointer index required')
            value = value[int(key)]
        else:
            require(type(value) is dict and key in value, 'JSON pointer does not exist: ' + path)
            value = value[key]
    return value


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def git_text(*args):
    return git(*args).decode().strip()


def maintained():
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
            for base in ('rouge', 'tests', 'scripts')
            for p in sorted((ROOT / base).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}


def full_scope():
    paths = set([*ROOT.glob('rouge/**/*.py'), *ROOT.glob('rouge/data/**/*.json'),
                 *ROOT.glob('tests/test_*.py'), ROOT / 'scripts/verify_full_available.py'])
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in sorted(paths)}


def ui_scope():
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in sorted((ROOT / 'rouge').rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}


def selected(raw, kind):
    if kind == 'json':
        value = json.loads(raw)
    else:
        require(kind == 'last_json_line', 'Explicit selected receipt kind required')
        value = json.loads(raw.decode().strip().splitlines()[-1])
    require(value['passed'] is True and value['failures'] == value['errors'] == 0, 'Selected suite failed')
    require(type(value['tests_run']) is int and type(value['skipped']) is int
            and 0 <= value['skipped'] <= value['tests_run'], 'Invalid selected counters')
    return value


def proof_binding(proof, contract, expected, visual=False):
    """Use the sealed context owner's explicit pointer/projection contract."""
    value = pointer(proof, contract['pointer'])
    require(contract['projection'] in ('full_ref', 'bytes_sha256'), 'Unknown explicit proof projection')
    if visual:
        require(contract['projection'] == 'full_ref', 'Visual proof must bind current file path too')
    if contract['projection'] == 'full_ref':
        require(value == expected, 'Actual proof full file reference differs')
    else:
        require(type(value) is dict and value.get('bytes') == expected['bytes']
                and value.get('sha256') == expected['sha256'], 'Actual proof file bytes/SHA differ')
        if 'path' in value:
            require(value['path'] == expected['path'], 'Actual proof file path differs')


def source_gate(source):
    require(git_text('branch', '--show-current') == BRANCH, 'Wrong development branch')
    require(git_text('rev-parse', 'HEAD') == HEAD92, 'Do not invent a section95 commit')
    require(source['passed'] is True and source['current_maintained'] == len(source['source_sha256_after']), 'Actual95 source guard invalid')
    require(maintained() == source['source_sha256_after'], 'Current maintained file set or bytes drifted')


def physical_files(base):
    """Exact recursive regular file set; directories/symlinks/special entries cannot disappear."""
    base = Path(base)
    require(base.is_absolute() and base.is_relative_to(ROOT) and base != ROOT,
            'Explicit repository archive directory required')
    for parent in (base, *base.parents):
        require(stat.S_ISDIR(parent.lstat().st_mode), 'Archive directory/ancestor must be a real directory')
        if parent == ROOT:
            break
    files = set()
    for path in base.rglob('*'):
        mode = path.lstat().st_mode
        require(stat.S_ISDIR(mode) or stat.S_ISREG(mode), 'Archive symlink/nonregular entry forbidden: ' + str(path))
        if stat.S_ISREG(mode):
            files.add(path.relative_to(ROOT).as_posix())
    return files


def index(paths, prefix=None):
    rows = {}
    args = ['ls-files', '--stage', '-z']
    if prefix is not None:
        args += ['--', prefix]
    for item in git(*args).split(b'\0'):
        if item:
            header, name = item.split(b'\t', 1)
            mode, blob, stage = header.decode().split()
            name = name.decode()
            if prefix is not None or name in paths:
                require(mode == '100644' and stage == '0', 'Regular resolved public file index required')
            rows[name] = blob
    if prefix is not None:
        require(physical_files(ROOT / relative(prefix)) == set(paths), 'Archive physical path set differs before index gate')
        require(set(rows) == set(paths), 'Archive index path set differs')
    else:
        changed = {p.decode() for p in git('diff', '--cached', '--name-only', '-z').split(b'\0') if p}
        require(changed == set(paths), 'Unexpected/missing staged batch paths')
    for name, raw in paths.items():
        require(rows.get(name) == hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(), 'Index blob differs: ' + name)


def stage(paths):
    names = sorted(paths)
    for offset in range(0, len(names), 80):
        git('add', '-f', '--', *names[offset:offset + 80])


def formal_gate(args, spec_raw):
    raw = read(args.formal_review)
    require(sha(raw) == args.formal_sha256, 'Fresh archive-helper formal review SHA differs')
    review = json.loads(raw)
    require(pointer(review, args.formal_pass_pointer) is True
            and pointer(review, args.formal_runtime_pointer) is False, 'Source-only review required, not invented runtime PASS')
    require(pointer(review, args.formal_helper_pointer) == sha(read(Path(__file__).resolve())), 'Formal review does not bind this helper')
    require(pointer(review, args.formal_spec_pointer) == sha(spec_raw), 'Formal review does not bind the actual completed spec')
    return sha(raw)


def collect(spec):
    require(spec['format_version'] == 1 and spec['section'] == 95
            and spec['status'] == 'ROOT_ACTUAL_FULL095_BINDINGS_READY', 'PENDING contract cannot execute')
    require(spec['expected_HEAD_before_batch_commit'] == HEAD92 and spec['branch'] == BRANCH, 'Actual92 HEAD binding required')
    bindings = spec['bindings']
    require(set(REQUIRED) <= set(bindings), 'Missing explicit runtime/guard/witness role')
    raw_by_role, decoded, payload, origins = {}, {}, {}, {}

    def add(name, raw, origin):
        name = relative(name)
        require(name not in ('archive-manifest.json', 'git-index-payload-closure.json'), 'Reserved generated name')
        if name in payload:
            require(payload[name] == raw and origins[name] == origin, 'Archive collision: ' + name)
        else:
            payload[name], origins[name] = raw, origin

    for role, item in bindings.items():
        require(item['public'] is True, 'Public qualification required: ' + role)
        raw = read(item['source_path'])
        require(len(raw) == item['bytes'] and sha(raw) == item['sha256'], 'Actual binding bytes/SHA differ: ' + role)
        raw_by_role[role] = raw
        if item['kind'] == 'json':
            decoded[role] = json.loads(raw)
        add(item['archive_path'], raw, item['source_path'])
    source = decoded['source095_guard']
    source_gate(source)
    require(sha(read(ROOT / 'scripts/verify_full_available.py')) == FULL_CLASSIFIER_SHA,
            'Original full classifier changed; a new source qualification is required')
    available, scope = {}, full_scope()
    for role, expected_wine in (('linux_full', False), ('wine_full', True)):
        receipt = decoded[role]
        require(receipt['available_checks_passed'] is True and receipt['failures'] == receipt['errors'] == 0
                and receipt['source_drift'] == [], 'Actual full suite failed/drifted: ' + role)
        require(receipt['source_sha256'] == scope and set(scope) <= set(source['source_sha256_after']), 'Exact dynamic full selector differs')
        require(receipt['wine_compatibility'] is expected_wine
                and receipt['native_windows_integration_verified'] is False, 'Full platform/native boundary differs')
        require(type(receipt['complete_repository_validation']) is bool, 'Repository completeness must be actual bool')
        require(type(receipt['unavailable']) is list and receipt['unavailable_records'] == len(receipt['unavailable']), 'Unavailable records were dropped or counter changed')
        if receipt['unavailable']:
            require(receipt['complete_repository_validation'] is False, 'Unavailable cannot become complete-repository PASS')
        available[role] = receipt
    for role in ('linux_selected', 'wine_selected'):
        available[role] = selected(raw_by_role[role], spec['selected_receipt_kinds'][role])
    for role in ('linux_pip_log', 'wine_pip_log'):
        require('No broken requirements found.' in raw_by_role[role].decode(errors='replace'), 'Dependency check did not pass')
    contracts = spec['contracts']
    final = decoded['context_final']
    get = lambda name: pointer(final, contracts['context'][name])
    require(get('status') == 'PASS_ACTUAL_FULL095_AVAILABLE_NOT_NATIVE_WINDOWS', 'Incomplete final context')
    require(get('section') == 95 and get('base_HEAD') == HEAD92, 'Final context actual source baseline differs')
    require(get('available_pass') is get('complete_ui') is get('fresh_selected') is True
            and get('selected_reuse') is get('native_windows') is False, 'Fresh available scope required')
    require(get('source_before') == get('source_after') == source['source_sha256_after']
            and get('source_drift') == [], 'Entire dynamic source context before/after differs')
    complete = available['linux_full']['complete_repository_validation'] and available['wine_full']['complete_repository_validation']
    require(get('complete_repository') is complete, 'Completeness does not match real receipts')
    require(type(get('completed_at')) is str and get('completed_at'), 'Final context completion time missing')
    start = decoded['context_start']
    require(start['status'] == 'ACTUAL_FULL095_STARTED_NOT_PASSED'
            and start['source_sha256'] == source['source_sha256_after'], 'Fresh original start context differs')
    for key, role in (('binding', 'context_source_binding'), ('final_context_runner', 'context_final_runner')):
        item = bindings[role]
        require(start[key] == final[key] == {'path': item['source_path'], 'bytes': item['bytes'], 'sha256': item['sha256']}, 'Started/final context source binding differs')
    actual_binding = decoded['context_source_binding']
    require((actual_binding['format_version'] == 2
             or (actual_binding['format_version'] == 3
                 and actual_binding.get('actual_ui_retry') is True
                 and actual_binding.get('root_spec_projection_from_ui_retry') is True))
            and actual_binding['section'] == 95 and
            actual_binding['status'] == 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS', 'Actual format2 sealed context binding required')
    actual_inputs = actual_binding['actual_inputs']
    execution_contracts = actual_inputs['execution_contracts']
    planned_outputs = actual_inputs['global_output_plan']['paths']
    require(actual_inputs['actual_base_HEAD'] == HEAD92 and actual_inputs['source_sha256'] == source['source_sha256_after']
            and set(execution_contracts) == set(JOBS) and set(spec['primary_exit_roles']) == set(JOBS),
            'Exact eight source-qualified execution contracts and status roles required')
    root_witness = decoded['root_primary_exits']
    require(root_witness['format_version'] == 2 and root_witness['section'] == 95 and
            root_witness['actual_root_observed_primary_exits'] is True and
            set(root_witness['executions']) == set(JOBS) and final['actual_root_primary_exits'] == root_witness and
            type(final['physical_primary_exit_files_verified']) is int and final['physical_primary_exit_files_verified'] == 8 and
            final['exact_execution_contracts_verified'] is True, 'Final context must bind actual eight-execution witness exactly')
    refs_by_path = {item['source_path']: {'path': item['source_path'], 'bytes': item['bytes'], 'sha256': item['sha256']}
                    for item in bindings.values()}
    began_context = datetime.fromisoformat(start['started_at'])
    completed_context = datetime.fromisoformat(get('completed_at'))
    physical_status_paths = []
    for job in JOBS:
        entry = root_witness['executions'][job]
        contract = execution_contracts[job]
        require(entry['actual_root_observed_primary_exit'] is entry['primary_exit_code_captured'] is entry['fresh_execution'] is True
                and type(entry['primary_exit_code']) is int and entry['primary_exit_code'] == 0,
                'Actual captured primary/fresh execution required: ' + job)
        require(entry['argv'] == contract['argv'] and entry['cwd'] == contract['cwd'] == str(ROOT)
                and entry['runner'] == contract['runner'] and entry['entry_kind'] == contract['entry_kind']
                and entry['script_arg_index'] == contract['script_arg_index'], 'Exact source-reviewed full execution contract differs: ' + job)
        began = datetime.fromisoformat(entry['started_at']); ended = datetime.fromisoformat(entry['completed_at'])
        require(began_context <= began <= ended <= completed_context, 'Actual execution outside fresh completed context: ' + job)
        role = spec['primary_exit_roles'][job]
        require(role in bindings and raw_by_role[role] in (b'0\n', b'0\r\n'), 'Canonical actual physical primary status required: ' + job)
        item = bindings[role]
        status_ref = {'path': item['source_path'], 'bytes': item['bytes'], 'sha256': item['sha256']}
        require(entry['exit_code_file'] == status_ref and Path(status_ref['path']).resolve() == Path(contract['exit_code_path']).resolve(),
                'Physical status must equal exact witness and unique planned exit sink: ' + job)
        physical_status_paths.append(str(Path(status_ref['path']).resolve()))
        stdout = entry['stdout_log']
        require(refs_by_path.get(stdout['path']) == stdout and
                Path(stdout['path']).resolve() == Path(planned_outputs[contract['stdout_key']]).resolve(),
                'Actual stdout file must be exact-bound and explicitly archived: ' + job)
        if entry['runner'] is not None:
            require(refs_by_path.get(entry['runner']['path']) == entry['runner'], 'Actual executed source must be explicitly archived: ' + job)
        if job == 'saved_review':
            require(role == 'ui_saved_review_exit' and entry['output_receipt'] == refs_by_path[bindings['ui_saved_review']['source_path']]
                    and Path(entry['output_receipt']['path']).resolve() == Path(planned_outputs['saved_review_receipt']).resolve(),
                    'Eighth physical status/output receipt must bind actual saved review')
    require(len(set(physical_status_paths)) == 8 and len(set(spec['primary_exit_roles'].values())) == 8,
            'Eight physical primary status paths/roles must be unique')
    # Root supplies actual final pointer locations, not guessed future output fields.
    links = spec['context_check_links']
    require(set(('linux_full', 'wine_full', 'linux_selected', 'wine_selected', 'linux_pip_log',
                 'wine_pip_log', 'ui_receipt', 'ui_extra_acceptance', 'ui_saved_review',
                 'ui_visual_review', 'root_primary_exits')) <= set(links), 'Context must link all actual full/UI review evidence')
    for role, ptr in links.items():
        item = bindings[role]
        require(pointer(final, ptr) == {'path': item['source_path'], 'bytes': item['bytes'], 'sha256': item['sha256']}, 'Final context exact artifact ref differs: ' + role)

    ui = decoded['ui_receipt']
    ug = lambda name: pointer(ui, contracts['ui'][name])
    require(ug('passed') is ug('complete_ui') is ug('private_isolation') is True
            and ug('native_windows') is False and ug('source_drift') == [], 'Actual UI incomplete/drifted/native scope mismatch')
    require(ug('game_captures') == ug('chat_requests') == 0, 'Game/chat actions are outside authorization')
    require(ug('source_before') == ug('source_after') == ui_scope(), 'Exact UI own selector before/after differs')
    checks = ug('checks')
    require(type(checks) is list and len(checks) == ug('actual_checks') == get('ui_checks')
            == spec['expected_actual_UI_checks'] and len(checks) > 0, 'Actual UI counts differ from qualified final plan')
    for item in spec['actual_UI_source_contract_assertions']:
        require(pointer(ui, item['pointer']) == item['expected'], 'Qualified final UI contract differs')
    require(spec['actual_UI_source_contract_assertions'], 'Explicit current fullUI source contract required')
    acceptance = get('ui_acceptance')
    item = bindings['ui_receipt']
    ui_ref = {'path': item['source_path'], 'bytes': item['bytes'], 'sha256': item['sha256']}
    require(acceptance['actual_ui_receipt'] == ui_ref, 'Checked extra acceptance belongs to another UI receipt')
    extra = decoded['ui_extra_acceptance']
    item = bindings['root_primary_exits']
    primary_ref = {'path': item['source_path'], 'bytes': item['bytes'], 'sha256': item['sha256']}
    require(extra['format_version'] == 2 and extra['section'] == 95 and
            extra['actual_ui_receipt'] == ui_ref and extra['artifacts'] == acceptance['artifacts'] and
            extra['primary_exit_witness'] == primary_ref, 'Original format2 extra acceptance/witness changed after context checking')
    outputs = spec['actual_UI_output_roles']
    require(type(outputs) is list and outputs and len(outputs) == len(set(outputs)), 'Actual declared native/PNG output roles required')
    require(set(spec['actual_PNG_roles']) <= set(outputs) and spec['actual_PNG_roles'], 'Actual declared PNG roles required')
    actual_files = {row['file']['path']: row for row in acceptance['artifacts']}
    expected_files = {bindings[role]['source_path']: {'path': bindings[role]['source_path'],
        'bytes': bindings[role]['bytes'], 'sha256': bindings[role]['sha256']} for role in outputs}
    require(len(actual_files) == len(acceptance['artifacts']) and set(actual_files) == set(expected_files)
            and all(actual_files[name]['file'] == value for name, value in expected_files.items()), 'All current declared native/PNG artifacts must be explicit archive bindings')
    screenshot_paths = {name for name, row in actual_files.items() if row['kind'] == 'screenshot'}
    require(screenshot_paths == {bindings[role]['source_path'] for role in spec['actual_PNG_roles']}
            and any(row['kind'] == 'native-evidence' for row in actual_files.values()), 'Actual native/PNG artifact kinds differ')
    refs_by_path = {item['source_path']: {'path': item['source_path'], 'bytes': item['bytes'], 'sha256': item['sha256']} for item in bindings.values()}
    expected_common = {'ui_receipt': ui_ref,
        'ui_runner': refs_by_path[bindings['ui_final_runner']['source_path']],
        'source_guard': refs_by_path[bindings['source095_guard']['source_path']]}
    checked_proofs = acceptance['receipts']
    require(len(checked_proofs) == len(extra['receipts']) == 2 and
            {row['kind'] for row in checked_proofs} == {row['kind'] for row in extra['receipts']} == {'saved-validation', 'visual-review'},
            'Exactly one actual saved and one pixel review required')
    for row in checked_proofs:
        require(row['kind'] in ('saved-validation', 'visual-review'), 'Unknown checked proof kind')
        require(refs_by_path.get(row['file']['path']) == row['file'], 'Checked proof receipt omitted from explicit archive bindings')
        proof = json.loads(read(row['file']['path']))
        original_rows = [item for item in extra['receipts'] if item['kind'] == row['kind'] and item['file'] == row['file']]
        require(len(original_rows) == 1, 'Actual checked proof row is ambiguous or missing in original acceptance')
        original = original_rows[0]
        require(original['required_true_pointers'] == row['checked_true_pointers']
                and original['common_file_bindings'] == row['checked_common_file_bindings']
                and original['artifact_bindings'] == row['checked_artifact_bindings'], 'Checked proof pointers differ from exact actual acceptance contract')
        require(row['checked_true_pointers'] and all(pointer(proof, ptr) is True for ptr in row['checked_true_pointers']), 'Checked actual acceptance proof no longer passes')
        visual = row['kind'] == 'visual-review'
        if visual:
            require(pointer(proof, original['actual_view_image_pointer']) is True, 'Source prose cannot replace actual root screenshot inspection')
        common = row['checked_common_file_bindings']
        required_common = {'ui_receipt'} if visual else {'ui_receipt', 'ui_runner', 'source_guard'}
        require(required_common <= set(common) and set(common) <= set(expected_common), 'Checked current proof common bindings incomplete')
        for name, contract in common.items():
            proof_binding(proof, contract, expected_common[name], visual)
        covered = set()
        for contract in row['checked_artifact_bindings']:
            name = contract['artifact_path']
            require(name in actual_files and name not in covered, 'Unrelated/duplicate checked proof artifact')
            covered.add(name)
            proof_binding(proof, contract, actual_files[name]['file'], visual)
        require((screenshot_paths if visual else set(actual_files)) <= covered, 'Checked proof does not cover actual declared artifacts')
        if not visual:
            witness = row['actual_saved_review_primary_exit']
            require(original['execution_name'] == 'saved_review' and witness == root_witness['executions']['saved_review'],
                    'Normalized saved execution must equal actual format2 common witness')
            require(witness['actual_root_observed_primary_exit'] is witness['primary_exit_code_captured'] is witness['fresh_execution'] is True
                    and type(witness['primary_exit_code']) is int and witness['primary_exit_code'] == 0
                    and witness['output_receipt'] == row['file'], 'Saved review actual captured primary exit missing')
            for key in ('runner', 'stdout_log'):
                reference = witness[key]
                require(refs_by_path.get(reference['path']) == reference, 'Saved review source/console omitted from public archive bindings')
        else:
            require(row['actual_saved_review_primary_exit'] is None, 'Visual review cannot fabricate a saved primary execution')
    for role in spec['actual_PNG_roles']:
        require(raw_by_role[role].startswith(b'\x89PNG\r\n\x1a\n'), 'Actual PNG signature differs')
    authorization = decoded['publication_authorization']
    require(authorization['user_explicit_destination'] == '提交并推送到 GitHub 当前开发分支'
            and authorization['branch'] == BRANCH, 'Existing explicit user push authorization missing')

    section_files = {}
    require([row['number'] for row in spec['sections']] == [93, 94, 95], 'Actual completed93/94/95 chain required')
    checked_chain = get('section_chain')
    require([row['section'] for row in checked_chain] == [93, 94, 95], 'Actual checked full context chain differs')
    for section, checked_section in zip(spec['sections'], checked_chain):
        n = section['number']
        receipt = decoded[section['receipt_role']]
        closure = decoded[section['closure_role']]
        guard = decoded[section['source_role']]
        require(receipt['section'] == closure['section'] == n
                and receipt['passed'] is receipt['workflow_complete'] is receipt['actual_window_verified_by_root'] is True, 'Section is only preparation or incomplete')
        require(receipt['completion_ref_is_Git_tag'] is False and
                receipt['commit_status'] == 'pending_next_fifth_section_full_PASS' and
                type(receipt['maintained_source_files']) is int and type(checked_section['source_files']) is int and
                receipt['maintained_source_files'] == checked_section['source_files'] == len(guard['source_sha256_after']),
                'Actual section completion/source count cannot invent a commit/tag or omit guarded sources')
        require(closure['status'] == 'VERIFIED_ARCHIVED_NOT_COMMITTED_OR_PUSHED'
                and closure['actual_HEAD_unchanged'] == HEAD92
                and closure['all_archive_index_blobs_exact'] is True, 'Section archival closure differs')
        require(closure['source_snapshot_sha256'] == bindings[section['source_role']]['sha256'], 'Section source guard binding differs')
        for name, role in (('receipt', section['receipt_role']), ('closure', section['closure_role']), ('source_guard', section['source_role'])):
            item = bindings[role]
            require(checked_section[name] == {'path': item['source_path'], 'bytes': item['bytes'], 'sha256': item['sha256']}, 'Context acceptance chain source/receipt binding differs')
        archive = relative(receipt['research_archive'])
        mf_path = ROOT / archive / 'archive-manifest.json'
        mf_raw = read(mf_path)
        require(sha(mf_raw) == closure['archive_manifest_sha256'], 'Section archive manifest drifted')
        require(checked_section['archive_manifest'] == {'path': str(mf_path), 'bytes': len(mf_raw), 'sha256': sha(mf_raw)}, 'Context archive manifest ref differs')
        manifest = json.loads(mf_raw)
        paths = {archive + '/' + relative(name): read(ROOT / archive / relative(name)) for name in manifest}
        for name, metadata in manifest.items():
            raw = paths[archive + '/' + name]
            require(len(raw) == metadata['bytes'] and sha(raw) == metadata['sha256'], 'Frozen section archive payload drifted')
        paths[archive + '/archive-manifest.json'] = mf_raw
        physical = physical_files(ROOT / archive)
        require(physical == set(paths) and type(closure['archive_files']) is int and closure['archive_files'] == len(physical),
                'Exact regular frozen section payload/count differs')
        require(sha(read(ROOT / archive / Path(bindings[section['source_role']]['source_path']).name)) ==
                bindings[section['source_role']]['sha256'], 'Actual completed guard was not preserved in exact section archive')
        index(paths, archive)
        section_files.update(paths)
        section_files[relative(Path(bindings[section['receipt_role']]['source_path']).relative_to(ROOT).as_posix())] = raw_by_role[section['receipt_role']]
        require(guard['passed'] is True and guard['current_maintained'] == len(guard['source_sha256_after']), 'Section snapshot malformed')
    require(decoded[spec['sections'][-1]['source_role']] == source, 'Full95 must use actually accepted95 source snapshot')

    for info in spec['public_packets']:
        require(info['public'] is True, 'Public packet qualification required')
        raw = read(info['manifest_path'])
        require(sha(raw) == info['manifest_sha256'], 'Explicit public manifest SHA differs')
        packet = json.loads(raw)
        style = info['style']
        if style == 'source_archive_rows':
            rows = packet['files']
        elif style == 'local_artifact_dict':
            rows = [{'source_path': str(Path(info['manifest_path']).parent / name), 'archive_path': name, **metadata}
                    for name, metadata in packet['artifacts'].items()]
        elif style == 'payload_file_rows':
            rows = [{'source_path': item['path'], 'archive_path': item['name'], 'bytes': item['bytes'], 'sha256': item['sha256']}
                    for item in packet['payload_files']]
        elif style == 'payload_ref_rows':
            # The announced regression sealer emits flat file_ref rows without
            # a name field; its actual source fixes this separate schema.
            rows = [{'source_path': item['path'], 'archive_path': Path(item['path']).name,
                     'bytes': item['bytes'], 'sha256': item['sha256']} for item in packet['payload_files']]
        else:
            raise ValueError('Only an explicitly selected qualified packet schema is supported')
        require(len(rows) == info['payload_count'], 'Explicit packet row count differs')
        require(info['numbered_section_completed'] is False, 'Public source packet is not a completed section')
        prefix = relative(info['archive_prefix'])
        for row in rows:
            data = read(row['source_path'])
            require(len(data) == row['bytes'] and sha(data) == row['sha256'], 'Public packet payload differs')
            add(prefix + '/' + relative(row['archive_path']), data, row['source_path'])
        add(prefix + '/' + Path(info['manifest_path']).name, raw, info['manifest_path'])
    require(spec['public_packets'], 'Bound final runtime/context/UI source and formal packets required')
    # The completed context's exact source runner/binding and UI final runner
    # must each occur in an explicitly sealed public packet, not just an unsealed
    # loose file role. The actual final/formal manifests are root supplied later.
    sealed_refs = set()
    for info in spec['public_packets']:
        packet = json.loads(read(info['manifest_path']))
        if info['style'] == 'source_archive_rows':
            sealed_refs.update((row['source_path'], row['sha256']) for row in packet['files'])
        elif info['style'] == 'local_artifact_dict':
            sealed_refs.update((str(Path(info['manifest_path']).parent / name), row['sha256'])
                               for name, row in packet['artifacts'].items())
        elif info['style'] == 'payload_file_rows':
            sealed_refs.update((row['path'], row['sha256']) for row in packet['payload_files'])
        elif info['style'] == 'payload_ref_rows':
            sealed_refs.update((row['path'], row['sha256']) for row in packet['payload_files'])
    for role in ('context_final_runner', 'context_source_binding', 'ui_final_runner'):
        require((bindings[role]['source_path'], bindings[role]['sha256']) in sealed_refs,
                'Actual final source role lacks a sealed public packet: ' + role)
    existing = dict(section_files)
    for item in spec['batch_product_and_metadata_files']:
        name = relative(item['path'])
        require(name not in DOCS and name not in existing and not name.startswith(PREFIX + '/'), 'Batch path collision')
        raw = read(ROOT / name)
        require(len(raw) == item['bytes'] and sha(raw) == item['sha256'], 'Explicit batch product/metadata bytes differ')
        existing[name] = raw
    require(spec['batch_product_and_metadata_files'], 'Actual product/metadata delta must be named explicitly')
    cp = json.loads(read(ROOT / DOCS[0]))
    require(cp['completed_sections'] == 95 and cp['next_section'] == 96
            and cp['full_validation_due'] is True, 'Only actual completed95 may receive full095 closure')
    require(cp['policy']['commit_after_each_section'] is False and cp['policy']['commit_interval'] == 5
            and cp['policy']['push_after_batch_commit'] is True, 'Wrong user batch-save cadence')
    require(cp['pending_batch_sections'] == [93, 94, 95], 'Wrong actual pending batch, never count96')
    require(type(spec['next_action']) is str and spec['next_action'].strip(), 'Concrete next96 action required')
    return payload, origins, source, available, final, contracts, existing, cp


def documents(cp, final, contracts, bindings, next_action):
    c = contracts['context']
    summary = ('第95节后fresh全量可用检验通过；Linux与Wine full/selected/pip及实际完整窗口均由本轮新运行产生，'
               '源码零漂移，缺失/私人记录保留为unavailable，不计通过；Wine不是原生Windows/game/desktop认证。'
               '93原Wine shell状态仍不可得；本轮不倒填。95资料报告已随本轮源码验收，96尚未开始。'
               '本组93–95准备统一commit并推送当前开发分支，尚无提交SHA或推送成功声明。')
    cp.update(full_validation_due=False, next_section=96, next_action=next_action)
    cp['last_full_validation'] = {'after_section': 95, 'completed_at': pointer(final, c['completed_at']),
        'completion_ref': 'working-tree-full-095', 'completion_ref_is_Git_tag': False,
        'actual_base_HEAD_before_batch_commit': HEAD92, 'source_snapshot_sha256': bindings['source095_guard']['sha256'],
        'linux': PREFIX + '/' + bindings['linux_full']['archive_path'],
        'wine': PREFIX + '/' + bindings['wine_full']['archive_path'],
        'ui': PREFIX + '/' + bindings['ui_receipt']['archive_path'],
        'complete_repository_validation': pointer(final, c['complete_repository']),
        'complete_ui_validation': True, 'fresh_selected_executed_linux_and_wine': True,
        'selected_reuse_performed': False, 'native_windows_verified': False,
        'archive_state': 'verified_index_collective_save_ready_NOT_COMMITTED_OR_PUSHED'}
    cp['pending_batch_save'].update(status='full_PASS_collective_save_ready_NOT_COMMITTED_OR_PUSHED',
        full_validation_after=95, destination='origin codex/p2-development', committed=False, pushed=False,
        actual_commit_sha=None, actual_push_sha=None,
        post_publication_closure='External receipt only; next96 may reference actual batch commit')
    cp['wine_validation'] = summary
    result = {DOCS[0]: encode(cp)}
    for name in DOCS[1:]:
        raw = read(ROOT / name)
        old = raw.decode().replace('\r\n', '\n')
        addition = summary + '\n下一步：' + next_action + '\n'
        text = old + '\n## 第95节后全量可用检验\n\n' + addition if name == DOCS[3] else '# 第95节后全量可用检验与云端保存准备\n\n' + addition + '\n---\n\n' + old
        result[name] = (text.replace('\n', '\r\n') if b'\r\n' in raw else text).encode()
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('phase', choices=('preflight', 'archive', 'prepare-save'))
    p.add_argument('--spec', type=Path, required=True)
    p.add_argument('--execute', action='store_true')
    for name in ('formal-review', 'formal-sha256', 'formal-pass-pointer', 'formal-runtime-pointer',
                 'formal-helper-pointer', 'formal-spec-pointer'):
        p.add_argument('--' + name, required=True)
    args = p.parse_args()
    spec_raw = read(args.spec)
    spec = json.loads(spec_raw)
    formal_sha = formal_gate(args, spec_raw)
    payload, origins, source, available, final, contracts, existing, cp = collect(spec)
    # This file is itself public source evidence, explicitly included without importing it.
    payload['archive-source/archive_full095.py'] = read(Path(__file__).resolve())
    origins['archive-source/archive_full095.py'] = str(Path(__file__).resolve())
    payload['archive-source/actual-archive-spec095.json'] = spec_raw
    origins['archive-source/actual-archive-spec095.json'] = str(args.spec)
    payload['archive-source/actual-formal-review095.json'] = read(args.formal_review)
    origins['archive-source/actual-formal-review095.json'] = str(args.formal_review)
    source_gate(source)
    base = ROOT / PREFIX
    if args.phase == 'preflight':
        require(not args.execute, 'Preflight never writes')
        require(not base.exists(), 'Existing partial/completed full095 archive requires explicit recovery')
        print(json.dumps({'source_only_preflight': True, 'actual_full_inputs_checked': True,
                          'planned_public_payloads': len(payload), 'mutations': 0, 'commit_or_push': False}))
        return
    require(args.execute, 'Root must select execute after actual fullPASS and formal review')
    if args.phase == 'archive':
        require(not base.exists(), 'Never overwrite partial/completed archive')
        output = Path(spec['archive_closure_output'])
        require(output.parent == LOCAL and not output.exists(), 'New external archive closure required')
        staged = {v.decode() for v in git('diff', '--cached', '--name-only', '-z').split(b'\0') if v}
        require(staged <= set(existing), 'Unexpected staged path before archive')
        for name, raw in payload.items():
            new(base / relative(name), raw)
        paths = {PREFIX + '/' + name: raw for name, raw in payload.items()}
        stage(paths)
        index(paths, PREFIX)
        source_gate(source)
        closure = {'format_version': 1, 'passed': True, 'actual_base_HEAD': HEAD92,
                   'payload_index_exact': True, 'payload_count': len(paths),
                   'excluded_self_and_final_manifest': ['git-index-payload-closure.json', 'archive-manifest.json'],
                   'commit_performed': False, 'push_performed': False}
        raw = encode(closure)
        new(base / 'git-index-payload-closure.json', raw)
        payload['git-index-payload-closure.json'] = raw
        origins['git-index-payload-closure.json'] = 'generated after actual archive payload index verification'
        manifest = {'format_version': 1, 'section': 95, 'actual_base_HEAD': HEAD92,
                    'files': [{'source_path': str(base / name), 'archive_path': name,
                               'bytes': len(data), 'sha256': sha(data), 'original_source_path': origins[name]}
                              for name, data in sorted(payload.items())]}
        raw = encode(manifest)
        new(base / 'archive-manifest.json', raw)
        paths = {PREFIX + '/' + name: data for name, data in payload.items()}
        paths[PREFIX + '/archive-manifest.json'] = raw
        stage(paths)
        index(paths, PREFIX)
        authored = [PREFIX + '/' + name for name in ('archive-source/archive_full095.py',
            'archive-source/actual-archive-spec095.json', 'archive-source/actual-formal-review095.json',
            'git-index-payload-closure.json', 'archive-manifest.json')]
        git('-c', 'core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol',
            'diff', '--cached', '--check', '--', *authored)
        source_gate(source)
        new(output, encode({'format_version': 1, 'section': 95, 'passed': True,
            'actual_base_HEAD': HEAD92, 'status': 'FULL095_ARCHIVE_INDEX_VERIFIED_NOT_COMMITTED_OR_PUSHED',
            'archive_manifest_sha256': sha(raw), 'source_guard_sha256': spec['bindings']['source095_guard']['sha256'],
            'archive_files': len(paths), 'formal_review_sha256': formal_sha,
            'files': {name: {'bytes': len(data), 'sha256': sha(data)} for name, data in paths.items()}}))
        print(json.dumps({'archive_index_verified': True, 'files': len(paths), 'checkpoint_changed': False,
                          'commit_performed': False, 'push_performed': False}))
        return
    # All archive/index gates precede checkpoint completion and batch preparation.
    archived = json.loads(read(spec['archive_closure_output']))
    require(archived['passed'] is True and archived['actual_base_HEAD'] == HEAD92
            and archived['status'] == 'FULL095_ARCHIVE_INDEX_VERIFIED_NOT_COMMITTED_OR_PUSHED'
            and archived['source_guard_sha256'] == spec['bindings']['source095_guard']['sha256'], 'Actual archive closure differs')
    manifest_raw = read(base / 'archive-manifest.json')
    require(sha(manifest_raw) == archived['archive_manifest_sha256'], 'Full095 manifest changed')
    manifest = json.loads(manifest_raw)
    require(manifest['format_version'] == 1 and manifest['section'] == 95 and manifest['actual_base_HEAD'] == HEAD92,
            'Actual full095 archive manifest scope differs')
    manifest_paths = set()
    for row in manifest['files']:
        name = relative(row['archive_path'])
        require(name != 'archive-manifest.json' and PREFIX + '/' + name not in manifest_paths and
                row['source_path'] == str(base / name), 'Full095 manifest member/path must be unique and exact')
        repo_name = PREFIX + '/' + name
        require(archived['files'].get(repo_name) == {'bytes': row['bytes'], 'sha256': row['sha256']},
                'Full095 closure and physical manifest payload metadata differ')
        manifest_paths.add(repo_name)
    manifest_paths.add(PREFIX + '/archive-manifest.json')
    require(set(archived['files']) == manifest_paths and physical_files(base) == manifest_paths and
            type(archived['archive_files']) is int and archived['archive_files'] == len(manifest_paths),
            'Full095 closure count and exact physical set must match manifest before metadata writes')
    paths = {name: read(ROOT / name) for name in archived['files']}
    for name, raw in paths.items():
        require(archived['files'][name] == {'bytes': len(raw), 'sha256': sha(raw)}, 'Full095 archived file changed')
    indexed_payload = json.loads(paths[PREFIX + '/git-index-payload-closure.json'])
    require(indexed_payload['passed'] is True and indexed_payload['actual_base_HEAD'] == HEAD92 and
            indexed_payload['payload_index_exact'] is True and indexed_payload['payload_count'] == len(paths) - 2 and
            indexed_payload['excluded_self_and_final_manifest'] == ['git-index-payload-closure.json', 'archive-manifest.json'] and
            indexed_payload['commit_performed'] is indexed_payload['push_performed'] is False,
            'Generated full095 payload index closure/count cannot invent publication')
    index(paths, PREFIX)
    source_gate(source)
    output = Path(spec['batch_save_ready_output'])
    require(output.parent == LOCAL and not output.exists(), 'New external batch ready receipt required')
    require(type(spec['batch_commit_message']) is str and spec['batch_commit_message'], 'Concrete batch commit message required')
    docs = documents(cp, final, contracts, spec['bindings'], spec['next_action'])
    expected = {**existing, **paths, **docs}
    for name, raw in docs.items():
        (ROOT / name).write_bytes(raw)
    stage(expected)
    index(expected)
    git('-c', 'core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol',
        'diff', '--cached', '--check', '--', *DOCS, *[row['path'] for row in spec['batch_product_and_metadata_files']])
    source_gate(source)
    # All tracked/unignored changes must be named; ignored public archive leaves
    # are already included in exact index checks. Do not use git add .
    dirty = {v.decode() for v in git('diff', 'HEAD', '--name-only', '-z').split(b'\0') if v}
    others = {v.decode() for v in git('ls-files', '--others', '--exclude-standard', '-z').split(b'\0') if v}
    require(dirty == set(expected) and not others, 'Unreviewed tracked or unignored batch path remains')
    ready = {'format_version': 1, 'section': 95, 'status': 'FULL095_COLLECTIVE_SAVE_READY_NOT_COMMITTED_OR_PUSHED',
             'actual_parent_HEAD': HEAD92, 'branch': BRANCH, 'destination': 'origin refs/heads/' + BRANCH,
             'commit_performed': False, 'push_performed': False, 'actual_commit_sha': None, 'actual_push_sha': None,
             'source_guard_path': spec['bindings']['source095_guard']['source_path'],
             'source_guard_sha256': spec['bindings']['source095_guard']['sha256'],
             'archive_manifest_sha256': sha(manifest_raw), 'actual_source_sha256': source['source_sha256_after'],
             'files': {name: {'bytes': len(raw), 'sha256': sha(raw)} for name, raw in sorted(expected.items())},
             'fresh_remote_read_required_before_publication': True,
             'normal_push_only': True, 'tag_required': False,
             'commit_command_argv': ['git', 'commit', '-m', spec['batch_commit_message']],
             'push_command_argv': ['git', 'push', '-u', 'origin', 'HEAD:refs/heads/' + BRANCH],
             'record_actual_commit_and_push_exits_then_remote_equality_externally': True,
             'completed_at': datetime.now(timezone.utc).isoformat()}
    new(output, encode(ready))
    print(json.dumps({'fullPASS_and_index_verified': True, 'next_section': 96,
                      'next_section_completed': False, 'ready_for_commit_and_push': True,
                      'commit_performed': False, 'push_performed': False}))


if __name__ == '__main__':
    main()
