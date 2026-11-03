"""Read exact named723 git blobs and current public source; no application calls."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
COMMIT='2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'
CONTEXT=Path('/workspace/.compat/wine-validation-085-context.json')
context=json.loads(CONTEXT.read_bytes())
assert context['commit']==COMMIT
expected=context['source_sha256'];assert len(expected)==723
listed=subprocess.check_output(['git','ls-tree','-r','-z',COMMIT],cwd=REPO)
entries={}
for entry in listed.split(b'\0'):
    if not entry:continue
    header,path=entry.split(b'\t',1);mode,kind,blob=header.split()
    name=path.decode()
    if name in expected:
        assert kind==b'blob'
        entries[name]=blob.decode()
assert entries.keys()==expected.keys()
process=subprocess.Popen(['git','cat-file','--batch'],cwd=REPO,
    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
ordered=sorted(entries)
process.stdin.write(''.join(entries[name]+'\n'for name in ordered).encode())
process.stdin.close()
rows=[]
for name in ordered:
    header=process.stdout.readline();blob,kind,size=header.rstrip(b'\n').split();size=int(size)
    assert blob.decode()==entries[name]and kind==b'blob'
    raw=process.stdout.read(size);assert len(raw)==size and process.stdout.read(1)==b'\n'
    digest=hashlib.sha256(raw).hexdigest();assert digest==expected[name],name
    current=(REPO/name).read_bytes();assert current==raw,name
    rows.append({'source_path':name,'git_blob_sha1':entries[name],'bytes':size,'sha256':digest})
assert process.wait()==0,process.stderr.read().decode()
receipt={'status':'PASS_EXACT_ROOT085_723_GIT_BLOBS_AND_CURRENT_SOURCE',
    'root_commit':COMMIT,'context_source_sha256':hashlib.sha256(CONTEXT.read_bytes()).hexdigest(),
    'maintenance_python_json_files':723,'total_source_bytes':sum(r['bytes']for r in rows),
    'context_source_map_exact':True,'current_source_matches_named_git_blobs':True,
    'files':rows,'application_API_calls':0,'Qt_executed':False,'Wine_executed':False}
target=HERE/'root-source-085-proof.json'
with target.open('x')as out:json.dump(receipt,out,ensure_ascii=False,indent=2);out.write('\n')
(HERE/'root-context-085-preserved.json').write_bytes(CONTEXT.read_bytes())
print(json.dumps({k:v for k,v in receipt.items()if k!='files'},ensure_ascii=False))
