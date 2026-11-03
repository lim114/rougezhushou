"""Check sealed bytes and receipts, then copy one runner; never execute Qt/API."""
import ast
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
SRC = Path('/workspace/.continuation/ui-085-draft')
OUT = Path('/workspace/.compat')
FROZEN = '2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'

def sha(data):
    return hashlib.sha256(data).hexdigest()

spec = json.loads(Path(sys.argv[1]).read_text())
assert Path.cwd() == ROOT
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == FROZEN
assert subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip() == 'codex/p2-development'
assert not subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip()
assert not (OUT / 'root-ui-preflight-085.json').exists()
for name in ('wine-ui-smoke-085.py', 'wine-ui-085.json', 'wine-ui-085-process.log', 'wine-window-085.png'):
    assert not (OUT / name).exists(), name
for name, digest in spec['fixed_hashes'].items():
    path = Path(name)
    assert not path.is_absolute() and '..' not in path.parts
    assert sha((SRC / path).read_bytes()) == digest, name
manifest = json.loads((SRC / spec['public_manifest_name']).read_text())
assert manifest['format_version'] == 1 and len(manifest['files']) == spec['public_attachment_count']
archive_names = set()
for row in manifest['files']:
    name = Path(row['archive_path'])
    assert not name.is_absolute() and '..' not in name.parts and name.as_posix() not in archive_names
    archive_names.add(name.as_posix())
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], row['source_path']
review = json.loads((SRC / 'review-final085/final-static-and-saved1154-review085.json').read_text())
assert review['status'] == 'PASS_FINAL_STATIC_AND_ALL_SAVED1154_0_NEW_PRODUCT_CALLS'
assert review['root_commit'] == FROZEN and review['planned_actual_UI_case_count'] == 4217
assert review['complete_old3063_body_inverse_exact'] and review['source723_named_commit_bytes_verified']
assert review['public125_complete_named_git_blobs_verified'] and review['saved_three_texts_per_success']
assert review['successful_saved_results'] == 1130 and review['exact_existing_ValueError_rows'] == 24
assert not review['reviewer_application_API_calls'] and not review['reviewer_formatter_calls']
summary = json.loads((SRC / 'public-schema-final-085-summary.json').read_text())
assert summary['root_commit'] == FROZEN and not summary['source_drift']
assert summary['calls'] == 1154 and summary['unique_requested_calculation_inputs'] == 1086
assert summary['successful_result_rows'] == 1130 and summary['expected_existing_error_rows'] == 24
assert summary['formatter_text_requests'] == 3390 and summary['actual_formatter_function_entries'] == 4520
assert summary['formatter_entry_counts'] == {'format_estimate': 1130, 'format_report_default': 2260, 'format_report_technical': 1130}
assert summary['actual_API_call_attribution']['previous_completed_case_request_repeated_for_retry'] == 0
assert not summary['GUI_executed'] and not summary['Wine_executed']
runner = (SRC / 'wine-ui-smoke-085.py').read_bytes()
assert sha(runner) == review['final_runner_sha256'] == spec['fixed_hashes']['wine-ui-smoke-085.py']
assert runner.startswith(b"if __name__ == '__main__' and False:")
assert b"receipt['sections83_85_final_checks_pending']=True" not in runner
ast.parse(runner)
compile(Path('/workspace/.continuation/archive-full-085.py').read_bytes(), 'archive-full-085.py', 'exec')
ctx = json.loads((OUT / 'wine-validation-085-context.json').read_text())
assert ctx['commit'] == FROZEN and len(ctx['source_sha256']) == 723
actual = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
          for folder in ('rouge', 'tests', 'scripts') for p in (ROOT / folder).rglob('*')
          if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
assert actual == ctx['source_sha256']
git_entries = subprocess.check_output(['git', 'ls-tree', '-r', '-z', FROZEN]).split(b'\0')
blobs = {}
for entry in git_entries:
    if not entry:
        continue
    meta, name = entry.split(b'\t', 1)
    mode, kind, digest = meta.split()
    if kind == b'blob':
        blobs[name.decode()] = digest.decode()
proof = json.loads((SRC / 'root-source-085-proof.json').read_text())
assert proof['root_commit'] == FROZEN and len(proof['files']) == 723
assert {row['source_path'] for row in proof['files']} == set(actual)
for row in proof['files']:
    raw = (ROOT / row['source_path']).read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'] == actual[row['source_path']]
    assert blob == row['git_blob_sha1'] == blobs[row['source_path']]
freeze = json.loads((SRC / 'public-source-freeze-085.json').read_text())
assert freeze['base_commit'] == FROZEN and freeze['base_git_blobs_equal']
assert len(freeze['source_sha256']) == 125
assert freeze['base_source_sha256'] == freeze['source_sha256']
for name, digest in freeze['source_sha256'].items():
    assert actual[name] == digest
    assert sha((SRC / 'public-schema-085' / name).read_bytes()) == digest
for packet in spec.get('additional_readonly_audits', []):
    path = Path(packet['manifest_path'])
    assert sha(path.read_bytes()) == packet['manifest_sha256']
    info = json.loads(path.read_text())
    assert info['format_version'] == 1 and len(info['files']) == packet['files']
    for row in info['files']:
        raw = Path(row['source_path']).read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
shutil.copyfile(SRC / 'wine-ui-smoke-085.py', OUT / 'wine-ui-smoke-085.py')
assert sha((OUT / 'wine-ui-smoke-085.py').read_bytes()) == review['final_runner_sha256']
receipt = dict(spec)
receipt.update(passed=True, public_attachments_verified_before_actual_execution=len(manifest['files']),
               source_files_verified=723, public_git_blob_files_verified=125, source_commit=FROZEN,
               gui_execution_done_in_this_preflight=False, new_API_calls=0, new_formatter_calls=0,
               API_preflight_actual_calls=1154, planned_actual_UI_records=4217, native_windows=False)
(OUT / 'root-ui-preflight-085.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: receipt[key] for key in ('passed', 'public_attachments_verified_before_actual_execution',
    'source_files_verified', 'public_git_blob_files_verified', 'source_commit', 'new_API_calls', 'planned_actual_UI_records')}))
