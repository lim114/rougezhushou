from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/sections/310-preparation/root-source-rebuild-final';OUT.mkdir()
def bound():return{p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest()for p in(ROOT/'research/p3-boss-cycle-310').rglob('*')if p.is_file()and p.name not in('build-receipt.json','source-manifest.json')}
before=bound();argv=[sys.executable,'-B','-X','utf8','scripts/build_boss_cycle_reference_310.py'];start=datetime.now(timezone.utc).isoformat()
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
    p=subprocess.Popen(argv,cwd=ROOT,stdout=stdout,stderr=stderr,stdin=subprocess.DEVNULL);code=p.wait()
after=bound();result=json.loads((OUT/'stdout.txt').read_bytes())if code==0 else None
record={'section':310,'kind':'actual_complete_source_rebuild_with_intended_derived_outputs_not_product_acceptance','argv':argv,'retained_popen_pid':p.pid,'actual_exit':code,'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'source_sha256_before':before,'source_sha256_after':after,'frozen_sources_and_template_unchanged':before==after,'derived_outputs':result,'passed':code==0 and before==after}
(OUT/'process.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(OUT/'process.exit').write_text(str(code)+'\n',encoding='ascii');(OUT/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
assert record['passed'],(OUT/'stderr.txt').read_text('utf8',errors='replace')
for name,pin in result['outputs'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==pin['sha256']
print(json.dumps({'actual_exit':code,'frozen_sources_unchanged':True,'runtime_source_members':result['runtime_source_members'],'outputs_verified':list(result['outputs'])}))
