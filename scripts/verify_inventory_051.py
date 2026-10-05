"""Current inventory/map regression; untouched numeric sources inherit 0.50."""
import hashlib,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    started=time.perf_counter();folder=ROOT/'.cache/inventory-051';folder.mkdir(exist_ok=True)
    previous=read('FINAL_0.50_VERIFICATION.json')
    allowed={'rouge/app.py','rouge/run_state.py','rouge/data/battle-map-projections.json','pyproject.toml'}
    changed={n.replace('\\','/') for n,sha in previous['source_sha256'].items() if digest(n)!=sha}
    assert changed<=allowed,changed-allowed
    numeric=('rouge/damage.py','rouge/operator_engine.py','rouge/elemental_relics.py','rouge/timing.py',
        'rouge/reporting.py','rouge/estimate.py','rouge/relics.py','rouge/data/relic-mechanics.json')
    recognition=('rouge/recognition.py','rouge/run_recognition.py','rouge/relic_recognition.py')
    assert all(digest(n)==previous['source_sha256'][n] for n in (*numeric,*recognition))
    backup=read('.cache/batch-051-before/manifest.json')
    assert len(backup)==8 and all(digest('.cache/batch-051-before/'+n)==sha for n,sha in backup.items())
    modules=[*read('P1_0.50_VERIFICATION.json')['test_modules'],'tests.test_inventory_snapshot_051']
    if (ROOT/'tests/test_map_projection_051.py').exists():modules.append('tests.test_map_projection_051')
    attempt=1
    while (folder/f'all-tests-{attempt}.log').exists():attempt+=1
    log=folder/f'all-tests-{attempt}.log'
    with log.open('x',encoding='utf-8') as stream:
        tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert tests.wasSuccessful(),[(t.id(),error[-1800:]) for t,error in [*tests.errors,*tests.failures]]
    assert len(tests.skipped)==70
    names={n.replace('\\','/') for n in previous['source_sha256']}|allowed
    names|={p.relative_to(ROOT).as_posix() for base in ('scripts','tests') for p in (ROOT/base).glob('*051.py')}
    result={'version':'0.51.0','passed':True,'tests_run':tests.testsRun,
        'current_tests_passed':tests.testsRun-len(tests.skipped),'new_unit_tests':tests.testsRun-662,
        'historical_combat_tests_skipped':len(tests.skipped),'failures':len(tests.failures),'errors':len(tests.errors),
        'test_modules':modules,'test_log':log.relative_to(ROOT).as_posix(),'test_log_sha256':digest(log.relative_to(ROOT)),
        'numeric_sources_unchanged':list(numeric),'recognition_sources_unchanged':list(recognition),
        'numeric_public_replay_rerun':False,'previous_numeric_replay_receipt':'P1_0.50_VERIFICATION.json',
        'previous_numeric_replay_receipt_sha256':digest('P1_0.50_VERIFICATION.json'),
        'inherited_exact_default_public_replays':732,'changed_existing_source_files':sorted(changed),
        'source_sha256':{n:digest(n) for n in sorted(names)},'game_actions':0,'chat_requests':0,
        'live_measurements':0,'new_recognition_speed_claim':False,'seconds':time.perf_counter()-started}
    (ROOT/'INVENTORY_0.51_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','test_modules')},ensure_ascii=False))


if __name__=='__main__':main()
