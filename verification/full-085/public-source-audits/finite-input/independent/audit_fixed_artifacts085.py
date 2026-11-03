"""Bounded independent source/hash/AST verification; no product code imports."""
import ast
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-after086-finite-input-source')
ROOT = Path('/workspace/rougezhushou')
BASE = '2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'
sha = lambda data: hashlib.sha256(data).hexdigest()
canon = lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
raw_manifest = (AUTHOR / 'public-artifacts-manifest.json').read_bytes()
assert sha(raw_manifest) == '58d25683715beef74e048b26c3e27014616e7c6b33cfded4d147ce9a8a825bb1'
manifest = json.loads(raw_manifest)
assert len(manifest['files']) == 38
for proof in manifest['files']:
    raw = Path(proof['source_path']).read_bytes()
    assert sha(raw) == proof['sha256'] and len(raw) == proof['bytes']
    assert proof['archive_path'] == str(Path(proof['source_path']).relative_to(AUTHOR))
assert sum(proof['bytes'] for proof in manifest['files']) == 783429
raw_handoff = (AUTHOR / 'handoff.json').read_bytes()
assert sha(raw_handoff) == 'ffa3cc6943d8833efb65a897a4fc64d12ee37278bdfd3e3cd627f05d4af4c5b1'
handoff = json.loads(raw_handoff)
assert handoff['fixed_commit'] == BASE and handoff['actionable_candidates'] == [] and handoff['numbered_section'] is False
assert not handoff['fresh_runtime_validation'] and all(v == 0 for v in handoff['counters'].values())
freeze = json.loads((AUTHOR / 'fixed-source-receipt.json').read_bytes())
assert freeze['fixed_commit'] == BASE and len(freeze['files']) == 29
assert freeze['production_files'] == 14 and freeze['history_files'] == 15 and not freeze['project_code_imported_or_executed']
names = list(freeze['files'])
batch = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
    input=('\n'.join(BASE + ':' + name for name in names) + '\n').encode(), capture_output=True, check=True).stdout
offset = 0; texts = {}; history = {}
for name in names:
    proof = freeze['files'][name]
    end = batch.index(b'\n', offset); header = batch[offset:end].split()
    assert header[1] == b'blob' and header[0].decode() == proof['git_blob']
    size = int(header[2]); raw = batch[end + 1:end + 1 + size]; offset = end + size + 2
    assert raw == (AUTHOR / proof['archive_path']).read_bytes()
    assert sha(raw) == proof['sha256'] and len(raw) == proof['bytes'] and proof['source_commit'] == BASE
    texts[name] = raw.decode().replace('\r\n', '\n')
    if name.startswith('research/') and name.endswith('.json'):
        history[name] = json.loads(raw)
assert offset == len(batch)
history_saved = json.loads((AUTHOR / 'historical-saved-receipts-read.json').read_bytes())
assert len(history) == len(history_saved) == 5 and canon(history) == canon(history_saved)
guard_saved = json.loads((AUTHOR / 'guard-function-excerpts.json').read_bytes())
assert len(guard_saved) == 18
for proof in guard_saved:
    tree = ast.parse(texts[proof['source_path']]); body = tree.body
    for part in proof['function'].split('.'):
        node = next(n for n in body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == part)
        body = node.body
    assert node.lineno == proof['line'] and node.end_lineno == proof['end_line']
    assert ast.get_source_segment(texts[proof['source_path']], node) == proof['source']
inventory_saved = json.loads((AUTHOR / 'numeric-call-ast-inventory.json').read_bytes())
rebuilt = []
for name in [name for name in names if name.startswith('rouge/')]:
    tree = ast.parse(texts[name]); parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node): parents[child] = node
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or ast.unparse(node.func) not in ('float', 'math.isfinite', 'finite', 'self.value', 'self.option', 'nonnegative'):
            continue
        scopes = []; parent = node
        while parent in parents:
            parent = parents[parent]
            if isinstance(parent, (ast.FunctionDef, ast.ClassDef)): scopes.append(parent.name)
        rebuilt.append({'source_path': name, 'scope': '.'.join(reversed(scopes)), 'line': node.lineno, 'call': ast.unparse(node)})
assert len(rebuilt) == len(inventory_saved) == 133
assert Counter(map(canon, rebuilt)) == Counter(map(canon, inventory_saved))
findings = json.loads((AUTHOR / 'findings.json').read_bytes())
assert findings['fixed_commit'] == BASE and findings['confirmed_missing_public_float_consumer_guards'] == findings['actionable_candidates'] == []
assert all(v == 0 for v in findings['counters'].values())
assert findings['limits'] == handoff['limits']
scope = {'status': 'PASS_BOUNDED_SOURCE_ARTIFACTS_ONLY', 'fixed_commit': BASE,
    'sealed_author_files_rehashed': 38, 'sealed_author_bytes': 783429, 'git_blob_sources_verified': 29,
    'production_files': 14, 'history_files': 15, 'full_guard_excerpts_reconstructed_from_AST': 18,
    'numeric_call_sites_independently_rebuilt': 133, 'historical_saved_JSON_receipts_exact': 5,
    'historical_receipts_are_current_fixed_commit_copies_of_previous_execution_evidence': True,
    'saved_history_does_not_prove_new_current_runtime': True, 'actionable_missing_guard_candidates': [],
    'negative_claim_scope': 'No source-supported absent finite gate confirmed in the bounded traced consumer paths. This is not a proof over every public field, dynamic path, or derived arithmetic result.',
    'no_fresh_NaN_inf_or_overflow_execution': True, 'native_state_clock_attachment_verified': False,
    'new_numeric_bounds_type_contracts_from_UI_ranges': False,
    'new_API_project_helper_tests_Qt_Wine_matrix_product_patch_tracked': 0,
    'section_086_boolean_module_qualification_probe_search_repeated': False,
    'manifest_sha256': sha(raw_manifest), 'handoff_sha256': sha(raw_handoff)}
(OUT / 'fixed-artifacts-review085.json').write_text(json.dumps(scope, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(scope, ensure_ascii=False))
