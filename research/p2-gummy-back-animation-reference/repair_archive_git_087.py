import hashlib,json,shutil,subprocess
from pathlib import Path

root=Path('/workspace/rougezhushou');archive=root/'research/p2-gummy-back-animation-reference';base=Path('/workspace/.continuation')
def git(*args):return subprocess.check_output(['git',*args],cwd=root)
def sha(b):return hashlib.sha256(b).hexdigest()
assert git('rev-parse','HEAD').decode().strip()=='1ce970fd30aa3b42d8ef787cde02513f05682b66'
assert git('status','--porcelain')==b''
before=json.loads((base/'archive-git-closure-087-before.json').read_bytes());assert before['archive_index_files']==310 and len(before['missing_tracked_files'])==2
old_manifest=json.loads((archive/'archive-manifest.json').read_bytes())
for row in before['missing_tracked_files']:
 data=(root/row['path']).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256']
subprocess.run(['git','add','-f','--',*[r['path'] for r in before['missing_tracked_files']]],cwd=root,check=True)
def staged_blobs():
 result={}
 for chunk in git('ls-files','--stage','-z','--',str(archive.relative_to(root))).split(b'\0'):
  if not chunk:continue
  header,name=chunk.split(b'\t',1);result[name.decode()]=header.decode().split()[1]
 return result
staged=staged_blobs()
for name,row in old_manifest.items():
 p=archive/name;data=p.read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256']
 assert staged[str(p.relative_to(root))]==hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
maintained_unchanged=0
for chunk in git('ls-tree','-rz','HEAD','--','rouge','scripts','tests').split(b'\0'):
 if not chunk:continue
 header,name=chunk.split(b'\t',1);name=name.decode()
 if not name.endswith(('.py','.json')):continue
 data=(root/name).read_bytes();assert header.decode().split()[2]==hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),name;maintained_unchanged+=1
receipt={'passed':True,'section':87,'supplement_ref':'p2-archive-closure-087','original_commit':'1ce970fd30aa3b42d8ef787cde02513f05682b66','original_archive_index_entries':310,'original_git_exact_entries':308,'two_ignored_public_files':before['missing_tracked_files'],'ignore_rule':'build/ in root .gitignore','original_310_entries_now_staged_git_blob_exact':True,'all_worktree_archive_hashes_correct':True,'maintained_py_json_unchanged':maintained_unchanged,'new_section_count':0,'tests_API_parser_download_Qt_Wine_calls':0,'sealed_original301_manifest_unchanged':True,'future_archive_helper':'Explicitly stage each public archive-index path and verify its Git blob before commit.'}
verification=root/'verification/archive-closure-087.json';assert not verification.exists();verification.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
for src,name in ((base/'archive-git-closure-087-before.json','archive-git-closure-087-before.json'),(base/'finish_section-before-git-closure.py','finish_section-before-git-closure.py'),(base/'finish_section.py','finish_section-with-git-closure.py'),(Path(__file__),Path(__file__).name)):
 assert not (archive/name).exists();shutil.copyfile(src,archive/name)
cp_path=root/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(cp_path.read_bytes());assert cp['completed_sections']==87 and cp['next_section']==88
cp.setdefault('archive_supplements',[]).append({'after_section':87,'ref':'p2-archive-closure-087','verification':'verification/archive-closure-087.json'})
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
section_path=root/'verification/sections/087.json';section=json.loads(section_path.read_bytes());section['archive_git_closure_supplement']='verification/archive-closure-087.json';section['archive_git_closure_ref']='p2-archive-closure-087';section_path.write_text(json.dumps(section,ensure_ascii=False,indent=2)+'\n')
def edit(name,fn):
 p=root/name;b=p.read_bytes();text=b.decode().replace('\r\n','\n');result=fn(text);p.write_bytes(result.replace('\n','\r\n').encode() if b'\r\n' in b else result.encode())
note='第87节归档Git闭合补证：工作树310索引件均hash正确，其中官方spine-core.js与spine-core.d.ts被build/忽略，原提交仅308件；两公开原件已明确补入并验证310全部Git blob。原301源清单不改，725维护py/json字节不变，不计新节、不重已通过测试或解析。后续存档对每个公开索引路径显式stage并核Git blob。见verification/archive-closure-087.json、标签p2-archive-closure-087。'
assert maintained_unchanged==725
edit('WORK_IN_PROGRESS.md',lambda old:'# 第87节归档恢复补证\n\n'+note+'\n\n---\n\n'+old)
edit('PROJECT_COMPLETED.md',lambda old:'# 第87节公开归档闭合\n\n'+note+'\n\n---\n\n'+old)
edit('BATCH_CONTINUOUS_P2.md',lambda old:old+'\n## 第87节归档补证（不计新节）\n\n'+note+'\n')
manifest={str(p.relative_to(archive)):{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(archive.rglob('*')) if p.is_file() and p.name!='archive-manifest.json'}
(archive/'archive-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
paths=[str(archive/name) for name in manifest]+[str(archive/'archive-manifest.json')]
subprocess.run(['git','add','-f','--',*paths],cwd=root,check=True)
staged=staged_blobs()
for path in paths:
 p=Path(path);data=p.read_bytes();assert staged[str(p.relative_to(root))]==hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
subprocess.run(['git','add','--','DEVELOPMENT_CHECKPOINT.json','WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md','BATCH_CONTINUOUS_P2.md','verification/sections/087.json','verification/archive-closure-087.json'],cwd=root,check=True)
subprocess.run(['git','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check'],cwd=root,check=True)
subprocess.run(['git','commit','--quiet','-m','补齐第87节被忽略的公开解析器原件并核对归档Git闭合'],cwd=root,check=True)
subprocess.run(['git','tag','p2-archive-closure-087'],cwd=root,check=True)
committed={}
for chunk in git('ls-tree','-rz','HEAD','--',str(archive.relative_to(root))).split(b'\0'):
 if not chunk:continue
 header,name=chunk.split(b'\t',1);committed[name.decode()]=header.decode().split()[2]
for path in paths:
 p=Path(path);assert committed[str(p.relative_to(root))]==staged[str(p.relative_to(root))]
assert git('status','--porcelain')==b''
print(json.dumps({'passed':True,'head':git('rev-parse','HEAD').decode().strip(),'supplement_ref':'p2-archive-closure-087','original_archive_entries_git_exact':310,'current_archive_files_git_exact':len(paths),'maintained_source_bytes_unchanged':725,'next_section':88}))
