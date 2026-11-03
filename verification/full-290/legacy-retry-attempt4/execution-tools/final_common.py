"""One FINAL A3 input declaration; execution success is a separate fact."""
import ast,hashlib,json,sys,types
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
A2=ROOT/'.cache/p3-full290-repair-prep'
TEMPLATE=BASE/'template-legacy'
BOUND=BASE/'bound-legacy'
PYTHON=ROOT/'.venv/Scripts/python.exe'
PRIOR=ROOT/'verification/full-290/source-freeze-repair.json'
FREEZE=ROOT/'verification/full-290/source-freeze-final-A3.json'
ACTIVATION=BASE/'activation-final-A3.json'
PRIOR_SHA='75cec266144a389b93aced04d150c4cf6e72a23403f250a9caab9915543e6ec0'
TARGET='tests/test_enemy_sp_inheritance_reference.py'
RUNNER='scripts/verify_full_available.py'
AFTER_SHA='0eb99b4d079a945f6254f55a9a2cbadffc8d6d408aa24889dc9f0de8f13eedf4'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def hashbytes(raw):return hashlib.sha256(raw).hexdigest()
def write_new(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def regular(path,boundary):
    if (not path.is_file() or path.is_symlink() or boundary.is_symlink()
            or not path.resolve().is_relative_to(boundary.resolve())):raise ValueError('Regular public file required: '+str(path))
    for p in path.parents:
        if p==boundary:break
        if p.is_symlink():raise ValueError('Linked public parent refused')
    return path

def prepared(parent,preparation_sha):
    if sys.platform!='win32' or Path(sys.executable).resolve()!=PYTHON.resolve():raise ValueError('Exact native project Python required')
    if sha(BASE/'preparation.json')!=preparation_sha or sha(PRIOR)!=PRIOR_SHA:raise ValueError('Reviewed preparation/prior freeze required')
    meta=json.loads((BASE/'preparation.json').read_bytes())
    for n,v in meta['new_tools_sha256'].items():
        if sha(regular(BASE/n,BASE))!=v:raise ValueError('Final A3 tool drift: '+n)
    for n,v in meta['template_bundle_sha256'].items():
        if sha(regular(TEMPLATE/n,TEMPLATE))!=v:raise ValueError('Immutable full template drift')
    for n,v in meta['prior_public_tool_sha256'].items():
        if sha(regular(ROOT/n,ROOT))!=v:raise ValueError('Prior executed public tool drift: '+n)
    p=A2/'full290_runtime_common.py';common=types.ModuleType('full290_runtime_common');common.__file__=str(p)
    sys.modules['full290_runtime_common']=common
    exec(compile(p.read_bytes(),str(p),'exec'),common.__dict__)
    old=common.validate_freeze(parent,check_live=False)
    bundles=common.bound_bundles(parent)
    if {n:v['activation_sha256'] for n,v in bundles.items()}!=meta['A2_activation_sha256']:raise ValueError('Original A2 activation changed')
    p=A2/'run_full290_orchestration.py';execution=types.ModuleType('_final_A3_original_execution');execution.__file__=str(p)
    exec(compile(p.read_bytes(),str(p),'exec'),execution.__dict__)
    return meta,common,execution,old

def source_state(meta,common,old,require_repaired=True):
    live=common.runner_api_snapshot();supplemental=common.supplemental_public_inputs()
    if (set(live['source_sha256'])!=set(old['source_sha256']) or live['selectors']!=old['selectors']
            or supplemental!=old['supplemental_public_inputs_sha256']
            or live['cloud_selector_api_sha256']!=old['cloud_selector_api_sha256']):raise ValueError('Complete source/selector/support scope changed')
    changed=[n for n in old['source_sha256'] if old['source_sha256'][n]!=live['source_sha256'][n]]
    if (require_repaired and set(changed)!={TARGET,RUNNER}) or not set(changed)<={TARGET,RUNNER}:raise ValueError('Only the exact display-test and offline report metadata changes are allowed')
    original=(BASE/'original-test6.py').read_bytes();approved=(BASE/'approved-test6.py').read_bytes()
    if hashbytes(original)!=old['source_sha256'][TARGET] or hashbytes(approved)!=AFTER_SHA:raise ValueError('Original/approved test source drift')
    expected=original.replace("self.assertIn('独立构造',text)".encode(),("self.assertIn('本关使用专属敌人资料',text)\n        self.assertIn('独立构造',enemy_text(entry,technical=True))").encode())
    if approved!=expected or (ROOT/TARGET).read_bytes()!=(approved if TARGET in changed else original):raise ValueError('Exact test bytes/strengthened technical assertion required')
    old_runner=(BASE/'original-verify-full-available.py').read_bytes();new_runner=(BASE/'approved-verify-full-available.py').read_bytes()
    old_line=b"'platform': platform.system(), 'wine_compatibility': args.wine"
    new_line=b"'platform': ('Windows' if sys.platform == 'win32' else platform.system()), 'wine_compatibility': args.wine"
    if (hashbytes(old_runner)!=old['source_sha256'][RUNNER] or old_runner.count(old_line)!=1
            or new_runner!=old_runner.replace(old_line,new_line)
            or (ROOT/RUNNER).read_bytes()!=(new_runner if RUNNER in changed else old_runner)
            or live['maintained_runner_sha256']!=hashbytes(new_runner if RUNNER in changed else old_runner)):
        raise ValueError('Only the exact Windows-only final report metadata shortcut is allowed')
    native=dict(meta['original_legacy_native_source_sha256'])
    for name in (TARGET,RUNNER):native[name]=live['source_sha256'][name]
    for n,v in {**native,**meta['original_legacy_additional_sha256']}.items():
        if sha(regular(ROOT/n,ROOT))!=v:raise ValueError('Native extra helper/research/runtime input changed: '+n)
    delta={'approved_changed_sources':{TARGET:{'old_sha256':hashbytes(original),'new_sha256':hashbytes(approved)},
                                     RUNNER:{'old_sha256':hashbytes(old_runner),'new_sha256':hashbytes(new_runner)}},
        'actual_repair_present':set(changed)=={TARGET,RUNNER},'other_full_source_paths_unchanged':1219,
        'supplemental_public_paths_unchanged':42,'original_numbers_and_qualification_assertions_unchanged':True,
        'technical_label_assertion_added':1,'native_extra_helper_preserved':'tests/offline_scope_retirement.py',
        'offline_result_platform_still_Windows_on_Windows':True,
        'AvailableResult_selectors_tests_and_qualification_logic_unchanged':True,
        'A2_GUI_reuse_is_cross_freeze_two_exact_nonproduction_input_equivalence':True}
    return live,supplemental,native,delta

def prior_archives(meta):
    result={}
    for name,expected in meta['prior_archive_manifest_sha256'].items():
        folder=ROOT/'verification/full-290'/name;p=regular(folder/'archive-manifest.json',folder)
        if sha(p)!=expected:raise ValueError('Prior original failure/window archive changed')
        data=json.loads(p.read_bytes())
        for n,v in data['files'].items():
            path=regular(folder/n,folder)
            if sha(path)!=v['sha256'] or path.stat().st_size!=v['bytes']:raise ValueError('Prior sealed original drift: '+name+'/'+n)
        result[name]={'manifest_sha256':expected,'files':len(data['files'])}
    return result

def closed(folder,execution):
    observed=json.loads((folder/'controller-process.json').read_bytes());sup=json.loads((folder/'supervisor.json').read_bytes())
    terminal,details=execution.terminal_job_record(folder,observed)
    origin=json.loads((folder/'process-exit-origin.json').read_bytes())
    if (not terminal or origin.get('derived_from_supervisor_json') is not False
            or origin.get('process_exit_sha256')!=sha(folder/'process.exit')
            or int((folder/'process.exit').read_text(encoding='ascii'))!=observed['actual_observed_popen_exit']):raise ValueError('Actual Popen/job/exit closure required')
    return observed,sup,details

def module_reference(parent,meta):
    """Reuse root's ACTUAL15-method receipt; do not rerun or invent a Qt/Popen proof."""
    import re
    for name,expected in meta['necessary_module_public_sha256'].items():
        if sha(regular(ROOT/name,ROOT))!=expected:raise ValueError('Root necessary-module original changed')
    folder=ROOT/'verification/sections/290-necessary-final-A3'
    path=folder/'process.json';raw=json.loads(path.read_bytes());stderr=(folder/'stderr.txt').read_text(encoding='utf8')
    expected_argv=[str(PYTHON),'-B','-X','utf8','-m','unittest','-v','tests.test_enemy_sp_inheritance_reference']
    if (raw.get('kind')!='necessary_change_related_tests_not_full_suite' or raw.get('exit_code')!=0
            or raw.get('modules')!=['tests.test_enemy_sp_inheritance_reference'] or raw.get('argv')!=expected_argv
            or raw.get('source_commit_before')!=parent or raw.get('source_unchanged') is not True
            or raw.get('source_sha256_before')!=raw.get('source_sha256_after')
            or not re.search(r'Ran 15 tests in [0-9.]+s\s+OK\s*$',stderr)
            or len(re.findall(r' \.\.\. ok$',stderr,re.MULTILINE))!=15):
        raise ValueError('Actual complete original15-method necessary pass required')
    for name,expected in raw['source_sha256_after'].items():
        if sha(regular(ROOT/name,ROOT))!=expected:raise ValueError('Necessary module declared source coverage changed')
    return {'public_receipt_relative':'verification/sections/290-necessary-final-A3/process.json',
        'receipt_sha256':sha(path),'actual_process_exit':0,'actual_tests_run':15,
        'stdout_sha256':sha(folder/'stdout.txt'),'stderr_sha256':sha(folder/'stderr.txt'),
        'receipt_declared_source_coverage_count':len(raw['source_sha256_after']),
        'receipt_declared_sources_unchanged':True,'full1221_scope_not_claimed_by_this_necessary_run':True,
        'Qt_window_or_game_chat_integration_claimed':False,'rerun_by_final_A3_preparation':False}

def frozen(parent,preparation_sha,freeze_sha):
    meta,common,execution,old=prepared(parent,preparation_sha)
    if sha(FREEZE)!=freeze_sha:raise ValueError('Exact final A3 full freeze required')
    data=json.loads(FREEZE.read_bytes());live,supp,native,delta=source_state(meta,common,old)
    if (data.get('root_declared') is not True or data.get('actual_validation_attempt')!=3 or data.get('section')!=290
            or data.get('parent_commit')!=parent or data.get('preparation_sha256')!=preparation_sha
            or data.get('source_sha256')!=live['source_sha256'] or data.get('selectors')!=live['selectors']
            or data.get('supplemental_public_inputs_sha256')!=supp or data.get('legacy_native_source_sha256')!=native
            or data.get('legacy_source_additional_sha256')!=meta['original_legacy_additional_sha256']
            or data.get('source_transition')!=delta or data.get('prior_archives')!=prior_archives(meta)
            or data.get('necessary_module_check')!=module_reference(parent,meta)):
        raise ValueError('Final full/native source, original history, or actual module proof changed')
    return meta,common,execution,data

def binding_recipe(data,freeze_sha,parent):
    guard=json.loads((TEMPLATE/'current-source-guard.json').read_bytes())
    old_guard_sha=hashbytes((TEMPLATE/'current-source-guard.json').read_bytes())
    guard.update(source_sha256=data['legacy_native_source_sha256'],source_additional_sha256=data['legacy_source_additional_sha256'],
        root_freeze_sha256=freeze_sha,tested_worktree_parent_commit=parent,actual_section=290,
        final_A3_actual_legacy_execution_ordinal=4,prior_guard_sha256_preserved=old_guard_sha,
        actual_final_A3_binding_not_historical_label=True)
    raw=(json.dumps(guard,ensure_ascii=False,indent=2)+'\n').encode('utf8');new_guard_sha=hashbytes(raw)
    old_window=(TEMPLATE/'window.py').read_bytes()
    literal=("_SOURCE125_GUARD_SHA256 = '"+old_guard_sha+"'").encode()
    if old_window.count(literal)!=1:raise ValueError('Unique native source guard pin required')
    window=old_window.replace(literal,("_SOURCE125_GUARD_SHA256 = '"+new_guard_sha+"'").encode())
    launcher=(TEMPLATE/'launcher125.py').read_bytes()
    import re
    launcher=re.sub(rb"(?m)^WINDOW_SHA256 = '[0-9a-f]{64}'$",("WINDOW_SHA256 = '"+hashbytes(window)+"'").encode(),launcher)
    launcher=re.sub(rb"(?m)^SOURCE125_GUARD_SHA256 = '[0-9a-f]{64}'$",("SOURCE125_GUARD_SHA256 = '"+new_guard_sha+"'").encode(),launcher)
    outer=(TEMPLATE/'launcher275.py').read_bytes().replace(b"HERE/'activation275.json'",b"HERE/'activation-final-A3.json'").replace(b"'CURRENT290_SOURCE_BOUND_NOT_EXECUTED'",b"'CURRENT290_FINAL_A3_BOUND_NOT_EXECUTED'")
    return {'current-source-guard.json':raw,'window.py':window,'launcher125.py':launcher,'launcher275.py':outer}

def bound(parent,preparation_sha,freeze_sha,activation_sha):
    meta,common,execution,data=frozen(parent,preparation_sha,freeze_sha)
    if sha(ACTIVATION)!=activation_sha:raise ValueError('Exact root final A3 activation required')
    act=json.loads(ACTIVATION.read_bytes());recipe=binding_recipe(data,freeze_sha,parent)
    expected={n:hashbytes(recipe[n]) if n in recipe else v for n,v in meta['template_bundle_sha256'].items()}
    if (act.get('status')!='CURRENT290_FINAL_A3_BOUND_NOT_EXECUTED' or act.get('binding_ready') is not True
            or act.get('root_freeze_sha256')!=freeze_sha or act.get('preparation_sha256')!=preparation_sha
            or act.get('tested_worktree_parent_commit')!=parent or act.get('execution_tools_sha256')!=expected):raise ValueError('Final A3 complete binding changed')
    if sha(BOUND/'activation-final-A3.json')!=activation_sha:raise ValueError('Child activation bytes differ')
    for n,v in expected.items():
        if sha(regular(BOUND/n,BOUND))!=v:raise ValueError('Actual bound fixture drift: '+n)
    return meta,common,execution,data,act

def owned_segment(container,mode,parent,preparation_sha,freeze_sha,activation_sha):
    source=container.resolve();prefix='rouge-full290-final-A3-'+mode+'-'
    if (not container.is_absolute() or container.is_symlink() or source.is_relative_to(ROOT)
            or not source.name.startswith(prefix)):raise ValueError('Exact owned final A3 segment required')
    own=json.loads((source/'owned-execution.json').read_bytes())
    if (own.get('kind')!='FULL290_FINAL_A3_SEGMENT_EXECUTION' or own.get('mode')!=mode
            or own.get('root')!=str(ROOT) or own.get('parent_commit')!=parent
            or own.get('root_freeze_sha256')!=freeze_sha or own.get('preparation_sha256')!=preparation_sha
            or own.get('activation_sha256')!=activation_sha or own.get('controller_sha256')!=sha(BASE/'run_segment.py')):raise ValueError('Actual segment provenance mismatch')
    return source,own
