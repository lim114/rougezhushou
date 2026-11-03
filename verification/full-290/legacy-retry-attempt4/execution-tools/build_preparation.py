"""Stdlib source-byte/AST preparation only. Never executes a test or Qt window."""
import ast,hashlib,json,re,sys,types
from pathlib import Path
from datetime import datetime,timezone

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
A2=ROOT/'.cache/p3-full290-repair-prep'
TEMPLATE=BASE/'template-legacy'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
    checks=[]
    def check(value,name):
        if not value:raise ValueError(name)
        checks.append(name)
    prior=ROOT/'verification/full-290/source-freeze-repair.json';old=json.loads(prior.read_bytes())
    check(sha(prior)=='75cec266144a389b93aced04d150c4cf6e72a23403f250a9caab9915543e6ec0','Prior A2 freeze exact')
    prior_tools=dict(old['preparation_tools_sha256']);acts={};original_bundle=None
    for label in ('legacy','current'):
        p=A2/label/'activation275.json';data=json.loads(p.read_bytes());acts[label]=sha(p)
        prior_tools[p.relative_to(ROOT).as_posix()]=sha(p)
        for n,v in data['execution_tools_sha256'].items():prior_tools[(A2/label/n).relative_to(ROOT).as_posix()]=v
        if label=='legacy':original_bundle=data['execution_tools_sha256']
    failed=ROOT/'.cache/p3-full290-legacy-retry-prep';failed_meta=json.loads((failed/'preparation.json').read_bytes())
    check(sha(failed/'preparation.json')=='ecb0787cd58d4131e77b1aa5a4f4aa07bbced0d98ca24aec4665ca810b784fa7','Original failed retry3 preparation exact')
    for n,v in failed_meta['new_tools_sha256'].items():prior_tools[(failed/n).relative_to(ROOT).as_posix()]=v
    for n,v in failed_meta['candidate_bundle_tools_sha256'].items():prior_tools[(failed/'legacy'/n).relative_to(ROOT).as_posix()]=v
    for p in (failed/'preparation.json',failed/'READY.json',failed/'legacy/activation-retry290.json'):
        prior_tools[p.relative_to(ROOT).as_posix()]=sha(p)
    for n,v in prior_tools.items():check(sha(ROOT/n)==v,'Prior executed tool unchanged: '+n)
    prior_archives={}
    for n in ('execution-attempt1','p3-supplementary-attempt1','execution-attempt2','p3-supplementary-attempt2','legacy-retry-attempt3-failed'):
        p=ROOT/'verification/full-290'/n/'archive-manifest.json';prior_archives[n]=sha(p)
    template_map={n:sha(TEMPLATE/n) for n in original_bundle}
    check([n for n in original_bundle if template_map[n]!=original_bundle[n]]==['window.py'],'Only immutable template window retimed/platformmetadata; other83 exact')
    original_window=(BASE/'original-A2-window.py').read_bytes();candidate=(TEMPLATE/'window.py').read_bytes()
    old_platform=b"'platform':platform.platform()"
    new_platform=b"'platform':{'source':'sys.platform + sys.getwindowsversion() raw; no WMI metadata query','sys_platform':sys.platform,'windows_version_raw':list(sys.getwindowsversion())}"
    check(original_window.count(b'1200')==6 and original_window.count(old_platform)==1
          and candidate==original_window.replace(b'1200',b'3600').replace(old_platform,new_platform),'Exact6 watchdog changes and1 optional receipt platform expression')
    a=ast.parse(original_window);b=ast.parse(candidate)
    def asserts(t):return [ast.dump(n,include_attributes=False) for n in sorted((x for x in ast.walk(t) if isinstance(x,ast.Assert)),key=lambda n:(n.lineno,n.col_offset))]
    check(len(asserts(a))==862 and asserts(a)==asserts(b),'Original862 assertion AST/order retained')
    ma=next(n for n in a.body if isinstance(n,ast.Try) and sum(isinstance(x,ast.Assert) for x in ast.walk(n))==552)
    mb=next(n for n in b.body if isinstance(n,ast.Try) and sum(isinstance(x,ast.Assert) for x in ast.walk(n))==552)
    main_old=ast.get_source_segment(original_window.decode(),ma).encode();main_new=ast.get_source_segment(candidate.decode(),mb).encode()
    check(main_old==main_new and digest(main_old)=='11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922','Original552 maintry physical bytes retained')
    funcs={}
    for n in ('cases075','preview_cases075','cases080','cases085','pending_cases083085','_replace_binding100','_increment100','_install_narrow_observers100','native090'):
        x=next(z for z in a.body if isinstance(z,ast.FunctionDef) and z.name==n);y=next(z for z in b.body if isinstance(z,ast.FunctionDef) and z.name==n)
        s=ast.get_source_segment(original_window.decode(),x).encode();t=ast.get_source_segment(candidate.decode(),y).encode()
        check(s==t,'Original generator/observer/typedcodec unchanged: '+n);funcs[n]=digest(s)
    original_runner=(BASE/'original-verify-full-available.py').read_bytes();approved_runner=(BASE/'approved-verify-full-available.py').read_bytes()
    expr=b"'platform': platform.system(), 'wine_compatibility': args.wine"
    repl=b"'platform': ('Windows' if sys.platform == 'win32' else platform.system()), 'wine_compatibility': args.wine"
    check(digest(original_runner)==old['source_sha256']['scripts/verify_full_available.py']
        and original_runner.count(expr)==1 and approved_runner==original_runner.replace(expr,repl),'Only exact Windows-only final report platform shortcut')
    old_tree=ast.parse(original_runner);new_tree=ast.parse(approved_runner)
    cls1=next(n for n in old_tree.body if isinstance(n,ast.ClassDef) and n.name=='AvailableResult')
    cls2=next(n for n in new_tree.body if isinstance(n,ast.ClassDef) and n.name=='AvailableResult')
    check(ast.get_source_segment(original_runner.decode(),cls1)==ast.get_source_segment(approved_runner.decode(),cls2),'AvailableResult whole source bytes unchanged')
    old_test=(BASE/'original-test6.py').read_bytes();new_test=(BASE/'approved-test6.py').read_bytes()
    check(digest(old_test)==old['source_sha256']['tests/test_enemy_sp_inheritance_reference.py']
        and digest(new_test)=='0eb99b4d079a945f6254f55a9a2cbadffc8d6d408aa24889dc9f0de8f13eedf4','Exact original/strengthened display test source')
    p=A2/'full290_runtime_common.py';mod={'__name__':'_final_A3_maintained_API_ONLY','__file__':str(p)}
    exec(compile(p.read_bytes(),str(p),'exec'),mod)
    live=mod['runner_api_snapshot']();supp=mod['supplemental_public_inputs']()
    changed=[n for n in old['source_sha256'] if old['source_sha256'][n]!=live['source_sha256'][n]]
    check(set(live['source_sha256'])==set(old['source_sha256']) and set(changed)=={'scripts/verify_full_available.py','tests/test_enemy_sp_inheritance_reference.py'},'Only2 actual maintained-source differences; other1219 identical')
    check((ROOT/'scripts/verify_full_available.py').read_bytes()==approved_runner and (ROOT/'tests/test_enemy_sp_inheritance_reference.py').read_bytes()==new_test,'Live two sources exactly approved candidates')
    check(live['selectors']==old['selectors'] and len(live['selectors'])==430 and supp==old['supplemental_public_inputs_sha256'] and len(supp)==42,'Original full430 order and42 supplemental bytes identical')
    guard=json.loads((TEMPLATE/'current-source-guard.json').read_bytes())
    native=dict(guard['source_sha256'])
    for n in changed:native[n]=live['source_sha256'][n]
    for n,v in {**native,**guard['source_additional_sha256']}.items():check(sha(ROOT/n)==v,'Final native/research input: '+n)
    check(set(native)-set(live['source_sha256'])=={'tests/offline_scope_retirement.py'},'Native extra helper remains explicitly verified')
    check(set(live['source_sha256'])-set(native)=={'CORE_0.70_VERIFICATION.json'},'CORE remains in original additional map')
    necessary={}
    for n in ('process.json','stderr.txt','stdout.txt'):
        p=ROOT/'verification/sections/290-necessary-final-A3'/n;necessary[p.relative_to(ROOT).as_posix()]=sha(p)
    process=json.loads((ROOT/'verification/sections/290-necessary-final-A3/process.json').read_bytes())
    check(process['exit_code']==0 and process['source_unchanged'] is True,'Root actual fresh15-method check exit0/source unchanged; reused not rerun')
    proof={'kind':'FINAL_A3_SOURCE_ADAPTATION_NOT_RUNTIME_PASS','original_window_sha256':digest(original_window),
        'retimed_native_platform_template_sha256':digest(candidate),'all862_assertion_AST_order_unchanged':True,
        'original552_maintry_physical_sha256':digest(main_old),'unchanged_function_source_sha256':funcs,
        'watchdog_replacements':6,'one_optional_WMI_metadata_expression_removed':True,
        'raw_windows_version_is_not_marketing_OS_claim':True,'prior_crash_cause_proven':False,
        'original_full_runner_sha256':digest(original_runner),'approved_full_runner_sha256':digest(approved_runner),
        'AvailableResult_whole_source_unchanged':True,'actual_source_differences':changed,
        'old_test_sha256':digest(old_test),'new_test_sha256':digest(new_test),
        'full_scope_expected':{'selectors':430,'full_sources':1221,'native_sources':1221,'native_additional':86,
            'supplemental':42,'assert_AST':862,'maintry':552,'states':52,'records':4283,'projections':42,
            'exact_admissions':10,'empty_traces':26,'damage_requests':52,'text_requests':156},
        'actual_full_or_GUI_started_by_preparation':False}
    put(BASE/'source-adaptation-proof.json',proof)
    names=('final_common.py','declare_freeze.py','activate.py','offline_child.py','run_segment.py','run_readback.py',
        'archive_segment.py','supervisor3690.py','build_preparation.py','SCHEMA.md','RUN_PLAN.md',
        'original-A2-window.py','original-test6.py','approved-test6.py','original-verify-full-available.py',
        'approved-verify-full-available.py','window-template-adaptation.diff','source-adaptation-proof.json')
    for n in names:
        if n.endswith('.py'):compile((BASE/n).read_bytes(),str(BASE/n),'exec');check(True,'Compile only: '+n)
    for n in template_map:
        if n.endswith('.py'):compile((TEMPLATE/n).read_bytes(),str(TEMPLATE/n),'exec')
    check(not (BASE/'bound-legacy').exists() and not (BASE/'activation-final-A3.json').exists(),'No binding/GUI performed')
    check(not (ROOT/'verification/full-290/source-freeze-final-A3.json').exists(),'No final sourcefreeze declared by preparer')
    meta={'kind':'FINAL_A3_INACTIVE_INPUT_AND_RUNTIME_PREPARATION','checked_at':datetime.now(timezone.utc).isoformat(),
        'parent_commit':old['parent_commit'],'prior_freeze_sha256':sha(prior),
        'new_tools_sha256':{n:sha(BASE/n) for n in names},'template_bundle_sha256':template_map,
        'prior_public_tool_sha256':prior_tools,'A2_activation_sha256':acts,
        'prior_archive_manifest_sha256':prior_archives,'necessary_module_public_sha256':necessary,
        'original_legacy_native_source_sha256':guard['source_sha256'],
        'original_legacy_additional_sha256':guard['source_additional_sha256'],
        'actual_source_difference_paths':changed,'future_success_is_not_input_declaration_prerequisite':True,
        'actual_new_GUI_full_test_freeze_or_activation_executed':False}
    put(BASE/'preparation.json',meta)
    # Read-only gate/provenance checks only. These do NOT run any project test.
    p=BASE/'final_common.py';module=types.ModuleType('_final_A3_static_gate_readback');module.__file__=str(p)
    exec(compile(p.read_bytes(),str(p),'exec'),module.__dict__)
    m,c,e,o=module.prepared(old['parent_commit'],sha(BASE/'preparation.json'))
    check(module.source_state(m,c,o)[0]==live,'Exact final source-state gate actual readback')
    check(module.module_reference(old['parent_commit'],m)['actual_tests_run']==15,'Root actual module proof actual readback; no rerun')
    check(len(module.prior_archives(m))==5,'All5 immutable prior archives actual hash readback')
    put(BASE/'static-preparation-evidence.json',{'kind':'STDLIB_HASH_AST_AND_READONLY_GATES_NOT_TEST_SUITE',
        'checks':checks,'check_count':len(checks),'actual_new_GUI_or_full_or_test_run':False,
        'preparation_sha256':sha(BASE/'preparation.json')})
    ready={'status':'READY_FOR_ROOT_REVIEW_NOT_ACTIVATED_NOT_EXECUTED','preparation_sha256':sha(BASE/'preparation.json'),
        'static_evidence_sha256':sha(BASE/'static-preparation-evidence.json'),'static_check_count':len(checks),
        'tool_pins':len(names),'immutable_template_pins':84,'actual_source_differences':changed,
        'actual_root_final15_reused':True,'future_offline_legacy_or_typed_pass_claimed':False}
    put(BASE/'READY.json',ready)
    print(json.dumps({**ready,'READY_sha256':sha(BASE/'READY.json')},ensure_ascii=False))

if __name__=='__main__':main()
