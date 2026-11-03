from pathlib import Path
import subprocess,tarfile,io,json,hashlib,datetime
root=Path('/workspace/rougezhushou');base=Path(__file__).parent
head='c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf'
observed_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
status=subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)
# Root began section61 after the first clean section60 observation; archive only exact committed60.
baseline=base/'baseline';baseline.mkdir()
archive=subprocess.check_output(['git','archive',head,'rouge'],cwd=root)
with tarfile.open(fileobj=io.BytesIO(archive)) as tar:tar.extractall(baseline,filter='data')
files={str(p.relative_to(baseline)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(baseline.rglob('*')) if p.is_file()}
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':head,'root_initial_clean_observation':True,'root_clean_at_snapshot':not status,'root_observed_head_at_snapshot':observed_head,'root_wip_paths_at_snapshot':status.splitlines(),'method':'git archive exact committed HEAD rouge, outside checkout','file_count':len(files),'files':files}
(base/'baseline-freeze064.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print({k:v for k,v in receipt.items() if k!='files'})
