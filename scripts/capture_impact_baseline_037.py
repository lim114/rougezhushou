"""Public-only backup and before-change calculations for fixed impact delay."""
import hashlib,json,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from capture_phase_baseline_036 import scenarios
from rouge.damage import calculate_damage

FILES=('rouge/timing.py','rouge/reporting.py','rouge/app.py','pyproject.toml','PROJECT_PROGRESS.md',
       'WORK_IN_PROGRESS.md','README.md','tests/test_timing.py','tests/test_relics.py',
       'RELIC_VERIFICATION.json','RELIC_COVERAGE.md','TARGET_ICON_VERIFICATION.json')


def main():
    backup=ROOT/'.cache/batch-037-before';backup.mkdir(parents=True,exist_ok=False)
    manifest={}
    for name in FILES:
        src=ROOT/name;dst=backup/name;dst.parent.mkdir(parents=True,exist_ok=True)
        content=src.read_bytes();dst.write_bytes(content)
        manifest[name]=hashlib.sha256(content).hexdigest()
    (backup/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    folder=ROOT/'.cache/impact-037';folder.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter();rows=[]
    for i,s in enumerate(scenarios(),1):
        rows.append({'scenario':s,'result':calculate_damage(s)})
        if i%100==0:print(json.dumps({'public_baseline_cases':i}),flush=True)
    (folder/'before-public-results.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
    (folder/'baseline.json').write_text(json.dumps({'cases':len(rows),
        'seconds':time.perf_counter()-started,'source_hashes':manifest},indent=2),encoding='utf-8')
    print(json.dumps({'cases':len(rows),'seconds':time.perf_counter()-started}),flush=True)


if __name__=='__main__':main()
