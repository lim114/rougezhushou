"""Transport explicitly sealed public packets and root receipts, without project calls."""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path('/workspace/rougezhushou')
sha=lambda b:hashlib.sha256(b).hexdigest()
spec=json.loads(Path(sys.argv[1]).read_bytes())
destination=ROOT/spec['archive']
assert destination.resolve().is_relative_to((ROOT/'research').resolve())
assert not destination.exists(), 'Archive must be new; never overwrite historical evidence.'
payload=[]
seen=set()

def add(source, archive, expected_sha=None, expected_bytes=None):
    source=Path(source);archive=Path(archive)
    assert source.is_file() and source.resolve().is_relative_to(Path('/workspace').resolve())
    assert not archive.is_absolute() and '..' not in archive.parts
    assert archive.as_posix() not in seen, archive
    seen.add(archive.as_posix())
    raw=source.read_bytes()
    if expected_sha is not None:assert sha(raw)==expected_sha, source
    if expected_bytes is not None:assert len(raw)==expected_bytes, source
    payload.append((source,archive,raw))

for packet in spec['packets']:
    mf=Path(packet['manifest_path']);raw=mf.read_bytes();assert sha(raw)==packet['manifest_sha256']
    data=json.loads(raw);label=Path(packet['label']);schema=packet['schema']
    if schema=='files':
        assert data['format_version']==1
        rows=data['files'];count=packet['declared_file_count'];total=packet['declared_total_bytes']
        if packet['original_count_field'] is not None:assert data[packet['original_count_field']]==count
        if packet['original_total_field'] is not None:assert data[packet['original_total_field']]==total
        for row in rows:add(row['source_path'],label/row['archive_path'],row['sha256'],row['bytes'])
    elif schema=='artifacts':
        assert data['schema_version']==1
        rows=data['artifacts'];count=data['artifact_count'];total=data['artifact_bytes']
        for row in rows:add(mf.parent/row['path'],label/row['path'],row['sha256'],row['bytes'])
    else:raise ValueError(schema)
    assert len(rows)==count and sum(row['bytes'] for row in rows)==total
    add(mf,label/mf.name,packet['manifest_sha256'],len(raw))
    for item in packet.get('extras',[]):
        add(item['source_path'],label/item['archive_path'],item['sha256'],item['bytes'])
for item in spec['root_files']:
    add(item['source_path'],item['archive_path'],item['sha256'],item['bytes'])

# Every byte and safe path is validated before any archive write.
destination.mkdir(parents=True)
for source,relative,raw in payload:
    path=destination/relative;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:f.write(raw)
    assert path.read_bytes()==raw
manifest={relative.as_posix():{'source_path':str(source),'sha256':sha(raw),'bytes':len(raw)} for source,relative,raw in payload}
with (destination/'transport-manifest091.json').open('xb') as f:
    f.write((json.dumps({'format_version':1,'file_count':len(manifest),'total_bytes':sum(x['bytes'] for x in manifest.values()),'files':manifest,'all_public_originals_byte_exact':True,'project_calls':0},ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'archived_files':len(manifest),'bytes':sum(x['bytes'] for x in manifest.values()),'project_calls':0}))
