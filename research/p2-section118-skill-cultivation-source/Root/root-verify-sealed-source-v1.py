"""Root stdlib-only Source manifest byte and compile verification."""
import argparse,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('manifest');p.add_argument('--sha256',required=True)
a=p.parse_args();f=Path(a.manifest);base=f.parent
assert f.is_file() and not f.is_symlink()
raw=f.read_bytes();assert hashlib.sha256(raw).hexdigest()==a.sha256
m=json.loads(raw);keys=[k for k in ('files','payloads','source_payloads') if k in m]
assert len(keys)==1,(keys,'one explicit payload schema required')
items=m[keys[0]]
if type(items) is dict: rows=[{'path':k,**v} for k,v in items.items()]
else: assert type(items) is list;rows=items
assert rows and len({x['path'] for x in rows})==len(rows)
for x in rows:
 q=Path(x['path']);assert not q.is_absolute() and '..' not in q.parts
 file=base/q;assert file.is_file() and not file.is_symlink()
 data=file.read_bytes();assert type(x['bytes']) is int and len(data)==x['bytes']
 assert type(x['sha256']) is str and re.fullmatch('[0-9a-f]{64}',x['sha256']) and hashlib.sha256(data).hexdigest()==x['sha256']
 if file.suffix=='.py':compile(data,str(file),'exec')
print(json.dumps({'Source_payloads_verified':len(rows),'runtime_executed':False,'manifest_sha256':a.sha256}))
