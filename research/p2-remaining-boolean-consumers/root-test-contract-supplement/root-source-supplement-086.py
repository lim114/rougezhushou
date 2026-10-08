import ast,hashlib,json,subprocess
from pathlib import Path

repo=Path('/workspace/rougezhushou');packet=Path('/workspace/.continuation/p2-remaining-boolean-consumers-086-draft');sup=Path('/workspace/.continuation/p2-section086-root-test-contract-supplement')
def sha(b):return hashlib.sha256(b).hexdigest()
base=json.loads((packet/'current-baseline-freeze.json').read_bytes());review=json.loads((packet/'review-freeze86.json').read_bytes())
for row in review['files']:
 data=(repo/row['path']).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256'];ast.parse(data.decode())
adapted='tests/test_orchid_near_text_input.py';old=(sup/'test_orchid_near_text_input-original085.py').read_bytes();new=(sup/'test_orchid_near_text_input-adapted086.py').read_bytes()
assert subprocess.check_output(['git','show',base['base_commit']+':'+adapted],cwd=repo)==old
assert sha(new)=='62c74f4f094442e689e60d5e6306fbdd6cec357173ff7a295bb5c47cf93af901'
assert (repo/adapted).read_bytes()==new and b'\r\n' not in new
replacement="        # Section86 rejects text at this actual S1 consumer; S2/S3 stay ignored.\n        with self.assertRaisesRegex(ValueError,'^double_charge 不接受文本条件；请使用布尔值。$'):\n            record({**args,'double_charge':'false'})\n".encode()
assert new.count(replacement)==1
assert new.replace(replacement,b"        self.assertEqual(record({**args,'double_charge':'false'}),default)\n")==old
excluded={r['path'] for r in review['files']}|{adapted,'scripts/verify_cloud.py'};unchanged=0
for row in base['files']:
 if row['path'] in excluded:continue
 data=(repo/row['path']).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256'];unchanged+=1
assert unchanged==719
registry=(repo/'scripts/verify_cloud.py').read_bytes();old_registry=subprocess.check_output(['git','show',base['base_commit']+':scripts/verify_cloud.py'],cwd=repo)
assert registry==old_registry.replace(b'MODULES = (\n',b'MODULES = (\n    "tests.test_remaining_boolean_condition_text_input",\n')
prior=json.loads(Path('/workspace/.continuation/root-source-086.json').read_bytes());assert prior['passed'] and prior['other_base_source_files_exact']==720
receipt={'passed':True,'section':86,'base_commit':base['base_commit'],'post_migration_other_old_sources_exact':719,'old_test_exact_inverse_to_base':True,'old_test_changed_assertions':1,'approved_products_and_new8_tests_unchanged':True,'registry_exact_single_insertion':True,'pre_migration_source_receipt_720_preserved':True,'source_receipt_720_scope':'Before adapting the historical S1 double_charge string expectation only.','new_API_calls':0,'new_project_helper_calls':0,'native_windows':False}
with (sup/'root-source-post-migration-086.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt))
