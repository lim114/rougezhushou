"""Read pinned public source inventory and verify downloaded Git blobs."""
import hashlib,json,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMMIT='6264b020513de479056c3db41216037abaadde50'
FOLDER=ROOT/'.cache/research/therapy-042'

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'rouge-public-research'})
    with urllib.request.urlopen(req,timeout=25) as response:return response.read()

def main():
    FOLDER.mkdir(parents=True,exist_ok=True)
    url=f'https://api.github.com/repos/Tim23333/Arknights_timer/contents/Ark_emulator/data_raw?ref={COMMIT}'
    body=fetch(url);(FOLDER/'data-raw-inventory.json').write_bytes(body)
    rows=json.loads(body)
    print(json.dumps({'names':[r['name'] for r in rows]},ensure_ascii=True),flush=True)
    old=json.loads((ROOT/'.cache/research/ammo-041/Ark_emulator-ark_emulator-inventory.json').read_text(encoding='utf-8'))
    selected=[r for r in old if r['name'] in ('buffs.py','attributes.py')]
    receipt={'commit':COMMIT,'inventory_url':url,'read_only':True,'foreign_runtime_executed':False,'files':{}}
    for row in selected:
        data=fetch(row['download_url']);sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert sha==row['sha'],row['name']
        (FOLDER/row['name']).write_bytes(data)
        receipt['files'][row['name']]={'url':row['download_url'],'bytes':len(data),'git_blob':sha,
            'sha256':hashlib.sha256(data).hexdigest()}
    (FOLDER/'source-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    template=json.loads((ROOT/'.cache/research/ammo-041/data_buff_templates.json').read_text(encoding='utf-8'))
    excerpt={'rogue_2_attr_up[limited]':template['rogue_2_attr_up[limited]']}
    (FOLDER/'template-excerpt.json').write_text(json.dumps(excerpt,indent=2),encoding='utf-8')
    print(json.dumps({'downloaded':list(receipt['files']),'template_bytes':(FOLDER/'template-excerpt.json').stat().st_size}),flush=True)

if __name__=='__main__':main()
