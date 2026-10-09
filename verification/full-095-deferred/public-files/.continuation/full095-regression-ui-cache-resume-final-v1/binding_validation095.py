"""Pure standard-library source/receipt binding; never import project code."""
import ast
import hashlib
import json
import re
import stat
import subprocess
from pathlib import Path, PureWindowsPath

CLASSIFIER_SHA256 = 'ea4481c9cd95fb9438f673b76c14c9386263469e12b2855fa04e9a47d7c63dcc'
EXPECTED_BRANCH = 'codex/p2-development'
WINE_WRAPPER_SHA256 = '65dd3806511e037290291ac592246abe80f346b1004b88c81e798612db4d79c8'
EXECUTION_NAMES = ('linux_full', 'wine_full', 'linux_selected', 'wine_selected',
                   'linux_pip', 'wine_pip', 'wine_ui', 'saved_review')
OUTPUT_NAMES = {
    'context_start': '/workspace/.compat/wine-validation-095-context.json',
    'context_final': '/workspace/.compat/wine-validation-095-context-final.json',
    'linux_full': '/workspace/.continuation/linux-full-095.json',
    'wine_full': '/workspace/.compat/wine-available-full-095.json',
    'linux_full_log': '/workspace/.continuation/linux-full-095.log',
    'wine_full_log': '/workspace/.compat/wine-available-full-095.log',
    'linux_full_console': '/workspace/.continuation/linux-full-095-console.log',
    'wine_full_console': '/workspace/.compat/wine-available-full-095-console.log',
    'linux_selected': '/workspace/.continuation/selected-095.log',
    'wine_selected': '/workspace/.compat/wine-cloud-095.log',
    'linux_pip': '/workspace/.continuation/linux-pipcheck-095.log',
    'wine_pip': '/workspace/.compat/wine-pipcheck-095.log',
    'execution_witness': '/workspace/.continuation/root-full095-primary-exits.json',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def is_digest(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def source_map(value):
    require(isinstance(value, dict) and value, 'Nonempty actual source map required')
    for name, value_hash in value.items():
        require(isinstance(name, str) and name and not Path(name).is_absolute()
                and '..' not in Path(name).parts and is_digest(value_hash),
                'Actual source names/digests must be safe nonnull strings')
    return value


def canonical_file(path):
    require(isinstance(path, str) and path and Path(path).is_absolute()
            and '..' not in Path(path).parts, 'Actual Linux absolute file path required')
    return str(Path(path).resolve(strict=False))


def bound_bytes(reference):
    require(isinstance(reference, dict), 'File reference must be an object')
    require({'path', 'bytes', 'sha256'} <= set(reference),
            'Actual file binding must include path, exact bytes and SHA256')
    path = Path(reference['path'])
    require(is_digest(reference['sha256']), 'Exact file SHA256 must be a real digest string')
    require(path.is_absolute() and path.is_file(), f'Actual file absent: {path}')
    require(not path.is_symlink(), f'Actual binding cannot be a symlink: {path}')
    data = path.read_bytes()
    require(digest(data) == reference['sha256'], f'Exact SHA256 mismatch: {path}')
    require(type(reference['bytes']) is int and reference['bytes'] >= 0
            and len(data) == reference['bytes'], f'Exact byte count mismatch: {path}')
    return data


def file_ref(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': digest(data)}


def bound_json(reference):
    return json.loads(bound_bytes(reference))


def pointer(value, expression):
    require(isinstance(expression, str) and expression.startswith('/'),
            'Nonempty JSON pointer required')
    for token in expression[1:].split('/'):
        token = token.replace('~1', '/').replace('~0', '~')
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def maintained_hashes(root):
    root = Path(root)
    return {p.relative_to(root).as_posix(): digest(p.read_bytes())
            for folder in ('rouge', 'tests', 'scripts')
            for p in sorted((root / folder).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}


def classifier_hashes(root):
    """Exact frozen classifier selector; this does not invoke its helper."""
    root = Path(root)
    files = [*root.glob('rouge/**/*.py'), *root.glob('rouge/data/**/*.json'),
             *root.glob('tests/test_*.py'), root / 'scripts/verify_full_available.py']
    return {p.relative_to(root).as_posix(): digest(p.read_bytes())
            for p in sorted(set(files))}


def assigned_literal(source, name):
    tree = ast.parse(source)
    matches = [n for n in tree.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    require(len(matches) == 1, f'Exact literal assignment not found: {name}')
    return ast.literal_eval(matches[0].value)


def selectors_from_source(root):
    root = Path(root)
    historical = json.loads((root / 'CORE_0.70_VERIFICATION.json').read_bytes())['test_modules']
    extra = assigned_literal((root / 'scripts/verify_full_available.py').read_text(), 'NEW_MODULES')
    selected = assigned_literal((root / 'scripts/verify_cloud.py').read_text(), 'MODULES')
    require(all(isinstance(x, str) for x in (*historical, *extra, *selected)),
            'Selector entries must be literal strings')
    return list(dict.fromkeys(historical + list(extra) + list(selected))), list(selected)


def git_output(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def archive_binding(root, receipt, closure, guard_reference):
    require(not Path(receipt['research_archive']).is_absolute()
            and '..' not in Path(receipt['research_archive']).parts,
            'Unsafe section archive path')
    archive = root / receipt['research_archive']
    require(archive.is_relative_to(root) and archive.is_dir() and not archive.is_symlink(),
            'Public section archive absent or symlinked')
    for parent in archive.parents:
        if parent == root:
            break
        require(not parent.is_symlink(), 'Public archive ancestor cannot be symlinked')
    manifest_path = archive / 'archive-manifest.json'
    manifest_bytes = manifest_path.read_bytes()
    require(digest(manifest_bytes) == closure['archive_manifest_sha256'],
            'Completed archive manifest differs from actual closure')
    manifest = json.loads(manifest_bytes)
    require(isinstance(manifest, dict) and manifest, 'Section archive manifest schema differs')
    require(all(isinstance(name, str) and name not in ('', '.', 'archive-manifest.json')
                and not Path(name).is_absolute() and '..' not in Path(name).parts
                and Path(name).as_posix() == name for name in manifest),
            'Archive manifest members must be canonical safe relative paths excluding the manifest itself')
    physical = set()
    for path in archive.rglob('*'):
        mode = path.lstat().st_mode
        require(not stat.S_ISLNK(mode), f'Archive symlink entry forbidden: {path}')
        require(stat.S_ISDIR(mode) or stat.S_ISREG(mode),
                f'Archive nonregular entry forbidden: {path}')
        if stat.S_ISREG(mode):
            physical.add(path.relative_to(archive).as_posix())
    expected_physical = set(manifest) | {'archive-manifest.json'}
    require(physical == expected_physical, 'Actual physical archive files differ from exact manifest set')
    require(type(closure['archive_files']) is int
            and closure['archive_files'] == len(expected_physical),
            'Completed archive closure file count differs from physical manifest set')
    names = set()
    for relative, expected in manifest.items():
        require(not Path(relative).is_absolute() and '..' not in Path(relative).parts,
                'Unsafe archive member path')
        path = archive / relative
        require(path.is_relative_to(archive) and not path.is_symlink(), 'Unsafe archive member')
        data = path.read_bytes()
        require(type(expected['bytes']) is int and expected['bytes'] >= 0
                and is_digest(expected['sha256'])
                and len(data) == expected['bytes'] and digest(data) == expected['sha256'],
                f'Completed archive payload changed: {path}')
        names.add(path.relative_to(root).as_posix())
    names.add(manifest_path.relative_to(root).as_posix())
    staged = {}
    for item in git_output(root, 'ls-files', '--stage', '-z', '--', archive.relative_to(root).as_posix()).split(b'\0'):
        if item:
            header, name = item.split(b'\t', 1)
            mode, blob, stage = header.decode().split()
            require(stage == '0' and mode in ('100644', '100755'), 'Archive index contains conflict/unsupported mode')
            staged[name.decode()] = blob
    require(set(staged) == names, 'Actual section archive index is not the exact completed set')
    for name in names:
        data = (root / name).read_bytes()
        expected_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(staged[name] == expected_blob, f'Actual archive index bytes differ: {name}')
    archived_guard = archive / Path(guard_reference['path']).name
    require(digest(archived_guard.read_bytes()) == guard_reference['sha256'],
            'Exact completed guard was not preserved in the section archive')
    return file_ref(manifest_path), [str(archive / name) for name in sorted(physical)]


def wine_mapping(spec):
    mapping = spec['wine_path_mapping']
    require(mapping['drive'] == 'Z:' and mapping['prefix'] == '/workspace/.compat/wine-prefix'
            and mapping['drive_link'] == '/workspace/.compat/wine-prefix/dosdevices/z:',
            'Configured Wine drive/prefix must match the exact bound wrapper')
    link = Path(mapping['drive_link'])
    require(link.is_symlink(), 'Actual configured Wine Z drive symlink absent')
    actual_target = canonical_file(str(link.resolve(strict=True)))
    require(actual_target == canonical_file(mapping['linux_root']),
            'Declared Wine mapping differs from actual configured drive target')
    proof = bound_json(mapping['proof'])
    require(pointer(proof, mapping['proof_pointers']['drive_link']) == mapping['drive_link']
            and pointer(proof, mapping['proof_pointers']['linux_target']) == actual_target
            and pointer(proof, mapping['proof_pointers']['wrapper_sha256']) == WINE_WRAPPER_SHA256,
            'Root mapping metadata does not bind the actual drive target and wrapper source')
    return {'drive': 'Z:', 'linux_root': actual_target,
            'drive_link': mapping['drive_link'], 'proof': mapping['proof']}


def wine_argument_path(value, mapping):
    require(isinstance(value, str), 'Actual Wine path argument must be a string')
    windows_path = PureWindowsPath(value)
    require(windows_path.drive == mapping['drive'] and windows_path.root == '\\'
            and '..' not in windows_path.parts,
            'Wine file argument must use the real source-bound absolute Z drive')
    return canonical_file(str(Path(mapping['linux_root']).joinpath(*windows_path.parts[1:])))


def wine_argument_for(linux_path, mapping):
    target = Path(canonical_file(linux_path))
    base = Path(mapping['linux_root'])
    require(target.is_relative_to(base), 'Linux file is outside the actual configured Wine drive')
    return str(PureWindowsPath(mapping['drive'] + '\\').joinpath(*target.relative_to(base).parts))


def exact_source_review(reference, pointers, runner_reference, argv=None, keys=None):
    review = bound_json(reference)
    require(pointer(review, pointers['source_pass']) is True
            and pointer(review, pointers['runtime_pass']) is False
            and pointer(review, pointers['runner_sha256']) == runner_reference['sha256'],
            'Actual future FINAL source review must pass and bind exact runner source, without runtime claim')
    if argv is not None:
        require(pointer(review, pointers['argv']) == argv,
                'Actual future FINAL source review does not bind exact executable/script/full CLI')
    if keys is not None:
        require(pointer(review, pointers['source_keys']) == keys,
                'Actual future FINAL source review does not bind exact UI own source selector keys')


def execution_plan(spec, root, mapping):
    python_entry = spec['linux_python_entry']
    require(python_entry == str(root / '.venv/bin/python') and Path(python_entry).is_file(),
            'Configured Linux Python entry differs from the reviewed cloud entry')
    wrapper = spec['wine_wrapper']['path']
    exit_paths = spec['io_plan']['exit_code_paths']
    require(set(exit_paths) == set(EXECUTION_NAMES), 'Eight unique actual primary status paths required')
    full = file_ref(root / 'scripts/verify_full_available.py')
    selected = file_ref(root / 'scripts/verify_cloud.py')
    fixed = {
        'linux_full': [python_entry, full['path'], '--output', OUTPUT_NAMES['linux_full']],
        'wine_full': [wrapper, wine_argument_for(full['path'], mapping), '--wine', '--output',
                      wine_argument_for(OUTPUT_NAMES['wine_full'], mapping)],
        'linux_selected': [python_entry, selected['path']],
        'wine_selected': [wrapper, wine_argument_for(selected['path'], mapping)],
        'linux_pip': [python_entry, '-m', 'pip', 'check'],
        'wine_pip': [wrapper, '-m', 'pip', 'check'],
    }
    stdout_keys = {'linux_full': 'linux_full_console', 'wine_full': 'wine_full_console',
                   'linux_selected': 'linux_selected', 'wine_selected': 'wine_selected',
                   'linux_pip': 'linux_pip', 'wine_pip': 'wine_pip',
                   'wine_ui': 'wine_ui_console', 'saved_review': 'saved_review_stdout'}
    plan = {}
    for name in EXECUTION_NAMES:
        if name in fixed:
            argv = fixed[name]
            runner = None if name.endswith('_pip') else (full if name.endswith('_full') else selected)
        else:
            owner = spec['ui'] if name == 'wine_ui' else spec['saved_review']
            runner = file_ref(owner['runner']['path'])
            bound_bytes(owner['runner'])
            contract = owner['execution_contract']
            argv = contract['argv']
            require(isinstance(argv, list) and len(argv) >= 2 and all(isinstance(x, str) for x in argv),
                    'Actual FINAL UI/saved-review full CLI remains unbound')
            expected_entry = wrapper if name == 'wine_ui' else python_entry
            require(argv[0] == expected_entry, 'Actual future CLI executable prefix differs')
            selected_script = wine_argument_path(argv[1], mapping) if name == 'wine_ui' else canonical_file(argv[1])
            require(selected_script == canonical_file(runner['path']),
                    'Actual Python script must be the executed argv[1] entry, not a later incidental argument')
            require(contract['cwd'] == str(root) and contract['script_arg_index'] == 1,
                    'Actual future source-qualified cwd/script entry position differs')
            exact_source_review(contract['source_review'], contract['review_pointers'], runner, argv=argv)
        plan[name] = {'argv': argv, 'cwd': str(root), 'runner': runner,
                      'entry_kind': 'python-module' if name.endswith('_pip') else 'python-script',
                      'script_arg_index': None if name.endswith('_pip') else 1,
                      'stdout_key': stdout_keys[name], 'exit_code_path': exit_paths[name]}
    return plan


def global_output_plan(spec, immutable_input_paths, extra_immutable_paths=()):
    outputs = dict(OUTPUT_NAMES)
    outputs.update(wine_ui=spec['ui']['receipt_path'], wine_ui_console=spec['ui']['console_log_path'],
                   saved_review_receipt=spec['saved_review']['receipt_path'],
                   saved_review_stdout=spec['saved_review']['stdout_log_path'],
                   visual_review=spec['io_plan']['visual_review_path'],
                   ui_extra_acceptance=spec['io_plan']['ui_extra_acceptance_path'])
    for name in EXECUTION_NAMES:
        outputs[name + '_exit_code'] = spec['io_plan']['exit_code_paths'][name]
    for index, row in enumerate(spec['ui']['required_saved_outputs']):
        outputs[f'ui_saved_output_{index}'] = row['path']
    for index, path in enumerate(spec['ui']['optional_output_paths']):
        outputs[f'ui_optional_output_{index}'] = path
    canonical = {name: canonical_file(path) for name, path in outputs.items()}
    require(len(set(canonical.values())) == len(canonical),
            'Canonical global fixed/UI/native/PNG/status/review/context output paths must be disjoint')
    require(all(not Path(other).is_relative_to(Path(path))
                for name, path in canonical.items() for other_name, other in canonical.items()
                if name != other_name), 'Output file sinks cannot be ancestors of other output file sinks')
    inputs = {canonical_file(path) for path in (*immutable_input_paths, *extra_immutable_paths)}
    require(not inputs.intersection(canonical.values()),
            'Canonical output path aliases an immutable source/receipt/archive/contract input')
    for path in canonical.values():
        require(not any(Path(other).is_relative_to(Path(path)) for other in inputs),
                'Output file path cannot be an ancestor of an immutable input')
    directories = [canonical_file(path) for path in spec['ui']['fresh_evidence_directories']]
    require(len(set(directories)) == len(directories)
            and all(not Path(other).is_relative_to(Path(path))
                    for index, path in enumerate(directories) for other_index, other in enumerate(directories)
                    if index != other_index), 'Fresh native evidence namespaces must be canonically disjoint')
    for directory in directories:
        require(not any(Path(path).is_relative_to(Path(directory))
                        or Path(directory).is_relative_to(Path(path)) for path in inputs),
                'Fresh native evidence namespace overlaps an immutable input path')
        for name, output in canonical.items():
            require(not Path(directory).is_relative_to(Path(output)),
                    'Output file sink cannot contain a fresh native evidence namespace')
            if not name.startswith(('ui_saved_output_', 'ui_optional_output_')):
                require(not Path(output).is_relative_to(Path(directory)),
                        'Fresh native namespace cannot contain context/status/log/review sinks')
    return {'paths': outputs, 'canonical_paths': canonical,
            'immutable_input_paths': sorted(inputs), 'fresh_evidence_directories': directories}


def validate_actual_inputs(spec, extra_immutable_paths=()):
    """Root executes this only when real 93/94/95 completions exist."""
    require(spec.get('format_version') == 2 and spec.get('section') == 95,
            'Actual binding spec must be format 2 / section 95')
    root = Path(spec['repo'])
    require(root == Path('/workspace/rougezhushou'), 'Unexpected repository')
    branch = git_output(root, 'branch', '--show-current').decode().strip()
    head = git_output(root, 'rev-parse', 'HEAD').decode().strip()
    require(branch == EXPECTED_BRANCH, 'Actual development branch differs')
    require(head == spec['actual_base_HEAD'], 'HEAD changed before full PASS; do not create a prerequisite commit')
    chain = spec['completed_working_tree_chain']
    require([row['section'] for row in chain] == [93, 94, 95],
            'Exact root-completed 93/94/95 working-tree chain required')
    observed = []
    refs = []
    archive_inputs = []
    for row in chain:
        n = row['section']
        receipt = bound_json(row['receipt'])
        closure = bound_json(row['closure'])
        guard = bound_json(row['source_guard'])
        source_map(guard['source_sha256_after'])
        require(receipt['section'] == n and receipt.get('passed') is True
                and receipt.get('workflow_complete') is True
                and receipt.get('actual_window_verified_by_root') is True,
                f'Section {n} is not an actual completed root workflow')
        require(receipt.get('completion_ref_is_Git_tag') is False
                and receipt.get('commit_status') == 'pending_next_fifth_section_full_PASS',
                f'Section {n} completion must describe its real uncommitted source snapshot')
        require(closure['section'] == n
                and closure['status'] == 'VERIFIED_ARCHIVED_NOT_COMMITTED_OR_PUSHED'
                and closure['all_archive_index_blobs_exact'] is True
                and closure['actual_HEAD_unchanged'] == head,
                f'Section {n} archived working-tree closure is incomplete')
        require(closure['source_snapshot_sha256'] == row['source_guard']['sha256'],
                f'Section {n} closure does not bind supplied actual source guard')
        require(guard.get('passed') is True and isinstance(guard['source_sha256_after'], dict)
                and guard['current_maintained'] == len(guard['source_sha256_after'])
                and receipt['maintained_source_files'] == len(guard['source_sha256_after']),
                f'Section {n} guard/receipt source scope differs')
        archive_ref, archive_paths = archive_binding(root, receipt, closure, row['source_guard'])
        archive_inputs.extend(archive_paths)
        refs.extend([row['receipt'], row['closure'], row['source_guard'], archive_ref])
        observed.append({'section': n, 'receipt': row['receipt'], 'closure': row['closure'],
                         'source_guard': row['source_guard'], 'archive_manifest': archive_ref,
                         'source_files': len(guard['source_sha256_after'])})
    guard95 = bound_json(chain[-1]['source_guard'])
    current = maintained_hashes(root)
    require(current == guard95['source_sha256_after'], 'Actual95 maintained source bytes changed')
    classifier = root / 'scripts/verify_full_available.py'
    require(digest(classifier.read_bytes()) == CLASSIFIER_SHA256,
            'Frozen available classification script changed; new classification needs independent review')
    require(current['scripts/verify_full_available.py'] == CLASSIFIER_SHA256,
            'Actual95 guard does not bind exact original classifier')
    cp = json.loads((root / 'DEVELOPMENT_CHECKPOINT.json').read_bytes())
    refs.append(file_ref(root / 'DEVELOPMENT_CHECKPOINT.json'))
    require(cp['completed_sections'] == 95 and cp['full_validation_due'] is True,
            'Full095 may start only after focused95 completion and before its full closure')
    require(cp['policy']['commit_after_each_section'] is False and cp['policy']['commit_interval'] == 5
            and cp['pending_batch_save']['commit_and_push_after_full_PASS'] is True,
            'Latest five-section commit/push policy differs')
    ui = spec['ui']
    require(Path(ui['receipt_path']).is_absolute(), 'Exact future actualUI receipt path required')
    require(ui['receipt_path'] == '/workspace/.compat/wine-ui-095.json',
            'Planned UI095 sink differs; root must review/update source packet explicitly')
    require(set(ui['pointers']) == {'passed', 'complete', 'checks', 'drift', 'source_before', 'source_after'},
            'UI field pointers must be supplied from the actual sealed runner')
    require(all(isinstance(v, str) and v.startswith('/') for v in ui['pointers'].values()),
            'Real finalUI field pointers required')
    saved_outputs = ui['required_saved_outputs']
    require(isinstance(saved_outputs, list) and saved_outputs
            and {'native-evidence', 'screenshot'} <= {row['kind'] for row in saved_outputs},
            'Root must declare actual finalUI native evidence and screenshot sinks')
    require(all(row['kind'] in ('native-evidence', 'screenshot')
                and Path(row['path']).is_absolute() for row in saved_outputs),
            'Exact public native/screenshot output paths required')
    require(len({row['path'] for row in saved_outputs}) == len(saved_outputs),
            'Planned actualUI evidence sink paths must be unique')
    require(isinstance(ui['optional_output_paths'], list)
            and all(isinstance(path, str) for path in ui['optional_output_paths']),
            'Exact optional native/failure/difference output file paths required')
    require(isinstance(ui['fresh_evidence_directories'], list)
            and all(isinstance(path, str) for path in ui['fresh_evidence_directories']),
            'Real FINAL native evidence namespace list required; empty if all files are declared')
    ui_runner = bound_bytes(ui['runner'])
    ui_tree = ast.parse(ui_runner)
    pending_assignments = [node for node in ui_tree.body if isinstance(node, ast.Assign)
                           and any(isinstance(target, ast.Name) and target.id == 'PENDING'
                                   for target in node.targets)]
    require(all(not (isinstance(node.value, ast.Constant) and node.value.value is True)
                for node in pending_assignments), 'Unsealed PENDING UI runner cannot bind full acceptance')
    refs.append(ui['runner'])
    bound_bytes(spec['wine_wrapper'])
    require(spec['wine_wrapper']['path'] == '/workspace/.compat/run-wine-python.sh'
            and spec['wine_wrapper']['sha256'] == WINE_WRAPPER_SHA256,
            'Actual Wine wrapper differs from the configured root entry')
    refs.append(spec['wine_wrapper'])
    mapping = wine_mapping(spec)
    refs.append(mapping['proof'])
    own = ui['own_source_scope']
    own_keys = own['keys']
    require(isinstance(own_keys, list) and own_keys and all(isinstance(name, str) for name in own_keys)
            and len(set(own_keys)) == len(own_keys) and set(own_keys) <= set(current),
            'Actual FINAL UI own source keys must be explicit unique maintained paths')
    exact_source_review(own['source_review'], own['review_pointers'], ui['runner'], keys=own_keys)
    refs.append(own['source_review'])
    saved = spec['saved_review']
    bound_bytes(saved['runner'])
    refs.append(saved['runner'])
    for owner in (ui, saved):
        refs.append(owner['execution_contract']['source_review'])
    plan = execution_plan(spec, root, mapping)
    immutable_inputs = [str(root / name) for name in current]
    immutable_inputs.extend(archive_inputs)
    immutable_inputs.extend(row['path'] for row in refs)
    immutable_inputs.extend([str(root / 'CORE_0.70_VERIFICATION.json'), spec['linux_python_entry']])
    outputs = global_output_plan(spec, immutable_inputs, extra_immutable_paths)
    complete_selectors, selected_selectors = selectors_from_source(root)
    return {'section': 95, 'branch': branch, 'actual_base_HEAD': head,
            'source_sha256': current, 'source_files': len(current),
            'classifier_source_sha256': classifier_hashes(root),
            'full_selectors': complete_selectors, 'selected_selectors': selected_selectors,
            'completed_working_tree_chain': observed,
            'extra_dependency': file_ref(root / 'CORE_0.70_VERIFICATION.json'),
            'UI_source_binding': ui, 'exact_input_references': refs,
            'UI_expected_own_source_keys': own_keys,
            'wine_path_mapping': mapping, 'execution_contracts': plan,
            'global_output_plan': outputs,
            'commit_or_push_performed': False, 'project_calls': 0}
