"""Root-run: archive actual direct visual observations, then run strict summary gate."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def load(n):return json.loads((ROOT/n).read_bytes())
def digest(p):return sha256(p.read_bytes()).hexdigest()
obs=load('.cache/p3-full305-root-visual-complete-observations.json')
inventory=load('.cache/p3-full305-closeout-readback-attempt2.json')['PNG_inventory']
assert len(inventory)==109 and len(obs['queue'])==100
observed={}
for batch in obs['batches']:
 for i in batch['indices']:
  assert i not in observed and batch['detail']=='high'
  observed[i]=batch['observation']
assert set(observed)==set(range(100))
representatives={r['sha256']:(i,r) for i,r in enumerate(obs['queue'])}
assert len(representatives)==100
images=[]
for row in inventory:
 p=Path(row['path']);assert p.is_file() and digest(p)==row['sha256'] and p.stat().st_size==row['bytes']
 i,rep=representatives[row['sha256']];rp=Path(rep['path']);assert digest(rp)==row['sha256']
 images.append({'file':p.relative_to(ROOT).as_posix(),'sha256':row['sha256'],'reviewed':True,
 'method':'direct_view' if p==rp else 'same_byte_reuse','representative_file':rp.relative_to(ROOT).as_posix(),
 'representative_sha256':row['sha256'],'detail':'high','observation':observed[i]})
review={'section':305,'reviewer':'root','actual_validation_attempt':2,'all_reviewed':True,
 'source_freeze_sha256':'4e2528deb25cbb166b74d74db8e0c3a6212ec6095a6d7b441bf62a911ade8086',
 'archive_manifest_sha256':'9d5eb91a5fd4415f7137108e4a2461cfb5d7e1d5546d466b048ff6f7e6b90c58',
 'at_utc':datetime.now(timezone.utc).isoformat(),'images':images,'actual_direct_view_batches':obs['batches'],
 'scope':'100 unique PNG byte contents directly displayed with view_image/high; nine exact same-byte files reuse only this execution representatives. Tool may resize. Representative images do not prove every unpictured row, original private/game/chat execution or pixel-perfect text at original resolution.'}
dest=ROOT/'verification/full-305/root-second-visual-review.json'
with dest.open('x',encoding='utf8') as f:f.write(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
source=ROOT/'.cache/p3-full305-summary-draft/build_summary305_attempt2.py'
text=source.read_text(encoding='utf8')
assert "'usage_wrap_up_triggered_below5_percent':True" in text
text=text.replace("'usage_wrap_up_triggered_below5_percent':True", "'usage_wrap_up_triggered_below5_percent':True,'below5_trigger_is_historical_not_current_usage':True,'current_wrap_up_threshold_percent':15,'user_requested_pause_after_section':305,'current_remaining_usage_not_inferred':True")
current=source.with_name('build_summary305_attempt2_current_policy.py')
with current.open('x',encoding='utf8') as f:f.write(text)
out=ROOT/'verification/full-305/summary-invocation';out.mkdir()
(out/'execution-summary.py').write_bytes(current.read_bytes())
(out/'execution-root-visual-and-summary.py').write_bytes(Path(__file__).read_bytes())
cmd=[sys.executable,'-B','-X','utf8',str(current),'--archive-sha256',review['archive_manifest_sha256'],'--visual-review',dest.relative_to(ROOT).as_posix(),'--apply']
started=datetime.now(timezone.utc).isoformat()
with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
 p=subprocess.Popen(cmd,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr)
 code=p.wait()
record={'section':305,'actual_retained_popen_pid':p.pid,'actual_observed_exit':code,'start_utc':started,'finish_utc':datetime.now(timezone.utc).isoformat(),'argv':cmd,'summary_producer_sha256':digest(current),'visual_review_sha256':digest(dest),'summary_sha256':digest(ROOT/'verification/full-305/summary.json') if (ROOT/'verification/full-305/summary.json').is_file() else None}
(out/'process.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(out/'process.exit').write_text(str(code)+'\n',encoding='ascii')
print(json.dumps(record,ensure_ascii=False));print((out/'stdout.log').read_text(encoding='utf8'));print((out/'stderr.log').read_text(encoding='utf8'))
raise SystemExit(code)
