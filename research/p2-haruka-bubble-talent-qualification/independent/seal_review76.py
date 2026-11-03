import hashlib
import json
from pathlib import Path

own = Path(__file__).parent
author = Path('/workspace/.continuation/p2-haruka-bubble-qualification-076')
original_base = Path('/workspace/.continuation/p2-haruka-bubble-qualification-audit-after-075/baseline153')
freeze = json.loads((own / 'final-author-freeze-receipt.json').read_text())
draft_freeze = json.loads((own / 'final-author-draft-freeze.json').read_text())
originals = json.loads((own / 'readonly-original-source-receipt.json').read_text())
def identity(path):
    raw = path.read_bytes()
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
checks = []
changed = []
for rel, expected in freeze['frozen_source_files'].items():
    for path in (original_base / rel, own / 'baseline153' / rel):
        assert identity(path) == expected, str(path)
    revised = identity(own / 'draft' / rel)
    assert revised == identity(author / 'draft' / rel), rel
    if revised != expected:
        changed.append(rel)
        assert revised == draft_freeze['draft_files'][rel]
    checks.append({'path': rel, 'baseline': expected, 'draft': revised})
assert changed == ['rouge/operator_engine.py']
new_file = 'tests/test_haruka_bubble_talent_qualification.py'
assert identity(own / 'draft' / new_file) == draft_freeze['draft_files'][new_file]
assert identity(author / 'draft' / new_file) == draft_freeze['draft_files'][new_file]
assert identity(own / 'final-author-changes.patch') == identity(author / 'changes.patch')
assert identity(author / 'changes.patch') == {k: draft_freeze['patch'][k] for k in ('sha256', 'bytes')}
raw_originals = {}
for name, source in originals['sources'].items():
    actual = identity(Path(source['path']))
    assert actual == {k: source[k] for k in ('sha256', 'bytes')}
    raw_originals[name] = actual
assert len(raw_originals) == 4
old = (own / 'baseline153' / 'rouge/operator_engine.py').read_bytes()
new = (own / 'draft' / 'rouge/operator_engine.py').read_bytes()
assert old.count(b'\n') == old.count(b'\r\n')
assert new.count(b'\n') == new.count(b'\r\n')
assert not list((own / 'baseline153').rglob('__pycache__'))
assert not list((own / 'draft').rglob('__pycache__'))
source_receipt = {'status': 'PASS', 'baseline_commit': freeze['baseline_commit'],
                  'verified_original_and_own_baseline_public_files': len(checks),
                  'verified_author_and_own_draft_public_files': len(checks) + 1,
                  'unchanged_old_public_files': len(checks) - len(changed),
                  'changed_production_files': changed, 'new_test_files': [new_file],
                  'files': checks, 'new_test_identity': draft_freeze['draft_files'][new_file],
                  'patch_identity': draft_freeze['patch'], 'raw_original_tables_rehashed': raw_originals,
                  'production_CRLF_preserved': True, 'no_generated_pycache_in_review_copies': True,
                  'root_tracked_author_draft_and_prior_sealed_evidence_not_modified': True,
                  'source_only_gate': {'uses_actual_selected_talent': True,
                                       'inactive_effective_count_is_float_0_0': True,
                                       'raw_declared_count_and_validation_unchanged': True,
                                       'only_two_dependent_emit_counts_modified': True,
                                       'positive_locked_note_only': True,
                                       'event_clock_or_native_attachment_added': False}}
(own / 'final-source-recheck76.json').write_text(json.dumps(source_receipt, ensure_ascii=False, indent=2) + '\n')
saved = json.loads((own / 'final-saved-comparison76.json').read_text())
fresh = json.loads((own / 'final-focused-comparison76.json').read_text())
tests = json.loads((own / 'final-tests76.json').read_text())
assert saved['status'] == fresh['status'] == tests['status'] == 'PASS'
receipt = {'status': 'PASS_SEALED', 'section': 76, 'baseline_commit': freeze['baseline_commit'],
           'patch': draft_freeze['patch'], 'source_scope': source_receipt['source_only_gate'],
           'source_recheck': identity(own / 'final-source-recheck76.json'),
           'design_review': identity(own / 'readonly-design-review.json'),
           'original_source_receipt': identity(own / 'readonly-original-source-receipt.json'),
           'fresh': {k: v for k, v in fresh.items() if k != 'details'},
           'saved_author_evidence_independently_compared': {k: v for k, v in saved.items() if k != 'details'},
           'tests': tests, 'limitations': [
               'No actual game event timing, first tick, native attachment or composition proof is inferred.',
               'E2 positive bursts, including zero attack, remain conditional unknown as before.',
               'Other independent pending healing/damage sources remain unchanged.',
               'This is external source/API review; no Wine, GUI, private/native binary or rolling root source execution.'],
           'harness_production_or_test_failures': 0,
           'read_shape_correction_from_initial_readonly_audit': 'Initial readonly record reader assumed every record accepted; all 20 accepted plus 4 error records subsequently classified and replayed exactly. This was a reader-shape correction, not a production failure.'}
