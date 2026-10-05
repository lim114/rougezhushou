"""Full unchanged defaults against the sealed 0.56 outputs; new fees have separate oracles."""
import hashlib,json,subprocess,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    old=json.loads((ROOT/'NUMERIC_REPLAY_0.56_VERIFICATION.json').read_text(encoding='utf-8'))
    assert old['passed'] and old['cases']==732
    path=ROOT/old['after_output'];assert sha(path)==old['after_output_sha256']
    rows=json.loads(path.read_text(encoding='utf-8'))
    # No empty-bed scenario occurs in this historical default corpus. Do not
    # claim it tests the new combination; the independent source oracle does.
    assert all('rogue_6_relic_cargo_3' not in str(row['scenario']) for row in rows)
    directory=ROOT/'.cache/numeric-replay-057'/str(time.time_ns());directory.mkdir(parents=True)
    inputs=directory/'inputs.json'
    inputs.write_text(json.dumps([row['scenario'] for row in rows]),encoding='utf-8')
    after=directory/'after.json';worker=directory/'worker.json'
    with (directory/'worker.log').open('x',encoding='utf-8') as log:
        subprocess.run([sys.executable,str(ROOT/'scripts/verify_calculation_replay_056.py'),'_worker',
            '--package',str(ROOT),'--inputs',str(inputs),'--output',str(after),'--receipt',str(worker)],
            cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    current=json.loads(after.read_text(encoding='utf-8'))
    differences=[i for i,(a,b) in enumerate(zip(rows,current)) if a!=b]
    details={'cases_before':len(rows),'cases_after':len(current),'unexpected_case_indices':differences}
    (directory/'comparison.json').write_text(json.dumps(details),encoding='utf-8')
    proof=json.loads(worker.read_text(encoding='utf-8'))
    assert proof['passed'] and len(rows)==len(current)==732 and not differences,details
    receipt={'version':'0.57.0','passed':True,'verified_at':time.time(),'cases':732,
        'exact_structured_unchanged':732,'unexpected_changes':[],
        'baseline_output':path.relative_to(ROOT).as_posix(),'baseline_sha256':sha(path),
        'current_output':after.relative_to(ROOT).as_posix(),'current_output_sha256':sha(after),
        'worker_receipt':worker.relative_to(ROOT).as_posix(),'worker_receipt_sha256':sha(worker),
        'source_sha256':proof['source_sha256'],'source_stable':proof['source_stable_during_calculation'],
        'new_empty_bed_cases_in_default_corpus':0,
        'separate_new_cost_evidence':'.cache/research/empty-bed-cost-057/freeze.json',
        'private_state_used':False,'game_actions':0,'chat_requests':0}
    with (ROOT/'NUMERIC_REPLAY_0.57_VERIFICATION.json').open('x',encoding='utf-8') as stream:
        json.dump(receipt,stream,ensure_ascii=False,indent=2)
    print(json.dumps({'passed':True,'exact_structured_unchanged':732,'new_cost_oracle_separate':True}))


if __name__=='__main__':main()
