"""Fetch official README-documented self-contained core JS only; do not execute."""
import hashlib,json
from pathlib import Path
import traceback,urllib.request
HERE=Path(__file__).resolve().parent
COMMIT='8b4844bd4b193ba9e54487ed397a777993cbad56'
name='spine-ts/build/spine-core.js'
url='https://raw.githubusercontent.com/EsotericSoftware/spine-runtimes/'+COMMIT+'/'+name
try:
    with urllib.request.urlopen(url,timeout=30)as response:raw=response.read();status=response.status
    target=HERE/'official-source'/name;target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb')as out:out.write(raw)
    row={'source_path':url,'archive_path':str(target.relative_to(HERE)),'bytes':len(raw),
        'sha256':hashlib.sha256(raw).hexdigest(),'http_status':status,'success':True}
except Exception as error:
    row={'source_path':url,'success':False,'error_type':type(error).__name__,
        'error':str(error),'traceback':traceback.format_exc()}
r={'official_repository_commit':COMMIT,'path_documented_by':'spine-ts/README.md Usage2',
    'self_contained_without_rendering_backend_per_official_README':True,'file':row,
    'TLS_verification_enabled':True,'proxy_retained':True,'bundle_execution_calls':0,
    'compile_attempts':0,'full_skeleton_parse_attempts':0,'application_API_helper_formatter_Qt_Wine_tests_calls':0}
with (HERE/'official-core-bundle-acquisition087.json').open('x')as out:json.dump(r,out,ensure_ascii=False,indent=2);out.write('\n')
print(json.dumps(row))
