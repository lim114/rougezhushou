"""Independent276 repair/source review using public literals and file bytes.

Does not invoke the game, native DLL, process memory, Qt, chat or private state.
The originalc2 fixtures and new-schema counterexample remain untouched.
"""
from copy import deepcopy
import argparse
import hashlib,json,mmap,sys
from pathlib import Path

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge import sp_initialization_reference as module

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dll-path',required=True,type=Path)
parser.add_argument('--metadata-path',required=True,type=Path)
args=parser.parse_args()

Q=4294967296
OUTPUT=ROOT/'verification/sections/276-readonly-source-review.json'
ORIGINAL=ROOT/'.cache/section276-review-original'
FORMAL=ROOT/'.cache/section276-review-formal-before'
core_path=Path(module.__file__)
core_bytes=core_path.read_bytes()
core_sha=hashlib.sha256(core_bytes).hexdigest()
preserve_paths=(ORIGINAL/'core-before.py',ORIGINAL/'original-probes.json',
                FORMAL/'core-before.py',FORMAL/'new-copy-unknown-original.json')
preserve_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in preserve_paths}
old_cases=json.loads((ORIGINAL/'original-probes.json').read_text(encoding='utf-8'))['cases']
formal_case=json.loads((FORMAL/'new-copy-unknown-original.json').read_text(encoding='utf-8'))
probes=[]

def probe(name,payload,expected,*,basis='new public literal',original=None,migration=None):
    output=module.sp_initialization_reference(deepcopy(payload))
    checks=[]
    for path,value in expected.items():
        actual=output
        for key in path.split('.'):
            actual=actual[int(key)] if type(actual) is list else actual[key]
        checks.append({'path':path,'expected':value,'actual':actual,
                       'passed':type(actual) is type(value) and actual==value})
    probes.append({'name':name,'basis':basis,'input':payload,'original_input':original,
                   'input_exactly_same_as_original':payload==original if original is not None else None,
                   'schema_migration':migration,'actual_output':output,'checks':checks,
                   'passed':output['source_valid'] is True and all(x['passed'] for x in checks)})

def migrate_old_capacity(payload):
    p=deepcopy(payload);changes=[]
    for a in p['actions']:
        for key,value in (('first_max_read',20),('second_max_read',21)):
            if key not in a:continue
            capacity=a[key]
            normal=capacity.pop('max_decode_normally')
            capacity['max_decode_read']={'id':capacity['id']+'-review独立解码',
                                         'normal':normal,'value':value}
            changes.append({'capacity':key,'removed':'max_decode_normally',
                            'added_independent_read':deepcopy(capacity['max_decode_read']),
                            'qualification':'New explicit public literal; not an observation, an inferred roundtrip, or same-schema input.'})
    return p,changes

case=old_cases[0]
probe('original unknown allocation exact same input',deepcopy(case['input']),{
    'normal_return_reference':None,'rows.0.known_prefix_state_reference.timer.exists':False,
    'state_after_reference.timer.exists':None},basis='genuine same input as c2 original',original=case['input'])

case=old_cases[1];p,changes=migrate_old_capacity(case['input'])
probe('cost unknown continuation with explicit schema migration',p,{
    'normal_return_reference':None,'rows.0.capacity_reads.0.cost_decode_called_reference':True,
    'rows.0.capacity_reads.0.charges_decode_called_reference':None,
    'rows.0.capacity_reads.0.max_encode_called_reference':None,
    'rows.0.capacity_reads.0.getter_return_called_reference':None,
    'rows.0.capacity_reads.0.max_decode_called_reference':None},
    basis='schema migrated c2 input',original=case['input'],migration=changes)

case=old_cases[2];p,changes=migrate_old_capacity(case['input'])
probe('capacity path unknown with explicit schema migration',p,{
    'normal_return_reference':None,'rows.0.capacity_reads.0.cost_decode_called_reference':None,
    'rows.0.capacity_reads.0.charges_decode_called_reference':None,
    'rows.0.capacity_reads.0.max_encode_called_reference':None,
    'rows.0.capacity_reads.0.getter_return_called_reference':None,
    'rows.0.capacity_reads.0.max_decode_called_reference':None},
    basis='schema migrated c2 input',original=case['input'],migration=changes)

