"""Stdlib source-text preparation only. Never imports or executes the generated harness."""
import ast, base64, collections, hashlib, json
from pathlib import Path

PACKET=Path(__file__).resolve().parent
ORIGINAL=Path('/workspace/.continuation/ui-090-final-gate-revision/wine-ui-smoke-090-final-gate-revision.py')
ORIGINAL_SHA='9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9'
DESIGN=Path('/workspace/.continuation/full095-efficient-source-design-only')
BASELINE=Path('/workspace/.continuation/ui-095-module-report-pending/baseline094-v2')
CANDIDATE=Path('/workspace/.continuation/p2-report095-candidate-v1')
sha=lambda value:hashlib.sha256(value).hexdigest()
def save(name,value):
    data=json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False).encode()+b'\n'
    if (PACKET/name).exists():assert (PACKET/name).read_bytes()==data,('existing preparation payload changed',name)
    else:
        with (PACKET/name).open('xb') as handle:handle.write(data)
    return {'name':name,'bytes':len(data),'sha256':sha(data)}

raw=ORIGINAL.read_bytes();assert len(raw)==729181 and sha(raw)==ORIGINAL_SHA
source=raw.decode();old_tree=ast.parse(source);lines=source.splitlines(keepends=True)
offsets=[0]
for line in lines:offsets.append(offsets[-1]+len(line))
design=json.loads((DESIGN/'patch-location-contract095.json').read_text())
for group in design['grouped_future_patch_contracts']:
    for row in group.get('anchors',[]):assert sha(lines[row['original_line']-1].rstrip('\r\n').encode())==row['line_sha256']
plan=json.loads((BASELINE/'wine-module-report-shared095-plan.json').read_text())
chosen=['window1/startup','ordinary/myrtle-below40-pot4','ordinary/myrtle-at40','ordinary/myrtle-stage3-pot5','legacy/mechanist-stage2','hidden/yato-y-negative-index','hidden/yato-y-technical','hidden/yato-y-structured','hidden/yato-y-return-technical','hidden/yato-y-return-normal','window2/startup','existing/natural-overview','patch/amiya-caster-stage3','priority/run-myrtle-below40','priority/run-myrtle-at40-preview','priority/account-reference','priority/return-run','existing/error-JSON','existing/recover-JSON','existing/return-no-module']
steps_by_id={row['id']:row for row in plan['steps']}
subgroup=[]
for case_id in chosen:
    step=steps_by_id[case_id]
    subgroup.append({'id':case_id,'step':step,'comparison':'paired_actual094','actual_baseline_binding':None,'actual095_delta_binding':None})
    if case_id=='legacy/mechanist-stage2':subgroup.append({'id':'full095/new94-defense-callback','step':{'id':'full095/new94-defense-callback','action':'numeric_callback','widget':'defense','old_value':0,'value':7,'restore_value':0},'comparison':'same_action_auto_manual','actual_baseline_binding':None,'actual095_delta_binding':None})
save('full095-subgroup-plan.json',{'format_version':1,'status':'PENDING_SOURCE_ONLY_NOT_RUNTIME','steps':subgroup,'counts_are_planned_only':{'states':len(subgroup),'fresh_MainWindows':2,'manual_buttons':len(subgroup)-2},'public_run_initial':plan['public_run_initial'],'same_source_baseline_plan':{'path':str(BASELINE/'wine-module-report-shared095-plan.json'),'sha256':'ce1e4f002d51f8f4d7fea7db1c95dce507ef260c5f90e02152a085ad959c6a8a'},'scope':'Independent full UI append subset, original legacy body still executes; no full focused41/93/92 replay. Baseline durable maps may contain other unselected owners; compare same actual caller/current owner and full result/texts, preserve this window own complete run/account/files.'})
manifest=(CANDIDATE/'public-code-artifacts-manifest095.json').read_bytes();freeze=(CANDIDATE/'implementation-code-freeze095.json').read_bytes()
assert sha(manifest)=='216d5c31a9bc89dbc51f0b875db073a4fe8ea8b85fb5c9b624f5d9d6f56a461a'
assert sha(freeze)=='086cb910f2166e1ea37079567ee0e69e077474c2ea620c6b07b0236692b48579'
for row in json.loads(manifest)['files']:
    data=Path(row['source_path']).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256']
