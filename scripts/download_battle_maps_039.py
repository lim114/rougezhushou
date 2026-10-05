"""Download authorized map assets from a pinned source; verify every blob/image."""
import concurrent.futures,hashlib,io,json,sys,time,urllib.request
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.catalog import stage_previews

def main():
    research=ROOT/'.cache/research/battle-039'
    source=json.loads((research/'structure.json').read_text(encoding='utf-8'))
    commit=source['resource_commit'];entries={x['path']:x for x in source['ro6_images']}
    dest=ROOT/'rouge/data/battle-maps';dest.mkdir(parents=True,exist_ok=True)
    def get(sid):
        name=sid+'.png';entry=entries[name]
        assert Path(name).name==name and len(entry['sha'])==40
        url=f'https://raw.githubusercontent.com/fexli/ArknightsResource/{commit}/mapreview/{name}'
        path=dest/name
        if path.exists():body=path.read_bytes()
        else:
            body=None
            for attempt in range(3):
                try:
                    body=urllib.request.urlopen(urllib.request.Request(url,
                        headers={'User-Agent':'rouge-map-assets'}),timeout=30).read();break
                except Exception:
                    if attempt==2:raise
                    time.sleep(.3*(attempt+1))
        assert len(body)==entry['size'] and len(body)<4*1024*1024
        blob=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()
        assert blob==entry['sha'],name
        with Image.open(io.BytesIO(body)) as picture:
            assert picture.format=='PNG';size=picture.size;picture.verify()
        if not path.exists():path.write_bytes(body)
        return sid,{'file':'battle-maps/'+name,'url':url,'source_blob_sha1':blob,
                    'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),
                    'width':size[0],'height':size[1]}
    images={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for sid,result in pool.map(get,stage_previews()):
            images[sid]=result
            if len(images)%20==0:print(json.dumps({'verified_map_images':len(images)}),flush=True)
    assert len(images)==105
    receipt={'resource_commit':commit,'source_repo':'https://github.com/fexli/ArknightsResource',
        'source_readme':'https://github.com/fexli/ArknightsResource/blob/'+commit+'/README_CN.md',
        'copyright':'Game assets belong to Shanghai Hypergryph Network Technology Co., Ltd.',
        'user_download_authorized':True,'images':images,'total_bytes':sum(v['bytes'] for v in images.values())}
    (research/'image-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'images':len(images),'bytes':receipt['total_bytes'],'resource_commit':commit}),flush=True)

if __name__=='__main__':main()
