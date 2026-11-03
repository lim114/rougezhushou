"""Explicit public archive manifest; excludes package clones and runtime files."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
EXPECTED='645ebd2e90ab3aef1fa5c9318300bd5e690c5f1dd6cfb67f94ed74f355ca4f03'
assert hashlib.sha256((P/'wine-ui-smoke-075.py').read_bytes()).hexdigest()==EXPECTED
names=['wine-ui-smoke-070-preserved.py','wine-ui-smoke-075.py','wine-ui-smoke-075-pending-preserved.py',
 'runner-075.patch','build_runner.py','public_contracts.py','cases075.py','supplemental-checks.py.fragment',
 'check_public_schema.py','check_api_text_contracts.py','freeze_public_source.py',
 'public-source-freeze-73.json','public-source-freeze-74.json','public-source-freeze-75.json',
 'public-schema-interim-73.json.gz','public-schema-interim-73-summary.json',
 'public-schema-interim-74.json.gz','public-schema-interim-74-summary.json',
 'public-schema-final-75.json.gz','public-schema-final-75-summary.json',
 'api-text-contracts-74.json.gz','api-text-contracts-74-summary.json','api-text-source-compatibility.json',
 'runner-static-review.json','preparation-failures.json','root-actual-receipt-reference.json','NOTE075.md','CHECKPOINT.md',
 'independent/control-notes071.md','independent/control-notes071.json',
 'independent/unfrozen-static-review071_074.json','independent/runner-review075.json',
 'seal_public_manifest.py','handoff.json']
# Add actual independent supporting programs/notes, retaining an explicit list.
names.extend(p.relative_to(P).as_posix()for p in sorted((P/'independent').glob('*'))
 if p.is_file() and p.suffix in ('.py','.md','.json') and p.relative_to(P).as_posix() not in names)
assert len(names)==len(set(names))
files=[]
for name in names:
 path=P/name;assert path.is_file(),name
 raw=path.read_bytes();files.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
manifest={'scope':'Explicit public design/evidence archive; excludes all public-schema-* source package directories, pycache and runtime/private state',
 'root':str(P),'runner_sha256':EXPECTED,'source_commit':'225cb66dc89143a3cd3a884bd6c62f47ed9d36bc',
 'planned_check_total':1455,'base_actual070_checks':841,'author_gui_executed':False,'author_wine_executed':False,
 'files':files}
dest=P/'archivable-public-manifest.json';dest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print({'public_files':len(files),'runner_sha256':EXPECTED,'manifest_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
