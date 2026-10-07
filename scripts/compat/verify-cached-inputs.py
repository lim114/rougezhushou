import hashlib,json,zipfile
from pathlib import Path
root=Path('/workspace/.compat');verified=[]
def check(path,digest):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,str(path)
    verified.append(str(path.relative_to(root)))
for r in json.loads((root/'debian-package-sources.json').read_text())['packages']:
    check(root/'apt/cache/archives'/r['filename'],r['sha256'])
for r in json.loads((root/'wheel-sources.json').read_text())['wheels']:
    matches=list(root.glob('wheels*/'+r['filename']));assert len(matches)==1,r['filename'];check(matches[0],r['sha256'])
for folder,receipt in [('python-windows','source.json'),('windows-sdk','cpp-source.json')]:
    r=json.loads((root/folder/receipt).read_text());name=r['url'].rsplit('/',1)[1];check(root/folder/name,r['sha256'])
print('Verified cached SHA256 inputs:',len(verified))
