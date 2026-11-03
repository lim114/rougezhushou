"""Single public enemy-page fetch; no retries, browser or TLS bypass."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request,urlopen
from urllib.parse import quote
from urllib.error import HTTPError
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
url='https://prts.wiki/w/'+quote('玻利瓦尔，症结之核')
receipt={'kind':'single-public-enemy-HTML-request-not-validation','url':url,
 'started_at':datetime.now(timezone.utc).isoformat(),'retry_count':0,'TLS_verification':True}
try:
 with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as response:
  raw=response.read();receipt.update(status=response.status,final_url=response.url,headers=dict(response.headers))
 target=HERE/'prts-chimera-current.html';target.write_bytes(raw)
 receipt.update(success=True,file=target.name,sha256=sha256(raw).hexdigest(),bytes=len(raw))
except HTTPError as error:
 raw=error.read();target=HERE/'prts-chimera-current-http-error.bin';target.write_bytes(raw)
 receipt.update(success=False,status=error.code,exception_type=type(error).__name__,message=str(error),
  error_file=target.name,error_bytes=len(raw),error_sha256=sha256(raw).hexdigest())
except Exception as error:
 receipt.update(success=False,exception_type=type(error).__name__,message=str(error))
receipt['finished_at']=datetime.now(timezone.utc).isoformat()
(HERE/'prts-chimera-current-http-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
