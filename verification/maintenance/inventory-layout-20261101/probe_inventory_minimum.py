from pathlib import Path
from unittest.mock import patch
import sys,json
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtWidgets import QSizePolicy
from rouge import player_acceptance
from player_ui_verification import run
def check(section,w,gui,require):
 w.show_compact();bar=w.compact_window;bar.open_inventory();d=bar.inventory_popup;gui.processEvents()
 def record(mode):
  print(json.dumps({'mode':mode,'popup':[d.width(),d.height()],'popup_min':[d.minimumWidth(),d.minimumHeight()],'pages_min_hint':[d.pages.minimumSizeHint().width(),d.pages.minimumSizeHint().height()],'panels':[(d.pages.tabText(i),[d.pages.widget(i).minimumSizeHint().width(),d.pages.widget(i).minimumSizeHint().height()],[d.pages.widget(i).minimumWidth(),d.pages.widget(i).minimumHeight()])for i in range(d.pages.count())]}),flush=True)
 record('before');d.pages.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Ignored);d.resize(1200,540);gui.processEvents();record('ignored')
 require(True,'probe_owned_Qt_layout_only');w.player_validation_target=d
out=R/'verification/maintenance/inventory-layout-20261101/minimum-probe';out.mkdir()
with patch.object(player_acceptance,'check',side_effect=check):raise SystemExit(run(445,out/'window.json'))
