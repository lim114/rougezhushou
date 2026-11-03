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
 model=import_module('rouge.'+spec.provider);sid=model.STAGES[0];ref=model.reference(sid);row=(ref.get('rows')or ref.get('entities'))[0];key=row['enemy_key']if name=='boss_documents'else row['key'];view=import_module('rouge.'+spec.provider.removesuffix('_reference')+'_view');d=getattr(view,spec.dialog)(sid,key);d.show();QTest.qWait(20);p=d.panel
 rows.append({'reader':name,'stage':sid,'actual_size':[d.width(),d.height()],'body_height':p.player.viewport().height(),'line_spacing':p.player.fontMetrics().lineSpacing(),'player_sha256':__import__('hashlib').sha256(p.player.toPlainText().encode('utf8')).hexdigest(),'technical_sha256':__import__('hashlib').sha256(p.technical.toPlainText().encode('utf8')).hexdigest(),'notice':p.notice.text()});d.reject();d.deleteLater();qt.processEvents()
(R/'verification/maintenance/mechanism-reading-density-20261101/reading-before.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps([{'reader':r['reader'],'body_height':r['body_height']}for r in rows]))
