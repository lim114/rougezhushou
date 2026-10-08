"""Only frozen runner difference/AST and eight new attachment bytes; no project execution."""
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
ORIGINAL = Path('/workspace/.continuation/ui-090-final')
REVISION = Path('/workspace/.continuation/ui-090-final-gate-revision')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def literal_rows(tree):
    values = [n.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == 'rows090' for t in n.targets)]
    assert len(values) == 1
    return ast.literal_eval(values[0])


manifest_path = REVISION / 'public-artifacts-manifest-two-gate-revision090.json'
manifest_raw = manifest_path.read_bytes()
assert sha(manifest_raw) == '354dc2b0bbd7f311fd302a39473edd8cfe2524ff5cee88effe4f4ae88205abbc'
new_manifest = json.loads(manifest_raw)
old_manifest_path = ORIGINAL / 'public-artifacts-manifest-final-runner090.json'
old_manifest_raw = old_manifest_path.read_bytes()
assert sha(old_manifest_raw) == '7675565345cd55711cb975c83dc49c433d1be7cfe0054634bc68938576822e10'
old_manifest = json.loads(old_manifest_raw)
assert new_manifest['format_version'] == 1 and len(new_manifest['files']) == 245
assert sum(row['bytes'] for row in new_manifest['files']) == 7533110
old_rows = {row['archive_path']: row for row in old_manifest['files']}
matched = set()
new_attachments = []
seen = set()
for row in new_manifest['files']:
    name = row['archive_path']
    rel = PurePosixPath(name)
    assert name == rel.as_posix() and not rel.is_absolute() and '\\' not in name
    assert rel.parts and not any(p in ('.', '..', '.git') for p in rel.parts)
    assert name not in seen
    seen.add(name)
    original_name = name.removeprefix('original-final237/')
    if name.startswith('original-final237/') and original_name in old_rows:
        expected = dict(old_rows[original_name], archive_path=name)
        assert row == expected
        matched.add(original_name)
        # Already passed original237 bytes are reused, not re-read/rehashed.
    else:
        path = Path(row['source_path'])
        assert path.is_absolute() and path.is_file() and not path.is_symlink()
        raw = path.read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
        new_attachments.append(row)
assert len(matched) == 237 and matched == set(old_rows)
assert len(new_attachments) == 8

old_path = ORIGINAL / 'wine-ui-smoke-090-final.py'
new_path = REVISION / 'wine-ui-smoke-090-final-gate-revision.py'
old_raw, new_raw = old_path.read_bytes(), new_path.read_bytes()
assert sha(old_raw) == 'bb35222b37dbbdb4416f415a011f3a0b678c5285729ac0bccb76ec8ba336983a'
assert sha(new_raw) == '9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9'
pair = 'coveredmodule:oblvns-ranged-skill-vs-normal'
replacements = [
    (b"profile_case090['kind']=='coveredmodule'", b"profile_case090['pair_id']=='coveredmodule:oblvns-ranged-skill-vs-normal'"),
    (b"row090['kind']=='coveredmodule'", b"row090['pair_id']=='coveredmodule:oblvns-ranged-skill-vs-normal'"),
]
expected = old_raw
for before, after in replacements:
    assert old_raw.count(before) == 1 and new_raw.count(after) == 1
    expected = expected.replace(before, after, 1)
assert expected == new_raw
inverse = new_raw
for before, after in replacements:
    inverse = inverse.replace(after, before, 1)
assert inverse == old_raw
old_tree, new_tree = ast.parse(old_raw), ast.parse(new_raw)
rows = literal_rows(new_tree)
assert rows == literal_rows(old_tree)
covered = [i for i, row in enumerate(rows) if row['pair_id'] == pair]
assert covered == [26, 27]
assert [rows[i]['kind'] for i in covered] == ['qualification', 'qualification']
assert [rows[i]['widget_checked'] for i in covered] == [False, True]
assert not any(row.get('kind') == 'coveredmodule' for row in rows)

