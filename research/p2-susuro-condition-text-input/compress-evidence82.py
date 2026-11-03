import gzip
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).parent
files=[]
for name in ('susuro-condition-public.json','baseline-public82.json','draft-public82.json'):
    path=OUT/name
    raw=path.read_bytes()
    packed=gzip.compress(raw,compresslevel=9,mtime=0)
    assert gzip.decompress(packed)==raw
    parsed=json.loads(raw)
    target=path.with_suffix(path.suffix+'.gz')
    with target.open('xb') as f:f.write(packed)
    assert gzip.decompress(target.read_bytes())==raw
    files.append({'source_raw':str(path),'source_gzip':str(target),
                  'raw_sha256':hashlib.sha256(raw).hexdigest(),'raw_bytes':len(raw),
                  'gzip_sha256':hashlib.sha256(packed).hexdigest(),'gzip_bytes':len(packed),
                  'parsed_rows':len(parsed),'lossless':True})
receipt={'passed':True,'files':files,'calculate_calls':0,'raw_reviewer_source_files_retained':True}
(OUT/'compression-receipt82.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
