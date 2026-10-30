"""Retain the actual summary-sealer process, executing an immutable public source copy."""
from pathlib import Path
from hashlib import sha256
import runpy,sys
R=Path(__file__).resolve().parents[1];assert len(sys.argv)==2 and int(sys.argv[1])>=1
n=int(sys.argv[1]);source=R/'.cache/seal425_composite.py';raw=source.read_bytes();public=R/f'verification/full-425/composite-sealer-source-attempt{n}.py';assert not public.exists();public.write_bytes(raw)
base=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'));out=f'verification/full-425/composite-seal-process-attempt{n}'
base['execute']([sys.executable,'-B','-X','utf8',str(public)],out)
assert source.read_bytes()==raw==public.read_bytes();target=R/out/'runner-source.py';assert not target.exists();target.write_bytes(Path(__file__).read_bytes())
print('Actual public-source composite sealer observed0:',sha256(raw).hexdigest())
