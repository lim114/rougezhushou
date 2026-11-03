"""Independent FINAL-byte Source review; reviewed code is never executed."""
import ast
import base64
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BASE=Path('/workspace/.continuation')
FINAL=BASE/'full095-ui-identity-evidence-final-v1'
OUT=BASE/'full095-ui-identity-evidence-final-independent-source-review-v1'
SEEN={}
CHECKS=[]
def digest(raw): return hashlib.sha256(raw).hexdigest()
def ref(path):
    p=Path(path)
    assert p.is_absolute() and p.is_file() and not p.is_symlink() and str(p.resolve())==str(p)
    raw=p.read_bytes(); row={'path':str(p),'bytes':len(raw),'sha256':digest(raw)}
    assert str(p) not in SEEN or SEEN[str(p)]==row
    SEEN[str(p)]=row
    return row
def doc(path):
    row=ref(path)
    return json.loads(Path(path).read_bytes()),row
def check(name,evidence): CHECKS.append({'name':name,'passed':True,'scope':'Source/metadata only','evidence':evidence})
def funcs(raw):
    tree=ast.parse(raw); lines=raw.splitlines(keepends=True)
    return {n.name:b''.join(lines[n.lineno-1:n.end_lineno]) for n in tree.body if isinstance(n,ast.FunctionDef)}

old_report_path=BASE/'full095-identity-evidence-helpers-independent-source-review-v1/formal-independent-source-review-identity-evidence-helpers095.json'
old_report,old_report_ref=doc(old_report_path)
assert old_report_ref['sha256']=='7b16c189f1ea249ef45a8a4b72a9b847c53ca428770514a73d5f6f1841ff94f1'
assert old_report['source_gate_passed'] is True and old_report['runtime_executed'] is old_report['runtime_pass'] is False
assert old_report['actual_completed_archive_spec_sha256'] is None and old_report['blockers']==[]
for row in old_report['physical_refs']:
    assert ref(row['path'])==row
check('frozen_prior_independent_source_basis',{'report':old_report_ref,'passed_checks':old_report['passed_checks'],'all_prior_physical_inputs_reverified':True})

mf,mfref=doc(FINAL/'public-artifacts-manifest-source-preparation095.json')
assert mfref['bytes']==1781 and mfref['sha256']=='c8358918a38fd52b331d6b25826ee0ebf18b36b2e55b80b1368a22bd58d2dd3d'
assert mf['STOPWRITE'] is True and mf['runtime_calls']==0 and mf['runtime_pass'] is False
for row in mf['payload_files']:
    assert ref(row['path'])==row
hand,handref=doc(FINAL/'handoff-source-preparation095.json')
assert hand['manifest']==mfref and hand['runtime_calls']==0 and hand['actual_completed_archive_spec'] is None
assert hand['archive_commit_push_executed'] is False
assert {str(p) for p in FINAL.iterdir() if p.is_file()}=={r['path'] for r in mf['payload_files']}|{mfref['path'],handref['path']}
check('actual_final_manifest_handoff_and_exclusive_physical_set',{'manifest':mfref,'handoff':handref,'payload_count':len(mf['payload_files'])})

findings,findingsref=doc(FINAL/'source-findings095.json')
assert findings['target_executions']==0 and findings['runtime_pass'] is False
assert findings['actual_UI_primary_exit'] is findings['actual_Saved_primary_exit'] is findings['actual_finished_context_PASS'] is findings['actual_completed_archive_spec'] is None
for row in findings['all_checked_physical_inputs']:
    assert ref(row['path'])==row
check('all_root_sealer_input_fullrefs_physically_reverified',{'findings':findingsref,'input_ref_count':len(findings['all_checked_physical_inputs']),'runtime_claims_null':True})

actual_refs={k:findings[k] for k in ('source_binding','context_runner','actual_Root_prelaunch')}
expected_shas={'source_binding':'e818ba9aefa4d8cd739da561540ef2e49cbf38c70311346cd10c7b2d86be1bf6','context_runner':'07c011b1fa94a3def915f4ff0efeaa32c21b6e1d91e9f8c3d3ef9dbbd4ea39ef','actual_Root_prelaunch':'f4d21b549be1ae9faaa01603e740d4de3eedf87bee723d1e125bd9d57b4ca0c8'}
for key,row in actual_refs.items():
    assert ref(row['path'])==row and row['sha256']==expected_shas[key]
binding=json.loads(Path(actual_refs['source_binding']['path']).read_bytes())
pre=json.loads(Path(actual_refs['actual_Root_prelaunch']['path']).read_bytes())
assert binding['format_version']==3 and binding['status']=='SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS'
assert binding['actual_ui_retry'] is binding['actual_ui_identity_retry'] is binding['root_spec_projection_from_ui_retry'] is True
assert binding['available_checks_passed'] is False
assert binding['recovery_spec']['root_ui_prelaunch']==actual_refs['actual_Root_prelaunch']
assert pre['runner']==binding['root_spec']['ui']['runner']
assert pre['source_gate_passed'] is pre['outputs_absent'] is True and pre['runtime_pass'] is False
check('actual_identity_binding_context_and_third_prelaunch_identity',actual_refs)

