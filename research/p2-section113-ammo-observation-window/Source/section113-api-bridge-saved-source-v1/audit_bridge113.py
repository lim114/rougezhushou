"""Source preparation only. Root alone executes all Saved native decoding.

No project imports/calculations; emit an admission only after complete actual proof.
"""
import argparse, ast, hashlib, json, math, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path('/workspace/.continuation')
HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
PROBE_SHA = 'b4e574e54d7798d06707ad7f80a2efe268209a5b8e22645f9d976ac86dd7e1d3'
INPUT_PATH = BASE/'root-section113-public22-inputs-v1.json'
INPUT_SHA = 'cf23b63490a6d9083561192740edaf249b763ca918c54e32417d3ca36c6915b5'
BASIS = BASE/'full115-bounded-window-source-draft-v1/window.py'
BASIS_SHA = '9b1e8d59986f92b76c222b0af8cdd834d4eb23852aedccde8bae3d05f6b5a07e'
TEMPLATE = BASE/'full115-113-window-compatibility-design-v1/EXPECTED_MAP_INACTIVE.json'
TEMPLATE_SHA = '87d8fc0be4fb145a7db7352ab25196576393bee5478fdddd6226332785628e3f'
INDICES = (18,19,20,21,38,39,40,41,44,45)
METRICS = ('window_seconds','window_dps','window_hps')
PHASES = ('calculate_damage','format_estimate','format_report','format_report_technical')

def sha(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value): return json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf-8')
def digest(value): return sha(encoded(value))
def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def native090(value):
    kind=type(value).__name__
    if value is None or type(value) in (bool,int,str):return {'type':kind,'value':value}
    if type(value) is float:return {'type':'float','hex':value.hex()}
    if type(value) in (list,tuple):return {'type':kind,'items':[native090(v) for v in value]}
    if type(value) is dict:return {'type':'dict','items':[[native090(k),native090(v)] for k,v in value.items()]}
    raise AssertionError(('unhandled native value',kind))
def projection090(result):
    keys=['attack','total_damage','components','attack_speed','base_attack_speed','interval_seconds','timing']
    if 'total_healing' in result:keys.append('total_healing')
    keys.extend(k for k in result if k.endswith('_reference'))
    out={key:result[key] for key in dict.fromkeys(keys)}
    out['estimate']={key:result['estimate'][key] for key in ('training','base_stats','skill')}
    return out
def scalar(present,value):
    assert type(present) is bool and (not present or value is None or type(value) in (int,float))
    assert type(value) is not float or math.isfinite(value)
    return {'present':present,'python_type':type(value).__name__ if present else None,
            'value':value if present else None,'float_hex':value.hex() if present and type(value) is float else None}
def write(path,value):
    with Path(path).open('xb') as stream:
        stream.write(encoded(value)+b'\n');stream.flush();os.fsync(stream.fileno())

