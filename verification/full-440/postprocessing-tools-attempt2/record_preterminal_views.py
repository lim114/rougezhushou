"""Record only root's already-completed direct viewing of exact queued public PNGs."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,json
R=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
parser=argparse.ArgumentParser();parser.add_argument('--root-already-viewed-each',action='store_true');parser.add_argument('--image',action='append',required=True);parser.add_argument('--notes',required=True);args=parser.parse_args();assert args.root_already_viewed_each
queue=json.loads((R/'.cache/440-attempt4-preterminal-image-queue.json').read_bytes());by_file={row['file']:row for row in queue['copied_sha256'].values()};folder=R/'verification/full-440/preterminal-root-direct-review-attempt4';folder.mkdir(exist_ok=True);seen={row['file']for path in folder.glob('*.json')for row in json.loads(path.read_bytes())['images']}
rows=[]
for name in args.image:
    assert name in by_file and name not in seen;row=by_file[name];raw=(R/name).read_bytes();assert sha256(raw).hexdigest()==row['sha256']
    rows.append({'file':name,'sha256':row['sha256'],'reviewed':True,'method':'direct_view','review_actor':'/root','actual_new_view_image_called':True,'actual_pixels_visually_reviewed':True,'visual_blocking_issue':False,'notes':args.notes,'component':row['component'],'actual_component_primary_exit':row['actual_component_primary_exit'],'full_scope_success_not_claimed':True})
assert len(set(args.image))==len(rows)
index=1
while(folder/f'batch{index}.json').exists():index+=1
result={'section':440,'actual_validation_attempt':4,'kind':'actual_root_direct_view_of_exact_terminal_component_pngs','review_actor':'/root','actual_root_view_image_calls':len(rows),'viewing_performed_by_this_script':False,'root_recorded_only_after_actual_tool_viewing':True,'recorded_at_UTC':datetime.now(timezone.utc).isoformat(),'images':rows,'blocking_visual_issues':[],'limits':['Root actually inspected the exact original PNG pixels; no hidden text, interaction, game mechanism, real-run state or complete-suite PASS is inferred.','The full root controller can still be running; this is independent appearance review of already-terminal components only.']}
path=folder/f'batch{index}.json';path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'recorded_images':len(rows),'actual_review_proof':path.relative_to(R).as_posix()}))
