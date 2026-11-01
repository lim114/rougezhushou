from pathlib import Path
import re,subprocess,sys,json
R=Path.cwd();B=R/'verification/maintenance/enemy-table-reading-20261101';out=B/'related';out.mkdir(exist_ok=False)
s=(R/'verification/maintenance/battle-overview-sections-20261101/related/bootstrap.py').read_text('utf8');modules=['tests.test_enemy_table_reading_review','tests.test_enemy_overview_review','tests.test_current_enemy_forecast_review','tests.test_battle_overview_sections_review','tests.test_current_battle_view_314','tests.test_compact_battle_review'];s=re.sub(r'modules=\[.*?\]',f'modules={modules!r}',s,count=1).replace('battle-overview-sections-20261101/related','enemy-table-reading-20261101/related');(out/'bootstrap.py').write_text(s,'utf8')
with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(out/'bootstrap.py')],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
(out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'exit':code,'result':json.loads((out/'results.json').read_bytes())if(out/'results.json').exists()else None,'failure':(out/'stderr.txt').read_text('utf8')[-3000:]if code else None},ensure_ascii=False));raise SystemExit(code)
