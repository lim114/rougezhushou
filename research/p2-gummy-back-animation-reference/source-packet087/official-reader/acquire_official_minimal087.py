"""Fetch only fixed official license, readme and compatible reader source over normal TLS."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import traceback
import urllib.request

HERE=Path(__file__).resolve().parent
COMMIT='8b4844bd4b193ba9e54487ed397a777993cbad56'
BASE='https://raw.githubusercontent.com/EsotericSoftware/spine-runtimes/'+COMMIT+'/'
FILES=['LICENSE','README.md','spine-ts/core/src/SkeletonBinary.ts']
def acquire(name):
    url=BASE+name
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Codex-source-only-reader-audit'}),timeout=30)as response:
            raw=response.read();status=response.status
        destination=HERE/'official-source'/name;destination.parent.mkdir(parents=True,exist_ok=True)
        with destination.open('xb')as out:out.write(raw)
        return {'source_path':url,'archive_path':str(destination.relative_to(HERE)),
            'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'http_status':status,'success':True}
    except Exception as error:
        return {'source_path':url,'success':False,'error_type':type(error).__name__,'error':str(error),
            'traceback':traceback.format_exc(),'application_or_source_parser_calls_started':0}
with ThreadPoolExecutor(max_workers=3)as pool:results=list(pool.map(acquire,FILES))
receipt={'scope':'Official pinned source acquisition only; not a skeleton parse or product operation',
    'official_repository':'https://github.com/EsotericSoftware/spine-runtimes',
    'reference':'refs/heads/3.8','resolved_git_commit':COMMIT,
    'git_ls_remote_observed_stdout':COMMIT+'\trefs/heads/3.8\n',
    'reader_language':'TypeScript','standard_TLS_verification_enabled':True,
    'inherited_proxy_retained':True,'files':results,'skeleton_parse_attempts':0,
    'application_API_calls':0,'formatter_calls':0,'production_helper_calls':0,
    'Qt_Wine_tests_or_tracked_changes':False}
with (HERE/'official-minimal-acquisition087.json').open('x')as out:
    json.dump(receipt,out,ensure_ascii=False,indent=2);out.write('\n')
print(json.dumps({'commit':COMMIT,'requests':len(results),'success':sum(r['success']for r in results),
    'failures':[{'source_path':r['source_path'],'error':r['error']}for r in results if not r['success']],
    'parse_attempts':0}))
