"""Optional exact-ID public image recovery; no enemy-data or numeric substitution."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
BOOK='rouge/data/enemy-portrait-supplement-433.json'
BOOK_SHA256='58c5db7d71244e3321327c0e73e9d7c7213391c9a04c2c38d154af43f53a834b'

def portrait(enemy):
    if not isinstance(enemy,dict):return None
    from . import expansion_reference as source
    try:
        raw=source._file(BOOK).read_bytes()
        if sha256(raw).hexdigest()!=BOOK_SHA256:return None
        book=json.loads(raw)
        if book.get('schema')!='exact-public-enemy-portrait-433':return None
        for field in('prefab_key','id'):
            identity=enemy.get(field)
            if not isinstance(identity,str):continue
            row=book['images'].get(identity)
            if row is None:continue
            if row['id']!=identity or row['file']!='rouge/data/current-enemies/'+identity+'.png':return None
            if row['resource_commit']!='de6cfb30ed1d41d9102d93e8ea400fc0cefc8ff7':return None
            tree=json.loads(source._file(row['existing_exact_tree']).read_bytes())
            if tree['sha']!='d311bf00c24fe2ad71675fbcb025f0136cc60e89':return None
            candidates=[r for r in tree['tree']if r.get('path')==identity+'.png']
            if len(candidates)!=1 or candidates[0]['sha']!=row['git_blob_sha1']or candidates[0]['size']!=row['bytes']:return None
            return row
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError):return None
    return None
