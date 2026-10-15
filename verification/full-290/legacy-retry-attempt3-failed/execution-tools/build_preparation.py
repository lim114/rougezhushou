"""Cache-only stdlib byte/AST metadata. Does not import production or execute GUI."""
import ast,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
A2=ROOT/'.cache/p3-full290-repair-prep'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
    checks=[]
    def check(value,label):
        if not value:raise ValueError(label)
        checks.append(label)
    freeze=ROOT/'verification/full-290/source-freeze-repair.json'
    frozen=json.loads(freeze.read_bytes());original=A2/'legacy';bundle=BASE/'legacy'
    check(sha(freeze)=='75cec266144a389b93aced04d150c4cf6e72a23403f250a9caab9915543e6ec0','Original A2 freeze exact')
    controls=frozen['preparation_tools_sha256']
    for n,v in controls.items():check(sha(ROOT/n)==v,'Original A2 controller: '+n)
    activations={};counts={}
    for label in ('legacy','current'):
        path=A2/label/'activation275.json';j=json.loads(path.read_bytes());activations[label]=sha(path)
        counts[label]=len(j['execution_tools_sha256'])
        for n,v in j['execution_tools_sha256'].items():check(sha(A2/label/n)==v,'Original A2 '+label+' tool: '+n)
    check(counts=={'legacy':84,'current':18},'Actual complete A2 tool-map84/18')
    original_map=json.loads((original/'activation275.json').read_bytes())['execution_tools_sha256']
    candidate_map={n:sha(bundle/n) for n in original_map}
    changed=[n for n in original_map if original_map[n]!=candidate_map[n]]
    check(changed==['launcher125.py','launcher275.py','window.py'],'Only3 explicitly adapted bundle files')
    old=(original/'window.py').read_bytes();new=(bundle/'window.py').read_bytes()
    check(old.count(b'1200')==6 and new==old.replace(b'1200',b'3600'),'Exact6 watchdog deadline/label replacements only')
    before=ast.parse(old);after=ast.parse(new)
    def assertions(t):return [ast.dump(n,include_attributes=False) for n in sorted((x for x in ast.walk(t) if isinstance(x,ast.Assert)),key=lambda x:(x.lineno,x.col_offset))]
    check(len(assertions(before))==862 and assertions(before)==assertions(after),'862 ordered assert AST unchanged')
    source_before=old.decode();source_after=new.decode()
    def maintry(t):return next(n for n in t.body if isinstance(n,ast.Try) and sum(isinstance(x,ast.Assert) for x in ast.walk(n))==552)
    main_old=ast.get_source_segment(source_before,maintry(before)).encode();main_new=ast.get_source_segment(source_after,maintry(after)).encode()
    check(main_old==main_new and hashlib.sha256(main_old).hexdigest()=='11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922','Original552 maintry exact physical bytes')
    for name in ('cases075','preview_cases075','cases080','cases085','pending_cases083085','_replace_binding100','_increment100','_install_narrow_observers100','native090'):
        a=next(n for n in before.body if isinstance(n,ast.FunctionDef) and n.name==name)
        b=next(n for n in after.body if isinstance(n,ast.FunctionDef) and n.name==name)
        check(ast.get_source_segment(source_before,a)==ast.get_source_segment(source_after,b),'Original generator/observer/codec source unchanged: '+name)
    old_launcher=(original/'launcher125.py').read_bytes()
    expected=old_launcher.replace(("WINDOW_SHA256 = '"+hashlib.sha256(old).hexdigest()+"'").encode(),("WINDOW_SHA256 = '"+hashlib.sha256(new).hexdigest()+"'").encode())
    check((bundle/'launcher125.py').read_bytes()==expected,'launcher125 changes only exact window hash pin')
    old_launcher=(original/'launcher275.py').read_bytes()
    expected=old_launcher.replace(b"HERE/'activation275.json'",b"HERE/'activation-retry290.json'").replace(b"'CURRENT290_SOURCE_BOUND_NOT_EXECUTED'",b"'CURRENT290_LEGACY_RETRY_BOUND_NOT_EXECUTED'")
    check((bundle/'launcher275.py').read_bytes()==expected,'outer child changes only independent activation filename/status')
    sup=(original/'supervisor275.py').read_bytes()
    expected=sup.replace(b'0<args.timeout<=1800',b'0<args.timeout<=3690').replace(b'<=1800-second timeout',b'<=3690-second timeout')
    check((BASE/'supervisor3690.py').read_bytes()==expected,'Supervisor only cap/error3690; actual Popen/job body unchanged')
    for n,v in frozen['source_sha256'].items():check(sha(ROOT/n)==v,'Full maintained source still frozen: '+n)
    for n,v in frozen['supplemental_public_inputs_sha256'].items():check(sha(ROOT/n)==v,'Full supplemental input still frozen: '+n)
    guard=json.loads((bundle/'current-source-guard.json').read_bytes())
    for n,v in {**guard['source_sha256'],**guard['source_additional_sha256']}.items():check(sha(ROOT/n)==v,'Original native source/additional input: '+n)
    check(set(guard['source_sha256'])-set(frozen['source_sha256'])=={'tests/offline_scope_retirement.py'},'Native extra helper explicitly retained')
    helpers=('retry_common.py','activate_legacy_retry.py','run_legacy_retry.py','run_readback.py','archive_legacy_retry.py','supervisor3690.py','build_preparation.py')
    for name in helpers:
        compile((BASE/name).read_bytes(),str(BASE/name),'exec');check(True,'Compile only, no module executed: '+name)
    for name in original_map:
        if name.endswith('.py'):compile((bundle/name).read_bytes(),str(bundle/name),'exec')
    check(not (bundle/'activation-retry290.json').exists(),'No retry activation or GUI execution started')
    check(not (BASE/'execution-once.json').exists(),'No one-shot retry invocation recorded')
    names=list(helpers)+['RUN_PLAN.md','initial-source-adaptation-proof.json','deadline-coordination-proof.json']
    for folder in ('A2-originals','A2-failure-originals'):
        names.extend(p.relative_to(BASE).as_posix() for p in sorted((BASE/folder).rglob('*')) if p.is_file())
    meta={'kind':'INACTIVE_ROOT_REVIEWED_LEGACY_RETRY_PREPARATION','checked_at':datetime.now(timezone.utc).isoformat(),
        'source_freeze_sha256':sha(freeze),'parent_commit':frozen['parent_commit'],
        'new_tools_sha256':{n:sha(BASE/n) for n in names},'candidate_bundle_tools_sha256':candidate_map,
        'original_A2_bundle_tools_sha256':original_map,'A2_activation_sha256':activations,
        'A2_native_source_sha256':guard['source_sha256'],'A2_additional_runtime_inputs_sha256':guard['source_additional_sha256'],
        'changed_bundle_files':changed,'full_scope':{'source_paths':1221,'selectors':430,'supplemental':42,
            'native_source_paths':1221,'native_additional':86,'ordered_assert_AST':862,'maintry_asserts':552,
            'saved_states':52,'checks':4283,'projections':42,'exact_admissions':10,'empty_traces':26},
        'timeouts_seconds':{'fixture_internal':3600,'owned_supervisor':3690,'controller_outer':3780},
        'actual_GUI_test_activation_freeze_or_pass_claimed':False}
    put(BASE/'preparation.json',meta)
    put(BASE/'static-preparation-evidence.json',{'kind':'STDLIB_FILE_HASH_AND_AST_PREPARATION_ONLY',
        'checks':checks,'check_count':len(checks),'production_or_test_module_imports':0,
        'preparation_sha256':sha(BASE/'preparation.json'),'actual_GUI_or_full_run':False})
    ready={'status':'READY_FOR_ROOT_REVIEW_NOT_ACTIVATED_NOT_EXECUTED','preparation_sha256':sha(BASE/'preparation.json'),
        'static_evidence_sha256':sha(BASE/'static-preparation-evidence.json'),'static_file_AST_check_count':len(checks),
        'candidate_window_sha256':candidate_map['window.py'],'new_tool_pins':len(names),
        'bundle_tool_pins':len(candidate_map),'actual_pass_or_GUI_execution_claimed':False,
        'root_explicit_declare_then_execute_required':True}
    put(BASE/'READY.json',ready)
    print(json.dumps({**ready,'READY_sha256':sha(BASE/'READY.json')},ensure_ascii=False))

if __name__=='__main__':main()
