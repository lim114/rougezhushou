"""Bind pinned skill IDs/iconId overrides to verified original local PNGs."""
import concurrent.futures, hashlib, io, json, sys, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.catalog import operator_profiles
BASE=ROOT/'.cache/research/skills-046'
ASSETS=ROOT/'rouge/data/skill-icons'
COMMIT='d0b5af0b004b044d322397ce5ae79632b6d9fcdd'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(task):
    name,entry=task
    url='https://raw.githubusercontent.com/fexli/ArknightsResource/'+COMMIT+'/skills/'+urllib.parse.quote(name)
    path=ASSETS/name
    for attempt in range(3):
        try:
            if path.exists():raw=path.read_bytes()
            else:
                req=urllib.request.Request(url,headers={'User-Agent':'rouge-offline-reference'})
                with urllib.request.urlopen(req,timeout=30) as response:raw=response.read()
            assert len(raw)==entry['size']
            assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['sha']
            with Image.open(io.BytesIO(raw)) as image:
                assert image.format=='PNG';image.load();size=image.size
            if not path.exists():path.write_bytes(raw)
            return name,{'file':'skill-icons/'+name,'url':url,'blob_sha1':entry['sha'],
                         'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
                         'width':size[0],'height':size[1]}
        except Exception as exc:error=str(exc)
    return name,{'error':error,'url':url,'attempts':3}


def main():
    started=time.perf_counter();ASSETS.mkdir(exist_ok=True)
    receipt=json.loads((ROOT/'.cache/game-data/receipt.json').read_text(encoding='utf-8'))
    skill_path=ROOT/'.cache/game-data/skill_table.json'
    assert digest(skill_path)==receipt['files']['skill_table']['sha256']
    table=json.loads(skill_path.read_text(encoding='utf-8'))
    tree=json.loads((BASE/'skill-tree.json').read_text(encoding='utf-8'))
    assert not tree.get('truncated')
    entries={v['path']:v for v in tree['tree'] if v['type']=='blob'}
    skills={};tasks={}
    for profile in operator_profiles().values():
        for skill in profile['skills']:
            sid=skill['id'];icon=table[sid].get('iconId') or sid;name='skill_icon_'+icon+'.png'
            assert name in entries,(sid,icon)
            skills[sid]={'icon_id':icon,'source_icon_id':table[sid].get('iconId'),'image':name}
            tasks[name]=entries[name]
    print('Downloading '+str(len(tasks))+' pinned skill originals for '+str(len(skills))+' unique skill IDs.',flush=True)
    images={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        futures=[pool.submit(fetch,task) for task in tasks.items()]
        for future in concurrent.futures.as_completed(futures):
            name,record=future.result();images[name]=record
            if len(images)%100==0:print(str(len(images))+'/'+str(len(tasks)),flush=True)
    result={'version':'0.46.0','game_commit':receipt['commit'],'resource_commit':COMMIT,
            'skill_source':receipt['files']['skill_table'],'tree_sha256':digest(BASE/'skill-tree.json'),
            'skills':dict(sorted(skills.items())),'images':dict(sorted(images.items())),
            'seconds':time.perf_counter()-started}
    (BASE/'download-receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    failed=[name for name,record in images.items() if 'error' in record]
    assert not failed,failed
    out=ROOT/'rouge/data/skill-icons.json';assert not out.exists()
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'skills':len(skills),'profile_skill_slots':sum(len(p['skills']) for p in operator_profiles().values()),
                      'images':len(images),'bytes':sum(r['bytes'] for r in images.values()),'seconds':result['seconds']}),flush=True)


if __name__=='__main__':main()
