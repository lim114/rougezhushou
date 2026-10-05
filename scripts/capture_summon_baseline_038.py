"""Public-only source backup and before-change calculations for summon modules."""
import hashlib,json,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from capture_phase_baseline_036 import scenarios
from rouge.damage import calculate_damage

FILES=('rouge/operator_engine.py','rouge/relics.py','rouge/reporting.py',
       'rouge/operator_options.py','rouge/app.py','pyproject.toml','PROJECT_PROGRESS.md',
       'WORK_IN_PROGRESS.md','README.md','RELIC_VERIFICATION.json','RELIC_COVERAGE.md',
       'TARGET_ICON_VERIFICATION.json')

def module_scenarios():
    for elite,level in ((1,60),(2,39),(2,40),(2,70)):
        for stage in range(4):
            for skill in (1,2):
                for rank in ((1,7) if elite==1 else (1,7,10)):
                    for extra in ({},{'relic_ids':['rogue_6_relic_legacy_134']},
                                  {'run_config':{'squad':{'id':'rogue_6_band_6','effect_verified':True}}}):
                        s={'operator':'char_110_deepcl','skill':skill,'skill_rank':rank,
                           'elite':elite,'level':level,'summon_count':1,**extra}
                        if stage:s.update(module_id='uniequip_002_deepcl',module_level=stage)
                        yield s

def main():
    backup=ROOT/'.cache/batch-038-before'
    if '--resume' in sys.argv:
        manifest=json.loads((backup/'manifest.json').read_text(encoding='utf-8'))
        for name,checksum in manifest.items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==checksum,name
    else:
        backup.mkdir(parents=True,exist_ok=False);manifest={}
        for name in FILES:
            content=(ROOT/name).read_bytes();dst=backup/name;dst.parent.mkdir(parents=True,exist_ok=True)
            dst.write_bytes(content);manifest[name]=hashlib.sha256(content).hexdigest()
        (backup/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    folder=ROOT/'.cache/summon-038';folder.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter()
    for label,items in (('before-public-results',scenarios()),('before-module-results',module_scenarios())):
        if '--resume' in sys.argv and (folder/(label+'.json')).exists():continue
        rows=[]
        for i,s in enumerate(items,1):
            rows.append({'scenario':s,'result':calculate_damage(s)})
            if i%100==0:print(json.dumps({'baseline':label,'cases':i}),flush=True)
        (folder/(label+'.json')).write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
        print(json.dumps({'baseline':label,'total_cases':len(rows)}),flush=True)
    (folder/'baseline.json').write_text(json.dumps({'seconds':time.perf_counter()-started,
        'source_hashes':manifest},indent=2),encoding='utf-8')

if __name__=='__main__':main()
