import hashlib,json
from pathlib import Path
base=Path('/workspace/rougezhushou/verification/full-085/public-source-audits/module-source-gap')
inputs=[('author','p2-module-source-gap-082-author','d6faddf65edf355b71ab778e3aa370c67f401077f492ae57035efd7f900c1351',16),('independent','p2-module-source-gap-082-independent','315ab897d04029a6aa4f0185624e9b3ef709f3895d2ea602e0e64b3ea00f030f',31)]
payloads=[]
for prefix,folder,digest,count in inputs:
 p=Path('/workspace/.continuation')/folder/'public-artifacts-manifest.json';b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==digest
 m=json.loads(b);assert m['format_version']==1 and len(m['files'])==count
 payloads.append((prefix+'/public-artifacts-manifest.json',b))
 for row in m['files']:
  name=Path(row['archive_path']);assert not name.is_absolute() and '..' not in name.parts
  data=Path(row['source_path']).read_bytes();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'];payloads.append((prefix+'/'+name.as_posix(),data))
assert len({n for n,b in payloads})==len(payloads);assert not base.exists();base.mkdir(parents=True)
for name,b in payloads:
 p=base/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);assert p.read_bytes()==b
(base/'root-archive-proof.json').write_text(json.dumps({'passed':True,'explicit_public_artifacts':47,'original_manifests':2,'new_API_GUI_Wine_calls':0,'original_author_API_calls':0,'original_independent_API_calls':6,'confirmed_defects':0,'counted_as_numbered_section':False,'native_validation':False},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'archived_negative_audit_artifacts':47,'counted_as_numbered_section':False}))
