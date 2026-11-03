from pathlib import Path
import sys,json
sys.path.insert(0,str(Path.cwd()))
from PySide6.QtWidgets import QApplication,QListWidget,QListWidgetItem,QListView
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
app=QApplication([]);original=QListWidget()
for key in ('public-first','public-second'):
 item=QListWidgetItem(key);item.setData(Qt.ItemDataRole.UserRole,key);original.addItem(item)
view=QListView();view.setModel(original.model());view.setSelectionModel(original.selectionModel());seen=[];original.currentItemChanged.connect(lambda item,_:seen.append(item.data(Qt.ItemDataRole.UserRole)if item else None));view.show();app.processEvents();before=original.currentRow();seen.clear();index=view.model().index(1,0);QTest.mouseClick(view.viewport(),Qt.MouseButton.LeftButton,pos=view.visualRect(index).center());app.processEvents();after=original.currentRow();events=list(seen);shared=view.model()is original.model()and view.selectionModel()is original.selectionModel();view.hide();original.clear();empty=view.model().rowCount()==0
result={'actual_Windows_QPA':app.platformName(),'same_Qt_model_and_selection_model':shared,'before_row':before,'after_row':after,'actual_item_signal_keys':events,'clear_propagates':empty,'no_game_chat_or_private_state_used':True};result['passed']=shared and after==1 and events==['public-second']and empty
out=Path('verification/maintenance/battle-overview-sections-20261101');(out/'shared-model-probe.json').write_text(json.dumps(result,indent=2)+'\n','utf8');(out/'shared-model-probe-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result));raise SystemExit(0 if result['passed']else 1)
