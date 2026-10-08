import hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
s=json.loads(Path(sys.argv[1]).read_text());n=s['number'];p=Path(s['verification']['research_archive']);assert p.is_dir()
assert n==91
rpath=Path('/workspace/.continuation/root-related-091.log');rraw=rpath.read_bytes()
availability=json.loads(Path(s['related_receipt']).read_bytes())
assert availability['available_checks_passed'] is True
original=availability['original_runner'];available=availability['available']
assert hashlib.sha256(rraw).hexdigest()==original['sha256']
assert original['tests_run']==56 and original['passed']==54 and original['errors']==2 and original['failures']==0 and original['exit_code']==1
assert rraw.decode().rstrip().endswith('FAILED (errors=2)')
assert availability['unavailable_count']==2 and len(availability['unavailable'])==2
assert available=={'run':54,'passed':54,'skipped':0,'failures':0,'errors':0}
run=available['run']
selected=json.loads(Path(f'/workspace/.continuation/root-selected-{n:03d}.log').read_text().strip().splitlines()[-1]);assert selected['passed'] and selected['failures']==0 and selected['errors']==0
s['verification']['checks']=[{'command':s['related_scope'],**available,'original_runner_tests_run':56,'original_runner_exit_code':1,'original_runner_errors':2,'unavailable':2,'complete_related_validation':False,'receipt':s['related_receipt']},{'command':'.venv/bin/python scripts/verify_cloud.py','run':selected['tests_run'],'passed':selected['tests_run']-selected['skipped'],'skipped':selected['skipped'],'failures':0,'errors':0}]
for label in ['related','selected','source']:
 ext='json' if label=='source' else 'log';src=Path(f'/workspace/.continuation/root-{label}-{n:03d}.{ext}');assert src.exists();shutil.copyfile(src,p/src.name)
script=Path(s.get('root_source_script','/workspace/.continuation/root-current-source.py'));destination=p/script.name
if script.resolve()!=destination.resolve():shutil.copyfile(script,destination)
else:assert destination.is_file()
(p/'archive-manifest.json').write_text(json.dumps({str(f.relative_to(p)):{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in sorted(p.rglob('*')) if f.is_file() and f.name!='archive-manifest.json'},indent=2)+'\n')
Path(sys.argv[1]).write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['.venv/bin/python','/workspace/.continuation/record_section.py',sys.argv[1]],check=True)
subprocess.run(['git','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--check'],check=True)
paths=s['changed_paths']+['DEVELOPMENT_CHECKPOINT.json','WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md','BATCH_CONTINUOUS_P2.md',f'verification/sections/{n:03d}.json',str(p)]
subprocess.run(['git','add',*paths],check=True)
archive_rows=json.loads((p/'archive-manifest.json').read_text())
archive_paths=[str(p/name) for name in archive_rows]+[str(p/'archive-manifest.json')]
subprocess.run(['git','add','-f','--',*archive_paths],check=True)
staged={}
for chunk in subprocess.check_output(['git','ls-files','--stage','-z','--',str(p)]).split(b'\0'):
 if not chunk:continue
 header,name=chunk.split(b'\t',1);staged[name.decode()]=header.decode().split()[1]
for path in archive_paths:
 data=Path(path).read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 assert staged[path]==blob,path
subprocess.run(['git','commit','--quiet','-m',s['commit_message']],check=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
for path in archive_paths:
 data=Path(path).read_bytes();assert subprocess.check_output(['git','show',f'{head}:{path}'])==data,path
for path in s['changed_paths']:
 assert subprocess.check_output(['git','show',f'{head}:{path}'])==Path(path).read_bytes(),path
subprocess.run(['git','tag',f'p2-section-{n:03d}'],check=True)
print(json.dumps({'section':n,'related':run,'selected':selected,'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()},ensure_ascii=False))
