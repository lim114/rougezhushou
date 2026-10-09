"""Source-only preparation; Root alone executes actual Saved native auditing."""
import argparse, hashlib, json, os, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=Path('/workspace/.continuation')
HELPER_SHA='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
PROBE_SHA='b4e574e54d7798d06707ad7f80a2efe268209a5b8e22645f9d976ac86dd7e1d3'
PART_PINS=('400af29f9aeb7a9cd5ec740b7d4f1233447fb448bf6ff305f17b9eeac26aa003',
           '24f604fc8ef7679511fe7584f7fbca725cc2d8da6d7ab00dd103ac52ce330eb9')
FULL=BASE/'section114-public-scalar-types-source-v3/original-probe-inputs.json'
FULL_SHA='df338b17c9e4054338fc8c2b283d4f9842bc024f311c8665717b1b15230ecdef'
CONTRACT=BASE/'section114-original-observation-contract-source-v1/contract.json'
CONTRACT_SHA='c9c4a4dd5540d3f0ce42f9ab22d3d99508f1f5f6293876c857f42db542682fd8'
PLAN_SHA='39f5d6ad5426324fb981915a063fc8467f15c68463c1dc6d129e97e8219320f2'
PLAIN=BASE/'root-section114-original-plain-export-v1.json'
PLAIN_SHA='abb9b1acc14df22c621b6871eeccffa2511a85d7f488bf7cf5d1eb2a19dc5b05'
PHASES=('calculate_damage','format_estimate','format_report','format_report_technical')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def meta(path):
    path=Path(path);raw=path.read_bytes()
    return {'path':str(path),'bytes':len(raw),'sha256':sha(raw)}
def error_core(error):
    if error is None:return None
    assert type(error) is dict and type(error['type']) is type(error['message']) is str
    assert type(error['traceback']) is str and error['traceback']
    return {k:error[k] for k in ('type','message')}

