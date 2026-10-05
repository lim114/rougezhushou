"""Read installed application code for exposed transports; no account data is read."""
import json
import re
import struct
from pathlib import Path

ARCHIVE=Path(r'C:\Program Files\WindowsApps\OpenAI.Codex_26.928.3736.0_x64__2p2nqsd0c76g0\app\resources\app.asar')
with ARCHIVE.open('rb') as archive:
    _,header_size,_,json_size=struct.unpack('<4I',archive.read(16))
    tree=json.loads(archive.read(json_size))
    files=[]
    def walk(node,prefix=''):
        for name,value in node.get('files',{}).items():
            path=prefix+name
            if 'files' in value:walk(value,path+'/')
            elif not value.get('unpacked') and path.endswith(('.js','.json')) and 'node_modules' not in path:
                files.append((path,value))
    walk(tree)
    patterns=['createServer','listen(','namedPipe','ipc.sock','chatgpt','send-message','sendMessage','chatgpt.com/backend-api','controlSocket','localhost','127.0.0.1']
    result=[]
    for path,entry in files:
        if entry.get('size',0)>20_000_000:continue
        archive.seek(8+header_size+int(entry['offset']))
        source=archive.read(entry['size']).decode('utf-8',errors='replace')
        matches=[]
        for term in patterns:
            found=list(re.finditer(re.escape(term),source,re.IGNORECASE))
            if found:
                matches.append({'term':term,'count':len(found),'examples':[source[max(0,m.start()-140):m.end()+180] for m in found[:3]]})
        if matches:result.append({'file':path,'size':entry['size'],'matches':matches})
    target=Path('.cache/client-interface-inspection.json')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('files',len(files),'matching',len(result))
    for row in result:
        if any(x['term'] in ('createServer','namedPipe','controlSocket','ipc.sock') for x in row['matches']):
            print(json.dumps(row,ensure_ascii=True))
