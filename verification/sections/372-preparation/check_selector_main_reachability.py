"""Observe original __main__ entry selectors and stop before main's first line.

Read-only source/definition execution; never load or execute tests, Qt or a suite.
The trace interrupts the genuine compiled main at its call event, rather than
moving a source statement or pretending import-mode discovery is CLI discovery.
"""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,ast,json,sys

R=Path(__file__).resolve().parents[1]
class StoppedBeforeMainBody(BaseException):pass

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();output=args.output if args.output.is_absolute()else R/args.output
    if output.exists()or not output.resolve().is_relative_to((R/'.cache').resolve()):raise ValueError('New cache-only observation output required')
    target=R/'scripts/verify_full_available.py';raw=target.read_bytes();source_hash=sha256(raw).hexdigest();tree=ast.parse(raw)
    # Inspect the actual current module top level before definition execution.
    # Existing top-level imports are stdlib; maintained_selectors imports only
    # the explicit MODULES tuple from verify_cloud, whose main guard is false.
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.ClassDef,ast.Import,ast.ImportFrom,ast.Assign,ast.AugAssign)):continue
        if isinstance(node,ast.Expr)and isinstance(node.value,ast.Constant):continue
        if isinstance(node,ast.Expr)and isinstance(node.value,ast.Call)and ast.unparse(node.value.func)=='sys.path.insert':continue
        if isinstance(node,ast.If)and ast.unparse(node.test)=="__name__ == '__main__'":continue
        raise ValueError('Review unexpected top-level executable statement before observation: '+ast.unparse(node))
    old_path=list(sys.path);old_trace=sys.gettrace();seen={};main_lines=0;entry_count=0
    if old_trace is not None:raise ValueError('Existing debugger/trace owner must not be replaced')
    def trace(frame,event,arg):
        nonlocal main_lines,entry_count
        if frame.f_code.co_filename==str(target)and frame.f_code.co_name=='main':
            if event=='line':main_lines+=1
            if event=='call':
                entry_count+=1
                seen['additional_modules']=list(frame.f_globals['ADDITIONAL_MODULES'])
                seen['maintained_selectors']=frame.f_globals['maintained_selectors']()
                raise StoppedBeforeMainBody()
        return trace
    try:
        sys.path[:0]=[str(R),str(R/'scripts')]
        snapshot={'__file__':str(target),'__name__':'_selector_snapshot_definition_only'}
        exec(compile(raw,str(target),'exec'),snapshot)
        expected={'additional_modules':list(snapshot['ADDITIONAL_MODULES']),'maintained_selectors':snapshot['maintained_selectors']()}
        actual={'__file__':str(target),'__name__':'__main__'}
        sys.settrace(trace)
        try:exec(compile(raw,str(target),'exec'),actual)
        except StoppedBeforeMainBody:pass
        else:raise ValueError('Original main entry was not actually intercepted')
    finally:
        sys.settrace(old_trace);sys.path[:]=old_path
    if entry_count!=1 or main_lines!=0:raise ValueError('Original main body must execute zero lines')
    if target.read_bytes()!=raw:raise ValueError('Source drift during read-only observation')
    same=seen==expected
    report={'kind':'ORIGINAL_MAIN_ENTRY_SELECTOR_REACHABILITY_NO_TEST_EXECUTION','at_utc':datetime.now(timezone.utc).isoformat(),
        'source':'scripts/verify_full_available.py','source_sha256':source_hash,'source_unchanged':True,
        'main_call_intercepted_from_original_compiled_source':True,'actual_main_entry_count':entry_count,
        'original_main_body_line_events':main_lines,'test_or_Qt_or_suite_started':False,'formal_tree_modified':False,
        'snapshot':expected,'actual_at_original_main_call':seen,'ordered_selector_sets_equal':same,
        'unreachable_additional_selectors':[v for v in expected['additional_modules']if v not in seen['additional_modules']],
        'not_full_validation_or_test_PASS':True}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf8')as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'observation':str(output),'sha256':sha256(output.read_bytes()).hexdigest(),
        'ordered_selector_sets_equal':same,'snapshot_selectors':len(expected['maintained_selectors']),
        'actual_main_entry_selectors':len(seen['maintained_selectors']),'main_body_lines_executed':main_lines,
        'tests_started':False},ensure_ascii=False))
    return 0 if same else 1
if __name__=='__main__':raise SystemExit(main())