(own / 'final-review76-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
text = '''# Section 76 independent review — PASS

Baseline is immutable commit `153b5dbf15d6567746047cbdea7f8d00a6879f3a`. Fixed patch SHA-256 is `215d29de8b5488d8dc5f92f6791ae5e5f001e0e36db82dae1c52e724ea6ac540` (11,598 bytes).

The original first talent 浮光泡影 exists from E0; bubble_bursts declares its ruptures. The second talent 扶摇花火 requires E2 level 1. Its bubble healing, and S2 damage derived from that healing, now use the declared count only when that talent is actually selected. Otherwise their count is float 0.0. Parsing, validation, the displayed declaration, ordinary healing, ordinary S2 damage, other conditional sources and all qualification error order stay unchanged. The only added explanation appears for a positive declaration without that selected talent.

Independent focused replay: 58 paired cases, 148 fresh public calculation calls including 16 zero controls per side. All original 24 discovery outcomes were reproduced. The 16 corrected cases match the original zero-count control in complete typed JSON after normalizing only the three declaration values and three exact added-note entries. The other 34 accepted outcomes and eight errors are completely unchanged. Full default/technical reports and the estimate formatter entry point were compared too. E2 S3 includes every unlocked module stage in both modes, plus zero attack; E2 potential 4/5 and module level 59/60 remain unchanged. No large calculation matrix was rerun.

The saved author evidence was independently decompressed and compared: 1,788 pairs, 588 corrected positive locked cases with 588 paired zero controls, 1,032 unchanged accepted outcomes, and 168 unchanged errors. This comparison executed zero new public calculation calls. Numeric integer/float types were compared using canonical JSON serialization.

Eight new and 29 related existing test methods passed (37 total, no failures/errors/skips). Post-test source verification matches all 711 baseline public files and 712 draft files against their immutable source/final draft. Exactly one production file changed, 710 old files stayed identical, and one test file was added. Four original public data tables were rehashed; CRLF is preserved.

Actual event placement, first ticks, native attachment and composition remain unproved. E2 positive declared events, including zero attack, retain their old unknown outcomes. Review copies only were modified; root tracked files, author evidence and previous sealed reviews were untouched. No GUI/Wine or private/native binary work was performed.
'''
(own / 'FINAL76_REVIEW.md').write_text(text)
paths = [p for p in own.iterdir() if p.is_file() and p.name not in ('final-artifact-hashes76.json', 'final-archive-list76.json')]
paths += [p for p in (own / 'readonly-source-selected').rglob('*') if p.is_file()]
archive_list = {'section': 76, 'relative_files': sorted(str(p.relative_to(own)) for p in paths),
                'excluded_whole_source_trees': ['baseline153', 'draft'],
                'author_may_copy_listed_files_without_modifying_this_original_directory': True}
(own / 'final-archive-list76.json').write_text(json.dumps(archive_list, ensure_ascii=False, indent=2) + '\n')
paths.append(own / 'final-archive-list76.json')
manifest = {'section': 76, 'status': 'SEALED', 'baseline_commit': freeze['baseline_commit'],
            'patch_sha256': draft_freeze['patch']['sha256'],
            'files': {str(p.relative_to(own)): identity(p) for p in sorted(paths)}}
(own / 'final-artifact-hashes76.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
for rel, expected in manifest['files'].items():
    assert identity(own / rel) == expected
print(json.dumps({'status': 'PASS_SEALED', 'manifest_files': len(manifest['files']),
                  'manifest': identity(own / 'final-artifact-hashes76.json'),
                  'receipt': identity(own / 'final-review76-receipt.json'),
                  'review': identity(own / 'FINAL76_REVIEW.md'),
                  'archive_list': identity(own / 'final-archive-list76.json'),
                  'source_recheck': identity(own / 'final-source-recheck76.json')}))
