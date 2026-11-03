"""Root uses only after actually viewing every supplied PNG with view_image."""
import argparse,datetime,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--section',type=int,choices=range(121,126),required=True);p.add_argument('--scope',required=True);p.add_argument('--Root-actually-viewed-all-PNGs',action='store_true',required=True);a=p.parse_args()
n=a.section;B=Path('/workspace/.continuation');R=Path('/workspace/rougezhushou');window=B/f'section{n}-window-actual-v1';w=json.loads((window/'receipt.json').read_bytes());g=json.loads((B/f'section{n}-candidate-source-v1.json').read_bytes())
assert (B/f'section{n}-window-actual-v1.exit-code').read_bytes()==b'0\n' and w['passed'] is True and w['workflow_complete'] is True
actual=dict(sorted((q.relative_to(R).as_posix(),hashlib.sha256(q.read_bytes()).hexdigest()) for d in ('rouge','tests','scripts') for q in (R/d).rglob('*') if q.is_file() and q.suffix in ('.py','.json') and '__pycache__' not in q.parts))
assert actual==g['source_sha256'] and all(hashlib.sha256((R/q).read_bytes()).hexdigest()==v for q,v in g['source_additional_sha256'].items())
assert w['source_guard_sha256']==hashlib.sha256((B/f'section{n}-candidate-source-v1.json').read_bytes()).hexdigest()
assert w['source_before']==w['source_after']==g['source_sha256'] and w['source_drift']==[]
assert w['source_additional_before']==w['source_additional_after']==g['source_additional_sha256'] and w['source_count']==len(actual)
assert len(w['pngs'])==2
for v in w['pngs']:
 q=window/v['path'];assert q.stat().st_size==v['bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==v['sha256']
v={'kind':'ROOT_ACTUAL_BOUNDED_FEATURE_PNG_VIEW','section':n,'passed':True,'workflow_complete':True,'source_drift':[],'Root_actual_pixels_viewed':True,'pngs':w['pngs'],'actual_visible_scope':a.scope,'PNG_all_report_text_coverage_claimed':False,'native_windows_game_chat_verified':False,'recorded_at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (B/f'section{n}-visual-actual-v1.json').open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'Root_actual_PNG_view_saved':True,'section':n,'bounded_PNGs':2}),flush=True)
