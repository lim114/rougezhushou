from pathlib import Path
import subprocess,sys,json
R=Path.cwd();rows=[]
for threads,cvthreads,tag in((2,18,'baseline'),(4,18,'ort4'),(2,1,'cv1'),(4,1,'ort4cv1')):
 out=R/'.cache/ocr-runtime-trials';out.mkdir(exist_ok=True)
 with(out/(tag+'-stdout.txt')).open('xb')as stdout,(out/(tag+'-stderr.txt')).open('xb')as stderr:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(R/'.cache/trial_ocr_runtime.py'),str(threads),str(cvthreads),tag],cwd=R,stdout=stdout,stderr=stderr);code=child.wait()
 row={'tag':tag,'retained_Popen_pid':child.pid,'actual_exit':code};rows.append(row);(out/'processes.json').write_text(json.dumps(rows,indent=2)+'\n','utf8')
 assert code==0,(out/(tag+'-stderr.txt')).read_text('utf8')
 print(json.dumps({'finished':tag,'actual_exit':code}),flush=True)
