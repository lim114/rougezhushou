import hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
s=json.loads(Path(sys.argv[1]).read_text());n=s['number'];p=Path(s['verification']['research_archive']);assert p.is_dir()
r=Path(f'/workspace/.continuation/root-related-{n:03d}.log').read_text();declared_skips=s.get('related_declared_skips',0);expected_end=f'OK (skipped={declared_skips})' if declared_skips else 'OK';assert r.rstrip().endswith(expected_end);run=int(re.search(r'Ran (\d+) tests',r).group(1));assert run>declared_skips
selected=json.loads(Path(f'/workspace/.continuation/root-selected-{n:03d}.log').read_text().strip().splitlines()[-1]);assert selected['passed'] and selected['failures']==0 and selected['errors']==0
s['verification']['checks']=[{'command':s.get('related_scope','related current checkout regression'),'run':run,'passed':run-declared_skips,'skipped':declared_skips,'failures':0,'errors':0},{'command':'.venv/bin/python scripts/verify_cloud.py','run':selected['tests_run'],'passed':selected['tests_run']-selected['skipped'],'skipped':selected['skipped'],'failures':0,'errors':0}]
for label in ['related','selected','source']:
 ext='json' if label=='source' else 'log';src=Path(f'/workspace/.continuation/root-{label}-{n:03d}.{ext}');assert src.exists();shutil.copyfile(src,p/src.name)
script=Path(s.get('root_source_script','/workspace/.continuation/root-current-source.py'));shutil.copyfile(script,p/script.name)
(p/'archive-manifest.json').write_text(json.dumps({str(f.relative_to(p)):{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in sorted(p.rglob('*')) if f.is_file() and f.name!='archive-manifest.json'},indent=2)+'\n')
Path(sys.argv[1]).write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['.venv/bin/python','/workspace/.continuation/record_section.py',sys.argv[1]],check=True)
subprocess.run(['git','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--check'],check=True)
paths=s['changed_paths']+['DEVELOPMENT_CHECKPOINT.json','WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md','BATCH_CONTINUOUS_P2.md',f'verification/sections/{n:03d}.json',str(p)]
subprocess.run(['git','add',*paths],check=True)
logs=[str(f) for f in p.rglob('*.log')]
if logs:subprocess.run(['git','add','-f',*logs],check=True)
subprocess.run(['git','commit','--quiet','-m',s['commit_message']],check=True);subprocess.run(['git','tag',f'p2-section-{n:03d}'],check=True)
print(json.dumps({'section':n,'related':run,'selected':selected,'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()},ensure_ascii=False))
