"""Static public source packet intake only, no archive draft execution."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
PACKETS = [
    {'label': 'future092_negative', 'root': '/workspace/.continuation/future092-source-lead',
     'manifest': 'public-artifacts-manifest-source092.json', 'handoff': 'final-handoff-source092.json',
     'manifest_sha256': '87db183743515325a648d802198e082381f4fcfa7952c8c38e79fdb14cb96c8a',
     'handoff_sha256': 'fcf6a5b375a573ff3dee56e1ee946fd45fc039baf411c6c962faff8d74f14ffd',
     'files': 20},
    {'label': 'future091_positive', 'root': '/workspace/.continuation/p2-continuous-attack-control-visibility091-source',
     'manifest': 'manifest-source091.json', 'handoff': 'handoff-source091.json',
     'manifest_sha256': 'e085ece169ef52cfd97a4f656bd1cf370bdc29ae78abd13e7e14962e01435c78',
     'handoff_sha256': 'f8d76dc142e9933939b65e862eedb444001b445a3e99ac1be8ae032780e3a86a',
     'files': 34},
]
sha = lambda b: hashlib.sha256(b).hexdigest()


def actual_binding(path):
    data = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(data), 'sha256': sha(data)}


results = []
for packet in PACKETS:
    root = Path(packet['root'])
    mf_path, hf_path = root / packet['manifest'], root / packet['handoff']
    assert sha(mf_path.read_bytes()) == packet['manifest_sha256']
    assert sha(hf_path.read_bytes()) == packet['handoff_sha256']
    manifest, handoff = json.loads(mf_path.read_bytes()), json.loads(hf_path.read_bytes())
    assert manifest['format_version'] == 1
    assert len(manifest['files']) == packet['files']
    for row in manifest['files']:
        path = Path(row['source_path'])
        assert path.is_absolute() and path.is_relative_to(root)
        archive = Path(row['archive_path'])
        assert not archive.is_absolute() and '..' not in archive.parts
        assert actual_binding(path) == {k: row[k] for k in ('source_path', 'bytes', 'sha256')}
    assert len({r['archive_path'] for r in manifest['files']}) == len(manifest['files'])
    verified_bytes = sum(r['bytes'] for r in manifest['files'])
    if packet['label'] == 'future092_negative':
        assert handoff['status'] == 'FINAL_STABLE_SOURCE_ONLY_NEGATIVE_UNKNOWN'
        assert handoff['positive_product_candidate'] is False
        assert handoff['completed_section_increment'] == 0
        assert handoff['native_common_skill_use_and_account_to_run_inheritance_unresolved'] is True
        classification = 'Negative/unknown source audit; no confirmed product candidate and no completed section.'
        unknown = handoff['restart_condition']
        assert verified_bytes == handoff['bytes'] == manifest['bytes']
    else:
        assert handoff['status'] == 'SEALED_READ_ONLY_POSITIVE_CANDIDATE091_PENDING_AFTER_FULL90'
        assert handoff['numbered_section_completed'] is False
        assert handoff['product_draft_created'] is False
        assert all(x == 0 for x in handoff['new_calls'].values())
        classification = 'Positive source-only UI visibility candidate; no product stage or completed section.'
        unknown = 'Actual GUI transition was not run; processed qualification/product implementation pending after full90. Retired received/event rules do not imply outgoing activation.'
        assert verified_bytes == manifest['total_bytes']
    results.append({'label': packet['label'], 'manifest': actual_binding(mf_path),
                    'handoff': actual_binding(hf_path), 'files_verified': len(manifest['files']),
                    'public_bytes_verified': verified_bytes, 'classification': classification,
                    'completed_section_increment': 0, 'boundary': unknown,
                    'all_manifest_public_bytes_SHA_verified': True})
receipt = {'format_version': 1, 'status': 'PASS_STATIC_FUTURE_SOURCE_PACKET_INTAKE_ONLY',
           'packets': results, 'public_files_verified': 54,
           'total_public_bytes_verified': sum(r['public_bytes_verified'] for r in results),
           'new_API_helpers_tests_Qt_Wine_network': 0,
           'archive_draft_executed': False, 'archive_or_product_written': False,
           'tracked_old088_or_source_packet_mutations': 0,
           'new_numbered_sections_completed': 0,
           'remaining_scope': 'Archive draft Git closure static review only after author supplies final draft; root exclusively executes actual archive.'}
receipt_path = OUT / 'source-packet-static-receipt.json'
assert not receipt_path.exists()
receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
files = []
for path in sorted(OUT.iterdir()):
    if path.is_file():
        files.append({**actual_binding(path), 'archive_path': path.name})
manifest_path = OUT / 'source-packet-static-manifest.json'
assert not manifest_path.exists()
manifest_path.write_text(json.dumps({'format_version': 1, 'status': 'SEALED_SOURCE_PACKET_INTAKE_ONLY',
                                    'files': files, 'file_count': len(files),
                                    'total_bytes': sum(r['bytes'] for r in files),
                                    'manifest_self_excluded': True}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'verified_original_files': 54,
                  'verified_original_bytes': receipt['total_public_bytes_verified'],
                  'manifest_sha256': sha(manifest_path.read_bytes()),
                  'receipt_sha256': sha(receipt_path.read_bytes()), 'all_new_project_calls': 0}))
