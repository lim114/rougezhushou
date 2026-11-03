from pathlib import Path
from hashlib import sha256
import ast,json,shutil
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'verification/sections/298-preparation'
def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def digest(p):return sha256(p.read_bytes()).hexdigest()
name='tests/test_node_catalog.py';old=DEST/'before'/name;new=ROOT/name
def methods(p):return{m.name:m for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.ClassDef)for m in n.body if isinstance(m,ast.FunctionDef)}
a,b=methods(old),methods(new);assert a.keys()==b.keys()
others=[k for k in a if k!='test_172'];assert all(ast.dump(a[k])==ast.dump(b[k])for k in others)
row={'kind':'historical_assertion_migration_for_new_documented_main_floor_scope','old_source':'verification/sections/298-preparation/before/'+name,
 'old_sha256':digest(old),'new_source':name,'new_sha256':digest(new),'unchanged_other_test_methods':len(others),
 'changed_method':'test_172','old_method':ast.unparse(a['test_172']),'new_method':ast.unparse(b['test_172']),
 'reason':'The previous fixed event DOM lacked floors for this event; section298 now binds an independent explicit natural-main-floor negative rule. Preserve the old source and replace precisely its outdated allowance assertion with no candidate, exact excluded identity, and false documentary floor match. New tests cover all36 contexts and content/history/source failure boundaries.',
 'product_or_test_failure_claimed':False,'coverage_scope_reduced':False}
(DEST/'historical-test-migration.json').write_bytes(encode(row))
copies=[('.cache/p3-298-event-requirements-candidate','author-source-model'),
        ('.cache/p3-298-event-gap-research','source-research'),
        ('.cache/p3-298-independent-review','independent-static-review'),
        ('.cache/p3-298-map-camera-research','map-camera-research')]
counts={}
for source,target in copies:
 base=ROOT/source;out=DEST/target;out.mkdir(exist_ok=False);count=0
 for p in sorted(base.rglob('*')):
  if not p.is_file()or p.is_symlink()or'__pycache__'in p.parts:continue
  rel=p.relative_to(base)
  if source.endswith('candidate')and rel.parts[0]=='candidate':continue
  dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);count+=1
 counts[target]=count
for source in ('.cache/start_section_298.py','.cache/integrate_section_298.py','.cache/capture_section_298_before.py','.cache/archive_section_298_preparation.py'):
 p=ROOT/source;dest=DEST/'root-producers'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
print(json.dumps({'archived_file_counts':counts,'unchanged_historical_test_methods':len(others),'new_test_sha256':digest(new)}))
