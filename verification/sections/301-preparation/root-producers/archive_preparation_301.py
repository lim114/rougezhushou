from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'verification/sections/301-preparation'
TARGET=BASE/'preparation-archive-manifest.json';assert not TARGET.exists()
def copy(source,dest):
    p=Path(source);p=p if p.is_absolute() else ROOT/p
    assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to((ROOT/'.cache').resolve())
    q=BASE/dest;raw=p.read_bytes()
    if q.exists():assert q.read_bytes()==raw;return
    q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)

backend=ROOT/'.cache/p3-301-backend'
for name in ('HANDOFF.json','READY.json','prepare_public_sources.py','public-dependencies.json','run_backend_checks.py','run_public_job.py','write_handoff.py'):
    copy(backend/name,'author-backend/'+name)
for folder in ('source-build-first','backend-first'):
    for p in (backend/folder).iterdir():
        if p.is_file():copy(p,'author-backend/'+folder+'/'+p.name)
view=ROOT/'.cache/p3-301-view';copy(view/'HANDOFF.json','author-view/HANDOFF.json')
handoff=json.loads((view/'HANDOFF.json').read_bytes())
for name,pin in handoff['owned_files'].items():
    if name.startswith('candidate/'):continue
    if 'source-before/' in name and name.rsplit('/',1)[-1] not in (
            'named_reward_items.py','named_reward_items_view.py','test_named_reward_items_view_301.py'):continue
    assert sha256((view/name).read_bytes()).hexdigest()==pin['sha256']
    copy(view/name,'author-view/'+name)
runtime=ROOT/'.cache/p3-301-native-window'
for p in runtime.iterdir():
    if p.is_file() and p.suffix in ('.json','.py','.md'):
        copy(p,'runtime-preparation/'+p.name)
for folder in ('necessary-revision2','necessary-revision3'):
    for p in (runtime/folder).iterdir():
        if p.is_file():copy(p,'runtime-preparation/'+folder+'/'+p.name)
repair=ROOT/'.cache/p3-301-historical-test-repair'
for p in repair.rglob('*'):
    if p.is_file():copy(p,'historical-test-preparation/'+p.relative_to(repair).as_posix())
for source_folder,dest in (('.cache/p3-301-named-reward-research','named-reward-research'),
                           ('.cache/p3-301-notes-research','future-notes-and-ritual-research')):
    for p in (ROOT/source_folder).rglob('*'):
        if p.is_file():copy(p,dest+'/'+p.relative_to(ROOT/source_folder).as_posix())
for name in ('start_section_301.py','prepare_parent_301.py','promote_section_301.py',
             'prepare_promotion_301_v2.py','promote_section_301_v2.py',
             'apply_historical_test_repair_301.py','archive_preparation_301.py'):
    copy('.cache/'+name,'root-producers/'+name)
files={}
for p in sorted(BASE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():files[p.relative_to(BASE).as_posix()]={'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
record={'section':301,'kind':'PUBLIC_PREPARATION_ARCHIVE_NOT_ADDITIONAL_ACCEPTANCE','files':files,
 'private_state_or_hash_lists_copied':False,'duplicate_complete_source_before_payloads_omitted':True,
 'source_before_full_originals_remain_hash_bound_in_actual_author_process':True,
 'author_backend24_and_view12_not_added_to_formal_pass_count':True,
 'first99_failure_and_original_legacy_test_preserved':True,
 'future_ritual_and_note_research_not_current_functional_completion':True}
TARGET.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'files':len(files),'bytes':sum(x['bytes'] for x in files.values()),
 'nonstandard':[p for p in files if Path(p).suffix not in {'.json','.md','.py','.txt','.log','.png','.html','.diff'}]}))