binding={'status':'PENDING_ROOT_ACTUAL095_GUARD_AND_ACTUAL_BASELINE_BINDINGS','source_guard':None,'candidate_manifest':{'path':str(CANDIDATE/'public-code-artifacts-manifest095.json'),'bytes':len(manifest),'sha256':sha(manifest)},'implementation_freeze':{'path':str(CANDIDATE/'implementation-code-freeze095.json'),'bytes':len(freeze),'sha256':sha(freeze)},'technical_tail_correction_artifact':None,'actual94_receipt':{'path':'/workspace/rougezhushou/verification/sections/094.json','sha256':'55dba304fe8075531e92de36f369c142f790da59ef69091edffc28299b97bac5'},'actual94_guard':{'path':'/workspace/.continuation/root-source-094.json','sha256':'259370708fe45e974511d1c1c010901d66981ee9dc2d53e7bce1ac978d463211'},'actual94_closure_sha256_root_announced':'613d5956762bd7b0a19d15c15173df698890a8545a8d0e14253086aaf728f806','baseline_receipt':None,'baseline_files':[],'cases':[],'qualified_reference_provenance':[],'public_run_initial':plan['public_run_initial'],'qualified_callback_widgets':['defense'],'report_contract':{'reference_key':'selected_module_source_reference','section_id':'selected_module_source','section_id_key':'id','section_path':['result','report','sections'],'section_title':'所选模组 · 原件资料与覆盖边界','technical_tail_prefix':'\n\n【所选模组原件追溯】\n','single_newline_freeze_claim_is_source_corrected':True},'root_final_source_review_required':True,'section_completed':False}
save('pending-binding095.json',binding)
header='''# BEGIN FULL095 PENDING ADMISSION AND ACTUAL MAINTAINED SOURCE GUARD
PENDING095 = True
'''+ 'BINDING095 = '+repr(binding)+'\n'+'''if PENDING095:
    raise RuntimeError('FULL095 PENDING: abort before project/Qt imports; actual095 guard and actual94 baseline/runtime bindings are absent')
import hashlib as _hash095, json as _json095, gzip as _guardgzip095
from pathlib import Path as _GuardPath095
_guard_root095=_GuardPath095(r'Z:\\workspace\\rougezhushou')
def _bound_bytes095(record):
    data=_GuardPath095(record['path']).read_bytes()
    assert _hash095.sha256(data).hexdigest()==record['sha256'],('bound artifact drift',record['path'])
    if 'bytes' in record:assert len(data)==record['bytes']
    return data
_guard_data095=_json095.loads(_bound_bytes095(BINDING095['source_guard']))
assert _guard_data095['passed'] is True and _guard_data095['candidate_bytes_exact'] is True
_maintained_expected095=_guard_data095['source_sha256_after']
assert len(_maintained_expected095)==_guard_data095['current_maintained']
def _validate_guard095():
    return {path.relative_to(_guard_root095).as_posix():_hash095.sha256(path.read_bytes()).hexdigest()
            for folder in ('rouge','tests','scripts') for path in sorted((_guard_root095/folder).rglob('*'))
            if path.is_file() and path.suffix in ('.py','.json') and '__pycache__' not in path.parts}
_maintained_before095=_validate_guard095()
assert _maintained_before095==_maintained_expected095,'actual maintained095 source drift before any project imports'
assert BINDING095['status']=='ROOT_BOUND_ACTUAL095_AND_ACTUAL94_BASELINE'
for _artifact095 in (BINDING095['candidate_manifest'],BINDING095['implementation_freeze'],BINDING095['technical_tail_correction_artifact'],BINDING095['actual94_receipt'],BINDING095['actual94_guard'],BINDING095['baseline_receipt']):_bound_bytes095(_artifact095)
_baseline_documents095={}
for _artifact095 in BINDING095['baseline_files']:
    _data095=_bound_bytes095(_artifact095)
    if _artifact095['encoding']=='gzip_json':_data095=_guardgzip095.decompress(_data095)
    else:assert _artifact095['encoding']=='json'
    _baseline_documents095[_artifact095['name']]=_json095.loads(_data095)
assert BINDING095['cases'] and all(case['baseline_file'] in _baseline_documents095 for case in BINDING095['cases'] if case['comparison']=='paired_actual094')
_guard_out095=_GuardPath095(r'Z:\\workspace\\.compat')
for _name095 in ('wine-ui-095.json','wine-ui-new-states-095.json.gz','wine-window-095.png','wine-movement-reference-095.png','wine-sown-tile-control-095.png','wine-medical-trait-095.png','wine-ui-failure-095.png','wine-ui-subgroup-failure-095.png','wine-ui-report-difference-095.json'):
    assert not (_guard_out095/_name095).exists(),('new095 evidence target already exists',_name095)
_guard_native_out095=_guard_out095/'full095-ui-native-v3'
assert not _guard_native_out095.exists(),'full095-ui-native-v3 namespace must be absent before launch'
_guard_native_out095.mkdir()  # Source-qualified fresh stdlib directory, before all project/Qt imports.
# END FULL095 PENDING ADMISSION AND ACTUAL MAINTAINED SOURCE GUARD
'''
codec_source=Path('/workspace/.continuation/ui-093-account-cache-final/wine-account-window-093-final.py').read_text();codec_tree=ast.parse(codec_source)
codec_names=['flat_native','native_inverse','clone','snapshot','delta','digest','filesystem','file_bytes']
codec_parts=[ast.get_source_segment(codec_source,next(node for node in codec_tree.body if isinstance(node,ast.FunctionDef) and node.name==name)) for name in codec_names]
byte_source=Path('/workspace/.continuation/ui-094-offline-input-refresh-final-v2/wine-focused-inputs-094-final.py').read_text();byte_tree=ast.parse(byte_source)
codec_parts.append(ast.get_source_segment(byte_source,next(node for node in byte_tree.body if isinstance(node,ast.FunctionDef) and node.name=='byte_evidence')))
fragment=(PACKET/'full095-runtime-fragment.txt').read_text();ast.parse(fragment)
new_helpers='\n# BEGIN UNCHANGED APPROVED093 NATIVE CODEC AND094V2 BYTE EVIDENCE\n'+'\n\n'.join(codec_parts)+'\n# END UNCHANGED APPROVED093 NATIVE CODEC AND094V2 BYTE EVIDENCE\n'+fragment+'\n'
edits=[]
def add(start,end,new,category):
    assert start<=end
    edits.append({'start':start,'end':end,'new':new,'old':source[start:end],'category':category})
