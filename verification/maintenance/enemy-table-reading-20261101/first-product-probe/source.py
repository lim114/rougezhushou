from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R));B=R/'verification/maintenance/enemy-table-reading-20261101/first-product-probe';B.mkdir(exist_ok=False)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QHeaderView
from PySide6.QtTest import QTest
from rouge.player_map_reader import make_reader
app=QApplication([]);d=make_reader('battle',{'id':'ro6_b_5','title':'公开固定资料'},None);d.show();d.panel.tabs.setCurrentIndex(1);QTest.qWait(40);tree=d.panel.enemy_overview.tree;rows=[tree.topLevelItem(i).child(j)for i in range(tree.topLevelItemCount())for j in range(tree.topLevelItem(i).childCount())];long=max(rows,key=lambda i:len(i.text(6)));index=tree.indexFromItem(long,6);tree.header().setSectionResizeMode(6,QHeaderView.ResizeMode.Interactive);tree.header().setStretchLastSection(False)
changes=[]
for w in [170,320,600]:
 tree.setColumnWidth(6,w);tree.doItemsLayout();QTest.qWait(40);changes.append({'actual_width':tree.columnWidth(6),'row_height':tree.visualRect(index).height(),'characters':len(long.text(6))})
tree.scrollTo(index);QTest.qWait(40);assert d.grab().save(str(B/'full-mechanism-table.png'));record={'width_results':changes,'actual_Qt_windows':True,'full_original_text':long.text(6),'product_no_game_or_formula_change':True};(B/'result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8');(B/'source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(record,ensure_ascii=False));d.close()
