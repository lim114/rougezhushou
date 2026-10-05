"""Fetch the six numerically labelled game icons for local image matching."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
root=Path(__file__).resolve().parents[1]
items=json.loads((root/'.cache/potential-assets-list.json').read_text(encoding='utf-8'))
target=root/'rouge/data/ui-icons';target.mkdir(exist_ok=True)
def fetch(entry):
    name=entry['name']
    if name not in [f'{i}.png' for i in range(1,7)]:raise ValueError('Unexpected icon name')
    with urlopen(Request(entry['download_url'],headers={'User-Agent':'rouge-development'}),timeout=25) as response:payload=response.read()
    blob=hashlib.sha1(f'blob {len(payload)}\0'.encode()+payload).hexdigest()
    if blob!=entry['sha']:raise ValueError('The icon changed since the directory was read')
    (target/f'potential-{name}').write_bytes(payload)
    return {'potential':int(name[0]),'file':f'ui-icons/potential-{name}',
            'source':entry['html_url'],'git_blob_sha1':blob,'sha256':hashlib.sha256(payload).hexdigest()}
with ThreadPoolExecutor(max_workers=3) as pool:icons=list(pool.map(fetch,items))
(root/'rouge/data/ui-icon-receipt.json').write_text(json.dumps({'repository':'Aceship/Arknight-Images','icons':icons},indent=2),encoding='utf-8')
print('Six labelled potential icons downloaded and source hashes verified')