def replace_line(number,new,category):add(offsets[number-1],offsets[number],new,category)
add(0,0,header+'\n','pending_admission_and_new_actual_guard')
replace_line(2,"if __name__ == '__main__' and False: # Historical090 guard literal retained; actual095 admission above\n",'historical090_guard_dormant_newguard_required')
add(offsets[1033],offsets[1033],new_helpers,'approved_codec_and_efficient_phase_instrumentation')
add(offsets[1042],offsets[1042],"_start095()\n",'outer_hooks_before_runtime_project_imports')
replace_line(1062,"        previous_profile090=sys.getprofile();_old_delegate095=True;_phase095='real_startup'\n",'old_startup_profile_delegation')
replace_line(1066,"        _old_delegate095=False;_phase095='automatic_control_or_signal'\n",'old_startup_profile_delegation')
add(offsets[1064],offsets[1064],"        assert window.operator_observations is window.account_cache.records\n",'account_live_alias_invariant')
for number,new in [(1261,lines[1260].replace("{'fields':","{'id':op,'fields':",1)),(1272,lines[1271].replace("{'fields':","{'id':op,'fields':",1)),(3083,lines[3082].replace("_copy090.deepcopy(fixture89_090)","{**_copy090.deepcopy(fixture89_090),'id':'mechanist'}")),(3084,lines[3083].replace("_copy090.deepcopy(fixture89_090)","{**_copy090.deepcopy(fixture89_090),'id':'char_151_myrtle'}")),(3095,lines[3094].replace("_copy090.deepcopy(fixture89_090)","{**_copy090.deepcopy(fixture89_090),'id':'mechanist'}"))]:replace_line(number,new,'legal_account_map_key_record_id')
for number,backup in [(1714,'account_snapshot'),(2484,'account075'),(2717,'account080'),(2902,'account085')]:
    original=lines[number-1]
    assert 'window.operator_observations=' in original
    actual=original.split('window.operator_observations=',1)[1].split(';',1)[0].strip()
    new=original.replace('window.operator_observations='+actual,'window.operator_observations.clear();window.operator_observations.update(_copy090.deepcopy('+actual+'));assert window.operator_observations is window.account_cache.records',1)
    replace_line(number,new,'in_place_raw_account_backup_restore')
