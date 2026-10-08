"""Combine immutable author/source/independent evidence without new calls."""
import ast,hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
IND=Path('/workspace/.continuation/p2-remaining-boolean-consumers-086-independent')
AUTHOR_SHA='8e0d6a7607246573d16a97320a8cf71bf1db6e18765304b4f09916b99281443f'
IND_SHA='3bf6435a474535c745cc5db99a84374ed3c8d4c981ca68a62d57b3488f98ca34'
IND_FINAL_SHA='c194f245eea2558d8bed79183e934c1af5cea7d8ff38eeaa19b692df88384d84'


def sha(data):return hashlib.sha256(data).hexdigest()
def save(name,value):
 with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
 author_path=OUT/'archivable-author-review-manifest.json'
 ind_path=IND/'independent-public-manifest086.json'
 assert sha(author_path.read_bytes())==AUTHOR_SHA and sha(ind_path.read_bytes())==IND_SHA
 author=json.loads(author_path.read_bytes());ind=json.loads(ind_path.read_bytes())
 assert len(author['files'])==84 and len(ind['files'])==39
 formal_path=IND/'independent-review-final086.json'
 assert sha(formal_path.read_bytes())==IND_FINAL_SHA
 formal=json.loads(formal_path.read_bytes())
 assert formal['status']=='PASS_FINAL_FROZEN'
 assert formal['author_review_manifest_sha256']==AUTHOR_SHA
 reviewed=json.loads((OUT/'review-freeze86.json').read_bytes())
 assert formal['approved_patch_sha256']==reviewed['patch_sha256']
 assert formal['approved_product_and_test_files']==reviewed['files']
 assert formal['new_tests']['methods']==8 and all(formal['new_tests'][k]==0 for k in ('failures','errors','skips'))
 for row in author['files']+ind['files']:
  data=Path(row['source_path']).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256']
 ledger=json.loads((OUT/'formatting-ledger-scope086.json').read_bytes())
 assert ledger['matrix']['explicit_three_text_requests_total']==1299
 assert ledger['isolated_private_cores']['explicit_three_text_requests_total']==42
 ast.parse((OUT/'root-current-source-086.py').read_text())
 save('root-source-script-preflight.json',{'passed':True,'scope':'static syntax/dependency availability only',
   'root_current_source_script':'root-current-source-086.py',
   'same_directory_dependencies':['current-baseline-freeze.json','review-freeze86.json'],
   'post_integration_source_script_run':False,'new_API_calls':0,'new_project_helper_calls':0,
   'root_registration_required':'tests.test_remaining_boolean_condition_text_input'})
 save('handoff-final86.json',{'status':'FINAL_STABLE_REVIEWED_READY_FOR_ROOT_INTEGRATION','section':86,
   'base_commit':reviewed['base_commit'],'branch':'codex/p2-development','patch_sha256':reviewed['patch_sha256'],
   'approved_files':reviewed['files'],'root_registry_module':'tests.test_remaining_boolean_condition_text_input',
   'author_review_manifest_sha256':AUTHOR_SHA,'author_review_manifest_files':84,
   'review_freeze_sha256':sha((OUT/'review-freeze86.json').read_bytes()),
   'independent_final_sha256':IND_FINAL_SHA,'independent_manifest_sha256':IND_SHA,'independent_files':39,
   'source28_plus_indsource17_and_original_manifests_exact_included':True,
   'author_public_matrix':{'pairs':268,'current_public_calls':536,'qualified_text_rejected':71,
      'whole_accepted_typed_JSON_three_texts_same':181,'exact_old_errors':16,'explicit_three_text_requests':1299},
   'author_isolated_internal_cores':{'pairs':8,'explicit_prepare_calls':8,'explicit_core_calls':16,
      'public_calls':0,'qualified_text_rejected':2,'whole_accepted_typed_three_texts_same':6,
      'prepared_before_after_same_to_old':True,'explicit_three_text_requests':42,
      'scope':'Internal core phase argument compatibility only, not public nondeployment phase envelope or native clock.'},
   'independent_fresh_risk_pairs':formal['fresh_independent'],
   'author_tests':'114 old baseline pass;114 old draft pass. Initial8new7pass1wrong-S1-expectation preserved;corrected1targetpass and7unchanged AST binding. No repeat of passed114/7.',
   'independent_new_tests':formal['new_tests'],
   'unittest_API_totals_and_internal_formatter_entries_not_instrumented':True,
   'combined_grand_total_not_claimed':True,'formatting_ledger_scope':'formatting-ledger-scope086.json',
   'ranged_signal':'Fresh Combat object in extended branch; reset at calculate entry; same actual qualified skill override and actual normal call; no user scenario/public marker.',
   'normal_eligibility_evidence':'S1 unbound duration/recharge None before normal;S2switch no cycle;S3actualnormal depends cycle/continuous. Matrix263 finalcycle150 butnormalNone; no saved S3normalactive-finalcycleNone claim.',
   'old_error_limit':'Actual source order and measured old paths only; no universal outer-error assertion.',
   'original_source36_240ranks_12module_audits_not_repeated':True,
   'new_native_multipliers_clocks_probabilities_or_attachment':False,
   'product_CRLF_and_test_LF':True,'root_current_source_script':'root-current-source-086.py',
   'root_source_script_dependencies':['current-baseline-freeze.json','review-freeze86.json'],
   'root_checks_pending':['apply reviewed surgical patch','register new selected module',
      'strict current source check','fresh related/new tests','fresh selected regression','archive/commit/checkpoint'],
   'root_full_next_due':90,'root_sole_tracked_integration_commit':True,'tracked_edits':0,'Qt':0,'Wine':0,
   'stop':'All final artifacts immutable; root may integrate without further author calls.'})
 rows=[]
 def add(path,archive):
  data=path.read_bytes();rows.append({'source_path':str(path),'archive_path':archive,'bytes':len(data),'sha256':sha(data)})
 for row in author['files']:rows.append(dict(row))
 add(author_path,author_path.name)
 for row in ind['files']:add(Path(row['source_path']),'independent-product/'+row['archive_path'])
 add(ind_path,'independent-product/'+ind_path.name)
 for name in ('formatting-ledger-scope086.json','root-current-source-086.py','root-source-script-preflight.json','seal_final.py','handoff-final86.json'):
  add(OUT/name,name)
 assert len(rows)==130 and len({r['archive_path'] for r in rows})==len(rows)
 save('archivable-public-manifest-final86.json',{'format_version':1,'status':'FINAL_STABLE_REVIEWED',
   'files':rows,'count':len(rows),'bytes':sum(r['bytes'] for r in rows),
   'author84_unchanged':True,'independent39_plus_own_manifest_exact':True,
   'includes_original_source28_independent17_and_their_manifest_files':True,
   'excludes':['complete reconstructable baseline/draft trees','__pycache__','private state'],
   'source_paths_explicit_and_all_verified_before_seal':True,'root_sole_integration':True})
 print(json.dumps({'passed':True,'files':len(rows),'bytes':sum(r['bytes'] for r in rows),
   'handoff_sha256':sha((OUT/'handoff-final86.json').read_bytes()),
   'manifest_sha256':sha((OUT/'archivable-public-manifest-final86.json').read_bytes()),
   'patch_sha256':reviewed['patch_sha256'],'new_API_calls':0}))


if __name__=='__main__':main()
