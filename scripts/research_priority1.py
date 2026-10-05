"""Fetch versioned public evidence; never touch private session state."""
import hashlib,json,concurrent.futures,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'.cache/research/priority1';DEST.mkdir(parents=True,exist_ok=True)
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rouge-mechanism-audit'}),timeout=25) as r:return r.read()
def save(name,url):
    try:
        payload=fetch(url);(DEST/name).parent.mkdir(parents=True,exist_ok=True);(DEST/name).write_bytes(payload)
        return {'file':name,'url':url,'sha256':hashlib.sha256(payload).hexdigest()}
    except Exception as e:return {'file':name,'url':url,'unavailable':str(e)[:160]}
jobs=[]
for repo in ('Ray144165154/arkdps','xulai1001/arkdps_data_collection','fexli/ArknightsResource'):
    meta=json.loads(fetch(f'https://api.github.com/repos/{repo}/commits/HEAD'));sha=meta['sha'];name=repo.split('/')[-1]
    jobs.append((name+'-tree.json',f'https://api.github.com/repos/{repo}/git/trees/{sha}?recursive=1'))
    if name=='arkdps':
        jobs.extend((name+'/'+file,f'https://raw.githubusercontent.com/{repo}/{sha}/{file}') for file in ('arkdps/damage.py','README.md','LICENSE'))
jobs.append(('prts-relics.html','https://prts.wiki/w/'+urllib.parse.quote('黑流树海/收藏品一览')))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:receipt=list(pool.map(lambda job:save(*job),jobs))
(DEST/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(receipt,ensure_ascii=True))