replace_line(3143,lines[3142].replace('window.operator_observations=account090','window.operator_observations.clear();window.operator_observations.update(_copy090.deepcopy(account090));assert window.operator_observations is window.account_cache.records'),'in_place_raw_account_backup_restore')
replace_line(3011,lines[3010].replace("(sp090=='INCREASE_WHEN_ATTACK')","(sp090 in ('INCREASE_WHEN_ATTACK','INCREASE_WITH_TIME'))"),'qualified_six_Natural_visibility_cases')
add(offsets[2926],offsets[2926],"        _scope095='legacy086_090'\n",'legacy090_phase_scope')
replace_line(2938,"        _old_delegate095=True\n",'old_group090_profile_delegation')
replace_line(3142,"            profile_case090=None;_old_delegate095=False\n",'old_group090_profile_delegation')
replace_line(3137,"            receipt['new_actual_automatic_damage_function_entries090']=_phase_entries095.get('legacy086_090|automatic_control_or_signal',{}).get('rouge/damage.py:calculate_damage',0)\n",'actual_automatic_entries_not_total_minus_buttons')
add(offsets[3157],offsets[3157],"        _scope095='legacy_footer'\n",'legacy090_phase_scope')
append="""        # BEGIN FULL095 NEW SOURCE-BOUND UI BEHAVIOR AFTER ORIGINAL4283 COUNT CLOSURE
        receipt['legacy_original4283_actual_checks']=len(checks)
        receipt['actual095_behavior_rows']=_new_subgroup095(app,module,backend)
        receipt['actual_total_checks095']=len(checks)
        receipt['total_actual_checks']=len(checks)
        receipt['legacy085_prefix4217_and090_additional66_preserved']=True
        # END FULL095 NEW SOURCE-BOUND UI BEHAVIOR AFTER ORIGINAL4283 COUNT CLOSURE
"""
add(offsets[3217],offsets[3217],append,'append_new095_after_original_count_assertions')
add(offsets[3243],offsets[3243],"    _finish095(receipt)\n",'final_source_guard_and_evidence_after_measured_cleanup')
replace_line(3252,"    print(json.dumps({'passed':receipt['passed'],'complete_ui_validation':receipt['complete_ui_validation'],'checks':len(checks),'legacy_checks':receipt.get('legacy_original4283_actual_checks'),'receipt':'wine-ui-095.json','full_native':receipt.get('full_native095'),'failure':receipt.get('failure')},ensure_ascii=False))\n",'compact_console_full_receipt_preserved')
# Token substitutions are registered by exact original offsets, never a broad090 namespace rewrite.
names={'wine-ui-report-difference-090.json':'wine-ui-report-difference-095.json','wine-sown-tile-control-090.png':'wine-sown-tile-control-095.png','wine-movement-reference-090.png':'wine-movement-reference-095.png','wine-medical-trait-090.png':'wine-medical-trait-095.png','wine-window-090.png':'wine-window-095.png','wine-ui-failure-090.png':'wine-ui-failure-095.png','wine-ui-new-states-090.json.gz':'wine-ui-new-states-095.json.gz','wine-ui-090.json':'wine-ui-095.json','app.processEvents()':'_processEvents095()'}
protected_ranges=[(offsets[row['lines'][0]-1],offsets[row['lines'][1]]) for row in design['protected_original_helpers']]
for old,new in names.items():
    cursor=0
    while True:
        position=source.find(old,cursor)
        if position<0:break
        cursor=position+len(old)
        if any(edit['start']<=position and edit['end']>=cursor for edit in edits):continue
        if old=='app.processEvents()' and any(start<=position<end for start,end in protected_ranges):continue
        add(position,cursor,new,'measured_same_Qt_event_call' if old=='app.processEvents()' else 'individual_output_filename_transport')
