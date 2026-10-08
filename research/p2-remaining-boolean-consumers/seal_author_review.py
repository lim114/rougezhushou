"""Explicit stable author packet; later independent final is a separate seal."""
import gzip,hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent


def sha(data):return hashlib.sha256(data).hexdigest()
def save(name,value):
 with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
 freeze=json.loads((OUT/'review-freeze86.json').read_bytes())
 assert freeze['status']=='FROZEN_FOR_FORMAL_REVIEW'
 assert sha((OUT/'section86.patch').read_bytes())==freeze['patch_sha256']
 for row in freeze['files']:
  data=Path(row['source_path']).read_bytes();assert sha(data)==row['sha256'] and len(data)==row['bytes']
 compressed=[]
 for package in ('baseline','draft'):
  for kind in ('matrix','isolated-cores'):
   summary=json.loads((OUT/(package+'-'+kind+'-summary.json')).read_bytes())
   path=OUT/(package+'-'+kind+('.jsonl.gz' if kind=='matrix' else '.json.gz'))
   data=path.read_bytes();decoded=gzip.decompress(data)
   assert sha(data)==summary['gzip_sha256'] and len(data)==summary['gzip_bytes']
   assert sha(decoded)==summary['decoded_sha256'] and len(decoded)==summary['decoded_bytes']
   compressed.append({'path':path.name,'gzip_sha256':sha(data),'gzip_bytes':len(data),
      'decoded_sha256':sha(decoded),'decoded_bytes':len(decoded),'lossless_verified':True})
 save('compressed-saved-results-proof.json',{'passed':True,'files':compressed,'new_API_calls':0,'new_project_helper_calls':0})
 save('author-review-handoff.json',{'status':'AUTHOR_FINAL_STABLE_PENDING_INDEPENDENT_PRODUCT_REVIEW',
    **{k:freeze[k] for k in ('base_commit','patch_sha256','patch_bytes','files','matrix_pairs','matrix_public_calls',
       'matrix_counts','isolated_core_pairs','explicit_prepare_helper_calls','explicit_core_helper_calls','matrix_formatters',
       'isolated_core_formatters','unittest_counts','unittest_API_call_counts','catalog_cache_reads_for_isolation')},
    'review_freeze_sha256':sha((OUT/'review-freeze86.json').read_bytes()),'registered_module_proposal':'tests.test_remaining_boolean_condition_text_input',
    'source_files_28_plus_independent_source_17_included_exact':True,'source_original_call_counts_not_relabelled_current':True,
    'source240_skill12_module_audits_not_rerun':True,'proofs':['current-source-and-scope-check.json',
       'current-test-evidence-binding.json','saved-matrix-comparison-attempt-1.json','isolated-core-saved-comparison.json',
       'compressed-saved-results-proof.json','NOTE.md'],
    'Qt':0,'Wine':0,'tracked_edits':0,'new_native_mechanism':False,
    'root_fresh_checks_not_yet_run':True,'independent_review_pending':True,
    'source_36_original_probes':'preserved original b5 source packets, not counted as current 9ef calls',
    'stop_product_changes':'Product/test/patch frozen; independent final attachments will be added in a separate final manifest.'})
 names=['prepare_draft.py','current-baseline-freeze.json','draft-product-receipt.json','run_related.py',
    'baseline-related.log','draft-related.log','new-test-attempt-1.py','test-expectation-diagnostic-attempt-1.json',
    'new-targeted-corrected.log','matrix_plan.py','run_matrix.py','baseline-matrix.jsonl.gz','draft-matrix.jsonl.gz',
    'baseline-matrix-summary.json','draft-matrix-summary.json','compare_saved_matrix.py','saved-matrix-comparison-attempt-1.json',
    'check_isolated_cores.py','baseline-isolated-cores.json.gz','draft-isolated-cores.json.gz',
    'baseline-isolated-cores-summary.json','draft-isolated-cores-summary.json','freeze_for_review.py',
    'isolated-core-saved-comparison.json','current-test-evidence-binding.json','current-source-and-scope-check.json',
    'section86.patch','review-freeze86.json','NOTE.md','seal_author_review.py','compressed-saved-results-proof.json','author-review-handoff.json',
    'baseline/rouge/operator_engine.py','baseline/rouge/damage.py','draft/rouge/operator_engine.py',
    'draft/rouge/damage.py','draft/tests/test_remaining_boolean_condition_text_input.py']
 rows=[]
 def add(path,archive):
  data=path.read_bytes();rows.append({'source_path':str(path),'archive_path':archive,'bytes':len(data),'sha256':sha(data)})
 for name in names:add(OUT/name,name)
 bindings=[]
 for prefix,path,expected in (
   ('source-preparation',Path('/workspace/.continuation/p2-remaining-boolean-consumers-086-source/archivable-public-manifest.json'),'43fb5c6cfd2806cca065c734bbc0e30e20dc2a447ff0a2ade5d45baa71647de8'),
   ('source-independent',Path('/workspace/.continuation/independent-source086/public-artifacts-manifest-independent086.json'),'d72869af176ec745bfa9b4aee8e352b8fb791970ba8014960cf91d5949b48296')):
  assert sha(path.read_bytes())==expected
  manifest=json.loads(path.read_bytes())
  for row in manifest['files']:
   source=Path(row['source_path']);data=source.read_bytes();assert sha(data)==row['sha256'] and len(data)==row['bytes']
   add(source,prefix+'/'+row['archive_path'])
  add(path,prefix+'/'+path.name);bindings.append({'manifest_path':str(path),'sha256':expected,'original_files':len(manifest['files'])})
 assert len(rows)==84 and len({r['archive_path'] for r in rows})==len(rows)
 save('archivable-author-review-manifest.json',{'format_version':1,'status':'AUTHOR_FINAL_STABLE_PENDING_INDEPENDENT_PRODUCT_REVIEW',
   'files':rows,'count':len(rows),'bytes':sum(r['bytes'] for r in rows),'source_packet_bindings':bindings,
   'excludes':['reconstructable baseline/draft complete trees','__pycache__','private state'],
   'root_apply_blocked_until_independent_final':True})
 print(json.dumps({'passed':True,'files':len(rows),'bytes':sum(r['bytes'] for r in rows),
     'handoff_sha256':sha((OUT/'author-review-handoff.json').read_bytes()),
     'manifest_sha256':sha((OUT/'archivable-author-review-manifest.json').read_bytes())}))


if __name__=='__main__':main()
