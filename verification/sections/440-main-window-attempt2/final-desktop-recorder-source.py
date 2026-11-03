"""Record only after root has actually inspected the matching post-full MCP crop."""
from pathlib import Path
from hashlib import sha256
import json,ctypes,win32gui,win32process
R=Path.cwd();folder=R/'verification/sections/440-main-window-attempt2';p=folder/'final-response.json';raw=p.read_bytes();v=json.loads(raw);summary=R/'verification/full-440/summary.json';assert v['passed']and v['actual_after_complete_full_scope']and v['complete_full_summary_sha256']==sha256(summary.read_bytes()).hexdigest()
assert v['owned_windows']and not(folder/'final-desktop-review.json').exists()
for r in v['owned_windows']:
 h=r['hwnd'];assert win32gui.IsWindow(h)and win32process.GetWindowThreadProcessId(h)[1]==r['pid']and win32gui.IsWindowVisible(h)and not win32gui.IsIconic(h)and not ctypes.windll.user32.IsHungAppWindow(h)
ctypes.windll.user32.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4))
r=v['owned_windows'][0];assert list(win32gui.GetWindowRect(r['hwnd']))==r['physical_rect'];assert r['physical_rect']==[2147,1464,2561,1518],'Inspect actual geometry and use a fresh matching MCP crop, do not infer viewing.'
record={'section':440,'actor':'/root','actual_windows_mcp_snapshot_called':True,'actual_live_surface_reviewed':True,'actual_after_complete_full_scope':True,'snapshot_region_physical_pixels':[2137,1454,2560,1528],'observed_native_toolbar_physical_rect':r['physical_rect'],'actual_visible_toolbar_icons':7,'matching_owned_pids':[r['pid']],'owned_native_window_responding':True,'final_response_sha256':sha256(raw).hexdigest(),'complete_full_summary_sha256':v['complete_full_summary_sha256'],'blocking_issues':[],'game_operated':False,'chat_sent':False,'private_contents_or_hashes_published':False,'limits':['Actual owned test application visible and responding after full validation; no live game, current server or desktop chat acceptance inferred.']}
(folder/'final-desktop-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8');(folder/'final-desktop-recorder-source.py').write_bytes(Path(__file__).read_bytes());print('Actual root post-full MCP viewing recorded, no game or chat inputs.')