edits.sort(key=lambda row:(row['start'],row['end']))
for left,right in zip(edits,edits[1:]):assert left['end']<=right['start'],('overlapping exact edits',left['category'],right['category'])
chunks=[];cursor=0;new_offset=0;ledger=[]
for edit in edits:
    unchanged=source[cursor:edit['start']];chunks.append(unchanged);new_offset+=len(unchanged.encode())
    before=edit['old'].encode();after=edit['new'].encode()
    ledger.append({'category':edit['category'],'original_byte_start':len(source[:edit['start']].encode()),'original_byte_count':len(before),'original_sha256':sha(before),'before_base64':base64.b64encode(before).decode(),'pending_byte_start':new_offset,'pending_byte_count':len(after),'pending_sha256':sha(after)})
    chunks.append(edit['new']);new_offset+=len(after);cursor=edit['end']
chunks.append(source[cursor:]);pending=''.join(chunks).encode();pending_tree=ast.parse(pending.decode())
recovered=pending
for row in reversed(ledger):
    start=row['pending_byte_start'];end=start+row['pending_byte_count'];assert sha(recovered[start:end])==row['pending_sha256']
    recovered=recovered[:start]+base64.b64decode(row['before_base64'])+recovered[end:]
assert recovered==raw and sha(recovered)==ORIGINAL_SHA
if (PACKET/'wine-full-ui-095-pending.py').exists():assert (PACKET/'wine-full-ui-095-pending.py').read_bytes()==pending
else:
    with (PACKET/'wine-full-ui-095-pending.py').open('xb') as handle:handle.write(pending)
save('exact-inverse-ledger095.json',{'schema':'full-ui095-exact-byte-inverse-v1','original':{'path':str(ORIGINAL),'bytes':len(raw),'sha256':sha(raw)},'pending_runner':{'file':'wine-full-ui-095-pending.py','bytes':len(pending),'sha256':sha(pending)},'operation_count':len(ledger),'operations':ledger,'whole_inverse_verified_by_source_bytes_only':True,'codec_or_project_execution':0})
old_asserts=collections.Counter(ast.dump(node,include_attributes=False) for node in ast.walk(old_tree) if isinstance(node,ast.Assert));new_asserts=collections.Counter(ast.dump(node,include_attributes=False) for node in ast.walk(pending_tree) if isinstance(node,ast.Assert))
removed=old_asserts-new_asserts;assert sum(removed.values())==4
removed_nodes=[node for node in ast.walk(old_tree) if isinstance(node,ast.Assert) and ast.dump(node,include_attributes=False) in removed]
assert sorted(node.lineno for node in removed_nodes)==[2365,2528,2687,3011]
for node in removed_nodes:
    if node.lineno==3011:continue
    renamed=ast.get_source_segment(source,node)
    for old,new in names.items():
        if old!='app.processEvents()':renamed=renamed.replace(old,new)
    assert ast.dump(ast.parse(renamed).body[0],include_attributes=False) in new_asserts
