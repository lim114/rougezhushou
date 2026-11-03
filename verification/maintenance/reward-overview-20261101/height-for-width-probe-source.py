from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R));B=R/'verification/maintenance/reward-overview-20261101'
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from rouge.player_map_reader import make_reader
app=QApplication([]);d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料'},None);d.show();r=d.panel.rewards;d.panel.tabs.setCurrentWidget(r);QTest.qWait(100);data={}
for name,w in [('dialog',d),('panel',d.panel),('main_tabs',d.panel.tabs),('reward',r),('reward_sections',r.sections),('reward_body',r.sections.widget(0)),('fold',r.overview_section),('fold_content',r.overview_section.content()),('old_tabs',r.tabs)]:
 item={'widget_hasHFW':w.hasHeightForWidth(),'size_hint':[w.sizeHint().width(),w.sizeHint().height()],'minimum_hint':[w.minimumSizeHint().width(),w.minimumSizeHint().height()],'heightForWidth':[w.heightForWidth(v)for v in(600,760,920)]}
 if w.layout()is not None:item['layout']={'hasHFW':w.layout().hasHeightForWidth(),'minimumHFW':[w.layout().minimumHeightForWidth(v)for v in(600,760,920)],'HFW':[w.layout().heightForWidth(v)for v in(600,760,920)]}
 data[name]=item
(B/'height-for-width-probe.json').write_text(json.dumps(data,indent=2)+'\n','utf8');(B/'height-for-width-probe-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(data));d.close()
