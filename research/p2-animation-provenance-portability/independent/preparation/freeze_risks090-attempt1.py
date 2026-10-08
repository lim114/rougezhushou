"""Static independent preparation; does not import or run the candidate."""
import ast
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/p2-animation-provenance-portability-090-draft')
SOURCE = Path('/workspace/.continuation/p2-animation-provenance-portability-090-source')
REPO = Path('/workspace/rougezhushou')
ROOT87 = '6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def description(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}

def save(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

assert not (HERE / 'risk-plan-frozen090.json').exists()
for name, expected in (
    ('archivable-author-review-manifest090.json', 'ca67748838191ddf110cec897be199799f4ee7657a3af667355908db2ddea47c'),
    ('author-review-handoff090.json', 'cd2a90ecbd89baec7716d5abc63fde414bc2799db490aaa3587073a1253777ce'),
    ('review-freeze090.json', 'e0f5fd4f72a1fafbca959d06365e3eaab842713e3b76112bba56c65a4542b4a2')):
    raw = (AUTHOR / name).read_bytes()
    assert sha(raw) == expected
    target = HERE / 'author-bound' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
author_manifest = json.loads((AUTHOR / 'archivable-author-review-manifest090.json').read_bytes())
source_manifest = json.loads((SOURCE / 'public-artifacts-manifest-source090.json').read_bytes())
assert len(author_manifest['files']) == 62 and len(source_manifest['files']) == 28
verified_manifests = []
for origin, manifest in ((AUTHOR, author_manifest), (SOURCE, source_manifest)):
    for row in manifest['files']:
        raw = Path(row['source_path']).read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    verified_manifests.append({'directory': str(origin), 'files': len(manifest['files']), 'all_row_bytes_sha256_match': True})
freeze = json.loads((AUTHOR / 'review-freeze090.json').read_bytes())
for row in freeze['product_files']:
    source = AUTHOR / 'draft' / row['path']
    raw = source.read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    target = HERE / 'candidate' / row['path']
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
for name in ('product090.patch', 'author-plan090.json', 'new-tests-operation090.json',
        'precheck-operation090.json', 'source-transport-619090.json', 'registry-proposal090.json'):
    target = HERE / 'author-bound' / name
    target.write_bytes((AUTHOR / name).read_bytes())
for name in ('public-artifacts-manifest-source090.json', 'final-handoff-source090.json'):
    target = HERE / 'source28-bound' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((SOURCE / name).read_bytes())
script = HERE / 'candidate/scripts/verify_original_animation_provenance.py'
tree = ast.parse(script.read_bytes())
imports = []
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        imports.extend(alias.name for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        imports.append(node.module)
assert set(imports) == {'__future__', 'argparse', 'gzip', 'hashlib', 'json', 'math', 'pathlib', 're'}
constants = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        try:
            constants[node.targets[0].id] = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            pass
required = constants['REQUIRED_LEAVES']
assert len(required) == 6
assert constants['PACKET_SHA'] == 'db2679793321d9d4a0f817757c53d93f88a16c4d4261f65f54223f69fb8b5265'
assert constants['EXTRACTION_SHA'] == '2b3785b65d526bf74329f249b90bf2034c02eb79708e25ec12bdebe73709dd77'
frame_builder = SOURCE / 'source-snapshots/scripts/build_original_animation_048.py'
canonical = ast.parse(frame_builder.read_bytes())
oldframes = next(n for n in canonical.body if isinstance(n, ast.FunctionDef) and n.name == 'frames')
newframes = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'frames')
class ResolvePolicy(ast.NodeTransformer):
    def visit_Name(self, node):
        return ast.copy_location(ast.Constant({'FPS': 30, 'EPSILON_FRAMES': 1e-5}[node.id]), node) if node.id in {'FPS', 'EPSILON_FRAMES'} else node
oldframes = ResolvePolicy().visit(oldframes)
assert ast.dump(oldframes, include_attributes=False) == ast.dump(newframes, include_attributes=False)
(HERE / 'source28-bound/build_original_animation_048.py').write_bytes(frame_builder.read_bytes())

packet_relative = 'research/p2-gummy-back-animation-reference/source-packet087'
plan = json.loads((AUTHOR / 'author-plan090.json').read_bytes())
fixture_rows = []
for row in plan['public_fixtures']:
    raw = (AUTHOR / 'draft' / row['path']).read_bytes()
    named = subprocess.check_output(['git', 'show', f'{ROOT87}:{row["path"]}'], cwd=REPO)
    assert raw == named and len(raw) == row['bytes'] and sha(raw) == row['sha256']
    target = HERE / 'public-fixture090' / row['path']
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    fixture_rows.append({'source_path': str(target), 'root_relative_path': row['path'],
        'bytes': len(raw), 'sha256': sha(raw),
        'git_blob_sha1': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(),
        'named_actual_root_commit': ROOT87, 'no_synthetic_leaf_or_manifest_hash_change': True})
assert len(fixture_rows) == 8
packet = HERE / 'public-fixture090' / packet_relative
manifest = json.loads((packet / 'public-artifacts-manifest087.json').read_bytes())
index = {row['archive_path']: row for row in manifest['files']}
for relative in required:
    raw = (packet / relative).read_bytes()
    assert len(raw) == index[relative]['bytes'] and sha(raw) == index[relative]['sha256']
data_raw = (HERE / 'public-fixture090/rouge/data/original-animation-references.json').read_bytes()
data = json.loads(data_raw)
baseline_raw = gzip.decompress((packet / 'history/original-animation-references.json.gz').read_bytes())
baseline = json.loads(baseline_raw)
inverse = json.loads(data_raw)
inverse['operators']['char_196_sunbr']['records'] = [r for r in inverse['operators']['char_196_sunbr']['records'] if r['orientation'] != 'Back']
inverse['operators']['char_196_sunbr']['missing_sources'] = baseline['operators']['char_196_sunbr']['missing_sources']
inverse['counts'] = constants['OLD_COUNTS']
del inverse['source_additions']
inverse_bytes = (json.dumps(inverse, ensure_ascii=False, indent=2) + '\n').replace('\n', '\r\n').encode()
assert inverse_bytes == baseline_raw and sha(baseline_raw) == constants['BASELINE_SHA']
backs = [r for r in data['operators']['char_196_sunbr']['records'] if r['orientation'] == 'Back']
assert [r['animation'] for r in backs] == ['Attack', 'Default', 'Idle', 'Skill', 'Start']
assert all(r['runtime_binding_verified'] is False for r in backs)
generic = next(r for r in backs if r['animation'] == 'Skill')
assert 'skill_number' not in generic and generic['id'] == 'char_196_sunbr:Back:Skill'
verify_fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'verify')
assert not any(isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and n.slice.value == 'source_path' for n in ast.walk(verify_fn))
read_modes = [ast.unparse(n) for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ('write_bytes', 'write_text', 'unlink', 'open', 'mkdir')]
assert read_modes == []
assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ('exec', 'eval', 'compile', '__import__') for n in ast.walk(tree))
assert '.local' not in script.read_text()
newreadme = (HERE / 'candidate/README.md').read_bytes()
oldreadme = (AUTHOR / 'baseline/README.md').read_bytes()
assert newreadme.startswith(oldreadme)
patch_paths = [line.split(b' b/', 1)[1].decode() for line in (AUTHOR / 'product090.patch').read_bytes().splitlines() if line.startswith(b'diff --git ')]
assert set(patch_paths) == {'scripts/verify_original_animation_provenance.py', 'tests/test_original_animation_provenance.py', 'README.md'}
operation = json.loads((AUTHOR / 'new-tests-operation090.json').read_bytes())
assert operation['author_total_verifier_entries'] == 28 and operation['tests_run'] == 6 and operation['passed'] is True
save('independent-static-review090.json', {
    'status': 'PASS_INDEPENDENT_STATIC_PENDING_FOUR_NEW_DIRECT_RISKS', 'passed': True,
    'bound_author_immutable_manifest': description(AUTHOR / 'archivable-author-review-manifest090.json'),
    'bound_author_handoff': description(AUTHOR / 'author-review-handoff090.json'),
    'author62_and_source28_manifests_all_rows_exact': verified_manifests,
    'root619_actual_8_inputs_and_six_manifest_leaves_exact': True,
    'stdlib_only_imports': imports, 'candidate_reads_archive_path_not_historical_source_path': True,
    'safe_relative_path_fixed_manifest_then_resolve_containment': True,
    'no_mutable_manifest_pin_test_claim': True, 'no_private_source_paths_or_write_calls': True,
    'frame_AST_exact_existing_policy_30_and_1e5': True,
    'baseline923_full_inverse_bytes_exact': True, 'baseline_bytes': len(baseline_raw),
    'Back5_no_runtime_and_GenericSkill_not_numbered': True,
    'patch_three_files_no_gameplay_or_original_data_changes': patch_paths,
    'README_prefix_inverse_exact': True, 'author28_and_six_tests_reused_not_reexecuted': True,
    'fresh_verifier_entries': 0, 'fresh_application_API_helper_formatter_parser_network_Qt_Wine': 0,
    'actual_root89_registry_transport_required_not_currently_certified': True})
