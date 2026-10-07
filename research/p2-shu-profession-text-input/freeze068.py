from pathlib import Path
import subprocess,tarfile,io,json,hashlib,datetime
root=Path('/workspace/rougezhushou');base=Path(__file__).parent
head='0e0d098e8bc8444cd74fb74f32754cc0ff78ecfb'
observed_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
status=subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)
baseline=base/'baseline';baseline.mkdir()
archive=subprocess.check_output(['git','archive',head,'rouge'],cwd=root)
with tarfile.open(fileobj=io.BytesIO(archive)) as tar:tar.extractall(baseline,filter='data')
files={str(p.relative_to(baseline)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(baseline.rglob('*')) if p.is_file()}
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_commit':head,'observed_root_head':observed_head,
 'root_wip_paths_at_snapshot':status.splitlines(),'snapshot_includes_root_wip':False,'root_checkout_clean_at_snapshot':not status,
 'method':'git archive exact committed section63 rouge, independently of root checkout WIP','file_count':len(files),'files':files}
(base/'baseline-freeze068.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in receipt.items() if k!='files'})
