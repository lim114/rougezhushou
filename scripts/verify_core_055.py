"""Explicit maintained regression suite, with an immutable per-run receipt."""
import hashlib,json,sys,time,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started=time.perf_counter()
    old=json.loads((ROOT/'READING_0.54_VERIFICATION.json').read_text(encoding='utf-8'))
    modules=list(old['test_modules'])
    for name in ('test_counter_semantics_054','test_deployment_native_054',
        'test_local_counters_054','test_held_footer_054','test_recipient_integration_054',
        'test_recipient_recognition_054','test_gray_counters_055',
        'test_recipient_live_055','test_ammo_counter_055','test_deployment_clock_audit_055',
        'test_name_recheck_055','test_recognition_crop_cache_055',
        'test_owned_popup_context_055','test_origin_discovery_055'):
        module='tests.'+name
        if module not in modules:modules.append(module)
    assert len(modules)==len(set(modules))
    directory=ROOT/'.cache/core-055';directory.mkdir(exist_ok=True)
    epoch=str(time.time_ns());log=directory/(epoch+'.log')
    sources={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'rouge').rglob('*.py')}
    sources.update({p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'rouge/data').glob('*.json')})
    print(json.dumps({'stage':'tests','modules':len(modules),'log':log.relative_to(ROOT).as_posix()}),flush=True)
    with log.open('x',encoding='utf-8',buffering=1) as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromNames(modules))
    changed=[n for n,h in sources.items() if sha(ROOT/n)!=h]
    receipt={'version':'0.55.0','passed':result.wasSuccessful() and not changed,
        'tests_run':result.testsRun,'current_tests_passed':result.testsRun-len(result.skipped)-len(result.failures)-len(result.errors),
        'historical_tests_skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors),
        'failed_cases':[t.id() for t,e in result.failures+result.errors],
        'test_modules':modules,'test_log':log.relative_to(ROOT).as_posix(),'test_log_sha256':sha(log),
        'source_sha256':sources,'source_drift_during_tests':changed,
        'elapsed_seconds':time.perf_counter()-started,'all_priority_1_completed':False,
        'scope':'Maintained test inventory. Real page holdouts and numerical/UI audits have separate receipts.'}
    out=directory/(epoch+'.json');out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','tests_run','current_tests_passed','historical_tests_skipped','failures','errors','failed_cases','source_drift_during_tests','elapsed_seconds')}),flush=True)
    print(json.dumps({'receipt':out.relative_to(ROOT).as_posix()}),flush=True)
    return 0 if receipt['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
