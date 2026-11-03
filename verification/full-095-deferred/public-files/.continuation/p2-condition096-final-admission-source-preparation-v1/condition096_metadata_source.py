"""New metadata-only Source interface, derived from frozen validation096 v2.

This module is not a target runner and contains no target imports or codecs.
Root supplies physical post-publication facts. No existing admission schema is
assumed: pointer maps below are explicit new input contracts for Root to fill.
"""
import ast
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat

LOCAL = Path('/workspace/.continuation')
V2 = LOCAL / 'p2-condition096-validation-source-pending-v2'
CANDIDATE = LOCAL / 'p2-condition096-candidate-v1'
GUARD095 = {'path': str(LOCAL / 'root-source-095-v2.json'), 'bytes': 84227, 'sha256': '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'}
BINDING_TEMPLATE = {'path': str(V2 / 'condition096-binding-template.json'), 'bytes': 1791, 'sha256': 'a924c7bcd763ffa14e02b155a7fa6c0dbc60422235c8c2a9c8bfc51a87ccfbc2'}
PINNED = {
    'validation_plan': {'path': str(V2 / 'condition096-validation-plan.json'), 'bytes': 601281, 'sha256': '55eab397b5bc908263d073318e610c7e23ddd33116759935b31e302144dc20fc'},
    'candidate_code_manifest': {'path': str(CANDIDATE / 'public-code-artifacts-manifest096.json'), 'bytes': 2487, 'sha256': '255d95b7c7241ebc34bb85a01a543bac0f50f7d9b44ad9de7b178a4598c45c36'},
    'condition096_formal_source_review': {'path': str(LOCAL / 'p2-condition096-final-formal-source-review-v1/formal-independent-source-review-condition096-v1.json'), 'bytes': 46823, 'sha256': '1e147f0385b11c730e73ec2a642a945f372ede74cff82571d23e7f334e29c2c6'},
}
RUNNERS = {
    'linux_worker': {'pending': 'linux-condition096-worker-pending.py', 'final': 'linux-condition096-worker-final.py', 'sha256': '5ab7870186cf4518288b98773f08a3198ce672f204bef5469eea9e1a2a594ebc', 'bytes': 13249},
    'wine_window': {'pending': 'wine-condition096-window-pending.py', 'final': 'wine-condition096-window-final.py', 'sha256': 'b8839010440352c968198f535284ce5605df8d9af96eadc1daa2abf96f8011ec', 'bytes': 45368},
    'linux_comparator': {'pending': 'compare-condition096-linux-pending.py', 'final': 'compare-condition096-linux-final.py', 'sha256': 'bf282583198a19f3105ca5021a68a2fffc3aa84d0c26a423610f1e13c7df6491', 'bytes': 5793},
}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(name):
    p = Path(name)
    require(p.is_absolute() and str(p) == str(p.resolve()), 'Canonical absolute host path required')
    return p


def ref(name):
    p = canonical(name)
    require(not p.is_symlink() and stat.S_ISREG(p.lstat().st_mode), 'Regular physical host file required')
    raw = p.read_bytes()
    return {'path': str(p), 'bytes': len(raw), 'sha256': sha(raw)}


def bound(row):
    require(type(row) is dict and set(('path', 'bytes', 'sha256')) <= set(row) and type(row['bytes']) is int, 'Physical full reference required')
    require(ref(row['path']) == {key: row[key] for key in ('path', 'bytes', 'sha256')}, 'Physical input bytes/SHA differ')
    return Path(row['path']).read_bytes()


def doc(row):
    return json.loads(bound(row))


def pointer(value, ptr):
    require(type(ptr) is str and ptr.startswith('/'), 'Root actual JSON pointer required')
    for token in ptr[1:].split('/'):
        key = token.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if type(value) is list else value[key]
    return value


def typed_gates(row, gates):
    value = doc(row)
    require(type(gates) is list and gates, 'Nonempty Root actual typed gates required')
    for gate in gates:
        actual = pointer(value, gate['pointer'])
        require(type(actual) is type(gate['expected']) and actual == gate['expected'], 'Physical Root proof gate differs')
    return value


def named_gates(row, pointers, expected):
    require(type(pointers) is dict and set(pointers) == set(expected), 'Explicit new named pointer contract required')
    gates = [{'pointer': pointers[name], 'expected': expected[name]} for name in expected]
    typed_gates(row, gates)
    return {'path': row['path'], 'bytes': row['bytes'], 'sha256': row['sha256'], 'JSON_pointer_gates': gates}


