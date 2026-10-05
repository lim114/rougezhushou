"""Fetch six pinned active-tool references; verify Git blobs before saving."""
import json,hashlib,urllib.request,concurrent.futures
from pathlib import Path
root=Path(__file__).resolve().parents[1]
receipt=json.loads((root/'rouge/data/relic-icon-receipt.json').read_text(encoding='utf-8'))
tree=json.loads((root/'.cache/relic-resource-tree.json').read_text(encoding='utf-8-sig'))
assert tree['sha']==receipt['tree_sha']
entries={v['path']:v for v in tree['tree']}
items=json.loads((root/'rouge/data/inventory-items.json').read_text(encoding='utf-8'))['active_tools']
folder=root/'rouge/data/relic-icons';icons=[]
def fetch(item):
    rid=item['id'];entry=entries[item['iconId']+'.png']
    url=f'https://raw.githubusercontent.com/{receipt["repository"]}/{receipt["commit"]}/rogueitem/{entry["path"]}'
    path=folder/f'{rid}.png'
    if path.exists():payload=path.read_bytes()
    else:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rouge-tactical-icons'}),timeout=20) as r:payload=r.read()
    assert hashlib.sha1(f'blob {len(payload)}\0'.encode()+payload).hexdigest()==entry['sha']
    path.write_bytes(payload)
    return {'id':rid,'file':f'relic-icons/{rid}.png','url':url,'git_blob_sha1':entry['sha'],'sha256':hashlib.sha256(payload).hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:icons=list(pool.map(fetch,items.values()))
(root/'rouge/data/tactical-icon-receipt.json').write_text(json.dumps({'repository':receipt['repository'],
    'commit':receipt['commit'],'icons':icons},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(icons)} tactical icons verified')
