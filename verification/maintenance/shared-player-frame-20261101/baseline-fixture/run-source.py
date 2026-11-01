from pathlib import Path
import sys,types,unittest,json,subprocess
R=Path.cwd();B=R/'verification/maintenance/shared-player-frame-20261101';out=B/'baseline-fixture';sys.path[:0]=[str(R),str(R/'scripts')]
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);code=p.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code,'old_compact_source':'7e4e2f5daf00277686459491fb6c6f85e0b0bcce'},indent=2),'utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'baseline_actual_exit':code});raise SystemExit(0 if code==1 else 1)
from PySide6.QtWidgets import QApplication
qt=QApplication([])
import tests.test_player_popover_refresh as t
m=types.ModuleType('rouge._baseline_compact_frame');m.__package__='rouge';exec(compile((R/'research/shared-player-frame-20261101/before-player_compact.py').read_text('utf8'),'baseline-player_compact.py','exec'),m.__dict__)
t.CompactAssistant=m.CompactAssistant;t.ToolPopover=m.ToolPopover
result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([t.PopoverRefreshTests('test_inventory_bundle_sleeps_and_restores_together')]))
raise SystemExit(0 if result.wasSuccessful()else 1)
