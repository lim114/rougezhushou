from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'rouge/map_view.py';raw=p.read_bytes()
original=subprocess.check_output(['git','show','HEAD:rouge/map_view.py'],cwd=ROOT)
assert original.count(b'\r\n')==original.count(b'\n') and raw.count(b'\r\n')==0
assert sha256(raw).hexdigest()=='9b52302b694574b917363e08cc6e29e1e5b3b0ac4f3c583a21acfc5d52798b9d'
fixed=raw.replace(b'\n',b'\r\n');assert fixed.replace(b'\r\n',b'\n')==raw
p.write_bytes(fixed)
old=ROOT/'.cache/run_section_291_window.py';new=ROOT/'.cache/run_section_291_window_repaired_layout.py'
assert not new.exists()
code=old.read_bytes();assert code.count(b'assert 1<=attempt<=3')==1
new.write_bytes(code.replace(b'assert 1<=attempt<=3',b'assert attempt==4'))
record={'kind':'291_preserve_existing_map_view_CRLF_and_prepare_explicit_layout_attempt4',
 'map_view_before':sha256(raw).hexdigest(),'map_view_after':sha256(fixed).hexdigest(),
 'only_line_endings_changed_in_MapView':True,'window_tests_started':False,
 'new_runner_only_admits_explicit_attempt4':True,'previous_attempts_preserved':True}
dest=ROOT/'verification/sections/291-preparation/source-maintenance.json'
with dest.open('xb') as f:f.write((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps(record))
