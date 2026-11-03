"""Stdlib-only source transport and runner generation; never executes the runner."""
from pathlib import Path
import ast, copy, gzip, hashlib, json, subprocess

HERE=Path(__file__).resolve().parent
ROOT=Path('/workspace/rougezhushou')
COMMIT='5e2ff697402d06e78b239e01f0b4307b50dd5633'
OLD=Path('/workspace/.compat/wine-ui-smoke-085.py')
STAGE=Path('/workspace/.continuation/ui-090-draft')
INPUT=Path('/workspace/.continuation/root-transport-preparation090')
NEW8=Path('/workspace/.continuation/ui-090-runtime-increment088')

def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,obj):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    return {'source_path':str(p),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
def file(p):return {'source_path':str(p),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}

assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==COMMIT
assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
context=json.loads(Path('/workspace/.compat/wine-validation-090-context.json').read_bytes())
assert context['commit']==COMMIT and len(context['source_sha256'])==730
paths=list(context['source_sha256'])
proc=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=('\n'.join(COMMIT+':'+p for p in paths)+'\n').encode(),capture_output=True,check=True)
cursor=0;rows=[]
for rel in paths:
    end=proc.stdout.index(b'\n',cursor);header=proc.stdout[cursor:end].split();assert header[1]==b'blob'
    size=int(header[2]);b=proc.stdout[end+1:end+1+size];cursor=end+1+size+1
    disk=(ROOT/rel).read_bytes();assert b==disk and sha(b)==context['source_sha256'][rel]
    rows.append({'root_relative_path':rel,'git_blob':header[0].decode(),'bytes':size,'sha256':sha(b)})
assert cursor==len(proc.stdout)
public=[r for r in rows if r['root_relative_path'].startswith('rouge/')]
assert len(public)==126
proof=save('actual-root090-source-binding.json',{'format_version':1,'passed':True,'actual_commit':COMMIT,'maintained_source_files':730,'public_source_files':126,'all_named_gitblobs_equal_working_bytes_and_root_full_context':True,'rows':rows,'complete_public_rebuild_command':'git show 5e2ff697402d06e78b239e01f0b4307b50dd5633:<root_relative_path>','duplicate_full_public_or_730_source_tree_copied':False,'API_helper_formatter_Qt_Wine_calls':0})

saved44=json.loads(gzip.decompress((STAGE/'api-ui090-section086.json.gz').read_bytes()))
saved8=json.loads(gzip.decompress((NEW8/'api-ui090-section088-new8.json.gz').read_bytes()))
assert len(saved44['records'])==44 and len(saved8['records'])==8
case44=json.loads((STAGE/'cases090-section086.json').read_bytes())['rows']
case8=json.loads((INPUT/'additional8-input-plan090.json').read_bytes())['cases']
assert [r['input'] for r in saved44['records']]==[r['input'] for r in case44]
assert [r['input'] for r in saved8['records']]==[r['input'] for r in case8]

def projection(result):
    keys=['attack','total_damage','components','attack_speed','base_attack_speed','interval_seconds','timing']
    if 'total_healing' in result:keys.append('total_healing')
    keys.extend(k for k in result if k.endswith('_reference'))
    out={k:result[k] for k in dict.fromkeys(keys)}
    out['estimate']={k:result['estimate'][k] for k in ('training','base_stats','skill')}
    return out
