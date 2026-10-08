"""Freeze the proposed CLI/test bytes and static inverse before any execution."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
SOURCE = Path('/workspace/.continuation/p2-animation-provenance-portability-090-source')
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def save(name, value):
    with (OUT / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


paths = ['scripts/verify_original_animation_provenance.py',
         'tests/test_original_animation_provenance.py', 'README.md']
files = []
trees = {}
for rel in paths:
    raw = (OUT / 'draft' / rel).read_bytes()
    if rel.endswith('.py'):
        assert b'\r\n' not in raw
        trees[rel] = ast.parse(raw, filename=rel)
    files.append({'path': rel, 'bytes': len(raw), 'sha256': sha(raw)})

script = trees[paths[0]]
stdlib_imports = []
for node in script.body:
    if isinstance(node, ast.Import):
        stdlib_imports.extend(alias.name for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        stdlib_imports.append(node.module)
assert set(stdlib_imports) == {'__future__', 'argparse', 'gzip', 'hashlib', 'json', 'math', 'pathlib', 're'}
tests = trees[paths[1]]
methods = [node.name for parent in tests.body if isinstance(parent, ast.ClassDef)
           for node in parent.body if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
assert len(methods) == 6

canonical = ast.parse((SOURCE / 'source-snapshots/scripts/build_original_animation_048.py').read_bytes())
canonical_frames = next(node for node in canonical.body if isinstance(node, ast.FunctionDef) and node.name == 'frames')
proposed_frames = next(node for node in script.body if isinstance(node, ast.FunctionDef) and node.name == 'frames')


class ResolvePolicyConstants(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id in {'FPS', 'EPSILON_FRAMES'}:
            return ast.copy_location(ast.Constant(30 if node.id == 'FPS' else 1e-5), node)
        return node


canonical_frames = ResolvePolicyConstants().visit(canonical_frames)
assert ast.dump(canonical_frames, include_attributes=False) == ast.dump(proposed_frames, include_attributes=False)
base_readme = (OUT / 'baseline/README.md').read_bytes()
new_readme = (OUT / 'draft/README.md').read_bytes()
assert new_readme.startswith(base_readme)
base_registry = (OUT / 'baseline/scripts/verify_cloud.py').read_bytes()
proposal = json.loads((OUT / 'registry-proposal090.json').read_bytes())
literal = proposal['new_entry_literal'].encode()
registered = (OUT / 'registered-verify_cloud090.py').read_bytes()
assert registered.count(literal) == 1 and registered.replace(literal, b'', 1) == base_registry
patch = (OUT / 'product090.patch').read_bytes()
result = subprocess.run(['git', 'apply', '--check', str(OUT / 'product090.patch')], cwd=ROOT,
                        capture_output=True, text=True)
assert result.returncode == 0, result.stderr
source_manifest = (SOURCE / 'public-artifacts-manifest-source090.json').read_bytes()
source_handoff = (SOURCE / 'final-handoff-source090.json').read_bytes()
assert sha(source_manifest) == 'd5d12ae2aaa8d2713a03abb400d4b50cc9973093841b43e91d335d5bba4ecb33'
assert sha(source_handoff) == '6dc5dbd02b4a692f022bb6f586dd4688f4fc2a7ff708e1a4acf28b84bfb1b5bd'
save('review-freeze090.json', {
    'format_version': 1, 'status': 'FROZEN_BEFORE_FIRST_NEW_TEST_EXECUTION',
    'baseline_commit': '6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0',
    'product_files': files, 'patch_bytes': len(patch), 'patch_sha256': sha(patch),
    'patch_apply_check_passed': True, 'new_test_method_names': methods,
    'frame_function_ast_exactly_matches_existing_builder_after_resolving_30_and_epsilon': True,
    'stdlib_imports_only': stdlib_imports,
    'README_inverse_exact': True, 'registry_inverse_exact': True,
    'existing_gameplay_files_touched': False,
    'source_proposal_manifest_sha256': sha(source_manifest),
    'source_proposal_handoff_sha256': sha(source_handoff),
    'source_proposal_snapshot28_unchanged_not_reexecuted': True,
    'author_budget': {'normal_CLI_precheck': 1, 'new_tests_CLI': 10,
                      'new_tests_direct_verify': 17, 'total_verify_entries_maximum': 28},
    'source_parser_network_application_API_project_helper_formatter_Qt_Wine_calls': 0,
    'test_executions_so_far': 0,
    'actual_root89_source_transport_pending': True})
print(json.dumps({'frozen_before_tests': True, 'new_test_methods': 6,
                  'frames_AST_policy_exact': True, 'patch_apply_check': True,
                  'planned_total_verifier_entries': 28, 'tests_executed': 0}))
