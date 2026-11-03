from pathlib import Path
import sys,json,subprocess
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/shared-player-frame-20261101';out=B/'card-close-probe'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);code=p.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'exit':code});raise SystemExit(0)
from rouge import player_acceptance
from player_ui_verification import run
from unittest.mock import patch
original=player_acceptance.check

def observed(section,window,gui,require):
 def record(value,label):
  if label=='card447_actual_close_symbol_fits_and_has_high_contrast_on_dark_background':
   viewer=window.compact_window.replay_popup.panel.statistics.card_controls.viewer;c=viewer.titleBar.closeBtn;v={'visible':c.isVisible(),'width':c.width(),'height':c.height(),'glyph_width':c.fontMetrics().horizontalAdvance('×'),'normal_paint_color':c.getNormalColor().name(),'hover_color':c.getHoverColor().name(),'palette_text':c.palette().buttonText().color().name(),'image_null':c.grab().isNull(),'frame_theme':viewer.property('playerTheme'),'class':type(c).__name__,'actual_check_value':bool(value)};(out/'observed.json').write_text(json.dumps(v,indent=2)+'\n','utf8');viewer.grab().save(str(out/'before.png'))
  require(value,label)
 return original(section,window,gui,record)
with patch.object(player_acceptance,'check',observed):raise SystemExit(run(447,out/'window.json'))
