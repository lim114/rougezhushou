import hashlib,json,shutil,subprocess
from pathlib import Path,PurePosixPath

repo=Path('/workspace/rougezhushou')
packet=Path('/workspace/.continuation/p2-remaining-boolean-consumers-086-draft')
archive=repo/'research/p2-remaining-boolean-consumers'
assert subprocess.check_output(['git','status','--porcelain'],cwd=repo)==b''
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo).decode().strip()=='9ef5a469673502754db3be320a8eece9a7fd18d4'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
mf=packet/'archivable-public-manifest-final86.json'
handoff=packet/'handoff-final86.json'
assert digest(mf)=='4a2ca8dc22ddd13b0319bdb12544102b680d7a87722366806c9de728e12a7b58'
assert digest(handoff)=='73ba1f24c6c024c6df1c838e6ce499ed08bb92a639a80206c51a613db87e4f0c'
rows=json.loads(mf.read_bytes())['files'];assert len(rows)==130
names=set();total=0
for row in rows:
 name=PurePosixPath(row['archive_path'])
 assert not name.is_absolute() and '..' not in name.parts and str(name) not in names
 names.add(str(name));src=Path(row['source_path']);data=src.read_bytes()
 assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],str(src)
 total+=len(data)
assert total==7910349
patch=packet/'section86.patch'
assert digest(patch)=='4834ec66e47ebdf8df0e8ef0c57e19dafe1693d80f51e9061245879c33005f87'
assert not archive.exists()
subprocess.run(['git','apply','--check',str(patch)],cwd=repo,check=True)
subprocess.run(['git','apply',str(patch)],cwd=repo,check=True)
registry=repo/'scripts/verify_cloud.py';old=registry.read_bytes()
assert old.count(b'MODULES = (\n')==1 and b'tests.test_remaining_boolean_condition_text_input' not in old
registry.write_bytes(old.replace(b'MODULES = (\n',b'MODULES = (\n    "tests.test_remaining_boolean_condition_text_input",\n'))
for row in json.loads(handoff.read_bytes())['approved_files']:
 dest=repo/row['path'];assert len(dest.read_bytes())==row['bytes'] and digest(dest)==row['sha256']
archive.mkdir()
for row in rows:
 dest=archive/row['archive_path'];dest.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(row['source_path'],dest)
 assert len(dest.read_bytes())==row['bytes'] and digest(dest)==row['sha256']
for src in (mf,handoff):
 assert src.name not in names
 shutil.copyfile(src,archive/src.name)
receipt={'passed':True,'section':86,'base_commit':'9ef5a469673502754db3be320a8eece9a7fd18d4','sealed_packet_files':130,'sealed_packet_bytes':total,'manifest_sha256':digest(mf),'handoff_sha256':digest(handoff),'products_hash_verified':True,'registry_only_new_module':True,'root_fresh_tests_pending':True}
with (archive/'root-integration-086.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
shutil.copyfile(__file__,archive/Path(__file__).name)
print(json.dumps(receipt))
