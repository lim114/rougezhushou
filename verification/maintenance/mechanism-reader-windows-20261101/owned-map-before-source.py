from pathlib import Path
from importlib import import_module
from unittest.mock import patch
import sys,json
R=Path.cwd();sys.path.insert(0,str(R))
from PySide6.QtWidgets import QApplication,QDialog
qt=QApplication([]);rows=[]
for provider,cls in [('current_sun_boss','CurrentSunBossPanel'),('current_boss_documents','CurrentBossDocumentsPanel'),('current_guest_knights','CurrentGuestKnightsPanel'),('current_guest_crystals','CurrentGuestCrystalsPanel'),('current_guest_material','CurrentGuestMaterialPanel')]:
 view=import_module('rouge.'+provider+'_view');model=view.model;sid=model.STAGES[0]
 for route in ('close','reject','done','owner'):
  p=getattr(view,cls)(sid);p.show();qt.processEvents();assert p.open_map();child=p.map_dialog
  with patch.object(child.panel,'clear_reference',wraps=child.panel.clear_reference)as clear:
   if route=='owner':p.clear_reference()
   elif route=='done':child.done(QDialog.DialogCode.Rejected)
   else:getattr(child,route)()
   qt.processEvents();rows.append({'provider':provider,'route':route,'clear_calls':clear.call_count,'source_cleared':child.panel.result is None,'visible':child.isVisible()})
  p.clear_reference();p.close();child.deleteLater();p.deleteLater();qt.processEvents()
(R/'verification/maintenance/mechanism-reader-windows-20261101/owned-map-before.json').write_text(json.dumps(rows,indent=2)+'\n','utf8');print(json.dumps(rows))