cases=[]
for section,designed,records in ((86,case44,saved44['records']),(88,case8,saved8['records'])):
    for designed_row,record in zip(designed,records):
        row=copy.deepcopy(designed_row);row['section']=section
        row['expected_public_projection']=projection(record['result'])
        row['saved_result_full_json_sha256']=sha(json.dumps(record['result'],ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
        cases.append(row)
save('saved52-UI-producer-inputs-and-public-projections090.json',{'format_version':1,'rows':cases,'record_count':52,'old44_and_new8_recalculated':False,'projection_scope':'Whole source-defined estimate training/base/skill, components/timing, numeric top-level shape and all present named references; UI-only cultivation and inventory notes retain their actual producer meaning.'})

animations=json.loads((ROOT/'rouge/data/original-animation-references.json').read_bytes())
back5=[r for r in animations['operators']['char_196_sunbr']['records'] if r['orientation']=='Back']
assert len(back5)==5
assert [r['animation'] for r in back5 if r['selectable_as_conventional_reference']]==['Attack','Skill']
back_attack=next(r for r in back5 if r['animation']=='Attack')
generic=next(r for r in back5 if r['animation']=='Skill')
assert not any(r['runtime_binding_verified'] for r in back5)
save('Back5-current-data-and-actual-choice-plan090.json',{'actual_commit':COMMIT,'Back5':back5,'genuine_combo_reference':back_attack['id'],'generic_Skill_excluded_from_normal_and_both_numbered_skill_combos':generic['id'],'planned_actual_control_rows':4,'planned_explicit_Back_damage_button_requests':0,'actual_combo_and_training_changes_trigger_automatic_calculations_counted_separately':True,'scope':'S1/S2 × normal/skill QComboBox, genuine Attack item selection/readback/label; generic Skill remains unnumbered; no native animation binding or game timing is claimed.'})

old=OLD.read_text();assert sha(OLD.read_bytes())=='b6976652eb50e06909cca68490b0b9d3e11ea81fbc9a73ca87efcbb10354e306'
pending=(STAGE/'wine-ui-smoke-090.py').read_text()
guard="if __name__ == '__main__' and True:\n    raise RuntimeError('UI090 sources and API contract remain pending; Qt execution is forbidden')\n\n"
assert pending.startswith(guard)
assert pending[len(guard):].replace('-090','-085')==old
helpers=(HERE/'runner-helpers090.txt').read_text()
states89=json.loads((INPUT/'saved89-five-state-UI-consumer-design090.json').read_bytes())['selected_saved_records']
assert len(states89)==5
contract89=json.loads((HERE/'review-saved89-source/expected-ten-state-contract089.json').read_bytes())['rows']
assert len(contract89)==10
block=(HERE/'runner-additions090.txt').read_text().replace('CASE_LITERAL',repr(cases)).replace('STATES89_LITERAL',repr(states89)).replace('CONTRACT89_LITERAL',repr(contract89))
boundguard='''# BEGIN FINAL090 SOURCE GUARD
if __name__ == '__main__':
    import hashlib as _hash090
    from pathlib import Path as _Path090
    _ROOT090=_Path090(r'Z:\\workspace\\rougezhushou')
    _SOURCE090=SOURCE_LITERAL
    for _rel090,_sha090 in _SOURCE090.items():
        assert _hash090.sha256((_ROOT090/_rel090).read_bytes()).hexdigest()==_sha090,('actual90 source drift before imports',_rel090)
# END FINAL090 SOURCE GUARD

'''.replace('SOURCE_LITERAL',repr(context['source_sha256']))
runner=boundguard+pending[len(guard):]
anchor='def source_hashes():\n';assert runner.count(anchor)==1
runner=runner.replace(anchor,helpers+'\n'+anchor)
startup='        app=QApplication([]);window=module.MainWindow();window.show();app.processEvents()\n'
assert runner.count(startup)==1
startaddition='        # BEGIN FINAL090 STARTUP INSTRUMENTATION\n        previous_profile090=sys.getprofile();sys.setprofile(profile090)\n        # END FINAL090 STARTUP INSTRUMENTATION\n'
endaddition='        # BEGIN FINAL090 STARTUP SNAPSHOT\n        sys.setprofile(previous_profile090)\n        receipt[\'actual_startup_runstate_entries_090\']=dict(entry_counts090)\n        # END FINAL090 STARTUP SNAPSHOT\n'
runner=runner.replace(startup,startaddition+startup+endaddition)
anchor='        # Final visible screenshot scenario demonstrates the restored explanation.\n'
assert runner.count(anchor)==1
runner=runner.replace(anchor,block+'\n'+anchor)
metadata_replacements=[]
for name in ['preserved_old_checks']+['preserved_full_%03d_checks'%i for i in (60,65,70,75,80)]:
    line=next(line for line in runner.splitlines(keepends=True) if "receipt['"+name+"']=len(checks)" in line)
    changed=line.rstrip('\n')+'-(group090_end-group090_start)\n'
    runner=runner.replace(line,changed);metadata_replacements.append({'old':line,'new':changed})
addedmetadata="        receipt['preserved_full_085_checks']=len(checks)-(group090_end-group090_start)\n        assert receipt['preserved_full_085_checks']==4217,receipt['preserved_full_085_checks']\n        assert len(checks)==4283,len(checks)\n"
anchor="        receipt['total_actual_checks']=len(checks)\n";assert runner.count(anchor)==1
runner=runner.replace(anchor,addedmetadata+anchor)
finalsink="# BEGIN FINAL090 LOSSLESS NEW STATE OUTPUT\nimport gzip as _gzip090\n_statebytes090=json.dumps({'format_version':1,'actual_new_window_states':actual_states090,'expected_UI_state_rows':52,'actual_main_window_execution_only':True,'passed':receipt['passed']},ensure_ascii=False,allow_nan=False).encode('utf-8')\n_statepath090=OUT/'wine-ui-new-states-090.json.gz'\n_statepath090.write_bytes(_gzip090.compress(_statebytes090,mtime=0))\nreceipt['new_state_archive090']={'file':_statepath090.name,'bytes':_statepath090.stat().st_size,'sha256':hashlib.sha256(_statepath090.read_bytes()).hexdigest(),'decoded_bytes':len(_statebytes090),'decoded_sha256':hashlib.sha256(_statebytes090).hexdigest(),'records':len(actual_states090)}\n# END FINAL090 LOSSLESS NEW STATE OUTPUT\n"
finalsink=''.join('    '+line+'\n' for line in finalsink.splitlines())
anchor="    (OUT/'wine-ui-090.json').write_text(";assert runner.count(anchor)==1
runner=runner.replace(anchor,finalsink+anchor)
ast.parse(runner)
(HERE/'wine-ui-smoke-090-final.py').write_text(runner)
inverse=runner.replace(boundguard,'').replace(helpers+'\n','').replace(startaddition,'').replace(endaddition,'').replace(block+'\n','').replace(addedmetadata,'').replace(finalsink,'')
for change in metadata_replacements:inverse=inverse.replace(change['new'],change['old'])
inverse=inverse.replace('-090','-085')
assert inverse==old
save('old4217-byte-inverse-proof090.json',{'passed':True,'old_actual085':file(OLD),'old_check_rows':4217,'new_runner':file(HERE/'wine-ui-smoke-090-final.py'),'whole_old_literal_restored_byte_exact':True,'source_guard_removed':True,'new_helper_and_runtime_block_removed':True,'startup_readonly_profile_insertion_removed':True,'six_preserved_count_only_metadata_adjustments_reversed':metadata_replacements,'new_count_metadata_and_lossless_sink_removed':True,'artifact_suffix_inverse_only':'090 -> 085 after all supplemental text removals','old_original_pending_090_runner_unchanged':file(STAGE/'wine-ui-smoke-090.py'),'new_expected_rows':66,'expected_total_rows':4283,'old_passed_matrices_reexecuted_by_this_generation':False})
unique_inputs=len({json.dumps(r['input'],sort_keys=True,separators=(',',':')) for r in cases})
assert unique_inputs==39
save('runner-scope-and-source-freeze090.json',{'format_version':1,'status':'FINAL_SOURCE_BOUND_RUNNER_ACTUAL_QT_PENDING','actual_commit':COMMIT,'maintained_source_files':730,'public_source_files':126,'source_binding':proof,'runner':file(HERE/'wine-ui-smoke-090-final.py'),'planned_new_actual_check_rows':{'86_real_boolean_and_hidden_producers':44,'87_Back_Attack_controls_and_generic_Skill_exclusion':4,'88_shared_continuous_checkbox_and_timing_JSON':8,'89_saved_state_readonly_training_consumers':10},'planned_new_rows_total':66,'planned_total_actual_check_rows':4283,'old_actual_rows':4217,'already_completed_preflight':{'UI_design_states':52,'unique_requested_inputs':39,'actual_API_requests':52,'explicit_three_text_requests':156,'measured_formatter_entries':208,'new8_same_harness_issue_failed_attempts':2,'product_errors':0},'planned_new_explicit_damage_button_requests_within_sole_actual_Qt':52,'automatic_control_refresh_damage_function_entries':'actual main-thread instrumentation, including genuine Back/89 consumer changes, additional to 52 explicit clicks; not predeclared zero','preparation_fresh_API_helper_formatter_Qt_Wine_tests':0,'old_saved44_new8_not_recalculated':True,'actual_GUI_pass':False,'artifact_unique_names':['wine-ui-090.json','wine-window-090.png','wine-movement-reference-090.png','wine-sown-tile-control-090.png','wine-medical-trait-090.png','wine-ui-failure-090.png','wine-ui-report-difference-090.json','wine-ui-new-states-090.json.gz'],'independent_final_formal_pending':True,'native_Windows_game_integration_verified':False})
print(json.dumps({'runner':file(HERE/'wine-ui-smoke-090-final.py'),'old4217_inverse':True,'planned_total':4283,'source_binding':proof},ensure_ascii=False))
