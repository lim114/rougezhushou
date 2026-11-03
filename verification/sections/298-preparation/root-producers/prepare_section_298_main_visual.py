from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[1]
receipt=ROOT/'verification/sections/298-window-attempt1/actual/window.json';w=json.loads(receipt.read_bytes());assert w['passed']
images={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest()for p in receipt.parent.glob('*.png')}
assert len(images)==5
row={'section':298,'kind':'root_archived_native_images_review','at_utc':datetime.now(timezone.utc).isoformat(),
 'actual_images_opened_with_view_image':True,'actual_image_count':5,'images':images,
 'observations':['Exact 未涉足之树 entry remains manually readable in the first-floor 已列条件不符 branch.',
 'Current visible title stays in the ordinary reference branch and the remembered clearing title stays in its separate 历史已读内容 branch.',
 'The warm source-failure screenshot replaces the prior excluded branch with 资格未确认; restored reading returns to the excluded branch, retaining the event identity.',
 'All five representative PNGs show the retained 资料与依据 tab. They visually establish directory, reading and history layout; they do not directly show the new player-condition block. Its exact Chinese wording, absence of IDs and context/source-invalid transitions were checked in the actual player widget by the canonical native and Panel tests.'],
 'representative_images_not_every_choice_every_tab':True,'actual_game_generation_or_entry_verified':False}
p=ROOT/'verification/sections/298-preparation/root-visual-review.json';assert not p.exists();p.write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode())
source=ROOT/'.cache/restart_window_297.py';raw=source.read_bytes()
new=raw.replace(b'297',b'298').replace(b'298-necessary-first',b'298-necessary-final').replace(b'== 30',b'== 24').replace(b'1837982, 38596',b'1510198, 36452')
assert new!=raw and b'1510198, 36452'in new
target=ROOT/'.cache/restart_window_298.py';assert not target.exists();target.write_bytes(new)
source2=ROOT/'.cache/focus_window_297.py';target2=ROOT/'.cache/focus_window_298.py';assert not target2.exists();target2.write_bytes(source2.read_bytes().replace(b'297',b'298'))
print(json.dumps({'visual_review':str(p.relative_to(ROOT)),'native_source_files':len(w['source_sha256_after']),'original_HWND':1510198,'original_PID':36452}))
