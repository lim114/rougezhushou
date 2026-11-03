"""Root final-source declaration only; this program never launches tests or Qt."""
from pathlib import Path
import argparse,ast,json,re,sys
from full410_common import (BASE,ROOT,FREEZE,READY_PATH,ATTEMPT,runner_snapshot,
    native_source_snapshot,input_bindings,public,sha,write_new,now,git,tool_pins,
    canonical_binding_plan,canonical_inputs,canonical_selected_source)


def visible_default(raw,name):
    """Read the actual canonical parser literal, never shorten its native budget."""
    found=[]
    for node in ast.walk(ast.parse(raw)):
        if not isinstance(node,ast.Call)or not isinstance(node.func,ast.Attribute)or node.func.attr!='add_argument':continue
        if not any(isinstance(arg,ast.Constant)and arg.value=='--visible-ms'for arg in node.args):continue
        values=[arg.value for arg in node.keywords if arg.arg=='default']
        if len(values)!=1:raise ValueError('Explicit reviewed canonical visible-ms default required: '+name)
        value=ast.literal_eval(values[0])
        if type(value)is not int or value<=0:raise ValueError('Positive literal visible-ms default required: '+name)
        found.append(value)
    if len(found)>1:raise ValueError('Ambiguous canonical visible-ms parser: '+name)
    return found[0]if found else None


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-finalized',action='store_true')
    p.add_argument('--expected-parent-commit',required=True)
    p.add_argument('--functional-receipts',required=True,type=Path,
                   help='Explicit root JSON with section410 and necessary/native/native_process public receipt paths.')
    args=p.parse_args()
    if not args.source_finalized:raise ValueError('Only root may explicitly finalize the actually ready410 source; never freeze in-progress candidates.')
    tool_pins()
    if FREEZE.exists():raise FileExistsError('Never overwrite an existing full source freeze.')
    parent=git('rev-parse','HEAD')
    if parent!=args.expected_parent_commit or git('branch','--show-current')!='codex/p2-development':raise ValueError('Exact current parent and development branch required.')
    prior_summary=public('verification/full-395/summary.json')
    summary=json.loads(prior_summary.read_bytes());prior_path=public(summary['source_freeze'])
    if sha(prior_path)!=summary['source_freeze_sha256']:raise ValueError('Original395 current authority is not its actual freeze.')
    old=json.loads(prior_path.read_bytes())
    if summary['available_checks_passed']is not True or summary['scope_not_reduced']is not True:raise ValueError('Original complete available395 receipt required.')
    if len(old['selectors'])!=642 or len(old['p3_scripts'])!=110:raise ValueError('Never shrink actual395 selector/native scope.')
    actual=runner_snapshot()
    if actual['selectors'][:len(old['selectors'])]!=old['selectors']:raise ValueError('All original642 ordered selectors must remain.')
    for name in actual['source_sha256']:
        if name.startswith('tests/test_')and name not in old['source_sha256']and'tests.'+Path(name).stem not in actual['selectors']:
            raise ValueError('New full test module missing from maintained selectors: '+name)
    native=native_source_snapshot()
    if set(actual['source_sha256'])-set(native)!={'CORE_0.70_VERIFICATION.json'}or set(native)-set(actual['source_sha256'])!={'tests/offline_scope_retirement.py'}:
        raise ValueError('Complete maintained and native source ranges must retain their original explicit difference; review new files rather than exclude them.')
    scripts=dict(old['p3_scripts']);new_scripts={};missing=[]
    for section in range(396,411):
        matches=sorted(path for path in(ROOT/'scripts').glob(f'verify*_window_{section}*.py')
                       if re.search(r'_window_'+str(section)+r'(?:_[^.]+)?\.py$',path.name))
        if not matches:missing.append(section);continue
        for index,path in enumerate(matches):
            mode='p3_'+str(section)+(''if index==0 else'_'+str(index+1))
            new_scripts[mode]=path.relative_to(ROOT).as_posix()
    if missing:raise ValueError('Final installed native harnesses are still missing for sections '+repr(missing)+'. Candidates are not installed or completed; do not create a freeze yet.')
    scripts.update(new_scripts)
    if len(set(scripts.values()))!=len(scripts):raise ValueError('Duplicate canonical window cannot stand in for a new workflow.')
    canonical_bindings=canonical_binding_plan();canonical_before=canonical_inputs(canonical_bindings)
    supplemental=set(old['supplemental_public_inputs_sha256']);selected={};options={}
    supplemental.update(row['public_path']for row in canonical_bindings)
    sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
    for mode,name in scripts.items():
        path=public(name);raw=path.read_bytes();tree=ast.parse(raw)
        bound=any(isinstance(n,ast.FunctionDef)and n.name=='bound_files'for n in tree.body)
        if bound:
            api={'__file__':str(path),'__name__':'_full410_selected_sources_only_not_main'}
            exec(compile(raw,str(path),'exec'),api)
            mapping=api['bound_files']()
            if not mapping or any(sha(canonical_selected_source(k,mode))!=(v['sha256']if type(v)is dict else v)for k,v in mapping.items()):raise ValueError('Actual public/canonical explicit source map differs: '+name)
            selected[mode]=sorted(mapping)
        elif mode in old['p3_script_selected_paths']:selected[mode]=old['p3_script_selected_paths'][mode]
        else:raise ValueError('New native window needs a complete source-binding API: '+name)
        if path.read_bytes()!=raw:raise ValueError('Source changed while discovering exact map: '+name)
        supplemental.update(k for k in selected[mode]if not k.startswith('.cache/'));supplemental.add(name)
        default=visible_default(raw,name)
        if mode in old['p3_script_options']:
            options[mode]=dict(old['p3_script_options'][mode])
            if options[mode]['accepts_visible_ms']!=(default is not None):raise ValueError('Changed parser contract requires review: '+name)
        else:options[mode]={'accepts_visible_ms':default is not None,'visible_ms':default}
        options[mode]['canonical_visible_default_ms']=default
    if canonical_inputs(canonical_bindings,selected)!=canonical_before:raise ValueError('Canonical369 local/public inputs drifted during discovery.')
    options['p3_311']['visible_ms']=300000
    options['p3_334']['visible_ms']=180000
    if options['p3_312']['canonical_visible_default_ms']!=120000:raise ValueError('Review312 parser if its actual default changes; never replace with60seconds.')
    options['p3_312'].update(visible_ms=120000,use_canonical_visible_default=True)
    options['p3_304']['explicit_current_source_freeze']=True
    options['p3_305']['explicit_current_source_freeze']=True
    for mode in('p3_304','p3_305'):
        if b'--source-freeze'not in public(scripts[mode]).read_bytes():raise ValueError('Canonical current-freeze parser required: '+mode)
    for name in old['supplemental_public_inputs_sha256']:public(name)
    bindings=old['local_public_input_bindings'];locals_before=input_bindings(bindings)
    extra={name:sha(ROOT/name)for name in old['legacy_external_additional_sha256']}
    templates={mode:{name:sha(BASE/('template-'+mode)/name)for name in names}for mode,names in old['template_bundle_sha256'].items()}
    if templates!=old['template_bundle_sha256']:raise ValueError('Original52/30/29/typed workflow templates changed.')
    requested=json.loads(args.functional_receipts.read_bytes())
    if requested.get('section')!=410 or set(requested['references'])!={'necessary','native','native_process'}:raise ValueError('Explicit actual410 necessary/native receipts required, not a presumed filename or old PASS.')
    refs={}
    for label,name in requested['references'].items():
        path=public(name);value=json.loads(path.read_bytes())
        if value.get('passed')is not True:raise ValueError('Final functional receipt did not pass: '+name)
        before=value['source_sha256_before'];after=value['source_sha256_after']
        if before!=after or any(sha(public(n))!=h for n,h in after.items()):raise ValueError('Final functional receipt has stale source: '+name)
        if label=='necessary'and not(value['actual_observed_exit']==0 and value['methods_ran']>0):raise ValueError('Actual necessary test exit is not0.')
        if label=='native'and not(value['unique_checks']>0 and value.get('verification_window_closed')is True and type(value.get('process_id'))is int and value['qpa']=='windows'):raise ValueError('Actual final native receipt is not complete Windows acceptance.')
        if label=='native_process'and value['actual_observed_exit']!=0:raise ValueError('Actual native process exit is not0.')
        refs[label]={'path':name,'sha256':sha(path)}
    record={'section':410,'actual_validation_attempt':ATTEMPT,'root_declared':True,'declared_at':now(),'parent_commit':parent,
        **actual,'supplemental_public_inputs_sha256':{n:sha(public(n))for n in sorted(supplemental)},
        'legacy_native_source_sha256':native,'legacy_external_additional_sha256':extra,
        'local_public_input_bindings':bindings,'local_public_input_sha256':locals_before,
        'canonical_local_public_input_bindings':canonical_bindings,'canonical_local_public_input_sha256':canonical_before,
        'historical_manifest_bindings':old['historical_manifest_bindings'],
        'p3_scripts':scripts,'p3_script_options':options,'p3_script_selected_paths':selected,
        'template_bundle_sha256':templates,'functional_validation':refs,
        'original_typed_auditor_sha256':sha(BASE/'template-legacy/audit_full261_saved_readback.py'),
        'preparation_ready_sha256':sha(READY_PATH),'Linux_WSL_Wine_or_original_private_Windows_verified':False,
        'previous_full_scope_receipt':'verification/full-395/summary.json',
        'previous_full_scope_receipt_sha256':sha(prior_summary),
        'previous_results_not_reused_as_current_PASS':True,
        'prior395_single_available_scope_execution_all_green':summary['single_available_scope_execution_all_green'],
        'all_old642_selectors_and110_native_supplements_retained':True,
        'new_installed_native_scripts':new_scripts,'new_installed_selector_count':len(actual['selectors'])-len(old['selectors']),
        'no_pending_candidates_counted_complete':True,
        'diagnostic_layout_modes':['legacy','current30','current29',*[mode for mode in scripts if int(mode.split('_')[1])<=380]],
        'diagnostic_layout_is_not_default_player_UI_coverage':True,
        'route_mode_not_forced_by_diagnostic_layout':True,
        '312_canonical120s_default_not_60s_and_no_latency_improvement_claimed':True}
    if runner_snapshot()!=actual or native_source_snapshot()!=native or input_bindings(bindings)!=locals_before:raise ValueError('Sources drifted during root declaration; no valid freeze may be written.')
    if any(sha(public(name))!=pin for name,pin in record['supplemental_public_inputs_sha256'].items()):raise ValueError('Supplemental inputs changed during declaration.')
    if any(sha(public(ref['path']))!=ref['sha256']for ref in refs.values()):raise ValueError('Functional evidence changed during declaration.')
    if canonical_inputs(canonical_bindings,selected)!=canonical_before:raise ValueError('Exact canonical local/public originals drifted during declaration.')
    if git('rev-parse','HEAD')!=parent or git('branch','--show-current')!='codex/p2-development':raise ValueError('Parent changed during declaration.')
    write_new(FREEZE,record)
    print(json.dumps({'freeze':str(FREEZE),'sha256':sha(FREEZE),'attempt':ATTEMPT,
                      'selectors':len(actual['selectors']),'source_files':len(actual['source_sha256']),
                      'native_supplements':len(scripts),'actual_Qt_or_tests_started':False},ensure_ascii=False))


if __name__=='__main__':main()
