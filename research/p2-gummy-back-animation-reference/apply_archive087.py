import hashlib,json,shutil,subprocess
from pathlib import Path,PurePosixPath

repo=Path('/workspace/rougezhushou');packet=Path('/workspace/.continuation/p2-gummy-back-animation-reference-087-draft');out=repo/'research/p2-gummy-back-animation-reference'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','status','--porcelain'],cwd=repo)==b''
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo).decode().strip()=='0f27027e7e1f49c08f298706b599e310e299238b'
mf=packet/'final-public-artifacts-manifest087.json';hand=packet/'final-handoff087.json'
assert sha(mf)=='4f5cabcc1169346c19782ed8b6a84b748ed746e7de9cf6becad83d5d7e37f0e7'
assert sha(hand)=='96fba297a135f3222dd128ead63589feecb3ffd52f4662e30d73f1c2a53ae845'
rows=json.loads(mf.read_bytes())['files'];assert len(rows)==301 and sum(r['bytes'] for r in rows)==7389271
seen=set()
for row in rows:
 name=PurePosixPath(row['archive_path']);assert not name.is_absolute() and '..' not in name.parts and str(name) not in seen;seen.add(str(name))
 p=Path(row['source_path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],str(p)
approved=json.loads(hand.read_bytes())
for row in approved['source_files']:
 p=repo/row['path']
 if row['baseline_bytes'] is None:assert not p.exists()
 else:assert p.stat().st_size==row['baseline_bytes'] and sha(p)==row['baseline_sha256']
patch=packet/'product087.patch';assert sha(patch)=='05d4f78b2bc319b0d87bb80f4d32366e27565d26c5b459800a773d7e7362cb93'
registry=repo/'scripts/verify_cloud.py';regold=registry.read_bytes();regnew=(packet/'registered-verify_cloud087.py').read_bytes()
literal=b'    "tests.test_gummy_back_animation_reference",\n';assert regnew.count(literal)==1 and regnew.replace(literal,b'',1)==regold and sha(packet/'registered-verify_cloud087.py')=='b2da5be3e6d309d97a01746161e63fa450f62ff5f9abb9c26fbfcd7abb91b3e8'
progress=repo/'PROJECT_PROGRESS.md';old=progress.read_bytes();needle='古米背面解析及'.encode();assert old.count(needle)==1 and b'\r\n' in old
assert not out.exists()
subprocess.run(['git','apply','--check',str(patch)],cwd=repo,check=True)
subprocess.run(['git','apply',str(patch)],cwd=repo,check=True)
registry.write_bytes(regnew)
progress.write_bytes(old.replace(needle,'古米前后面实际动作绑定及'.encode()))
for row in approved['source_files']:
 p=repo/row['path'];assert p.stat().st_size==row['draft_bytes'] and sha(p)==row['draft_sha256']
 data=p.read_bytes()
 if row['line_endings']=='CRLF':assert b'\r\n' in data and b'\n' not in data.replace(b'\r\n',b'')
 else:assert b'\r\n' not in data
out.mkdir()
for row in rows:
 p=out/row['archive_path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['source_path'],p);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
for p in (mf,hand):
 if p.name in seen:assert sha(out/p.name)==sha(p)
 else:shutil.copyfile(p,out/p.name)
receipt={'passed':True,'section':87,'base_commit':'0f27027e7e1f49c08f298706b599e310e299238b','sealed_packet_files':301,'sealed_packet_bytes':7389271,'all_source_and_archive_hash_bytes_verified':True,'approved3targets_and_registry_verified':True,'old923_inverse_pending_root_checker':True,'progress_only_removes_completed_Back_metadata_parse_gap':True,'root_fresh_tests_pending':True,'new_source_parse_downloads':0}
with (out/'root-integration087.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
shutil.copyfile(__file__,out/Path(__file__).name);shutil.copyfile('/workspace/.continuation/root-related-087.py',out/'root-related-087.py')
print(json.dumps(receipt))
