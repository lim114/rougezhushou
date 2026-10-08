"""Independent bytes/AST/Git source audit only. Never imports or executes project code."""
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess

HERE = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/p2-continuous-attack-controls-091-ui-candidate')
ROOT = Path('/workspace/rougezhushou')
BASE = '2cbc45f03f99ed4f04b9c7e2612b58542f909168'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(node):
    return ast.dump(node, include_attributes=False)


manifest_path = AUTHOR / 'ui-author-public-manifest091.json'
manifest_raw = manifest_path.read_bytes()
assert sha(manifest_raw) == '2b286f356a0d10da925f269f6e303c731adfcf9674efc18eef22363e092a7b53'
manifest = json.loads(manifest_raw)
assert manifest['format_version'] == 1 and len(manifest['files']) == 66
seen = set()
for row in manifest['files']:
    path, name = Path(row['source_path']), row['archive_path']
    rel = PurePosixPath(name)
    assert path.is_absolute() and path.is_file() and not path.is_symlink()
    assert name == rel.as_posix() and not rel.is_absolute() and '\\' not in name
    assert rel.parts and not any(p in ('.', '..', '.git') for p in rel.parts)
    assert name not in seen
    seen.add(name)
    raw = path.read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name
assert sum(row['bytes'] for row in manifest['files']) == 1459348

freeze_raw = (AUTHOR / 'ui-review-freeze091.json').read_bytes()
handoff_raw = (AUTHOR / 'ui-author-handoff091.json').read_bytes()
assert sha(freeze_raw) == 'afd5c14c8fe8d4b43079b5834c8eaf267184120a0597a98dd839f726d3bf9b6d'
assert sha(handoff_raw) == 'df3b867e1fc8b878a6ccc68f87a3cdd30798851f3ae40e77d086c862ca85b21e'
freeze = json.loads(freeze_raw)
assert freeze['actual_full90_commit'] == BASE
assert subprocess.check_output(['git', 'rev-parse', 'p2-validation-090'], cwd=ROOT).decode().strip() == BASE
paths = ['rouge/app.py', 'scripts/verify_damage_ui.py', 'rouge/catalog.py']
old_files = {}
for rel in paths:
    baseline = (AUTHOR / 'baseline' / rel).read_bytes()
    fixed = subprocess.check_output(['git', 'show', BASE + ':' + rel], cwd=ROOT)
    assert baseline == fixed == (ROOT / rel).read_bytes(), rel
    old_files[rel] = baseline

old_app, old_runner = old_files['rouge/app.py'], old_files['scripts/verify_damage_ui.py']
new_app = (AUTHOR / 'candidate/rouge/app.py').read_bytes()
new_runner = (AUTHOR / 'candidate/scripts/verify_damage_ui.py').read_bytes()
assert len(new_app) == 95400 and sha(new_app) == 'fa27d6eceaf88f8caf1bc4e994641c6d110884ee9fbf673ab7d46a355cc41143'
assert len(new_runner) == 10738 and sha(new_runner) == '0b0dcbcade07f0ff11b2bdcba7c7598a696ff4ece3418bc296312ce97c2a2d54'
assert b'\n' not in new_app.replace(b'\r\n', b'') and b'\r' not in new_runner

tooltip = '声明估算时是否持续普攻；自然回复技能也可能通过适用的天赋或藏品使用此条件。显示此项不表示必有额外技力。未核验的技力来源仅作资料参考，未知回转保持未知。'
before_refresh = "        self.continuous_attacks.setChecked(True)\r\n        form.addRow('攻击回复条件',self.continuous_attacks)\r\n"
after_refresh = "        self.continuous_attacks.setChecked(True)\r\n        self.continuous_attacks.setToolTip('" + tooltip + "')\r\n        self.continuous_attacks.toggled.connect(lambda:self.calculate())\r\n        form.addRow('普攻回技力条件',self.continuous_attacks)\r\n"
changes = [
    (before_refresh.encode(), after_refresh.encode()),
    (b"        healer=op in catalog()['operators'] and has_healing(op,skill)\r\n", b"        implemented=op in catalog()['operators']\r\n        healer=implemented and has_healing(op,skill)\r\n"),
    (b"                    (self.continuous_attacks,current.get('sp_type')=='INCREASE_WHEN_ATTACK'),\r\n", b"                    (self.continuous_attacks,implemented and current.get('sp_type') in ('INCREASE_WHEN_ATTACK','INCREASE_WITH_TIME')),\r\n"),
]
expected = old_app
inverse = new_app
for before, after in changes:
    assert old_app.count(before) == new_app.count(after) == 1
    expected = expected.replace(before, after, 1)
    inverse = inverse.replace(after, before, 1)
assert expected == new_app and inverse == old_app
old_expr = b"app_module.catalog()['operators'][op]['skills'][skill-1]['levels'][-1]['sp_type']=='INCREASE_WHEN_ATTACK'"
new_expr = b"app_module.catalog()['operators'][op]['skills'][skill-1]['levels'][window.skill_rank_value()-1]['sp_type'] in ('INCREASE_WHEN_ATTACK','INCREASE_WITH_TIME')"
assert old_runner.count(old_expr) == new_runner.count(new_expr) == 1
assert old_runner.replace(old_expr, new_expr, 1) == new_runner
assert new_runner.replace(new_expr, old_expr, 1) == old_runner

