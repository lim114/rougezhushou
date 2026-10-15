from pathlib import Path
from datetime import datetime, timezone
import json, subprocess, sys
root=Path(__file__).resolve().parents[1]
kind=sys.argv[1];assert kind in ('functional','metadata')
assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='codex/p2-development'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=root)
dest=root/f'.cache/section292-{kind}-push.json';assert not dest.exists()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
argv=['git','push','origin','HEAD:refs/heads/codex/p2-development']
actual=subprocess.run(argv,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
row={'section':292,'kind':kind,'commit':head,'argv':argv,'exit_code':actual.returncode,
 'stdout':actual.stdout.decode('utf8',errors='replace'),'stderr':actual.stderr.decode('utf8',errors='replace'),
 'at_utc':datetime.now(timezone.utc).isoformat(),'ordinary_push':True}
dest.write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'section':292,'kind':kind,'commit':head,'actual_push_exit':actual.returncode}))
raise SystemExit(actual.returncode)
