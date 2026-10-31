from pathlib import Path
import sys,json
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette,QColor,QFont
from rouge.player_compact import ToolPopover
from rouge.player_item_hover import ItemHoverCard
from rouge.player_map_hover import NodeHoverCard
from player_ui_verification import run
assets=R/'.cache/qt-themes-446/generated-final';colors=json.loads((assets/'palettes.json').read_bytes())
sheets={n:(assets/(n+'.qss')).read_text('utf8').replace('@ICONS@',(assets/'icons').as_posix())for n in colors}
def palette(name):
 result=QPalette()
 for group,roles in colors[name].items():
  for role,color in roles.items():result.setColor(QPalette.ColorGroup[group],QPalette.ColorRole[role],QColor(color))
 return result
original=ToolPopover.setStyleSheet
def apply_sheet(self,skin):
 name='dark'if self.objectName()in('inventoryWindow','itemHoverCard','nodeHoverCard')else'light'
 self.setPalette(palette(name));self.setFont(QFont('Microsoft YaHei UI',9));original(self,sheets[name]+skin)
ToolPopover.setStyleSheet=ItemHoverCard.setStyleSheet=NodeHoverCard.setStyleSheet=apply_sheet
out=R/'verification/sections/446-theme-candidate';out.mkdir(exist_ok=False)
raise SystemExit(run(445,out/'window.json'))
