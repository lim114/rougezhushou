"""Root Source-only byte verification; accept explicit relative or package-local absolute paths."""
import argparse, hashlib, json, re
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('manifest'); p.add_argument('--sha256', required=True)
a = p.parse_args(); f = Path(a.manifest).resolve(); base = f.parent
assert f.is_file() and not f.is_symlink()
raw = f.read_bytes(); assert hashlib.sha256(raw).hexdigest() == a.sha256
m = json.loads(raw); keys = [k for k in ('files', 'payload', 'payloads', 'source_payloads') if k in m]
assert len(keys) == 1
items = m[keys[0]]
rows = [{'path': k, **v} for k, v in items.items()] if type(items) is dict else items
assert type(rows) is list and rows and len({x['path'] for x in rows}) == len(rows)
for x in rows:
    q = Path(x['path']); assert '..' not in q.parts
    leaf = q if q.is_absolute() else base / q
    assert leaf.is_relative_to(base) and leaf.is_file() and not leaf.is_symlink()
    assert leaf.resolve().is_relative_to(base)
    b = leaf.read_bytes(); assert type(x['bytes']) is int and len(b) == x['bytes']
    assert type(x['sha256']) is str and re.fullmatch('[0-9a-f]{64}', x['sha256'])
    assert hashlib.sha256(b).hexdigest() == x['sha256']
    if leaf.suffix == '.py': compile(b, str(leaf), 'exec')
print(json.dumps({'Source_payloads_verified': len(rows), 'runtime_executed': False, 'manifest_sha256': a.sha256}))
