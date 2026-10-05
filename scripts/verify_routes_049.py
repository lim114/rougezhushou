"""Current regression and unchanged numeric/recognition core source guard."""
import hashlib,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    started=time.perf_counter();folder=ROOT/'.cache/routes-049';folder.mkdir(exist_ok=True)
    previous=read('FINAL_0.48_VERIFICATION.json');modules=[*read('MECHANISMS_0.48_VERIFICATION.json')['test_modules'],
        'tests.test_exploration_routes_049','tests.test_map_projection_049']
    allowed={'rouge/app.py','rouge/map_reporting.py','rouge/map_view.py','rouge/battle_view.py',
             'rouge/data/battle-map-projections.json','pyproject.toml'}
    changed={n for n,sha in previous['source_sha256'].items() if digest(n)!=sha}
    assert changed<=allowed,changed-allowed
    numeric=('rouge/damage.py','rouge/operator_engine.py','rouge/elemental_relics.py','rouge/timing.py',
             'rouge/reporting.py','rouge/estimate.py','rouge/relics.py','rouge/run_state.py','rouge/recognition.py')
    assert all(digest(n)==previous['source_sha256'][n] for n in numeric)
    backup=read('.cache/batch-049-before/manifest.json')
    assert all(digest('.cache/batch-049-before/'+n)==sha for n,sha in backup.items())
    attempt=1
    while (folder/f'all-tests-{attempt}.log').exists():attempt+=1
    log=folder/f'all-tests-{attempt}.log'
    with log.open('x',encoding='utf-8') as stream:
        tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert tests.wasSuccessful(),[(t.id(),error[-1600:]) for t,error in [*tests.errors,*tests.failures]]
    assert len(tests.skipped)==70
    source=set(previous['source_sha256'])|{'rouge/exploration_routes.py','rouge/map_view.py',
        'tests/test_exploration_routes_049.py','tests/test_map_projection_049.py','scripts/build_map_projections_049.py'}
    result={'version':'0.49.0','passed':True,'tests_run':tests.testsRun,
        'current_tests_passed':tests.testsRun-len(tests.skipped),'new_unit_tests':tests.testsRun-614,
        'historical_combat_tests_skipped':len(tests.skipped),'failures':len(tests.failures),'errors':len(tests.errors),
        'test_modules':modules,'test_log':str(log.relative_to(ROOT)),
        'test_log_sha256':digest(str(log.relative_to(ROOT))),
        'numeric_and_recognition_core_sources_unchanged':True,'numeric_public_replay_rerun':False,
        'previous_numeric_replay_receipt':'MECHANISMS_0.48_VERIFICATION.json',
        'previous_numeric_replay_receipt_sha256':digest('MECHANISMS_0.48_VERIFICATION.json'),
        'previous_exact_default_public_replays':732,'changed_existing_source_files':sorted(changed),
        'source_sha256':{n:digest(n) for n in sorted(source)},'game_actions':0,'chat_requests':0,
        'live_measurements':0,'new_recognition_speed_claim':False,'seconds':time.perf_counter()-started}
    (ROOT/'ROUTES_0.49_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','test_modules')}))


if __name__=='__main__':main()
