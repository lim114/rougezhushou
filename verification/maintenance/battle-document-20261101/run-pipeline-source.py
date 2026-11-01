from pathlib import Path
import sys,subprocess,json
from hashlib import sha256
R=Path.cwd();out=R/'verification/maintenance/battle-document-20261101';files=['rouge/recognition.py','rouge/page_ocr.py','rouge/dynamic_ocr.py','rouge/recognition_cache.py'];before={p:sha256((R/p).read_bytes()).hexdigest()for p in files}
with(out/'pipeline-stdout.txt').open('xb')as a,(out/'pipeline-stderr.txt').open('xb')as b:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(R/'.cache/benchmark_battle_document_pipeline.py')],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
same=all(sha256((R/p).read_bytes()).hexdigest()==h for p,h in before.items());(out/'pipeline-process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code,'source_unchanged':same,'source_sha256':before},indent=2)+'\n','utf8');(out/'pipeline-source.py').write_bytes((R/'.cache/benchmark_battle_document_pipeline.py').read_bytes());(out/'run-pipeline-source.py').write_bytes(Path(__file__).read_bytes());assert same;print({'actual_exit':code},flush=True);raise SystemExit(code)
