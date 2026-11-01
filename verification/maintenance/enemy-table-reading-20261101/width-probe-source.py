from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R));B=R/'verification/maintenance/enemy-table-reading-20261101'
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QStyledItemDelegate,QStyleOptionViewItem,QAbstractItemView,QHeaderView
from PySide6.QtTest import QTest
from rouge.player_map_reader import make_reader
class WidthDelegate(QStyledItemDelegate):
 def sizeHint(self,option,index):
  copy=QStyleOptionViewItem(option);copy.rect.setWidth(self.parent().columnWidth(index.column()));return super().sizeHint(copy,index)
app=QApplication([]);d=make_reader('battle',{'id':'ro6_b_5','title':'公开固定资料'},None);d.show();d.panel.tabs.setCurrentIndex(1);QTest.qWait(40);tree=d.panel.enemy_overview.tree;rows=[tree.topLevelItem(i).child(j)for i in range(tree.topLevelItemCount())for j in range(tree.topLevelItem(i).childCount())];long=max(rows,key=lambda i:len(i.text(6)));index=tree.indexFromItem(long,6);tree.header().setSectionResizeMode(6,QHeaderView.ResizeMode.Interactive);tree.header().setStretchLastSection(False)
original=[];after=[]
for dest in [original,after]:
 if dest is after:tree.setItemDelegate(WidthDelegate(tree))
 for w in [170,320,600]:
  tree.setColumnWidth(6,w);tree.doItemsLayout();QTest.qWait(30);dest.append({'actual_width':tree.columnWidth(6),'row_height':tree.visualRect(index).height(),'characters':len(long.text(6))})
tree.scrollTo(index);QTest.qWait(30);assert d.grab().save(str(B/'width-prototype.png'));record={'original_native_delegate':original,'width_constrained_native_delegate':after,'actual_Qt_windows':True,'same_full_original_row_text':long.text(6),'prototype_only_not_product_or_formula_change':True};(B/'width-probe.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8');(B/'width-probe-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(record,ensure_ascii=False));d.close()
