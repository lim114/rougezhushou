"""Own stdlib Source transport and compile-only; never execute the generated code."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

PACKET = Path(__file__).resolve().parent
BASE = Path('/workspace/.continuation/full105-bounded-window-source-v1')
BASE_WINDOW_SHA = '98e6cef848ffea73d36f330edb071e28cc884e676838a876a76995d28ea821a5'
def sha(raw):
    return hashlib.sha256(raw).hexdigest()


base = (BASE / 'window.py').read_bytes()
supervisor_base = (BASE / 'supervisor100-preserved.py').read_bytes()
if sha(base) != BASE_WINDOW_SHA:
    raise ValueError('The frozen full105 v1 Source changed')
# The exact supervisor pin is recorded below from its actual bytes and checked
# against the previous packet MANIFEST when present, rather than guessed.
prior_manifest = json.loads((BASE / 'MANIFEST.json').read_text())
supervisor_entry = prior_manifest['files']['supervisor100-preserved.py']
if len(supervisor_base) != supervisor_entry['bytes'] or sha(supervisor_base) != supervisor_entry['sha256']:
    raise ValueError('The frozen prior supervisor Source changed')

PROGRESS_SOURCE = '''def _write_progress105(count, last_check):
    # Only completed append count and public scalar labels; never dump checks,
    # window, caller, state, function vectors or repeat a full Source hash scan.
    record = {'kind': 'FULL105_ATTEMPT2_APPENDED_CHECK_PROGRESS',
              'after_section': 105, 'attempt': 2, 'passed': False,
              'workflow_complete': False, 'appended_checks': count,
              'last_check': last_check,
              'elapsed_seconds': round(time.perf_counter()-_started100, 3),
              'checkpoint_every_appended_checks': 32,
              'complete_function_vector_measured': False}
    temporary = OUT / 'full105-progress.json.tmp'
    with temporary.open('w', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, OUT / 'full105-progress.json')


class _ProgressChecks105(list):
    def __init__(self):
        super().__init__()
        _write_progress105(0, {})

    def append(self, item):
        # Real list.append first. Its original None return is preserved; an
        # observer IO error propagates to the unchanged outer failure handler.
        super().append(item)
        count = len(self)
        if count % 32 == 0:
            labels = {}
            if type(item) is dict:
                for key in ('scope', 'section', 'operator', 'skill', 'pair_id'):
                    value = item.get(key)
                    if key in item and (value is None or type(value) in (str, int, bool)):
                        labels[key] = value
            _write_progress105(count, labels)


'''

window_changes = [
    ('child deadline', '_deadline100 = _started100 + 600\n',
     '_deadline100 = _started100 + 1200\n'),
    ('soft deadline label', "raise TimeoutError('Fresh full105 deadline of600 seconds reached')",
     "raise TimeoutError('Fresh full105 attempt2 deadline of1200 seconds reached')"),
    ('hard deadline receipt',
     "record = {'passed': False, 'scope': 'actual full105 hard deadline', 'after_section': 105,\n              'deadline_seconds': 600,",
     "record = {'passed': False, 'scope': 'actual full105 attempt2 hard deadline', 'after_section': 105,\n              'attempt': 2, 'deadline_seconds': 1200,"),
    ('hard deadline stdout', "print(json.dumps({'passed': False, 'hard_deadline': 600}), flush=True)",
     "print(json.dumps({'passed': False, 'attempt': 2, 'hard_deadline': 1200}), flush=True)"),
    ('hard watchdog budget', 'threading.Timer(600, _hard_timeout100)',
     'threading.Timer(1200, _hard_timeout100)'),
    ('outside-functional-Try progress observer', 'def _replace_binding100(owner, name, replacement):\n',
     PROGRESS_SOURCE + 'def _replace_binding100(owner, name, replacement):\n'),
    ('outside-functional-Try checks initialization',
     'checks=[];started=time.perf_counter();window=None;app=None;before=source_hashes()\n',
     'checks=_ProgressChecks105();started=time.perf_counter();window=None;app=None;before=source_hashes()\n'),
    ('receipt attempt and progress metadata',
     "         'deadline_seconds':600,'global_profile_or_trace_used':False,\n",
     "         'deadline_seconds':1200,'global_profile_or_trace_used':False,\n"
     "         'full105_attempt':2,'progress_checkpoint_file':'full105-progress.json',\n"
     "         'progress_every_appended_checks':32,'progress_is_partial_observation_only':True,\n"
     "         'full105_v1_source_sha256':'" + BASE_WINDOW_SHA + "',\n"),
]

supervisor_changes = [
    ('supervisor description',
     'Linux-only fresh full100 launcher with an independent600-second deadline.',
     'Linux-only fresh full105 attempt2 launcher with an independent1200-second deadline.'),
    ('independent supervisor budget and attempt metadata',
     "              'deadline_seconds': 600, 'native_windows_verified': False,\n",
     "              'deadline_seconds': 1200, 'native_windows_verified': False,\n"
     "              'after_section': 105, 'full105_attempt': 2,\n"),
    ('actual independent process wait budget',
     'process.wait(timeout=max(0, 600-(time.monotonic()-started)))',
     'process.wait(timeout=max(0, 1200-(time.monotonic()-started)))'),
]


def transport(original, changes):
    value = original
    rows = []
    for label, before, after in changes:
        old = before.encode('utf-8')
        new = after.encode('utf-8')
        if value.count(old) != 1:
            raise ValueError((label, 'before is not unique', value.count(old)))
        value = value.replace(old, new)
        rows.append({'label': label, 'before': before, 'after': after})
    inverse = value
    for row in reversed(rows):
        new, old = row['after'].encode(), row['before'].encode()
        if inverse.count(new) != 1:
            raise ValueError((row['label'], 'after is not unique', inverse.count(new)))
        inverse = inverse.replace(new, old)
    if inverse != original:
        raise ValueError('Inverse did not recover baseline bytes')
    return value, rows


window, window_rows = transport(base, window_changes)
supervisor, supervisor_rows = transport(supervisor_base, supervisor_changes)
old_ast, new_ast = ast.parse(base), ast.parse(window)
compile(window, str(PACKET / 'window.py'), 'exec')
compile(supervisor, str(PACKET / 'supervisor105.py'), 'exec')
dump = lambda node: ast.dump(node, include_attributes=False)
old_asserts = [dump(node) for node in ast.walk(old_ast) if isinstance(node, ast.Assert)]
new_asserts = [dump(node) for node in ast.walk(new_ast) if isinstance(node, ast.Assert)]
if len(old_asserts) != 831 or old_asserts != new_asserts:
    raise ValueError('Original 831 assertions changed')
old_tries = [node for node in old_ast.body if isinstance(node, ast.Try)]
new_tries = [node for node in new_ast.body if isinstance(node, ast.Try)]
if len(old_tries) != 1 or len(new_tries) != 1 or dump(old_tries[0]) != dump(new_tries[0]):
    raise ValueError('The full functional Try changed')
old_functions = {node.name: node for node in old_ast.body if isinstance(node, ast.FunctionDef)}
new_functions = {node.name: node for node in new_ast.body if isinstance(node, ast.FunctionDef)}
changed = [name for name, node in old_functions.items() if dump(node) != dump(new_functions[name])]
if changed != ['_deadline_check100', '_hard_timeout100']:
    raise ValueError(('Original helper change', changed))
added_functions = sorted(set(new_functions) - set(old_functions))
if added_functions != ['_write_progress105']:
    raise ValueError(('Unexpected helper addition', added_functions))
old_super_ast, new_super_ast = ast.parse(supervisor_base), ast.parse(supervisor)
old_super_funcs = {node.name: node for node in old_super_ast.body if isinstance(node, ast.FunctionDef)}
new_super_funcs = {node.name: node for node in new_super_ast.body if isinstance(node, ast.FunctionDef)}
super_changed = [name for name in old_super_funcs if dump(old_super_funcs[name]) != dump(new_super_funcs[name])]
if super_changed != ['main']:
    raise ValueError(('Supervisor process cleanup changed', super_changed))

(PACKET / 'window.py').write_bytes(window)
(PACKET / 'supervisor105.py').write_bytes(supervisor)
(PACKET / 'exact-local-transports.json').write_text(json.dumps({
    'kind': 'SOURCE_ONLY_FULL105_ATTEMPT2_BUDGET_AND_PARTIAL_PROGRESS',
    'product_pass': False, 'author_Runtime_executed': False,
    'window_baseline_sha256': sha(base), 'window_sha256': sha(window),
    'supervisor_baseline_sha256': sha(supervisor_base), 'supervisor_sha256': sha(supervisor),
    'window_changes': window_rows, 'supervisor_changes': supervisor_rows,
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
for name, old, new in [('window-source.diff', base, window),
                       ('supervisor-source.diff', supervisor_base, supervisor)]:
    (PACKET / name).write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),
        new.decode().splitlines(True), fromfile='frozen-v1', tofile='fresh-v2')),
        encoding='utf-8')
proof = {'kind': 'SOURCE_ONLY_AUTHOR_STDLIB_AST_COMPILE_TRANSPORT',
    'project_helper_codec_Qt_Wine_tests_Git_execution_count': 0, 'tracked_writes': 0,
    'runner': {'bytes': len(window), 'sha256': sha(window)},
    'supervisor': {'bytes': len(supervisor), 'sha256': sha(supervisor)},
    'baseline_runner': {'bytes': len(base), 'sha256': sha(base)},
    'baseline_supervisor': {'bytes': len(supervisor_base), 'sha256': sha(supervisor_base)},
    'all_original_assert_AST_same': True, 'original_assert_count': len(old_asserts),
    'entire_functional_Try_AST_same': True,
    'functional_Try_AST_sha256': sha(dump(old_tries[0]).encode()),
    'original_top_level_FunctionDef_changed': changed,
    'original_top_level_FunctionDef_unchanged': len(old_functions)-len(changed),
    'new_top_level_FunctionDef': added_functions, 'new_class': '_ProgressChecks105',
    'supervisor_changed_methods': super_changed,
    'supervisor_owned_session_cleanup_FunctionDef_AST_same': True,
    'forward_inverse_exact': True, 'compile_only': True,
    'deadline_child_seconds': 1200, 'deadline_supervisor_seconds': 1200,
    'progress_initial_count': 0, 'progress_every_appended_checks': 32,
    'old_scope_limitations_preserved': True, 'actual_runtime_pending': True}
(PACKET / 'AUTHOR_SOURCE_CHECK.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
print(json.dumps(proof, indent=2))
