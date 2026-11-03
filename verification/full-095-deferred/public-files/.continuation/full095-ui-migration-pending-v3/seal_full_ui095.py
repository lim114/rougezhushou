"""Root-only stdlib binding after actual095 apply and completed actual94 baseline.

No imports or execution of project, runner, Qt, native codec, tests or Wine.
CLI: python seal_full_ui095.py --guard ACTUAL_GUARD --binding REVIEWED_BINDING_JSON --output-directory NEW_FINAL_DIRECTORY
"""
import argparse, ast, base64, hashlib, json
from pathlib import Path

PACKET=Path(__file__).resolve().parent
EXPECTED_ORIGINAL='9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9'
EXPECTED_CODE_MANIFEST='216d5c31a9bc89dbc51f0b875db073a4fe8ea8b85fb5c9b624f5d9d6f56a461a'
sha=lambda data:hashlib.sha256(data).hexdigest()
def read(record):
    path=Path(record['path']).resolve()
    assert str(path).startswith('/workspace/'),('Only explicitly bound public workspace artifacts',str(path))
    data=path.read_bytes();assert sha(data)==record['sha256'],str(path)
    if 'bytes' in record:assert len(data)==record['bytes'],str(path)
    return data
def windows_path(path):
    assert str(path).startswith('/workspace/')
    return 'Z:'+str(path).replace('/','\\')
def pointer(value,path):
    if path=='':return value
    assert path.startswith('/')
    for key in path[1:].split('/'):
        key=key.replace('~1','/').replace('~0','~')
        value=value[int(key)] if type(value) is list else value[key]
    return value
def metadata(path):
    data=path.read_bytes();return {'path':str(path),'bytes':len(data),'sha256':sha(data)}
def dump_new(path,value):
    data=json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2).encode()+b'\n'
    with path.open('xb') as handle:handle.write(data)
    return {'file':path.name,'bytes':len(data),'sha256':sha(data)}

parser=argparse.ArgumentParser();parser.add_argument('--guard',type=Path,required=True);parser.add_argument('--binding',type=Path,required=True);parser.add_argument('--output-directory',type=Path,required=True);args=parser.parse_args()
assert not args.output_directory.exists(),'FINAL directory must be new; no overwrite or implicit rerun'
mf=json.loads((PACKET/'public-artifacts-manifest-pending095.json').read_text())
assert mf['status']=='STOPWRITE_PENDING_FULL095_UI_SOURCE_ONLY_RUNTIME_UNRUN'
for name,row in mf['artifacts'].items():assert len((PACKET/name).read_bytes())==row['bytes'] and sha((PACKET/name).read_bytes())==row['sha256'],name
pending=(PACKET/'wine-full-ui-095-pending.py').read_bytes();ledger=json.loads((PACKET/'exact-inverse-ledger095.json').read_text());recovered=pending
for row in reversed(ledger['operations']):
    start=row['pending_byte_start'];end=start+row['pending_byte_count'];assert sha(recovered[start:end])==row['pending_sha256'];recovered=recovered[:start]+base64.b64decode(row['before_base64'])+recovered[end:]
assert len(recovered)==729181 and sha(recovered)==EXPECTED_ORIGINAL
guard_record=metadata(args.guard.resolve());guard=json.loads(read(guard_record))
assert guard['passed'] is True and guard['candidate_bytes_exact'] is True
mapping=guard['source_sha256_after'];assert len(mapping)==guard['current_maintained']
repo=Path('/workspace/rougezhushou')
actual_mapping={path.relative_to(repo).as_posix():sha(path.read_bytes())
                for folder in ('rouge','tests','scripts') for path in sorted((repo/folder).rglob('*'))
                if path.is_file() and path.suffix in ('.py','.json') and '__pycache__' not in path.parts}
assert actual_mapping==mapping,'Full actual maintained selector mismatch, including new/deleted keys'
binding=json.loads(args.binding.read_text());assert binding['status']=='ROOT_BOUND_ACTUAL095_AND_ACTUAL94_BASELINE'
binding['source_guard']=guard_record
assert binding['candidate_manifest']['sha256']==EXPECTED_CODE_MANIFEST
code_manifest=json.loads(read(binding['candidate_manifest']))
for row in code_manifest['files']:
    assert sha((repo/row['destination_repo_path']).read_bytes())==row['sha256']
    assert len((repo/row['destination_repo_path']).read_bytes())==row['bytes']
    assert mapping[row['destination_repo_path']]==row['sha256']