save('source-preparation-diagnostic095.json',{'status':'SOURCE_ONLY_PREPARATION_CHECKER_CORRECTED_NO_PRODUCT_FAILURE','first_preflight_assertion':'Expected only one changed AST Assert; actual four include three exact artifact filename transports and one qualified Natural visibility predicate. Whole inverse had already passed before checker assertion.','first_traceback_location':'prepare_full_ui095.py original line148','first_attempt_project_codec_Qt_Wine_calls':0,'source_qualified_correction':'Require exact original assert lines2365/2528/2687/3011; verify first three preserve same save assertion with only enumerated095 filename. No report/numeric/notes assertion relaxed.','harness_runner_body_changed_for_this_checker_correction':False,'current_AST_preflight':'continues after exact four classified assertions','same_issue_source_preparation_attempts':2})
helpers=[]
for row in design['protected_original_helpers']:
    old_node=next(node for node in ast.walk(old_tree) if isinstance(node,ast.FunctionDef) and node.name==row['name']);new_node=next(node for node in ast.walk(pending_tree) if isinstance(node,ast.FunctionDef) and node.name==row['name'])
    old_segment=ast.get_source_segment(source,old_node);new_segment=ast.get_source_segment(pending.decode(),new_node)
    helpers.append({'name':row['name'],'original_ast_source_sha256':sha(old_segment.encode()),'pending_ast_source_sha256':sha(new_segment.encode()),'byteexact':old_segment==new_segment,'allowed_change':'map-key id fixture at1272 only' if row['name']=='train' else None})
    assert old_segment==new_segment or row['name']=='train'
literals=[]
for name,row in design['literal_provenance'].items():
    nodes=[next(node for node in ast.walk(tree) if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id==name for target in node.targets)) for tree in (old_tree,pending_tree)]
    assert ast.get_source_segment(source,nodes[0])==ast.get_source_segment(pending.decode(),nodes[1])
    literals.append({'name':name,'assignment_source_sha256':row['assignment_source_sha256'],'entire_literal_byteexact':True})
save('source-only-preflight095.json',{'format_version':1,'status':'AST_RAW_SOURCE_QUALIFIED_PENDING_RUNTIME_UNRUN','PENDING_true':True,'abort_before_any_import':True,'entire729181_original_inverse_exact':True,'original_assert_statements':sum(old_asserts.values()),'original_asserts_AST_exact':sum((old_asserts&new_asserts).values()),'original_asserts_preserved_including_three_exact_output_transports':sum((old_asserts&new_asserts).values())+3,'output_path_only_assert_lines':[2365,2528,2687],'visibility_delta_count':1,'four_literal_assignments':literals,'fourteen_helpers':helpers,'category_counts':dict(collections.Counter(row['category'] for row in ledger)),'approved_native_functions_source_copied_only':codec_names+['byte_evidence'],'report_key_section_source_frozen':True,'technical_tail_exact_source_double_newline':'\n\n【所选模组原件追溯】\n','technical_interface_single_newline_history_preserved':True,'actual95_guard_baseline_outputhash_and_qualified_report_goldens':None,'project_imports_API_helpers_formatter_tests_Qt_Wine_codecs_network':0,'tracked_edits':0,'completed_section_increment':0})
print(json.dumps({'source_only_preparation':True,'pending_bytes':len(pending),'pending_sha256':sha(pending),'inverse_operations':len(ledger),'all_original_asserts_except_qualified_visibility_retained':True,'PENDING_abort':True,'runtime':0},ensure_ascii=False))
