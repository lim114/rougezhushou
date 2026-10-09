"""Stdlib only; root supplies completed093 receipt and actual applied094 guard later."""
import argparse,ast,hashlib,json
from pathlib import Path

def sha(data):return hashlib.sha256(data).hexdigest()
def write_json(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def pointer(value,source_pointer):
    assert source_pointer.startswith('/')
    for part in source_pointer[1:].split('/'):
        part=part.replace('~1','/').replace('~0','~')
        value=value[int(part)] if isinstance(value,list) else value[part]
    return value
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--actual-guard',required=True,type=Path)
    parser.add_argument('--expected-guard-sha256',required=True)
    parser.add_argument('--completed093-receipt',required=True,type=Path)
    parser.add_argument('--expected-completed093-receipt-sha256',required=True)
    parser.add_argument('--completed093-success-pointer',required=True,help='Exact JSON pointer supplied by root from the actual completed093 receipt schema; no guessed filename/schema')
    parser.add_argument('--completed093-workflow-complete-pointer',required=True,help='Exact actual receipt JSON pointer whose value must be true')
    parser.add_argument('--repo',type=Path,default=Path('/workspace/rougezhushou'))
    parser.add_argument('--output',type=Path,default=Path('/workspace/.continuation/ui-094-offline-input-refresh-final-v2'))
    args=parser.parse_args();base=Path(__file__).resolve().parent
    assert not args.output.exists(),'Never overwrite a frozen final packet'
    pending=base/'wine-focused-inputs-094-pending.py';pending_bytes=pending.read_bytes();pending_text=pending_bytes.decode('utf-8')
    pending_tree=ast.parse(pending_text);assert isinstance(pending_tree.body[0],ast.Assign) and pending_tree.body[0].value.value is True
    declared=json.loads((base/'public-artifacts-manifest-pending094.json').read_text(encoding='utf-8'))
    for rel,info in declared['artifacts'].items():
        data=(base/rel).read_bytes();assert len(data)==info['bytes'] and sha(data)==info['sha256'],rel
    actual_guard_bytes=args.actual_guard.read_bytes();assert sha(actual_guard_bytes)==args.expected_guard_sha256
    actual_guard=json.loads(actual_guard_bytes);predicted=json.loads((base/'wine-focused-inputs-094-pending-source.json').read_text(encoding='utf-8'))
    assert actual_guard['passed'] is True and len(actual_guard['source_sha256_after'])==732
    assert actual_guard['source_sha256_after']==predicted['source_sha256_after'],'Actual094 guard must equal exact predicted732 mapping; drift requires requalification'
    for rel,digest_value in actual_guard['source_sha256_after'].items():assert sha((args.repo/rel).read_bytes())==digest_value,rel
    completion_bytes=args.completed093_receipt.read_bytes();assert sha(completion_bytes)==args.expected_completed093_receipt_sha256
    completion=json.loads(completion_bytes)
    assert pointer(completion,args.completed093_success_pointer) is True
    assert pointer(completion,args.completed093_workflow_complete_pointer) is True
    replacements=[('PENDING_PREPARATION = True','PENDING_PREPARATION = False'),
        ("EXPECTED_GUARD_SHA256='PENDING_ROOT_ACTUAL_094_SOURCE_GUARD'","EXPECTED_GUARD_SHA256='"+args.expected_guard_sha256+"'"),
        ("GUARD=Path(__file__).with_name('wine-focused-inputs-094-pending-source.json')","GUARD=Path(__file__).with_name('wine-focused-inputs-094-source.json')")]
    final_text=pending_text
    for old,new in replacements:assert final_text.count(old)==1;final_text=final_text.replace(old,new,1)
    inverse=final_text
    for old,new in reversed(replacements):assert inverse.count(new)==1;inverse=inverse.replace(new,old,1)
    assert inverse.encode('utf-8')==pending_bytes,'Only three binding substitutions permitted'
    ast.parse(final_text);final_bytes=final_text.encode('utf-8');args.output.mkdir()
    (args.output/'wine-focused-inputs-094-final.py').write_bytes(final_bytes)
    (args.output/'wine-focused-inputs-094-pending-original.py').write_bytes(pending_bytes)
    (args.output/'wine-focused-inputs-094-plan.json').write_bytes((base/'wine-focused-inputs-094-plan.json').read_bytes())
    (args.output/'wine-focused-inputs-094-source.json').write_bytes(actual_guard_bytes)
    (args.output/'source-preflight094.json').write_bytes((base/'source-preflight094.json').read_bytes())
    (args.output/'source-correction-byte-evidence094.json').write_bytes((base/'source-correction-byte-evidence094.json').read_bytes())
    diagnostic={'format_version':1,'status':'THREE_BINDINGS_ONLY_ACTUAL_ROOT094_SOURCE_BOUND_FRESH_FINAL_REVIEW_PENDING_RUNTIME_UNRUN',
        'pending_runner_sha256':sha(pending_bytes),'final_runner_sha256':sha(final_bytes),'inverse_restores_pending_byteexact':True,
        'replacement_count':3,'changes':[{'before':old,'after':new} for old,new in replacements],
        'actual094_guard':{'path':str(args.actual_guard),'bytes':len(actual_guard_bytes),'sha256':sha(actual_guard_bytes)},
        'completed093_receipt':{'path':str(args.completed093_receipt),'bytes':len(completion_bytes),'sha256':sha(completion_bytes),
            'success_pointer':args.completed093_success_pointer,'workflow_complete_pointer':args.completed093_workflow_complete_pointer},
        'project_imports':0,'project_API_calls':0,'helper_calls':0,'formatter_calls':0,'codec_executions':0,'Qt_calls':0,'Wine_calls':0,'tests_executed':0,'tracked_writes':0,
        'final_source_only_review_role':'root-appointed fresh final reviewer pending; earlier development preflight is not formal approval'}
    write_json(args.output/'binding-diagnostic094.json',diagnostic)
    names=('wine-focused-inputs-094-final.py','wine-focused-inputs-094-pending-original.py','wine-focused-inputs-094-plan.json',
        'wine-focused-inputs-094-source.json','source-preflight094.json','source-correction-byte-evidence094.json','binding-diagnostic094.json')
    artifacts={name:{'bytes':len((args.output/name).read_bytes()),'sha256':sha((args.output/name).read_bytes())} for name in names}
    manifest={'format_version':1,'status':'FINAL_SOURCE_BOUND_FRESH_FINAL_SOURCE_ONLY_REVIEW_PENDING_RUNTIME_UNRUN',
        'artifacts':artifacts,'artifact_count_excluding_manifest_and_handoff':len(artifacts),
        'total_artifact_bytes_excluding_manifest_and_handoff':sum(info['bytes'] for info in artifacts.values()),
        'actual094_guard_sha256':args.expected_guard_sha256,'runtime_passes':0,'section094_completed':False,'root_sole_Wine_executor':True,'STOPWRITE_after_seal':True}
    write_json(args.output/'public-artifacts-manifest-focused-inputs094.json',manifest)
    handoff={'format_version':1,'status':manifest['status'],'manifest':{'path':'public-artifacts-manifest-focused-inputs094.json',
        'bytes':(args.output/'public-artifacts-manifest-focused-inputs094.json').stat().st_size,'sha256':sha((args.output/'public-artifacts-manifest-focused-inputs094.json').read_bytes())},
        'runner':{'path':'wine-focused-inputs-094-final.py',**artifacts['wine-focused-inputs-094-final.py']},
        'source':{'path':'wine-focused-inputs-094-source.json',**artifacts['wine-focused-inputs-094-source.json']},
        'completed093_receipt':diagnostic['completed093_receipt'],'required_next':'Root appoints fresh final source-only reviewer, then root alone executes actual Wine and independently validates saved native/JSON/3texts and views three PNGs.',
        'no_runtime_pass_claim':True,'root_sole_tracked_writer':True,'STOPWRITE_after_seal':True}
    write_json(args.output/'handoff-focused-inputs094.json',handoff)
    for name,info in artifacts.items():assert len((args.output/name).read_bytes())==info['bytes'] and sha((args.output/name).read_bytes())==info['sha256']
    print(json.dumps({'status':manifest['status'],'directory':str(args.output),'runner_sha256':sha(final_bytes),
        'manifest_sha256':sha((args.output/'public-artifacts-manifest-focused-inputs094.json').read_bytes()),
        'handoff_sha256':sha((args.output/'handoff-focused-inputs094.json').read_bytes())},ensure_ascii=False))
if __name__=='__main__':main()
