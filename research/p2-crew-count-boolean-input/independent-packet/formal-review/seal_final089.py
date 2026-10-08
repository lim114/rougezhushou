"""One final external89 seal; read-only bytes/git transport, no project calls."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
REPO = Path('/workspace/rougezhushou')
MANIFEST = OUT / 'final-public-artifacts-manifest089.json'
HANDOFF = OUT / 'final-handoff089.json'
assert not MANIFEST.exists() and not HANDOFF.exists()

def binding(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'archive_path': path.relative_to(ROOT).as_posix(),
            'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

prep = ROOT / 'source-preparation-manifest089.json'
assert binding(prep)['sha256'] == '3190bfc20b83c71648702bd83ba654ba89ea5c6844fd7718a2f6fbccdef2bce4'
source_manifest = json.loads(prep.read_bytes())
assert len(source_manifest['files']) == 49
for row in source_manifest['files']:
    path = Path(row['source_path'])
    assert path.is_relative_to(ROOT)
    actual = binding(path)
    assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']

formal = json.loads((OUT / 'independent-formal-review089.json').read_bytes())
assert formal['status'].startswith('PASS_')
assert formal['actual_constructor_entries'] == 20 and formal['actual_apply_entries'] == 30
assert formal['frozen_newtests_once']['pass'] == 7
static = json.loads((OUT / 'frozen-draft-static-review089.json').read_bytes())
assert static['status'].startswith('PASS_')
saved = json.loads((OUT / 'author71-saved38-review089.json').read_bytes())
assert saved['status'].startswith('PASS_') and saved['imported_files'] == 71 and saved['saved_record_count'] == 38
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
old = (OUT / 'frozen-draft-snapshots/baseline/rouge/run_state.py').read_bytes()
current = subprocess.check_output(['git', '-C', str(REPO), 'show', head + ':rouge/run_state.py'])
assert current == old
registry = subprocess.check_output(['git', '-C', str(REPO), 'show', head + ':scripts/verify_cloud.py'])
assert registry.count(b'MODULES = (\n') == 1 and b'tests.test_run_crew_count_boolean_input' not in registry
transport = {'status': 'PASS_CURRENT_COMMITTED_RUNSTATE_BASELINE_EXACT_ONLY',
    'actual_root_commit_at_seal': head, 'run_state_bytes': len(current),
    'run_state_sha256': hashlib.sha256(current).hexdigest(),
    'registry_current_sha256': hashlib.sha256(registry).hexdigest(),
    'registry_scope': 'Root adapts one newmodule literal to actual current88 registry; no registry/working tree mutation here.',
    'product_baseline_source_commit': '0f27027e7e1f49c08f298706b599e310e299238b',
    'author_transport_commit': '1ce970fd30aa3b42d8ef787cde02513f05682b66',
    'new_project_calls': 0}
with (OUT / 'current-committed-transport089.json').open('x', encoding='utf-8') as stream:
    json.dump(transport, stream, ensure_ascii=False, indent=2)
    stream.write('\n')

handoff = {'status': 'FINAL_SEALED_PASS_INDEPENDENT089_SOURCE_SAVED_NATIVE_STATE_DISK_AND_ORIGINAL7',
    'packet_root': str(ROOT), 'public_manifest': str(MANIFEST),
    'author_final_manifest_sha256': saved['manifest_sha256'],
    'author_final_handoff_sha256': saved['handoff_sha256'],
    'source_preparation_manifest': binding(prep),
    'static_receipt': binding(OUT / 'frozen-draft-static-review089.json'),
    'author71_saved38_receipt': binding(OUT / 'author71-saved38-review089.json'),
    'independent_formal_receipt': binding(OUT / 'independent-formal-review089.json'),
    'preparation_diagnostics': binding(OUT / 'preparation-diagnostics089.json'),
    'current_committed_transport': binding(OUT / 'current-committed-transport089.json'),
    'counts': {'fresh_independent_constructor': 20, 'fresh_independent_apply': 30,
        'complete_native_records': 50, 'old_draft_pairs': 3, 'frozen_new_test_methods': 7,
        'new_tests_pass': 7, 'new_tests_skip': 0, 'fresh_pair_seed_apply': 0,
        'author_record_constructor': 14, 'author_record_apply': 24,
        'author_source_record_constructor': 5, 'author_source_record_apply': 10,
        'author_calls_not_repeated': True, 'independent_passed_baseline_not_repeated': True},
    'exact_native_scope': 'Each pair uses the same actual persisted seed bytes/UUID/time; full native state and caller trees are saved before JSON. Two pairs onlycounttype/value differs; priorerrorpair whole-native/rawdisk exact.',
    'other_calls': formal['other_calls'],
    'failure_scope': 'All preparation diagnostics explicit; original cache traceback retained but raw failed-script copy unavailable. Fixed loader copy not represented as failed original.',
    'remaining_root_work': ['Current working tree/patch transport and88 registry insertion',
        'Root sole product/test integration', 'Root related/selected validation', 'Root section89 commit/archive', 'Root eventualactualUI90'],
    'limits': formal['limits'],
    'stop_writing_all_manifest_listed_files': True,
    'seal_time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
with HANDOFF.open('x', encoding='utf-8') as stream:
    json.dump(handoff, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
files = sorted(path for path in ROOT.rglob('*') if path.is_file() and path != MANIFEST)
assert all(not path.is_symlink() for path in files)
rows = [binding(path) for path in files]
manifest = {'version': 1, 'status': handoff['status'], 'files': rows,
    'file_count': len(rows), 'total_bytes': sum(row['bytes'] for row in rows),
    'self_excluded': True, 'handoff_included': True,
    'actual_calls_at_seal': {'constructor': 20, 'apply': 30, 'new_test_methods': 7},
    'sealing_new_project_calls': 0, 'immutable': True}
with MANIFEST.open('x', encoding='utf-8') as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
for row in rows:
    path = Path(row['source_path'])
    assert binding(path) == row
print(json.dumps({'status': handoff['status'], 'manifest': binding(MANIFEST),
    'handoff': binding(HANDOFF), 'formal_receipt': binding(OUT / 'independent-formal-review089.json'),
    'file_count': len(rows), 'total_bytes': manifest['total_bytes'],
    'constructors': 20, 'apply': 30, 'newtests_pass': 7, 'newcalls_at_seal': 0}, ensure_ascii=False))
