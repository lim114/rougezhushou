"""Static file/schema preparation checks only, not closeout or publication execution."""
import ast
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CLOSE=ROOT/'.cache/p3-303-closeout';PUB=ROOT/'.cache/p3-303-publication-prep'
def pin(path):
 raw=path.read_bytes();return{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def constants(path):
 out={}
 for node in ast.parse(path.read_bytes()).body:
  if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
   try:out[node.targets[0].id]=ast.literal_eval(node.value)
   except(ValueError,TypeError):pass
 return out
paths=[CLOSE/'close_section_303.py',*[PUB/(name+'_303.py')for name in('stage_section','push_section','verify_publication','finish_publication')]]
for path in paths:
 raw=path.read_bytes();compile(raw,str(path),'exec')
 for forbidden in('ritual_weakening','named_reward','fixed_choice_count','partial_direct_reference_scope_unchanged','rouge/node_catalog_view.py'):
  if forbidden in raw.decode():raise ValueError('Previous functional scope leaked: '+str(path)+' '+forbidden)
cfg=constants(paths[0]);scope=json.loads((ROOT/'verification/sections/303-preparation/scope.json').read_bytes())
assert cfg['PARENT']==scope['parent_commit']=='c2b78e4aa4136fe739067b5ccf9d13b595142320'
assert cfg['DATA']=='rouge/data/fixed-landmark-references.json'
assignments={node.targets[0].id:node.value for node in ast.parse(paths[0].read_bytes()).body
 if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name)}
assert ast.dump(assignments['CHANGED_EXISTING'],include_attributes=False)==ast.dump(ast.Set(elts=[ast.Name(id='DATA',ctx=ast.Load())]),include_attributes=False)
assert cfg['MAINTENANCE']=={n:pin(ROOT/n)['sha256']for n in cfg['MAINTENANCE']}
assert cfg['MANIFEST_SHA']==pin(ROOT/'research/p3-map-direct-ground-303/source-manifest.json')['sha256']
assert cfg['DATA_SHA']==pin(ROOT/cfg['DATA'])['sha256']
assert cfg['COMPARISON_SHA']==pin(ROOT/'research/p3-map-direct-ground-303/build-receipt.json')['sha256']
for name in('stage_section','verify_publication'):
 assert(PUB/(name+'_303.py')).read_bytes()==(PUB/(name+'_303.py.txt')).read_bytes()
assert "index=text.index('## 功能第302节')"in(PUB/'verify_publication_303.py').read_text(encoding='utf8')
assert "index=text.index('## 功能第301节')"not in(PUB/'verify_publication_303.py').read_text(encoding='utf8')
native_path=ROOT/'.cache/p3-303-native-window/READY.json';native=json.loads(native_path.read_bytes())
assert native['canonical']==cfg['CANONICAL']and native['prior_commit']==cfg['PARENT']and len(native['necessary_modules'])==5
backend=ROOT/'.cache/p3-303-backend/HANDOFF.json'
static={'kind':'SECTION303_STATIC_TOOL_PREPARATION_ONLY_NOT_ACTUAL_ACCEPTANCE','at_utc':datetime.now(timezone.utc).isoformat(),
 'compiled_files':{str(p.relative_to(ROOT)).replace('\\','/'):pin(p)for p in paths},
 'source_schema_checks':'exact scope parent/data/manifest/comparison/maintenance pins and native five-module contract',
 'closeout_preview_apply_publication_producers_Qt_tests_Git_executed':False,
 'actual_necessary_methods':None,'actual_native_checks':None,'actual_native_assertions':None,
 'functional_commit':None,'publication_passed':None}
(CLOSE/'static-preparation.json').write_text(json.dumps(static,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
close={'section':303,'kind':'SECTION303_CLOSEOUT_READY_CACHE_PREPARATION_ONLY','parent_commit':cfg['PARENT'],
 'files':{name:pin(CLOSE/name)for name in('close_section_303.py','CONTRACT.md','static-preparation.json')},
 'backend_HANDOFF':{'path':str(backend.relative_to(ROOT)).replace('\\','/'),**pin(backend)},
 'native_READY':{'path':str(native_path.relative_to(ROOT)).replace('\\','/'),**pin(native_path)},
 'actual_counts':{'necessary_methods':None,'native_unique_checks':None,'native_assertions':None},
 'functional_and_maintenance_maps_separate':True,'source_counts_dynamic_from_actual_promotion':True,
 'actual_preview_required_before_apply':True,'ordinary_publication_still_required':True,
 'producer_or_Git_Qt_tests_live_private_operations':False,'next_section':304,'next_full_section':305,
 'old_full_is_historical_section':290,'numeric_endpoint':None}
(CLOSE/'READY.json').write_text(json.dumps(close,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
members=('stage_section_303.py','push_section_303.py','verify_publication_303.py','finish_publication_303.py',
 'stage_section_303.py.txt','verify_publication_303.py.txt','RUN_PLAN.md','BASELINE.json')
publication={'section':303,'kind':'SECTION303_PUBLICATION_READY_CACHE_PREPARATION_ONLY','parent_commit':cfg['PARENT'],
 'branch':'codex/p2-development','files':{name:pin(PUB/name)for name in members},
 'closeout_READY':{'path':'.cache/p3-303-closeout/READY.json',**pin(CLOSE/'READY.json')},
 'functional_commit':None,'metadata_commit':None,'publication_passed':None,
 'publication_tools_executed':False,'Qt_tests_Git_live_private_operations':False,
 'sole_existing_production_change':cfg['DATA'],'historical_test_maintenance_paths':sorted(cfg['MAINTENANCE']),
 'PROGRESS_change':'exact partial-scope parenthetical only; other todo bytes retained',
 'source_counts_dynamic_from_actual_promotion':True,'next_section':304,'last_full_section':290,
 'next_full_section':305,'numeric_endpoint':None,
 'nonstandard_raw_archive_allowlist':'actual section-bound archive exact paths+SHA only'}
(PUB/'READY.json').write_text(json.dumps(publication,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'closeout_READY':pin(CLOSE/'READY.json'),'helper':pin(CLOSE/'close_section_303.py'),
 'publication_READY':pin(PUB/'READY.json'),'publication_files':publication['files'],
 'producers_Git_Qt_tests_executed':False},ensure_ascii=False))
