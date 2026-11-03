import hashlib
import json
from pathlib import Path

BASE = Path('/workspace/.continuation')
PACKETS = (
    'p2-condition096-candidate-v1',
    'p2-condition096-final-formal-source-review-v1',
    'p2-condition096-validation-source-pending-v2',
    'condition096-validation-independent-source-review-v2',
    'p2-account-persistence-candidate-next-v1',
    'p2-account-persistence-independent-source-review-next-v1',
    'p2-account-persistence097-validation-source-plan-v1',
    'account097-validation-plan-independent-source-review-v1',
    'p2-after097-remaining-source-audit-v1',
    'p2-runstate-leads-root-probe-source-v1',
    'p2-runstate-leads-root-probe-actual-v1',
    'full095-ui-cache-profile-identity-source-proposal-v1',
    'full095-profile-identity-independent-source-review-v1',
    'full095-ui-cache-archive-final-review-source-preparation-v1',
    'full095-ui-cache-archive-final-review-source-preparation-v2',
)
ROOT_FILES = (
    'root-runstate-leads095-actual-v1-observation.json',
    'root-runstate-leads095-actual-v1-console.log',
    'root-runstate-leads095-actual-v1.exit-code',
    'root-record-runstate-leads095-observation-v1.log',
    'root-record-runstate-leads095-observation-v1.exit-code',
    'root-full095-code-hash-static-sample-proof-v1.py',
    'root-full095-code-hash-static-sample-proof-v1.json',
    'root-full095-code-hash-static-sample-proof-v1.log',
    'root-full095-code-hash-static-sample-proof-v1.exit-code',
    'root-full095-ui-cache-readonly-native-location-v1.py',
    'root-full095-ui-cache-readonly-native-location-v1.log',
    'root-full095-ui-cache-readonly-native-location-v1.exit-code',
    'root-full095-ui-cache-readonly-native-location-v2.py',
    'root-full095-ui-cache-readonly-native-location-v2.log',
    'root-full095-ui-cache-readonly-native-location-v2.exit-code',
    'ROOT_CURRENT_WORK_095_UI_CACHE_RETRY_PROGRESS_V2.json',
    'root-full095-ui-cache-progress-02-native-index.json',
    'root-record095-live-progress-v2.py',
    'root-record095-live-progress-v2.log',
    'root-record095-live-progress-v2.exit-code',
    'root-WORK_IN_PROGRESS-before095-ui-live-v2.bin',
)
def ref(path):
    assert path.is_file() and not path.is_symlink()
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

rows = []
packet_counts = {}
for name in PACKETS:
    packet = BASE / name
    assert packet.is_dir() and not packet.is_symlink()
    files = sorted(path for path in packet.rglob('*') if path.is_file())
    assert files
    packet_counts[name] = len(files)
    for path in files:
        assert not path.is_symlink() and '__pycache__' not in path.parts
        archive = 'continuation-public-preparation/' + name + '/' + path.relative_to(packet).as_posix()
        rows.append({'file': ref(path), 'archive_path': archive,
                     'qualification': 'Future Source preparation or separately identified past public lead observations; no numbered completion or full095 runtime gate is supplied by this file.'})
for name in ROOT_FILES:
    path = BASE / name
    rows.append({'file': ref(path), 'archive_path': 'continuation-public-preparation/root-observations/' + name,
                 'qualification': 'Root public temporary diagnostics, past lead collection, or still-running UI checkpoint; original primary/progress scope is retained.'})
assert len(rows) == len({row['archive_path'] for row in rows})
assert all(row['file']['bytes'] < 100 * 1024 * 1024 for row in rows)
result = {'status': 'EXPLICIT_PUBLIC_CONTINUATION_SUPPLEMENTS_PREPARED_NOT_ARCHIVED_OR_FULLPASS',
          'full095_available_validation_passed': False, 'commit_or_push_performed': False,
          'completed_section_increment': 0, 'future_actual096_097_098_guards': None,
          'scope': 'Explicitly named public Source packets and Root public diagnostics only; no private/runtime directory discovery, DLL or Python binary selection.',
          'packet_file_counts': packet_counts, 'rows': rows,
          'actual_files': len(rows), 'actual_total_bytes': sum(row['file']['bytes'] for row in rows)}
out = BASE / 'root-full095-public-continuation-supplements-v1.json'
with out.open('x', encoding='utf-8') as handle:
    json.dump(result, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
print(json.dumps({'selection': ref(out), 'actual_files': len(rows), 'actual_total_bytes': result['actual_total_bytes'],
                  'completed_section_increment': 0, 'fullPASS_or_commit_or_push': False}))
