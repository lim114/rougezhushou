from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'verification/sections/302-preparation/root-final-producers'
base.mkdir(parents=True,exist_ok=True)
files={}
for relative in ('prepare_original_302.py','restart_window_302.py','focus_window_302.py','archive_root_302.py',
                 'p3-302-native-window/root-launch/stdout.txt','p3-302-native-window/root-launch/stderr.txt'):
    source=ROOT/'.cache'/relative;raw=source.read_bytes()
    dest=base/relative;dest.parent.mkdir(parents=True,exist_ok=True)
    assert not dest.exists();dest.write_bytes(raw)
    files[relative]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
(base/'archive-manifest.json').write_text(json.dumps({'section':302,'kind':'root_actual_public_producers_and_original_launch_output_not_additional_acceptance','files':files,'private_content_or_hash_lists':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'archived_public_files':len(files),'private_state_copied':False}))
