"""Root current source+CORE guard, after an actual per-section cloud publication."""
import argparse,hashlib,json,subprocess,datetime
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--section',type=int,required=True);p.add_argument('--out',required=True);a=p.parse_args()
R=Path('/workspace/rougezhushou');B=Path('/workspace/.continuation');n=a.section;out=Path(a.out);assert B in out.resolve().parents and not out.exists()
cp=json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_text());assert cp['completed_sections']==n-1 and cp['next_section']==n
branch=subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert branch=='codex/p2-development'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=R,text=True).strip()
pub=B/f'section{n-1:03d}-publication-v1.json';proof=json.loads(pub.read_text());assert proof['local_HEAD']==proof['remote_HEAD']==head and proof['clean'] and proof['push_primary_exit']==0
source=dict(sorted((f.relative_to(R).as_posix(),hashlib.sha256(f.read_bytes()).hexdigest())for d in ['rouge','tests','scripts']for f in (R/d).rglob('*')if f.is_file()and f.suffix in('.py','.json')and '__pycache__'not in f.parts))
g={'kind':'ROOT_ACTUAL_CURRENT_SECTION_SOURCE_GUARD','section':n,'root_prior_HEAD':head,'branch':branch,'recorded_at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':source,'source_additional_sha256':{'CORE_0.70_VERIFICATION.json':hashlib.sha256((R/'CORE_0.70_VERIFICATION.json').read_bytes()).hexdigest()},'prior_actual_cloud_publication':str(pub),'changed_paths':[],'product_applied':False,'passed':False,'candidate_completed':False}
with out.open('x')as h:json.dump(g,h,ensure_ascii=False,indent=2);h.write('\n')
print(json.dumps({'section':n,'actual_prior_HEAD':head,'actual_source_files':len(source),'runtime_pass':False}))
