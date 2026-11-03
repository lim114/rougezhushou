from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
from hashlib import sha256
from datetime import datetime,timezone
import json,re

OUT=Path(__file__).parent;records=[]
for filename,title in(('lorentz-complete.html','洛伦茨，扰动之谬'),('cube-complete.html','源阶方'),
 ('module-complete.html','源阶方模块'),('stage-complete.html','ISW-DF 混沌源阶理论')):
 url='https://m.prts.wiki/w/'+quote(title.replace(' ','_'),safe='')
 row={'title':title,'requested_url':url,'utc':datetime.now(timezone.utc).isoformat()}
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 (public reference research)'}),timeout=35)as response:
   raw=response.read();row.update(status=response.status,final_url=response.url,headers=dict(response.headers))
  text=raw.decode('utf-8');revision=re.search(r'"wgRevisionId"\s*:\s*(\d+)',text)
  if title not in text or revision is None:raise ValueError('Expected full document and actual revision required')
  row.update(revision=revision.group(1),sha256=sha256(raw).hexdigest(),bytes=len(raw),file=filename)
  (OUT/filename).write_bytes(raw)
 except Exception as e:row.update(error=type(e).__name__+': '+str(e))
 records.append(row)
(OUT/'http-source-records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{k:v for k,v in r.items()if k!='headers'}for r in records],ensure_ascii=False))
