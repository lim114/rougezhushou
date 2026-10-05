"""Fetch exact-ID asset references linked by the public game wiki."""
import concurrent.futures,hashlib,json,urllib.request
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];file=ROOT/'rouge/data/relic-icon-receipt.json'
receipt=json.loads(file.read_text(encoding='utf8'));missing=receipt['unavailable'];folder=ROOT/'rouge/data'
def one(item):
    rid=item['id'];url=f'https://torappu.prts.wiki/assets/roguelike_topic_itempic/{rid}.png'
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rouge-reference-research'}),timeout=25) as r:payload=r.read()
        image=cv2.imdecode(np.frombuffer(payload,np.uint8),cv2.IMREAD_UNCHANGED)
        if image is None or image.ndim!=3 or image.shape[2]!=4:raise ValueError('Expected decoded RGBA sprite')
        target=folder/'relic-icons'/f'{rid}.png';target.write_bytes(payload)
        return {'id':rid,'file':f'relic-icons/{rid}.png','url':url,'sha256':hashlib.sha256(payload).hexdigest(),
                'source_page':'https://m.prts.wiki/w/沉沦者的黑流树海/拟造物质编目',
                'verification':'exact_asset_id_rgba_decode_sha256','dimensions':list(image.shape[:2])}
    except Exception as e:return {'id':rid,'error':str(e)[:180]}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(one,missing))
good=[r for r in results if 'sha256' in r];bad=[r for r in results if 'error' in r]
receipt['icons']=sorted(receipt['icons']+good,key=lambda r:r['id']);receipt['unavailable']=bad
receipt['secondary_reference_source']='Exact-ID PRTS torappu game asset mirror; not Git-blob verified.'
file.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
audit={'downloaded':len(good),'still_missing':bad,'sources':good,'artwork_equivalence':{}}
byhash={}
for e in receipt['icons']:byhash.setdefault(e['sha256'],[]).append(e['id'])
audit['artwork_equivalence']={key:values for key,values in byhash.items() if len(values)>1}
(ROOT/'RELIC_REFERENCE_0.21_VERIFICATION.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'downloaded':len(good),'still_missing':bad,'shared_artwork_groups':len(audit['artwork_equivalence'])}))
