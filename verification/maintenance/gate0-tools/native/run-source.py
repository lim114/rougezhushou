from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from tempfile import TemporaryDirectory
import sys,json,subprocess,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/maintenance/gate0-tools/native'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('wb')as a,(out/'stderr.txt').open('wb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],stdout=a,stderr=b);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'exit':code});print((out/'stderr.txt').read_text('utf8')[-2200:]);raise SystemExit(code)
from PySide6.QtCore import QTimer
from rouge import player_acceptance
from rouge.session_recording import SessionRecorder
import player_ui_verification as ui
import numpy as np

def check(section,window,gui,require):
 for timer in window.findChildren(QTimer):timer.stop()
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window
 with TemporaryDirectory(prefix='gate0-isolated-native-')as temp:
  recorder=SessionRecorder(Path(temp)/'session',scenario='normal');window.session_recorder=recorder
  require(c.open_full(window.inventory_panel),'shared_inventory_entry');gui.processEvents()
  recorder.surfaces(gui,entry=type(window.workspace.currentWidget()).__name__)
  observation={'page':'unknown','nodes':[],'captured_at':max(time.time(),window.run.state['started_at']+.001),'performance':{'total_ms':1,'backend':'synthetic_gate0'},'_sampling':{'epoch':window.sample_epoch,'generation':window.capture.stats()['generation'],'seq':1}}
  window.sample_received((np.full((24,36,3),65,np.uint8),observation));gui.processEvents()
  stale={**observation,'_sampling':{**observation['_sampling'],'epoch':window.sample_epoch+1}}
  window.sample_received((np.full((24,36,3),65,np.uint8),stale));gui.processEvents()
  c.game_map_overlay.tick() if hasattr(c,'game_map_overlay') else None
  recorder.close();window.session_recorder=None
  rows=[json.loads(line)for line in(recorder.folder/'events.jsonl').read_text('utf8').splitlines()]
  samples=[row for row in rows if row['event']=='sample'];surfaces=[row for row in rows if row['event']=='surfaces']
  require(len(samples)==2 and samples[0]['applied']and not samples[1]['applied'],'actual_sample_hooks_accept_and_reject')
  require(samples[1]['reason']=='stale_generation','actual_stale_reason')
  require(any(row['class']=='ReferenceWindow'for row in surfaces[0]['visible']),'actual_shared_window_inventory')
  require(any(row['page_class']for row in surfaces[0]['visible']),'actual_shared_page_inventory')
  require(window.run.state==before,'read_only_instrumentation_preserves_run')
  require(rows[-1]['event']=='session_end','queue_drained_and_closed')
  window.player_validation_target=c.reference_window
player_acceptance.check=check
raise SystemExit(ui.run(472,out/'window.json'))
