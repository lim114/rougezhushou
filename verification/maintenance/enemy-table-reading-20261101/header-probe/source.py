from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R));B=R/'verification/maintenance/enemy-table-reading-20261101/header-probe';B.mkdir(exist_ok=False)
from PySide6.QtWidgets import QApplication,QHeaderView
from PySide6.QtTest import QTest
from rouge.player_map_reader import make_reader
app=QApplication([]);d=make_reader('battle',{'id':'ro6_b_5','title':'公开固定资料'},None);d.show();d.panel.tabs.setCurrentIndex(1);t=d.panel.enemy_overview.tree;h=t.header()
for c,w in enumerate((150,80,75,70,70,125)):t.setColumnWidth(c,w)
h.setSectionResizeMode(6,QHeaderView.ResizeMode.Interactive);t.setColumnWidth(6,240);sizes=[]
for w in(760,920,1250):d.resize(w,720);QTest.qWait(40);sizes.append({'width':d.width(),'columns':[t.columnWidth(c)for c in range(7)],'horizontal_max':t.horizontalScrollBar().maximum()});assert d.grab().save(str(B/(str(w)+'.png')))
(B/'result.json').write_text(json.dumps(sizes,indent=2)+'\n','utf8');(B/'source.py').write_bytes(Path(__file__).read_bytes());print(sizes);d.close()
