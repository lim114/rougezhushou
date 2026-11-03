"""Save two targeted official API references; generic API docs are not game capture evidence."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import urllib.error
import urllib.request

HERE=Path(__file__).resolve().parent
rows=[]
for api in ('Camera.WorldToScreenPoint','Camera.projectionMatrix','Camera.fieldOfView','Camera.pixelRect'):
 url=f'https://docs.unity3d.com/2023.2/Documentation/ScriptReference/{api}.html'
 row={'url':url,'requested_utc':datetime.now(timezone.utc).isoformat(),'scope':'generic Unity2023.2 API only; installed game engine/capture version equivalence not established'}
 try:
  request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(request,timeout=20)as response:
   raw=response.read();row.update(http_status=response.status,final_url=response.url)
  name=api+'.html';(HERE/name).write_bytes(raw)
  row.update(file=name,bytes=len(raw),sha256=sha256(raw).hexdigest())
 except(urllib.error.URLError,TimeoutError,OSError)as exc:
  row.update(error_type=type(exc).__name__,error=str(exc),not_fetched=True)
 rows.append(row)
result={'kind':'ACTUAL_TARGETED_OFFICIAL_UNITY_REFERENCE_FETCH_NOT_GAME_EVIDENCE','requests':rows,
 'search_tool_prior_observation':{'WorldToScreenPoint':'accessible HTML, API describes world space to screen pixels',
   'projectionMatrix/fieldOfView/pixelRect':'web tool returned inaccessible/internal error, not a verified HTTP status'},
 'game_or_process_or_Qt_or_test_or_fit_operations':False}
(HERE/'unity-reference-fetch.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(result,ensure_ascii=False,indent=2))