# Confirm the two revised actual comparisons retain the intended consumer names.
gates = []
for node in ast.walk(new_tree):
    if not isinstance(node, ast.Compare) or len(node.comparators) != 1:
        continue
    right = node.comparators[0]
    left = node.left
    if isinstance(right, ast.Constant) and right.value == pair:
        assert isinstance(node.ops[0], ast.Eq)
        assert isinstance(left, ast.Subscript) and isinstance(left.value, ast.Name)
        assert isinstance(left.slice, ast.Constant) and left.slice.value == 'pair_id'
        gates.append({'consumer': left.value.id, 'line': node.lineno})
assert sorted(g['consumer'] for g in gates) == ['profile_case090', 'row090']
profile = next(n for n in new_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'profile090')
assert gates[0]['line'] >= 1
assert any(g['consumer'] == 'profile_case090' and profile.lineno <= g['line'] <= profile.end_lineno for g in gates)
assert b"'normal_not_none':frame.f_locals['normal'] is not None" in new_raw
assert b"'actual_ranged_condition_consumed':combat.ranged_attack_condition_consumed" in new_raw
assert b"'actual_selected_note_max_cnt':combat.tv['\xe9\xa2\x82\xe4\xb9\x90\xe9\x9f\xb3\xe7\xac\xa6']['max_cnt']" in new_raw
assert b"assert len(normal_entries090)==1 and len(returned090)==1" in new_raw
assert b"assert returned090[0]['normal_not_none'] is True" in new_raw
assert b"assert returned090[0]['actual_ranged_condition_consumed'] is True" in new_raw
assert b"assert returned090[0]['actual_selected_note_max_cnt']==12" in new_raw

result = {
    'format_version': 1, 'status': 'FINAL_STATIC_DIFFERENCE_PASS_PENDING_ROOT_SOLE_ACTUAL_WINDOW',
    'actual_root': '5e2ff697402d06e78b239e01f0b4307b50dd5633',
    'runner': {'source_path': str(new_path), 'bytes': len(new_raw), 'sha256': sha(new_raw)},
    'revision_public_manifest': {'source_path': str(manifest_path), 'sha256': sha(manifest_raw), 'files': 245, 'bytes': 7533110},
    'old237_scope': {'exact_manifest_descriptors_reused_under_archive_prefix': 237, 'source_bytes_rehashed_or_old_formal_rerun': False},
    'eight_new_attachments_hash_checked': new_attachments,
    'exact_two_gates_only': True, 'reverse_restores_original_bb_runner': True,
    'old52_cases_inputs_kinds_projections_unchanged': True,
    'two_pair_id_AST_gates': gates,
    'reachable_row_indexes0': covered, 'both_original_kinds': ['qualification', 'qualification'],
    'actual_trace_assertion_readiness': 'Source gate now reaches existing observer and existing assertions for exactly these two cases; old saved44 same-call traces support expectations. No new trace is claimed observed.',
    'transitive_reuse': ['original730 source/Git/context guard PASS', 'old4217 byte inverse PASS', '52 genuine controls/Back4/saved89/counters source PASS'],
    'original_conditional_flag_scope_clarification': 'native_before_JSON_result_saved:true in original receipt describes source-defined future actual result capture and existing saved52 evidence, not a newly executed root window; planned actual result/scenario native capture only, zero new actual window calls here.',
    'actual_GUI_pass_claimed': False,
    'project_calls': {'API': 0, 'helper': 0, 'formatter': 0, 'tests': 0, 'Qt': 0, 'Wine': 0},
    'current_problem_attempts': {'original_dead_gate_static_blocker': 1, 'bounded_two_gate_correction_difference_review': 1, 'new_product_runtime_failures': 0},
    'root_only_remaining': ['fresh actual Wine MainWindow single run', 'measured startup/replay/calculation/formatter entry ledgers', 'full730 root source context and exact126 UI runtime source map', 'inspect four actual screenshots', 'archive actual resulting bytes/commit/tag'],
}
(HERE / 'formal-two-gate-difference-receipt090.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ('status', 'runner', 'exact_two_gates_only', 'reachable_row_indexes0', 'project_calls')}, ensure_ascii=False))
