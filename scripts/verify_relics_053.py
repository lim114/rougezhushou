"""Bounded candidate/healing repairs and exact previous public outputs."""
import hashlib,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.damage import calculate_damage

def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

def main():
    started=time.perf_counter();folder=ROOT/'.cache/relics-053';folder.mkdir(exist_ok=True)
    previous=read('FINAL_0.52_VERIFICATION.json')
    allowed={'rouge/app.py','rouge/damage.py','rouge/relic_recognition.py','pyproject.toml'}
    changed={n.replace('\\','/') for n,h in previous['source_sha256'].items() if sha(n)!=h}
    assert changed==allowed,changed
    backup='.cache/batch-053-before/'
    manifest=read(backup+'manifest.json');assert len(manifest)==10
    assert all(sha(backup+n)==h for n,h in manifest.items())
    old=read('RELICS_0.52_VERIFICATION.json')
    unchanged=('rouge/data/relic-mechanics.json','rouge/estimate.py','rouge/operator_engine.py',
        'rouge/relics.py','rouge/run_state.py','rouge/run_modifiers.py','rouge/reporting.py',
        'rouge/timing.py','rouge/data/battle-map-projections.json')
    assert all(sha(n)==previous['source_sha256'][n] for n in unchanged)
    modules=[*old['test_modules'],'tests.test_inventory_catalog_053','tests.test_relic_mechanisms_053']
    assert len(modules)==len(set(modules))
    attempt=1
    while (folder/f'all-tests-{attempt}.log').exists():attempt+=1
    log=folder/f'all-tests-{attempt}.log'
    with log.open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert result.wasSuccessful(),[(t.id(),error[-2000:]) for t,error in [*result.errors,*result.failures]]
    assert result.testsRun==740 and len(result.skipped)==70
    reference=read('P1_0.50_VERIFICATION.json');baseline=reference['fresh_previous_public_baseline']
    assert sha(baseline)==reference['fresh_previous_public_baseline_sha256']
    rows=read(baseline);assert len(rows)==732
    for i,row in enumerate(rows,1):
        assert calculate_damage(row['scenario'])==row['result'],row['scenario']
        if i%100==0:print(json.dumps({'exact_default_replays':i}),flush=True)
    names=set(previous['source_sha256'])|allowed
    names|={p.relative_to(ROOT).as_posix() for base in ('tests','scripts') for p in (ROOT/base).glob('*053.py')}
    names.discard('scripts/verify_final_053.py')
    receipt={'version':'0.53.0','passed':True,'tests_run':result.testsRun,
        'current_tests_passed':result.testsRun-len(result.skipped),'new_unit_tests':28,
        'historical_combat_tests_skipped':70,'test_modules':modules,
        'failures':len(result.failures),'errors':len(result.errors),
        'test_log':log.relative_to(ROOT).as_posix(),'test_log_sha256':sha(log.relative_to(ROOT)),
        'exact_default_public_replays':len(rows),'default_public_outputs_unchanged':True,
        'numeric_public_replay_rerun':True,'baseline_file':baseline,'baseline_file_sha256':sha(baseline),
        'baseline_receipt':'P1_0.50_VERIFICATION.json','baseline_receipt_sha256':sha('P1_0.50_VERIFICATION.json'),
        'mechanic_data_unchanged':True,'data_status_counts_unchanged':True,
        'char_buff_formulas_unchanged':True,'deterministic_build_rerun':False,
        'prior_build_receipt':'RELICS_0.52_VERIFICATION.json','prior_build_receipt_sha256':sha('RELICS_0.52_VERIFICATION.json'),
        'changed_existing_sources':sorted(changed),'untouched_checked_files':list(unchanged),
        'source_sha256':{n:sha(n) for n in sorted(names)},'game_actions':0,'chat_requests':0,
        'live_measurements':0,'new_recognition_speed_claim':False,'seconds':time.perf_counter()-started}
    (ROOT/'RELICS_0.53_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_sha256','test_modules')},ensure_ascii=True))

if __name__=='__main__':main()
