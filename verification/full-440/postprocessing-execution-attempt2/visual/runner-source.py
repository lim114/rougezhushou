"""Explicit postprocessing only; never tests, windows, image viewing or retries."""
from pathlib import Path
from hashlib import sha256
import sys,json,runpy
R=Path(__file__).resolve().parents[1];stage=sys.argv[1]
assert stage in ('archive','inventory','visual','seal')
base=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'));launch=base['read']('.cache/full440-launch-input-attempt2.json')
B=R/'.cache/full440-prepared/attempt-2';P=R/'.cache/full440-post-attempt2';A=R/'verification/full-440/execution-attempt2'
process=json.loads((B/'root-launch/controller-process.json').read_bytes())
assert process['status']=='completed' and type(process['actual_observed_exit'])is int
common=['--expected-parent-commit',launch['parent'],'--freeze-sha256',launch['freeze_sha256'],'--activation-sha256',launch['activation_sha256']]
def sha(p):return sha256(p.read_bytes()).hexdigest()
inventory=R/'.cache/full440-final-visual-inventory-attempt2.json'
visual=R/'verification/full-440/root-visual-review.json'
if stage=='archive':
    argv=[str(B/'archive_full440.py'),'--archive',*common]
elif stage=='inventory':
    registry=R/'verification/full-440/public-prior-visual-registry-v2.json'
    if not registry.exists():registry=R/'verification/full-440/public-prior-visual-registry-v2.json'
    argv=[str(P/'actual_png_visual_inventory.py'),'--archive',str(A),'--attempt','2','--archive-manifest-sha256',sha(A/'archive-manifest.json'),'--registry',str(registry),'--registry-sha256',sha(registry),'--output',str(inventory),'--actor','/root']
elif stage=='visual':
    argv=[str(P/'assemble_root_visual.py'),inventory.relative_to(R).as_posix()]
else:
    assert process['actual_observed_exit']==0
    argv=[str(P/'seal_summary440.py'),'--seal','--attempt','2',*common,'--archive-manifest-sha256',sha(A/'archive-manifest.json'),'--visual-sha256',sha(visual),'--review-helper-sha256',sha(B/'review_results440.py')]
out=f'verification/full-440/postprocessing-execution-attempt2/{stage}'
public_tools=R/'verification/full-440/postprocessing-tools-attempt2';public_tools.mkdir(exist_ok=True)
for tool in P.glob('*.py'):
    copy=public_tools/tool.name
    if copy.exists():assert copy.read_bytes()==tool.read_bytes(),'Never rewrite archived post-tool source'
    else:copy.write_bytes(tool.read_bytes())
base['execute']([sys.executable,'-B','-X','utf8',*argv],out)
(R/out/'runner-source.py').write_bytes(Path(__file__).read_bytes())
print((R/out/'stdout.txt').read_text('utf8'))
