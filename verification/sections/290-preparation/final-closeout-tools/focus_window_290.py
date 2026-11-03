import ctypes,json
from pathlib import Path
import win32gui,win32process
ROOT=Path(__file__).resolve().parents[1]
target=ROOT/'verification/sections/290-main-window-focus.json'
assert not target.exists()
receipt=json.loads((ROOT/'verification/sections/290-main-window.json').read_bytes())
assert receipt['passed'] and receipt['private_hashes_equal'] and len(receipt['visible_windows'])==1
window=receipt['visible_windows'][0]
handle,process_id=window['hwnd'],window['pid']
assert win32gui.IsWindow(handle) and win32process.GetWindowThreadProcessId(handle)[1]==process_id
returned=bool(ctypes.windll.user32.SetForegroundWindow(handle))
report={'hwnd':handle,'pid':process_id,'set_foreground_returned':returned,
        'actual_foreground':win32gui.GetForegroundWindow(),
        'visible':bool(win32gui.IsWindowVisible(handle))}
with target.open('x',encoding='utf8') as stream:stream.write(json.dumps(report,ensure_ascii=False)+'\n')
print(json.dumps(report))
assert report['actual_foreground']==handle and report['visible']
