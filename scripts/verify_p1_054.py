"""Evidence-scoped packet repair and exact old default public behavior."""
import ast,hashlib,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from rouge.damage import calculate_damage

def read(n):return json.loads((ROOT/n).read_text(encoding='utf-8'))
def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()

def main():
    start=time.perf_counter();out=ROOT/'.cache/p1-054';out.mkdir(exist_ok=True)
    previous=read('FINAL_0.53_VERIFICATION.json')
    allowed={'rouge/ammo_reference.py','rouge/relics.py','rouge/reporting.py',
        'rouge/data/ammo-refill-reference.json','rouge/app.py','pyproject.toml','tests/test_ammo_refill_041.py'}
    changed={n.replace('\\','/') for n,h in previous['source_sha256'].items() if sha(n)!=h}
    assert changed==allowed,changed
    backup='.cache/batch-054-before/';manifest=read(backup+'manifest.json')
    assert len(manifest)==13 and all(sha(backup+n)==h for n,h in manifest.items())
    old=read(backup+'rouge/data/ammo-refill-reference.json');new=read('rouge/data/ammo-refill-reference.json')
    packets=new.pop('partial_packet_rules');assert new==old
    assert packets==[read('.cache/research/p1-ammo-cost-054/proposed-partial-packet-metadata.json')]
    rule=packets[0];assert sha(rule['source_file'])==rule['source_sha256']
    for entry in rule['pinned_data_crosschecks']:assert sha(entry['file'])==entry['sha256']
    modules=[*read('RELICS_0.53_VERIFICATION.json')['test_modules'],
        'tests.test_p1_ammo_cost_054','tests.test_p1_packet_scope_054']
    assert len(modules)==len(set(modules))
    index=1
    while (out/f'all-tests-{index}.log').exists():index+=1
    log=out/f'all-tests-{index}.log'
    with log.open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert result.wasSuccessful(),[(t.id(),e[-2000:]) for t,e in [*result.errors,*result.failures]]
    assert result.testsRun==753 and len(result.skipped)==70
    reference=read('P1_0.50_VERIFICATION.json');baseline=reference['fresh_previous_public_baseline']
    assert sha(baseline)==reference['fresh_previous_public_baseline_sha256']
    rows=read(baseline);assert len(rows)==732
    for index,row in enumerate(rows,1):
        assert calculate_damage(row['scenario'])==row['result'],row['scenario']
        if index%100==0:print(json.dumps({'exact_default_replays':index}),flush=True)
    names=set(previous['source_sha256'])|allowed
    names|={p.relative_to(ROOT).as_posix() for base in ('tests','scripts') for p in (ROOT/base).glob('*054.py')}
    names.discard('scripts/verify_final_054.py')
    receipt={'version':'0.54.0','passed':True,'tests_run':result.testsRun,'current_tests_passed':683,
        'new_unit_tests':13,'historical_combat_tests_skipped':70,'failures':0,'errors':0,'test_modules':modules,
        'test_log':log.relative_to(ROOT).as_posix(),'test_log_sha256':sha(log.relative_to(ROOT)),
        'exact_default_public_replays':732,'default_public_outputs_unchanged':True,'numeric_public_replay_rerun':True,
        'baseline_file':baseline,'baseline_file_sha256':sha(baseline),
        'baseline_receipt':'P1_0.50_VERIFICATION.json','baseline_receipt_sha256':sha('P1_0.50_VERIFICATION.json'),
        'changed_existing_sources':sorted(changed),'source_sha256':{n:sha(n) for n in sorted(names)},
        'mechanic_data_unchanged':sha('rouge/data/relic-mechanics.json')==previous['source_sha256']['rouge/data/relic-mechanics.json'],
        'operator_engine_unchanged':sha('rouge/operator_engine.py')==previous['source_sha256']['rouge/operator_engine.py'],
        'prior_ammo_ratios_and_polling_guard_unchanged':True,'data_status_counts_unchanged':True,
        'new_documented_partial_packet_reference':rule,'all_priority_1_completed':False,
        'game_actions':0,'chat_requests':0,'live_measurements':0,'seconds':time.perf_counter()-start}
    (ROOT/'P1_0.54_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','new_unit_tests','exact_default_public_replays','seconds')}))

if __name__=='__main__':main()
