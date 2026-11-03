"""Stage only validated public section301 paths; root executes after closeout/index."""
from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
PARENT='5607cbc46c9cf17a841939a778a247e6e1a2a371'
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
def load(name):return json.loads((ROOT/name).read_bytes())
def digest(name):return sha256((ROOT/name).read_bytes()).hexdigest()
assert git(['branch','--show-current']).decode().strip()=='codex/p2-development'
assert git(['rev-parse','HEAD']).decode().strip()==PARENT
assert not git(['diff','--cached','--name-only'])
tracked=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/node_catalog_view.py','tests/test_documented_item_integration_295.py']
assert set(git(['diff','--name-only']).decode().splitlines())==set(tracked)
section=load('verification/sections/301.json')
assert section['section']==301 and section['prior_commit']==PARENT and section['cloud_published']is False and section['next_section']==302
repair=section['historical_test_maintenance']
assert repair['test_file']=='tests/test_documented_item_integration_295.py'and repair['new_test_sha256']=='53b54f8f3524ca9aa5ecfec976af0231aba9113e6e1b32e380d71ef89926e3cc'
assert repair['test_methods']==9 and repair['changed_methods']==1 and repair['unchanged_test_method_AST']==8
assert repair['original38_loop_and_baseline_unchanged']is True and repair['current_reward_function_AST_unchanged']is True
assert sha256((ROOT/repair['receipt']).read_bytes()).hexdigest()==repair['sha256']=='9367f7dc8c1e49065eb8a9aef443155ea34448204b730e809cf95cefed7c3f35'
assert sha256((ROOT/repair['test_file']).read_bytes()).hexdigest()==repair['new_test_sha256']
assert section['only_existing_production_sources_changed']==['rouge/node_catalog_view.py']and section['existing_source_changes_including_test_maintenance']==['rouge/node_catalog_view.py','tests/test_documented_item_integration_295.py']
assert section['old_tracked_test_maintenance']is True
promotion=load(section['source_promotion']['receipt'])
assert digest(section['source_promotion']['receipt'])==section['source_promotion']['sha256']
assert set(promotion['existing_production_changes'])=={'rouge/node_catalog_view.py'}
assert set(section['source_sha256'])==set(promotion['promoted'])|set(promotion['existing_production_changes'])|set(promotion['existing_test_maintenance'])
assert promotion['parent_commit']==PARENT and promotion['old_tests_modified']is True
assert promotion['existing_test_maintenance']=={'tests/test_documented_item_integration_295.py':'53b54f8f3524ca9aa5ecfec976af0231aba9113e6e1b32e380d71ef89926e3cc'}
assert promotion['before_test_sha256']=={'tests/test_documented_item_integration_295.py':'4e946fd3579f37bc3f222f855f9c23811c1279c946a4345431161ed141fcc2f9'}
assert sha256(git(['show',PARENT+':tests/test_documented_item_integration_295.py'])).hexdigest()==promotion['before_test_sha256']['tests/test_documented_item_integration_295.py']
for name,pin in {**promotion['promoted'],**promotion['existing_production_changes'],**promotion['existing_test_maintenance']}.items():
 assert type(pin)is str and digest(name)==pin==section['source_sha256'][name]
for name,before in promotion['before_existing_sha256'].items():
 assert sha256(git(['show',PARENT+':'+name])).hexdigest()==before
assert section['typed_named_grant_count_unchanged']==17 and section['original_entry_gaps_unchanged']==[25,57]
assert section['remaining_global_stage_floor_gaps_unchanged']==15 and section['unparsed_notes_unchanged']==10
assert section['partial_direct_reference_scope_unchanged']==[10,18,58] and section['whole_map_gaps_unchanged']==[81,59]
assert section['actual_server_generation_or_inventory_verified']is False
assert section['full_validation']['after_section']==290 and section['full_validation']['full_suite_rerun']is False
assert section['source_reference']['fixed_choice_count']==16 and section['source_reference']['fixed_event_count']==10 and section['source_reference']['fixed_item_count']==13
assert section['source_reference']['runtime_verifies_complete_original_bytes']is False
assert section['source_reference']['actual_quantity_claim_held_effect_or_eligibility_verified']is False
assert digest('PROJECT_PROGRESS.md')==section['PROJECT_PROGRESS_unchanged_sha256']
assert git(['show','HEAD:PROJECT_PROGRESS.md'])==(ROOT/'PROJECT_PROGRESS.md').read_bytes()
for label in ('necessary_validation','native_windows_validation'):
 source=section[label];assert digest(source['receipt'])==source['sha256']
 actual=load(source['receipt']);assert actual['source_sha256_before']==actual['source_sha256_after']
 if label=='necessary_validation':assert actual['exit_code']==0
 else:assert actual['passed']is True and actual['qt_exit_code']==0 and actual['verification_window_closed']is True
 for name,value in actual['source_sha256_after'].items():
  assert not name.startswith(('.cache/','.local/'))and name!='local-settings.json'
  assert digest(name)==value
