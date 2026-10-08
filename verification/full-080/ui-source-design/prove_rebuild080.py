"""Exact hash/byte and git-object recipe for excluded duplicate public packages."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
freeze=json.loads((HERE/'public-source-freeze-080.json').read_text())
commit=freeze['base_commit']
rows=[]
for name,digest in freeze['source_sha256'].items():
 raw=(HERE/'public-schema-080'/name).read_bytes()
 committed=subprocess.check_output(['git','show',f'{commit}:{name}'],cwd=REPO)
 assert raw==committed and hashlib.sha256(raw).hexdigest()==digest,name
 blob=subprocess.check_output(['git','rev-parse',f'{commit}:{name}'],cwd=REPO,text=True).strip()
 rows.append({'path':name,'bytes':len(raw),'sha256':digest,'git_blob_object_id':blob})
receipt={'scope':'All final public source bytes are exact root80 git blobs; duplicate external package excluded from evidence archive',
 'root_source_commit':commit,'public_source_files':len(rows),'all_bytes_equal':True,'source_drift':[],
 'rebuild_recipe':'For each path, read git show <root_source_commit>:<path> without modifying or supplementing its bytes. Files are public tracked rouge .py/.json only.',
 'files':rows,'new_public_API_calls':0,'gui_executed':False,'wine_executed':False}
(HERE/'public-package-rebuild-proof080.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print({'public_source_files':len(rows),'exact_hash_bytes_and_git_object_proven':True})
