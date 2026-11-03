"""Root-only stdlib sealer. It executes no project, native codec, Qt or tests."""
import argparse,ast,gzip,hashlib,json,shutil
from pathlib import Path

def digest(data):return hashlib.sha256(data).hexdigest()
def check(row):
    path=Path(row['path']);data=path.read_bytes()
    assert len(data)==row['bytes'] and digest(data)==row['sha256'],('Exact supplied root artifact',row['path'])
    return data

def pointer(value,path):
    if path=='':return value
    assert path.startswith('/')
    for token in path[1:].split('/'):
        token=token.replace('~1','/').replace('~0','~')
        value=value[int(token)] if isinstance(value,list) else value[token]
    return value

def row(path):
    path=Path(path);data=path.read_bytes()
    return {'path':str(path),'bytes':len(data),'sha256':digest(data)}

def winpath(value):
    path=Path(value).resolve();rel=path.relative_to('/workspace')
    return 'Z:\\workspace\\'+str(rel).replace('/','\\')

def winrow(value):
    result=dict(value);result['path']=winpath(result['path']);return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('root_binding_json');parser.add_argument('destination');args=parser.parse_args()
    here=Path(__file__).resolve().parent;root=Path('/workspace/rougezhushou')
    manifest_path=here/'public-artifacts-manifest-pending095.json';manifest=json.loads(manifest_path.read_text())
    assert manifest['status']=='STOPWRITE_SOURCE_ONLY_PENDING095_NOT_EXECUTABLE_NOT_COMPLETED'
    for item in manifest['payload']:check(item)
    supplied_path=Path(args.root_binding_json);supplied=json.loads(supplied_path.read_text())
    assert supplied['status']=='ROOT_ACTUAL95_SOURCE_AND_BASELINE_READY_TO_SEAL'
    guard_bytes=check(supplied['actual95_guard']);guard=json.loads(guard_bytes);source=guard['source_sha256_after'];assert guard['passed'] is True
    old_guard_path=Path('/workspace/.continuation/ui-095-module-report-pending/baseline094-v2/wine-module-report-baseline094-source.json');old_guard_bytes=old_guard_path.read_bytes();assert digest(old_guard_bytes)=='259370708fe45e974511d1c1c010901d66981ee9dc2d53e7bce1ac978d463211'
    old_guard=json.loads(old_guard_bytes);old_source=old_guard['source_sha256_after'];assert len(old_source)==732
    for rel,h in source.items():assert digest((root/rel).read_bytes())==h,('Actual root-applied95 maintained source',rel)
    code_bytes=check(supplied['candidate_code_manifest']);assert digest(code_bytes)=='216d5c31a9bc89dbc51f0b875db073a4fe8ea8b85fb5c9b624f5d9d6f56a461a'
    code=json.loads(code_bytes);assert len(code['files'])==5
    candidate_paths={item['destination_repo_path'] for item in code['files']}
    for item in code['files']:
        check({'path':item['source_path'],'bytes':item['bytes'],'sha256':item['sha256']})
        assert source[item['destination_repo_path']]==item['sha256']
    test_manifest_bytes=check(supplied['single_test_supplement_manifest']);assert digest(test_manifest_bytes)=='6a580bed1e8e60a1782fb53495996b4f841626a77eea9292f10952acdd194fcc'
    test_manifest=json.loads(test_manifest_bytes);assert len(test_manifest['files'])==8 and len(test_manifest['code_files'])==1
    for item in test_manifest['files']:check({'path':item['source_path'],'bytes':item['bytes'],'sha256':item['sha256']})
    test_row=test_manifest['code_files'][0];test_rel='tests/test_token_duration_reference.py'
    assert test_row['destination_repo_path']==test_rel and test_row['before_sha256']=='cea16b4243c949fd1749c1cab4f323b2f5ea7267ad69928e715ea570ab27e199' and test_row['sha256']=='ad4a6381e6ec6f1a6db08cb1df0339b614883c960a1db3865d019ac08b12b554'
    assert old_source[test_rel]==test_row['before_sha256'] and source[test_rel]==test_row['sha256']
    initial_bytes=check(supplied['initial_core095_guard']);assert digest(initial_bytes)=='57e80f30aa67384225c49fd16b58bd3289fe9df41e018feca242ce132d105b82'
    initial=json.loads(initial_bytes);initial_source=initial['source_sha256_after'];assert initial['passed'] is True and len(initial_source)==735 and set(initial_source)==set(source)
    assert {rel for rel in initial_source if initial_source[rel]!=source[rel]}=={test_rel} and initial_source[test_rel]==test_row['before_sha256']
    inverse_bytes=check(supplied['single_test_inverse']);assert digest(inverse_bytes)=='2d1eb27fa3f4067beb813815c547acaa94f23084ff37290f354aae1e06f0fa5d'
    inverse=json.loads(inverse_bytes);assert inverse['destination_repo_path']==test_rel and len(inverse['edits'])==2 and inverse['new_test_methods']==0
    candidate_test=check({'path':test_row['source_path'],'bytes':test_row['bytes'],'sha256':test_row['sha256']});restored=candidate_test.decode('utf-8')
    for edit in reversed(inverse['edits']):
        assert restored.count(edit['new'])==1;restored=restored.replace(edit['new'],edit['old'],1)
    assert len(restored.encode())==inverse['before_bytes']==9319 and digest(restored.encode())==inverse['before_sha256']==test_row['before_sha256']
    original_test=next(item for item in test_manifest['files'] if item['sha256']==test_row['before_sha256'])
    assert restored.encode()==check({'path':original_test['source_path'],'bytes':original_test['bytes'],'sha256':original_test['sha256']})
    added=set(source)-set(old_source);changed={rel for rel in old_source if rel in source and source[rel]!=old_source[rel]}
    assert set(old_source)<=set(source) and added=={'rouge/module_source_reference.py','rouge/data/module-source-reference.json','tests/test_selected_module_source_reference.py'}
    assert changed=={'rouge/reporting.py','scripts/verify_cloud.py',test_rel} and added|changed==candidate_paths|{test_rel}
    assert len(source)==735 and len(old_source)-len(changed)==729
    interface_bytes=check(supplied['candidate_interface_artifact']);assert digest(interface_bytes)=='086cb910f2166e1ea37079567ee0e69e077474c2ea620c6b07b0236692b48579'
    interface=json.loads(interface_bytes)
    assert interface['report_addition_key']=='selected_module_source_reference' and interface['notes_only_section']['id']=='selected_module_source'
    assert interface['technical_tail']['delimiter']=='\n【所选模组原件追溯】\n'
    tail_bytes=check(supplied['technical_tail_correction_artifact']);tail_diagnostic=json.loads(tail_bytes)
    assert digest(tail_bytes)=='7d3d57a2e71dd2f321e1a288486a708d5a4bfd7baa238ccacdafbf3383124a6e'
    corrected_tail='\n\n【所选模组原件追溯】\n'
    assert tail_diagnostic['actual_complete_append_tail_prefix']==corrected_tail and tail_diagnostic['exact_code_product_manifest_sha256']==digest(code_bytes)
    baseline_bytes=check(supplied['baseline_receipt']);baseline=json.loads(baseline_bytes)
    assert baseline['passed'] is True and baseline['workflow_complete'] is True and baseline['completed_section_increment']==0
    assert baseline['kind']=='FRESH_ACTUAL94_FOCUSED095_BASELINE_NOT_SECTION_COMPLETION' and baseline['source_guard_sha256']==digest(old_guard_bytes)
    assert baseline['runner_sha256']=='4740c8b9f6386a32cd78929f98c8265201ba5b891d1e6eddbbb812faebebd829'
    assert baseline['plan_sha256']=='ce1e4f002d51f8f4d7fea7db1c95dce507ef260c5f90e02152a085ad959c6a8a' and baseline['source_drift']==[]
    assert baseline['source_sha256_before']==baseline['source_sha256_after']==old_source
    assert check(supplied['baseline_shell_status'])==b'0\n','Real root captured shell status required; source intention is not a primary result'
    records_bytes=check(supplied['baseline_records']);assert digest(records_bytes)==baseline['records']['sha256'] and len(records_bytes)==baseline['records']['bytes']
    records_raw=gzip.decompress(records_bytes);assert len(records_raw)==baseline['records']['decoded_bytes'] and digest(records_raw)==baseline['records']['decoded_sha256']
    records=json.loads(records_raw);assert records['schema']=='focused-module-report-baseline-v1' and records['passed'] is True
    plan_path=here/'wine-module-report-shared095-plan.json';plan_bytes=plan_path.read_bytes();assert digest(plan_bytes)==baseline['plan_sha256'];plan=json.loads(plan_bytes)
    assert [s['id'] for s in records['states']]==[s['id'] for s in plan['steps']] and all(s['passed'] is True for s in records['states'])
    assert baseline['states']==len(records['states'])==plan['counts']['states_planned'] and baseline['fresh_windows']==records['fresh_windows']==2
    gate_rows=supplied['required_gate_files'];assert len(gate_rows)==2 and len({g['role'] for g in gate_rows})==2
    roles={g['role']:g for g in gate_rows};assert set(roles)=={'baseline_saved_only_review','actual95_candidate_source_review'}
    def gate_check(gate_row,required):
        value=json.loads(check(gate_row));gates=gate_row['JSON_pointer_gates'];assert len(gates)==len({g['pointer'] for g in gates})
        provided={g['pointer']:g['expected'] for g in gates}
        for key,expected in required.items():assert key in provided and type(provided[key]) is type(expected) and provided[key]==expected
        for gate in gates:
            actual=pointer(value,gate['pointer']);assert type(actual) is type(gate['expected']) and actual==gate['expected'],('Real source/saved review pointer',gate_row['path'],gate['pointer'])
        return value
    gate_check(roles['baseline_saved_only_review'],{'/passed':True,'/actual_runtime_receipt_sha256':supplied['baseline_receipt']['sha256'],'/actual_native_archive_sha256':supplied['baseline_records']['sha256']})
    gate_check(roles['actual95_candidate_source_review'],{'/source_gate_passed':True,'/runtime_pass':False,'/code_manifest_sha256':supplied['candidate_code_manifest']['sha256'],'/base_source_guard_sha256':digest(old_guard_bytes),'/interface_sha256':supplied['candidate_interface_artifact']['sha256']})
    test_review_bytes=check(supplied['single_test_formal_review']);assert digest(test_review_bytes)=='86418bd3c790485b99d365cbf4cd6b0cf7da328aa51fe8364fcc0bca6d313e09'
    gate_check(supplied['single_test_formal_review'],{'/source_gate_passed':True,'/runtime_pass':False,'/test_manifest_sha256':digest(test_manifest_bytes),'/before_test_sha256':test_row['before_sha256'],'/after_test_sha256':test_row['sha256'],'/baseline95_guard_sha256':digest(initial_bytes)})
    for original,expected_sha,expected_bytes in [('original_battle','006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460',5710707),('original_modules','b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9',3365012)]:
        data=check(supplied[original]);assert digest(data)==expected_sha and len(data)==expected_bytes
    destination=Path(args.destination);destination.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(plan_path,destination/plan_path.name)
    shutil.copyfile(supplied['actual95_guard']['path'],destination/'wine-module-report-095-source.json')
    binding={'format_version':1,'status':'ROOT_SEALED_ACTUAL95_FOCUSED_BINDING','completed_section_increment':0,'actual95_guard_sha256':digest(guard_bytes),'actual95_maintained_count':len(source),'candidate_interface':interface,'technical_tail_exact_delimiter':corrected_tail}
    for key in ('baseline_receipt','baseline_records','baseline_shell_status','candidate_code_manifest','candidate_interface_artifact','technical_tail_correction_artifact','single_test_supplement_manifest','single_test_inverse','single_test_formal_review','initial_core095_guard','original_battle','original_modules'):binding[key]=winrow(supplied[key])
    binding['required_gate_files']=[winrow(g) for g in supplied['required_gate_files']]
    binding_path=destination/'wine-module-report-095-binding-final.json';binding_bytes=(json.dumps(binding,ensure_ascii=False,indent=2)+'\n').encode();binding_path.write_bytes(binding_bytes)
    pending_path=here/'wine-module-report-095-pending.py';pending=pending_path.read_text()
    changes=[('PENDING_PREPARATION = True','PENDING_PREPARATION = False'),("EXPECTED_BINDING_SHA256='ROOT_FINAL_BINDING_SHA256_PENDING095'",f"EXPECTED_BINDING_SHA256='{digest(binding_bytes)}'")]
    final=pending
    for before,after in changes:assert final.count(before)==1;final=final.replace(before,after,1)
    inverse=final
    for before,after in reversed(changes):inverse=inverse.replace(after,before,1)
    assert inverse==pending;ast.parse(final)
    final_path=destination/'wine-module-report-095-final.py';final_path.write_text(final)
    shutil.copyfile(pending_path,destination/'wine-module-report-095-pending-original.py')
    diagnostic={'format_version':1,'status':'ROOT_STDLIB_SEALED_FINAL095_SOURCE_RUNTIME_UNRUN','completed_section_increment':0,'substitutions':len(changes),'whole_pending_inverse_byte_exact':True,'actual95_maintained':len(source),'exact_added':sorted(added),'exact_changed':sorted(changed),'unchanged_old732':729,'single_test_whole_file_two_edit_inverse_exact':True,'initial_core095_guard_sha256':digest(initial_bytes),'single_test_supplement_manifest_sha256':digest(test_manifest_bytes),'single_test_formal_review_sha256':digest(test_review_bytes),'binding':row(binding_path),'root_supplied_binding':row(supplied_path),'baseline_receipt':supplied['baseline_receipt'],'baseline_records':supplied['baseline_records'],'actual_primary_shell_status_captured':True,'formal_final_source_review':'PENDING; root independently reviews this exact final runner before sole Wine execution','project_imports_codecs_APIs_formatters_tests_Qt_Wine_network':0}
    diagnostic_path=destination/'binding-diagnostic095.json';diagnostic_path.write_text(json.dumps(diagnostic,ensure_ascii=False,indent=2)+'\n')
    final_manifest={'format_version':1,'status':'STOPWRITE_ROOT_SEALED_FINAL095_SOURCE_NOT_RUNTIME_PASS','payload':[row(path) for path in sorted(destination.iterdir())]}
    final_manifest_path=destination/'public-artifacts-manifest-final095.json';final_manifest_path.write_text(json.dumps(final_manifest,ensure_ascii=False,indent=2)+'\n')
    handoff={'format_version':1,'status':'STOPWRITE_ROOT_FINAL095_READY_FOR_FRESH_INDEPENDENT_SOURCE_REVIEW_RUNTIME_UNRUN','completed_section_increment':0,'manifest':row(final_manifest_path),'runner':row(final_path),'counts':plan['counts'],'new_outputs':['/workspace/.compat/wine-module-report-window-095.json','/workspace/.compat/wine-module-report-window-095-records.json.gz'],'PNGs':[s['PNG'] for s in plan['steps'] if 'PNG' in s],'root_sole_Wine_execution_after_final_formal_review':True,'pending_source_edited':False,'STOPWRITE':True}
    handoff_path=destination/'handoff-final095.json';handoff_path.write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'final_directory':str(destination),'manifest':row(final_manifest_path),'handoff':row(handoff_path),'runner':row(final_path),'runtime_pass':False},ensure_ascii=False))

if __name__=='__main__':main()
