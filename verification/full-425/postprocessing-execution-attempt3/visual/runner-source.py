"""Explicit postprocessing only; never tests, windows, image viewing or retries."""
from pathlib import Path
from hashlib import sha256
import sys,json,runpy
R=Path(__file__).resolve().parents[1];stage=sys.argv[1]
assert stage in ('archive','inventory','visual','seal')
base=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'));launch=base['read']('.cache/full425-launch-input-attempt3.json')
B=R/'.cache/full425-prepared/attempt-3';P=R/'.cache/full425-post-attempt3';A=R/'verification/full-425/execution-attempt3'
process=json.loads((B/'root-launch/controller-process.json').read_bytes())
assert process['status']=='completed' and type(process['actual_observed_exit'])is int
common=['--expected-parent-commit',launch['parent'],'--freeze-sha256',launch['freeze_sha256'],'--activation-sha256',launch['activation_sha256']]
def sha(p):return sha256(p.read_bytes()).hexdigest()
inventory=R/'.cache/full425-final-visual-inventory-attempt3.json'
visual=R/'verification/full-425/root-visual-review.json'
if stage=='archive':
    argv=[str(B/'archive_full425.py'),'--archive',*common]
elif stage=='inventory':
    registry=R/'verification/full-425/public-prior-visual-registry-v3.json'
    if not registry.exists():registry=R/'verification/full-425/public-prior-visual-registry-v2.json'
    argv=[str(P/'actual_png_visual_inventory.py'),'--archive',str(A),'--attempt','3','--archive-manifest-sha256',sha(A/'archive-manifest.json'),'--registry',str(registry),'--registry-sha256',sha(registry),'--output',str(inventory),'--actor','/root']
elif stage=='visual':
    argv=[str(P/'assemble_root_visual.py'),inventory.relative_to(R).as_posix()]
else:
    assert process['actual_observed_exit']==0
    argv=[str(P/'seal_summary425.py'),'--seal','--attempt','3',*common,'--archive-manifest-sha256',sha(A/'archive-manifest.json'),'--visual-sha256',sha(visual),'--review-helper-sha256',sha(B/'review_results425.py')]
out=f'verification/full-425/postprocessing-execution-attempt3/{stage}'
base['execute']([sys.executable,'-B','-X','utf8',*argv],out)
(R/out/'runner-source.py').write_bytes(Path(__file__).read_bytes())
print((R/out/'stdout.txt').read_text('utf8'))
