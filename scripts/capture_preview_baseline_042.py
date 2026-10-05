"""Save public files and fresh 0.41 outputs before adding enemy skill references."""
import hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from capture_phase_baseline_036 import scenarios
from rouge.damage import calculate_damage
FILES=('rouge/app.py','rouge/battle_preview.py','rouge/battle_view.py','rouge/data/battle-previews.json',
    'pyproject.toml','PROJECT_PROGRESS.md','WORK_IN_PROGRESS.md','README.md')

def main():
    backup=ROOT/'.cache/batch-042-before';backup.mkdir(parents=True,exist_ok=False);manifest={}
    for name in FILES:
        body=(ROOT/name).read_bytes();dst=backup/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(body)
        manifest[name]=hashlib.sha256(body).hexdigest()
    (backup/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    folder=ROOT/'.cache/preview-042';folder.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter();rows=[]
    for i,s in enumerate(scenarios(),1):
        rows.append({'scenario':s,'result':calculate_damage(s)})
        if i%100==0:print(json.dumps({'public_baseline_cases':i}),flush=True)
    (folder/'before-public-results.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
    (folder/'baseline.json').write_text(json.dumps({'cases':len(rows),'seconds':time.perf_counter()-start,
        'source_hashes':manifest},indent=2),encoding='utf-8')
    print(json.dumps({'public_cases':len(rows)}),flush=True)

if __name__=='__main__':main()
