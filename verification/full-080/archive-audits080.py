import hashlib,json,shutil
from pathlib import Path
base=Path('/workspace/rougezhushou/verification/full-080/public-source-audits')
inputs=[
 ('p2-four-owner-cultivation-readonly-audit','d0d3ef41c29aba16f4238a3eeb7f73812e7d89a10eb0dce05e96234ae639a89e'),
 ('p2-run-skill-cultivation-contract-audit','1ef1cd0528147f2e9fee60a5ebb0641d6d4d768ce951e780be09c52c7be017c8'),
 ('p2-next-owner-source-leads-after-079-readonly','a06e05b031bfb3f15239a717131c02c7e0e23a140bd9b87933d4cf7b73059fa6')]
payloads=[]
for folder,digest in inputs:
 p=Path('/workspace/.continuation')/folder/'public-artifacts-manifest-v1.json';b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==digest
 j=json.loads(b);assert isinstance(j['files'],list)
 payloads.append((folder+'-manifest.json',b))
 for row in j['files']:
  name=row['archive_path'];assert not Path(name).is_absolute() and '..' not in Path(name).parts
  data=Path(row['source_path']).read_bytes();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'];payloads.append((name,data))
extra=Path('/workspace/.continuation/p2-incantation-follow-on-source-audit/archivable-public-manifest.json');eb=extra.read_bytes();ed='b4ae135219aac935dba69cdce7524e1bf2e84a76bb53ad9d81baa0e50dff1843';assert hashlib.sha256(eb).hexdigest()==ed
em=json.loads(eb);assert em['format_version']==1 and len(em['files'])==4
payloads.append(('incantation-follow-on/archivable-public-manifest.json',eb))
for row in em['files']:
 name=Path(row['archive_path']);assert not name.is_absolute() and '..' not in name.parts
 b=Path(row['source_path']).read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'];payloads.append(('incantation-follow-on/'+name.as_posix(),b))
assert len({name for name,b in payloads})==len(payloads)
assert not base.exists();base.mkdir(parents=True)
for name,b in payloads:
 p=base/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);assert p.read_bytes()==b
(base/'root-archive-proof.json').write_text(json.dumps({'passed':True,'read_only_audits':4,'explicit_public_artifacts':len(payloads)-4,'manifests':4,'counted_as_numbered_sections':False,'new_public_API_or_GUI_calls':0,'native_validation':False,'source_manifest_sha256':{**dict(inputs),'incantation-follow-on':ed}},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'archived_read_only_artifacts':len(payloads)-4,'manifests':4,'counted_as_numbered_sections':False}))
