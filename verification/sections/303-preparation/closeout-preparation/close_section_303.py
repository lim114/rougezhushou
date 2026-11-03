"""Strict303 public closeout; preview by default, actual root-only --apply.
No tests/Qt/game/chat/private reads or Git mutation. Missing actual evidence fails.
"""
import argparse,ast,math,runpy
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,re,struct,subprocess
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
HERE=ROOT/'.cache/p3-303-closeout'
PARENT='c2b78e4aa4136fe739067b5ccf9d13b595142320'
TITLE='畸症与本性难移固定原图的49格独立直接参考'
CANONICAL='scripts/verify_direct_map_window_303.py'
PACKET='research/p3-map-direct-ground-303'
MANIFEST=PACKET+'/source-manifest.json'
DATA='rouge/data/fixed-landmark-references.json'
REGULAR='rouge/data/battle-map-projections.json'
BUILDER='scripts/extend_direct_landmark_303.py'
COMPARISON=PACKET+'/build-receipt.json'
MANIFEST_SHA='e1ad287b4d4c2879e7fbad16b60b825db660147c2ba0a719dde60b7cfea6e2c4'
DATA_SHA='dc43bbbe70eab6f11cc8661c3bfeab994000ea614ea0f8c999a596f5cb2c445a'
COMPARISON_SHA='93f1d1db4ea633a32a720d650ff513592294ba82a61db3ec9cf10d9f70ecdaad'
FULL='verification/full-290/summary.json';FULL_SHA='2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
CHANGED_EXISTING={DATA}
MAINTENANCE={
 'tests/test_direct_landmark_294.py':'263cea49f3f19514a5fb6be72a3dc42926ba4cab6007bbc14d21a489a07c1f52',
 'tests/test_map_projection_048.py':'b2454d2c5c53a3b81164cce528f6dcd5c9f99aa2b0a3027b721e23aa50e145de'}
PROGRESS_SHA_BEFORE='111962b1622515c494ae81a06ac19b915db797211e926165a9947b80fade8a0b'
OLD_PROGRESS='其中10图/18关已有58格直接参考，整图仍未校准'
NEW_PROGRESS='其中12图/21关已有107格直接参考，整图仍未校准'

def require(value,message):
 if value is not True:raise ValueError('303 closeout prerequisite: '+message)

def path(value):
 p=Path(value);p=p if p.is_absolute() else ROOT/p
 require(p.resolve().is_relative_to(ROOT.resolve()) and not p.is_symlink(),'regular public repository path')
 require(p.is_file(),'public file exists: '+str(value));return p

def rel(value):return path(value).resolve().relative_to(ROOT.resolve()).as_posix()

def digest(value):return sha256(path(value).read_bytes()).hexdigest()

def load(value):return json.loads(path(value).read_bytes())

def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')

def check_map(values,label):
 require(isinstance(values,dict) and bool(values),label+' nonempty map')
 for name,expected in values.items():
  require(isinstance(name,str) and not Path(name).is_absolute() and '..' not in Path(name).parts and '\\' not in name
    and isinstance(expected,str) and re.fullmatch('[0-9a-f]{64}',expected) is not None,label+' safe relative SHA path')
  require(digest(name)==expected,label+' final live exact bytes: '+name)

def owned_process(value,window_value,window):
 process=load(value);child=process['child_argv']
 require(len(child)==9 and Path(child[0]).resolve()==(ROOT/'.venv/Scripts/python.exe').resolve()
  and child[1:4]==['-B','-X','utf8'] and Path(child[4]).resolve()==(ROOT/CANONICAL).resolve()
  and child[5]=='--receipt' and child[7]=='--visible-ms' and re.fullmatch('[0-9]+',child[8])is not None and 0<int(child[8])<=120000,'canonical actual child argv, not a cache or synthetic result')
 raw=Path(child[6]);require(raw.is_absolute() and raw.name==path(window_value).name,'raw/public receipt basename preserved')
 require(process['section']==303 and process['kind']=='actual_native_window_owned_process_execution'
  and process['status']=='completed' and type(process['exit_code']) is int and process['exit_code']==0
  and type(process['child_primary_exit']) is int and process['child_primary_exit']==0 and process['timed_out'] is False
  and process['owned_job_no_live_execution_verified'] is True and process['source_before_after_unchanged'] is True
  and process['window_receipt_sha256']==digest(window_value),'actual supervisor+primary child0, owned job empty, exact report')
 argv=process['argv'];require(argv.count('--')==1 and argv[argv.index('--')+1:]==child
  and argv.count('--status')==1 and argv.count('--timeout')==1,'actual supervisor/child argv exact correspondence')
 status=Path(argv[argv.index('--status')+1]);require(status.is_absolute() and status.name==process['supervisor_receipt']=='supervisor.json'
  and 0<float(argv[argv.index('--timeout')+1])<=3690,'bounded owned supervisor raw status')
 spath=path(value).with_name('supervisor.json');sup=load(spath)
 require(sup['status']=='completed' and sup['argv']==child and type(sup['pid']) is int and sup['pid']>0
  and sup['supervisor_exit']==process['exit_code']==0 and sup['child_primary_exit']==process['child_primary_exit']==0
  and sup['timed_out'] is False and sup['owned_handle_retained'] is True and sup['owned_job_assigned'] is True
  and sup['owned_job_no_live_execution_verified'] is True and sup['global_process_termination'] is False
  and sup['game_operations']==sup['chat_requests']==0 and not sup.get('launch_or_supervision_error'),
  'original retained-Popen/owned-job terminal record, no invented natural all-descendant exit')
 sources=[Path(arg) for arg in argv[1:argv.index('--')] if isinstance(arg,str) and arg.endswith('.py')]
 require(len(sources)==1 and digest(sources[0])==process['supervisor_sha256']==sup['supervisor_sha256'],'actual supervisor source exact bytes')
 for channel in ('stdout','stderr'):
  row=sup[channel];require(Path(row['file']).name==row['file'],'public original log basename')
  log=spath.with_name(row['file']);require(digest(log)==row['sha256'] and path(log).stat().st_size==row['bytes'],'actual supervisor raw '+channel)
 return raw,{'receipt':rel(value),'sha256':digest(value),'supervisor_receipt':rel(spath),'supervisor_sha256':digest(spath),
  'actual_supervisor_exit':0,'actual_primary_child_exit':0,'owned_job_no_live_execution_verified':True,
  'supervisor_child_launch_pid':sup['pid'],'fixture_reported_pid':window['process_id'],'same_pid_required':False,
  'historical_ancestry_or_fixture_job_membership_verified':False,
  'cleanup':{'active_after_primary_child_exit':sup.get('owned_job_active_processes_after_child_exit'),
    'descendants_live_before_cleanup':sup.get('owned_descendants_still_live'),'termination_scope_recorded':sup.get('termination_scope'),
    'all_descendants_natural_exit_claimed':False}}