case=old_cases[3]
probe('original later conditional construction exact same input',deepcopy(case['input']),{
    'normal_return_reference':None,'rows.1.called_reference':None,
    'state_after_reference.timer.exists':None},basis='genuine same input as c2 original',original=case['input'])

probe('formal encoder unknown copy invocation exact same input',deepcopy(formal_case['input']),{
    'normal_return_reference':None,'rows.0.initial_sp_prefix.encoder_called_reference':True,
    'rows.0.initial_sp_prefix.encoder_normal_reference':None,
    'rows.0.initial_sp_prefix.sp_payload_copy_called_reference':None,
    'rows.0.initial_sp_prefix.copied_byte_count_reference':None},
    basis='genuine same input as first formal276 counterexample',original=formal_case['input'])

def init_payload():
    p=module.public_example();p['actions']=[p['actions'][1]]
    p['state']['timer']={'exists':True,'period_raw':Q,'remaining_raw':Q}
    return p

for normal,copy_called in ((False,False),(True,True)):
    p=init_payload();p['actions'][0]['single_encoder_normally']=normal
    probe('encoder qualification control '+str(normal),p,{
        'rows.0.initial_sp_prefix.sp_payload_copy_called_reference':copy_called,
        'rows.0.initial_sp_prefix.copied_byte_count_reference':40 if normal else None,
        'normal_return_reference':normal})

p=init_payload();a=p['actions'][0]
a['first_max_read']['max_decode_read']['value']=23
a['second_max_read']['max_decode_read']['value']=17
probe('independent decoded capacities differ from product',p,{
    'rows.0.capacity_reads.0.signed32_product_reference':20,
    'rows.0.capacity_reads.0.returned_max_sp_reference':23,
    'rows.0.capacity_reads.0.roundtrip_equality_reference':None,
    'rows.0.initial_sp_prefix.signed_min_reference':23,
    'rows.0.initial_sp_prefix.encoder_constructor_argument_raw_reference':98784247808,
    'rows.0.capacity_reads.1.signed32_product_reference':21,
    'rows.0.capacity_reads.1.returned_max_sp_reference':17,
    'state_after_reference.max_sp':17})

p=init_payload();a=p['actions'][0]
a['first_max_read']['cost_decode']['value']=0
a['first_max_read']['max_decode_read']['value']=None
probe('zero encoded input is not unknown decoded return zero',p,{
    'rows.0.capacity_reads.0.signed32_product_reference':0,
    'rows.0.capacity_reads.0.returned_max_sp_reference':None,
    'rows.0.initial_sp_prefix.signed_min_reference':None,
    'rows.0.initial_sp_prefix.encoder_constructor_argument_raw_reference':None})

for normal in (False,None):
    p=init_payload();a=p['actions'][0];a['first_max_read']['getter_returns_normally']=normal
    probe('opaque getter return blocks or conditionally precedes decode '+str(normal),p,{
        'rows.0.capacity_reads.0.max_encode_called_reference':True,
        'rows.0.capacity_reads.0.getter_return_called_reference':True,
        'rows.0.capacity_reads.0.max_decode_called_reference':False if normal is False else None,
        'normal_return_reference':normal})

p=init_payload();p['actions'][0]['first_max_read']['cost_decode']['normal']=False
probe('known first decode exception blocks later calls',p,{
    'rows.0.capacity_reads.0.cost_decode_called_reference':True,
    'rows.0.capacity_reads.0.charges_decode_called_reference':False,
    'rows.0.capacity_reads.0.max_encode_called_reference':False,
    'rows.0.capacity_reads.0.getter_return_called_reference':False,
    'rows.0.capacity_reads.0.max_decode_called_reference':False})

