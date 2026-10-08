"""Fetch the documented declarations and official attachment/region sources only."""
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,traceback,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
COMMIT='8b4844bd4b193ba9e54487ed397a777993cbad56'
FILES=['spine-ts/build/spine-core.d.ts','spine-ts/core/src/attachments/AttachmentLoader.ts',
    'spine-ts/core/src/attachments/RegionAttachment.ts','spine-ts/core/src/attachments/MeshAttachment.ts',
    'spine-ts/core/src/Texture.ts']
def acquire(name):
    url='https://raw.githubusercontent.com/EsotericSoftware/spine-runtimes/'+COMMIT+'/'+name
    try:
        with urllib.request.urlopen(url,timeout=30)as response:raw=response.read();status=response.status
        target=HERE/'official-source'/name;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb')as out:out.write(raw)
        return {'source_path':url,'archive_path':str(target.relative_to(HERE)),'bytes':len(raw),
            'sha256':hashlib.sha256(raw).hexdigest(),'http_status':status,'success':True}
    except Exception as error:
        return {'source_path':url,'success':False,'error_type':type(error).__name__,
            'error':str(error),'traceback':traceback.format_exc(),'full_parse_attempts':0}
with ThreadPoolExecutor(max_workers=5)as pool:rows=list(pool.map(acquire,FILES))
r={'official_commit':COMMIT,'files':rows,'compile_or_bundle_execution_attempts':0,'full_parse_attempts':0,
    'application_API_helper_formatter_tests_Qt_Wine_calls':0,'standard_TLS_and_inherited_proxy':True}
with (HERE/'official-loader-contract-acquisition087.json').open('x')as out:json.dump(r,out,ensure_ascii=False,indent=2);out.write('\n')
print(json.dumps({'requests':len(rows),'success':sum(r['success']for r in rows),
    'failures':[{'path':r['source_path'],'error':r['error']}for r in rows if not r['success']],'full_parse':0}))
