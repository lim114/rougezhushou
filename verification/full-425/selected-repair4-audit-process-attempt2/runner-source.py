"""Retain an actual read-only evidence auditor process and its exact executed source."""
from pathlib import Path
from hashlib import sha256
import runpy,sys
R=Path(__file__).resolve().parents[1];assert len(sys.argv)==2 and sys.argv[1]in ['baseline3','selected4']
stage=sys.argv[1];script=R/('.cache/audit425_baseline3.py'if stage=='baseline3'else'.cache/audit425_selected_repairs.py')
out='verification/full-425/'+('baseline3-readonly-audit-process'if stage=='baseline3'else'selected-repair4-audit-process-attempt2')
raw=script.read_bytes();base=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'))
try:base['execute']([sys.executable,'-B','-X','utf8',str(script)],out)
finally:
 assert script.read_bytes()==raw
 target=R/out/'auditor-source.py'
 assert not target.exists();target.write_bytes(raw)
 target=R/out/'runner-source.py'
 assert not target.exists();target.write_bytes(Path(__file__).read_bytes())
print('Actual auditor observed0 and its unchanged executed source preserved:',stage,sha256(raw).hexdigest())
