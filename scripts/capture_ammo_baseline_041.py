"""Preserve public preview files and old calculation outputs before this batch."""
import hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from capture_phase_baseline_036 import scenarios
from rouge.damage import calculate_damage
FILES=('rouge/app.py','rouge/relics.py','rouge/relic_events.py','rouge/reporting.py',
       'rouge/damage.py','rouge/operator_engine.py','rouge/data/relic-mechanics.json',
       'tests/test_relic_extension.py','pyproject.toml','PROJECT_PROGRESS.md','WORK_IN_PROGRESS.md',
       'README.md','RELIC_VERIFICATION.json','RELIC_COVERAGE.md','TARGET_ICON_VERIFICATION.json')


def main():
    backup=ROOT/'.cache/batch-041-before';backup.mkdir(parents=True,exist_ok=False);manifest={}
    for name in FILES:
        body=(ROOT/name).read_bytes();dst=backup/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(body)
        manifest[name]=hashlib.sha256(body).hexdigest()
    (backup/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    folder=ROOT/'.cache/ammo-041';folder.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter();rows=[]
    for i,s in enumerate(scenarios(),1):
        rows.append({'scenario':s,'result':calculate_damage(s)})
        if i%100==0:print(json.dumps({'public_baseline_cases':i}),flush=True)
    (folder/'before-public-results.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
    (folder/'baseline.json').write_text(json.dumps({'cases':len(rows),'seconds':time.perf_counter()-start,
        'source_hashes':manifest},indent=2),encoding='utf-8')
    print(json.dumps({'public_cases':len(rows)}),flush=True)
    from rouge.catalog import catalog
    rows=[]
    for op,p in catalog()['operators'].items():
        for skill,entry in enumerate(p['skills'],1):
            ranks=range(1,11) if entry['levels'][-1]['duration_type']=='AMMO' else (10,)
            for rank in ranks:
                for mode in ('frames','continuous'):
                    for ids in (['rogue_6_relic_legacy_139'],['rogue_6_relic_legacy_140'],['rogue_6_relic_legacy_139','rogue_6_relic_legacy_140']):
                        sc={'operator':op,'skill':skill,'skill_rank':rank,'timing_mode':mode,'relic_ids':ids}
                        rows.append({'scenario':sc,'result':calculate_damage(sc)})
    (folder/'before-book-results.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'book_baseline_cases':len(rows)}),flush=True)

if __name__=='__main__':main()
