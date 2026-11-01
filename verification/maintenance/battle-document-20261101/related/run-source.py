from pathlib import Path
from hashlib import sha256
import sys,subprocess,json,re
R=Path.cwd();B=R/'verification/maintenance/battle-document-20261101';out=B/'related';out.mkdir(exist_ok=False)
modules=['tests.test_battle_document_review', 'tests.test_interpret_lookup_review', 'tests.test_enemy_overview_review', 'tests.test_enemy_table_reading_review', 'tests.test_battle_overview_sections_review', 'tests.test_current_battle_view_314', 'tests.test_compact_battle_review', 'tests.test_spawn_reading_review', 'tests.test_page_ocr_seed_bridge', 'tests.test_page_ocr_056']
s=(R/'verification/maintenance/reward-overview-20261101/related/bootstrap.py').read_text('utf8');s=re.sub(r'modules=\[.*?\]',f'modules={modules!r}',s,count=1).replace('reward-overview-20261101/related','battle-document-20261101/related')
s=s.replace('forbidden=[]','forbidden=[]\nslot_errors=[]\ndef slot_error(kind,value,tb):\n import traceback\n slot_errors.append(str(value));traceback.print_exception(kind,value,tb)\nsys.excepthook=slot_error')
s=s.replace('assert not forbidden,forbidden','assert not forbidden,forbidden\n assert not slot_errors,slot_errors')
(out/'bootstrap.py').write_text(s,'utf8');paths=[p for root in ('rouge','tests')for p in(R/root).rglob('*')if p.suffix in('.py','.cjs')];sources={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()for p in paths};(out/'source-before.json').write_text(json.dumps(sources,indent=2)+'\n','utf8')
with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(out/'bootstrap.py')],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
same=all(sha256((R/p).read_bytes()).hexdigest()==h for p,h in sources.items());(out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code,'tested_source_unchanged':same},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());assert same
print(json.dumps({'actual_exit':code,'result':json.loads((out/'results.json').read_bytes())if(out/'results.json').exists()else None,'failure':(out/'stderr.txt').read_text('utf8')[-3000:]if code else None},ensure_ascii=False));raise SystemExit(code)
