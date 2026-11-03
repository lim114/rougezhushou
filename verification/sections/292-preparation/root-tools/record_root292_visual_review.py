from pathlib import Path
from hashlib import sha256
import json
from datetime import datetime, timezone
root=Path(__file__).resolve().parents[1]
folder=root/'verification/sections/292-window-attempt1/actual'
receipt=json.loads((folder/'window.json').read_bytes())
assert receipt['passed'] and receipt['unique_checks']==33
images={}
for item in receipt['screenshots']:
    path=folder/Path(item['path']).name
    raw=path.read_bytes();assert sha256(raw).hexdigest()==item['sha256']
    images[path.relative_to(root).as_posix()]=item['sha256']
row={'section':292,'kind':'root_actual_archived_images_review',
 'at_utc':datetime.now(timezone.utc).isoformat(),'actual_images_opened_with_view_image':True,
 'receipt':'verification/sections/292-window-attempt1/actual/window.json',
 'images':images,'image_count':4,'client_size_logical':[1050,720],
 'observed':['Two adjacent scene/choice filters are inside the window and readable in Chinese.',
 'Ordinary option exposes its own fixed emergency reference without borrowing another option.',
 'Actual fixed battle map, enemy icon and stage title are visible after the button.',
 'Nonbattle option shows an empty preview placeholder and disabled battle button.'],
 'not_proved_by_pixels':['Actual in-game eligibility, random branch, choice execution or rewards.',
 'Whole repository, game capture, chat or the historical full290 range on new292 source.'],
 'external_operations_per_raw_receipt':receipt['external_operation_attempts']}
dest=root/'verification/sections/292-preparation/root-visual-review.json'
with dest.open('xb') as f:f.write((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'reviewed':len(images),'section':292}))
