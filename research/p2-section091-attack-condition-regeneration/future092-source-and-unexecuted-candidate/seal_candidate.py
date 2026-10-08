"""Metadata/copy seal only; no project execution and no actual91 claim."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
SOURCE=Path('/workspace/.continuation/p2-window-target-timing-candidate-source')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def put(name,obj):(HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


mfpath=SOURCE/'public-source-manifest.json';raw=mfpath.read_bytes()
assert sha(raw)=='fa7955a7b6114e4eb47ce2e87afc3c4f1451d832f102c1298fdb29fe40b1add1'
source_mf=json.loads(raw);assert source_mf['file_count']==33 and source_mf['total_bytes']==609755
provenance={}
for item in source_mf['files']:
    content=Path(item['source_path']).read_bytes()
    assert len(content)==item['bytes'] and sha(content)==item['sha256']
    dest=HERE/'source33'/item['archive_path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
    provenance[dest.relative_to(HERE).as_posix()]=item['source_path']
    assert dest.read_bytes()==content
(HERE/'source33/public-source-manifest.json').write_bytes(raw)
provenance['source33/public-source-manifest.json']=str(mfpath)
proof=json.loads((HERE/'candidate-static-proof.json').read_text())
for product in proof['products']:
    before=Path(product['source_path']).read_bytes();after=Path(product['candidate_path']).read_bytes()
    assert sha(before)==product['old_sha256'] and len(before)==product['old_bytes']
    assert sha(after)==product['new_sha256'] and len(after)==product['new_bytes']
patch=(HERE/'candidate-flow.patch').read_bytes();assert sha(patch)==proof['patch_sha256']
put('candidate-handoff.json',{
    'format_version':1,'status':'FINAL_REVIEWABLE_PROSPECTIVE_CANDIDATE_STOPWRITE_NOT_IMPLEMENTED_OR_COMPLETED_SECTION',
    'directory':str(HERE),'source33_manifest':{'path':str(mfpath),'sha256':sha(raw),'original33':33,'original_bytes':609755,'copies_same_bytes':True},
    'actual_source_commit':'2cbc45f03f99ed4f04b9c7e2612b58542f909168',
    'prospective91_product_base':'Published frozen91 UI app and Deepcolor reporting leaf hashes, not actual91root until root commits/transports',
    'base_binding':str(HERE/'prospective-base-binding.json'),
    'products':proof['products'],'patch':{'path':str(HERE/'candidate-flow.patch'),'bytes':len(patch),'sha256':sha(patch)},
    'manifest':str(HERE/'public-candidate-manifest.json'),'verification_contract':str(HERE/'verification-contract.json'),
    'new_runtime_or_project_calls':{'API':0,'helper':0,'formatter':0,'ctor':0,'tests':0,'Qt':0,'Wine':0},
    'new_tests_or_registry':None,'source_and_product_static_AST_byte_inverse':'PASS only, not runtime success',
    'source_preparation_failures':'Source33 preserves four distinct metadata/preparation diagnostics1failureeach, no product calls; candidate two source generations0fail, latter only exact effective-zero tooltip wording',
    'numeric_rule_scope':'No changes engine/damage/estimate/timing/prepare/guards; report gains effective existing window-length metric, average positive guard unchanged',
    'all91_changes_preserved_in_prospective_products':True,
    'unknowns':['ActualQt signal/API counts and initialization','Unplaced/specialsource quantities/native clocks','No universal duration clipping across specialmodes','Received/event remains reference_only'],
    'parent_dependency':'Root91 actualcommit/tag then actualbase transport and explicit stage/budget approval; before that0API/Qt/Wine/tests/tracked',
    'root_sole_tracked_mutations':True,'stopwrite':True})
files=[]
for path in sorted(HERE.rglob('*')):
    if path.is_file() and path.name!='public-candidate-manifest.json':
        raw=path.read_bytes();rel=path.relative_to(HERE).as_posix()
        files.append({'source_path':provenance.get(rel,str(path)),'archive_path':rel,'bytes':len(raw),'sha256':sha(raw)})
manifest={'format_version':1,'status':'FINAL_PROSPECTIVE_WORKFLOW_CANDIDATE_SOURCE_ONLY_NOT_COMPLETED_SECTION',
          'files':files,'file_count':len(files),'total_bytes':sum(x['bytes'] for x in files),
          'new_API_helper_formatter_ctor_tests_Qt_Wine':0,'tracked_changed':False,'manifest_itself_excluded':True,'stopwrite':True}
put('public-candidate-manifest.json',manifest)
for item in files:
    raw=(HERE/item['archive_path']).read_bytes();assert len(raw)==item['bytes'] and sha(raw)==item['sha256']
print(json.dumps({'status':'CANDIDATE_FINAL_STOPWRITE_NOT_COMPLETED_SECTION','files':len(files),'bytes':manifest['total_bytes'],
                  'manifest_sha256':sha((HERE/'public-candidate-manifest.json').read_bytes()),
                  'handoff_sha256':sha((HERE/'candidate-handoff.json').read_bytes()),
                  'patch_sha256':sha(patch),'new_calls':0}))
