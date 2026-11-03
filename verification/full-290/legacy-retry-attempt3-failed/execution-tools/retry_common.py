"""Native legacy retry guards; no job, Qt or production import at module load."""
import hashlib
import json
import sys
import types
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
A2=ROOT/'.cache/p3-full290-repair-prep'
BUNDLE=BASE/'legacy'
PYTHON=ROOT/'.venv/Scripts/python.exe'
FREEZE=ROOT/'verification/full-290/source-freeze-repair.json'
FREEZE_SHA='75cec266144a389b93aced04d150c4cf6e72a23403f250a9caab9915543e6ec0'
ACTIVATION=BUNDLE/'activation-retry290.json'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write_new(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')

def regular(path,boundary):
    if (not path.is_file() or path.is_symlink() or boundary.is_symlink()
            or not path.resolve().is_relative_to(boundary.resolve())):
        raise ValueError('Exact regular public file required: '+str(path))
    for p in path.parents:
        if p==boundary:break
        if p.is_symlink():raise ValueError('Linked parent refused')
    return path

def prepared(parent,preparation_sha):
    if sys.platform!='win32' or Path(sys.executable).resolve()!=PYTHON.resolve():
        raise ValueError('Exact native project Python required')
    path=BASE/'preparation.json'
    if sha(path)!=preparation_sha or sha(FREEZE)!=FREEZE_SHA:
        raise ValueError('Reviewed preparation and unchanged original A2 freeze required')
    meta=json.loads(path.read_bytes())
    for name,expected in meta['new_tools_sha256'].items():
        if sha(regular(BASE/name,BASE))!=expected:raise ValueError('Retry preparation tool drift: '+name)
    old=json.loads(FREEZE.read_bytes())
    for name,expected in old['preparation_tools_sha256'].items():
        if sha(regular(ROOT/name,ROOT))!=expected:raise ValueError('Original A2 controller changed')
    p=A2/'full290_runtime_common.py'
    common=types.ModuleType('full290_runtime_common');common.__file__=str(p)
    sys.modules['full290_runtime_common']=common
    exec(compile(p.read_bytes(),str(p),'exec'),common.__dict__)
    common.validate_freeze(parent)
    old_bundles=common.bound_bundles(parent)
    if {name:r['activation_sha256'] for name,r in old_bundles.items()}!=meta['A2_activation_sha256']:
        raise ValueError('A2 activation identity changed')
    guard=json.loads((BUNDLE/'current-source-guard.json').read_bytes())
    if (guard['source_sha256']!=meta['A2_native_source_sha256']
            or guard['source_additional_sha256']!=meta['A2_additional_runtime_inputs_sha256']):
        raise ValueError('Original native source/additional maps changed')
    for name,expected in {**guard['source_sha256'],**guard['source_additional_sha256']}.items():
        if sha(regular(ROOT/name,ROOT))!=expected:raise ValueError('Native declared input changed: '+name)
    for name,expected in meta['candidate_bundle_tools_sha256'].items():
        if sha(regular(BUNDLE/name,BUNDLE))!=expected:raise ValueError('Exact retry bundle bytes changed: '+name)
    if (len(old['source_sha256']),len(old['supplemental_public_inputs_sha256']),len(old['selectors']))!=(1221,42,430):
        raise ValueError('Original complete source/selector scope changed')
    p=A2/'run_full290_orchestration.py'
    execution=types.ModuleType('_legacy_retry_original_A2_execution');execution.__file__=str(p)
    exec(compile(p.read_bytes(),str(p),'exec'),execution.__dict__)
    return meta,common,execution,old

def closed(folder,execution):
    observed=json.loads((folder/'controller-process.json').read_bytes())
    terminal,detail=execution.terminal_job_record(folder,observed)
    origin=json.loads((folder/'process-exit-origin.json').read_bytes())
    supervisor=json.loads((folder/'supervisor.json').read_bytes())
    if (not terminal or origin.get('derived_from_supervisor_json') is not False
            or origin.get('process_exit_sha256')!=sha(folder/'process.exit')
            or int((folder/'process.exit').read_text(encoding='ascii'))!=observed['actual_observed_popen_exit']):
        raise ValueError('Real retained Popen exit and owned-job closure required')
    return observed,supervisor,detail

def prior_closed_and_sealed(parent,execution):
    result={}
    for archive,kind,controller,key,names,status in (
        ('execution-attempt2','FULL290_REPAIR_ROOT_OWNED_ACTUAL_EXECUTION','run_full290_orchestration.py',
         'source_freeze_sha256',['offline','legacy','current30','current29'],'all_four_terminal'),
        ('p3-supplementary-attempt2','FULL290_REPAIR_ROOT_OWNED_P3_SUPPLEMENTARY_EXECUTION','run_p3_supplementary_windows_290.py',
         'root_freeze_sha256',['p3_286','p3_287','p3_288','p3_289','p3_290'],'all_five_terminal')):
        folder=ROOT/'verification/full-290'/archive
        manifest_path=regular(folder/'archive-manifest.json',folder)
        manifest=json.loads(manifest_path.read_bytes())
        if (manifest.get('source_freeze_sha256')!=FREEZE_SHA or manifest.get('parent_commit')!=parent
                or (archive=='execution-attempt2' and manifest.get('status')!='sealed_exact_outputs_no_pass_claim')):
            raise ValueError('Both original A2 archives must be sealed first')
        for name,info in manifest['files'].items():
            if sha(regular(folder/name,folder))!=info['sha256']:raise ValueError('A2 archive original changed')
        source=Path(manifest['source_container'])
        if (not source.is_absolute() or source.is_symlink() or source.resolve().is_relative_to(ROOT)
                or not source.name.startswith('rouge-full290-repair-')):
            raise ValueError('Actual external owned A2 namespace required')
        own=json.loads((source/'owned-execution.json').read_bytes())
        ledger=json.loads((source/'orchestration.json').read_bytes())
        if (own.get('kind')!=kind or own.get('root')!=str(ROOT) or own.get('parent_commit')!=parent
                or own.get(key)!=FREEZE_SHA or own.get('controller_sha256')!=sha(A2/controller)
                or ledger.get('status')!=status or [r['name'] for r in ledger['steps']]!=names):
            raise ValueError('All nine original A2 jobs must genuinely close')
        rows={r['name']:r for r in ledger['steps']};steps={}
        for name in names:
            observed,sup,details=closed(source/name,execution)
            if (sup.get('supervisor_sha256')!=sha(A2/'legacy/supervisor275.py')
                    or observed.get('argv')!=rows[name]['argv'] or sup.get('argv')!=rows[name]['argv'][9:]):
                raise ValueError('A2 actual supervisor/argv mismatch')
            steps[name]={'observed_exit':observed['actual_observed_popen_exit'],**details,
                         'supervisor_json_sha256':sha(source/name/'supervisor.json')}
            if name=='offline':
                if not (observed['actual_observed_popen_exit']==124 and sup['timed_out'] is True and sup['deadline_seconds']==1800):
                    raise ValueError('This specific plan requires preserved A2 offline timeout1800')
            elif name=='legacy':
                hard=json.loads((source/name/'actual/hard-timeout-100.json').read_bytes())
                if not (observed['actual_observed_popen_exit']==1 and sup['child_primary_exit']==124
                        and sup['timed_out'] is False and hard['deadline_seconds']==1200):
                    raise ValueError('This retry is for the exact original inner1200 legacy failure')
                steps[name]['original_hard_timeout_sha256']=sha(source/name/'actual/hard-timeout-100.json')
                steps[name]['original_progress_sha256']=sha(source/name/'actual/full125-progress.json')
            elif name=='current30' and observed['actual_observed_popen_exit']!=0:
                failure=json.loads((source/name/'actual/window.json').read_bytes()).get('failure') or {}
                if ('[WinError 1314]' not in failure.get('message','')
                        or 'diagnostic.symlink_to(public_target.name)' not in failure.get('traceback','')):
                    raise ValueError('Additional current30 failure requires review')
                steps[name]['unavailable_not_passed']=True
            elif observed['actual_observed_popen_exit']!=0:
                raise ValueError('Additional A2 failure must be reviewed separately')
        result[archive]={'archive_manifest_sha256':sha(manifest_path),'source_container':str(source),'steps':steps}
    return result

def activated(parent,preparation_sha,activation_sha):
    meta,common,execution,frozen=prepared(parent,preparation_sha)
    if sha(ACTIVATION)!=activation_sha:raise ValueError('Exact root retry activation hash required')
    data=json.loads(ACTIVATION.read_bytes())
    if (data.get('status')!='CURRENT290_LEGACY_RETRY_BOUND_NOT_EXECUTED' or data.get('binding_ready') is not True
            or data.get('tested_worktree_parent_commit')!=parent or data.get('root_freeze_sha256')!=FREEZE_SHA
            or data.get('execution_tools_sha256')!=meta['candidate_bundle_tools_sha256']
            or data.get('preparation_sha256')!=preparation_sha
            or data.get('prior_A2_closed_and_sealed')!=prior_closed_and_sealed(parent,execution)):
        raise ValueError('Retry activation/complete old evidence changed')
    return meta,common,execution,frozen,data

def owned_retry(container,parent,preparation_sha,activation_sha):
    source=container.resolve()
    if (not container.is_absolute() or container.is_symlink() or source.is_relative_to(ROOT)
            or not source.name.startswith('rouge-full290-legacy-retry-')):
        raise ValueError('Real fresh owned retry namespace required')
    own=json.loads((source/'owned-execution.json').read_bytes())
    if (own.get('kind')!='FULL290_SAME_SOURCE75_LEGACY_RETRY_EXECUTION3' or own.get('root')!=str(ROOT)
            or own.get('parent_commit')!=parent or own.get('root_freeze_sha256')!=FREEZE_SHA
            or own.get('preparation_sha256')!=preparation_sha or own.get('activation_sha256')!=activation_sha
            or own.get('controller_sha256')!=sha(BASE/'run_legacy_retry.py')):
        raise ValueError('Actual owned legacy retry identity mismatch')
    return source,own
