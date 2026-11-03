from pathlib import Path
from hashlib import sha256
import json,time,sys
import httpx
R=Path.cwd();meta=json.loads((R/'.cache/page-feature-vector-model-candidate.json').read_bytes())
revision=meta['revision'];out=R/'.cache/vlm-qwen3-4b-int4-candidate';out.mkdir(exist_ok=False)
started=time.monotonic();records=[]
with httpx.Client(proxy='http://127.0.0.1:7890',trust_env=False,timeout=httpx.Timeout(60,connect=20),follow_redirects=True)as c:
    for record in meta['public_files']:
        name=record['path'];path=out/name;assert path.parent==out
        digest=sha256();size=0;reported=time.monotonic()
        with c.stream('GET',f'https://huggingface.co/OpenVINO/Qwen3-VL-4B-Instruct-int4-ov/resolve/{revision}/{name}')as response:
            response.raise_for_status()
            with path.open('xb')as target:
                for block in response.iter_bytes(1024*1024):
                    target.write(block);digest.update(block);size+=len(block)
                    if time.monotonic()-reported>10:
                        print(json.dumps({'file':name,'MiB':round(size/1024**2,1),'elapsed_seconds':round(time.monotonic()-started)}),flush=True);reported=time.monotonic()
        assert size==record['bytes'],name
        if record['lfs_sha256']:assert digest.hexdigest()==record['lfs_sha256'],name
        records.append({'file':name,'bytes':size,'sha256':digest.hexdigest(),'original_lfs_sha256_matches':True if record['lfs_sha256']else None})
        print(json.dumps({'completed_files':len(records),'file':name}),flush=True)
        (out/'download-progress.json').write_text(json.dumps({'revision':revision,'files':records},indent=2)+'\n','utf8')
(out/'download-complete.json').write_text(json.dumps({'passed':True,'revision':revision,'files':records,'elapsed_seconds':time.monotonic()-started,'public_downloads_only':True,'private_inputs_sent':False},indent=2)+'\n','utf8')
print(json.dumps({'complete':True,'files':len(records)}),flush=True)