p=module.public_example();p['actions']=p['actions'][:1]
p['actions'][0]['timer_assign_normally']=False
probe('failed timer assignment cannot prove final pointer',p,{
    'normal_return_reference':False,'state_after_reference.timer.exists':None,
    'rows.0.known_prefix_state_reference.timer.exists':False})

p=module.public_example();p['actions']=p['actions'][:1]
p['actions'][0]['timer_allocate_normally']=False
probe('known allocation failure keeps old pointer',p,{
    'normal_return_reference':False,'state_after_reference.timer.exists':False,
    'rows.0.known_prefix_state_reference.timer.exists':False})

source=module.source_data()
if source is None:raise RuntimeError('Current bound source is invalid.')
primary=module.verify_primary_files(args.dll_path,args.metadata_path)
supplement_path=ROOT/'research/p2-sp-initialization-276/protected-integer-proof.json'
supplement=json.loads(supplement_path.read_text(encoding='utf-8'))
fresh={'supplemental_method_count':len(supplement['methods']),
       'supplemental_unique_instruction_count':supplement['unique_instruction_count'],
       'supplemental_checked_spans':0,'file_hashes':{},'passed':True}
for kind,path in (('dll',args.dll_path),('metadata',args.metadata_path)):
    with Path(path).open('rb') as handle,mmap.mmap(handle.fileno(),0,access=mmap.ACCESS_READ) as original:
        digest=hashlib.sha256(original).hexdigest();fresh['file_hashes'][kind]=digest
        if digest!=supplement[kind+'_sha256']:fresh['passed']=False
        for span in supplement['byte_spans']:
            if span['source']!=kind:continue
            at=span['physical_offset'];raw=bytes.fromhex(span['raw_hex'])
            if at<0 or original[at:at+len(raw)]!=raw:
                raise RuntimeError('Fresh supplemental bytes mismatch: '+span['label'])
            fresh['supplemental_checked_spans']+=1
fresh['passed']=fresh['passed'] and fresh['supplemental_checked_spans']==452
unchanged=core_path.read_bytes()==core_bytes
old_unchanged=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in preserve_hashes.items())
for p in probes:
    for key in ('actual_current_sp','complete_cycle','actual_attribute_values'):
        if p['actual_output'][key] is not None:p['passed']=False
review={'scope':'Independent necessary276 readonly repair/source review; schema migrations are labeled separately from genuine same-input checks.',
        'core_sha256':core_sha,'manifest_sha256':hashlib.sha256((ROOT/module.SOURCE).read_bytes()).hexdigest(),
        'review_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_artifacts_sha256':source['source_artifacts_sha256'],
        'primary_file_guard':primary,'supplemental_fresh_file_guard':fresh,
        'probe_count':len(probes),'check_count':sum(len(p['checks']) for p in probes),
        'probes':probes,'prior_source_and_counterexamples_sha256':preserve_hashes,
        'prior_source_and_counterexamples_unchanged':old_unchanged,
        'core_unchanged_during_review':unchanged,
        'passed':primary['passed'] and fresh['passed'] and unchanged and old_unchanged and all(p['passed'] for p in probes),
        'game_dll_executed':False,'process_memory_read':False,'private_state_used':False,
        'game_or_chat_operated':False,'window_run':False,
        'remaining_unknown':['Actual SP/codec keys/protected payloads and live callbacks',
                             'Full initialization/skill clock and real game observations'],
        'substantive_findings':[{'probe':p['name'],'failed_checks':[c for c in p['checks'] if not c['passed']]}
                                for p in probes if not p['passed']]}
if OUTPUT.exists():raise RuntimeError('Do not overwrite the original276 review receipt.')
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
OUTPUT.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':review['passed'],'probes':review['probe_count'],'checks':review['check_count'],
                  'fresh_spans':primary['checked_spans']+fresh['supplemental_checked_spans'],
                  'core_sha256':core_sha,'receipt_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
                  'findings':review['substantive_findings']},ensure_ascii=False))
sys.exit(0 if review['passed'] else 1)
