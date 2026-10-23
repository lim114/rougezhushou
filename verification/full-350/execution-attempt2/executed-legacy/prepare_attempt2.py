"""Prepare only attempt2 observer import-order adapter; never overwrite used attempt1."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OLD=ROOT/'.cache/full275-legacy-bundle'
SEAL=HERE/'attempt1-original-seal'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def source(path):return path.read_bytes().decode('utf-8')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def vector(text):
    nodes=sorted((n for n in ast.walk(ast.parse(text)) if isinstance(n,ast.Assert)),key=lambda n:(n.lineno,n.col_offset))
    return [ast.dump(n,include_attributes=False) for n in nodes]


def maintry(text):
    nodes=[n for n in ast.parse(text).body if isinstance(n,ast.Try) and sum(isinstance(a,ast.Assert) for a in ast.walk(n))==552]
    if len(nodes)!=1:raise ValueError('Exactly the original552-assert maintry must remain')
    return ast.get_source_segment(text,nodes[0])


def observer_function(text):
    nodes=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='_install_narrow_observers100']
    if len(nodes)!=1:raise ValueError('Exactly the original observer installer source function must remain')
    return ast.get_source_segment(text,nodes[0])


def tools():
    excluded={'activation275.json','attempt2-draft.json','current-source-guard.json','source-freeze.json','draft275.json'}
    return {p.relative_to(HERE).as_posix():sha(p) for p in sorted(HERE.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.name not in excluded and p.suffix!='.pyc'}


def sealed_failure_verified():
    record=json.loads((SEAL/'seal.json').read_bytes())
    if record['actual_child_exit']!=1 or record['timed_out'] or record['source_drift']:
        raise ValueError('Actual original attempt1 terminal failure is required')
    for relative,pin in record['raw_originals'].items():
        if sha(SEAL/relative)!=pin['sha256'] or (SEAL/relative).stat().st_size!=pin['bytes']:
            raise ValueError('Sealed original evidence/source changed: '+relative)


def prepare():
    if (HERE/'activation275.json').exists():raise ValueError('Retain an existing attempt2 phase')
    sealed_failure_verified()
    old_state=json.loads((OLD/'activation275.json').read_bytes())
    for name,expected in old_state['execution_tools_sha256'].items():
        if sha(OLD/name)!=expected:raise ValueError('Used attempt1 source changed: '+name)
    early=json.loads((HERE/'observer-import-order-early_app.json').read_bytes())
    correct=json.loads((HERE/'observer-import-order-original.json').read_bytes())
    if (early['actual_same_call_entry_delta'].get('calculate_damage',0)!=0 or
        correct['actual_same_call_entry_delta'].get('calculate_damage',0)!=1 or
        early['actual_result_sha256']!=correct['actual_result_sha256'] or
        early['QApplication_created'] or correct['QApplication_created']):
        raise ValueError('Actual non-GUI unchanged-observer counterexample closure is required')
    for p in sorted(OLD.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        relative=p.relative_to(OLD);target=HERE/relative
        if target.exists():raise ValueError('Do not overwrite candidate path: '+str(relative))
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
        if sha(target)!=sha(p):raise ValueError('Attempt1 tool copy is not exact')
    original=source(OLD/'window.py')
    marker_start='# BEGIN EXPLICIT NATIVE275 HISTORICAL FIXTURE CONSTRUCTOR\n'
    marker_end='# END EXPLICIT NATIVE275 HISTORICAL FIXTURE CONSTRUCTOR\n\n'
    first=original.index(marker_start);last=original.index(marker_end,first)+len(marker_end)
    delayed=("# BEGIN EXPLICIT NATIVE275 HISTORICAL FIXTURE CONSTRUCTOR\n"
             "import native275_bootstrap as _native275_bootstrap\n"
             "def _native275_after_unchanged_observers(original_installer):\n"
             "    @functools.wraps(original_installer)\n"
             "    def _call_original_then_constructor_bootstrap(*args, **kwargs):\n"
             "        returned = original_installer(*args, **kwargs)\n"
             "        _native275_bootstrap.install(ROOT, OUT)\n"
             "        return returned\n"
             "    return _call_original_then_constructor_bootstrap\n"
             "_install_narrow_observers100 = _native275_after_unchanged_observers(_install_narrow_observers100)\n"
             "# END EXPLICIT NATIVE275 HISTORICAL FIXTURE CONSTRUCTOR\n\n")
    candidate=original[:first]+delayed+original[last:]
    candidate,count=re.subn(r"(?m)^_SOURCE125_GUARD_SHA256 = '[0-9a-f]{64}'$",'_SOURCE125_GUARD_SHA256 = None',candidate)
    if count!=1:raise ValueError('One source guard binding is required')
    candidate,count=re.subn(r'(?m)^_SOURCE125_MAINTAINED_COUNT = [0-9]+$','_SOURCE125_MAINTAINED_COUNT = None',candidate)
    if count!=1:raise ValueError('One maintained-count binding is required')
    if (len(vector(candidate))!=862 or vector(candidate)!=vector(original) or
        maintry(candidate)!=maintry(original) or observer_function(candidate)!=observer_function(original)):
        raise ValueError('Any original assertion,552 maintry or observer installer source changed')
    (HERE/'window.py').write_bytes(candidate.encode('utf-8'))
    launcher=source(HERE/'launcher125.py')
    launcher,count=re.subn(r"(?m)^WINDOW_SHA256 = '[0-9a-f]{64}'$",'WINDOW_SHA256 = None',launcher)
    if count!=1:raise ValueError('One window launcher binding is required')
    launcher,count=re.subn(r"(?m)^SOURCE125_GUARD_SHA256 = '[0-9a-f]{64}'$",'SOURCE125_GUARD_SHA256 = None',launcher)
    if count!=1:raise ValueError('One source launcher binding is required')
    (HERE/'launcher125.py').write_bytes(launcher.encode())
    ledger={'kind':'SECTION275_ATTEMPT2_OBSERVER_IMPORT_ORDER_ONLY_ADAPTATION',
        'status':'PREPARED_NOT_ROOT_BOUND_NOT_EXECUTED','actual_attempt1_completed_appends':4213,
        'original_attempt1_failure_seal_sha256':sha(SEAL/'seal.json'),
        'root_source_freeze_sha256_unchanged_required':old_state['root_freeze_sha256'],
        'original_active_attempt1_window_sha256':sha(OLD/'window.py'),
        'prepared_attempt2_window_sha256':sha(HERE/'window.py'),
        'all862_original_assert_AST_order_unchanged':True,'original552_maintry_source_bytes_unchanged':True,
        'original_observer_installer_function_source_bytes_unchanged':True,
        'counter_values_or_damage_aliases_manually_patched':False,
        'calculator_results_rewritten':False,'game_api_mocked':False,
        'only_change':'Delegate the exact original narrow observer installer first, preserve its return/exceptions, then perform the normal constructor bootstrap/app import',
        'early_import_actual_calculate_damage_delta':0,'original_import_actual_calculate_damage_delta':1,
        'actual_calculator_result_hash_equal':early['actual_result_sha256'],
        'states_required':52,'records_required':4283,'projection_records_required':42,
        'bridge_indices':[18,19,20,21,38,39,40,41,44,45],
        'production_or_tests_edited':False,'native_gui_reexecuted':False}
    write(HERE/'attempt2-adaptation.json',ledger)
    write(HERE/'activation275.json',{'status':'INACTIVE_DRAFT','binding_ready':False,
          'runtime_executed':False,'allowed_modes':['legacy'],'root_source_frozen_by_this_worker':False})
    write(HERE/'attempt2-draft.json',{'status':'INACTIVE_DRAFT','reviewed_draft_tools_sha256':tools(),
          'old_root_freeze_sha256':old_state['root_freeze_sha256'],
          'old_root_freeze_relative':old_state['root_freeze_relative'],
          'old_parent_commit':old_state['tested_worktree_parent_commit'],
          'root_rebinding_required':True,'native_gui_executed':False})
    print(json.dumps({'prepared':True,'activated':False,'gui_started':False,'original862_asserts':True,
                      '552maintry':True,'observer_installer_original_source':True},ensure_ascii=False))


def activate(freeze,parent):
    draft=json.loads((HERE/'attempt2-draft.json').read_bytes())
    state=json.loads((HERE/'activation275.json').read_bytes())
    if state['binding_ready'] or state['status']!='INACTIVE_DRAFT':raise ValueError('Only a new inactive attempt2 may be root-bound')
    if tools()!=draft['reviewed_draft_tools_sha256']:raise ValueError('Reviewed attempt2 executed source changed')
    sealed_failure_verified()
    if git('branch','--show-current')!='codex/p2-development' or git('rev-parse','HEAD')!=parent or parent!=draft['old_parent_commit']:
        raise ValueError('The exact same root-frozen branch/parent is required')
    freeze=freeze.resolve()
    if (not freeze.is_relative_to(ROOT) or freeze.relative_to(ROOT).as_posix()!=draft['old_root_freeze_relative'] or
        sha(freeze)!=draft['old_root_freeze_sha256']):raise ValueError('Exact same root-declared source-freeze bytes are required')
    frozen=json.loads(freeze.read_bytes())
    for name,expected in frozen['source_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('Original root-frozen source changed: '+name)
    guard=json.loads((OLD/'current-source-guard.json').read_bytes())
    for name,expected in guard['source_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('Complete original maintained source changed: '+name)
    relocated={}
    old_prefix=OLD.relative_to(ROOT).as_posix()+'/'
    new_prefix=HERE.relative_to(ROOT).as_posix()+'/'
    for name,expected in guard['source_additional_sha256'].items():
        new_name=new_prefix+name[len(old_prefix):] if name.startswith(old_prefix) else name
        if sha(ROOT/new_name)!=expected:raise ValueError('Original supplemental proof bytes changed: '+name)
        relocated[new_name]=expected
    relocated[(HERE/'prepare_attempt2.py').relative_to(ROOT).as_posix()]=sha(HERE/'prepare_attempt2.py')
    relocated[(HERE/'attempt2-adaptation.json').relative_to(ROOT).as_posix()]=sha(HERE/'attempt2-adaptation.json')
    guard.update(source_additional_sha256=relocated,actual_full275_native_attempt=2,
          observer_import_order_adapter_corrected=True,original_observer_function_unchanged=True,
          source_freeze_sha256_same_as_attempt1=draft['old_root_freeze_sha256'],runtime_executed=False)
    write(HERE/'current-source-guard.json',guard)
    guard_sha=sha(HERE/'current-source-guard.json')
    candidate=source(HERE/'window.py').replace('_SOURCE125_GUARD_SHA256 = None',"_SOURCE125_GUARD_SHA256 = '"+guard_sha+"'",1).replace('_SOURCE125_MAINTAINED_COUNT = None','_SOURCE125_MAINTAINED_COUNT = '+str(len(guard['source_sha256'])),1)
    original=source(OLD/'window.py')
    if vector(candidate)!=vector(original) or maintry(candidate)!=maintry(original) or observer_function(candidate)!=observer_function(original):
        raise ValueError('Binding changed original assertions/maintry/observer source')
    (HERE/'window.py').write_bytes(candidate.encode())
    launcher=source(HERE/'launcher125.py').replace('WINDOW_SHA256 = None',"WINDOW_SHA256 = '"+sha(HERE/'window.py')+"'",1).replace('SOURCE125_GUARD_SHA256 = None',"SOURCE125_GUARD_SHA256 = '"+guard_sha+"'",1)
    (HERE/'launcher125.py').write_bytes(launcher.encode())
    write(HERE/'activation275.json',{'status':'CURRENT275_SOURCE_BOUND_NOT_EXECUTED','binding_ready':True,
          'runtime_executed':False,'allowed_modes':['legacy'],'tested_worktree_parent_commit':parent,
          'root_freeze_relative':draft['old_root_freeze_relative'],'root_freeze_sha256':sha(freeze),
          'root_freeze_source_count':len(frozen['source_sha256']),'execution_tools_sha256':tools(),
          'current_root_source_declared_frozen_by_caller':True,'actual_native_attempt':2,
          'source_freeze_same_as_actual_attempt1':True})
    print(json.dumps({'root_bound':True,'executed':False,'guard_sha256':guard_sha,
                      'root_source_freeze_unchanged':True},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare',action='store_true');group.add_argument('--activate',action='store_true')
    parser.add_argument('--same-root-freeze',type=Path);parser.add_argument('--expected-parent-commit')
    args=parser.parse_args()
    if args.prepare:prepare()
    else:
        if args.same_root_freeze is None or args.expected_parent_commit is None:parser.error('Root must explicitly bind exact same freeze/parent')
        activate(args.same_root_freeze,args.expected_parent_commit)
