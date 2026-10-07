"""Freeze committed public Python/JSON files without reading root WIP or state."""
import hashlib,io,json,subprocess,sys,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent;REPO=Path('/workspace/rougezhushou')
commit=subprocess.check_output(['git','rev-parse',sys.argv[1]],cwd=REPO,text=True).strip()
label=sys.argv[2] if len(sys.argv)>2 else '75'
target=P/f'public-schema-{label}'
assert not target.exists(),'Preserve existing freeze; use a new version for an changed commit'
archive=subprocess.check_output(['git','archive',commit,'rouge'],cwd=REPO)
target.mkdir();files={}
with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
 for item in tar.getmembers():
  if item.isfile() and Path(item.name).suffix in ('.py','.json'):
   raw=tar.extractfile(item).read();dest=target/item.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
   blob=subprocess.check_output(['git','show',f'{commit}:{item.name}'],cwd=REPO)
   assert raw==blob
   files[item.name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
receipt={'scope':'Exact committed public Python/JSON git archive; excludes root WIP/private state',
 'commit':commit,'source_file_count':len(files),'git_blob_matches_all_files':True,'source_files':files,
 'gui_executed':False,'wine_executed':False}
(P/f'public-source-freeze-{label}.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print({'commit':commit,'public_source_files':len(files),'git_blobs_equal':True})
