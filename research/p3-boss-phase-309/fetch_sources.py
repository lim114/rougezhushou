from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
from hashlib import sha256
import json,re,datetime

OUT=Path(__file__).parent
records=[]
for name,title in(('boss-complete.html','玻利瓦尔，症结之核'),('stage-complete.html','ISW-DF 畸症')):
 url='https://m.prts.wiki/w/'+quote(title.replace(' ','_'),safe='')
 record={'requested_url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'title':title}
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 (public reference research)'}),timeout=35)as response:
   raw=response.read();record.update(status=response.status,final_url=response.url,headers=dict(response.headers))
  text=raw.decode('utf-8');match=re.search(r'"wgRevisionId"\s*:\s*(\d+)',text)
  record.update(bytes=len(raw),sha256=sha256(raw).hexdigest(),revision=match.group(1)if match else None)
  if title not in text or not match:raise ValueError('Complete expected public title/revision not found')
  (OUT/name).write_bytes(raw);record['file']=name
 except Exception as e:record.update(error=type(e).__name__+': '+str(e))
 records.append(record)
(OUT/'http-source-records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{k:v for k,v in row.items()if k!='headers'}for row in records],ensure_ascii=False))
