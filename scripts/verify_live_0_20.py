"""One actual background game frame; no game or chat writes."""
import hashlib,json,sys,time
from pathlib import Path
import win32gui
import cv2
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from rouge.capture import GameCapture,list_game_windows
from rouge.recognition import ScreenReader
from rouge.run_state import RunState

targets=list_game_windows();capture=GameCapture()
receipt={'version':'0.20.0','verified_at':time.time(),'chat_requests':0,'game_input_actions':0}
try:
    if len(targets)!=1 or targets[0]['minimized']:
        receipt.update(status='unavailable',reason='Game absent, ambiguous, or minimized; no restoration performed.')
    else:
        capture.connect(targets[0]);foreground=win32gui.GetForegroundWindow();frame=capture.capture(timeout=8)
        observed=ScreenReader().read(frame['image'],client_rect=frame.get('client_rect'))
        saved=RunState(ROOT/'.local/run-state.json');before=json.loads((ROOT/'.cache/upgrade-0.20-checkpoint.json').read_text(encoding='utf8'))
        same_run=before['run_id_hash']==hashlib.sha256(saved.state['id'].encode()).hexdigest()
        if same_run:assert len(saved.state['history'])>=before['history_count']
        graph=observed.get('map') or {};stored=saved.state['maps'].get(graph.get('zone_id')) or {}
        sample=ROOT/'samples/native-client/live-0.20.png';cv2.imencode('.png',frame['image'])[1].tofile(sample)
        receipt.update(status='captured',page=observed['page'],captured_at=frame['captured_at'],
            viewport=observed['viewport'],map_status=graph.get('status'),template=graph.get('template_id'),
            app_map_matches=bool(graph.get('status')=='matched' and stored.get('template_id')==graph['template_id']),
            app_run_last_read=saved.state['last_read'],same_run_preserved=same_run,history_preserved=True if same_run else None,
            game_in_background=foreground!=targets[0]['hwnd'],foreground_unchanged=foreground==win32gui.GetForegroundWindow(),
            sample=str(sample.relative_to(ROOT)),sample_sha256=hashlib.sha256(sample.read_bytes()).hexdigest(),
            performance=observed['performance'])
    (ROOT/'LIVE_0.20_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('performance','viewport')},ensure_ascii=False))
finally:capture.close()
