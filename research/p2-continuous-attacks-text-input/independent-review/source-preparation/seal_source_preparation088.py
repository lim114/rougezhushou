"""Seal a source-only independent preparation once; no project imports/calls."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
manifest = ROOT / 'v1-public-files-manifest088.json'
handoff = ROOT / 'source-preparation-handoff088.json'
assert not manifest.exists() and not handoff.exists()
receipt = json.loads((ROOT / 'independent-source-preparation-receipt088.json').read_bytes())
assert receipt['status'] == 'PASS_INDEPENDENT_SOURCE_PREPARATION_ONLY'
assert receipt['new_public_API_calls'] == receipt['new_product_helper_calls'] == 0


def row(path):
    data = path.read_bytes()
    return {'source_path': str(path), 'archive_path': str(path.relative_to(ROOT)),
            'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


for bound in receipt['bound_consumer_producer_core_files']:
    data = Path(bound['copied_path']).read_bytes()
    assert len(data) == bound['bytes'] and hashlib.sha256(data).hexdigest() == bound['sha256']
details = {
    'format_version': 1, 'status': 'FINAL_SOURCE_PREPARATION_PENDING_PRODUCT_FREEZE',
    'baseline_commit': receipt['current_baseline_commit'],
    'source_packet_verified_files': receipt['source_packet_verified_files'],
    'source_packet_verified_bytes': receipt['source_packet_verified_bytes'],
    'source_packet_manifest_sha256': receipt['source_packet_manifest']['sha256'],
    'saved_old_source16_rows_verified': 16,
    'static_literal_gets_in_five_bound_modules': 12,
    'confirmed_saved_active_groups': 3, 'confirmed_saved_inactive_groups': 1,
    'new_API_helper_formatter_tests_network_Qt_Wine_Spine_calls': 0,
    'tracked_mutations': 0, 'formal_product_review': 'Pending frozen draft/budget; no fresh product calls yet.',
    'source_key_boundary': 'event native0 incoming-only waitFalse inactive; actually reached ready!=None/waitTrue tail is separate true consumer.',
    'author_supplement_preview_notice': 'Observer at actual event tail accepted by root; verify frozen implementation and fresh risks later.',
    'all087_final_directories_immutable': True,
    'manifest_path': str(manifest), 'source_receipt': row(ROOT / 'independent-source-preparation-receipt088.json'),
    'unknown_native_clock_or_attachment_inferred': False
}
handoff.write_text(json.dumps(details, ensure_ascii=False, indent=2) + '\n')
files = [row(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p != manifest]
manifest.write_text(json.dumps({'format_version': 1, 'status': 'FINAL_SOURCE_PREPARATION_ONLY',
                               'archive_root': str(ROOT), 'files': files,
                               'file_count': len(files), 'total_bytes': sum(r['bytes'] for r in files)},
                              ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': details['status'], 'files': len(files), 'bytes': sum(r['bytes'] for r in files),
                  'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(),
                  'handoff_sha256': hashlib.sha256(handoff.read_bytes()).hexdigest()}))
