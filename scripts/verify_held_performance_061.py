"""Interleaved, separate-process measurements of the adopted original matcher."""
import hashlib,json,subprocess,sys,time,types
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
DIRECTORY=ROOT/'.cache/research/held-performance-061'
FIXTURES=ROOT/'.cache/research/run-performance-059/threads-1791179141499034400/fixtures.json'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,value):
    with p.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)


def worker(mode,destination):
    from rouge import relic_recognition as current
    before=ROOT/'.cache/batch-061-before/rouge/relic_recognition.py'
    manifest=read(ROOT/'.cache/batch-061-before/manifest.json')['source_hashes']
    assert sha(before)==manifest['rouge/relic_recognition.py']
    module=current
    if mode=='baseline':
        module=types.ModuleType('rouge._held_baseline061');module.__package__='rouge'
        exec(compile(before.read_text(encoding='utf-8'),str(before),'exec'),module.__dict__)
        # These exact source functions are unchanged; use the same public
        # packaged artwork and cold immutable reference caches in each process.
        for name in ('prepared_templates','_refined_template','artwork_families'):
            setattr(module,name,getattr(current,name))
    cases=[]
    for case in read(FIXTURES)['cases']:
        path=ROOT/case['file'];assert sha(path)==case['sha256']
        with np.load(path,allow_pickle=False) as z:
            roi=z['roi'].copy();h=int(z['height']);w=int(z['width'])
        started=time.perf_counter();result=module._match_bar(roi,h,w,0,0)
        cases.append({'case':case['case'],'elapsed_ms':(time.perf_counter()-started)*1000,
                      'result':result,'fixture_sha256':case['sha256']})
    write(destination,{'mode':mode,'cases':cases,'baseline_source_sha256':sha(before),
                       'current_source_sha256':sha(ROOT/'rouge/relic_recognition.py')})


def main():
    if len(sys.argv)>1 and sys.argv[1]=='worker':
        worker(sys.argv[2],Path(sys.argv[3]));return
    folder=DIRECTORY/('formal-'+str(time.time_ns()));folder.mkdir()
    hashes={p.relative_to(ROOT).as_posix():sha(p) for p in (
        ROOT/'rouge/relic_recognition.py',Path(__file__),FIXTURES,
        ROOT/'rouge/data/relic-icon-receipt.json',ROOT/'rouge/data/tactical-icon-receipt.json',
        ROOT/'rouge/data/relic-reference-equivalence.json')}
    for receipt in ('relic-icon-receipt.json','tactical-icon-receipt.json'):
        for item in read(ROOT/'rouge/data'/receipt)['icons']:
            path=ROOT/'rouge/data'/item['file'];hashes[path.relative_to(ROOT).as_posix()]=sha(path)
    results=[];workers={}
    for cycle in range(3):
        pair={}
        for mode in (('baseline','current') if cycle%2==0 else ('current','baseline')):
            out=folder/f'{cycle}-{mode}.json'
            subprocess.run([sys.executable,__file__,'worker',mode,str(out)],cwd=ROOT,check=True,timeout=60)
            pair[mode]=read(out);workers[out.relative_to(ROOT).as_posix()]=sha(out)
        for old,new in zip(pair['baseline']['cases'],pair['current']['cases']):
            canonical=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'))
            row={'cycle':cycle,'case':old['case'],'equal':canonical(old['result'])==canonical(new['result']),
                 'baseline_ms':old['elapsed_ms'],'current_ms':new['elapsed_ms']}
            results.append(row);print(json.dumps(row),flush=True)
    import statistics
    metrics={}
    for name in {r['case'] for r in results}:
        rows=[r for r in results if r['case']==name]
        metrics[name]={mode+'_median_ms':statistics.median(r[mode+'_ms'] for r in rows)
                       for mode in ('baseline','current')}
    drift=[name for name,digest in hashes.items() if sha(ROOT/name)!=digest]
    proof={'version':'0.61.0','passed':not drift and all(r['equal'] for r in results),
           'rows':results,'metrics':metrics,'source_sha256':hashes,'source_drift':drift,
           'workers':workers,'threads_changed_globally':False,'game_actions':0,'chat_requests':0,
           'limits':['Two existing bar crops, three interleaved pairs; not independent accuracy or universal performance.',
                     'Every worker process starts with cold immutable reference caches; second bar reuses their UI scale.',
                     'Existing test application remained running; background workload is not controlled.']}
    write(folder/'receipt.json',proof);assert proof['passed']
    write(ROOT/'HELD_PERFORMANCE_0.61_VERIFICATION.json',proof)
    print(json.dumps({'passed':True,'metrics':metrics}),flush=True)


if __name__=='__main__':main()