old_tree, new_tree = ast.parse(old_app), ast.parse(new_app)
old_class = next(n for n in old_tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainWindow')
new_class = next(n for n in new_tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainWindow')
old_methods = {n.name: n for n in old_class.body if isinstance(n, ast.FunctionDef)}
new_methods = {n.name: n for n in new_class.body if isinstance(n, ast.FunctionDef)}
assert set(old_methods) == set(new_methods)
changed = sorted(name for name in old_methods if dump(old_methods[name]) != dump(new_methods[name]))
assert changed == ['make_damage_tab', 'update_skill_options']
assert dump(old_methods['calculate']) == dump(new_methods['calculate'])
assert dump(old_methods['update_operator']) == dump(new_methods['update_operator'])
assert dump(ast.parse(inverse)) == dump(old_tree)
ast.parse(new_runner)

# This checks syntax of the selected-source predicate without running UI or helpers.
conditions = next(n.value for n in ast.walk(new_methods['update_skill_options'])
    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'conditions' for t in n.targets))
entry = next(n for n in conditions.elts if isinstance(n, ast.Tuple)
             and isinstance(n.elts[0], ast.Attribute) and n.elts[0].attr == 'continuous_attacks')
predicate = entry.elts[1]
assert isinstance(predicate, ast.BoolOp) and isinstance(predicate.op, ast.And)
assert isinstance(predicate.values[0], ast.Name) and predicate.values[0].id == 'implemented'
comparison = predicate.values[1]
assert isinstance(comparison, ast.Compare) and isinstance(comparison.ops[0], ast.In)
assert ast.literal_eval(comparison.comparators[0]) == ('INCREASE_WHEN_ATTACK', 'INCREASE_WITH_TIME')
assert new_app.count(b'self.continuous_attacks.setChecked(True)') == 1
assert new_app.count(b'self.continuous_attacks.toggled.connect(lambda:self.calculate())') == 1
assert new_app.count(b"'continuous_attacks':self.continuous_attacks.isChecked()") == 1

patch_path = AUTHOR / 'candidate-ui091.patch'
patch_raw = patch_path.read_bytes()
assert len(patch_raw) == 3069 and sha(patch_raw) == 'e9a79b6b62012d5636195c954130344c737ec62bb74e9c7b0f2a3ea9e1b86a09'
proc = subprocess.run(['git', 'apply', '--check', str(patch_path)], cwd=ROOT, capture_output=True)
assert proc.returncode == 0, proc.stderr.decode()

receipt = {
    'format_version': 1, 'status': 'INDEPENDENT_SOURCE_BYTE_AST_PASS_PENDING_ROOT_ACTUAL_WINDOW',
    'actual_base_commit': BASE,
    'author_manifest': {'source_path': str(manifest_path), 'sha256': sha(manifest_raw), 'files': 66, 'bytes': 1459348},
    'author_freeze_sha256': sha(freeze_raw), 'author_handoff_sha256': sha(handoff_raw),
    'baseline3_Git_current_bytes_exact': {rel: {'bytes': len(raw), 'sha256': sha(raw)} for rel, raw in old_files.items()},
    'candidate2': {'rouge/app.py': {'bytes': len(new_app), 'sha256': sha(new_app), 'endings': 'CRLF'},
                   'scripts/verify_damage_ui.py': {'bytes': len(new_runner), 'sha256': sha(new_runner), 'endings': 'LF'}},
    'byte_inverse': {'app_exact3_blocks': True, 'runner_exact1_expression': True, 'whole_AST_inverse': True},
    'changed_MainWindow_methods': changed, 'unchanged_calculate_and_update_operator_AST': True,
    'patch_readonly_apply_check': {'returncode': proc.returncode, 'stderr': proc.stderr.decode(), 'tracked_written': False},
    'visibility_scope': 'Implemented catalog owner and currently selected legal skill/rank; Attack or Natural. Natural visibility permits condition access and does not itself qualify extra credit. Other SP/None/unimplemented hidden.',
    'default_hidden_bool_scope': 'Original single True setter and single isChecked producer preserved. No reset/persistence migration added; hidden retains widget state, not a disk persistence claim.',
    'runner_migration_scope': 'Single former final-rank Attack-only expression replaced by Attack|Natural at selected skill_rank_value()-1. Existing implemented-owner filter and every unrelated runner byte preserved.',
    'runtime_entry_claims': 'None; startup signal/emission/reentrancy, refreshed results, state transitions, rendering, and actual call counts require root focused real MainWindow acceptance.',
    'project_calls': {'API': 0, 'helper': 0, 'formatter': 0, 'constructor': 0, 'tests': 0, 'Qt': 0, 'Wine': 0},
    'source_preparation_failures': 0, 'product_or_runtime_failures': 0,
    'root_exclusive': ['tracked apply', 'focused actual Qt/Wine behavior checks', 'grouped Deepcolor integration', 'archive/commit'],
}
(HERE / 'source-byte-AST-formal-receipt091.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'files': 66, 'bytes': 1459348, 'changed_methods': changed, 'apply_check': proc.returncode, 'project_calls': receipt['project_calls']}))