contextmf,contextmfref=doc(BASE/'full095-regression-ui-identity-resume-final-v1/public-artifacts-manifest-sealed-recovery095.json')
assert actual_refs['source_binding'] in contextmf['payload_files'] and actual_refs['context_runner'] in contextmf['payload_files']
for row in contextmf['payload_files']:
    assert ref(row['path'])==row
check('actual_final_context_manifest_payload_fullrefs',{'manifest':contextmfref,'payload_count':len(contextmf['payload_files']),'contains_actual_binding_and_context':True})

helpers=hand['helpers']
expected_helpers={'assemble_actual_acceptance095.py':(18400,'4f88fab3fea9db443fa2f74f523b849e41da06abc8236821e21216aa904ca739'),'assemble_archive_spec095.py':(26472,'abfada1c927533c7b3355202e16425af43c841bf79e4cf0dd56a11b7321c483c'),'review_actual_archive_spec095.py':(40878,'ab24ff7de67b48aba471b934918ed0a048a701164299da67adab44f7d6fea698')}
inverses={}
for key,filename in [('acceptance','assemble_actual_acceptance095.py'),('archive','assemble_archive_spec095.py'),('reviewer','review_actual_archive_spec095.py')]:
    full=helpers[filename]; expected=expected_helpers[filename]
    assert ref(full['path'])==full and (full['bytes'],full['sha256'])==expected
    ledger=findings['inverses'][key]
    assert ledger['target_executions']==0 and ledger['exact_whole_byte_inverse'] is True
    assert ref(ledger['original']['path'])==ledger['original']
    old=Path(ledger['original']['path']).read_bytes(); new=Path(full['path']).read_bytes(); restored=new
    for op in reversed(ledger['operations']):
        start,count=op['pending_byte_start'],op['pending_byte_count']
        assert digest(restored[start:start+count])==op['pending_sha256']
        before=base64.b64decode(op['before_base64'],validate=True)
        assert digest(before)==op['before_sha256']
        restored=restored[:start]+before+restored[start+count:]
    assert restored==old
    if key=='acceptance':
        expected_raw=old.replace(b'__ACTUAL_UI_IDENTITY_RETRY_BINDING_SHA256_PENDING__',actual_refs['source_binding']['sha256'].encode(),1)
    elif key=='reviewer':
        expected_raw=old.replace(b"'__ACTUAL_UI_IDENTITY_RETRY_BINDING_FULL_REF_PENDING__'",repr(actual_refs['source_binding']).encode(),1)
        expected_raw=expected_raw.replace(b'__ACTUAL_UI_IDENTITY_RETRY_CONTEXT_RUNNER_SHA256_PENDING__',actual_refs['context_runner']['sha256'].encode(),1)
    else:
        expected_raw=old
    assert new==expected_raw
    compile(new,full['path'],'exec')  # Syntax only; never executed.
    before_funcs,after_funcs=funcs(old),funcs(new)
    assert before_funcs.keys()==after_funcs.keys()
    changed=[n for n in before_funcs if before_funcs[n]!=after_funcs[n]]
    assert changed==(['review'] if key=='reviewer' else [])
    inverses[key]={'original':ledger['original'],'actual_final':full,'exact_whole_byte_inverse':True,'operations':len(ledger['operations']),'functions_count':len(before_funcs),'functions_whole_unchanged':len(before_funcs)-len(changed),'functions_changed':changed}
check('three_actual_final_whole_inverses_and_independent_regeneration',inverses)

pending,pendingref=doc(BASE/'full095-archive-ui-identity-spec-source-v2/source-inputs095.json')
expected=copy.deepcopy(pending)
for key,source in [('recovery_binding','source_binding'),('recovery_runner','context_runner'),('ui_prelaunch','actual_Root_prelaunch')]:
    slot=expected['pinned_source_inputs'][key]
    assert slot['path']==actual_refs[source]['path'] and slot['bytes'] is slot['sha256'] is None
    expected['pinned_source_inputs'][key]=actual_refs[source]
