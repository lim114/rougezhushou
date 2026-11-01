from pathlib import Path
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import patch
import sys,json
R=Path.cwd();sys.path.insert(0,str(R))
from PySide6.QtWidgets import QApplication,QDialog
from PySide6.QtTest import QTest
from rouge import battle_enemy_readers as readers
qt=QApplication([]);rows=[]
for name,spec in readers._READERS.items():
 model=import_module('rouge.'+spec.provider);sid=model.STAGES[0];ref=model.reference(sid);row=(ref.get('rows')or ref.get('entities'))[0];key=row['enemy_key']if name=='boss_documents'else row['key'];view=import_module('rouge.'+spec.provider.removesuffix('_reference')+'_view');ctor=getattr(view,spec.dialog)
 for route in('close','reject','done','owner','owner_hidden'):
  d=ctor(sid,key)
  if route!='owner_hidden':d.show();QTest.qWait(20)
  geometry=[d.width(),d.height()]
  with patch.object(d.panel,'clear_reference',wraps=d.panel.clear_reference)as clear:
   if route.startswith('owner'):readers.close_reader(SimpleNamespace(**{name+'_dialog':d}),name)
   elif route=='done':d.done(QDialog.DialogCode.Rejected)
   else:getattr(d,route)()
   qt.processEvents();rows.append({'reader':name,'stage':sid,'route':route,'actual_size':geometry,'clear_calls':clear.call_count,'result_cleared':d.panel.result is None,'visible':d.isVisible()})
  d.deleteLater();qt.processEvents()
(R/'verification/maintenance/mechanism-reader-windows-20261101/closing-after.json').write_text(json.dumps(rows,indent=2)+'\n','utf8');print(json.dumps([{'reader':name,'counts':{x['route']:x['clear_calls']for x in rows if x['reader']==name}}for name in readers._READERS]))
