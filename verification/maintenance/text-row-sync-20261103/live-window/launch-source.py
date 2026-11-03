from pathlib import Path
from datetime import datetime
import sys,json,time,uuid
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from rouge.app import MainWindow
from rouge.session_recording import SessionRecorder,state_snapshot
r=Path.cwd();folder=r/'.local/gate0'/f'{datetime.now():%Y%m%d-%H%M%S}-text-rows-{uuid.uuid4().hex[:6]}'
recorder=SessionRecorder(folder,scenario='text_row_background_smoke')
(r/'.cache/current-sync-session-folder.txt').write_text(str(folder),'utf8')
app=QApplication([]);w=MainWindow();w.show_compact();c=w.compact_window;initial_id=w.run.state['id']
recorder.event('state_baseline',state=state_snapshot(w.run.state))
ready={'started':False}
def source_ready(_result):
 if not ready['started']and w.last_sample_at>0:
  ready['started']=True;w.session_recorder=recorder;recorder.event('source_ready',utc=datetime.now().astimezone().isoformat())
  recorder.sample(w.observation,w.run.state,applied=True,reason='source_ready_first_frame')
  QTimer.singleShot(60000,stop_recording)
w.events.sample.connect(source_ready)
def report():
 b=c.game_binding;s=b.snapshot;host=c.reference_window;stats=w.capture.stats();rect=s['logical_client']if s and s['active']else None
 value={'toolbar_visible':c.isVisible(),'reader_visible':host.isVisible(),'tray_visible':c.tray.isVisible(),'native_bar':int(c.winId()),'native_host':int(host.winId()),'auto_sampling':w.auto.isChecked(),'binding_active':bool(rect),'outside_game':not c.geometry().intersects(rect)if rect and c.isVisible()else None,'same_run':w.run.state['id']==initial_id,'pending':stats['pending'],'overflow':stats['overflow'],'last_sample_at':w.last_sample_at,'last_sample_seq':w.last_sample_seq,'inferred_text_rows':(w.observation or {}).get('performance',{}).get('ocr',{}).get('inferred_text_rows'),'reused_text_rows':(w.observation or {}).get('performance',{}).get('ocr',{}).get('reused_text_rows'),'reader_width':host.width(),'reader_height':host.height(),'reader_overlap_fraction':(lambda v:v.width()*v.height()/max(1,rect.width()*rect.height()))(host.geometry().intersected(rect))if rect and host.isVisible()else None,'at':time.time()}
 (r/'.cache/current-sync-live-status.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
 if w.session_recorder is not None:recorder.event('sampling_queue',pending=stats['pending'],overflow=stats['overflow'],oldest_at=stats.get('oldest_at'),latest_at=stats.get('latest_at'))
 if w.session_recorder is not None:recorder.surfaces(app,entry=type(w.workspace.currentWidget()).__name__)
def stop_recording():
 recorder.close();w.session_recorder=None;timer.setInterval(2000)
 (r/'.cache/current-sync-recording-finished.json').write_text(json.dumps({'done':True,'seconds':60,'app_continues_sampling':True}),'utf8')
timer=QTimer();timer.setInterval(1000);timer.timeout.connect(report);timer.start()
app.aboutToQuit.connect(recorder.close)
w.auto.setChecked(True)
raise SystemExit(app.exec())
