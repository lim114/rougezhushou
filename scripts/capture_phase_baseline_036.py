"""Save public calculations and source hashes before the phase-flow change."""
import hashlib,json,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.catalog import catalog
from rouge.damage import calculate_damage

FILES=('rouge/damage.py','rouge/app.py','pyproject.toml','PROJECT_PROGRESS.md',
       'WORK_IN_PROGRESS.md','README.md')


def scenarios():
    wines=('rogue_6_relic_legacy_95','rogue_6_relic_legacy_96','rogue_6_relic_legacy_97')
    for op,p in catalog()['operators'].items():
        for skill in range(1,len(p['skills'])+1):
            for mode in ('frames','continuous'):
                s={'operator':op,'skill':skill,'timing_mode':mode}
                yield s
                for wine in wines:yield {**s,'relic_ids':[wine]}
    examples=[('mechanist',1),('char_133_mm',1),('char_1044_hsgma2',1),
              ('char_4182_oblvns',3),('char_1042_phatm2',3),('char_4107_vrdant',2)]
    for op,skill in examples:
        s={'operator':op,'skill':skill,'relic_ids':[wines[0]],
           'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':'enemy_1093_ccsbr','level':0},
           'run_config':{'difficulty':{'value':9}}}
        for extra in ({'window_seconds':.1}, {'timing':{'target_windows':[]}},
                      {'timing':{'initial_movement_windows':[[0,10]],'sp_lockout_extra_seconds':2}},
                      {'relic_ids':[wines[0],wines[2]]},
                      {'relic_ids':[wines[0],'rogue_6_start_4','rogue_6_relic_fight_25']},
                      {'char_buff_ids':['rogue_6_from_relic_9']}):
            yield {**s,**extra}


def main():
    backup=ROOT/'.cache/batch-036-before';backup.mkdir(parents=True,exist_ok=False)
    manifest={}
    for name in FILES:
        src=ROOT/name;dst=backup/name;dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_bytes(src.read_bytes());manifest[name]=hashlib.sha256(src.read_bytes()).hexdigest()
    (backup/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    folder=ROOT/'.cache/phase-036';folder.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter();rows=[]
    for i,s in enumerate(scenarios(),1):
        rows.append({'scenario':s,'result':calculate_damage(s)})
        if i%100==0:print(json.dumps({'public_cases':i}),flush=True)
    (folder/'before-public-results.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
    (folder/'baseline.json').write_text(json.dumps({'cases':len(rows),'seconds':time.perf_counter()-started,
        'source_hashes':manifest},indent=2),encoding='utf-8')
    print(json.dumps({'cases':len(rows),'elapsed_seconds':time.perf_counter()-started}),flush=True)


if __name__=='__main__':main()
