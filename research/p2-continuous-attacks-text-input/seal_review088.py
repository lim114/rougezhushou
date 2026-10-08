"""One source/product/test/matrix review freeze, zero project calls."""
from pathlib import Path
import ast,hashlib,json,subprocess
OUT=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
PRIOR='6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0'
def sha(data):return hashlib.sha256(data).hexdigest()
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def row(path,archive):
    data=path.read_bytes()
    return {'source_path':str(path),'archive_path':archive,'bytes':len(data),'sha256':sha(data)}
index=json.loads((OUT/'fixed-source-index088.json').read_text())
proof=[]
for r in index['files']:
    fixed=subprocess.check_output(['git','show',PRIOR+':'+r['path']],cwd=REPO)
    assert (len(fixed),sha(fixed))==(r['bytes'],r['sha256'])
    assert (REPO/r['path']).read_bytes()==fixed
    proof.append({'path':r['path'],'bytes':len(fixed),'sha256':sha(fixed)})
ast.parse((OUT/'root-current-source-088.py').read_text())
check=subprocess.run(['git','apply','--check',str(OUT/'section88.patch')],cwd=REPO,capture_output=True,text=True)
assert check.returncode==0
save('recovered-prior-source088.json',{'status':'PASS_STATIC_RECOVERY_SAME_PRODUCT_BYTES','prior_revision':PRIOR,
    'baseline_revision':index['baseline_commit'],'files':proof,'file_count':len(proof),'root_current_source_checker_executed':False,
    'root_current_source_checker_AST_parsed':True,'readonly_patch_apply_check':{'returncode':check.returncode,'stdout':check.stdout,'stderr':check.stderr},
    'new_project_calls':0,'tracked_mutations':0})
transport=json.loads((OUT/'patch-and-source-after088.json').read_text())
comparison=json.loads((OUT/'saved-comparison088.json').read_text())
binding=json.loads((OUT/'final-test-binding088.json').read_text())
assert comparison['status']=='PASS_STRICT_SAVED_FULL_COMPARISON' and binding['status']=='PASS_FINAL_EIGHT_METHODS_BOUND'
assert sha((OUT/'test_continuous_attacks_text_input.py').read_bytes())==binding['final_test_sha256']
save('review-freeze088.json',{'status':'EXPLICIT_SOURCE_PRODUCT_TEST_MATRIX_FROZEN_FOR_FORMAL_REVIEW',
    'baseline_revision':index['baseline_commit'],'recovered_prior_revision':PRIOR,
    'patch_sha256':transport['patch_sha256'],'product_and_test_files':transport['product_and_test_files'],
    'matrix_plan_sha256':sha((OUT/'matrix-plan088.json').read_bytes()),
    'baseline_saved_sha256':sha((OUT/'baseline-public60.jsonl.gz').read_bytes()),
    'draft_saved_sha256':sha((OUT/'draft-public60.jsonl.gz').read_bytes()),
    'comparison_sha256':sha((OUT/'saved-comparison088.json').read_bytes()),
    'actual_public_matrix_calls':120,'unique_pairs':60,'text_rejections':23,'whole_same':32,'exact_old_errors':5,
    'new_tests_final_binding_sha256':sha((OUT/'final-test-binding088.json').read_bytes()),
    'new_tests_actual_public_entries':19,'new_tests_explicit_context_helper_requests':32,
    'old_success_tests_repeated':0,'source16_repeated':0,'Qt':0,'Wine':0,'tracked_mutations':0,
    'root_current_source_checker_executed':False})
save('author-review-handoff088.json',{'status':'READY_FOR_FORMAL_INDEPENDENT_REVIEW_ONLY',
    'freeze_sha256':sha((OUT/'review-freeze088.json').read_bytes()),'patch_sha256':transport['patch_sha256'],
    'source_manifest_sha256':'8ec63ee21862e89abe8ead88175c39268a515fded8a865bc39a18d1c68aea645',
    'matrix_calls':120,'new_test_public_entries':19,'new_test_explicit_context_helper_requests':32,
    'saved_comparison_new_calls':0,'independent_work':'Recompare all60 saved zeroAPI; independent root-authorized different risks/new8 as needed; no author matrix rerun.',
    'evidence_boundary':'Read EVIDENCE_BOUNDARY.md; current event-SP public examples are reference-only, tail qualification verified in scoped helper unit test.',
    'root_current_source_checker':'Provided but NOT executed by author; pure source check after root applies.',
    'source_product_test_matrix_mutations_after_freeze':0})
files=[]
for p in sorted(OUT.iterdir()):
    if p.is_file() and p.name!='author-review-public-manifest088.json':files.append(row(p,p.name))
for name in list(transport['product_and_test_files']):
    if name.startswith('tests/'):continue
    p=OUT/'draft'/name;files.append(row(p,'product/'+name))
    if (OUT/'baseline'/name).exists():files.append(row(OUT/'baseline'/name,'baseline-source/'+name))
source=Path('/workspace/.continuation/p2-section088-candidate-audit/public-artifacts-manifest-source088.json')
for r in json.loads(source.read_text())['files']:
    p=Path(r['source_path']);actual=row(p,'source-candidate/'+r['archive_path'])
    assert actual['sha256']==r['sha256'] and actual['bytes']==r['bytes'];files.append(actual)
files.append(row(source,'source-candidate/'+source.name))
assert len({r['archive_path'] for r in files})==len(files)
save('author-review-public-manifest088.json',{'format_version':1,'status':'FINAL_STABLE_AUTHOR_REVIEW_PACKET',
    'files':files,'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files),'manifest_self_excluded':True,
    'execution_tree_scope':'Remaining baseline/draft execution tree py/json are excluded from duplicated public archive; every one is pinned by real Git blob/bytes/hash index and static current87 proof, no research/cache copies.'})
for r in files:
    actual=row(Path(r['source_path']),r['archive_path']);assert actual==r
print(json.dumps({'freeze_sha256':sha((OUT/'review-freeze088.json').read_bytes()),
    'handoff_sha256':sha((OUT/'author-review-handoff088.json').read_bytes()),
    'manifest_sha256':sha((OUT/'author-review-public-manifest088.json').read_bytes()),
    'files':len(files),'bytes':sum(r['bytes'] for r in files),'patch_sha256':transport['patch_sha256']}))
