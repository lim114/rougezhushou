"""Save official property pages after correcting method/property URL syntax."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import urllib.request
import urllib.error
HERE=Path(__file__).resolve().parent
rows=[]
for api in ('Camera-projectionMatrix','Camera-fieldOfView','Camera-pixelRect'):
 url=f'https://docs.unity3d.com/2023.2/Documentation/ScriptReference/{api}.html'
 row={'url':url,'requested_utc':datetime.now(timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20)as response:
   raw=response.read();row.update(http_status=response.status,final_url=response.url)
  name=api+'.html'
  with(HERE/name).open('xb')as stream:stream.write(raw)
  row.update(file=name,bytes=len(raw),sha256=sha256(raw).hexdigest())
 except(urllib.error.URLError,TimeoutError,OSError)as exc:row.update(error_type=type(exc).__name__,error=str(exc))
 rows.append(row)
result={'kind':'ACTUAL_CORRECT_OFFICIAL_PROPERTY_URL_FETCH','requests':rows,
 'prior_failed_requests_retained_in':'unity-reference-fetch.json',
 'URL_correction':'Methods use Camera.Method; properties use Camera-property. Prior404 is a URL-construction error, not absence of documented API.',
 'proves_game_preview_capture_settings':False,'no_game_process_Qt_fit_or_product_operations':True}
with(HERE/'unity-properties-fetch.json').open('xb')as stream:stream.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(result,ensure_ascii=False,indent=2))
