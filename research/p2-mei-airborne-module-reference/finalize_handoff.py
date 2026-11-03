"""Seal explicit archivable public artifacts, without a full frozen checkout copy."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
status = sys.argv[1] if len(sys.argv) > 1 else 'pending'
freeze = json.loads((ROOT / 'draft-freeze.json').read_text())
matrix = json.loads((ROOT / 'matrix-comparison.json').read_text())
independent_path = ROOT.parent / 'p2-mei-airborne-module-reference-073-independent'
independent = None
if status == 'passed':
    independent = json.loads((independent_path / 'independent-review073.json').read_text())
    assert independent['status'] == 'independent_review_passed' and not independent['blockers']
    assert independent['patch_sha256'] == freeze['patch_sha256']
handoff = {
    'section_candidate': 73,
    'baseline_commit': freeze['baseline_commit'],
    'patch_path': str(ROOT / 'section073.patch'),
    'patch_sha256': freeze['patch_sha256'],
    'draft_path': str(ROOT / 'draft'),
    'source_receipt': str(ROOT / 'source-receipt.json'),
    'tests': {'new_methods': 8, 'related_old_methods': 40, 'passed_methods': 48,
              'log': str(ROOT / 'new-and-related-tests.log')},
    'paired_public_validation': matrix,
    'independent_review': {'status': status,
                           'path': str(independent_path),
                           **({'receipt_sha256': hashlib.sha256((independent_path / 'independent-review073.json').read_bytes()).hexdigest(),
                               'fresh_pairs': independent['fresh_paired_scenarios'],
                               'fresh_calls': independent['fresh_public_calls'],
                               'fresh_counts': independent['fresh_counts'],
                               'saved_whole_json_pairs_recompared': independent['saved_author_paired_scenarios_strictly_recompared'],
                               'new_tests_passed': independent['new_tests_independently_passed']}
                              if independent else {})},
    'implementation_scope': 'Qualified source-only conditional trait reference. No checkbox, numeric multiplier, target inference or native timing change.',
    'remaining_mechanism_unknowns': ['actual airborne target condition', 'native module attachment',
                                    'damage composition with skill and other modifiers', 'current live state'],
    'tracked_files_modified_by_author': False, 'gui_or_wine_executed_by_author': False,
    'archive_instructions': 'Copy exactly the public-artifacts-manifest.json files. Frozen baseline/draft dependency copies and pycache are not archive payloads.'}
(ROOT / 'handoff.json').write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
names = ['NOTE.md', 'source-receipt.json', 'section073.patch', 'draft-freeze.json', 'baseline-path.json',
         'handoff.json', 'collect_source.py', 'public_matrix.py', 'compare_matrix.py', 'finalize_handoff.py',
         'public-baseline.json.gz', 'public-draft.json.gz', 'matrix-comparison.json',
         'baseline-matrix.log', 'draft-matrix.log', 'new-and-related-tests.log',
         'initial-test-assumption-errors.log', 'initial-related-test-assumption-errors.log']
names += ['draft/' + name for name in freeze['draft_files']]
files = []
for name in names:
    path = ROOT / name
    files.append({'source_path': str(path), 'archive_path': name,
                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size})
if independent:
    for path in sorted(independent_path.iterdir()):
        if path.is_file():
            files.append({'source_path': str(path), 'archive_path': 'independent-review/' + path.name,
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size})
audit_path = ROOT.parent / 'p2-after-070-source-audit'
for name in ('NOTE.md', 'lead-audit-receipt.json', 'common-skill-public-contract.json',
             'null-module-candidate-leads.json', 'freeze070-receipt.json'):
    path = audit_path / name
    files.append({'source_path': str(path), 'archive_path': 'prior-readonly-audit/' + name,
                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size})
manifest = {'format_version': 1, 'baseline_commit': freeze['baseline_commit'],
            'files': files, 'file_count': len(files),
            'original_raw_sources': json.loads((ROOT / 'source-receipt.json').read_text())['source_files'],
            'original_raw_source_archive_note': 'Exact full bytes remain in the external public cache at cited paths and are reproducible from fixed commit URLs. Full relevant original records are included in source-receipt.json.'}
(ROOT / 'public-artifacts-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'independent': status, 'public_artifacts': len(files),
                  'manifest_sha256': hashlib.sha256((ROOT / 'public-artifacts-manifest.json').read_bytes()).hexdigest(),
                  'handoff_sha256': hashlib.sha256((ROOT / 'handoff.json').read_bytes()).hexdigest()}))
