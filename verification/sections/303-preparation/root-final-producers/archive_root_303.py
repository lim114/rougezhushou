from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'verification/sections/303-preparation/root-final-producers';base.mkdir(parents=True,exist_ok=True)
names=('prepare_original_303.py','restart_window_303.py','focus_window_303.py','record_closeout_first_failure_303.py','archive_root_303.py',
       'p3-303-native-window/root-launch/launch.json','p3-303-native-window/root-launch/stdout.txt','p3-303-native-window/root-launch/stderr.txt')
files={}
for name in names:
    source=ROOT/'.cache'/name;body=source.read_bytes();target=base/name;target.parent.mkdir(parents=True,exist_ok=True)
    assert not target.exists();target.write_bytes(body);files[name]={'sha256':sha256(body).hexdigest(),'bytes':len(body)}
target=base/'archive-manifest.json';assert not target.exists()
target.write_text(json.dumps({'section':303,'kind':'root_actual_public_producers_and_original_helper_launch_outputs_not_additional_acceptance','files':files,'private_state_contents_or_hash_lists_copied':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'public_producers_and_original_launch_outputs':len(files),'private_files_copied':False}))