expected['status']='ROOT_SEALED_IDENTITY_SOURCE_INPUTS_NOT_RUNTIME_PASS'
expected['actual_identity_final_refs_present']=True
expected['public_packets'].append({'manifest_path':contextmfref['path'],'manifest_sha256':contextmfref['sha256'],'payload_count':len(contextmf['payload_files']),'style':'payload_ref_rows','archive_prefix':'source-preparation/identity-FINAL-context095','numbered_section_completed':False,'public':True,'qualification':'Actual Root-sealed SOURCE, not runtime or section completion.'})
for i,info in enumerate(expected.pop('source_identity_required_extra_packets')):
    packet,pr=doc(info['path'])
    if info['style']=='local_artifact_dict':
        expected['public_packets'].append({'manifest_path':pr['path'],'manifest_sha256':pr['sha256'],'payload_count':len(packet['artifacts']),'style':'local_artifact_dict','archive_prefix':info['archive_prefix'],'numbered_section_completed':False,'public':True,'qualification':'Explicit frozen SOURCE, not runtime or numbered completion.'})
    else:
        assert info['style']=='flat_file_meta_dict'
        for name,row in packet['files'].items():
            expected['supplemental_public_inputs']['identity_Source_packet_%02d_%s'%(i,name.replace('.','_'))]=row
        expected['supplemental_public_inputs']['identity_Source_manifest_%02d'%i]=pr
config,configref=doc(FINAL/'source-inputs095.json')
assert config==expected
check('exact_config_null_to_actual_transform_no_other_schema_delta',{'pending_config':pendingref,'actual_final_config':configref,'three_real_slots_filled':True,'all_other_original_config_fields_preserved':True})

for key,row in config['pinned_source_inputs'].items():
    assert ref(row['path'])==row
for row in config['supplemental_public_inputs'].values():
    assert ref(row['path'])==row
for info in config['public_packets']:
    packet,pr=doc(info['manifest_path'])
    assert pr['sha256']==info['manifest_sha256'] and info['public'] is True and info['numbered_section_completed'] is False
    style=info['style']
    if style=='local_artifact_dict':
        rows=[{'path':str(Path(info['manifest_path']).parent/name),**row} for name,row in packet['artifacts'].items()]
    elif style in ('payload_ref_rows','payload_file_rows'):
        rows=[{k:row[k] for k in ('path','bytes','sha256')} for row in packet['payload_files']]
    elif style=='source_archive_rows':
        rows=[{'path':row['source_path'],'bytes':row['bytes'],'sha256':row['sha256']} for row in packet['files']]
    else:
        raise ValueError(style)
    assert len(rows)==info['payload_count']
    for row in rows: assert ref(row['path'])==row
check('every_final_config_fullref_and_supported_public_packet_style',{'supplemental_ref_count':len(config['supplemental_public_inputs']),'public_packet_count':len(config['public_packets']),'future_receipts_filled':False})

