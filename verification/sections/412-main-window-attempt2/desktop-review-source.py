from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json
R=Path(__file__).resolve().parents[1];out=R/'verification/sections/412-main-window-attempt2'
runtime=json.loads((out/'window.json').read_bytes());assert runtime['passed']and runtime['private_six_paths_unchanged']
desktop={'section':412,'actor':'/root','actual_windows_mcp_snapshot_called':True,'actual_live_surface_reviewed':True,
    'blocking_issues':[],'matching_owned_pids':[r['pid']for r in runtime['owned_windows']],
    'runtime_receipt_sha256':sha256((out/'window.json').read_bytes()).hexdigest(),
    'private_screenshot_saved_or_published':False,'actual_region':[1500,1250,2560,1600],
    'visible_scope':'Actual right-bottom transparent single-row toolbar with separate circular tools. No game or current recognition accuracy is inferred. Ownership is from exact native PID receipt; snapshot UI-tree gave no ownership.',
    'at_UTC':datetime.now(timezone.utc).isoformat()}
(out/'desktop-review.json').write_bytes((json.dumps(desktop,ensure_ascii=False,indent=2)+'\n').encode())
p=R/'verification/sections/412-video-appearance.json';value=json.loads(p.read_bytes())
value['retained_attempt2_failure']='The test directly called setFocus on the same tool after closing its popup; focusWidget at failure was not recorded, so its precise cause is not claimed. Final verification activates the owned toolbar, sends Tab from the previous tool, checks the keyboard focus indicator, and uses Space to open the tool. Original assertion and raw failure remain.'
p.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())
(R/'verification/sections/412-usage.json').write_bytes((json.dumps({'section':412,'remaining_percent':60,'source':'actual account usage tool: usedPercent40;10080-minute window','secondary_unavailable':True,'triggered':False,'threshold_strictly_below':15},ensure_ascii=False,indent=2)+'\n').encode())
(out/'desktop-review-source.py').write_bytes(Path(__file__).read_bytes())
print('Actual updated toolbar reviewed. Private screenshot omitted, raw failures retained, verified remaining60 percent.')
