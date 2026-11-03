"""Seal a complete visual path inventory from real prior/direct review proofs only."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import json,sys
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
inventory=ROOT/sys.argv[1];output=ROOT/'verification/full-440/root-visual-review.json';assert not output.exists();data=json.loads(inventory.read_bytes());assert data['section']==440 and data['actual_validation_attempt']==1
views={}
for path in sorted((ROOT/'verification/full-440/direct-root-review').glob('*.json')):
    proof=json.loads(path.read_bytes());assert proof['actor']=='/root'and not proof['blocking_visual_issues']and proof['tool_viewing_performed_by_this_script']is False
    for row in proof['images']:
        original=ROOT/row['file'];assert sha256(original.read_bytes()).hexdigest()==row['sha256']and row['actual_new_view_image_called']and row['actual_pixels_visually_reviewed']and row['reviewed']and row['visual_blocking_issue']is False
        views[row['file']]={'row':row,'receipt':path.relative_to(ROOT).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()}
for group in data['needs_actual_view']:
    representative=group['representative_file'];assert representative in views,representative;view=views[representative];assert view['row']['sha256']==group['sha256']
    for row in data['images']:
        if row['file']not in group['all_same_sha_files']:continue
        assert row['sha256']==group['sha256']and row['reviewed']is False
        direct=row['file']==representative
        row.update(reviewed=True,method='direct_view'if direct else'same_byte_reuse',reviewed_file=representative,review_receipt=view['receipt'],review_receipt_sha256=view['sha256'],review_actor='/root',registry_proof=None,status='actual_current_original_viewed'if direct else'exact_full_bytes_reused_from_current_direct_view',actual_new_view_image_called=direct,actual_pixels_visually_reviewed=direct,visual_blocking_issue=False)
assert all(row['reviewed']for row in data['images'])
data.update(all_reviewed=True,pending_actual_view_rows=0,needs_actual_view=[],needs_actual_view_unique_sha256=0,method_counts=dict(Counter(row['method']for row in data['images'])),actual_root_direct_view_image_calls=len(views),blocking_visual_issues=[],all_images_directly_viewed_by_root_claimed=False)
output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'images':len(data['images']),'actual_root_direct_views':len(views),'methods':data['method_counts'],'visual_sha256':sha256(output.read_bytes()).hexdigest()}))