def write_json(path, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    with path.open('xb') as stream:
        stream.write(raw)
    require(path.read_bytes() == raw, 'Exclusive metadata output changed')
    return ref(str(path))


def runtime_path(host, platform):
    p = canonical(host)
    return str(p) if platform == 'linux' else 'Z:' + str(p).replace('/', '\\')


def runtime_ref(row, platform):
    value = dict(row)
    value['path'] = runtime_path(row['path'], platform)
    return value


def current_helper_refs(here):
    return {name: ref(str(here / name)) for name in ('condition096_metadata_source.py', 'seal_condition096_final.py', 'admit_condition096_final.py')}


def source_inputs(spec, here):
    require(spec['format_version'] == 1 and spec['section'] == 96 and spec['status'] == 'ROOT_ACTUAL_95_PUBLICATION_CLOSED_096_FINAL_INPUTS', 'Pending Source input cannot seal')
    require(spec['root_seal_authorized'] is True and spec['root_intends_runtime_after_external_FINAL_admission'] is True, 'Root metadata seal and conditional runtime intent required')
    require(spec['mode'] in ('gold', 'candidate') and spec['platform'] in ('linux', 'wine'), 'Actual mode/platform required')
    target = spec['execution_target']
    require(target in RUNNERS and ((target == 'wine_window') is (spec['platform'] == 'wine')), 'Actual target/platform differs')
    head = spec['actual_published95_HEAD']
    require(type(head) is str and len(head) == 40 and all(c in '0123456789abcdef' for c in head), 'Actual published95 commit required')
    full = spec['actual_full095_validation_receipt']
    full_gates = named_gates(full, {'status': '/status', 'section': '/section', 'available': '/available_checks_passed', 'UI': '/complete_ui_validation', 'native': '/native_windows'}, {'status': 'PASS_ACTUAL_FULL095_AVAILABLE_NOT_NATIVE_WINDOWS', 'section': 95, 'available': True, 'UI': True, 'native': False})
    publication = spec['actual_post_full095_commit_push_proof']
    publication_gates = named_gates(publication, spec['publication_proof_pointers'], {'commit_push_closed': True, 'fresh_remote_equal': True, 'published_HEAD': head, 'current_HEAD': head, 'full095_receipt_sha256': full['sha256']})
    helper_refs = current_helper_refs(here)
    helper_gates = named_gates(spec['metadata_helpers_independent_source_review'], spec['metadata_helpers_review_pointers'], {'source_pass': True, 'runtime_pass': False, **{name: row['sha256'] for name, row in helper_refs.items()}})
    source_root = canonical(spec['source_root'])
    guard = doc(spec['actual_source_guard'])
    baseline = doc(GUARD095)
    full_context = doc(full)
    require(full_context['source_sha256'] == full_context['source_sha256_after'] == baseline['source_sha256_after'] and full_context['source_drift'] == [], 'Actual full095 context must bind the preserved Source735 map')
    require(guard['passed'] is True and type(spec['actual_maintained_count']) is int and len(guard['source_sha256_after']) == spec['actual_maintained_count'], 'Actual fresh guard/count required')
    expected = dict(baseline['source_sha256_after'])
    require(len(expected) == 735, 'Frozen gold Source735 differs')
    code_manifest = doc(PINNED['candidate_code_manifest'])
    if spec['mode'] == 'candidate':
        for row in code_manifest['files']:
            bound({'path': row['source_path'], 'bytes': row['bytes'], 'sha256': row['sha256']})
            old = row['expected_old']
            require((old is None and row['destination_repo_path'] not in expected) or (old is not None and expected.get(row['destination_repo_path']) == old['sha256']), 'Candidate exact old/absence inventory differs')
            expected[row['destination_repo_path']] = row['sha256']
    require(guard['source_sha256_after'] == expected, 'Actual gold/candidate guard is not the exact frozen Source map')
    for name, value in expected.items():
        relative = PurePosixPath(name)
        require(not relative.is_absolute() and '..' not in relative.parts, 'Guard source path is unsafe')
        require(sha(bound(ref(str(source_root / name)))) == value, 'Actual guarded source bytes differ')
    for name, row in PINNED.items():
        bound(row)
    implementation = doc(PINNED['condition096_formal_source_review'])
    require(implementation['source_gate_passed'] is True and implementation['runtime_pass'] is False and implementation['code_manifest_sha256'] == PINNED['candidate_code_manifest']['sha256'], 'Frozen functional Source qualification differs')
    admission_expected = {'source_pass': True, 'runtime_pass': False, 'scope': 'PENDING_TEMPLATE_PRESEAL_SOURCE_ADMISSION_ONLY', 'published_HEAD': head, 'full095_receipt_sha256': full['sha256'], 'publication_proof_sha256': publication['sha256'], 'actual_guard_sha256': spec['actual_source_guard']['sha256'], 'mode': spec['mode'], 'platform': spec['platform'], 'source_root': str(source_root), 'validation_plan_sha256': PINNED['validation_plan']['sha256'], 'candidate_manifest_sha256': PINNED['candidate_code_manifest']['sha256'], **{name: row['sha256'] for name, row in RUNNERS.items()}}
    preseal_gates = named_gates(spec['independent_preseal_source_admission'], spec['preseal_admission_pointers'], admission_expected)
    output = canonical(spec['fresh_output_directory'])
    require(not output.exists() and output != source_root and not output.is_relative_to(source_root) and not source_root.is_relative_to(output), 'Fresh runtime output must be absent and separate from source')
    gates = [full_gates, publication_gates, helper_gates, preseal_gates]
    gates += [named_gates(PINNED['candidate_code_manifest'], {'runtime': '/runtime_pass', 'increment': '/completed_section_increment'}, {'runtime': False, 'increment': 0}), named_gates(PINNED['condition096_formal_source_review'], {'source': '/source_gate_passed', 'runtime': '/runtime_pass'}, {'source': True, 'runtime': False})]
    # Baseline records are opaque physical files here: no codec executes.
    baseline_keys = ('actual_baseline_receipt', 'actual_baseline_records', 'actual_baseline_shell_status', 'actual_baseline_saved_review')
    if target == 'wine_window' and spec['mode'] == 'candidate':
        baseline_receipt = doc(spec['actual_baseline_receipt'])
        require(baseline_receipt['mode'] == 'gold' and baseline_receipt['passed'] is baseline_receipt['workflow_complete'] is True and baseline_receipt['source_drift'] == [] and baseline_receipt['plan_sha256'] == PINNED['validation_plan']['sha256'], 'Actual Wine gold receipt required')
        require(bound(spec['actual_baseline_shell_status']) in (b'0\n', b'0\r\n'), 'Actual Wine gold primary raw zero required')
        bound(spec['actual_baseline_records'])
        gates.append(named_gates(spec['actual_baseline_saved_review'], spec['baseline_saved_review_pointers'], {'passed': True, 'project_calls': 0, 'gold_receipt_sha256': spec['actual_baseline_receipt']['sha256'], 'gold_records_sha256': spec['actual_baseline_records']['sha256'], 'gold_primary_status_sha256': spec['actual_baseline_shell_status']['sha256']}))
    else:
        require(all(spec[key] is None for key in baseline_keys), 'Baseline refs belong only to candidate Wine')
    if spec['platform'] == 'wine':
        mapping = spec['wine_path_mapping']
        require(mapping['drive'] == 'Z:' and mapping['linux_root'] == '/', 'Actual Wine Z mapping contract required')
        bound(mapping['wrapper'])
        gates.append(named_gates(mapping['proof'], mapping['proof_pointers'], {'drive_link': mapping['drive_link'], 'linux_root': '/', 'wrapper_sha256': mapping['wrapper']['sha256']}))
    else:
        require(spec['wine_path_mapping'] is None, 'Linux binding has no Wine mapping')
    # The embedded legacy label is deliberately preseal only. Final Source hashes
    # and Root launch authorization are separate later inputs, never backedges.
    binding = doc(BINDING_TEMPLATE)
    binding.update(status='ROOT_SEALED_CONDITION096_RUNTIME_BINDING', mode=spec['mode'], root_runtime_authorized=True, source_root=runtime_path(str(source_root), spec['platform']), fresh_output_directory=runtime_path(str(output), spec['platform']), actual_maintained_count=len(expected), actual_source_guard=runtime_ref(spec['actual_source_guard'], spec['platform']), actual_full095_validation_receipt=runtime_ref(full, spec['platform']), actual_post_full095_commit_push_proof=runtime_ref(publication, spec['platform']), actual_FINAL_runner_formal_review=runtime_ref(spec['independent_preseal_source_admission'], spec['platform']), required_actual_prerequisite_gates=[runtime_ref(row, spec['platform']) for row in gates])
    for name, row in PINNED.items():
        binding[name] = runtime_ref(row, spec['platform'])
    binding['gold095_source_guard'] = runtime_ref(GUARD095, spec['platform'])
    for key in baseline_keys:
        binding[key] = None if spec[key] is None else runtime_ref(spec[key], spec['platform'])
    binding['embedded_admission_scope'] = 'PENDING_TEMPLATE_PRESEAL_SOURCE_ADMISSION_ONLY'
    binding['external_actual_postseal_FINAL_review_required_before_launch'] = True
    binding['actual_postseal_FINAL_review_embedded'] = False
    return binding, helper_refs


def final_source(pending, binding_sha):
    flag = b'PENDING_PREPARATION = True'
    require(pending.count(flag) == 1, 'Exact one pending flag required')
    candidate = pending.replace(flag, b'PENDING_PREPARATION = False', 1)
    changes = [{'before_base64': base64.b64encode(flag).decode(), 'after_base64': base64.b64encode(b'PENDING_PREPARATION = False').decode()}]
    before = b'EXPECTED_BINDING_SHA256=None'
    if before in pending:
        require(pending.count(before) == 1, 'Exact one binding literal required')
        after = ('EXPECTED_BINDING_SHA256=' + repr(binding_sha)).encode('ascii')
        candidate = candidate.replace(before, after, 1)
        changes.append({'before_base64': base64.b64encode(before).decode(), 'after_base64': base64.b64encode(after).decode()})
    reversed_bytes = candidate
    for row in reversed(changes):
        after = base64.b64decode(row['after_base64'], validate=True)
        before = base64.b64decode(row['before_base64'], validate=True)
        require(reversed_bytes.count(after) == 1, 'Unique exact inverse literal required')
        reversed_bytes = reversed_bytes.replace(after, before, 1)
    require(reversed_bytes == pending, 'All original worker/window/comparator/codec logic must remain whole bytes')
    ast.parse(candidate)
    compile(candidate, '<condition096-final-source-syntax-only>', 'exec')  # Never execute this object.
    return candidate, changes