source={name:Path(row['path']).read_text() for name,row in helpers.items()}
for name,text in source.items():
    assert '__ACTUAL_UI_IDENTITY_RETRY_' not in text
    tree=ast.parse(text)
    imports=[a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
    imports += [n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
    assert set(imports)<= {'argparse','ast','base64','hashlib','json','re','stat','datetime','pathlib'}
check('actual_helper_slots_filled_stdlib_only_compile_without_execution',{'helper_refs':helpers,'target_executions':0})

guard=binding['root_spec']['completed_working_tree_chain'][-1]['source_guard']
assert guard['path']=='/workspace/rougezhushou/research/p2-section095-selected-module-source-report/root-source-095-v2.json'
assert ref(guard['path'])==guard and guard['bytes']==84227 and guard['sha256']=='41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
g=json.loads(Path(guard['path']).read_bytes())
assert g['source_sha256_after']==binding['actual_inputs']['source_sha256'] and len(g['source_sha256_after'])==735
check('archived_real_guard735_binding_exact_without_runtime_claim',{'guard':guard,'source_count':735})

recovery=binding['recovery_spec']
capsule=json.loads(Path(recovery['prior_incomplete_ui_cache']['path']).read_bytes())
assert ref(recovery['prior_incomplete_ui_cache']['path'])==recovery['prior_incomplete_ui_cache']
assert capsule['primary_exit_code'] is None and capsule['primary_exit_code_captured'] is False
assert capsule['native_outcome']=='pending' and capsule['same_UI_execution_problem_incomplete_attempt_count']==2 and capsule['third_attempt_failure_requires_deferral'] is True
assert len(capsule['all_closed_compressed_chunk_refs_verified'])==2310
assert all(row in config['supplemental_public_inputs'].values() for row in capsule['all_closed_compressed_chunk_refs_verified'])
assert len(recovery['preserved_passed_executions'])+len(recovery['preserved_recovery_passed_executions'])==6
prior_ui=json.loads(Path(recovery['prior_ui_retry']['context']['path']).read_bytes())
assert prior_ui['ui_retry_started_at']=='2026-10-09T00:59:43.753835+00:00'
assert recovery['prior_ui_retry']['binding']['sha256']=='b83ab67ca978d1b1b9e393c6d4e2cfb6c77e3bf9600af9d7ae87fe40975dbb84'
check('six_actual_zero_rows_both_lost_unknown_and_exact_prior_epoch',{'six_preserved_rows':6,'second_closed_compressed_chunk_refs':2310,'prior_ui_retry_epoch':prior_ui['ui_retry_started_at'],'third_incomplete_requires_deferral':True})

acceptance=source['assemble_actual_acceptance095.py']
reviewer=source['review_actual_archive_spec095.py']
archive=source['assemble_archive_spec095.py']
assert 'identity_start' in acceptance and "start['ui_identity_retry_started_at']" in archive and "row['started_at']) >= identity" in reviewer
assert "guard in spec['ui_binding_input_refs']" in acceptance
assert "'actual_root_view_image'" in acceptance and "'actual_PNGs_viewed'" in acceptance
assert "len(png_roles) == len(set(png_roles)) == len(png_paths) == 4" in reviewer
check('unchanged_fresh_identity_all8_saved_and_four_root_png_requirements',{'actual_runtime_evidence_provided_by_this_review':False})

tree=ast.parse(archive)
nodes=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='--next-action']
assert len(nodes)==1 and any(k.arg=='required' and isinstance(k.value,ast.Constant) and k.value.value is True for k in nodes[0].keywords)
assert "template['next_action'] = args.next_action" in archive and 'args.next_action.strip()' in archive
helper=config['pinned_source_inputs']['archive_helper']
helperraw=Path(helper['path']).read_bytes()
assert helper['sha256']=='d93ca9bb4c50248f73337ef7b6535402e3925ec1aedd80d2e74dbe78853f0936'
assert b'next_action=next_action' in helperraw
check('user_pause_required_next_action_preserved_to_prepare_save',{'final_archive_v2_exact':helpers['assemble_archive_spec095.py'],'required_Root_pause_CLI_text_not_yet_an_actual_completed_spec':True,'automatic96_template_text_superseded_at_assembly':True})

formal=funcs(helperraw)['formal_gate']
assert b'pointer(review, args.formal_spec_pointer) == sha(spec_raw)' in formal
assert b'pointer(review, args.formal_helper_pointer) == sha(read(Path(__file__).resolve()))' in formal
check('unchanged_late_actual_completed_spec_formal_gate',{'helper':helper,'formal_gate_source_sha256':digest(formal),'actual_completed_archive_spec_sha256':None})

for row in tuple(SEEN.values()): assert ref(row['path'])==row
check('final_all_immutable_physical_inputs_reread',{'unique_physical_inputs':len(SEEN)})
report={'format_version':1,'section':95,'status':'PASS_INDEPENDENT_ACTUAL_FINAL_IDENTITY_EVIDENCE_HELPERS_SOURCE_ONLY',
 'passed':True,'source_gate_passed':True,'runtime_executed':False,'runtime_pass':False,'execution_ready_for_Source_metadata_only':True,
 'actual_completed_archive_spec_sha256':None,'actual_completed_archive_spec_review_passed':False,
 'actual_UI_primary_exit':None,'actual_Saved_primary_exit':None,'actual_full095_finish_PASS':None,
 'final_manifest':mfref,'final_handoff':handref,'helpers':helpers,'actual_Source_refs':actual_refs,
 'original_independent_Source_report':old_report_ref,'exact_inverses':inverses,'checks':CHECKS,'passed_checks':len(CHECKS),'failed_checks':0,'blockers':[],
 'calls':{'target_helpers':0,'compiled_reviewed_code_execution':0,'codecs':0,'project_imports':0,'project_calls':0,'tests':0,'Qt':0,'Wine':0,'Git':0,'external_APIs':0,'process_sampling':0},
 'qualifications':['This report admits exact actual sealed Source helper bytes only; no target helper or codec was executed.',
 'Root must pass the latest user pause text via required archive --next-action and inspect actual completed spec and prepare-save documents. No later numbered section was applied or counted here.',
 'Actual UI/Saved primary-zero, all native saved evidence, four genuine Root PNG views, finish and late independent actual completed-spec review remain separate required Root gates.',
 'The third same UI issue remaining incomplete requires deferral. Both previous UI exits remain unknown/uncaptured/pending; six earlier zero observations are preserved without replay.'],
 'completed_sections_increment':0,'tracked_mutations':0,'archive_commit_push_executed':False,'native_Windows_game_chat_verified':False,
 'reviewed_at':datetime.now(timezone.utc).isoformat(),'physical_refs':list(SEEN.values()),'STOPWRITE':True}
rp=OUT/'formal-independent-source-review-final-identity-evidence095.json'
with rp.open('xb') as s: s.write((json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode())
print(json.dumps({'report':ref(rp),'passed_checks':len(CHECKS),'target_executions':0,'actual_completed_archive_spec_sha256':None}))
