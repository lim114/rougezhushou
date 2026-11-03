from pathlib import Path
import subprocess,tarfile,io,hashlib,json,datetime
root=Path('/workspace/rougezhushou');base=Path(__file__).parent
commit='59531ff2e9475410a84ef0e60836f89793fd35a9'
paths=['rouge','scripts/build_run_config.py','scripts/build_technology_reference.py',
       'research/p2-technology','research/p2-enemy-rune-selectors','research/p2-run-eligibility',
       'research/p2-aglna-manual-weight','PROJECT_PROGRESS.md']
status=subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).splitlines()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
snapshot=base/'baseline';snapshot.mkdir(exist_ok=True)
data=subprocess.check_output(['git','archive',commit,*paths],cwd=root)
with tarfile.open(fileobj=io.BytesIO(data)) as archive:archive.extractall(snapshot,filter='data')
files={str(p.relative_to(snapshot)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
       for p in sorted(snapshot.rglob('*')) if p.is_file()}
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_commit':commit,
     'observed_root_head':head,'root_wip_paths_at_snapshot':status,'snapshot_includes_root_wip':False,
     'root_checkout_clean_at_snapshot':not status,'method':'git archive explicit committed public paths; no working-tree files',
     'archive_paths':paths,'file_count':len(files),'files':files}
(base/'baseline-freeze.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print({k:v for k,v in out.items() if k!='files'})