prep_ref=section['preparation_archive'];assert digest(prep_ref['receipt'])==prep_ref['sha256']
prep=load(prep_ref['receipt']);prep_base=Path(prep_ref['receipt']).parent
exact_raw={}
for name,pin in prep['files'].items():
 assert type(name)is str and not Path(name).is_absolute()and'..'not in Path(name).parts and'\\'not in name
 relative=(prep_base/name).as_posix()
 assert digest(relative)==pin['sha256']and(ROOT/relative).stat().st_size==pin['bytes']
 if Path(relative).suffix not in{'.json','.log','.md','.png','.py','.txt','.diff','.stderr','.stdout','.html'}:
  exact_raw[relative]=pin['sha256']
# Nonstandard archived raw logs are admitted only by their exact immutable
# preparation manifest path+hash, already bound by the section's closeout receipt.
new=set(promotion['promoted'])
for entry in (ROOT/'verification/sections').iterdir():
 if not entry.name.startswith('301'):continue
 for path in [entry]if entry.is_file()else entry.rglob('*'):
  assert not path.is_symlink()
  if path.is_file():
   relative=path.relative_to(ROOT).as_posix()
   assert path.suffix in{'.json','.log','.md','.png','.py','.txt','.diff','.stderr','.stdout','.html'}or relative in exact_raw
   if relative in exact_raw:assert digest(relative)==exact_raw[relative]
   assert path.stat().st_size<20_000_000
   new.add(relative)
names=sorted(set(tracked)|new)
assert not set(tracked)&new
assert all(not n.startswith(('.local/','.cache/'))and n!='local-settings.json'for n in names)
assert (ROOT/'verification/sections/301-preparation/closeout-tools/archive-manifest.json').is_file()
cp=load('DEVELOPMENT_CHECKPOINT.json');index=load('CLOUD_INDEX.json')
assert cp['completed_sections']==index['completed_sections']==301 and cp['next_section']==index['next_section']==302 and'active_section'not in cp
assert cp['policy']['current_user_batch_target_section']is None and cp['next_full_validation_after']==305
assert index['requirements']['sha256']==digest('PROJECT_REQUIREMENTS.md')
for name,value in index['public_pointers'].items():assert digest(name)==value
assert not(ROOT/'.cache/section301-stage-readback.json').exists()and not(ROOT/'.cache/section301-stage-allowlist.txt').exists()
listing=ROOT/'.cache/section301-stage-allowlist.txt';listing.write_bytes(('\n'.join(names)+'\n').encode('utf8'))
subprocess.check_call(['git','add','-f','--pathspec-from-file='+str(listing)],cwd=ROOT)
assert set(git(['diff','--cached','--name-only']).decode().splitlines())==set(names)
blobs=git(['cat-file','--batch'],input=(''.join(':'+n+'\n'for n in names)).encode('utf8'));offset=0;expected={}
for name in names:
 end=blobs.index(b'\n',offset);header=blobs[offset:end].split();assert header[1]==b'blob'
 size=int(header[2]);offset=end+1;raw=blobs[offset:offset+size];offset+=size
 assert blobs[offset:offset+1]==b'\n';offset+=1;assert raw==(ROOT/name).read_bytes(),name
 expected[name]=sha256(raw).hexdigest()
assert offset==len(blobs)
row={'section':301,'prior_commit':PARENT,'staged_public_files':len(names),'total_public_bytes':sum((ROOT/n).stat().st_size for n in names),
 'staged_and_disk_sha256':expected,'no_private_or_cache_paths_staged':True,'all_staged_blobs_match_disk_exactly':True,
 'exact_nonstandard_public_raw_files':exact_raw,'old_tracked_tests_changed':True,'only_old_test_guard_maintenance':True}
dest=ROOT/'.cache/section301-stage-readback.json'
with dest.open('xb')as stream:stream.write((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({k:v for k,v in row.items()if k not in('staged_and_disk_sha256','exact_nonstandard_public_raw_files')}))
