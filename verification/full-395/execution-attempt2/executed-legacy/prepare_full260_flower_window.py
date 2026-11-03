"""Explicit source-justified revision of only require_warning_order085.

The complete original cases and functional try remain intact. No runtime
function shadowing, result changes, extra check records, or new admissions.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
TARGET='require_warning_order085'
spec=importlib.util.spec_from_file_location('_source_bound_reset_factory',BASE/'prepare_full260_reset_window.py')
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def span(source,name=TARGET):
    node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name==name)
    lines=source.splitlines(keepends=True)
    return node,sum(map(len,lines[:node.lineno-1])),sum(map(len,lines[:node.end_lineno]))
def assertion_nodes(source,exclude=False):
    tree=ast.parse(source);target=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==TARGET)
    nodes=sorted((n for n in ast.walk(tree) if isinstance(n,ast.Assert)),key=lambda n:(n.lineno,n.col_offset))
    return [n for n in nodes if not exclude or not target.lineno<=n.lineno<=target.end_lineno]
def assertion_dumps(source,exclude=False):
    return [ast.dump(n,include_attributes=False) for n in assertion_nodes(source,exclude)]
def normalized_bindings(source):
    source=re.sub(r"^_SOURCE125_GUARD_SHA256 = (?:None|'[0-9a-f]{64}')$",'_SOURCE125_GUARD_SHA256 = None',source,flags=re.M)
    return re.sub(r'^_SOURCE125_MAINTAINED_COUNT = (?:None|[0-9]+)$','_SOURCE125_MAINTAINED_COUNT = None',source,flags=re.M)
def main_try_bytes(source):
    nodes=[n for n in ast.parse(source).body if isinstance(n,ast.Try)]
    node=max(nodes,key=lambda n:sum(isinstance(a,ast.Assert) for a in ast.walk(n)))
    assert sum(isinstance(a,ast.Assert) for a in ast.walk(node))==552
    return ast.get_source_segment(source,node).encode()
def audit(source,bundle):
    basis=(bundle/'legacy-preserved-basis-window.py').read_text()
    replacement=(bundle/'flower-warning-current.py').read_text()
    _,start,end=span(basis)
    expected=basis[:start]+replacement+basis[end:]
    assert normalized_bindings(source)==expected,'Change outside explicitly replaced function/hash bindings'
    assert assertion_dumps(source,True)==assertion_dumps(basis,True),'Other original assertion AST/order changed'
    assert main_try_bytes(source)==main_try_bytes(basis),'Original552 main try bytes changed'
    _,ns,ne=span(source)
    assert source[ns:ne]==replacement,'Embedded current function differs from reviewed source'
    original=parent.module.LEGACY
    protected=['bridge125.py','expected-map125.json']+[str(p.relative_to(original)) for p in sorted((original/'proofs').iterdir()) if p.is_file()]
    hashes={name:digest(bundle/name) for name in protected}
    assert all(hashes[name]==digest(original/name) for name in protected),'Original42/10 comparison basis changed'
    old_count=len(assertion_nodes(basis));new_count=len(assertion_nodes(source))
    old_node,os,oe=span(basis)
    cases={n.name:hashlib.sha256(ast.get_source_segment(basis,n).encode()).hexdigest()
        for n in ast.parse(basis).body if isinstance(n,ast.FunctionDef) and 'cases' in n.name}
    return {'status':'PASS_EXPLICIT_CURRENT_FUNCTION_REVISION_AND_COMPLETE_SCOPE_PRESERVATION',
        'candidate_after_section':260,'historical_assertions':old_count,'current_assertions':new_count,
        'original_831_all_unchanged_claimed':False,'unchanged_assertions_outside_named_function':len(assertion_nodes(source,True)),
        'outside_function_assertion_AST_order_sha256':hashlib.sha256(json.dumps(assertion_dumps(source,True),separators=(',',':')).encode()).hexdigest(),
        'historical_function_assertions':sum(isinstance(n,ast.Assert) for n in ast.walk(old_node)),
        'current_function_assertions':sum(isinstance(n,ast.Assert) for n in ast.walk(span(source)[0])),
        'historical_function_sha256':hashlib.sha256(basis[os:oe].encode()).hexdigest(),'current_function_sha256':digest(bundle/'flower-warning-current.py'),
        'current_assertion_AST_order_sha256':hashlib.sha256(json.dumps(assertion_dumps(source),separators=(',',':')).encode()).hexdigest(),
        'original_functional_try_assertions':552,'functional_try_bytes_sha256':hashlib.sha256(main_try_bytes(source)).hexdigest(),
        'original_functional_try_bytes_unchanged':True,'all_source_outside_function_and_two_binding_constants_unchanged':True,
        'case_function_raw_sha256':cases,'original42_projection_and_exact10_bridge_fixture_sha256':hashes,
        'literal_indices_preserved':[18,19,20,21,38,39,40,41,44,45],
        'expected_runtime_checks_if_complete':4283,'expected_saved_states_if_complete':52,
        'dynamic_function_shadowing':False,'runtime_executed':False,'product_pass_claimed':False,'native_windows_verified':False}

def prepare(bundle):
    proof=json.loads((BASE/'flower-warning-probe-proof.json').read_bytes())
    if proof.get('tests_passed')!=5 or proof.get('original_section81_cases')!=136:
        raise ValueError('Required source/actual-consumption/negative probes not complete')
    if proof['current_guard_sha256']!=digest(BASE/'flower-warning-current.py'):
        raise ValueError('Current function changed after probes')
    for name,sha in proof['producer_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('Probed producer changed: '+name)
    parent.prepare(bundle)
    shutil.copyfile(bundle/'window.py',bundle/'legacy-preserved-basis-window.py')
    for name in ('flower-warning-current.py','flower-warning-probe-proof.json','test_flower_warning_revision.py'):
        shutil.copyfile(BASE/name,bundle/name)
    basis=(bundle/'window.py').read_text();_,start,end=span(basis)
    old=basis[start:end];new=(bundle/'flower-warning-current.py').read_text()
    (bundle/'window.py').write_text(basis[:start]+new+basis[end:])
    old_asserts=assertion_nodes(old);new_asserts=assertion_nodes(new)
    new_dumps={ast.dump(n,include_attributes=False) for n in new_asserts}
    evidence=ROOT/'research/p2-flower-healing-composition-current/receipt.json'
    ledger={'kind':'EXPLICIT_SOURCE_JUSTIFIED_WARNING_CONTRACT_REVISION','target_function':TARGET,
        'actual_full260_attempt':3,'source_receipt':str(evidence.relative_to(ROOT)),'source_receipt_sha256':digest(evidence),
        'old_function_sha256':hashlib.sha256(old.encode()).hexdigest(),'old_function_assertions':len(old_asserts),
        'new_function_sha256':digest(bundle/'flower-warning-current.py'),'new_function_assertions':len(new_asserts),
        'replaced_old_contract':'Exact proved three flower parameter groups no longer require unknown warnings/rule suppression/incomplete records.',
        'source_supported_current_contract':'Exact per-source native rule proof and product-heal/additive-regen oracles; offline parameters only, actual attachment/ticks/hotfix unknown.',
        'old_assertions':[{'old':ast.unparse(n),'same_assertion_retained':ast.dump(n,include_attributes=False) in new_dumps,
            'replacement_current_function_sha256':digest(bundle/'flower-warning-current.py'),'source_receipt_sha256':digest(evidence)} for n in old_asserts],
        'new_assertions':[ast.unparse(n) for n in new_asserts],
        'old_original831_history_immutable':['/workspace/work/full260-window-evidence/executed-tools/window.py','/workspace/work/full260-window-evidence-attempt2/executed-tools/window.py'],
        'cases_or_check_records_added':False,'original_expected_projection_or_bridge_changed':False,
        'dynamic_shadow_function':False,'original552_maintry_bytes_unchanged':True}
    write(bundle/'flower-warning-revision-ledger.json',ledger)
    result=audit((bundle/'window.py').read_text(),bundle);write(bundle/'static-preservation.json',result)
    record=json.loads((bundle/'activation.json').read_bytes())
    record.update(actual_full260_attempt=3,explicit_revised_warning_contract=True,
        original831_all_unchanged_claimed=False,revision_ledger_sha256=digest(bundle/'flower-warning-revision-ledger.json'))
    for name in ('window.py','flower-warning-current.py','flower-warning-revision-ledger.json','flower-warning-probe-proof.json',
                 'legacy-preserved-basis-window.py','test_flower_warning_revision.py'):
        record['draft_sha256'][name]=digest(bundle/name)
    write(bundle/'activation.json',record)
    return result

def activate(bundle,expected_parent):
    original_audit=parent.module.audit;original_write=parent.module.write_json
    def current_writer(path,value):
        if path.name==parent.module.OUTPUT_GUARD_NAME:
            extra=['flower-warning-current.py','flower-warning-revision-ledger.json','flower-warning-probe-proof.json',
                   'legacy-preserved-basis-window.py','test_flower_warning_revision.py']
            for name in extra:
                value['source_additional_sha256'][(bundle/name).relative_to(ROOT).as_posix()]=digest(bundle/name)
            evidence=ROOT/'research/p2-flower-healing-composition-current/receipt.json'
            value['source_additional_sha256'][evidence.relative_to(ROOT).as_posix()]=digest(evidence)
            for name,sha in json.loads(evidence.read_bytes())['artifacts_sha256'].items():
                p=evidence.parent/name
                if digest(p)!=sha:raise ValueError('Composition evidence artifact drift: '+name)
                value['source_additional_sha256'][p.relative_to(ROOT).as_posix()]=sha
            value.update(actual_full260_attempt=3,explicit_revised_warning_contract=True,
                         original831_all_unchanged_claimed=False,revision_ledger_sha256=digest(bundle/'flower-warning-revision-ledger.json'))
        original_write(path,value)
    parent.module.audit=lambda source:audit(source,bundle)
    parent.module.write_json=current_writer
    try:return parent.activate(bundle,expected_parent)
    finally:
        parent.module.audit=original_audit;parent.module.write_json=original_write

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    op=parser.add_mutually_exclusive_group(required=True);op.add_argument('--prepare',action='store_true');op.add_argument('--activate',action='store_true')
    parser.add_argument('--expected-parent-commit')
    args=parser.parse_args();bundle=args.bundle.resolve()
    if not bundle.is_relative_to(ROOT/'work'):raise ValueError('Work-only revised bundle required')
    if args.activate and not re.fullmatch('[0-9a-f]{40}',args.expected_parent_commit or ''):raise ValueError('Exact root-frozen HEAD required')
    print(json.dumps(prepare(bundle) if args.prepare else activate(bundle,args.expected_parent_commit),ensure_ascii=False))
