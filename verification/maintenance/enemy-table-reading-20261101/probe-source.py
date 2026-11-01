from pathlib import Path
from hashlib import sha256
import sys,json,subprocess
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/enemy-table-reading-20261101';D=R/'research/enemy-table-reading-20261101'
if len(sys.argv)==1:
 B.mkdir(exist_ok=False);D.mkdir(exist_ok=False)
 files=['rouge/enemy_overview.py','tests/test_enemy_overview_review.py','scripts/verify_full_available.py']
 for n in files:(D/('before-'+Path(n).name)).write_bytes((R/n).read_bytes())
 private=['.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/conversations.json.pending','local-settings.json','.local/player-shortcut.json']
 (R/'.cache/enemy-table-before.json').write_text(json.dumps({'base_commit':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),'private':{n:sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None for n in private}},indent=2),'utf8')
 with(B/'probe-stdout.txt').open('xb')as a,(B/'probe-stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);code=child.wait()
 (B/'probe-process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(B/'probe-source.py').write_bytes(Path(__file__).read_bytes());print({'exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QStyledItemDelegate,QStyleOptionViewItem,QAbstractItemView
from PySide6.QtTest import QTest
from rouge.player_map_reader import make_reader
class WidthDelegate(QStyledItemDelegate):
 def sizeHint(self,option,index):
  copy=QStyleOptionViewItem(option);copy.rect.setWidth(self.parent().columnWidth(index.column()));return super().sizeHint(copy,index)
app=QApplication([]);assert app.platformName()=='windows';d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料'},None);d.show();d.panel.tabs.setCurrentIndex(1);QTest.qWait(50);tree=d.panel.enemy_overview.tree
assert d.grab().save(str(B/'before.png'))
rows=[tree.topLevelItem(i).child(j)for i in range(tree.topLevelItemCount())for j in range(tree.topLevelItem(i).childCount())];lookup={e['key']:e for e in d.panel.result['enemies']};long=max(rows,key=lambda i:len('\n'.join(lookup[i.data(0,Qt.ItemDataRole.UserRole)]['abilities'])));index=tree.indexFromItem(long,6);original={'characters':len(long.text(6)),'row_height':tree.visualRect(index).height(),'cell_width':tree.columnWidth(6)}
for item in rows:
 enemy=lookup[item.data(0,Qt.ItemDataRole.UserRole)];item.setText(6,'\n'.join(enemy['abilities'])or enemy['description'])
tree.setItemDelegate(WidthDelegate(tree));tree.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel);tree.setTextElideMode(Qt.TextElideMode.ElideNone);tree.header().sectionResized.connect(tree.doItemsLayout);tree.doItemsLayout();QTest.qWait(30)
changes=[]
for w in [170,320,600]:
 tree.header().setStretchLastSection(False);tree.setColumnWidth(6,w);tree.doItemsLayout();QTest.qWait(30);changes.append({'column_width':tree.columnWidth(6),'height':tree.visualRect(index).height(),'characters':len(long.text(6))})
assert d.grab().save(str(B/'native-delegate-prototype.png'));record={'original':original,'full_text_native_width_results':changes,'actual_Qt_windows':True,'no_game_chat_private_state':True};(B/'probe.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(record,ensure_ascii=False));d.close()
