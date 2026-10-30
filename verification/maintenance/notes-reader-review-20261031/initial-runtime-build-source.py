from pathlib import Path
from hashlib import sha256
import json,sys
R=Path.cwd();sys.path.insert(0,str(R))
def pin(p):
 raw=(R/p).read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(p,v):
 path=R/p;assert not path.exists(),p;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def manifest(pack,schema,files):
 name=pack+'/runtime-manifest.json';write(name,{'schema':schema,'game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','files':{n:pin(n)for n in sorted(files)}});return pin(name)['sha256']
if sys.argv[1]=='directory':
 from rouge import current_event_directory as model
 old_manifest=json.loads((R/model.MANIFEST).read_bytes());old_notes=json.loads((R/model.NOTES).read_bytes());code={n:v for n,v in old_notes['original_sources'].items()if n.endswith('.py')}
 assert len(code)==24 and {n for n,v in old_manifest['files'].items()if pin(n)!=v}=={'rouge/expansion_reference.py','rouge/node_catalog.py'}
 notes=dict(old_notes);notes['schema']='current_event_directory_runtime_notes_v2';notes['original_sources']={n:v for n,v in old_notes['original_sources'].items()if n not in code}
 notes['historical_recipe_code_sources']=code;notes['historical_recipe_manifest']={'path':model.MANIFEST,**pin(model.MANIFEST)}
 notes['runtime_policy']='Runtime validates every cited data/document/manifest byte and event snapshot. Program-source provenance is historical build evidence, reviewed and tested with Git; unrelated program refactors do not invalidate unchanged public data.'
 pack='research/runtime-event-directory-20261031';write(pack+'/source-notes.json',notes)
 digest=manifest(pack,'current_event_directory_runtime_manifest_v2',{model.DATA,pack+'/source-notes.json',*notes['original_sources']})
 print(json.dumps({'pack':pack,'sha256':digest,'historical_code_sources':len(code),'runtime_files':len(notes['original_sources'])+2}))
else:
 from rouge import current_event_directory as directory,current_event_resources as resources,current_event_item_uses as uses,expansion_reference as version
 base=directory.packet();assert base is not None
 results={}
 for tag,model,field,schema in [('resources',resources,'directory_source_identity','current_event_resources_runtime_manifest_v2'),('item-uses',uses,'source_directory_identity','current_event_item_uses_runtime_manifest_v2')]:
  old=json.loads((R/model.DATA).read_bytes());new=model.derive(base)if tag=='resources'else model.derive(base,json.loads((R/version.PACK/'current-topic.json').read_bytes())['details'])
  assert {k:v for k,v in old.items()if k!=field}=={k:v for k,v in new.items()if k!=field}
  pack='research/runtime-event-'+tag+'-20261031';write(pack+'/data.json',new)
  write(pack+'/source-notes.json',{'schema':'current_event_derived_runtime_notes_v2','historical_recipe_manifest':{'path':model.MANIFEST,**pin(model.MANIFEST)},'historical_data':{'path':model.DATA,**pin(model.DATA)},'runtime_directory_manifest':{'path':directory.MANIFEST,**pin(directory.MANIFEST)},'changed_data_fields':[field],'all_other_data_identical':True,'row_count':len(new['rows']),'code_provenance_is_build_evidence_not_runtime_data_authority':True,'mechanism_change':False})
  files={pack+'/data.json',pack+'/source-notes.json',directory.DATA,directory.MANIFEST}
  if tag=='item-uses':files.add(version.PACK+'/current-topic.json')
  results[tag]={'pack':pack,'sha256':manifest(pack,schema,files),'rows':len(new['rows'])}
 print(json.dumps(results))
