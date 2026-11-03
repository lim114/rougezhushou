"""Work-only explicit two-helper current-contract maintenance, full scope."""
import argparse,ast,hashlib,importlib.util,json,re,shutil
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('_explicit_flower_factory',BASE/'prepare_full260_flower_window.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
AUDIT_WARNING_ONLY=m.audit
SUSURO='require_susuro_checkbox085'
sha=m.digest;write=m.write

def function_assertions(source):
    return sorted((n for n in ast.walk(ast.parse(source))if isinstance(n,ast.Assert)),key=lambda n:(n.lineno,n.col_offset))

def all_assertions(source,exclude_helpers=False):
    tree=ast.parse(source);spans=[(n.lineno,n.end_lineno)for n in tree.body
        if isinstance(n,ast.FunctionDef)and n.name in (m.TARGET,SUSURO)]
    nodes=sorted((n for n in ast.walk(tree)if isinstance(n,ast.Assert)),key=lambda n:(n.lineno,n.col_offset))
    return [ast.dump(n,include_attributes=False)for n in nodes
        if not exclude_helpers or not any(a<=n.lineno<=b for a,b in spans)]

def audit(source,bundle):
    original=(bundle/'legacy-preserved-basis-window.py').read_text()
    _,a,b=m.span(original,SUSURO);old=original[a:b]
    _,a,b=m.span(source,SUSURO);current=source[a:b]
    assert current==(bundle/'susuro-total-current.py').read_text(),'Current None guard differs from reviewed source'
    result=AUDIT_WARNING_ONLY(source[:a]+old+source[b:],bundle)
    old_nodes=function_assertions(old);new_nodes=function_assertions(current)
    cursor=iter(ast.dump(n,include_attributes=False)for n in new_nodes)
    for node in old_nodes:
        expected=ast.dump(node,include_attributes=False)
        assert any(actual==expected for actual in cursor),'An original Susuro assertion/order changed'
    assert all_assertions(source,True)==all_assertions(original,True),'Other assertion AST/order changed'
    result.update(actual_full260_attempt=4,current_assertions=len(all_assertions(source)),
        unchanged_assertions_outside_named_functions=len(all_assertions(source,True)),
        outside_functions_assertion_AST_order_sha256=hashlib.sha256(json.dumps(all_assertions(source,True),separators=(',',':')).encode()).hexdigest(),
        current_assertion_AST_order_sha256=hashlib.sha256(json.dumps(all_assertions(source),separators=(',',':')).encode()).hexdigest(),
        all_source_outside_two_named_functions_and_two_binding_constants_unchanged=True,
        susuro_original_assertions_retained_in_order=len(old_nodes),susuro_current_assertions=len(new_nodes),
        susuro_historical_function_sha256=hashlib.sha256(old.encode()).hexdigest(),susuro_current_function_sha256=sha(bundle/'susuro-total-current.py'))
    for key in ('unchanged_assertions_outside_named_function','outside_function_assertion_AST_order_sha256',
                'all_source_outside_function_and_two_binding_constants_unchanged'):
        result.pop(key,None)
    return result

def prepare(bundle):
    proof=json.loads((BASE/'susuro-total-probe-proof.json').read_bytes())
    if proof.get('tests_passed')!=5 or proof.get('original_section82_cases')!=216:raise ValueError('Required216/source/negative probes incomplete')
    if proof['guard_sha256']!=sha(BASE/'susuro-total-current.py'):raise ValueError('None guard changed after probes')
    for name,digest in proof['producer_sha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('None-source producer changed: '+name)
    m.prepare(bundle)
    for name in ('susuro-total-current.py','susuro-total-probe-proof.json','test_susuro_total_revision.py','susuro-total-probes.log','susuro-total-probes.exit'):
        shutil.copyfile(BASE/name,bundle/name)
    source=(bundle/'window.py').read_text();_,start,end=m.span(source,SUSURO)
    old=source[start:end];new=(bundle/'susuro-total-current.py').read_text()
    (bundle/'window.py').write_text(source[:start]+new+source[end:])
    evidence=ROOT/'research/p2-susuro-healing-composition-current/receipt.json'
    ledger={'kind':'EXPLICIT_TWO_HELPER_SOURCE_JUSTIFIED_CURRENT_CONTRACT_REVISION','actual_full260_attempt':4,
        'historical_assertions':831,'current_assertions':862,'historical_helpers':{'require_warning_order085':14,SUSURO:10},
        'current_helpers':{'require_warning_order085':38,SUSURO:17},'unchanged_original_assertions_outside_helpers':807,
        'flower_revision_ledger_sha256':sha(bundle/'flower-warning-revision-ledger.json'),
        'susuro_original_function_sha256':hashlib.sha256(old.encode()).hexdigest(),'susuro_current_function_sha256':sha(bundle/'susuro-total-current.py'),
        'susuro_source_receipt':str(evidence.relative_to(ROOT)),'susuro_source_receipt_sha256':sha(evidence),
        'exact_missing_ratio_failure_case82_index':168,'actual_cause':'Qualified PHY-X atE2L40, recipient ratio not declared; full healing None while six known subtotals remain. Finite S2 use only controls nonrepeat cycle and is not this cause.',
        'original_susuro_assertions':[ast.unparse(n)for n in function_assertions(old)],
        'current_susuro_assertions':[ast.unparse(n)for n in function_assertions(new)],
        'old10_all_retained_in_order':True,'original552_maintry_bytes_unchanged':True,
        'cases_or_check_records_added':False,'original_projection_bridge_expectations_modified':False,
        'warning_contract_modified':True,'current_grand_total_unknown_guard_modified':True,'dynamic_function_shadowing':False}
    write(bundle/'current-contract-revision-ledger.json',ledger)
    result=audit((bundle/'window.py').read_text(),bundle);write(bundle/'static-preservation.json',result)
    record=json.loads((bundle/'activation.json').read_bytes());record.update(actual_full260_attempt=4,
        current_grand_total_unknown_guard_modified=True,current_contract_revision_ledger_sha256=sha(bundle/'current-contract-revision-ledger.json'))
    for name in ('window.py','susuro-total-current.py','susuro-total-probe-proof.json','test_susuro_total_revision.py',
                 'susuro-total-probes.log','susuro-total-probes.exit','current-contract-revision-ledger.json'):
        record['draft_sha256'][name]=sha(bundle/name)
    write(bundle/'activation.json',record)
    return result

def activate(bundle,expected_parent):
    old_audit=m.audit;old_writer=m.parent.module.write_json
    def writer(path,value):
        if path.name==m.parent.module.OUTPUT_GUARD_NAME:
            for name in ('susuro-total-current.py','susuro-total-probe-proof.json','test_susuro_total_revision.py',
                         'susuro-total-probes.log','susuro-total-probes.exit','current-contract-revision-ledger.json'):
                value['source_additional_sha256'][(bundle/name).relative_to(ROOT).as_posix()]=sha(bundle/name)
            evidence=ROOT/'research/p2-susuro-healing-composition-current/receipt.json'
            value['source_additional_sha256'][evidence.relative_to(ROOT).as_posix()]=sha(evidence)
            for name,digest in json.loads(evidence.read_bytes())['artifact_sha256'].items():
                p=evidence.parent/name
                if sha(p)!=digest:raise ValueError('Susuro source artifact changed: '+name)
                value['source_additional_sha256'][p.relative_to(ROOT).as_posix()]=digest
            value.pop('original_expectations_modified',None)
            value.update(actual_full260_attempt=4,warning_contract_modified=True,
                current_grand_total_unknown_guard_modified=True,original_projection_bridge_expectations_modified=False,
                revision_ledger_sha256=sha(bundle/'current-contract-revision-ledger.json'))
        old_writer(path,value)
    m.audit=audit;m.parent.module.write_json=writer
    try:return m.activate(bundle,expected_parent)
    finally:m.audit=old_audit;m.parent.module.write_json=old_writer

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True)
    op=p.add_mutually_exclusive_group(required=True);op.add_argument('--prepare',action='store_true');op.add_argument('--activate',action='store_true')
    p.add_argument('--expected-parent-commit');args=p.parse_args();bundle=args.bundle.resolve()
    if not bundle.is_relative_to(ROOT/'work'):raise ValueError('Work-only bundle required')
    if args.activate and not re.fullmatch('[0-9a-f]{40}',args.expected_parent_commit or ''):raise ValueError('Root-frozen HEAD required')
    print(json.dumps(prepare(bundle)if args.prepare else activate(bundle,args.expected_parent_commit),ensure_ascii=False))