def original_window(main_value,focus_value,fixture,necessary_data,necessary_value,native_value):
 main,focus=load(main_value),load(focus_value)
 require(path(main_value).resolve()==(ROOT/'verification/sections/303-main-window.json').resolve()
  and path(focus_value).resolve()==(ROOT/'verification/sections/303-main-window-focus.json').resolve(),
  'strict same-section canonical303 main/focus receipt paths')
 require(main['section']==303 and focus['section']==303
  and main['necessary_receipt_sha256']==digest(necessary_value)
  and main['native_receipt_sha256']==digest(native_value)
  and main['native_receipt']==rel(native_value) and main['necessary_receipt']==rel(necessary_value)
  and focus['main_receipt_sha256']==digest(main_value),
  'actual303 main binds both final evidence receipts; focus binds exact same main bytes')
 require(main['source_sha256_before']==main['source_sha256_after']==fixture['source_sha256_after']
  and set(main['source_sha256_after'])==selected_window_sources(),
  'same final actual native_selected source map stable through original window restart')
 check_map(main['source_sha256_after'],'original303 window final native_selected sources')
 timestamps={name:datetime.fromisoformat(value.replace('Z','+00:00')) for name,value in {
  'started':main['started_utc'],'finished':main['finished_utc'],'focus':focus['at_utc'],
  'necessary_finished':necessary_data['finished_utc'],'native_finished':fixture['finished_at']}.items()}
 require(all(value.tzinfo is not None and value.utcoffset() is not None for value in timestamps.values()),
  'actual main/focus/final-check timestamps are timezone-aware')
 require(timestamps['started']>timestamps['necessary_finished'] and timestamps['started']>timestamps['native_finished']
  and timestamps['finished']>=timestamps['started'] and timestamps['focus']>=timestamps['finished'],
  'original303 restart occurs after both final validations; focus follows completed main receipt')
 require(main['passed'] is True and main['private_file_hash_comparison_count']==5 and main['private_hashes_equal'] is True
  and main['changed_private_paths']==[] and main['private_contents_parsed_copied_or_restored'] is False and main['no_private_restoration'] is True,
  'actual original-window update/private5 hash unchanged, no content parsing/copy/restore')
 require(len(main['visible_windows'])==1,'one visible original project window');visible=main['visible_windows'][0]
 require(visible['visible'] is True and visible['responding'] is True and visible['minimized'] is False and visible['hwnd']>0
  and visible['pid']!=fixture['process_id'],'original window responsive/visible and not fixture')
 require(focus['visible'] is True and focus['pid']==visible['pid'] and focus['hwnd']==focus['actual_foreground']==visible['hwnd'],
  'actual foreground original project window')
 return {'receipt':rel(main_value),'sha256':digest(main_value),'focus_receipt':rel(focus_value),'focus_sha256':digest(focus_value),
  'section':303,'necessary_receipt_sha256':digest(necessary_value),'native_receipt_sha256':digest(native_value),
  'native_selected_current_source_unchanged':True,'started_after_final_necessary_and_native':True,'focus_after_main_finished':True,
  'private_hash_comparisons':5,'changed_private_paths':0,'visible_responsive_foreground':True,'private_contents_read_by_helper':False}

def join_sources(necessary_map,native_map):
 common=set(necessary_map)&set(native_map);extra=set(native_map)-set(necessary_map)
 require(bool(common)and all(necessary_map[n]==native_map[n]for n in common),'all common necessary/native source bytes match')
 additional={}
 for name in sorted(extra):
  require(name.startswith('research/')and Path(name).suffix in{'.html','.json','.md','.png'},
   'native-only extra must be an existing public source document, never omitted product code or new runtime data')
  require(digest(name)==native_map[name],'actual native-only document still current')
  parent_bytes=subprocess.check_output(['git','show',PARENT+':'+name],cwd=ROOT)
  require(sha256(parent_bytes).hexdigest()==native_map[name],'native-only document exact unchanged parent bytes')
  additional[name]={'sha256':native_map[name],'native_actual_before_after_guarded':True,
   'current_file_verified':True,'parent_blob_verified':True,'parent_commit':PARENT,'absent_from_necessary_map':True}
 return{'necessary_source_files':len(necessary_map),'native_selected_source_files':len(native_map),
  'common_source_files':len(common),'native_is_subset_of_necessary':not bool(extra),
  'additional_native_document_sources':additional,'joined_source_files':len(set(necessary_map)|set(native_map)),
  'arbitrary_missing_sources_permitted':False}

def visual_review(value,window):
 name='verification/sections/303-preparation/root-visual-review.json';review=load(name)
 require(review['section']==303 and review['kind']=='root_archived_native_images_review'
  and review['actual_images_opened_with_view_image']is True,'root actually reviewed new303 images')
 expected={rel(path(value).with_name(Path(row['path']).name)):row['sha256']for row in window['screenshots']}
 require(review['images']==expected and review['actual_image_count']==len(expected),'root visual review exact all actual images')
 return{'receipt':name,'sha256':digest(name),'actual_root_reviewed_images':len(expected),'helper_performed_visual_review':False}

def selected_window_sources():
 # The already-reviewed canonical script has no product/Qt import at module scope.
 # Its explicit public-byte bound_files() is the actual producer, not guessed counts.
 result=runpy.run_path(str(path(CANONICAL)))['bound_files']()
 check_map(result,'canonical selected public source producer')
 return set(result)

def preparation_archive(value):
 record=load(value);require(record['section']==303 and type(record['files'])is dict and bool(record['files']),'public preparation archive exact section and nonempty inventory')
 base=path(value).parent
 for name,pin in record['files'].items():
  require(type(name)is str and not Path(name).is_absolute()and'..'not in Path(name).parts and'\\'not in name,'relative public preparation member')
  member=base/name
  require(digest(member)==pin['sha256']and path(member).stat().st_size==pin['bytes'],'exact retained preparation/first evidence '+name)
 return{'receipt':rel(value),'sha256':digest(value),'member_count':len(record['files']),
  'preparation_or_author_checks_added_to_product_pass_count':False}