def main():
    parser=argparse.ArgumentParser()
    for name in ('root','guard','original1','original2','candidate1','candidate2',
                 'original-exit1','original-exit2','candidate-exit1','candidate-exit2','out'):
        parser.add_argument('--'+name,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    assert not out.exists() and out != root and root not in out.parents
    for path,pin in ((HERE/'native_evidence.py',HELPER_SHA),(HERE/'qualification-plan.json',PLAN_SHA),
                     (FULL,FULL_SHA),(CONTRACT,CONTRACT_SHA),(PLAIN,PLAIN_SHA)):
        assert not path.is_symlink() and sha(path.read_bytes())==pin
    sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
    from native_evidence import read_record,assert_native_equal as exact,source_map
    guard_path=Path(args.guard).resolve();guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert guard['section']==114 and set(extra)=={'CORE_0.70_VERIFICATION.json'}
    def source_check():
        assert source_map(root)==expected and guard_path.read_bytes()==guard_raw
        assert {name:sha((root/name).read_bytes()) for name in extra}==extra
    source_check();full=load(FULL)['cases'];contract=load(CONTRACT);plan=load(HERE/'qualification-plan.json')['rows']
    healthy=contract['source_proposed_valid_only_baseline']['ids'];ignored=contract['separate_consumption_controls']['ids']
    assert len(healthy)==50 and len(set(healthy))==50 and len(ignored)==18 and len(set(ignored))==18
    assert len(full)==len(plan)==133 and [r['id'] for r in full]==[r['id'] for r in plan]
    parts=[]
    for i in (1,2):
        path=BASE/f'root-section114-public-inputs-part{i}-v1.json';assert sha(path.read_bytes())==PART_PINS[i-1]
        part=load(path);assert part['original_full_fixture_sha256']==FULL_SHA and part['original_total_cases']==133
        assert part['original_offset']==(0 if i==1 else 67);parts.append(part['cases'])
    assert [len(part) for part in parts]==[67,66];exact(parts[0]+parts[1],full,'complete ordered 133 fixtures')
    plain=load(PLAIN);assert plain['runtime_actual'] is True and plain['total']==133 and plain['actual_errors']==34
    assert plain['healthy50_actual_success'] is True and [r['id'] for r in plain['rows']]==[r['id'] for r in full]
    summaries=[];decoded=0;phase_guard_shas={}
    def audit_part(folder,phase,primary,part_index):
        nonlocal decoded
        folder=Path(folder).resolve();receipt_path=folder/'observations.json';receipt=load(receipt_path)
        assert Path(primary).read_bytes().strip()==b'0'
        assert receipt['kind']=='ROOT_ACTUAL_PUBLIC_API_THREE_FORMATTER_OBSERVATION' and receipt['phase']==phase
        assert receipt['observation_only'] is True and receipt['product_pass'] is False and receipt['observation_complete'] is True
        assert receipt['source_and_CORE_unchanged'] is True and 'fatal_error' not in receipt
        assert receipt['runner']['sha256']==PROBE_SHA and receipt['fixture']['sha256']==PART_PINS[part_index]
        assert receipt['source_before']==receipt['source_after'] and receipt['CORE_before']==receipt['CORE_after']==extra
        actual_guard_path=Path(receipt['guard']['path']);actual_guard_raw=actual_guard_path.read_bytes();actual_guard=json.loads(actual_guard_raw)
        assert sha(actual_guard_raw)==receipt['guard']['sha256'] and len(actual_guard_raw)==receipt['guard']['bytes']
        assert actual_guard['section']==114 and actual_guard['source_sha256']==receipt['source_before'] and actual_guard['source_additional_sha256']==extra
        if phase in phase_guard_shas:assert phase_guard_shas[phase]==sha(actual_guard_raw)
        else:phase_guard_shas[phase]=sha(actual_guard_raw)
        if phase=='candidate':assert actual_guard_raw==guard_raw and receipt['source_after']==expected
        else:assert plain['receipts'][part_index]['sha256']==sha(receipt_path.read_bytes())
        cases=parts[part_index];refs=receipt['records'];calls=receipt['calls'];rows=receipt['rows']
        assert len({r['path'] for r in refs})==len(refs)
        assert [json.loads(line) for line in (folder/'native/index.jsonl').read_text().splitlines()]==refs
        assert receipt['actual_completed_cases']==len(cases) and [r['id'] for r in rows]==[c['id'] for c in cases]
        values={}
        for ref in refs:
            value=read_record(folder/'native',ref);decoded+=1
            assert (ref['case'],ref['phase']) not in values;values[(ref['case'],ref['phase'])]=value
            exact(value['after'],value['before'],'complete per-call/whole-case native caller purity')
            assert ref['kind'] in ('actual-public-consumer','whole-case-caller')
        result={};ref_index=call_index=errors=successful=0
        for case,row in zip(cases,rows):
            identity=case['id'];numeric=values[(identity,PHASES[0])];error=error_core(numeric['error'])
            exact(numeric['before'],(case['scenario'],),'complete numerical fixture caller')
            assert row['calculate_error']==numeric['error'] and row['formatters_blocked'] is (error is not None)
            active=PHASES if error is None else PHASES[:1];texts=[]
            for step in active:
                ref=refs[ref_index];call=calls[call_index];saved=values[(identity,step)];ref_index+=1;call_index+=1
                assert ref['kind']=='actual-public-consumer' and (ref['case'],ref['phase'])==(identity,step)
                assert call['native']==ref and (call['case'],call['phase'])==(identity,step)
                assert call['error']==saved['error'] and call['caller_unchanged'] is True
                if step!=PHASES[0]:
                    assert saved['error'] is None and type(saved['result']) is str
                    exact(saved['before'],(numeric['result'],),'complete actual formatter result graph');texts.append(saved['result'])
            whole_ref=refs[ref_index];ref_index+=1;whole=values[(identity,'caller')]
            assert whole_ref['kind']=='whole-case-caller' and (whole_ref['case'],whole_ref['phase'])==(identity,'caller')
            exact(whole['before'],case['scenario'],'whole-case fixture caller')
            if error is None:
                assert type(numeric['result']) is dict and len(texts)==3 and texts[0]==texts[1];successful+=1
            else:
                assert numeric['result'] is None and texts==[];errors+=1
            result[identity]={'result':numeric['result'],'error':error,'caller':numeric['before'][0],'texts':texts}
        assert ref_index==len(refs)==receipt['actual_native_records']==2*len(cases)+3*successful
        assert call_index==len(calls)==receipt['actual_public_calls']==len(cases)+3*successful
        assert errors==receipt['consumer_error_count']
        summaries.append({'phase':phase,'part':part_index+1,'receipt':meta(receipt_path),'raw_primary':meta(primary),
                          'actual_cases':len(cases),'actual_numeric_successes':successful,'actual_numeric_errors':errors,
                          'actual_public_calls':len(calls),'actual_native_records':len(refs)})
        return result
    original={};candidate={}
    for i in (1,2):original.update(audit_part(getattr(args,f'original{i}'),'original',getattr(args,f'original_exit{i}'),i-1))
    for i in (1,2):candidate.update(audit_part(getattr(args,f'candidate{i}'),'candidate',getattr(args,f'candidate_exit{i}'),i-1))
    assert list(original)==list(candidate)==[r['id'] for r in full];checks=[];rejected=[];success_preserved=[];error_preserved=[]
    for row,plain_row in zip(plan,plain['rows']):
        identity=row['id'];before=original[identity];after=candidate[identity]
        exact(after['caller'],before['caller'],'same complete original/candidate caller')
        observed_error=error_core(plain_row['error'])
        assert before['error']==observed_error==row['Root_actual_original_error_observed']
        assert (before['error'] is None) is row['Root_actual_original_success_observed']
        mode=row['mode']
        if mode=='qualified_bool_rejection':
            assert before['error'] is None and after['error']==row['candidate_error'] and after['result'] is None and after['texts']==[]
            rejected.append(identity);scope='Source-qualified consumer now rejects actual previously accepted bool with exact field/type/message'
        else:
            assert mode in ('preserve_observed_outcome','preserve_observed_earlier_error')
            if mode=='preserve_observed_earlier_error':assert before['error'] is not None
            assert after['error']==before['error']
            if before['error'] is None:
                exact(after['result'],before['result'],'complete preserved output types/order/floatbits/internal aliases')
                exact(after['texts'],before['texts'],'all three complete preserved formatter texts')
                success_preserved.append(identity);scope='whole successful result and all three complete texts exactly preserved'
            else:
                assert before['result'] is after['result'] is None and before['texts']==after['texts']==[]
                error_preserved.append(identity);scope='actual original numeric exception stage/type/message and blocked formatters preserved; traceback retained, line numbers not compared'
        if identity in healthy:assert mode=='preserve_observed_outcome' and before['error'] is after['error'] is None
        if identity in ignored:assert mode=='preserve_observed_outcome'
        checks.append({'id':identity,'mode':mode,'consumer':row['consumer'],'scope':scope,'healthy50':identity in healthy,
                       'ignored18':identity in ignored,'original_error':before['error'],'candidate_error':after['error']})
    assert len(rejected)==32 and len(success_preserved)==67 and len(error_preserved)==34
    assert set(healthy)<=set(success_preserved) and set(ignored)<=set(success_preserved+error_preserved)
    source_check();report={'kind':'ROOT_ACTUAL_114_COMPLETE_SAVED_API_AUDIT','passed':True,'workflow_complete':True,'source_drift':[],
        'source_guard_sha256':sha(guard_raw),'source_count':len(expected),'CORE_unchanged':True,'actual_cases':133,
        'actual_native_records_decoded':decoded,'observations':summaries,'case_checks':checks,
        'healthy50_complete_native_and_three_texts_equal':True,'ignored18_actual_outcomes_preserved':True,
        'actual_original_successes':99,'actual_original_numeric_errors':34,'actual_candidate_successes':67,
        'actual_candidate_numeric_errors':66,'actual_new_qualified_bool_rejections':32,
        'source_qualification_plan':meta(HERE/'qualification-plan.json'),'Root_original_plain_export':meta(PLAIN),
        'whole_alias_scope':'Each saved graph and whole comparison retains internal alias checks; no shared identity claim across independent observations.',
        'all133_product_success_claimed':False,'native_windows_game_chat_verified':False,'private_state_access':False,
        'runner':meta(Path(__file__).resolve())}
    with out.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,ensure_ascii=False,allow_nan=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'passed':True,'actual_cases':133,'native_records_decoded':decoded,'new_qualified_rejections':32}))

if __name__=='__main__':main()
