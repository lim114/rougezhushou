"""Inspect public scheduling source files only; never execute external tools."""
import hashlib,json,urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'.cache/research/battle-040'
BASE='https://api.github.com/repos/Tim23333/Arknights_timer/'

def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'rouge-research'})
    with urllib.request.urlopen(request,timeout=25) as response:return response.read()

def main():
    FOLDER.mkdir(parents=True,exist_ok=True)
    commit=json.loads(fetch(BASE+'commits/main'))['sha']
    root=json.loads(fetch(BASE+'git/trees/'+commit))['tree']
    trees={x['path']:x['sha'] for x in root if x['type']=='tree'}
    paths=['Ark_emulator/ark_emulator/waves.py','Ark_emulator/ark_sim/kernel/scheduler.py','LICENSE','README.md']
    inventories={}
    for dirname in ('docs','tools','Ark_emulator'):
        t=json.loads(fetch(BASE+'git/trees/'+trees[dirname]+'?recursive=1'))
        inventories[dirname]={'sha':trees[dirname],'truncated':t.get('truncated'),
            'paths':[dirname+'/'+x['path'] for x in t['tree'] if x['type']=='blob' and
                     any(k in x['path'].lower() for k in ('wave','sched','enemy_health','dump','reverse','branch','route','level','timing'))]}
    (FOLDER/'source-inventory.json').write_text(json.dumps({'commit':commit,'inventories':inventories},indent=2),encoding='utf-8')
    paths+= [p for p in inventories['docs']['paths'] if p.endswith('.md')]
    paths+= [p for p in inventories['tools']['paths'] if 'enemy_health/' in p and
             any(k in p.rsplit('/',1)[-1].lower() for k in ('sched','plan','model','spawn')) and p.endswith('.py')]
    def save(name):
        url='https://raw.githubusercontent.com/Tim23333/Arknights_timer/'+commit+'/'+name
        body=fetch(url);target=FOLDER/'source'/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(body)
        return name,{'url':url,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}
    with ThreadPoolExecutor(max_workers=4) as pool:files=dict(pool.map(save,dict.fromkeys(paths)))
    (FOLDER/'source-receipt.json').write_text(json.dumps({'commit':commit,'files':files},indent=2),encoding='utf-8')
    print(json.dumps({'commit':commit,'downloaded':list(files),'inventories':inventories},ensure_ascii=True)[:15000],flush=True)

if __name__=='__main__':main()
