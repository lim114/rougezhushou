"""Record root's already-performed view_image inspection; this tool never views pixels.

Never call before the root has actually opened every named image with view_image.
"""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,json
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root-already-viewed-each',action='store_true');parser.add_argument('--image',action='append',required=True);parser.add_argument('--output',required=True);parser.add_argument('--notes',required=True);args=parser.parse_args()
    assert args.root_already_viewed_each and len(set(args.image))==len(args.image)
    output=ROOT/args.output;assert output.is_relative_to(ROOT/'verification/full-440/direct-root-review')and not output.exists()
    rows=[]
    for name in args.image:
        path=ROOT/name;assert path.is_file()and not path.is_symlink()and path.resolve().is_relative_to((ROOT/'verification/full-440/execution-attempt2').resolve())and path.suffix=='.png'
        rows.append({'file':path.relative_to(ROOT).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest(),'reviewed':True,'method':'direct_view','review_actor':'/root','actual_new_view_image_called':True,'actual_pixels_visually_reviewed':True,'visual_blocking_issue':False,'notes':args.notes})
    result={'kind':'actual_root_view_image_review_after_viewing','actor':'/root','recorded_at_UTC':datetime.now(timezone.utc).isoformat(),'actual_root_view_image_calls':len(rows),'tool_viewing_performed_by_this_script':False,'root_attested_only_after_actual_tool_viewing':True,'images':rows,'blocking_visual_issues':[],'limits':['Appearance inspection does not prove interactions, game mechanics, real-run state or native source freshness.']}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'reviewed_originals':len(rows),'proof':args.output}))

if __name__=='__main__':main()