def necessary_attempt_history(final_value):
 result=[];final=path(final_value).resolve()
 for record_path in sorted((ROOT/'verification/sections').glob('303-necessary-*/process.json')):
  if record_path.resolve()==final:continue
  record=load(record_path);require(record['section']==303,'same-section actual necessary history only')
  stderr=record_path.with_name('stderr.txt');text=path(stderr).read_text(encoding='utf8')
  match=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',text)
  ending=re.findall(r'FAILED \(([^)]+)\)',text)
  result.append({'receipt':rel(record_path),'sha256':digest(record_path),'stderr':rel(stderr),'stderr_sha256':digest(stderr),
   'actual_exit':record['exit_code'],'timed_out':record.get('timed_out',False),
   'observed_methods':int(match[-1][0])if match else None,'observed_failure_summary':ending[-1]if ending else None,
   'source_before_after_unchanged':record['source_sha256_before']==record['source_sha256_after'],
   'counts_added_to_final_methods_passed':False,'prior_attempt_not_relabelled_as_final':True})
 return result

def same_json(a,b):
 return json.dumps(a,sort_keys=True,allow_nan=False)==json.dumps(b,sort_keys=True,allow_nan=False)

def method_asts(value):
 tree=ast.parse(path(value).read_bytes())
 return{n.name:ast.dump(n,include_attributes=False)for c in tree.body if isinstance(c,ast.ClassDef)
  for n in c.body if isinstance(n,ast.FunctionDef)and n.name.startswith('test_')}

def historical_maintenance():
 result={}
 for name,expected in MAINTENANCE.items():
  original='verification/sections/303-preparation/historical-tests/before/'+name
  parent_bytes=subprocess.check_output(['git','show',PARENT+':'+name],cwd=ROOT)
  require(path(original).read_bytes()==parent_bytes,'exact original old test before303 '+name)
  require(digest(name)==expected,'reviewed exact compatibility patch '+name)
  before,after=method_asts(original),method_asts(name)
  require(before.keys()==after.keys(),'no historical test method removed or renamed '+name)
  changed=[key for key in before if before[key]!=after[key]]
  if name.endswith('294.py'):
   require(len(before)==18 and changed==[],'all18 historical294 method ASTs unchanged')
   require('prior-direct-references.json'in path(name).read_text(encoding='utf8')
    and '63ec9488f8f905d2ced1a4e349413e9c92d78125b9f1c94c00293cafa4d348f5'in path(name).read_text(encoding='utf8'),
    'historical294 exact public58 fixture, not current data replacement')
  else:
   require(len(before)==9 and changed==['test_unaccepted_wood_decorations_and_portal_probes_are_retained'],
    'only one historical048 method changes; other8 ASTs unchanged')
  result[name]={'before':original,'before_sha256':digest(original),'after_sha256':expected,
    'original_method_count':len(before),'unchanged_method_ASTs':len(before)-len(changed),'changed_methods':changed,
    'not_skipped_or_removed':True,'historical_public_replay_not_private_or_full_acceptance':True}
 old_builder='scripts/extend_direct_landmark_294.py'
 require(path(old_builder).read_bytes()==subprocess.check_output(['git','show',PARENT+':'+old_builder],cwd=ROOT),
  'historical294 builder unchanged')
 return result

def public_local_bindings(data):
 # Filled from the actual necessary runner contract before this helper is frozen.
 bindings=data['local_public_input_bindings']
 before=data['local_public_input_sha256_before'];after=data['local_public_input_sha256_after']
 declared='verification/sections/303-preparation/historical-source-inputs/local-public-bindings.json'
 require(digest(declared)=='df86f3604392ad20e6f20b5a796277ce1796eb7d6ded031ddfab38b2e5522d05',
  'frozen explicit public historical replay binding manifest')
 require(data['local_public_binding_manifest']==declared and data['local_public_binding_manifest_sha256']==digest(declared)
  and data['local_public_input_binding_error_after']is None and data['original_test_runtime_paths_redirected']is False
  and data['historical_public_replay_not_private_original_samples']is True,
  'actual runner declares original paths and successful dual public replay, not redirected/private history')
 frozen=load(declared)
 # Runtime author publishes the list itself or an enclosing manifest; both read
 # the exact same immutable bytes, not a mutable test-output guess.
 expected=frozen if type(frozen)is list else frozen['bindings']
 require(same_json(bindings,expected)and len(bindings)==10 and before==after,
  'actual local/public historical input maps stable and complete10')
 require(data['local_public_input_bytes_before']==data['local_public_input_bytes_after']
  =={r['local_path']:r['bytes']for r in bindings},'actual local replay lengths guarded twice')
 require(set(before)=={r['local_path']for r in bindings},'no actual local replay consumption omitted')
 for row in bindings:
  local,public=row['local_path'],row['public_path']
  require(type(local)is str and local.startswith('.cache/')and'..'not in Path(local).parts,
   'only declared public historical cache inputs, no private paths')
  require(type(public)is str and public.startswith(('research/','rouge/data/',
   'verification/sections/303-preparation/historical-source-inputs/legacy-cache/')),
   'exact public counterpart, not private state')
  require(digest(local)==digest(public)==row['sha256']==before[local]
   and path(local).stat().st_size==path(public).stat().st_size==row['bytes'],
   'actual local bytes equal stable public source '+local)
  require(data['source_sha256_after'].get(public)==row['sha256'],'public counterpart in standard source map')
 return{'bindings':bindings,'before_after_unchanged':True,'actual_local_public_inputs_guarded':True,
  'private_historical_samples_or_full_validation_claimed':False}

def required_modules():
 # The frozen actual necessary runner lists the complete unchanged4+new1 scope.
 ready=load('verification/sections/303-preparation/runtime-preparation/READY.json')
 modules=ready['necessary_modules']
 require(type(modules)is list and len(modules)==len(set(modules))==5
  and {'tests.test_direct_landmark_294','tests.test_map_projection_048'}<=set(modules),
  'full required five-module current and historical map scope')
 return set(modules)

