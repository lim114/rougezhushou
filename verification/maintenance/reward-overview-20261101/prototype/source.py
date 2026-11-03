from pathlib import Path
from hashlib import sha256
from types import ModuleType
from unittest.mock import patch
import sys,json,subprocess
R=Path.cwd();sys.path.insert(0,str(R));B=R/'verification/maintenance/reward-overview-20261101';D=R/'research/reward-overview-20261101'
if len(sys.argv)==1:
 out=B/'prototype';out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'source.py').write_bytes(Path(__file__).read_bytes());print({'exit':code});raise SystemExit(code)
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from rouge import current_reward_view as view
from rouge.player_map_reader import make_reader
app=QApplication([]);assert app.platformName()=='windows';out=B/'prototype';prior=ModuleType('rouge._before_reward_overview');prior.__package__='rouge';exec(compile((D/'before-current_reward_view.py').read_bytes(),'<exact-own-baseline-reward-view>','exec'),prior.__dict__)
with patch.object(view,'CurrentRewardPanel',prior.CurrentRewardPanel):
 d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料'},None);d.show();d.panel.tabs.setCurrentWidget(d.panel.rewards);QTest.qWait(50);assert d.grab().save(str(out/'before.png'));d.close()
d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料'},None);d.show();p=d.panel;r=p.rewards;p.tabs.setCurrentWidget(r);QTest.qWait(40);images=[]
for width in(760,920,1250):
 d.resize(width,720);QTest.qWait(50);path=out/f'overview-{width}.png';assert d.grab().save(str(path));images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest(),'section_height':r.overview_section.height(),'tree_height':r.overview.height(),'plain_height':r.player.height(),'window_width':d.width()})
QTest.mouseClick(r.overview.viewport(),Qt.MouseButton.LeftButton,pos=r.overview.visualItemRect(r.overview.topLevelItem(0).child(0)).center());QTest.qWait(40);assert not r.overview_section.isExpanded()and r.row_id is not None and r.player.isVisible();assert d.grab().save(str(out/'selected-detail.png'))
data={'images':images,'actual_Qt_windows':True,'public_fixed_reward_source_rows':len(r.result['rows']),'selected_exact_row':r.row_id,'actual_click_opens_full_existing_reader':True,'no_game_chat_or_private_state':True};(out/'result.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(data,ensure_ascii=False));d.close()
