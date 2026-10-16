from pathlib import Path
from hashlib import sha256
import json,shutil
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'verification/sections/299-preparation'
plans={}
def tree(base,target,skip_candidates=False):
 assert base.is_dir(),str(base)
 for p in sorted(base.rglob('*')):
  if not p.is_file()or p.is_symlink():continue
  rel=p.relative_to(base)
  if '__pycache__'in rel.parts or (skip_candidates and 'candidate'in rel.parts):continue
  plans[target+'/'+rel.as_posix()]=p
tree(ROOT/'.cache/p3-299-spawn-candidates-candidate','author-backend',True)
tree(ROOT/'.cache/p3-299-fixed-spawn-research','source-research')
tree(ROOT/'.cache/p3-299-spawn-view-candidate','author-view')
tree(ROOT/'.cache/p3-299-parent-integration-tests','author-parent-tests')
tree(ROOT/'.cache/p3-299-root-integration','root-integration-drafts')
tree(ROOT/'.cache/p3-299-native-window','runtime-preparation')
tree(ROOT/'.cache/p3-299-auxiliary-images-research','unused-auxiliary-images-research')
tree(ROOT/'.cache/p3-299-event-gap-research','future-event-effects-research')
for name in ('rouge/spawn_candidates.py','tests/test_spawn_candidates_299.py'):
 plans['author-backend/pre-revision2-source/'+name]=ROOT/'.cache/p3-299-spawn-candidates-candidate/candidate'/name
for name in ('start_section_299.py','draft_section_299_integration.py','revise_section_299_parent.py',
 'promote_section_299.py','freeze_section_299_native.py','repair_battle_entry_binding_299.py',
 'freeze_section_299_entry_repair.py','archive_section_299_preparation.py'):
 plans['root-producers/'+name]=ROOT/'.cache'/name
assert all(p.is_file()and not p.is_symlink()and not(DEST/n).exists()for n,p in plans.items())
manifest={'section':299,'kind':'immutable_public_preparation_and_actual_author_evidence_archive',
 'files':{n:{'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}for n,p in plans.items()},
 'unused_research_not_functionally_promoted':['unused-auxiliary-images-research','future-event-effects-research'],
 'root_product_formal_validation_reported_separately':True,'private_files_copied':False}
for name,p in plans.items():
 dest=DEST/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 for_field=manifest['files'][name];assert sha256(dest.read_bytes()).hexdigest()==for_field['sha256']
(DEST/'preparation-archive-manifest.json').write_bytes((json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'archived_files':len(plans),'public_bytes':sum(p.stat().st_size for p in plans.values()),
 'raw_files':{n:pin['sha256']for n,pin in manifest['files'].items()if not Path(n).suffix}},ensure_ascii=False))