save('public-fixture-root619-reconstruction090.json', {
    'status': 'PASS_EIGHT_BYTE_EXACT_NAMED_ROOT619_PUBLIC_INPUTS', 'files': fixture_rows,
    'rebuild_using': 'git cat-file blob <git_blob_sha1> and root_relative_path; every original sixleaf+manifest and references byte is immutable',
    'omit_duplicate_input_tree_from_formal_manifest': True})

risks = [
    {'id': 'R1-runtime-false-is-int-zero', 'record_id': 'char_196_sunbr:Back:Attack',
     'key': 'runtime_binding_verified', 'old': {'type': 'bool', 'value': False},
     'new': {'type': 'int', 'value': 0}, 'expected_code': 'binding_scope_mismatch',
     'different_from_author': 'Author tested bool True, not equality alias integer0'},
    {'id': 'R2-extraction-hash-addition-field', 'pointer': ['source_additions', 0, 'extraction_sha256'],
     'old': {'type': 'str', 'value': data['source_additions'][0]['extraction_sha256']},
     'new': {'type': 'str', 'value': '0' * 64}, 'expected_code': 'addition_metadata_mismatch',
     'different_from_author': 'Only mutable references addition metadata changes; all actual extraction/packet leaves and manifest hash remain exact'},
    {'id': 'R3-single-addition-nondict', 'pointer': ['source_additions', 0],
     'old': {'type': 'dict', 'whole_sha256': sha(json.dumps(data['source_additions'][0], ensure_ascii=False).encode())},
     'new': {'type': 'list', 'value': []}, 'expected_code': 'addition_metadata_mismatch',
     'different_from_author': 'One malformed existing addition; not author additional unsupported scope'},
    {'id': 'R4-Front-eligibility-is-int-one', 'record_id': 'char_196_sunbr:Front:Attack',
     'key': 'selectable_as_conventional_reference', 'old': {'type': 'bool', 'value': True},
     'new': {'type': 'int', 'value': 1}, 'expected_code': 'invalid_data',
     'different_from_author': 'Front eligibility alias, leaving all Back derived fields untouched; not author preview bool mutation'}]
