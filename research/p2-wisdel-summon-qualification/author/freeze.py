import hashlib,json,pathlib,subprocess
root=pathlib.Path('/workspace/rougezhushou'); dest=pathlib.Path(__file__).resolve().parent
head='552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9'
paths=subprocess.check_output(['git','-C',str(root),'ls-tree','-r','--name-only',head],text=True).splitlines()
public=[p for p in paths if (p.startswith('rouge/') and pathlib.PurePosixPath(p).suffix in ('.py','.json')) or (p.startswith('tests/') and p.endswith('.py'))]
assert public and all('/state' not in p and '.cache' not in p for p in public)
hashes={}
for rel in public:
 b=subprocess.check_output(['git','-C',str(root),'show',head+':'+rel]); hashes[rel]=hashlib.sha256(b).hexdigest()
 for name in ('frozen70','draft'):
  p=dest/name/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
doc_paths=['PROJECT_PROGRESS.md','research/p2-wisdel-secondary/RESEARCH.md','research/p2-wisdel-ghost-clock/RESEARCH.md','research/p2-module-qualification-notes/NOTES.md']
docs={}
for rel in doc_paths:
 b=subprocess.check_output(['git','-C',str(root),'show',head+':'+rel]);p=dest/'baseline-notes'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);docs[rel]=hashlib.sha256(b).hexdigest()
receipt={'baseline_head':head,'commit_subject':subprocess.check_output(['git','-C',str(root),'show','-s','--format=%s',head],text=True).strip(),'public_source_hashes':hashes,'baseline_note_hashes':docs,'public_package_and_test_files':len(public),'private_state_copied':False,'source':'immutable git blobs only; no root working tree copied'}
(dest/'freeze70.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'baseline':head,'public_files':len(public),'package_files':sum(p.startswith('rouge/') for p in public),'freeze_sha256':hashlib.sha256((dest/'freeze70.json').read_bytes()).hexdigest()}))
