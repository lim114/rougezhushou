"""Real public temporary IO: two writes pending publication, no game state."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from rouge.persistence_install import write_temporary_record, install_initial_record

source = ROOT / 'rouge/persistence_install.py'
receipt = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
           'native_windows_verified': False, 'game_actions': 0, 'chat_requests': 0,
           'actual_public_temporary_io': True, 'cases': []}
for initial in (True, False):
    with tempfile.TemporaryDirectory(prefix='public-261-archive-interleave-') as folder:
        destination = Path(folder) / 'run.json'
        if not initial:
            destination.write_text('ORIGINAL', encoding='utf-8')
        first = write_temporary_record(destination, 'PUBLIC-WRITER-A')
        first_before_second = first.read_bytes()
        second = write_temporary_record(destination, 'PUBLIC-WRITER-B')
        if initial:
            install_initial_record(first, destination)
        else:
            first.replace(destination)
        receipt['cases'].append({
            'first_install': initial, 'first_returned_name': first.name,
            'second_returned_name': second.name,
            'first_own_bytes_hex': first_before_second.hex(),
            'bytes_published_by_first_writer_hex': destination.read_bytes().hex(),
            'first_published_own_bytes': destination.read_bytes() == first_before_second,
            'retained_original_entries': [{'name': entry.name, 'bytes_hex': entry.read_bytes().hex()}
                for entry in destination.parent.iterdir() if '.preserved-' in entry.name],
            'second_returned_name_still_exists': second.exists(),
        })
receipt['source_sha256_after'] = hashlib.sha256(source.read_bytes()).hexdigest()
receipt['source_drift'] = receipt['source_sha256'] != receipt['source_sha256_after']
print(json.dumps(receipt, ensure_ascii=False, indent=2))
