from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from urllib.parse import quote
from datetime import datetime,timezone
from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor
import json,re
OUT=Path(__file__).resolve().parent
DOCS=[('boss-complete.html','卡德霍，黑流之源'),('avatar-complete.html','痛楚化身'),('hound-complete.html','猎犬proto'),('stage-normal-complete.html','ISW-DF 永无安宁'),('stage-pursuit-complete.html','ISW-DF 痛苦将息')]
def fetch(pair):
 filename,title=pair;url='https://m.prts.wiki/w/'+quote(title.replace(' ','_'),safe='');row={'title':title,'requested_url':url,'utc':datetime.now(timezone.utc).isoformat()}
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 (public documentary research)'}),timeout=40)as response:
   raw=response.read();row.update(status=response.status,final_url=response.url,headers=dict(response.headers))
  text=raw.decode('utf8');revision=re.search(r'"wgRevisionId"\s*:\s*(\d+)',text)
  (OUT/filename).write_bytes(raw)
  row.update(file=filename,bytes=len(raw),sha256=sha256(raw).hexdigest(),revision=revision.group(1)if revision else None)
  if title not in text or revision is None:raise ValueError('Full expected page title and actual revision required')
 except HTTPError as e:
  raw=e.read();error_file=filename+'.http-error-body';(OUT/error_file).write_bytes(raw);row.update(status=e.code,headers=dict(e.headers),error_file=error_file,error_sha256=sha256(raw).hexdigest(),error_bytes=len(raw),error=str(e))
 except Exception as e:row.update(error=type(e).__name__+': '+str(e))
 return row
with ThreadPoolExecutor(max_workers=5)as pool:records=list(pool.map(fetch,DOCS))
(OUT/'http-source-records.json').write_bytes((json.dumps(records,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps([{k:v for k,v in r.items()if k!='headers'}for r in records],ensure_ascii=False))
