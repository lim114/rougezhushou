"""Append the designated independent FINAL packet; never rerun frozen work."""
from pathlib import Path
import argparse,hashlib,json

parser=argparse.ArgumentParser()
parser.add_argument('--independent-manifest',type=Path,required=True)
parser.add_argument('--expected-independent-manifest-sha',required=True)
parser.add_argument('--independent-final',type=Path,required=True)
parser.add_argument('--expected-independent-final-sha',required=True)
args=parser.parse_args()
OUT=Path(__file__).resolve().parent
sha=lambda d:hashlib.sha256(d).hexdigest()
def row(path,archive):
    data=path.read_bytes()
    return {'source_path':str(path.resolve()),'archive_path':archive,'bytes':len(data),'sha256':sha(data)}
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def verify(r):
    data=Path(r['source_path']).read_bytes()
    assert (len(data),sha(data))==(r['bytes'],r['sha256']),r['source_path']
author_path=OUT/'author-review-public-manifest088.json'
author=json.loads(author_path.read_text())
assert sha(author_path.read_bytes())=='4772c026843a995921c6013fb435fd547e2cb5a67d8f4f6e73245b7e5dbcc445'
assert len(author['files'])==89 and author['total_bytes']==1871550
for r in author['files']:verify(r)
indpath=args.independent_manifest.resolve();finalpath=args.independent_final.resolve()
assert sha(indpath.read_bytes())==args.expected_independent_manifest_sha
assert sha(finalpath.read_bytes())==args.expected_independent_final_sha
ind=json.loads(indpath.read_text());final=json.loads(finalpath.read_text())
status=final['status']
assert status.startswith('PASS') and all(word not in status for word in ('DRAFT','PREP','STATIC'))
for r in ind['files']:verify(r)
assert any(Path(r['source_path']).resolve()==finalpath for r in ind['files'])
save('handoff-final88.json',{'status':'AUTHOR_FINAL_AFTER_DESIGNATED_FORMAL_INDEPENDENT_PASS',
    'independent_status':status,'independent_final_sha256':args.expected_independent_final_sha,
    'independent_manifest_sha256':args.expected_independent_manifest_sha,
    'author_review_manifest_sha256':sha(author_path.read_bytes()),
    'author_review_freeze_sha256':'10e5e8bcbc3e6a8a74e838d5ddd12638a3574230385a876a0c6d03a7c98baf99',
    'patch_sha256':'6cad7ce79a0458e494cb975d3670b404c98f004227f97bb975e87b14fffd9627',
    'registry_proposal_sha256':'4543ae4bce8519b203cefd12ccaa5fb1fb14505923464753c788d347c90832fc',
    'baseline_revision':'1ce970fd30aa3b42d8ef787cde02513f05682b66',
    'approved_prior_revision':'6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0',
    'author_60_unique_pairs_public_calls':120,'author_text_rejections':23,'author_whole_same':32,'author_exact_old_errors':5,
    'author_new_test_public_entries':19,'author_new_test_explicit_context_helper_requests':32,
    'root_current_source_checker_executed_by_author':False,
    'public_event_SP_examples_reference_only':True,'tail_ready_wait_contract_scope':'Scoped internal helper units, not publicly reactivated retired event mechanics.',
    'new_project_calls_during_final_seal':0,'author_frozen_89_files_unchanged':True,
    'source16_or_matrix_or_passed_tests_repeated_during_final_seal':False,
    'root_responsibility':'Sole apply/registry/current-source proof/fresh related-selected/commit/full090.'})
files=list(author['files'])
files.append(row(author_path,author_path.name))
known={Path(r['source_path']).resolve() for r in files}
for path in sorted(OUT.iterdir()):
    if path.is_file() and path.resolve() not in known and path.name!='archivable-public-manifest-final88.json':
        files.append(row(path,path.name));known.add(path.resolve())
for r in ind['files']:
    files.append({**r,'archive_path':'independent-review/'+r['archive_path']})
files.append(row(indpath,'independent-review/'+indpath.name))
assert len({r['archive_path'] for r in files})==len(files)
save('archivable-public-manifest-final88.json',{'format_version':1,'status':'FINAL_STABLE_AUTHOR_AND_INDEPENDENT_PUBLIC_PACKET',
    'files':files,'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files),'manifest_self_excluded':True,
    'private_execution_trees_excluded':'Fixed remaining baseline/draft125py-json tree has Gitblob/bytes/hash receipts; not duplicated research/cache.'})
for r in files:verify(r)
print(json.dumps({'final_handoff_sha256':sha((OUT/'handoff-final88.json').read_bytes()),
    'final_manifest_sha256':sha((OUT/'archivable-public-manifest-final88.json').read_bytes()),
    'files':len(files),'bytes':sum(r['bytes'] for r in files),'new_project_calls':0}))
