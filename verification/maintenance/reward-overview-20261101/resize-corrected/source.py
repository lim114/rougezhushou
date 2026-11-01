from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R));B=R/'verification/maintenance/reward-overview-20261101';out=B/'resize-corrected';out.mkdir(exist_ok=False)
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from rouge.player_map_reader import make_reader
app=QApplication([]);d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料'},None);d.show();r=d.panel.rewards;d.panel.tabs.setCurrentWidget(r);QTest.qWait(50);data=[]
for width,height in[(640,650),(760,720),(920,720),(1250,720),(640,650),(920,720)]:
 d.resize(width,height);QTest.qWait(60);v={'requested':[width,height],'actual':[d.width(),d.height()],'dialog_minimum':[d.minimumWidth(),d.minimumHeight()],'dialog_hint':[d.minimumSizeHint().width(),d.minimumSizeHint().height()],'reward_hint':[r.minimumSizeHint().width(),r.minimumSizeHint().height()],'fold':[r.overview_section.height(),r.overview_section.minimumSizeHint().height(),r.overview_section.content().maximumHeight()],'tree':[r.overview.width(),r.overview.height()]};data.append(v);path=out/(str(len(data))+'.png');assert d.grab().save(str(path))
(out/'result.json').write_text(json.dumps(data,indent=2)+'\n','utf8');(out/'source.py').write_bytes(Path(__file__).read_bytes());print(data);d.close()