def necessary(value):
 data=load(value)
 require(data['section']==303 and data['kind']=='necessary_change_related_tests_not_full_suite'
  and type(data['exit_code'])is int and data['exit_code']==0 and data.get('timed_out',False)is False
  and data['source_unchanged']is True and data['source_sha256_before']==data['source_sha256_after'],
  'actual final necessary0/stable')
 modules=data['modules']
 require(type(modules)is list and len(modules)==len(set(modules))and set(modules)==required_modules()
  and data['argv'][1:7]==['-B','-X','utf8','-m','unittest','-v']and data['argv'][7:]==modules
  and data['source_commit_before']==PARENT,'actual exact complete5 required modules and parent')
 require(data['game_sampling_verified']is False and data['chat_verified']is False
  and data['full_scope_reduced']is False and data['full_suite_rerun']is False,'necessary not full/private/game/chat')
 minimum={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/**/*.py')}
 minimum|={p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/data/*.json')}
 minimum|={'tests/'+m.split('.')[-1]+'.py'for m in modules}|selected_window_sources()|{BUILDER}
 require(minimum<=set(data['source_sha256_after']),'all current product/static JSON/current+old tests/source members guarded')
 require(all(not n.startswith(('.cache/','.local/'))for n in data['source_sha256_after']),
  'standard source map contains no local/private inputs')
 check_map(data['source_sha256_after'],'actual necessary sources')
 old_ref=load('verification/sections/302.json')['necessary_validation']
 require(digest(old_ref['receipt'])==old_ref['sha256'],'actual previous302 necessary receipt')
 old=load(old_ref['receipt'])
 kept={n:v for n,v in old['source_sha256_after'].items()if n.startswith('rouge/')and n not in CHANGED_EXISTING
  and(n.endswith('.py')or(n.startswith('rouge/data/')and n.endswith('.json')))}
 require(bool(kept)and all(data['source_sha256_after'].get(n)==v for n,v in kept.items()),
  'all original product code/staticJSON except one direct reference data unchanged')
 tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only',PARENT,'--','tests'],cwd=ROOT,text=True).splitlines())
 changed=set(subprocess.check_output(['git','diff','HEAD','--name-only','--','tests'],cwd=ROOT,text=True).splitlines())
 require(tracked&changed==set(MAINTENANCE),'only exact two old test compatibility changes')
 maintenance=historical_maintenance();local=public_local_bindings(data)
 log=path(value).with_name('stderr.txt');text=log.read_text(encoding='utf8')
 counts=re.findall(r'Ran ([0-9]+) tests in ([0-9.]+)s',text)
 require(len(counts)==1 and int(counts[0][0])>0 and text.rstrip().endswith('OK')
  and not re.search(r'^(FAIL|ERROR):',text,re.M),'actual unmodified Ran/OK log')
 return data,{'receipt':rel(value),'sha256':digest(value),'stderr':rel(log),'stderr_sha256':digest(log),
  'stdout_sha256':digest(path(value).with_name('stdout.txt')),'actual_exit':0,'methods_run':int(counts[0][0]),
  'seconds':float(counts[0][1]),'source_files':len(data['source_sha256_after']),'source_unchanged':True,
  'modules':modules,'unchanged_existing_product_Python_static_JSON_files':len(kept),
  'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),'old_tracked_test_maintenance':maintenance,
  'local_public_input_replay':local,'author_checks_not_added_to_formal_methods':True}

def promotion(value,tests,reviewed_sha):
 record=load(value)
 require(record['section']==303 and record['parent_commit']==PARENT and record['old_tests_modified']is True
  and record['old_test_maintenance_scope_exact']is True,'exact303 parent and explicit old-test maintenance')
 require(set(record['existing_production_changes'])==CHANGED_EXISTING
  and set(record['historical_test_maintenance'])==set(MAINTENANCE),'sole current data and two old tests separate')
 expected={CANONICAL,BUILDER,'tests/test_direct_landmark_303.py'}
 expected|={p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file()}
 require(set(record['promoted'])==expected and record.get('native_script_pending',False)is False,
  'all actual new functional paths, no old-test maintenance mixed in')
 functional={**record['promoted'],**record['existing_production_changes']}
 validated={**functional,**record['historical_test_maintenance']}
 check_map(validated,'final function and maintenance source bytes')
 require(all(tests['source_sha256_after'].get(n)==v for n,v in validated.items()),'all final validated source bytes in actual necessary')
 for name in CHANGED_EXISTING|set(MAINTENANCE):
  old=subprocess.check_output(['git','show',PARENT+':'+name],cwd=ROOT)
  require(sha256(old).hexdigest()==record['before_existing_sha256'][name],'exact parent bytes for old changed path '+name)
 require(digest(CANONICAL)==reviewed_sha,'final reviewed native script source')
 return functional,validated,{'receipt':rel(value),'sha256':digest(value),
  'new_functional_paths_including_final_native':len(expected),'functional_source_paths':len(functional),
  'maintenance_source_paths':len(MAINTENANCE),'validated_source_paths':len(validated),
  'existing_production_paths':1,'historical_test_maintenance_paths':sorted(MAINTENANCE),
  'canonical_native_separately_bound':{'path':CANONICAL,'sha256':reviewed_sha},'promotion_is_not_acceptance':True}

def packet():
 require(digest(MANIFEST)==MANIFEST_SHA and digest(DATA)==DATA_SHA and digest(COMPARISON)==COMPARISON_SHA,
  'frozen full direct-map manifest, final append and complete build comparison')
 manifest=load(MANIFEST);data=load(DATA);prior=load(PACKET+'/prior-direct-references.json')
 regular=load(PACKET+'/prior-regular-projections.json');comparison=load(COMPARISON)
 require(manifest['section']==303 and manifest['all_source_eligible_requests']==89
  and manifest['agreement_tolerance_px']==4 and manifest['source_adjustments']==0,'complete89/4px frozen input')
 for name,pin in manifest['files'].items():
  require(digest(name)==pin['sha256']and path(name).stat().st_size==pin['bytes'],'all source originals fresh byte equality '+name)
 require(digest(PACKET+'/READER_A_ORIGINAL.json')=='ccef7dd5a1cf227945a29143dfd41eadc4b39deb412b970850d53f3aab8083e2'
  and digest(PACKET+'/READER_B_ORIGINAL.json')=='03179421fe88573290a2fa342bd856eca8b9ba95d443d8a753ebd216c6701994',
  'both complete first reader originals unchanged; not humans or gameplay measurements')
 require(same_json(load(REGULAR),regular),'whole regular12/24 dictionary unchanged')
 for group in ('references','stages'):
  require(all(k in data[group]and same_json(data[group][k],v)for k,v in prior[group].items()),'all old58 complete records unchanged')
 require(sum(len(r['points'])for r in prior['references'].values())==58
  and len(data['references'])==12 and len(data['stages'])==21
  and sum(len(r['points'])for r in data['references'].values())==107,'actual prior58 and resulting12/21/107')
 require(comparison['section']==303 and comparison['source_manifest_sha256']==MANIFEST_SHA
  and comparison['source_pixel_adjustments']==0 and comparison['new_requested_points']==89
  and comparison['original58_records_unchanged']is True and comparison['original_regular_dictionary_unchanged']is True
  and comparison['actual_enemy_position_inverse_or_segment_verified']is False,'retained complete actual build comparison')
 rows=comparison['new_agreement_comparisons'];require(len(rows)==89 and len({r['request_id']for r in rows})==89,'all requests incl null/rejected preserved')
 readers={k:load(PACKET+'/READER_'+k+'_ORIGINAL.json')for k in ('A','B')}
 accepted={};counts={}
 for row in rows:
  identity=row['reference'];require(identity in('ro6_b_6','ro6_n_2_3')and row['tile_key']in('tile_floor','tile_road'),'exact LOWLAND floor/road source groups')
  for key,column in(('A','observed_pixel'),('B','independent_pixel')):
   index=row['original_reader_rows'][key]
   require(index['file']=='READER_'+key+'_ORIGINAL.json','exact original reader file identity')
   original=readers[key]['images'][index['image_index']]['readings'][index['reading_index']]
   require(original['request_id']==row['request_id']and original['row']==row['row']and original['col']==row['col']
    and same_json(original['pixel'],row[column]),'unmodified exact reader pixels/link '+row['request_id'])
  a,b=row['observed_pixel'],row['independent_pixel']
  finite=lambda v:type(v)is list and len(v)==2 and all(type(n)in(int,float)and math.isfinite(n)for n in v)
  distance=math.hypot(a[0]-b[0],a[1]-b[1])if finite(a)and finite(b)else None
  allowed=distance is not None and distance<=4
  require(row['agreement_px']==distance and row['accepted_for_runtime']is allowed,'exact unrounded Euclidean gate; no averaging')
  counts[identity]=counts.get(identity,0)+int(allowed)
  if allowed:accepted[(identity,row['row'],row['col'])]=row
 require(counts=={'ro6_b_6':37,'ro6_n_2_3':12}and len(accepted)==comparison['new_accepted_points']==49
  and comparison['new_rejected_or_unknown_points']==40,'actual computed49 accepted/40 retained rejects')
 for identity in ('ro6_b_6','ro6_n_2_3'):
  ref=data['references'][identity]
  require(ref['agreement_tolerance_px']==4,'existing direct admission gate unchanged')
  require(len(ref['points'])==counts[identity],'no unaccepted points added')
  for point in ref['points']:
   original=accepted[(identity,point['row'],point['col'])]
   require(all(same_json(point[k],original[k])for k in('observed_pixel','independent_pixel','agreement_px','tile_key','original_reader_rows')),
    'only accepted first-reader pixel, no adjustment or mean')
 require(data['stages']['ro6_n_2_3']['reference']==data['stages']['ro6_e_2_3']['reference']=='ro6_n_2_3'
  and data['stages']['ro6_n_2_3']['level_sha256']==data['stages']['ro6_e_2_3']['level_sha256'],
  'normal/emergency alias shares explicit source geometry but keeps separate image path')
 records=load(PACKET+'/source-records.json')['stages']
 for sid,meta in records.items():
  binding=data['stages'][sid];ref=data['references'][binding['reference']]
  require(binding['image_file']==meta['image']['file']and binding['level_sha256']==meta['level_source']['sha256']
   and ref['bitmap_sha256']==meta['image']['sha256']and ref['grid_sha256']==meta['grid_sha256']
   and[ref['rows'],ref['cols']]==meta['grid_size']and[ref['width'],ref['height']]==[meta['image']['width'],meta['image']['height']],
   'exact stage alias/image/level/grid/dimensions preserved '+sid)
 return{'manifest':MANIFEST,'manifest_sha256':MANIFEST_SHA,'data':DATA,'data_sha256':digest(DATA),
  'comparison':COMPARISON,'comparison_sha256':digest(COMPARISON),'source_members':len(manifest['files']),
  'all89_original_requests_preserved':True,'accepted_points':49,'rejected_or_unknown_points':40,
  'per_image_accepted':counts,'old58_complete_records_unchanged':True,'regular12_images24_stages_unchanged':True,
  'prior_partial_direct_scope':[10,18,58],'current_partial_direct_scope':[12,21,107],
  'whole_map_gaps_unchanged':[81,59],'reader_kind':'two isolated-context agents, not human/gameplay observers',
  'actual_enemy_position_inverse_or_segment_verified':False}

def native(value,process_value,tests,reviewed_sha):
 data=load(value)
 require(data['section']==303 and data['kind']=='isolated_native_windows_direct_ground_centers'
  and data['passed']is True and data['failure']is None and data['qpa']=='windows'
  and type(data['qt_exit_code'])is int and data['qt_exit_code']==0
  and data['verification_window_closed']is True,'actual complete owned native303 Qt0 and closed')
 require(type(data['process_id'])is int and data['process_id']>0 and digest(CANONICAL)==reviewed_sha,
  'actual fixture PID and reviewed canonical source')
 tree=ast.parse(path(CANONICAL).read_text(encoding='utf8'))
 labels={n.args[1].value for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)
  and n.func.id=='require'and len(n.args)>1 and isinstance(n.args[1],ast.Constant)and type(n.args[1].value)is str}
 require(type(data['checks'])is list and len(data['checks'])==len(set(data['checks']))==data['unique_checks']
  and labels<=set(data['checks'])and data['successful_assertion_executions_including_repeated_guards']>=len(data['checks']),
  'all reviewed native labels actually executed; dynamic counts')
 require(data['source_sha256_before']==data['source_sha256_after']
  and set(data['source_sha256_after'])==selected_window_sources()
  and data['source_guard_is_selected_not_all_transitive_dependencies']is True,'selected source exact/stable')
 check_map(data['source_sha256_after'],'native303 source')
 joined=join_sources(tests['source_sha256_after'],data['source_sha256_after'])
 require(data['temporary_state_root']is True and data['state_paths_replaced_before_constructor']==['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE']
  and data['private_state_read_copied_or_restored']is False and data['external_entrypoints_blocked_before_original_call']is True,
  'four temporary paths before constructor, no private contents')
 attempts=data['external_operation_attempts']
 require(set(attempts)=={'game_enumeration','game_connect','game_capture','game_next_frame','desktop_start','desktop_request','provider_chat','credential_read'}
  and all(type(v)is int and v==0 for v in attempts.values()),'actual eight external attempt counters zero')
 require(data['game_operated']is False and data['game_captures']==0 and data['chat_sent']is False and data['chat_attempted']is False
  and data['original_project_window_operated_or_restarted']is False and data['actual_process_termination_verified_by_this_script']is False
  and data['owned_supervisor_exit_and_cleanup_required_separately']is True
  and data['launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID']is True,
  'fixture does not claim game/chat, original private window update, or process genealogy/terminal cleanup')
 raw,process=owned_process(process_value,value,data)
 stages=['ro6_b_6','ro6_n_2_3','ro6_e_2_3'];sizes=[[1280,850],[1440,900],[1520,940]]
 require(data['expected_stage_ids']==stages and data['requested_logical_sizes']==sizes,
  'three exact stage aliases and three reviewed requested sizes')
 require(data['accepted_point_source']==COMPARISON and data['actual_accepted_source_points']==49
  and data['source_requested_points']==89 and data['rejected_or_unknown_source_points']==40
  and data['prior_direct_points_preserved']==58 and data['regular_image_and_stage_scope_preserved']==[12,24]
  and data['remaining_full_map_stage_and_image_gaps']==[81,59],'actual source counts, prior scope and full-map limits')
 require(data['total_partial_scope_from_current_data']==[12,21,107],'actual current partial12/21/107, not full-map completion')
 runtime=load(DATA);comparisons=load(COMPARISON)['new_agreement_comparisons']
 observations=data['stage_observations'];require(len(observations)==3 and[r['stage_id']for r in observations]==stages,
  'each actual stage alias flow retained')
 handles=set();size_count=0
 def handle(row,requested=None):
  require(type(row['hwnd'])is int and row['hwnd']>0 and row['process_id']==data['process_id']and row['qpa']=='windows',
   'actual native HWND belongs to fixture PID')
  if requested is not None:require(row['client_size']==requested,'actual client size, not requested-only')
  else:require(row['client_size']in sizes,'screenshot actual client size in reviewed three sizes')
  handles.add(row['hwnd'])
 for observation in observations:
  sid=observation['stage_id'];reference=runtime['stages'][sid]['reference']
  points=runtime['references'][reference]['points']
  expected={(p['row'],p['col']):p['observed_pixel']for p in points}
  require(len(observation['sizes'])==3 and[r['requested_size']for r in observation['sizes']]==sizes,
   'actual three-size coverage per stage')
  for size in observation['sizes']:
   handle(size['native_window'],size['requested_size']);size_count+=1
   mapped=size['mapped_accepted_points']
   require(len(mapped)==len(expected)and{(p['cell']['row'],p['cell']['col']):p['source_pixel']for p in mapped}==expected
    and all(type(v)in(int,float)and math.isfinite(v)for p in mapped for v in p['widget_pixel'])
    and size['same_size_refresh_preserved']is True,'each accepted original pixel displayed at every actual size; refresh preserved')
  manual=observation['clicked_registered_ground_cell'];unknown=observation['clicked_unknown_ground_cell_left_unmapped']
  raised=observation['clicked_raised_surface_left_unmapped'];move=observation['new_MOVE_cell']
  require((manual['row'],manual['col'])in expected and(move['row'],move['col'])in expected
   and(unknown['row'],unknown['col'])not in expected and(raised['row'],raised['col'])not in expected,
   'accepted manual/MOVE vs rejected and raised positions separate')
  rejected=observation['rejected_source_row']
  require(any(same_json(rejected,r)for r in comparisons if r['reference']==reference and r['accepted_for_runtime']is False)
   and rejected['row']==unknown['row']and rejected['col']==unknown['col'],'unmapped click is a retained original rejected request')
  require(type(observation['actual_selected_main_SPAWN_row_id'])is str
   and type(observation['MOVE_added_yellow_pixels'])is int and observation['MOVE_added_yellow_pixels']>0
   and observation['MOVE_yellow_before']>=0 and observation['MOVE_yellow_after']>=observation['MOVE_added_yellow_pixels']
   and observation['MOVE_unchanged_geometry']is True
   and same_json(observation['MOVE_geometry_before'],observation['MOVE_geometry_after']),
   'same-geometry actual yellow MOVE difference, not map repaint geometry change')
  require(observation['right_original_supports_segments']is False and observation['logical_grid_existing_route_lines_unchanged']is True
   and observation['actual_enemy_position_or_route_activation']is None and observation['inverse_or_full_calibration_claimed']is False,
   'sparse original points do not imply segments/inverse/current enemy or full calibration')
 images=data['screenshots'];names={sid+'-mapped'for sid in stages}|{'ro6_b_6-rejected','ro6_n_2_3-rejected'}
 require(data['screenshot_count']==len(images)==5 and{r['name']for r in images}==names and all(r['player_text']is True for r in images),
  'five actual representative player images, three maps and two unmarked rejected positions')
 require(same_json(data['extra_screenshots'],[r for r in images if r['name'].endswith('-rejected')]),
  'two extras are already included in five; do not double-count screenshots')
 for image in images:
  source=Path(image['path']);require(source.is_absolute()and source.parent==raw.parent,'original owned screenshot namespace retained')
  output=path(value).with_name(source.name);blob=path(output).read_bytes()
  require(sha256(blob).hexdigest()==image['sha256']and blob[:8]==b'\x89PNG\r\n\x1a\n'and len(blob)>24
   and all(v>0 for v in struct.unpack('>II',blob[16:24])),'actual PNG/hash/header/dimensions')
  handle(image['native_window'])
  if image['name'].endswith('-rejected'):
   require(image['original_marker']is None and any(r['request_id']==image['source_request_id']
    and r['rejection']==image['source_rejection']and r['accepted_for_runtime']is False for r in comparisons),
    'actual rejected-surface screenshot points to rejected source and no original marker')
 require(size_count==9 and len(handles)==1,'actual nine stage-size runs share one isolated owned MainWindow')
 return data,{'receipt':rel(value),'sha256':digest(value),'reviewed_native_source_sha256':reviewed_sha,
  'source_selected_files':len(data['source_sha256_after']),'source_unchanged':True,'source_join':joined,
  'unique_checks':data['unique_checks'],'actual_assertion_executions':data['successful_assertion_executions_including_repeated_guards'],
  'screenshots':len(images),'representative_images':len(images),'actual_player_reader_images':len(images),
  'actual_stage_size_combinations':size_count,'actual_stage_ids':stages,'actual_logical_sizes':sizes,
  'actual_Qt_exit':0,'owned_process':process,'actual_game_enemy_position_or_inverse_or_segments_verified':False}

def main(args):
 require(Path(__file__).resolve()==(HERE/'close_section_303.py').resolve(),'canonical reviewed cache303 helper')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 require(branch=='codex/p2-development'and parent==PARENT and not(ROOT/'verification/sections/303.json').exists(),
  'authorized branch and exact parent; exclusive303 closeout')
 require(digest(CANONICAL)==args.native_source_sha256,'reviewed native source before executing selected source producer')
 source_ref=packet();archive_ref=preparation_archive(args.preparation_archive_manifest)
 tests,test_ref=necessary(args.necessary_receipt)
 feature_map,validated_map,promotion_ref=promotion(args.promotion_receipt,tests,args.native_source_sha256)
 window,window_ref=native(args.window_receipt,args.window_process_receipt,tests,args.native_source_sha256)
 window_ref['root_visual_review']=visual_review(args.window_receipt,window)
 main_ref=original_window(args.main_window_receipt,args.focus_receipt,window,tests,args.necessary_receipt,args.window_receipt)
 full=load(FULL)
 require(digest(FULL)==FULL_SHA and full['after_section']==290 and full['available_checks_passed']is True
  and full['scope_not_reduced']is True and full['complete_repository_validation']is False,'only historical290 full scope reused')
 cp=load('DEVELOPMENT_CHECKPOINT.json')
 require(cp['completed_sections']==cp['latest_functional_section']==302 and cp['next_section']==303
  and cp['active_section']['section']==303 and cp['policy']['priority_order']==['P3','P2','P1']
  and cp['policy']['current_user_batch_target_section']is None and cp['policy']['stop_after_section']is None,
  'actual active303/current302, P3-first and no numeric endpoint')
 require(cp['last_full_validation']['after_section']==290 and cp['current_available_full_validation']['section']==290
  and cp['policy']['full_validation_interval']==15 and cp['policy']['full_validation_anchor_section']==125
  and 125+((303-125)//15+1)*15==305,'historical full290 and next cadence305 unchanged')
 cloud=cp['last_verified_cloud_save'];proof=load(cloud['proof'])
 require(cloud['section']==302 and digest(cloud['proof'])==cloud['proof_sha256']and proof['passed']is True
  and proof['commit']==proof['remote_HEAD']==cloud['commit']and proof['push_primary_exit']==0,
  'actual previous302 ordinary publication')
 docs={n:path(n).read_bytes()for n in('DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md',
  'PROJECT_REQUIREMENTS.md','AGENTS.md','PROJECT_PROGRESS.md')}
 progress=docs['PROJECT_PROGRESS.md'];text=progress.decode('utf8')
 require(sha256(progress).hexdigest()==PROGRESS_SHA_BEFORE and text.count(OLD_PROGRESS)==1,
  'actual old todo source, exact one scope fragment only')
 new_progress=text.replace(OLD_PROGRESS,NEW_PROGRESS,1).encode('utf8')
 now=datetime.now(timezone(timedelta(hours=8))).isoformat()
 capability=('畸症及本性难移普通/紧急的固定原图新增49个独立同意的低地地板/道路中心；'
  '两份首次完整读数保留全部89格，37+12通过原4像素门，40个未读清或不同意的格仍不画点。'
  '只用第一读者原像素，不平均或调整；原58点完整记录与12图24关规则投影原样保留。'
  '当前部分参考为12图21关107格，仍不代表81关59图整图校准、高台/入口/出生偏移或实际敌人位置。')
 limits=['两名隔离上下文代理独立读图，不是两位真人或游戏内实测；同意不证明绝对精度。',
  '全部89格比较保留，40拒绝或未知不延伸；部分点不能插值、反查、连线或推实际敌人位置。',
  '原58记录/规则12图24关不变；81关59图完整校准缺口不减；本性难移普通与紧急只共享已证原图和语义网格。',
  '294历史测试仅换SHA绑定公开58输入，18方法AST原样；048仅一个方法迁移当前12点准入，其余8方法AST原样。',
  '旧048公开.cache输入有十项精确公开对照及实际两次hash/bytes守卫；不冒称私有历史样本或本节完整全量。',
  '17typed、15全局层数、25场景/57选项与10附注待办不变；P3/P2/P1未完成，识别最后，不推荐路线。',
  '原290全量按原来源保留，下次305；完成303后续304，无数字终点。']
 receipt={'section':303,'kind':'functional_section','title':TITLE,'at_Beijing':now,'branch':branch,'prior_commit':parent,
  'remaining_item':'P3固定战斗地图映射与独立地标核验','new_capability':capability,
  'files':sorted(feature_map),'source_sha256':feature_map,'validated_source_sha256':validated_map,
  'source_reference':source_ref,'source_promotion':promotion_ref,'preparation_archive':archive_ref,
  'only_existing_production_sources_changed':sorted(CHANGED_EXISTING),
  'existing_source_changes_including_test_maintenance':sorted(CHANGED_EXISTING|set(MAINTENANCE)),
  'old_tracked_test_maintenance':test_ref['old_tracked_test_maintenance'],
  'actual_server_generation_or_inventory_verified':False,'remaining_global_stage_floor_gaps_unchanged':15,
  'original_entry_gaps_unchanged':[25,57],'unparsed_notes_unchanged':10,'typed_named_grant_count_unchanged':17,
  'partial_direct_reference_scope_before':[10,18,58],'partial_direct_reference_scope':[12,21,107],
  'whole_map_gaps_unchanged':[81,59],'necessary_validation':test_ref,
  'necessary_attempt_history':necessary_attempt_history(args.necessary_receipt),
  'native_windows_validation':{**window_ref,'original_project_window':main_ref},
  'full_validation':{'receipt':FULL,'sha256':FULL_SHA,'after_section':290,'full_suite_rerun':False,
   'new303_source_full_validation_claimed':False,'next_periodic_section':305,'scope_not_reduced':True,
   'complete_repository_validation':False},
  'PROJECT_PROGRESS_change':{'before_sha256':PROGRESS_SHA_BEFORE,'after_sha256':sha256(new_progress).hexdigest(),
   'before_fragment':OLD_PROGRESS,'after_fragment':NEW_PROGRESS,'only_exact_scope_fragment_replaced':True},
  'limits':limits,'next_section':304,'cloud_publication_binding':'enclosing_commit','cloud_published':False,
  'P3_complete':False,'P2_complete':False}
 history='historical_before303_current_pointers';require(history not in cp,'exclusive303 current pointer archive')
 cp[history]={k:deepcopy(cp[k])for k in('current_section_save','current_section_validation','latest_section_environment',
  'active_section','current_batch','cloud_publication_closeout')if k in cp}
 cp.pop('active_section',None);cp.pop('cloud_publication_closeout',None)
 cp.update(completed_sections=303,latest_functional_section=303,next_section=304,
  batch_status='P3_SECTION303_VALIDATED_AWAITING_PUBLICATION',next_full_validation_after=305,
  next_action='从304继续有证P3剩余事项，无数字终点；下次完整可用全量305。')
 cp['policy']['next_full_validation_after']=305;cp['current_batch_commit_policy']['next_full_validation_after']=305
 cp['current_batch'].update(status=cp['batch_status'],next_section=304,next_section_started=False,
  receipt='verification/sections/303.json',next_full_validation_after=305,batch_closed=False)
 cp['confirmed_next_stage_direction'].update(last_completed_functional_section=303,next_functional_section_started=False)
 cp['sections'].append({'number':303,'completion_ref':'p3-section-303','topic':TITLE,'verification':'verification/sections/303.json'})
 cp['current_section_save']={'section':303,'verification':'verification/sections/303.json','scope':'current_functional_section',
  'binding':'enclosing_commit','commit_reference':'commit containing303 exact frozen direct-ground append, real acceptance, requirements and index'}
 cp['last_verified_cloud_save']['scope']='previous_functional_section'
 cp['current_section_validation']={'section':303,'receipt':'verification/sections/303.json',
  'necessary_methods_passed':test_ref['methods_run'],'native_isolated_window_checks':window['unique_checks'],
  'full_suite_rerun':False,'last_full_receipt':FULL,'full_source_is_historical290':True}
 cp['latest_section_environment']={'section':303,'receipt':'verification/sections/303.json',
  'native_windows':f"{test_ref['methods_run']} actual necessary; {window['unique_checks']} unique native; {window_ref['screenshots']} representative PNG; original visible/private5 unchanged",
  'native_game_or_chat_verified':False,'current_section_full_rerun':False,'new_Linux_Wine_full_run':False,'last_full_receipt':FULL}
 cp['functional_sections_since_latest_requirement']=list(dict.fromkeys([*cp['functional_sections_since_latest_requirement'],303]))
 completed=(f'## 功能第303节 · {TITLE}\n\n{now}。{capability}\n\n'
  f"实际{test_ref['methods_run']}必要检查、原生{window['unique_checks']}唯一检查通过；{window_ref['screenshots']}张真实代表PNG由根代理查看。"
  '两项历史测试兼容维护与新功能源分开，原失败/原件保留；原窗口更新/私人5路径不变。'
  '来源及回执verification/sections/303.json；部分参考不等于整图校准，其它待办保留。原290全量沿用/下次305，后续304，无数字终点。待普通推送核对。\n\n')
 mutations={'verification/sections/303.json':encode(receipt),'DEVELOPMENT_CHECKPOINT.json':encode(cp),
  'PROJECT_COMPLETED.md':completed.encode()+docs['PROJECT_COMPLETED.md'],'PROJECT_PROGRESS.md':new_progress}
 wip=docs['WORK_IN_PROGRESS.md'].decode();require('## 功能第302节'in wip,'prior302 history retained')
 mutations['WORK_IN_PROGRESS.md']=(completed+wip[wip.index('## 功能第302节'):]).encode()
 req=docs['PROJECT_REQUIREMENTS.md'].decode();a,b=req.index('<!-- current-delivery:start -->'),req.index('<!-- current-delivery:end -->')
 block=('<!-- current-delivery:start -->\n## 当前交付与续接 · 第303节\n\n2026-10-16继续P3，无数字终点。'+capability
  +f"实际{test_ref['methods_run']}必要检查与原生{window['unique_checks']}唯一检查通过；原窗口更新/私人5路径不变。"
  +'部分12/21/107参考并非整图完成，81/59与17typed、15/25/57/10待办保持。290全量原来源/下次305；P3→P2→P1、识别最后，无路线建议。待普通推送核对。\n')
 mutations['PROJECT_REQUIREMENTS.md']=(req[:a]+block+req[b:]).encode()
 agents=docs['AGENTS.md'].decode();a,b=agents.index('## 当前续接 · 第302节'),agents.index('## 当前优先顺序与输出可读性')
 mutations['AGENTS.md']=(agents[:a]+'## 当前续接 · 第303节已完成功能与必要/原生验收\n\n'+capability
  +'来源及实际回执verification/sections/303.json；两项历史测试维护分列，原窗口更新/私人5路径不变。'
  +'未跑303全量，290完整范围沿用原来源。下一节304/下次305，无数字终点。'
  +'P3→P2→P1、识别最后，不推荐/排序/自动选路；待普通推送核对，源码/要求/验收/索引同提交。\n\n'+agents[b:]).encode()
 require('初次招募时即处于已进阶状态'in mutations['PROJECT_REQUIREMENTS.md'].decode()
  and'初次招募即处于已进阶状态'in mutations['AGENTS.md'].decode(),'verified直升 definition preserved')
 require(all(str(i)+'.'in mutations['AGENTS.md'].decode().split('## 当前续接')[0]for i in range(1,6)),
  'highest five independent judgment/source requirements retained')
 archive=ROOT/'verification/sections/303-preparation/closeout-tools';require(not archive.exists(),'exclusive closeout source archive')
 copies={'close_section_303.py':path(HERE/'close_section_303.py').read_bytes(),'CONTRACT.md':path(HERE/'CONTRACT.md').read_bytes()}
 copies.update({'before-'+n:v for n,v in docs.items()})
 manifest={'kind':'SECTION303_PUBLIC_CLOSEOUT_TOOLS_NOT_PRIVATE_STATE',
  'files':{n:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}for n,raw in copies.items()},'private_contents_or_hash_lists_copied':False}
 print(json.dumps({'gates_passed':True,'apply_requested':args.apply,'necessary_actual_methods':test_ref['methods_run'],
  'native_actual_unique_checks':window['unique_checks'],'source_join':window_ref['source_join'],
  'functional_source_paths':len(feature_map),'maintenance_source_paths':len(MAINTENANCE),
  'validated_source_paths':len(validated_map),'planned_public_files':list(mutations),
  'PROJECT_PROGRESS_only_exact_scope_fragment':True,'full_rerun':False,'next_full_section':305,
  'numeric_endpoint':None,'cloud_published':False},ensure_ascii=False))
 if not args.apply:return
 for name,raw in docs.items():require(path(name).read_bytes()==raw,'public document stable before apply '+name)
 check_map(tests['source_sha256_after'],'prewrite necessary');check_map(window['source_sha256_after'],'prewrite native')
 public_local_bindings(tests)
 archive.mkdir(parents=True)
 for name,raw in copies.items():
  with(archive/name).open('xb')as stream:stream.write(raw)
 with(archive/'archive-manifest.json').open('xb')as stream:stream.write(encode(manifest))
 for name,raw in mutations.items():
  target=ROOT/name;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb'if name=='verification/sections/303.json'else'wb')as stream:stream.write(raw)
 print(json.dumps({'section':303,'local_closeout_written':True,'cloud_published':False,'next_section':304,'next_full_section':305}))

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 for name in ('necessary-receipt','window-receipt','window-process-receipt','native-source-sha256'):
  parser.add_argument('--'+name,required=True)
 parser.add_argument('--promotion-receipt',default='verification/sections/303-preparation/promotion.json')
 parser.add_argument('--preparation-archive-manifest',default='verification/sections/303-preparation/preparation-archive-manifest.json')
 parser.add_argument('--main-window-receipt',default='verification/sections/303-main-window.json')
 parser.add_argument('--focus-receipt',default='verification/sections/303-main-window-focus.json')
 parser.add_argument('--apply',action='store_true');main(parser.parse_args())
