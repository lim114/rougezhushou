from pathlib import Path
import subprocess,sys,json
R=Path.cwd();out=R/'verification/maintenance/grade16-review-20261031'
with(out/'profile-audit-closure-stdout.txt').open('xb')as stdout,(out/'profile-audit-closure-stderr.txt').open('xb')as stderr:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(R/'.cache/audit_grade16_profiles.py')],cwd=R,stdout=stdout,stderr=stderr);code=child.wait()
(out/'profile-audit-closure-process.json').write_text(json.dumps({'actual_retained_Popen_pid':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8')
print((out/'profile-audit-closure-stdout.txt').read_text('utf8'));print((out/'profile-audit-closure-stderr.txt').read_text('utf8')[-1800:]);raise SystemExit(code)
