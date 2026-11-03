"""Lossless deterministic compression and independent decompression proof."""
import gzip
import hashlib
import io
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
rows = []
for label in ('baseline', 'draft'):
    original = OUT / ('public-' + label + '083.json')
    data = original.read_bytes()
    buffer = io.BytesIO()
    with gzip.GzipFile(filename='', fileobj=buffer, mode='wb', compresslevel=9, mtime=0) as stream:
        stream.write(data)
    packed = buffer.getvalue()
    path = Path(str(original) + '.gz')
    path.write_bytes(packed)
    restored = gzip.decompress(path.read_bytes())
    assert restored == data
    rows.append({'original_path': original.name, 'original_bytes': len(data),
        'original_sha256': hashlib.sha256(data).hexdigest(), 'archive_path': path.name,
        'archive_bytes': len(packed), 'archive_sha256': hashlib.sha256(packed).hexdigest(),
        'decompressed_bytes': len(restored), 'decompressed_sha256': hashlib.sha256(restored).hexdigest(),
        'lossless': True, 'gzip_mtime': 0, 'gzip_filename': ''})
(OUT / 'lossless-compression083.json').write_text(json.dumps({'passed': True,
    'API_calls': 0, 'files': rows}, indent=2) + '\n')
print(json.dumps({'passed': True, 'API_calls': 0, 'files': len(rows),
                  'original_bytes': sum(row['original_bytes'] for row in rows),
                  'compressed_bytes': sum(row['archive_bytes'] for row in rows)}))
