"""Prepare inactive byte-preserved275 fixtures; activate only on root's explicit freeze."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

ROOT=Path(__file__).resolve().parents[2]
LEGACY=ROOT/'.cache/full275-legacy-bundle'
CURRENT=ROOT/'.cache/full275-current-window'
BASIS=ROOT/'verification/full-261/legacy-window-final/executed-tools'
CURRENT_BASIS=ROOT/'verification/full-261/new-window/verification-scripts'
MAIN_SHA='11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922'
INDICES=[18,19,20,21,38,39,40,41,44,45]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def hashraw(raw):return hashlib.sha256(raw).hexdigest()
def write(path,data):path.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def text(path):return path.read_bytes().decode('utf-8')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def vectors(source):
    tree=ast.parse(source)
    assertions=sorted((n for n in ast.walk(tree) if isinstance(n,ast.Assert)),key=lambda n:(n.lineno,n.col_offset))
    return [ast.dump(n,include_attributes=False) for n in assertions]


def main_try(source):
    trees=[n for n in ast.parse(source).body if isinstance(n,ast.Try) and sum(isinstance(v,ast.Assert) for v in ast.walk(n))==552]
    if len(trees)!=1:raise ValueError('Exact original552 main try was not identified')
    return trees[0],ast.get_source_segment(source,trees[0])


def bootstrap_snippet(out_name):
    return ("# BEGIN EXPLICIT NATIVE275 HISTORICAL FIXTURE CONSTRUCTOR\n"
            "import native275_bootstrap as _native275_bootstrap\n"
            "_native275_restore, _native275_write = _native275_bootstrap.install(ROOT, "+out_name+")\n"
            "# END EXPLICIT NATIVE275 HISTORICAL FIXTURE CONSTRUCTOR\n\n")


def all_tools(folder):
    excluded={'activation275.json','draft275.json','current-source-guard.json','source-freeze.json'}
    return {p.relative_to(folder).as_posix():digest(p) for p in sorted(folder.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.name not in excluded and p.suffix!='.pyc'}


def copy_exact(source,destination):
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():
        if digest(destination)!=digest(source):raise ValueError('Existing candidate path differs from exact copy: '+str(destination))
    else:shutil.copyfile(source,destination)
    if digest(destination)!=digest(source):raise ValueError('Copy was not byte-exact')


def prepare():
    if (LEGACY/'activation275.json').exists() or (CURRENT/'activation275.json').exists():
        raise ValueError('Existing fixture phase must be retained; do not overwrite preparation/activation')
    basis_sha=digest(BASIS/'window.py')
    if basis_sha!='333e9c6efd073e2e8e9ace56e365a3d53ed34bf34bc4609c6dcc8e1aaac260aa':
        raise ValueError('Actual full261 window original differs from successful archived basis')
    originals={}
    for p in sorted(BASIS.rglob('*')):
        if not p.is_file():continue
        relative=p.relative_to(BASIS)
        copy_exact(p,LEGACY/relative);originals[relative.as_posix()]=digest(p)
    copy_exact(BASIS/'window.py',LEGACY/'original261-window.py')
    copy_exact(BASIS/'launcher125.py',LEGACY/'original261-launcher125.py')
    copy_exact(BASIS/'current-source-guard.json',LEGACY/'original261-current-source-guard.json')
    source=text(BASIS/'window.py');node,original_main=main_try(source)
    normalized_main=original_main.replace('\r\n','\n')
    if hashraw(normalized_main.encode())!=MAIN_SHA or len(vectors(source))!=862:
        raise ValueError('Original complete862 AST or552 main try pin differs')
    modified=source.replace("_SOURCE125_GUARD_SHA256 = '93bf61df68409b0ef4bee533fc7c4fef8eca4ce47e403f95ed9a027727277753'",'_SOURCE125_GUARD_SHA256 = None',1)
    modified=modified.replace('_SOURCE125_MAINTAINED_COUNT = 1102','_SOURCE125_MAINTAINED_COUNT = None',1)
    lines=modified.splitlines(keepends=True)
    modified=''.join(lines[:node.lineno-1])+bootstrap_snippet('OUT')+''.join(lines[node.lineno-1:])
    if vectors(source)!=vectors(modified) or main_try(modified)[1]!=original_main:
        raise ValueError('Fixture bootstrap changed any original assert AST or552 main try bytes')
    (LEGACY/'window.py').write_bytes(modified.encode('utf-8'))
    launcher=text(BASIS/'launcher125.py').replace("WINDOW_SHA256 = '"+basis_sha+"'",'WINDOW_SHA256 = None',1).replace("SOURCE125_GUARD_SHA256 = '93bf61df68409b0ef4bee533fc7c4fef8eca4ce47e403f95ed9a027727277753'",'SOURCE125_GUARD_SHA256 = None',1)
    if 'WINDOW_SHA256 = None' not in launcher or 'SOURCE125_GUARD_SHA256 = None' not in launcher:
        raise ValueError('Exactly both archived launcher bindings must be inactive')
    (LEGACY/'launcher125.py').write_bytes(launcher.encode('utf-8'))
    mapping=json.loads((LEGACY/'expected-map125.json').read_bytes())
    if [row['literal_index'] for row in mapping['rows']]!=INDICES:raise ValueError('Exact ten original bridge indices differ')
    preparation=json.loads((ROOT/'.cache/full275-preparation.json').read_bytes())
    relocations=preparation['legacy_window']['additional_dependency_archive_mapping']
    if len(relocations)!=17 or not all(row['matches_old_guard_bytes'] for row in relocations):
        raise ValueError('Exactly17 measured original archive mappings are required')
    new_map=[]
    old_guard=json.loads((BASIS/'current-source-guard.json').read_bytes())
    for index,row in enumerate(relocations):
        archived=ROOT/row['archive_relative']
        expected=old_guard['source_additional_sha256'][row['old_relative']]
        if digest(archived)!=expected:raise ValueError('Archive original SHA changed: '+row['old_relative'])
        target=LEGACY/'bound-prerequisites'/(str(index).zfill(2)+'-'+archived.name)
        copy_exact(archived,target)
        new_map.append({'old_relative':row['old_relative'],'archive_relative':row['archive_relative'],
                        'new_relative':target.relative_to(ROOT).as_posix(),'sha256':expected})
    adaptation={'kind':'SECTION275_INACTIVE_LEGACY_BYTE_PRESERVATION_AUDIT','runtime_executed':False,
                'original_window_sha256':basis_sha,'candidate_window_sha256':digest(LEGACY/'window.py'),
                'all862_assertion_AST_order_unchanged':True,'assertions':862,
                'original552_main_try_bytes_unchanged':True,
                'original552_normalized_main_try_sha256':MAIN_SHA,
                'original552_physical_main_try_utf8_sha256':hashraw(original_main.encode()),
                'case_generators_byte_identical':True,'bridge_indices':INDICES,
                'saved_states_required':52,'runtime_records_required':4283,'projection_records_required':42,
                'original_tool_copies_sha256':originals,'relocations':new_map,
                'only_source_binding_and_explicit_constructor_bootstrap_adapted':True,
                'main_try_and_calculation_results_rewritten':False,'game_api_mocked':False}
    # Prove every original case generator against the successful static ledger.
    static=json.loads((BASIS/'static-preservation.json').read_bytes())
    current_tree=ast.parse(modified)
    for name,expected in static['case_function_raw_sha256'].items():
        nodes=[n for n in current_tree.body if isinstance(n,ast.FunctionDef) and n.name==name]
        if len(nodes)!=1 or hashraw(ast.get_source_segment(modified,nodes[0]).replace('\r\n','\n').encode())!=expected:
            raise ValueError('Original complete case generator changed: '+name)
    write(LEGACY/'adaptation-before-after.json',adaptation)
    prepare_current()
    for folder,allowed in ((LEGACY,['legacy']),(CURRENT,['current30','current29'])):
        write(folder/'draft275.json',{'status':'INACTIVE_DRAFT_NOT_FROZEN_NOT_EXECUTED',
              'allowed_modes':allowed,'draft_tools_sha256':all_tools(folder),
              'root_source_frozen':False,'runtime_executed':False,'source_freeze_required':True})
        write(folder/'activation275.json',{'status':'INACTIVE_DRAFT','binding_ready':False,
              'runtime_executed':False,'allowed_modes':allowed,'root_source_frozen':False})
    print(json.dumps({'prepared':True,'active':False,'legacy_assertions':862,'main_try_unchanged':True,
          'states_required':52,'runtime_records_required':4283,'current30_preserved':True,
          'current29_separate':'only confirmed unavailable symlink specialization omitted, raw30 still required'},ensure_ascii=False))


def prepare_current():
    CURRENT.mkdir(parents=True,exist_ok=True)
    for p in sorted(CURRENT_BASIS.iterdir()):
        if p.is_file():copy_exact(p,CURRENT/p.name)
    copy_exact(CURRENT_BASIS/'window.py',CURRENT/'original261-window.py')
    copy_exact(CURRENT_BASIS/'source-freeze.json',CURRENT/'original261-source-freeze.json')
    copy_exact(LEGACY/'native275_bootstrap.py',CURRENT/'native275_bootstrap.py')
    copy_exact(LEGACY/'launcher275.py',CURRENT/'launcher275.py')
    probe=ROOT/'.cache/full275-preflight/symlink-probe.json'
    copy_exact(probe,CURRENT/'symlink-capability-275.json')
    capability=json.loads(probe.read_bytes())
    if capability['creation_succeeded'] is not False or capability['exception']['winerror']!=1314 or capability['cleanup_pending'] is not False:
        raise ValueError('Separate29 path requires the actual completed same-kind1314 capability proof')
    original=text(CURRENT_BASIS/'window.py')
    modified=original.replace("FREEZE_SHA256='fb50b8dce90e44e329528fe8da126470fdabf7f4d3a4a38f3551e826afbe3aa5'",'FREEZE_SHA256=None',1)
    modified=modified.replace('window=None;qt=None',bootstrap_snippet('OUT')+'window=None;qt=None',1)
    modified=modified.replace("'platform':'Windows binaries under Wine'","'platform':'Actual current native Windows Qt fixture; original Windows history remains unverified'",1)
    modified=modified.replace("record['wine_runtime_requested']='Wine11 devel launcher through shared wine_python lock'","record['actual_runtime_requested']='Native project Windows Python, ownedPopen/job supervisor'",1)
    if vectors(original)!=vectors(modified):raise ValueError('Original30 assertion AST/order changed')
    (CURRENT/'window.py').write_bytes(modified.encode())
    start=modified.index('  # Real MainWindow-owned public state:')
    end=modified.index('  window.close();qt.processEvents();window=None',start)
    omitted=modified[start:end]
    insert=("  record['maintenance261_safe_save_check']=False\n"
            "  record['maintenance261_symlink_specialization']='unavailable: actual same-kind native Windows probe returned WinError1314'\n"
            "  record['original30_full_script_retained_and_required']=True\n")
    available=modified[:start]+insert+modified[end:]
    (CURRENT/'window29.py').write_bytes(available.encode())
    # Original29-prefix statements before the30th block are exact; helpers byte exact.
    if available[:start]!=modified[:start] or available[start+len(insert):]!=modified[end:]:
        raise ValueError('Separate29 path changed statements outside the proven unavailable30th block')
    write(CURRENT/'adaptation-before-after.json',{
        'kind':'SECTION275_INACTIVE_CURRENT_WINDOW_30_AND_AVAILABLE29_PRESERVATION',
        'runtime_executed':False,'root_source_frozen':False,
        'original30_script_sha256':digest(CURRENT_BASIS/'window.py'),
        'candidate30_script_sha256':digest(CURRENT/'window.py'),
        'candidate29_script_sha256':digest(CURRENT/'window29.py'),
        'all_original30_assertion_AST_order_unchanged':True,
        'original30_assertion_count':len(vectors(original)),
        'available29_all_statements_outside_261_symlink_block_exact':True,
        'available29_has_not_passed_yet':True,'original30_must_execute_and_preserve_actual_failure':True,
        'omitted_only_in_separate29':{'raw_source_utf8_sha256':hashraw(omitted.encode()),
            'assertion_count':len(vectors(textwrap.dedent(omitted))), 'reason':'Actual native WinError1314 capability, not a numerical/model failure',
            'capability_proof_sha256':digest(CURRENT/'symlink-capability-275.json')},
        'helper_exact_sha256':{name:digest(CURRENT/name) for name in ('window_added_flows.py','window_extra_flows.py')},
        'hardlink_junction_regular_substitute_used':False,'results_rewritten':False})


def maintained_sources():
    result={}
    for folder in ('rouge','tests','scripts'):
        for p in sorted((ROOT/folder).rglob('*')):
            if '__pycache__' in p.parts or p.suffix not in ('.py','.json') or not p.is_file():continue
            if p.is_symlink():raise ValueError('Production source symlinks are not accepted')
            result[p.relative_to(ROOT).as_posix()]=digest(p)
    return dict(sorted(result.items()))


def activate(freeze,parent):
    if git('branch','--show-current')!='codex/p2-development' or git('rev-parse','HEAD')!=parent:
        raise ValueError('Root-declared branch/parent differs')
    freeze=freeze.resolve()
    if not freeze.is_relative_to(ROOT):raise ValueError('Root freeze must be an existing project artifact')
    frozen=json.loads(freeze.read_bytes())
    if frozen.get('parent_commit')!=parent or not isinstance(frozen.get('source_sha256'),dict):
        raise ValueError('The explicit root freeze/parent declaration is required')
    for name in frozen['source_sha256']:
        relative=Path(name)
        if (not isinstance(name,str) or relative.is_absolute() or '..' in relative.parts or
            '\\' in name or name!=relative.as_posix() or
            (name!='CORE_0.70_VERIFICATION.json' and
             (not relative.parts or relative.parts[0] not in ('rouge','tests','scripts') or relative.suffix not in ('.py','.json')))):
            raise ValueError('Freeze paths must contain maintained public source only; private paths are refused')
        if (ROOT/relative).is_symlink():raise ValueError('Frozen source symlink refused')
    for name,expected in frozen['source_sha256'].items():
        if digest(ROOT/name)!=expected:raise ValueError('Root-frozen actual source drift: '+name)
    for folder in (LEGACY,CURRENT):
        state=json.loads((folder/'activation275.json').read_bytes())
        draft=json.loads((folder/'draft275.json').read_bytes())
        if state['binding_ready'] or state['status']!='INACTIVE_DRAFT':raise ValueError('Only a fresh inactive phase may activate')
        if all_tools(folder)!=draft['draft_tools_sha256']:raise ValueError('Reviewed draft executed-tool bytes changed')
    sources=maintained_sources()
    old=json.loads((LEGACY/'original261-current-source-guard.json').read_bytes())
    adaptation=json.loads((LEGACY/'adaptation-before-after.json').read_bytes())
    remap={r['old_relative']:r for r in adaptation['relocations']}
    additional={}
    for name,expected in old['source_additional_sha256'].items():
        target=ROOT/remap[name]['new_relative'] if name in remap else ROOT/name
        if digest(target)!=expected:raise ValueError('Unchanged original supplemental proof differs: '+name)
        additional[target.relative_to(ROOT).as_posix()]=expected
    additional[freeze.relative_to(ROOT).as_posix()]=digest(freeze)
    for name in ('native275_bootstrap.py','supervisor275.py','launcher275.py','prepare275.py'):
        additional[(LEGACY/name).relative_to(ROOT).as_posix()]=digest(LEGACY/name)
    covered=set(sources)|set(additional)
    if set(frozen['source_sha256'])-covered:raise ValueError('Root freeze has files outside the complete legacy guard')
    guard=dict(old)
    guard.update(section=275,product_commit=parent,tested_worktree_parent_commit=parent,
                 source_sha256=sources,source_additional_sha256=additional,
                 actual_full275_native_run_required=True,runtime_executed=False,
                 old140_source_guard_reused=False,source273_274_added_and_275_current_bound=True,
                 root_freeze_sha256=digest(freeze),root_freeze_source_count=len(frozen['source_sha256']),
                 source_coverage_complete=True,scope='Current275 complete preserved legacy fixture, actual native Windows; no historical native/game/chat certification')
    write(LEGACY/'current-source-guard.json',guard)
    guard_sha=digest(LEGACY/'current-source-guard.json')
    legacy_text=text(LEGACY/'window.py').replace('_SOURCE125_GUARD_SHA256 = None',"_SOURCE125_GUARD_SHA256 = '"+guard_sha+"'",1).replace('_SOURCE125_MAINTAINED_COUNT = None','_SOURCE125_MAINTAINED_COUNT = '+str(len(sources)),1)
    if vectors(text(LEGACY/'original261-window.py'))!=vectors(legacy_text) or main_try(legacy_text)[1]!=main_try(text(LEGACY/'original261-window.py'))[1]:
        raise ValueError('Activation changed original legacy assertion/maintry semantics')
    (LEGACY/'window.py').write_bytes(legacy_text.encode())
    launcher_text=text(LEGACY/'launcher125.py').replace('WINDOW_SHA256 = None',"WINDOW_SHA256 = '"+digest(LEGACY/'window.py')+"'",1).replace('SOURCE125_GUARD_SHA256 = None',"SOURCE125_GUARD_SHA256 = '"+guard_sha+"'",1)
    (LEGACY/'launcher125.py').write_bytes(launcher_text.encode())
    copy_exact(freeze,CURRENT/'root-declared-source-freeze.json')
    # This independent alias replaces the copied261 freeze only inside the new bundle.
    (CURRENT/'source-freeze.json').write_bytes(freeze.read_bytes())
    for name in ('window.py','window29.py'):
        (CURRENT/name).write_bytes(text(CURRENT/name).replace('FREEZE_SHA256=None',"FREEZE_SHA256='"+digest(freeze)+"'",1).encode())
    if sources!=maintained_sources() or git('rev-parse','HEAD')!=parent:
        raise ValueError('Production source changed during activation; do not run this candidate')
    for folder,allowed in ((LEGACY,['legacy']),(CURRENT,['current30','current29'])):
        write(folder/'activation275.json',{'status':'CURRENT275_SOURCE_BOUND_NOT_EXECUTED',
            'binding_ready':True,'runtime_executed':False,'allowed_modes':allowed,
            'tested_worktree_parent_commit':parent,'root_freeze_relative':freeze.relative_to(ROOT).as_posix(),
            'root_freeze_sha256':digest(freeze),'root_freeze_source_count':len(frozen['source_sha256']),
            'execution_tools_sha256':all_tools(folder),'current_root_source_declared_frozen_by_caller':True})
    print(json.dumps({'activated':True,'executed':False,'root_source_files':len(frozen['source_sha256']),
                     'legacy_maintained_files':len(sources),'selectors_in_root_freeze':len(frozen.get('selectors',[])),
                     'legacy_guard_sha256':guard_sha},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();op=parser.add_mutually_exclusive_group(required=True)
    op.add_argument('--prepare',action='store_true');op.add_argument('--activate',action='store_true')
    parser.add_argument('--root-declared-freeze',type=Path);parser.add_argument('--expected-parent-commit')
    args=parser.parse_args()
    if args.prepare:prepare()
    else:
        if args.root_declared_freeze is None or args.expected_parent_commit is None:
            parser.error('Root must explicitly provide its declared final freeze and exact parent before activation')
        activate(args.root_declared_freeze,args.expected_parent_commit)
