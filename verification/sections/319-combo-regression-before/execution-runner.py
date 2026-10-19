from pathlib import Path
from hashlib import sha256
import json,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'verification/sections/319-combo-regression-before';out.mkdir()
names=['rouge/current_map_position.py','rouge/current_map_position_view.py','tests/test_current_map_position_view_319.py'];before={n:sha256((ROOT/n).read_bytes()).hexdigest()for n in names}
argv=[sys.executable,'-B','-X','utf8','-m','unittest','-v','tests.test_current_map_position_view_319.CurrentMapPositionView319Tests.test_real_grid_click_selects_observed_center_and_scales_on_original']
with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:p=subprocess.Popen(argv,cwd=ROOT,stdout=stdout,stderr=stderr,env=dict(os.environ,QT_QPA_PLATFORM='offscreen',PYTHONDONTWRITEBYTECODE='1'));code=p.wait()
after={n:sha256((ROOT/n).read_bytes()).hexdigest()for n in names};log=(out/'stderr.txt').read_text('utf8')
r={'section':319,'actual_exit':code,'retained_popen_pid':p.pid,'argv':argv,'expected_red_regression_observed':code==1 and'0 not greater than 0'in log,'passed_product':False,'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,'root_visual_discovery':'Mapped grid selection left the known-cell dropdown on placeholder'}
(out/'process.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');(out/'execution-runner.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'actual_exit':code,'red_regression':r['expected_red_regression_observed']}));assert r['expected_red_regression_observed']and before==after
