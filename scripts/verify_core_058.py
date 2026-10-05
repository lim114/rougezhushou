"""Seal the maintained 0.57 suite plus the three 0.58 recognition modules."""
import hashlib,json,sys,time,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def files_for(modules):
    tests=[ROOT.joinpath(*module.split('.')[:2]).with_suffix('.py') for module in modules]
    assert all(path.is_file() for path in tests),tests
    return sorted(set([*(ROOT/'rouge').rglob('*.py'),*(ROOT/'rouge/data').rglob('*.json'),
        *[p for folder in ('page-features','visual-anchors')
          for p in (ROOT/'rouge/data'/folder).glob('*') if p.is_file()],
        *tests,*([ROOT/'tests/__init__.py'] if (ROOT/'tests/__init__.py').is_file() else []),
        Path(__file__),ROOT/'scripts/verify_hybrid_058.py',
        ROOT/'CORE_0.57_VERIFICATION.json']))


def snapshot(modules):
    return {p.relative_to(ROOT).as_posix():digest(p) for p in files_for(modules)}


def main():
    started=time.perf_counter()
    old=json.loads((ROOT/'CORE_0.57_VERIFICATION.json').read_text(encoding='utf-8'))
    assert old['passed'] and len(old['test_modules'])==82
    modules=list(old['test_modules'])
    for module in ('tests.test_page_ocr_058','tests.test_page_features_058','tests.test_hybrid_safety_058'):
        if module not in modules:modules.append(module)
    directory=ROOT/'.cache/core-058';directory.mkdir(exist_ok=True)
    epoch=str(time.time_ns());log=directory/(epoch+'.log')
    sources=snapshot(modules)
    print(json.dumps({'modules':len(modules),'log':log.relative_to(ROOT).as_posix()}),flush=True)
    with log.open('x',encoding='utf-8',buffering=1) as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    after=snapshot(modules)
    changed=[name for name in sorted(set(sources)|set(after)) if sources.get(name)!=after.get(name)]
    receipt={'version':'0.58.0','passed':result.wasSuccessful() and not changed,
        'tests_run':result.testsRun,'current_tests_passed':result.testsRun-len(result.skipped)-len(result.failures)-len(result.errors),
        'historical_tests_skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors),
        'failed_cases':[test.id() for test,error in result.failures+result.errors],
        'test_modules':modules,'test_log':log.relative_to(ROOT).as_posix(),'test_log_sha256':digest(log),
        'source_sha256':sources,'source_sha256_after':after,'source_drift_during_tests':changed,
        'maintained_test_files_sealed':True,'runner_sealed':True,'elapsed_seconds':time.perf_counter()-started,
        'all_priority_1_completed':False,'scope':'Maintained regression scope; independent image and performance receipts are separate.'}
    path=directory/(epoch+'.json')
    with path.open('x',encoding='utf-8') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2)
    print(json.dumps({k:receipt[k] for k in ('passed','tests_run','current_tests_passed','historical_tests_skipped','failures','errors','failed_cases','source_drift_during_tests','elapsed_seconds')}),flush=True)
    print(json.dumps({'receipt':path.relative_to(ROOT).as_posix()}),flush=True)
    return 0 if receipt['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
