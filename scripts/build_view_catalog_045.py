"""Download pinned gallery originals and bind presentation-only classifications."""
import concurrent.futures
import hashlib
import io
import json
import sys
import time
import urllib.request
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from rouge.catalog import catalog,operator_profiles
from rouge.battle_preview import battle_data
from build_battle_previews_039 import resolve

BASE=ROOT/'.cache/research/visual-catalog-045'
COMMIT='d0b5af0b004b044d322397ce5ae79632b6d9fcdd'
ASSETS=ROOT/'rouge/data/portraits'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch_asset(task):
    kind,name,entry=task
    prefix='avatar/ASSISTANT/' if kind=='operator' else 'enemy/'
    url='https://raw.githubusercontent.com/fexli/ArknightsResource/'+COMMIT+'/'+prefix+name
    path=ASSETS/name;error=None
    for attempt in range(3):
        try:
            if path.exists():raw=path.read_bytes()
            else:
                req=urllib.request.Request(url,headers={'User-Agent':'rouge-offline-reference'})
                with urllib.request.urlopen(req,timeout=30) as response:raw=response.read()
            assert len(raw)==entry['size']
            assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['sha']
            with Image.open(io.BytesIO(raw)) as im:
                assert im.format=='PNG';im.load();size=im.size
            if not path.exists():path.write_bytes(raw)
            return name,{'file':'portraits/'+name,'url':url,'blob_sha1':entry['sha'],
                         'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
                         'width':size[0],'height':size[1]}
        except Exception as exc:error=str(exc)
    return name,{'url':url,'error':error,'attempts':3}


def main():
    started=time.perf_counter();ASSETS.mkdir(exist_ok=True)
    avatar={e['path']:e for e in json.loads((BASE/'avatar-assistant-tree.json').read_text(encoding='utf-8'))['tree']}
    enemy={e['path']:e for e in json.loads((BASE/'enemy-tree.json').read_text(encoding='utf-8'))['tree']}
    profiles=operator_profiles();operators={};tasks={}
    for key,p in profiles.items():
        name=next((n for n in (p['id']+'.png',p['id']+'_2.png') if n in avatar),None)
        assert name is not None,key
        operators[key]={'character_id':p['id'],'profession':p['profession'],'portrait':name,
                        'variant':'elite_2' if name.endswith('_2.png') else 'default'}
        tasks[name]=('operator',name,avatar[name])
    source=json.loads((ROOT/'.cache/game-data/level-receipt.json').read_text(encoding='utf-8'))
    dbpath=ROOT/'.cache/game-data/levels/enemydata/enemy_database.json'
    assert digest(dbpath)==source['files']['enemydata/enemy_database.json']['sha256']
    db={e['Key']:e['Value'] for e in json.loads(dbpath.read_text(encoding='utf-8'))['enemies']}
    enemies={};prefab_evidence={};unknown_ranks=[]
    for sid,stage in battle_data()['stages'].items():
        name=catalog()['stages'][sid]['levelId'].lower()+'.json'
        path=ROOT/'.cache/game-data/levels'/name
        assert digest(path)==source['files'][name]['sha256']
        level=json.loads(path.read_text(encoding='utf-8'))
        for ref in level['enemyDbRefs']:
            eid=ref['id'];resolved=resolve(db,ref);prefab=resolved.get('prefabKey')
            filename=eid+'.png' if eid+'.png' in enemy else (prefab or '')+'.png'
            portrait=filename if filename in enemy else None
            record={'prefab_key':prefab,'portrait':portrait}
            if eid in enemies:assert enemies[eid]==record,(sid,eid)
            enemies[eid]=record
            if portrait:tasks[filename]=('enemy',filename,enemy[filename])
            if filename!=eid+'.png':
                prefab_evidence.setdefault(eid,[]).append({'stage':sid,'level_sha256':stage['level_source']['sha256'],
                                                         'prefab_key':prefab,'reference_level':ref['level']})
            entry=next(e for e in stage['enemies'] if e['id']==eid and e['level']==ref['level'])
            if entry['level_type'] not in ('NORMAL','ELITE','BOSS'):
                unknown_ranks.append({'stage':sid,'enemy_id':eid,'level':ref['level'],
                                      'defined_level_type':resolved.get('levelType')})
    print('Downloading '+str(len(tasks))+' pinned original PNGs.',flush=True)
    images={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for future in concurrent.futures.as_completed([pool.submit(fetch_asset,t) for t in tasks.values()]):
            name,record=future.result();images[name]=record
            if len(images)%100==0:print(str(len(images))+'/'+str(len(tasks)),flush=True)
    receipt={'commit':COMMIT,'seconds':time.perf_counter()-started,'images':images,
             'prefab_evidence':prefab_evidence,'rank_unknown':unknown_ranks}
    (BASE/'portrait-download-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    failed=[n for n,r in images.items() if 'error' in r]
    assert not failed,failed
    floors=json.loads((BASE/'stage-floor-input.json').read_text(encoding='utf-8'))
    by_name={name:group for group in floors['groups'] for name in group['names']}
    assert len(by_name)==sum(len(g['names']) for g in floors['groups'])
    groups={}
    for sid,stage in battle_data()['stages'].items():
        g=by_name.get(stage['name'])
        groups[sid]={'group':g['id'],'label':g['label'],'floor':g['floor']} if g else {
            'group':'unconfirmed','label':'事件/特殊（层数未确认）','floor':None}
    data={'version':'0.45.0','source':{'game_commit':source['commit'],'resource_commit':COMMIT,
          'stage_floor_source':floors['source'],'floor_input_sha256':digest(BASE/'stage-floor-input.json'),
          'copyright':'游戏图片版权归鹰角网络；本地资料头像不代表当前装扮或实战状态。'},
          'operators':operators,'enemies':enemies,'stages':groups,'images':dict(sorted(images.items()))}
    out=ROOT/'rouge/data/view-catalog.json';assert not out.exists()
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'operators':len(operators),'enemy_ids':len(enemies),'downloaded_images':len(images),
          'image_bytes':sum(r['bytes'] for r in images.values()),
          'missing_enemy_images':[eid for eid,r in enemies.items() if not r['portrait']],
          'stage_groups':{g:sum(r['group']==g for r in groups.values()) for g in sorted({r['group'] for r in groups.values()})},
          'unknown_rank_references':len(unknown_ranks)},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
