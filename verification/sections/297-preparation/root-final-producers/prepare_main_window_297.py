from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[1]
for name in ('restart_window','focus_window'):
 raw=(ROOT/f'.cache/{name}_295.py').read_bytes();s=raw.decode().replace('295','297')
 if name=='restart_window':
  s=s.replace('assert len(expected_sources) == 34','assert len(expected_sources) == 30')
  s=s.replace('handle, expected_pid = 2297712, 35924','handle, expected_pid = 1837982, 38596')
  s=s.replace('print(json.dumps(report, ensure_ascii=False))',"print(json.dumps({k:v for k,v in report.items() if not k.startswith('source_sha256')}, ensure_ascii=False))")
 p=ROOT/f'.cache/{name}_297.py';assert not p.exists();p.write_bytes(s.encode())
base=ROOT/'verification/sections/297-window-attempt1/actual';window=json.loads((base/'window.json').read_bytes())
assert window['passed']and window['unique_checks']==65
images={('verification/sections/297-window-attempt1/actual/'+Path(r['path']).name):r['sha256']for r in window['screenshots']}
assert len(images)==5
for name,value in images.items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
review={'section':297,'kind':'root_archived_native_images_review','at_utc':datetime.now(timezone.utc).isoformat(),
 'actual_images_opened_with_view_image':True,'actual_image_count':5,'images':images,
 'observations':['Node parent shows the exact 未涉足之树 entry and manual expedition reading button without altering retained technical-reading tab.',
 'Rest result clearly places2hope under选择时; no beak or promotion attributes shown for rest.',
 'Manual root return-item page shows the fixed beacon icon, complete use/description/unlock distinction and explains it is on return, not immediate choice grant.',
 'Both source-negative images clear selected choice, all old result/item content and icon; no stale reward remains.'],
 'representative_images_not_every_choice_every_tab':True,'actual_game_dispatch_return_or_reward_verified':False}
p=ROOT/'verification/sections/297-preparation/root-visual-review.json';assert not p.exists()
p.write_bytes((json.dumps(review,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'root_visual_images':5,'source_maps_before_restart_pending':True}))
