from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R))
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtTest import QTest
from rouge.current_battle_view import CurrentBattleDialog
from rouge.player_map_reader import make_reader
app=QApplication([]);owner=QWidget();rows=[]
for kind in('factory','direct'):
 d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开资料'},owner)if kind=='factory'else CurrentBattleDialog('ro6_n_2_6',owner);d.show();QTest.qWait(100);app.processEvents();p=d.panel
 rows.append({'kind':kind,'default':[d.width(),d.height()],'hint':[d.minimumSizeHint().width(),d.minimumSizeHint().height()]})
 for w,h in((640,360),(800,340),(920,720),(800,340)):
  d.resize(w,h)
  for i in range(4):p.tabs.setCurrentIndex(i);QTest.qWait(80);app.processEvents();rows.append({'kind':kind,'requested':[w,h],'actual':[d.width(),d.height()],'tab':i,'body':[p.reading_stack.width(),p.reading_stack.height()]})
 d.close();app.processEvents()
out=R/'verification/maintenance/compact-battle-window-20261101/geometry-probe.json';out.write_text(json.dumps(rows,indent=2)+'\n','utf8');print(json.dumps(rows))
