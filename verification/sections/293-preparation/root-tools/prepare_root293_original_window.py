from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import ast,json
root=Path(__file__).resolve().parents[1]
native=json.loads((root/'verification/sections/293-window-attempt1/actual/window.json').read_bytes())
assert native['passed'] and len(native['screenshots'])==6
row={'section':293,'kind':'root_archived_native_images_review','at_utc':datetime.now(timezone.utc).isoformat(),
 'actual_images_opened_with_view_image':True,'images':{},'actual_image_count':6,
 'observed':['Dedicated entry fits the1050x720 main window.',
 'Default result card separates three future buttons and their amounts, with Chinese labels.',
 'Explicit scene page shows the99 gold text as reference, not actual receipt.',
 'Technical raw fields remain in the separate source tab.',
 'Source invalidation removes old content; recovered state is unselected.'],
 'not_verified_from_images':['The conflict card itself is not a separate image; both conflict messages are checked by actual native assertions.',
 'Actual game choice, eligibility, full pool and rewards remain unknown.']}
for image in native['screenshots']:
    path=root/'verification/sections/293-window-attempt1/actual'/Path(image['path']).name
    assert sha256(path.read_bytes()).hexdigest()==image['sha256']
    row['images'][path.relative_to(root).as_posix()]=image['sha256']
dest=root/'verification/sections/293-preparation/root-visual-review.json'
with dest.open('xb') as f:f.write((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
src=(root/'.cache/restart_window_292.py').read_text(encoding='utf8').replace('292','293')
src=src.replace('293-necessary-repair','293-necessary-first').replace('len(expected_sources) == 20',f'len(expected_sources) == {len(native["source_sha256_after"])}')
src=src.replace('handle, expected_pid = 2494016, 10220','handle, expected_pid = 4721974, 27964')
for name,text in [('restart_window_293.py',src),('focus_window_293.py',(root/'.cache/focus_window_292.py').read_text(encoding='utf8').replace('292','293'))]:
    raw=text.encode('utf8');ast.parse(raw);target=root/'.cache'/name;assert not target.exists();target.write_bytes(raw)
print(json.dumps({'reviewed_actual_images':6,'selected_native_sources':len(native['source_sha256_after']),'original_window_tools_prepared':True}))
