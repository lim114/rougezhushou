"""Freeze clean public source, then overlay only explicitly frozen public hunks."""
import hashlib,io,json,subprocess,sys,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent;REPO=Path('/workspace/rougezhushou')
commit=subprocess.check_output(['git','rev-parse',sys.argv[1]],cwd=REPO,text=True).strip()
label=sys.argv[2];target=P/f'public-schema-{label}'
assert not target.exists(),target
target.mkdir();archive=subprocess.check_output(['git','archive',commit,'rouge'],cwd=REPO)
with tarfile.open(fileobj=io.BytesIO(archive))as tar:
 for item in tar.getmembers():
  if item.isfile()and Path(item.name).suffix in('.py','.json'):
   raw=tar.extractfile(item).read();dest=target/item.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
   assert raw==subprocess.check_output(['git','show',f'{commit}:{item.name}'],cwd=REPO)
def hashes():
 return {p.relative_to(target).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(target.rglob('*'))if p.is_file()}
original=hashes();patches=[]
for spec in sys.argv[3:]:
 expected,name=spec.split(':',1);path=Path(name);raw=path.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==expected
 sections=raw.split(b'diff --git ');source=b''
 for section in sections[1:]:
  header=section.splitlines()[0];left,right=header.split(b' ',1)
  relative=right.removeprefix(b'b/').decode()
  if relative.startswith('rouge/')and Path(relative).suffix in('.py','.json'):
   source+=b'diff --git '+section
 assert source
 subprocess.run(['git','apply','--check','-'],cwd=target,input=source,check=True,capture_output=True)
 subprocess.run(['git','apply','-'],cwd=target,input=source,check=True,capture_output=True)
 patches.append({'path':str(path),'sha256':expected,'applied_scope':'only public rouge .py/.json hunks','source_hunks_sha256':hashlib.sha256(source).hexdigest()})
receipt={'scope':'Exact committed public Python/JSON git blobs plus named frozen source hunks, never root WIP/private state',
 'base_commit':commit,'public_source_files':len(hashes()),'base_git_blobs_equal':True,'base_source_sha256':original,
 'patches':patches,'source_sha256':hashes(),'gui_executed':False,'wine_executed':False}
(P/f'public-source-freeze-{label}.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print({'base_commit':commit,'public_source_files':len(hashes()),'overlays':len(patches)})
