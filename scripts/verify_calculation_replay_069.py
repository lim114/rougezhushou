"""Compare 732 complete outputs; only the exact new token report is allowed."""
import copy,hashlib,json,subprocess,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def snapshot():
    files=[*(ROOT/'rouge').rglob('*.py'),*(ROOT/'rouge/data').rglob('*.json'),
        *[p for folder in ('page-features','visual-anchors')
          for p in (ROOT/'rouge/data'/folder).iterdir() if p.is_file()],
        Path(__file__),ROOT/'scripts/verify_calculation_replay_056.py',ROOT/'NUMERIC_REPLAY_0.68_VERIFICATION.json']
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(files))}


def main():
    old=json.loads((ROOT/'NUMERIC_REPLAY_0.68_VERIFICATION.json').read_text(encoding='utf-8'))
    assert old['passed'] and old['cases']==old['exact_structured_unchanged']==732
    path=ROOT/old['current_output']
    assert sha(path)==old['current_output_sha256']
    rows=json.loads(path.read_text(encoding='utf-8'))
    assert len(rows)==732
    assert all('rogue_6_relic_cargo_3' not in str(row['scenario']) for row in rows)
    directory=ROOT/'.cache/numeric-replay-069'/str(time.time_ns());directory.mkdir(parents=True)
    inputs=directory/'inputs.json'
    inputs.write_text(json.dumps([row['scenario'] for row in rows]),encoding='utf-8')
    before=snapshot()
    after=directory/'after.json';worker=directory/'worker.json'
    with (directory/'worker.log').open('x',encoding='utf-8') as log:
        subprocess.run([sys.executable,str(ROOT/'scripts/verify_calculation_replay_056.py'),'_worker',
            '--package',str(ROOT),'--inputs',str(inputs),'--output',str(after),'--receipt',str(worker)],
            cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    current=json.loads(after.read_text(encoding='utf-8'))
    # JSON-canonical equality retains numeric type/precision and every public
    # field. Python equality alone would accept an int-to-float change.
    canonical=lambda row:json.dumps(row,sort_keys=True,ensure_ascii=False,separators=(',',':'))
    differences=[i for i,(a,b) in enumerate(zip(rows,current)) if canonical(a)!=canonical(b)]
    expected=copy.deepcopy(rows);allowances=[]
    for i,row in enumerate(rows):
        s=row['scenario']
        if s['operator']!='char_110_deepcl':continue
        # These old cases have neither SUM-Y nor extra concurrent tokens.
        # All damage, SP, cycle, token attributes and other report fields must
        # remain exact. Do not exempt the operator's whole numerical result.
        assert 'module_id' not in s and 'elite' not in s and 'summon_count' not in s
        report=expected[i]['result']['report']['sections']
        index=next(j for j,r in enumerate(report) if r['id']=='summons')
        metrics=report[index]['metrics']
        assert metrics[0]=={'key':'summon_count','label':'当前在场触手','value':1,'unit':'个'}
        metrics[0]['label']='参与测算触手数（局外假设）'
        metrics.insert(1,{'key':'concurrent_limit','label':'触手同时在场上限','value':4,'unit':'个'})
        allowances.append({'case_index':i,'scope':'exact_summons_report_update_only',
            'label_path':f'result.report.sections[{index}].metrics[0].label',
            'label_before':'当前在场触手','label_after':'参与测算触手数（局外假设）',
            'insert_path':f'result.report.sections[{index}].metrics[1]',
            'insert_value':metrics[1]})
    unexpected=[i for i,(a,b) in enumerate(zip(expected,current)) if canonical(a)!=canonical(b)]
    assert len(allowances)==16
    final=snapshot()
    drift=[name for name in sorted(set(before)|set(final)) if before.get(name)!=final.get(name)]
    details={'cases_before':len(rows),'cases_after':len(current),'changed_case_indices':differences,
             'unexpected_case_indices':unexpected,'allowances':allowances,'source_drift':drift}
    with (directory/'comparison.json').open('x',encoding='utf-8') as stream:json.dump(details,stream,ensure_ascii=False,indent=2)
    proof=json.loads(worker.read_text(encoding='utf-8'))
    assert proof['passed'] and proof['source_stable_during_calculation']
    assert len(rows)==len(current)==732 and not unexpected and not drift,details
    assert differences==[a['case_index'] for a in allowances],differences
    receipt={'version':'0.69.0','passed':True,'verified_at':time.time(),'cases':732,
        'exact_structured_unchanged':716,'all_existing_numerical_fields_unchanged':732,
        'expected_report_only_cases':16,'unexpected_changes':[],'allowances':allowances,
        'baseline_output':path.relative_to(ROOT).as_posix(),'baseline_sha256':sha(path),
        'baseline_version':'0.68.0','current_output':after.relative_to(ROOT).as_posix(),'current_output_sha256':sha(after),
        'worker_receipt':worker.relative_to(ROOT).as_posix(),'worker_receipt_sha256':sha(worker),
        'source_sha256':proof['source_sha256'],'source_stable':proof['source_stable_during_calculation'],
        'full_formal_source_sha256':before,'full_formal_source_sha256_after':final,
        'source_drift':drift,'runner_sealed':True,'new_empty_bed_cases_in_default_corpus':0,
        'separate_new_cost_evidence':'.cache/research/empty-bed-cost-057/freeze.json',
        'private_state_used':False,'game_actions':0,'chat_requests':0}
    with (ROOT/'NUMERIC_REPLAY_0.69_VERIFICATION.json').open('x',encoding='utf-8') as stream:
        json.dump(receipt,stream,ensure_ascii=False,indent=2)
    print(json.dumps({'passed':True,'exact_structured_unchanged':716,
        'all_existing_numerical_fields_unchanged':732,'expected_report_only_cases':16,'source_drift':drift}))


if __name__=='__main__':main()
