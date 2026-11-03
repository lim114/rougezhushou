"""One public fixed-revision HTML attempt; never retries or bypasses TLS."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import hashlib, json

HERE=Path(__file__).resolve().parent
url='https://prts.wiki/index.php?'+urlencode({'title':'沉沦者的黑流树海/黑流数据库','oldid':'434599'})
record={'kind':'single-public-fixed-revision-HTTP-attempt','url':url,
        'started_at':datetime.now(timezone.utc).isoformat(),'TLS_verification':True,
        'game_chat_Qt_private_Git_operations':False,'retry_count':0}
try:
    with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as response:
        raw=response.read();record.update(status=response.status,headers=dict(response.headers),final_url=response.url)
    target=HERE/'prts-database-434599.html';target.write_bytes(raw)
    record.update(html_file=target.name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),success=True)
except HTTPError as error:
    raw=error.read();target=HERE/'prts-database-434599-HTTP-error-body.bin';target.write_bytes(raw)
    record.update(success=False,exception_type=type(error).__name__,status=error.code,message=str(error),
                  error_body_file=target.name,error_body_sha256=hashlib.sha256(raw).hexdigest(),error_body_bytes=len(raw))
except Exception as error:
    record.update(success=False,exception_type=type(error).__name__,message=str(error))
record['finished_at']=datetime.now(timezone.utc).isoformat()
(HERE/'prts-database-434599-HTTP-receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(record,ensure_ascii=False,indent=2))
