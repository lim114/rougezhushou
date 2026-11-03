import hashlib,json,shutil
from pathlib import Path

repo=Path('/workspace/rougezhushou');packet=Path('/workspace/.continuation/p2-remaining-boolean-consumers-086-draft');archive=repo/'research/p2-remaining-boolean-consumers'
mf=packet/'archivable-public-manifest-final86.json';hand=packet/'handoff-final86.json'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(mf)=='4a2ca8dc22ddd13b0319bdb12544102b680d7a87722366806c9de728e12a7b58'
assert digest(hand)=='73ba1f24c6c024c6df1c838e6ce499ed08bb92a639a80206c51a613db87e4f0c'
rows=json.loads(mf.read_bytes())['files'];assert len(rows)==130
for row in rows:
 for p in (Path(row['source_path']),archive/row['archive_path']):
  assert len(p.read_bytes())==row['bytes'] and digest(p)==row['sha256'],str(p)
assert digest(archive/mf.name)==digest(mf)
for row in json.loads(hand.read_bytes())['approved_files']:
 p=repo/row['path'];assert len(p.read_bytes())==row['bytes'] and digest(p)==row['sha256']
assert (repo/'scripts/verify_cloud.py').read_bytes().count(b'"tests.test_remaining_boolean_condition_text_input",')==1
for src,name in ((Path('/workspace/.continuation/apply_archive086.py'),'apply_archive086-attempt1.py'),(Path('/workspace/.continuation/root-integration-preparation-failure086.json'),'root-integration-preparation-failure086.json'),(Path(__file__),Path(__file__).name)):
 assert not (archive/name).exists();shutil.copyfile(src,archive/name)
receipt={'passed':True,'section':86,'sealed_packet_files':130,'sealed_packet_bytes':sum(r['bytes'] for r in rows),'manifest_sha256':digest(mf),'handoff_sha256':digest(hand),'all_source_and_archive_bytes_verified':True,'products_hash_verified':True,'registry_only_new_module':True,'root_archive_preparation_failure_count':1,'failure_scope':'extra-copy duplicate handoff assertion, not product failure; original attempt retained','root_fresh_tests_pending':True}
with (archive/'root-integration-086.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt))
