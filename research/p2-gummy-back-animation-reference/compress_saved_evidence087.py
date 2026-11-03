import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
entries=[]
for name in ('matrix-baseline-results.json','matrix-draft-results.json'):
    path=ROOT/name;raw=path.read_bytes();packed=gzip.compress(raw,compresslevel=9,mtime=0)
    out=ROOT/(name+'.gz')
    if out.exists():raise RuntimeError('Do not replace an existing compressed evidence file')
    out.write_bytes(packed);restored=gzip.decompress(packed)
    assert restored==raw
    entries.append({'source_path':str(path),'original_bytes':len(raw),'original_sha256':hashlib.sha256(raw).hexdigest(),
      'compressed_source_path':str(out),'compressed_archive_path':out.name,'compressed_bytes':len(packed),'compressed_sha256':hashlib.sha256(packed).hexdigest(),
      'decompressed_bytes':len(restored),'decompressed_sha256':hashlib.sha256(restored).hexdigest(),'lossless_roundtrip':True,'compression':'gzip9/mtime0',
      'API_formatter_test_parser_download_calls':0})
(ROOT/'lossless-compression-map087.json').write_text(json.dumps({'version':1,'entries':entries,'original_frozen_files_unchanged':True},indent=2)+'\n')
print(json.dumps({'original_bytes':sum(x['original_bytes'] for x in entries),'compressed_bytes':sum(x['compressed_bytes'] for x in entries),'roundtrip':True}))
