"""Seal the maintained 0.65 suite plus counter lifecycle regression."""
import hashlib,json,sys,time,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def files_for(modules):
    tests=[ROOT.joinpath(*module.split('.')[:2]).with_suffix('.py') for module in modules]
    assert all(path.is_file() for path in tests),tests
    probe_path=ROOT/'.cache/research/hybrid-059/epoch2-current/footer-current-rec-probe-1791183933046002600/receipt.json'
    probe=json.loads(probe_path.read_text(encoding='utf-8'))
    fixtures=[probe_path,ROOT/'HYBRID_0.58_VERIFICATION.json']
    for key in ('source_frame','source_worker_row','crop_file'):
        item=probe[key];fixtures.append(ROOT/item.get('path',item.get('file')))
    old_hybrid=json.loads((ROOT/'HYBRID_0.58_VERIFICATION.json').read_text(encoding='utf-8'))
    fixtures.extend(ROOT/name for name in old_hybrid['replay_receipts'])
    prose_path=ROOT/'.cache/research/hybrid-059/epoch3-current/existing-description-reconfirm-1791186974924856300/receipt.json'
    prose=json.loads(prose_path.read_text(encoding='utf-8'));fixtures.append(prose_path)
    fixtures.extend(ROOT/line['crop']['path'] for line in prose['lines'])
    return sorted(set([*(ROOT/'rouge').rglob('*.py'),*(ROOT/'rouge/data').rglob('*.json'),
        *[p for folder in ('page-features','visual-anchors')
          for p in (ROOT/'rouge/data'/folder).glob('*') if p.is_file()],
        *tests,*([ROOT/'tests/__init__.py'] if (ROOT/'tests/__init__.py').is_file() else []),
        Path(__file__),ROOT/'scripts/verify_hybrid_059.py',ROOT/'scripts/build_relic_mechanics.py',
        ROOT/'.cache/research/held-performance-061/baseline-profile.json',
        ROOT/'.cache/batch-060-before/rouge/digit_counters.py',
        ROOT/'.cache/research/counter-reading-060/diagnosis-1791195600883958000.json',
        ROOT/'.cache/research/page-routing-056/epoch-1791136902879484600/inventory.json',
        ROOT/'.cache/batch-059-before/manifest.json',
        ROOT/'.cache/batch-059-before/tests/test_page_features_056.py',
        ROOT/'CORE_0.65_VERIFICATION.json',*fixtures]))


def snapshot(modules):
    return {p.relative_to(ROOT).as_posix():digest(p) for p in files_for(modules)}


def main():
    started=time.perf_counter()
    old=json.loads((ROOT/'CORE_0.65_VERIFICATION.json').read_text(encoding='utf-8'))
    assert old['passed'] and len(old['test_modules'])==96
    modules=list(old['test_modules'])
    for module in ('tests.test_sp_sources_066',):
        if module not in modules:modules.append(module)
    directory=ROOT/'.cache/core-066';directory.mkdir(exist_ok=True)
    epoch=str(time.time_ns());log=directory/(epoch+'.log')
    sources=snapshot(modules)
    print(json.dumps({'modules':len(modules),'log':log.relative_to(ROOT).as_posix()}),flush=True)
    with log.open('x',encoding='utf-8',buffering=1) as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    after=snapshot(modules)
    changed=[name for name in sorted(set(sources)|set(after)) if sources.get(name)!=after.get(name)]
    receipt={'version':'0.66.0','passed':result.wasSuccessful() and not changed,
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