def main():
    p=argparse.ArgumentParser()
    for name in ('root','guard','original','candidate','original-exit','candidate-exit','out'):p.add_argument('--'+name,required=True)
    args=p.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    assert not out.exists() and root != out and root not in out.parents
    for path,pin in ((HERE/'native_evidence.py',HELPER_SHA),(INPUT_PATH,INPUT_SHA),(BASIS,BASIS_SHA),(TEMPLATE,TEMPLATE_SHA)):
        assert not path.is_symlink() and sha(path.read_bytes())==pin
    sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
    from native_evidence import read_record,assert_native_equal as exact,freeze,source_map
    guard_path=Path(args.guard).resolve();guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert guard['section']==113 and set(extra)=={'CORE_0.70_VERIFICATION.json'}
    def check_source():
        assert source_map(root)==expected and guard_path.read_bytes()==guard_raw
        assert {name:sha((root/name).read_bytes()) for name in extra}==extra
    check_source();cases=load(INPUT_PATH)['cases'];assert len(cases)==22 and len({c['id'] for c in cases})==22
    source=BASIS.read_text();tree=ast.parse(source)
    for name in ('projection090','native090'):
        original=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
        own=next(n for n in ast.parse(Path(__file__).read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name)
        assert ast.dump(original,include_attributes=False)==ast.dump(own,include_attributes=False)
    rows_node=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='rows090' for t in n.targets))
    literals=ast.literal_eval(rows_node.value);assert len(literals)==52
    records_decoded=0;receipts={};proof_raw={};case_checks=[]
    def observation(folder,phase,primary):
        nonlocal records_decoded
        folder=Path(folder).resolve();receipt_raw=(folder/'observations.json').read_bytes();receipt=json.loads(receipt_raw)
        primary_raw=Path(primary).read_bytes();assert primary_raw.strip()==b'0'
        assert receipt['kind']=='ROOT_ACTUAL_PUBLIC_API_THREE_FORMATTER_OBSERVATION' and receipt['phase']==phase
        assert receipt['observation_only'] is True and receipt['product_pass'] is False and receipt['observation_complete'] is True
        assert receipt['source_and_CORE_unchanged'] is True and 'fatal_error' not in receipt
        assert receipt['runner']['sha256']==PROBE_SHA and receipt['fixture']['sha256']==INPUT_SHA
        assert receipt['actual_completed_cases']==22 and receipt['actual_public_calls']==88 and receipt['actual_native_records']==110
        assert receipt['consumer_error_count']==0 and receipt['CORE_before']==receipt['CORE_after']==extra
        actual_guard=Path(receipt['guard']['path']);actual_guard_raw=actual_guard.read_bytes();actual_guard_data=json.loads(actual_guard_raw)
        assert sha(actual_guard_raw)==receipt['guard']['sha256'] and len(actual_guard_raw)==receipt['guard']['bytes']
        assert actual_guard_data['section']==113 and receipt['source_before']==receipt['source_after']==actual_guard_data['source_sha256']
        assert actual_guard_data['source_additional_sha256']==extra
        if phase=='candidate':assert actual_guard_raw==guard_raw and receipt['source_after']==expected
        refs=receipt['records'];assert len(refs)==110 and len({r['path'] for r in refs})==110
        assert [json.loads(line) for line in (folder/'native/index.jsonl').read_text().splitlines()]==refs
        assert len(receipt['calls'])==88 and [r['id'] for r in receipt['rows']]==[r['id'] for r in cases]
        values={}
        for ref in refs:
            value=read_record(folder/'native',ref);records_decoded+=1;values[(ref['case'],ref['phase'])]=value
            exact(value['after'],value['before'],'complete actual per-call/case caller purity')
            assert ref['kind'] in ('actual-public-consumer','whole-case-caller')
            if ref['kind']=='actual-public-consumer':assert value['error'] is None
        assert len(values)==110
        result={}
        for i,case in enumerate(cases):
            identity=case['id'];numeric=values[(identity,PHASES[0])];whole=values[(identity,'caller')]
            assert receipt['rows'][i]['calculate_error'] is None and receipt['rows'][i]['formatters_blocked'] is False
            exact(numeric['before'],(case['scenario'],),'whole original fixture numeric caller')
            exact(whole['before'],case['scenario'],'whole original fixture case caller');texts=[]
            for j,phase_name in enumerate(PHASES):
                call=receipt['calls'][i*4+j];assert (call['case'],call['phase'])==(identity,phase_name)
                assert call['native']==refs[i*5+j] and call['caller_unchanged'] is True and call['error'] is None
                if j:
                    saved=values[(identity,phase_name)];exact(saved['before'],(numeric['result'],),'whole formatter result graph')
                    assert type(saved['result']) is str;texts.append(saved['result'])
            assert texts[0]==texts[1];result[identity]={'result':numeric['result'],'caller':numeric['before'][0],'texts':texts}
        proof_raw[phase+'_primary']=primary_raw;proof_raw[phase+'_receipt']=receipt_raw;proof_raw[phase+'_guard']=actual_guard_raw
        receipts[phase]=receipt;return result
    original=observation(args.original,'original',args.original_exit);candidate=observation(args.candidate,'candidate',args.candidate_exit)
    def restore_denominator(old,new,scenario):
        before=old['estimate']['skill'];after=new['estimate']['skill'];normalized=freeze(new)
        exact(after['window_seconds'],float(scenario['window_seconds']),'exact requested finite ammo observation domain')
        for key in METRICS:
            assert (key in before)==(key in after)
            if key not in before:continue
            if key!='window_seconds':
                numerator=after.get('window_damage',new['total_damage']) if key=='window_dps' else after['window_healing']
                value=numerator/after['window_seconds'] if numerator is not None and after['window_seconds'] else None
                exact(after[key],value,'Source exact published window numerator/denominator')
                assert (before[key] is None)==(after[key] is None) and type(before[key]) is type(after[key])
            normalized['estimate']['skill'][key]=before[key]
        for name,metric,numerator in (('known_damage_subtotals','window_dps','window_damage'),('known_healing_subtotals','window_hps','window_healing')):
            assert (name in old)==(name in new)
            if name in new:
                exact(new[name][metric],new[name][numerator]/after['window_seconds'] if after['window_seconds'] else None,'exact known subtotal denominator')
                normalized[name][metric]=old[name][metric]
        assert len(old['report']['sections'])==len(new['report']['sections'])
        for index,(old_section,new_section) in enumerate(zip(old['report']['sections'],new['report']['sections'])):
            assert old_section['id']==new_section['id'] and len(old_section['metrics'])==len(new_section['metrics'])
            for j,(old_metric,new_metric) in enumerate(zip(old_section['metrics'],new_section['metrics'])):
                assert old_metric['key']==new_metric['key']
                if old_section['id'] in ('damage','healing') and new_metric['key'] in METRICS:
                    key=new_metric['key'];value=after['window_seconds']
                    if key!='window_seconds':
                        numerator=after.get('window_damage',new['total_damage']) if key=='window_dps' else after['window_healing']
                        value=numerator/after['window_seconds'] if numerator is not None and after['window_seconds'] else None
                    exact(new_metric['value'],value,'exact denominator-derived report metric')
                    normalized['report']['sections'][index]['metrics'][j]['value']=old_metric['value']
        exact(normalized,old,'whole remainder exact: cast/phase/cycle/SP/components/timing/unknowns/provenance/report metadata')
        if native090(new)==native090(old):return False
        return True
    for case in cases:
        identity=case['id'];exact(candidate[identity]['caller'],original[identity]['caller'],'same complete original/candidate callers')
        changed=restore_denominator(original[identity]['result'],candidate[identity]['result'],case['scenario'])
        if not changed:exact(candidate[identity]['texts'],original[identity]['texts'],'all three complete unchanged texts')
        case_checks.append({'id':identity,'only_window_denominator_leaves_changed':True,'actual_changed':changed})
    mapping=load(TEMPLATE);assert [r['literal_index'] for r in mapping['rows']]==list(INDICES);audit_rows=[]
    for admitted in mapping['rows']:
        index=admitted['literal_index'];literal=literals[index];identity=f'legacy-full-window-row-{index}'
        old=original[identity];new=candidate[identity];old_projection=projection090(old['result']);new_projection=projection090(new['result'])
        assert digest(literal)==admitted['full_source_row_sha256_json_ordered'] and digest(literal['input'])==admitted['input_sha256_json_ordered']
        for name in ('section','pair_id','widget_checked'):assert literal[name]==admitted[name] and type(literal[name]) is type(admitted[name])
        assert native090(old_projection)==native090(literal['expected_public_projection'])
        for key,value in literal['input'].items():exact(old['caller'][key],value,'entire historical requested input field')
        normalized=freeze(new_projection);old_skill=old_projection['estimate']['skill'];new_skill=new_projection['estimate']['skill'];changed=[]
        for name in METRICS:
            leaf=admitted['metric_leaf_admission']['estimate.skill.'+name];before=scalar(name in old_skill,old_skill.get(name));after=scalar(name in new_skill,new_skill.get(name))
            assert before==scalar(leaf['old_present'],leaf['old_source_value']) and before['python_type']==leaf['old_python_type'] and before['float_hex']==leaf['old_float_hex']
            assert before['present'] is after['present'] and before['python_type']==after['python_type']
            is_changed=encoded(before)!=encoded(after)
            if name=='window_hps':assert not is_changed
            if name=='window_seconds':assert after==scalar(True,literal['input']['window_seconds']) and is_changed
            leaf.update(actual_candidate_present=after['present'],actual_candidate_python_type=after['python_type'],actual_candidate_value=after['value'],actual_candidate_float_hex=after['float_hex'],actual_changed=is_changed)
            if is_changed:normalized['estimate']['skill'][name]=old_skill[name];changed.append(name)
        exact(normalized,old_projection,'whole measured legacy projection except only measured seconds/DPS')
        assert changed and 'window_seconds' in changed
        for field,value in (('original_projection',old_projection),('candidate_projection',new_projection),('original_caller',old['caller']),('candidate_caller',new['caller'])):
            admitted[field+'_native090_sha256']=digest(native090(value))
        assert admitted['original_caller_native090_sha256']==admitted['candidate_caller_native090_sha256']
        admitted.update(expected_mapping_ready=True,Root_actual_original_receipt_sha256=sha(proof_raw['original_receipt']),Root_actual_candidate_receipt_sha256=sha(proof_raw['candidate_receipt']))
        audit_rows.append({key:admitted[key] for key in ('literal_index','full_source_row_sha256_json_ordered','input_sha256_json_ordered','original_projection_native090_sha256','candidate_projection_native090_sha256','original_caller_native090_sha256','candidate_caller_native090_sha256')})
        audit_rows[-1]['metric_leaf_admission_sha256']=digest(admitted['metric_leaf_admission'])
    check_source()
    audit={'kind':'ROOT_ACTUAL_113_SAME_INPUT_PROJECTION_AUDIT','passed':True,'workflow_complete':True,'source_drift':[],
        'literal_indices':list(INDICES),'same_full_callers':True,'only_measured_window_metric_leaves_changed':True,
        'caller_and_three_formatter_purity':True,'whole_source_and_CORE_stable':True,'rows':audit_rows,
        'actual_API_cases_per_phase':22,'actual_API_calls_per_phase':88,'actual_native_records_decoded':records_decoded,
        'all22_case_checks':case_checks,'runner_sha256':sha(Path(__file__).read_bytes()),
        'scope':'42 unchanged historical projections;10 protected projections with explicit proved113 window-metric exceptions',
        'native090_scope':'Ordered type/floatbits tree; internal alias/caller purity independently checked by strict native helper.',
        'native_windows_game_chat_verified':False,'actual_full115_runtime_claimed':False}
    assert records_decoded==220;proof_raw['pair_audit']=encoded(audit)+b'\n'
    for admitted in mapping['rows']:admitted['Root_actual_pair_audit_sha256']=sha(proof_raw['pair_audit'])
    mapping.update(kind='ROOT_ACTUAL_113_NARROW_WINDOW_METRIC_ADMISSION',ready=True,runtime_executed=True,product_pass=False,
        actual113_original_guard_sha256=sha(proof_raw['original_guard']),actual113_candidate_guard_sha256=sha(proof_raw['candidate_guard']),
        Root_actual_original_primary_exit_sha256=sha(proof_raw['original_primary']),Root_actual_candidate_primary_exit_sha256=sha(proof_raw['candidate_primary']),
        proof_files={name:{'path':'proofs/'+name.replace('_','-')+('.exit-code' if name.endswith('_primary') else '.json'),
                           'bytes':len(raw),'sha256':sha(raw)} for name,raw in proof_raw.items()})
    assert mapping['future_actual115_guard_sha256'] is None and len(mapping['proof_files'])==7
    out.mkdir();(out/'proofs').mkdir()
    for name,raw in proof_raw.items():
        with (out/mapping['proof_files'][name]['path']).open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    write(out/'expected-map115.json',mapping);write(out/'receipt.json',audit);check_source()
    print(json.dumps({'passed':True,'cases_per_phase':22,'native_records_decoded':220,'measured_admissions':10}))

if __name__=='__main__':main()