# The full actual maintained map is authoritative. Additional formally reviewed test
# adaptation(s) may change other maintained paths while the five product payloads stay exact.
# No changed-path count, two-old-path whitelist, predicted735 guard or clean-Git gate.
for artifact in binding.get('additional_formal_artifacts',[]):
    document=json.loads(read(artifact))
    for row in artifact['source_targets']:
        assert mapping[row['destination_repo_path']]==row['sha256']
        assert sha((repo/row['destination_repo_path']).read_bytes())==row['sha256']
        if 'bytes' in row:assert len((repo/row['destination_repo_path']).read_bytes())==row['bytes']
    review=json.loads(read(artifact['formal_review']))
    assert pointer(review,artifact['formal_review_pass_pointer']) is True
freeze=json.loads(read(binding['implementation_freeze']))
assert freeze['report_addition_key']=='selected_module_source_reference' and freeze['notes_only_section']['id']=='selected_module_source'
correction=json.loads(read(binding['technical_tail_correction_artifact']))
assert correction['actual_complete_append_tail_prefix']=='\n\n【所选模组原件追溯】\n'
assert correction['exact_code_product_manifest_sha256']==EXPECTED_CODE_MANIFEST
assert binding['report_contract']['reference_key']=='selected_module_source_reference' and binding['report_contract']['section_id']=='selected_module_source'
assert binding['report_contract']['technical_tail_prefix']==correction['actual_complete_append_tail_prefix']
assert binding['actual94_guard']['sha256']=='259370708fe45e974511d1c1c010901d66981ee9dc2d53e7bce1ac978d463211'
assert binding['actual94_receipt']['sha256']=='55dba304fe8075531e92de36f369c142f790da59ef69091edffc28299b97bac5'
assert json.loads(read(binding['actual94_receipt']))['workflow_complete'] is True
read(binding['actual94_guard'])
baseline_receipt=json.loads(read(binding['baseline_receipt']))
assert baseline_receipt['passed'] is True,'Source preflight or incomplete baseline is insufficient'
assert binding['baseline_source_guard_sha256']==binding['actual94_guard']['sha256']
assert binding['baseline_saved_verifier_passed'] is True and binding['baseline_process_status_provenance']
assert binding['baseline_saved_verifier'] and json.loads(read(binding['baseline_saved_verifier']))['passed'] is True
assert binding['actual95_section_completed'] is False,'This is admission before full095 runtime completion'
documents={}
import gzip
for row in binding['baseline_files']:
    data=read(row)
    assert row['encoding'] in ('json','gzip_json')
    if row['encoding']=='gzip_json':data=gzip.decompress(data)
    documents[row['name']]=json.loads(data)
plan=json.loads((PACKET/'full095-subgroup-plan.json').read_text())
assert [case['id'] for case in binding['cases']]==[case['id'] for case in plan['steps']]
assert all(case['step']==proposed['step'] and case['comparison']==proposed['comparison'] for case,proposed in zip(binding['cases'],plan['steps']))
assert binding['public_run_initial']==plan['public_run_initial'] and binding['qualified_callback_widgets']==['defense']
provenance={}
for row in binding['qualified_reference_provenance']:
    document=json.loads(read(row));provenance[row['name']]=document
assert provenance,'Actual qualified new report reference/section/text evidence must be bound'
for case in binding['cases']:
    if case['comparison']=='same_action_auto_manual':continue
    baseline=pointer(documents[case['baseline_file']],case['baseline_pointer']);assert baseline['id']==case['id'] and baseline['passed'] is True
    assert baseline['planned']['JSON_projection']==case['step']
    delta=case['delta']
    if not delta['has_addition']:
        assert not delta.get('reference_path') and not delta.get('text_insertions')
        continue
    assert delta['reference_path']==['result','report','selected_module_source_reference']
    assert delta['sections_path']==['result','report','sections'] and delta['section_id']=='selected_module_source' and delta['section_id_key']=='id'
    qualified=pointer(provenance[delta['provenance_file']],delta['provenance_pointer'])
    for key in ('expected_reference_native','expected_section_native','text_insertions'):assert delta[key]==qualified[key]
    assert qualified['actual95_source_guard_sha256']==guard_record['sha256'] and qualified['actual94_full_native_and_existing_report_exact'] is True
    assert qualified['independent_raw_source_qualified'] is True
    for mode in ('estimate','default','technical'):
        insertions=delta['text_insertions'][mode];assert insertions
        for insertion in insertions:assert type(insertion['offset']) is int and type(insertion['text']) is str and insertion['text'] and sha(insertion['text'].encode())==insertion['sha256']
    # Require the full exact technical tail, not a whitespace-normalized or generic stripped suffix.
    assert any(insertion['text'].startswith(correction['actual_complete_append_tail_prefix']) for insertion in delta['text_insertions']['technical'])
