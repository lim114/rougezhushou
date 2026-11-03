from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[1]
native_path=ROOT/'verification/sections/303-window-attempt1/actual/window.json'
native=json.loads(native_path.read_bytes());assert native['passed'] and native['screenshot_count']==5
for name in ('restart_window','focus_window'):
    target=ROOT/f'.cache/{name}_303.py';assert not target.exists()
    text=(ROOT/f'.cache/{name}_302.py').read_text(encoding='utf8').replace('302','303')
    if name=='restart_window':
        text=text.replace('2753884, 35808','12452876, 24088').replace('len(expected_sources) == 39','len(expected_sources) == '+str(len(native['source_sha256_after'])))
    target.write_text(text,encoding='utf8')
images={}
for row in native['screenshots']:
    path=native_path.with_name(Path(row['path']).name)
    assert sha256(path.read_bytes()).hexdigest()==row['sha256']
    images[path.relative_to(ROOT).as_posix()]=row['sha256']
record={'section':303,'kind':'root_archived_native_images_review','actual_images_opened_with_view_image':True,
 'actual_image_count':5,'images':images,'at_utc':datetime.now(timezone.utc).isoformat(),
 'observations':['Root directly viewed all five archived actual native PNGs.',
  '畸症 and both 本性难移 stage variants display the matching fixed bitmap, enemy picture and direct point markers; captions correctly state37 or12 approximate ground centers.',
  'The three mapped pages visibly distinguish fixed schedule offsets from actual entry times and do not imply actual battle tracking.',
  'The two true rejected-source cells show the Chinese position-unverified message and have no original-map marker; no borrowed or extrapolated point is drawn.',
  'Player text explains partial coverage; neither all-terrain calibration nor actual spawn accuracy is claimed.'],
 'actual_gameplay_or_absolute_position_accuracy_verified':False}
path=ROOT/'verification/sections/303-preparation/root-visual-review.json';assert not path.exists();path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source_count':len(native['source_sha256_after']),'actual_native_images_reviewed':5,'restart_focus_prepared_not_executed':True}))
