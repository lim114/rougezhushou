from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[1]
for name in ('restart_window','focus_window'):
 source=ROOT/f'.cache/{name}_295.py';raw=source.read_bytes();text=raw.decode('utf8')
 text=text.replace('295','296')
 if name=='restart_window':
  text=text.replace('296-window-attempt1','296-window-attempt2')
  text=text.replace('296-necessary-first','296-necessary-reading-retry2')
  assert 'assert len(expected_sources) == 34' in text
  text=text.replace('assert len(expected_sources) == 34','assert len(expected_sources) == 64')
  assert 'handle, expected_pid = 2297712, 35924' in text
  text=text.replace('handle, expected_pid = 2297712, 35924','handle, expected_pid = 1249148, 8260')
  text=text.replace('print(json.dumps(report, ensure_ascii=False))',"print(json.dumps({k:v for k,v in report.items() if not k.startswith('source_sha256')}, ensure_ascii=False))")
 target=ROOT/f'.cache/{name}_296.py';assert not target.exists();target.write_bytes(text.encode('utf8'))
review=ROOT/'verification/sections/296-preparation/root-visual-review.json';assert not review.exists()
base=ROOT/'verification/sections/296-window-attempt2/actual'
window=json.loads((base/'window.json').read_bytes())
assert window['passed'] and window['unique_checks']==78
images={('verification/sections/296-window-attempt2/actual/'+Path(row['path']).name):row['sha256'] for row in window['screenshots']}
assert len(images)==5
for name,value in images.items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
row={'section':296,'kind':'root_archived_native_images_review',
 'at_utc':datetime.now(timezone.utc).isoformat(),'actual_images_opened_with_view_image':True,
 'actual_image_count':5,'images':images,
 'observations':['Manual entry reference reader has ordinary-player Chinese event/choice and event-only floor scope.',
 'Exact event body now shows scene2 and selected option1强行驱赶; title/cursor visible, not a claim that the entire effect paragraph fits.',
 'Autopsy shows separate main3/4/5 and fake-floor reference, source/community conditions and unproven actual-entry limits.',
 'Both damaged-source representative images clear stale reading content and event manual button is disabled when relevant.'],
 'screenshots_are_representative_not_every_stage':True,'actual_game_or_chat_verified':False}
review.write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
extra=ROOT/'verification/sections/296-preparation/review/reading-anchor-correction-review.json'
assert not extra.exists();extra.write_bytes((ROOT/'.cache/p3-296-independent-review/reading-anchor-correction-review.json').read_bytes())
print(json.dumps({'section':296,'root_reviewed_actual_images':5,'main_scripts_prepared':True,'main_window_not_yet_restarted':True}))
