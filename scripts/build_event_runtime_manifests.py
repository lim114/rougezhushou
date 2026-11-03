"""Reproduce public runtime data from retained recipes; no private state or downloads."""
from pathlib import Path
from hashlib import sha256
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
def pin(p):
 raw=(R/p).read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(p,v):
 path=R/p;raw=(json.dumps(v,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode('utf8')
 if path.exists():assert path.read_bytes()==raw,'Existing runtime snapshot differs; do not overwrite: '+p
 else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
def manifest(pack,schema,files):
 name=pack+'/runtime-manifest.json';write(name,{'schema':schema,'game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','files':{n:pin(n)for n in sorted(files)}});return pin(name)['sha256']
if sys.argv[1]=='directory':
 from rouge import current_event_directory as model
 original='research/p3-current-event-directory-372';old_manifest_name=original+'/runtime-manifest.json';old_manifest=json.loads((R/old_manifest_name).read_bytes());old_notes=json.loads((R/original/'source-notes.json').read_bytes());code={n:v for n,v in old_notes['original_sources'].items()if n.endswith('.py')}
 assert len(code)==24
 assert all(pin(n)==v for n,v in old_manifest['files'].items()if not n.endswith('.py'))
 notes=dict(old_notes);notes['schema']='current_event_directory_runtime_notes_v2';notes['original_sources']={n:v for n,v in old_notes['original_sources'].items()if n not in code}
 notes['historical_recipe_code_sources']=code;notes['historical_recipe_manifest']={'path':old_manifest_name,**pin(old_manifest_name)}
 notes['runtime_policy']='Runtime validates every cited data/document/manifest byte and event snapshot. Program-source provenance is historical build evidence, reviewed and tested with Git; unrelated program refactors do not invalidate unchanged public data.'
 pack='research/runtime-event-directory-20261031';write(pack+'/source-notes.json',notes)
 digest=manifest(pack,'current_event_directory_runtime_manifest_v2',{model.DATA,pack+'/source-notes.json',*notes['original_sources']})
 print(json.dumps({'pack':pack,'sha256':digest,'historical_code_sources':len(code),'runtime_files':len(notes['original_sources'])+2}))
elif sys.argv[1]=='derived':
 from rouge import current_event_directory as directory,current_event_resources as resources,current_event_item_uses as uses,expansion_reference as version
 base=directory.packet();assert base is not None
 results={}
 for tag,model,field,schema in [('resources',resources,'directory_source_identity','current_event_resources_runtime_manifest_v2'),('item-uses',uses,'source_directory_identity','current_event_item_uses_runtime_manifest_v2')]:
  old_data='rouge/data/current-event-resources.json'if tag=='resources'else'rouge/data/current-event-item-uses.json';old_manifest_name='research/p3-current-event-resources-374/runtime-manifest.json'if tag=='resources'else'research/p3-current-event-item-uses-376/runtime-manifest.json'
  old=json.loads((R/old_data).read_bytes());new=model.derive(base)if tag=='resources'else model.derive(base,json.loads((R/version.PACK/'current-topic.json').read_bytes())['details'])
  assert {k:v for k,v in old.items()if k!=field}=={k:v for k,v in new.items()if k!=field}
  pack='research/runtime-event-'+tag+'-20261031';write(pack+'/data.json',new)
  write(pack+'/source-notes.json',{'schema':'current_event_derived_runtime_notes_v2','historical_recipe_manifest':{'path':old_manifest_name,**pin(old_manifest_name)},'historical_data':{'path':old_data,**pin(old_data)},'runtime_directory_manifest':{'path':directory.MANIFEST,**pin(directory.MANIFEST)},'changed_data_fields':[field],'all_other_data_identical':True,'row_count':len(new['rows']),'code_provenance_is_build_evidence_not_runtime_data_authority':True,'mechanism_change':False})
  files={pack+'/data.json',pack+'/source-notes.json',directory.DATA,directory.MANIFEST}
  if tag=='item-uses':files.add(version.PACK+'/current-topic.json')
  results[tag]={'pack':pack,'sha256':manifest(pack,schema,files),'rows':len(new['rows'])}
 print(json.dumps(results))

else:raise SystemExit("Choose directory or derived; snapshots are checked or created, never overwritten.")