save('risk-plan-frozen090.json', {
    'format_version': 1, 'status': 'FROZEN_BEFORE_ANY_FRESH_VERIFIER_CALL',
    'candidate_script': description(script), 'author_freeze': description(AUTHOR / 'review-freeze090.json'),
    'named_root619_inputs': description(HERE / 'public-fixture-root619-reconstruction090.json'),
    'static_receipt': description(HERE / 'independent-static-review090.json'),
    'maximum_fresh_verifier_entries': 4, 'fresh_CLI_invocations_planned': 0,
    'fresh_direct_verifier_entries_planned': 4, 'risk_count': len(risks), 'risks': risks,
    'all_mutations_only_external_public_references_copies': True,
    'manifest_and_six_original_leaves_remain_exact': True,
    'no_source_manifest_or_leaf_hash_rebinding': True,
    'author28_six_tests_or_source28_old_matrices_repeats': 0,
    'application_API_helper_formatter_parser_network_Qt_Wine_calls_planned': 0,
    'root89_tracked_apply_or_registry_rebase_not_performed': True})
print(json.dumps({'status': 'FROZEN_FOUR_DIFFERENT_DIRECT_RISKS',
    'plan': description(HERE / 'risk-plan-frozen090.json'),
    'static': description(HERE / 'independent-static-review090.json')}, ensure_ascii=False))
