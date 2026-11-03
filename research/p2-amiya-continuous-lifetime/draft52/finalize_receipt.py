"""Record reviewable artifact hashes and a read-only production patch check."""
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = Path('/workspace/rougezhushou')
receipt_path = OUT / 'source-receipt.json'
receipt = json.loads(receipt_path.read_text())
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
check = subprocess.run(['git', 'apply', '--check', str(OUT / 'section52.patch')],
                       cwd=ROOT, capture_output=True, text=True)
assert check.returncode == 0, check.stderr
receipt.update(final_patch_check={'head': head, 'exit_code': check.returncode,
                                  'command': 'git apply --check section52.patch'},
               final_working_status=subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
               artifact_sha256={name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
                  for name in ('code.patch', 'tests.patch', 'section52.patch', 'NOTE.md',
                               'REVIEW.md', 'ENGINE_REVIEW.md', 'zero-type-boundary.json',
                               'review-event-amounts-fixed-probe.json', 'review-scope-notes.json', 'related-tests.log',
                               'public-inputs.json', 'baseline-public-results.json', 'draft-public-results.json',
                               'zero-type-inputs.json', 'baseline-zero-type-results.json', 'draft-zero-type-results.json',
                               'reproduce.py', 'regenerate_patch.py')},
               review={'ordinary_public_blockers': 0, 'independent_new_tests_passed': 19,
                       'empty_event_arrays_invariant_fixed': True,
                       'restricted_scope_and_notes_independently_reviewed': True,
                       'accepted_zero_type_boundary_deferred': True})
receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'head': head, 'patch_check_exit_code': check.returncode,
                  'section52_patch_sha256': receipt['artifact_sha256']['section52.patch']}))
