from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R))
from PySide6.QtWidgets import QApplication,QWidget
from rouge.player_map_reader import make_reader
app=QApplication([]);owner=QWidget();d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开资料'},owner);d.show();p=d.panel;rows=[]
for tab in range(4):
 p.tabs.setCurrentIndex(tab);app.processEvents()
 if tab==3:p.rewards.sections.setCurrentWidget(p.settlement);app.processEvents()
 targets=[p.overview_scroll,p.enemy_scroll,p.wave_scroll,p.rewards,p.settlement][tab:tab+1]if tab<3 else[p.rewards,p.settlement]
 for widget in targets:
  rows.append({'tab':tab,'type':type(widget).__name__,'size':[widget.width(),widget.height()],'minimum_hint':[widget.minimumSizeHint().width(),widget.minimumSizeHint().height()],'bottom_in_dialog':widget.mapTo(d,widget.rect().bottomRight()).y(),'dialog_height':d.height()})
out=R/'verification/maintenance/compact-battle-window-20261101/reach-probe.json';out.write_text(json.dumps(rows,indent=2)+'\n','utf8');print(json.dumps(rows));d.close()
