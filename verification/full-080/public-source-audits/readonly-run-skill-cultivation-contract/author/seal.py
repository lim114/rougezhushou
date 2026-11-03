import hashlib, json, pathlib

OUT = pathlib.Path(__file__).resolve().parent
IND = OUT / 'independent'
ind_manifest = json.loads((IND / 'independent-final-public-manifest.json').read_bytes())
ind_manifest_sha = hashlib.sha256((IND / 'independent-final-public-manifest.json').read_bytes()).hexdigest()
assert ind_manifest_sha == '7363bc0d7652d33ce314ac41d16db29a318d386817e651c38811372394ce4172'
for name, expected in ind_manifest['files'].items():
    raw = (IND / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected['sha256'] and len(raw) == expected['bytes'], name
static = json.loads((IND / 'independent-flow-static-review.json').read_bytes())
handoff = {'schema_version': 1, 'status': 'READONLY_DEFER_SEALED', 'sealed_artifacts': True, 'baseline_head': 'a52a4bf9217aee3c11617135b7fc9cc6c38fd0f2', 'game_source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'not_a_completed_numbered_section': True, 'patch': None, 'conclusion_file': 'final-readonly-conclusion.json', 'conclusion_sha256': hashlib.sha256((OUT / 'final-readonly-conclusion.json').read_bytes()).hexdigest(), 'independent_final_manifest_sha256': ind_manifest_sha, 'independent_static_receipt_sha256': hashlib.sha256((IND / 'independent-flow-static-review.json').read_bytes()).hexdigest(), 'independent_files_verified': len(ind_manifest['files']), 'validation': {'author_public_calls': 72, 'author_accepted': 42, 'author_exact_errors': 30, 'author_method': 'immutable exact AST with synthetic controls; not actual Qt/client', 'independent_new_public_calls': 0, 'independent_tests': 0, 'independent_saved_records_read': 72, 'no_gate_changed': True}, 'bounded_claims': ['Current program flow and saved outcomes only.', 'No observed account-to-run native skill inheritance rule.', 'Source-layer audit alone does not establish absent future official/help evidence.', 'Original-scenario comparison is not an independent mutation check of the passed deepcopy.', 'Same synthetic rank for all three skills does not establish mixed per-skill-rank combinations.'], 'retained_preproduction_attempts': ['Single Linux full-app import missing win32gui; no retry and no fake native module.', 'Reviewer first harness syntax typo failed before execution; corrected once and original log retained.'], 'archive_manifest': 'public-artifacts-manifest-v1.json', 'no_private_state_no_tracked_edit_no_native_no_wine': True}
(OUT / 'handoff-receipt.json').write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
author_names = ('freeze.py', 'freeze75-receipt.json', 'flow_probe.py', 'flow_source_receipt.py', 'flow-source-selectors.json', 'FLOW_NOTE.md', 'synthetic-flow-public-whole-outcomes.json.gz', 'synthetic-flow-probe-receipt.json', 'synthetic-flow-controls.json', 'finalize.py', 'final-readonly-conclusion.json', 'seal.py', 'handoff-receipt.json')
docs = ('PROJECT_PROGRESS.md', 'research/p2-mei-airborne-module-reference/prior-readonly-audit/NOTE.md', 'research/p2-mei-airborne-module-reference/prior-readonly-audit/common-skill-public-contract.json', 'research/p2-mei-airborne-module-reference/prior-readonly-audit/lead-audit-receipt.json', 'research/p2-training-input-types/rebuild-receipt.json')
files = []
def add(source, archive):
    raw = source.read_bytes()
    files.append({'source_path': str(source), 'archive_path': archive, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
for name in author_names:
    add(OUT / name, 'readonly-run-skill-cultivation-contract/author/' + name)
for name in docs:
    add(OUT / 'prior-receipts' / name, 'readonly-run-skill-cultivation-contract/author/prior-receipts/' + name)
for name in list(ind_manifest['files']) + ['independent-final-public-manifest.json']:
    add(IND / name, 'readonly-run-skill-cultivation-contract/independent/' + name)
manifest = {'schema_version': 1, 'status': 'READONLY_DEFER_SEALED', 'not_a_completed_numbered_section': True, 'baseline_head': handoff['baseline_head'], 'scope': 'explicit public author and independent source/probe evidence; excludes frozen whole package and private cache/state', 'files': files}
(OUT / 'public-artifacts-manifest-v1.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'files': len(files), 'bytes': sum(f['bytes'] for f in files), 'handoff_sha256': hashlib.sha256((OUT / 'handoff-receipt.json').read_bytes()).hexdigest(), 'manifest_sha256': hashlib.sha256((OUT / 'public-artifacts-manifest-v1.json').read_bytes()).hexdigest(), 'independent_manifest_sha256': ind_manifest_sha, 'sealed': True}))