pending_binding=json.loads((PACKET/'pending-binding095.json').read_text())
for key in ('source_guard','candidate_manifest','implementation_freeze','technical_tail_correction_artifact','actual94_receipt','actual94_guard','baseline_receipt','baseline_saved_verifier'):
    if binding.get(key) is not None:binding[key]={**binding[key],'path':windows_path(binding[key]['path'])}
for key in ('baseline_files','qualified_reference_provenance'):
    binding[key]=[{**row,'path':windows_path(row['path'])} for row in binding[key]]
binding['additional_formal_artifacts']=[{**row,'path':windows_path(row['path']),'formal_review':{**row['formal_review'],'path':windows_path(row['formal_review']['path'])}} for row in binding.get('additional_formal_artifacts',[])]
old_flag=b'PENDING095 = True';new_flag=b'PENDING095 = False'
old_binding=('BINDING095 = '+repr(pending_binding)+'\n').encode();new_binding=('BINDING095 = '+repr(binding)+'\n').encode()
assert pending.count(old_flag)==1 and pending.count(old_binding)==1
final=pending.replace(old_flag,new_flag,1).replace(old_binding,new_binding,1);ast.parse(final.decode())
assert final.replace(new_binding,old_binding,1).replace(new_flag,old_flag,1)==pending
args.output_directory.mkdir(parents=True)
runner_path=args.output_directory/'wine-full-ui-095-final.py'
with runner_path.open('xb') as handle:handle.write(final)
runner={'file':runner_path.name,'bytes':len(final),'sha256':sha(final)}
binding_row=dump_new(args.output_directory/'root-bound-input095.json',binding)
proof=dump_new(args.output_directory/'final-source-inverse095.json',{'schema':'full-ui095-final-binding-and-exact-inverse-v1','runner':runner,'pending_runner_sha256':sha(pending),'pending_manifest_sha256':sha((PACKET/'public-artifacts-manifest-pending095.json').read_bytes()),'pending_inverse_ledger_sha256':sha((PACKET/'exact-inverse-ledger095.json').read_bytes()),'final_binding_substitutions':2,'binding_reverse_restores_pending_byteexact':True,'pending_reverse_restores_original729181':EXPECTED_ORIGINAL,'root_guard_sha256':guard_record['sha256'],'runtime_project_codec_Qt_Wine_calls':0})
artifacts={row['file']:{k:v for k,v in row.items() if k!='file'} for row in (runner,binding_row,proof)}
final_mf=dump_new(args.output_directory/'public-artifacts-manifest-final095.json',{'format_version':1,'status':'STOPWRITE_FINAL_SOURCE_BOUND_ROOT_FRESH_FORMAL_REVIEW_AND_SOLE_RUNTIME_REQUIRED','artifacts':artifacts,'root_source_guard_sha256':guard_record['sha256'],'actual095_completed':False,'runtime_calls':0})
handoff=dump_new(args.output_directory/'handoff-final095.json',{'status':'FINAL_SOURCE_ONLY_RUNTIME_UNRUN_ROOT_FORMAL_REVIEW_REQUIRED','runner':runner,'manifest':final_mf,'actual_root_guard_sha256':guard_record['sha256'],'original_inverse_sha256':EXPECTED_ORIGINAL,'Wine_command_template':"/workspace/.compat/run-wine-python.sh '"+windows_path(runner_path)+"' > /workspace/.continuation/root-window-095.log 2>&1",'runtime_receipt':'/workspace/.compat/wine-ui-095.json','native_index':'/workspace/.compat/full095-ui-native-v3/wine-ui-full-native-index-095.json','fresh_native_directory':'/workspace/.compat/full095-ui-native-v3','section_completed':False,'STOPWRITE':True})
print(json.dumps({'runner':runner,'manifest':final_mf,'handoff':handoff,'root_source_guard_sha256':guard_record['sha256'],'runtime':0},ensure_ascii=False))
