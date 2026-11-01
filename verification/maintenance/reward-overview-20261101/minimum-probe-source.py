from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R));B=R/'verification/maintenance/reward-overview-20261101';(B/'initial-source').mkdir(exist_ok=False)
for name in ['rouge/current_reward_view.py','rouge/current_reward_reference.py','rouge/enemy_overview.py','rouge/wrapped_item_delegate.py','tests/test_reward_overview_review.py']:(B/'initial-source'/Path(name).name).write_bytes((R/name).read_bytes())
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from rouge.player_map_reader import make_reader
app=QApplication([]);d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料'},None);d.show();d.panel.tabs.setCurrentWidget(d.panel.rewards);d.resize(760,720);QTest.qWait(40);r=d.panel.rewards
def info(w):return {'actual':[w.width(),w.height()],'minimum_hint':[w.minimumSizeHint().width(),w.minimumSizeHint().height()],'minimum':[w.minimumWidth(),w.minimumHeight()]}
result={n:info(w)for n,w in [('dialog',d),('panel',d.panel),('reward',r),('fold_section',r.overview_section),('content',r.overview_section.content()),('tree',r.overview),('old_tabs',r.tabs)]};(B/'initial-minimum.json').write_text(json.dumps(result,indent=2)+'\n','utf8');(B/'minimum-probe-source.py').write_bytes(Path(__file__).read_bytes());print(result);d.close()
