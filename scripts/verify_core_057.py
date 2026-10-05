"""Maintain the latest explicit suite and seal every regression epoch."""
import hashlib,json,sys,time,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started=time.perf_counter()
    modules=list(json.loads((ROOT/'CORE_0.56_VERIFICATION.json').read_text(encoding='utf-8'))['test_modules'])
    for module in ('tests.test_visual_recognition','tests.test_visual_recognition_057','tests.test_recognition_057','tests.test_empty_bed_cost_057'):
        if module not in modules:modules.append(module)
    directory=ROOT/'.cache/core-057';directory.mkdir(exist_ok=True)
    epoch=str(time.time_ns());log=directory/(epoch+'.log')
    files=[*(ROOT/'rouge').rglob('*.py'),*(ROOT/'rouge/data').rglob('*.json'),
           *[p for folder in ('page-features','visual-anchors') for p in (ROOT/'rouge/data'/folder).glob('*') if p.is_file()]]
    sources={p.relative_to(ROOT).as_posix():digest(p) for p in files}
    print(json.dumps({'modules':len(modules),'log':log.relative_to(ROOT).as_posix()}),flush=True)
    with log.open('x',encoding='utf-8',buffering=1) as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    changed=[name for name,sha in sources.items() if digest(ROOT/name)!=sha]
    receipt={'version':'0.57.0','passed':result.wasSuccessful() and not changed,
        'tests_run':result.testsRun,'current_tests_passed':result.testsRun-len(result.skipped)-len(result.failures)-len(result.errors),
        'historical_tests_skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors),
        'failed_cases':[test.id() for test,error in result.failures+result.errors],
        'test_modules':modules,'test_log':log.relative_to(ROOT).as_posix(),'test_log_sha256':digest(log),
        'source_sha256':sources,'source_drift_during_tests':changed,'elapsed_seconds':time.perf_counter()-started,
        'all_priority_1_completed':False,'scope':'Maintained regression scope; image holdouts and performance are separate receipts.'}
    path=directory/(epoch+'.json');path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','tests_run','current_tests_passed','historical_tests_skipped','failures','errors','failed_cases','source_drift_during_tests','elapsed_seconds')}),flush=True)
    print(json.dumps({'receipt':path.relative_to(ROOT).as_posix()}),flush=True)
    return 0 if receipt['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
