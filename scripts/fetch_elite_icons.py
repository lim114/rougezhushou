"""Fetch labelled elite emblems from the already pinned asset tree."""
import hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen
root=Path(__file__).resolve().parents[1]
tree=json.loads((root/'.cache/image-tree.json').read_text(encoding='utf-8-sig'))
paths={t['path']:t for t in tree['tree']}
receipt=[]
for elite in range(3):
    for suffix in ('','-s'):
        name=f'{elite}{suffix}.png';path=f'ui/elite/{name}'
        url=f'https://raw.githubusercontent.com/Aceship/Arknight-Images/{tree["commit"]}/{path}'
        with urlopen(Request(url,headers={'User-Agent':'rouge-elite-research'}),timeout=20) as response:payload=response.read()
        blob=hashlib.sha1(f'blob {len(payload)}\0'.encode()+payload).hexdigest()
        if blob!=paths[path]['sha']:raise RuntimeError('Elite emblem changed')
        target=root/f'rouge/data/ui-icons/elite-{name}';target.write_bytes(payload)
        receipt.append({'elite':elite,'file':f'ui-icons/elite-{name}','url':url,'git_blob_sha1':blob,'sha256':hashlib.sha256(payload).hexdigest()})
(root/'rouge/data/elite-icon-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print('6 elite references verified')
