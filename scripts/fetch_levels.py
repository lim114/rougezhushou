"""Cache public levels and enemy database at the same pinned commit as the catalog."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache'/'game-data'
receipt=json.loads((CACHE/'receipt.json').read_text(encoding='utf-8'))
catalog=json.loads((ROOT/'rouge/data/catalog.json').read_text(encoding='utf-8'))
base=f'https://raw.githubusercontent.com/{receipt["repository"]}/{receipt["commit"]}/zh_CN/gamedata/levels/'
paths=sorted({s['levelId'].lower()+'.json' for s in catalog['stages'].values() if s.get('levelId')})
paths.append('enemydata/enemy_database.json')

def fetch(path):
    target=CACHE/'levels'/path
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():
        with urlopen(Request(base+path,headers={'User-Agent':'rouge-development'}),timeout=60) as response:
            payload=response.read()
        json.loads(payload)
        target.write_bytes(payload)
    payload=target.read_bytes()
    return path,{'url':base+path,'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload)}

records={}
errors={}
with ThreadPoolExecutor(max_workers=5) as pool:
    futures={path:pool.submit(fetch,path) for path in paths}
    for path,future in futures.items():
        try:
            key,value=future.result()
            records[key]=value
        except Exception as error:
            errors[path]=type(error).__name__
(CACHE/'level-receipt.json').write_text(json.dumps({'commit':receipt['commit'],'files':records,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(records)} downloaded/cached; {len(errors)} failed')
if errors:print(json.dumps(errors))
