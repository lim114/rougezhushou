import json
from pathlib import Path
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'verification/sections/300-preparation'
target=BASE/'preparation-archive-manifest.json'
assert not target.exists()
def copy(source, dest):
    p=ROOT/source if not Path(source).is_absolute() else Path(source)
    assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to((ROOT/'.cache').resolve())
    q=BASE/dest;assert not q.exists();q.parent.mkdir(parents=True,exist_ok=True)
    q.write_bytes(p.read_bytes())

backend=ROOT/'.cache/p3-300-backend'
for name in ('HANDOFF.json','READY.json','prepare_sources.py','run_backend_checks.py','run_public_job.py'):
    copy(backend/name,'author-backend/'+name)
for folder in ('source-build-first','backend-first','revision2/source-build-first','revision2/backend-first'):
    for p in (backend/folder).iterdir():
        if p.is_file():copy(p,'author-backend/'+folder+'/'+p.name)
for name in ('rouge/future_region_effects.py','scripts/build_future_region_effects_300.py',
             'research/p3-future-region-effects-300/source-manifest.json',
             'research/p3-future-region-effects-300/README.md',
             'research/p3-future-region-effects-300/SCHEMA.md'):
    copy(backend/'candidate'/name,'author-backend/first-candidate/'+name)
copy(backend/'revision2/runtime-scope.diff','author-backend/revision2/runtime-scope.diff')

view=ROOT/'.cache/p3-300-view'
copy(view/'HANDOFF.json','author-view/HANDOFF.json')
handoff=json.loads((view/'HANDOFF.json').read_bytes())
for name,pin in handoff['actual_evidence_allowlist'].items():
    source=Path(name);assert sha256(source.read_bytes()).hexdigest()==pin['sha256']
    copy(source,'author-view/'+source.relative_to(view).as_posix())
for name in ('rouge/node_catalog_view.py','tests/test_future_region_integration_300.py'):
    copy('.cache/p3-300-parent/'+name,'parent-first-draft/'+name)
for name in ('READY.json','NECESSARY_READY.json','NATIVE_PLAN.md','run_section_300_window.py','run_section_300_necessary.py','preparation-literal-schema.json'):
    copy('.cache/p3-300-native-window/'+name,'runtime-preparation/'+name)
for p in (ROOT/'.cache/p3-300-evidence-audit').iterdir():
    if p.is_file():copy(p,'independent-evidence-audit/'+p.name)
for name in ('start_section_300.py','prepare_parent_300.py','promote_section_300.py','repair_test_isolation_300.py','archive_preparation_300.py'):
    copy('.cache/'+name,'root-producers/'+name)

files={}
for p in sorted(BASE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():files[p.relative_to(BASE).as_posix()]={'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
record={'section':300,'kind':'PUBLIC_PREPARATION_ARCHIVE_NOT_ADDITIONAL_PRODUCT_ACCEPTANCE',
 'files':files,'private_state_contents_or_hash_lists_copied':False,
 'duplicate_complete_game_table_omitted':True,
 'reused_complete_public_table':'research/p3-future-region-effects-300/game-topic-complete.json',
 'first_97_test_failure_and_original_source_kept_separately':True,
 'author_backend_21_and_23_and_view10_not_added_to_formal97':True}
target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'archived_files':len(files),'bytes':sum(p['bytes'] for p in files.values()),
 'nonstandard_members':[p for p in files if Path(p).suffix not in {'.json','.py','.txt','.log','.md','.html','.diff','.png'}]}))
