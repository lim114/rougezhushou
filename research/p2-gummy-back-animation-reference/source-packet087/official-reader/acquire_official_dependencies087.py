"""Pinned official TS error-site and attachment-loader contract, no compile/parse."""
from concurrent.futures import ThreadPoolExecutor
import hashlib,json
from pathlib import Path
import traceback,urllib.request
HERE=Path(__file__).resolve().parent
COMMIT='8b4844bd4b193ba9e54487ed397a777993cbad56'
FILES=['spine-ts/core/src/SlotData.ts','spine-ts/core/src/BoneData.ts',
    'spine-ts/core/src/AttachmentLoader.ts','spine-ts/README.md']
def acquire(name):
    url='https://raw.githubusercontent.com/EsotericSoftware/spine-runtimes/'+COMMIT+'/'+name
    try:
        with urllib.request.urlopen(url,timeout=30)as response:raw=response.read();status=response.status
        dest=HERE/'official-source'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb')as out:out.write(raw)
        return {'source_path':url,'archive_path':str(dest.relative_to(HERE)),
            'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'http_status':status,'success':True}
    except Exception as error:
        return {'source_path':url,'success':False,'error_type':type(error).__name__,'error':str(error),
            'traceback':traceback.format_exc(),'parse_attempts':0}
with ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(acquire,FILES))
r={'scope':'Official error-site/loader contracts only','repository_commit':COMMIT,'files':rows,
    'standard_TLS_and_inherited_proxy':True,'compile_attempts':0,'full_parse_attempts':0,
    'application_API_helper_formatter_tests_Qt_Wine_calls':0}
with (HERE/'official-dependency-acquisition087.json').open('x')as out:json.dump(r,out,ensure_ascii=False,indent=2);out.write('\n')
print(json.dumps({'requests':len(rows),'success':sum(x['success']for x in rows),
    'failures':[x['error']for x in rows if not x['success']],'compile':0,'parse':0}))
