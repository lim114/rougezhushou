"""Archive exact immutable candidates and their original failed review history."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
DEST = ROOT / 'research/p2-section093-account-cache-safety'
BASE = 'f509d186e501bfcfd042e45b46e398ec756840ec'
HELPER = ROOT / 'research/p2-section092-observation-window-workflow/root/root-archive092.py'
helper_bytes = HELPER.read_bytes()
assert helper_bytes == subprocess.check_output(['git', 'show', BASE + ':' + HELPER.relative_to(ROOT).as_posix()], cwd=ROOT)
source = helper_bytes.decode()
assert source.count('phase = sys.argv[1]') == 1
ns = {}
exec(compile(source.split('phase = sys.argv[1]', 1)[0], str(HELPER), 'exec'), ns)
ns['DEST'] = DEST
save_new, row, sealed, copy_rows = (ns[name] for name in ('save_new', 'row', 'sealed', 'copy_rows'))
phase = sys.argv[1]
if phase == 'prepare':
    assert not DEST.exists()
    packets = [
        ('p2-account-cache-candidate093-v1/public-artifacts-manifest-v1.json', '5c5fb72cc746e0a8673594928017e62b3a5935989f7be69d588e785bf229317b', 'candidate-v1-original-blocked', 'source_archive_rows'),
        ('p2-account-cache-candidate093-independent-v1/public-artifacts-manifest-v1.json', '6cf905c62d82aa25198c288659ed18196fa4314629f0fdd1b0c3038e83dbbaa6', 'independent-v1-original-blocked', 'local_archive_rows'),
        ('p2-account-cache-candidate093-v2/public-artifacts-manifest-v2.json', '1de97227f79be43751c1c6bc24a9fdc466305cc005403f1b208ae95b92becfc0', 'candidate-v2', 'source_archive_rows'),
        ('p2-account-cache-candidate093-independent-v2/public-artifacts-manifest-v2.json', '32512fc4f67647015e453a7cc0edf14f8df35614106d536c20ba7f82694df9c5', 'independent-v2', 'local_archive_rows'),
        ('ui-093-account-cache-final/public-artifacts-manifest-account-window093.json', '2e9b610e906016101ac6785791a7412e99b6574e46803038de2f9bb71f99d708', '', 'source_archive_rows'),
    ]
    rows = []
    for name, sha, prefix, style in packets:
        extra = [] if name.startswith('ui-') else ['final-handoff093.json']
        rows += sealed(LOCAL / name, sha, prefix, style, extra)
    directory = LOCAL / 'full095-account-fixture-transport-supplement'
    manifest_path = directory / 'public-artifacts-manifest-account-fixture-transport095.json'
    raw = manifest_path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '0349af738b449bc4dab3e6fd3ae05f12409c67b07e15bfb9daf7741841f42055'
    for item in json.loads(raw)['sealed_payload_files']:
        observed = row(Path(item['path']), 'future095-account-fixture-source-only/' + Path(item['path']).name)
        assert observed['bytes'] == item['bytes'] and observed['sha256'] == item['sha256']
        rows.append(observed)
    for name in ('public-artifacts-manifest-account-fixture-transport095.json', 'final-handoff-account-fixture-transport095.json'):
        rows.append(row(directory / name, 'future095-account-fixture-source-only/' + name))
    note = {'format_version': 1, 'status': 'SOURCE_ONLY_TRANSPORT_PLAN_NOT_COMPLETED95',
        'author_declared_errata_in_frozen_analysis': ['mechanism/myrtle means mechanist/myrtle', 'The named operator written as 棘刺 in one sentence is char_1048_orchd2 焰狐龙梓兰; exact IDs in source refs are authoritative.'],
        'original_frozen_packet_not_modified': True, 'plans_are_not_runtime_validation': True,
        'actual93v2_source_transport_and_tests_not_proof_old_full_window_unchanged': True,
        '95_positive_module_reference_source_qualification_still_pending': True,
        'project_calls': 0}
    save_new(LOCAL / 'root-full095-source-supplement-qualification093.json', note)
    for name in ('root-integrate093.py', 'root-integration-plan093.json', 'root-integration-applied093.json', 'root-source-093.json',
                 'root-related093.py', 'root-related-093.log', 'root-selected-093.log',
                 'ROOT_CURRENT_WORK_AFTER092.json', 'ROOT_CURRENT_WORK_093_IN_PROGRESS.json', 'PROGRESS_REPORT_AFTER092.md',
                 'root-full095-source-supplement-qualification093.json'):
        rows.append(row(LOCAL / name, 'root/' + name))
    rows.append(row(Path(__file__), 'root/' + Path(__file__).name))
    copy_rows(rows)
    save_new(LOCAL / 'root-archive-prepared093.json', {'format_version': 1,
        'status': 'SEALED_SOURCE_HISTORY_AND_FRESH_LINUX_LOGS_COPIED_ACTUAL_WINDOW_PENDING',
        'files': rows, 'file_count': len(rows), 'total_bytes': sum(item['bytes'] for item in rows),
        'reused_helper_actual92_Git_path': HELPER.relative_to(ROOT).as_posix(),
        'reused_helper_sha256': hashlib.sha256(helper_bytes).hexdigest(), 'project_calls': 0})
    print(json.dumps({'prepared_files': len(rows), 'bytes': sum(item['bytes'] for item in rows), 'project_calls': 0}))
elif phase == 'append':
    assert DEST.is_dir()
    spec = json.loads(Path(sys.argv[2]).read_bytes())
    copy_rows(spec['files'])
    print(json.dumps({'appended_files': len(spec['files']), 'project_calls': 0}))
else:
    raise ValueError(phase)
