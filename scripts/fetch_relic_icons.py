"""Fetch only catalogued relic icons; verify Git blob hashes before saving."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.request import Request,urlopen

root=Path(__file__).resolve().parents[1]
repository='fexli/ArknightsResource'
def get(url):
    with urlopen(Request(url,headers={'User-Agent':'rouge-relic-research'}),timeout=20) as response:
        return response.read()
commit=json.loads(get(f'https://api.github.com/repos/{repository}/commits/main'))
metadata=json.loads((root/'.cache/relic-resource-root.json').read_text(encoding='utf-8-sig'))
if commit['commit']['tree']['sha']!=metadata['sha']:
    metadata=json.loads(get(f'https://api.github.com/repos/{repository}/git/trees/{commit["sha"]}'))
    (root/'.cache/relic-resource-root.json').write_text(json.dumps(metadata),encoding='utf-8')
tree=json.loads((root/'.cache/relic-resource-tree.json').read_text(encoding='utf-8-sig'))
expected=next(entry['sha'] for entry in metadata['tree'] if entry['path']=='rogueitem')
if expected!=tree['sha']:
    tree=json.loads(get(f'https://api.github.com/repos/{repository}/git/trees/{expected}?recursive=1'))
    (root/'.cache/relic-resource-tree.json').write_text(json.dumps(tree),encoding='utf-8')
if tree.get('truncated'):raise RuntimeError('Resource directory is incomplete')
catalog=json.loads((root/'rouge/data/catalog.json').read_text(encoding='utf-8'))['relics']
entries={Path(t['path']).stem:t for t in tree['tree'] if t['type']=='blob' and t['path'].endswith('.png')}
folder=root/'rouge/data/relic-icons';folder.mkdir(exist_ok=True)
def fetch(rid):
    if rid not in entries:raise RuntimeError('No image in pinned resource directory')
    entry=entries[rid];url=f'https://raw.githubusercontent.com/{repository}/{commit["sha"]}/rogueitem/{entry["path"]}'
    target=folder/f'{rid}.png'
    payload=target.read_bytes() if target.exists() else get(url)
    blob=hashlib.sha1(f'blob {len(payload)}\0'.encode()+payload).hexdigest()
    if blob!=entry['sha']:raise RuntimeError('Image does not match pinned Git blob')
    target.write_bytes(payload)
    return {'id':rid,'file':f'relic-icons/{rid}.png','url':url,'git_blob_sha1':blob,
            'sha256':hashlib.sha256(payload).hexdigest()}
icons=[];failures=[]
with ThreadPoolExecutor(max_workers=6) as pool:
    futures={pool.submit(fetch,rid):rid for rid in catalog}
    for future in as_completed(futures):
        rid=futures[future]
        try:icons.append(future.result())
        except Exception as error:failures.append({'id':rid,'error':str(error)})
        if (len(icons)+len(failures))%20==0:print(f'{len(icons)} verified icons; {len(failures)} unavailable',flush=True)
receipt={'repository':repository,'commit':commit['sha'],'tree_sha':tree['sha'],
         'icons':sorted(icons,key=lambda x:x['id']),'unavailable':failures,
         'notice':'Game artwork belongs to Hypergryph; research/testing use. See licenses/GAME-ICON-NOTICE.md.'}
(root/'rouge/data/relic-icon-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(icons)} / {len(catalog)} relic references verified; {len(failures)} unavailable',flush=True)
