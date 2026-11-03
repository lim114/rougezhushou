"""Copy explicit sealed public payloads, verifying every byte before writing."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
DEST = ROOT / 'research/p2-section092-observation-window-workflow'
def sha(data):
    return hashlib.sha256(data).hexdigest()
def check_name(name):
    path = Path(name)
    assert not path.is_absolute() and '..' not in path.parts
    return path.as_posix()
def row(source, name):
    source = Path(source)
    data = source.read_bytes()
    return {'source_path': str(source), 'archive_path': check_name(name), 'bytes': len(data), 'sha256': sha(data)}
def sealed(manifest_path, expected_sha, prefix, style, extra_metadata):
    path = Path(manifest_path)
    data = path.read_bytes()
    assert sha(data) == expected_sha, path
    obj = json.loads(data)
    output = []
    if style == 'source_archive_rows':
        entries = [(Path(item['source_path']), item['archive_path'], item) for item in obj['files']]
    elif style == 'local_archive_rows':
        entries = [(path.parent / item['archive_path'], item['archive_path'], item) for item in obj['files']]
    elif style == 'local_artifact_dict':
        entries = [(path.parent / name, name, item) for name, item in obj['artifacts'].items()]
    elif style == 'source_name_rows':
        entries = [(Path(item['path']), item['name'], item) for item in obj['sealed_payload_files']]
    else:
        raise ValueError(style)
    names = set()
    for source, name, expected in entries:
        observed = row(source, f'{prefix}/{name}' if prefix else name)
        assert observed['bytes'] == expected['bytes'] and observed['sha256'] == expected['sha256'], source
        assert observed['archive_path'] not in names
        names.add(observed['archive_path'])
        output.append(observed)
    for source, name in [(path, path.name)] + [(path.parent / item, item) for item in extra_metadata]:
        observed = row(source, f'{prefix}/{name}' if prefix else name)
        if observed['archive_path'] in names:
            assert next(item for item in output if item['archive_path'] == observed['archive_path']) == observed
        else:
            output.append(observed)
            names.add(observed['archive_path'])
    return output
def save_new(path, value):
    with path.open('xb') as stream:
        stream.write((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())
def copy_rows(rows):
    assert len(rows) == len({item['archive_path'] for item in rows})
    # Validate all sources before adding any destination file.
    for item in rows:
        data = Path(item['source_path']).read_bytes()
        assert len(data) == item['bytes'] and sha(data) == item['sha256']
        assert not (DEST / item['archive_path']).exists(), item['archive_path']
    for item in rows:
        target = DEST / item['archive_path']
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(Path(item['source_path']).read_bytes())
        assert sha(target.read_bytes()) == item['sha256']

phase = sys.argv[1]
if phase == 'prepare':
    assert not DEST.exists()
    rows = []
    packets = [
        ('p2-window-target-timing-flow-092-author/FINAL-manifest092.json', '1ccb6c01dd85d9a1d3e9f87e1158bb6c2de8b8d6ad1838f4e7c08d659f915f27', 'author', 'source_archive_rows', ['author-handoff092.json']),
        ('p2-window092-final-independent-review/FINAL-review-manifest092.json', '9da78b4b891d17bde487aed961a165a17998d300d4a56c9c3c83007abda75de3', 'independent', 'source_archive_rows', ['review-handoff092.json']),
        ('ui-092-focused-final/public-artifacts-manifest-focused-window092.json', '0f1fc034316a42f7958beab2a6b088eb2ab15e12454d8eb92561bc2faee1fff4', '', 'source_archive_rows', []),
        ('p2-account-cache-input-workflow-source093-v1/public-artifacts-manifest-v1.json', '7b36fa88b1748fb249e61d9f7093b7d9f3d7a16267c1a34416aee44a87bb4056', 'future093-source-only', 'source_archive_rows', ['final-handoff093.json']),
        ('p2-account-cache-design093-independent-v1/public-artifacts-manifest-v1.json', 'e551304fe3dd63aa4e30daa3adae579857ab6d9cc3428bbd3611d84bbcb2b908', 'future093-design-review-only', 'local_archive_rows', ['final-handoff093.json']),
        ('p2-offline-input-refresh-source094-v1/manifest094.json', '85bdf1afbddbcc1eb592adad40e3a285464ee95434f3cc526faa97ea21ea5481', 'future094-source-only', 'local_artifact_dict', []),
        ('full095-source-migration-plan/public-artifacts-manifest-source-plan095.json', '5af9bbd5c0d954d8d85bd6848505439cbca7bb092a0aee68b88fcceb83fc91c0', 'future095-source-plan-only', 'source_name_rows', ['final-handoff-source-plan095.json']),
    ]
    for name, digest, prefix, style, extra in packets:
        rows += sealed(LOCAL / name, digest, prefix, style, extra)
    recovery = json.loads((LOCAL / 'root-recovery-and-quota092.json').read_bytes())['recovery']
    recovery_record = {'format_version': 1, 'recorded_at': datetime.now(timezone.utc).isoformat(), 'current_recovery': recovery,
        'source730_before_product_apply_retained': True, 'active_rule': 'Original continuous work and 15 percent wrap-up rule; recent reset-card and2/5percent requests retracted by user.',
        'usage_interface_available': False, 'reset_executed': False, 'project_calls': 0,
        'readonly_filename_failure': {'command': 'cat research/p2-section091-attack-condition-regeneration/future092-source-and-unexecuted-candidate/candidate-flow092.patch', 'exit_code': 1,
            'reason': 'Root used an established basename in the wrong archive directory instead of reading its actual manifest archive_path.',
            'not_retried': True, 'blind_path_lookup_workflow_already_deferred': True, 'subsequent_reads_use_actual_manifest_rows_or_explicitly_verified_files': True,
            'project_or_product_effect': 0},
        'future_packets_093_094_095': 'Frozen preparations only; not completed sections. 93 candidate and94 integration/full95 execution still pending.'}
    save_new(LOCAL / 'root-recovery-final092.json', recovery_record)
    for name in ('root-integrate092.py', 'root-integration-plan092.json', 'root-integration-applied092.json', 'root-related092.py',
                 'root-verify-focused092.py', 'root-readonly-preparation-diagnostics092.json', 'root-recovery-final092.json',
                 'root-quota-retraction092.json', 'PROGRESS_REPORT_AFTER091.md', 'PROGRESS_REPORT_AFTER091.source-read.json'):
        rows.append(row(LOCAL / name, 'root/' + name))
    rows.append(row(Path(__file__), 'root/' + Path(__file__).name))
    copy_rows(rows)
    save_new(LOCAL / 'root-archive-prepared092.json', {'format_version': 1, 'status': 'SEALED_PUBLIC_PREPARATIONS_COPIED_ACTUAL_WINDOW_ARCHIVE_PENDING',
        'archive': str(DEST), 'files': rows, 'file_count': len(rows), 'total_bytes': sum(item['bytes'] for item in rows), 'project_calls': 0})
    print(json.dumps({'prepared_files': len(rows), 'bytes': sum(item['bytes'] for item in rows), 'project_calls': 0}))
elif phase == 'append':
    assert DEST.is_dir()
    spec = json.loads(Path(sys.argv[2]).read_bytes())
    copy_rows(spec['files'])
    print(json.dumps({'appended_files': len(spec['files']), 'project_calls': 0}))
else:
    raise ValueError(phase)
