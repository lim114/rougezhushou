from pathlib import Path
from unittest.mock import patch
import sys,json
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtWidgets import QLayout
from rouge import player_acceptance
from player_ui_verification import run
original=player_acceptance.check
def check(section,w,gui,require):
 original(445,w,gui,require);bar=w.compact_window;bar.open_inventory();d=bar.inventory_popup;d.panel.reader.hide();gui.processEvents()
 def record(mode):
  layout=d.layout()
  print(json.dumps({'mode':mode,'popup':[d.width(),d.height()],'popup_min':[d.minimumWidth(),d.minimumHeight()],'layout_min':[layout.minimumSize().width(),layout.minimumSize().height()],'hfw':[(n,layout.totalHeightForWidth(n))for n in(480,640,900,1200)],'resources_hint':[d.resources.sizeHint().width(),d.resources.sizeHint().height()]}),flush=True)
 record('before');d.layout().setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint);d.setMinimumSize(0,0);d.resize(1200,540);gui.processEvents();record('no_fixed_minimum')
 for width in(480,640,900,1200):
  d.resize(width,540);gui.processEvents();record('width_'+str(width))
 require(True,'probe_actual_height_for_width_only');w.player_validation_target=d
out=R/'verification/maintenance/inventory-layout-20261101/minimum-probe2';out.mkdir()
with patch.object(player_acceptance,'check',side_effect=check):raise SystemExit(run(445,out/'window.json'))
