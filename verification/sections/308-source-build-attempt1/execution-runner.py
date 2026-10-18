from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/sections/308-source-build-attempt1';OUT.mkdir()
def pin(p):return{'bytes':p.stat().st_size,'sha256':sha256(p.read_bytes()).hexdigest()}
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
handoff=ROOT/'.cache/p3-308-backend/HANDOFF_REVIEW_READY.json';assert pin(handoff)['sha256']=='60512950b3158c953360addfc7c222dbf72ef8106818244ad5a6c87b1e59fd26'
h=json.loads(handoff.read_bytes())
for n,p in h['file_pins'].items():assert pin(handoff.parent/n)==p,n
manifest=ROOT/'research/p3-map-direct-ground-308/source-manifest.json';m=json.loads(manifest.read_bytes());assert pin(manifest)['sha256']==h['source_manifest']['sha256']
def bound():return{n:pin(ROOT/n)['sha256']for n in m['files']}
before=bound();live_before=pin(ROOT/'rouge/data/fixed-landmark-references.json')
argv=[sys.executable,'-B','-X','utf8','.cache/p3-308-backend/candidate/scripts/extend_direct_landmark_308.py','--output-dir','.cache/p3-308-root-build-attempt1']
started=datetime.now(timezone.utc).isoformat()
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);code=p.wait()
after=bound()
record={'section':308,'argv':argv,'actual_retained_popen_pid':p.pid,'actual_observed_exit':code,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'source_sha256_before':before,'source_sha256_after':after,'sources_unchanged':before==after,'live_prior107_unchanged':pin(ROOT/'rouge/data/fixed-landmark-references.json')==live_before,'passed':code==0 and before==after and pin(ROOT/'rouge/data/fixed-landmark-references.json')==live_before}
(OUT/'process.json').write_bytes(enc(record));(OUT/'process.exit').write_text(str(code)+'\n',encoding='ascii');(OUT/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in record.items()if not k.startswith('source_sha')},ensure_ascii=False))
if code:print((OUT/'stderr.txt').read_text('utf8'));raise SystemExit(code)
assert record['passed']
target=ROOT/'.cache/p3-308-root-build-attempt1';r=json.loads((target/'build-receipt.json').read_bytes());data=json.loads((target/'fixed-landmark-references.json').read_bytes());first=json.loads((ROOT/'verification/sections/308-preparation/first-frozen-comparison.json').read_bytes())
assert(r['new_requested_points'],r['new_accepted_points'],r['new_rejected_or_unknown_points'])==(67,16,51)
by_id={v['request_id']:v for v in first['comparisons']}
for c in r['new_agreement_comparisons']:
 f=by_id[c['request_id']];assert(c['observed_pixel'],c['independent_pixel'],c['agreement_px'],c['accepted_for_runtime'])==(f['original_A'],f['original_B'],f['unrounded_distance'],f['accepted'])
assert(len(data['references']),len(data['stages']),sum(len(v['points'])for v in data['references'].values()))==(14,25,123)
outputs={'data':pin(target/'fixed-landmark-references.json'),'build_receipt':pin(target/'build-receipt.json'),'builder':pin(handoff.parent/'candidate/scripts/extend_direct_landmark_308.py'),'manifest':pin(manifest),'first_comparison':pin(ROOT/'verification/sections/308-preparation/first-frozen-comparison.json')}
(ROOT/'.cache/308-actual-build-pins.json').write_bytes(enc(outputs));(OUT/'actual-generated-output-pins.json').write_bytes(enc(outputs));print(json.dumps(outputs,ensure_ascii=False))
