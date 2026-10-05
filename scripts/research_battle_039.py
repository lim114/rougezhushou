"""Read pinned level structure and locate source map images; no game access."""
import collections,json,sys,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.catalog import catalog,stage_previews

def fetch(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url,
        headers={'User-Agent':'rouge-research'}),timeout=30))

def main():
    folder=ROOT/'.cache/research/battle-039';folder.mkdir(parents=True,exist_ok=True)
    commit='d0b5af0b004b044d322397ce5ae79632b6d9fcdd'
    base='https://api.github.com/repos/fexli/ArknightsResource/'
    root=fetch(base+'contents/?ref='+commit)
    tree=next(x['sha'] for x in root if x['name']=='mapreview')
    files=fetch(base+'git/trees/'+tree)['tree']
    image_files=[f for f in files if 'rogue6' in f['path'].lower() or 'ro6' in f['path'].lower()]
    actions=collections.Counter();coords=collections.Counter();maps={};examples={}
    for sid,p in catalog()['stages'].items():
        if sid not in stage_previews():continue
        path=ROOT/'.cache/game-data/levels'/(p['levelId'].lower()+'.json')
        d=json.loads(path.read_text(encoding='utf-8'))
        maps[sid]={'map_id':d['mapId'],'level_id':d['levelId'],'rows':len(d['mapData']['map']),
            'cols':len(d['mapData']['map'][0]),'waves':len(d['waves']),
            'source':str(path.relative_to(ROOT))}
        for w in d['waves']:
            for f in w['fragments']:
                for a in f['actions']:actions[a['actionType']]+=1
        for r in d['routes']:coords.update(r['startPosition'].keys())
        if sid=='ro6_n_1_2':
            spawn=next(a for w in d['waves'] for f in w['fragments'] for a in f['actions'] if a['actionType']=='SPAWN')
            examples={'first_spawn':spawn,'route':d['routes'][spawn['routeIndex']],
                'map_keys':list(d['mapData']),'predefines_keys':list(d['predefines'])}
    receipt={'resource_commit':commit,'mapreview_tree':tree,'mapreview_entries':len(files),
        'ro6_images':image_files,'stages':maps,'action_types':dict(actions),
        'route_coordinate_keys':dict(coords),'example':examples}
    (folder/'structure.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'mapreview_entries':len(files),'images':len(image_files),
        'first_images':[f['path'] for f in image_files[:8]],'stage_count':len(maps),
        'map_example':maps['ro6_n_1_2'],'action_types':dict(actions),'example':examples}),flush=True)

if __name__=='__main__':main()
