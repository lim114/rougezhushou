"""Five authorised display-contract migrations, offscreen public state only."""
import ast
from contextlib import ExitStack
from datetime import datetime,timezone
import hashlib,json,os
from pathlib import Path
import sys,tempfile,traceback,unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'rouge/app.py').is_file())
ORIGINAL=ROOT/'.cache/p3-full290-diagnostic/public-source'
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
os.environ['QT_QPA_PLATFORM']='offscreen'
MODULES=('tests.test_player_node_information_286','tests.test_enemy_prefab_skill_gates',
 'tests.test_enemy_skill_resources','tests.test_enemy_configuration_view','tests.test_original_entry_planning')
METHODS={
 'tests/test_player_node_information_286.py':'PlayerNodeInformationTests.test_every_fixed_event_preserves_each_scene_option_and_conditional_in_source_order',
 'tests/test_enemy_prefab_skill_gates.py':'EnemyPrefabSkillGateViewTests.test_fixed_preview_shows_finite_limit_without_english_ids_or_actual_count',
 'tests/test_enemy_skill_resources.py':'EnemySkillResourceViewTests.test_fixed_preview_displays_chinese_gate_and_never_claims_actual_cast',
 'tests/test_enemy_configuration_view.py':'EnemyConfigurationViewTests.test_fixed_preview_unknown_grade_keeps_source_but_no_prediction',
 'tests/test_original_entry_planning.py':'OriginalEntryViewTests.test_original_portal_preview_requires_exact_declared_scene_id',
}
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def copy(path,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(path.read_bytes())
def methods(tree):
    return {node.name+'.'+child.name:child for node in tree.body if isinstance(node,ast.ClassDef)
            for child in node.body if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef))}
def asserts(node):
    return sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)
               and n.func.attr.startswith('assert') for n in ast.walk(node))
def flatten(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from flatten(item)
        else:yield item

def main():
    if (HERE/'first-run.json').exists():raise FileExistsError('Preserve the first migration run')
    frozen_raw=(ROOT/'verification/full-290/source-freeze.json').read_bytes()
    frozen=json.loads(frozen_raw);expected={**frozen['source_sha256'],**frozen['supplemental_public_inputs_sha256']}
    before={name:sha(ROOT/name) for name in expected}
    changed=[name for name in expected if before[name]!=expected[name]]
    if set(changed)!=set(METHODS)|{'scripts/verify_full_available.py'} or before['scripts/verify_full_available.py']!='857339d08274515133d0a26c46c5e3c74d9dff494449f1e3c6358fc1d8b8729d':raise ValueError('Only the five authorised tests may differ from A1 freeze: '+str(changed))
    delta={}
    for name,method in METHODS.items():
        prior,current=ORIGINAL/name,ROOT/name
        if sha(prior)!=expected[name]:raise ValueError('Preserved original differs from A1 freeze')
        old_tree,new_tree=ast.parse(prior.read_bytes()),ast.parse(current.read_bytes())
        old,new=methods(old_tree),methods(new_tree)
        if old.keys()!=new.keys():raise ValueError('No test method may be removed, added or renamed')
        changed_methods=[key for key in old if ast.dump(old[key],include_attributes=False)!=ast.dump(new[key],include_attributes=False)]
        if changed_methods!=[method]:raise ValueError('Unexpected method mutation: '+name+str(changed_methods))
        if asserts(new[method])<asserts(old[method]):raise ValueError('Assertion-call count must not shrink')
        copy(prior,HERE/'before'/name);copy(current,HERE/'after'/name)
        delta[name]={'before_sha256':sha(prior),'after_sha256':sha(current),'changed_method':method,
            'method_names_unchanged':True,'other_methods_AST_identical':True,
            'before_assertion_calls':asserts(old[method]),'after_assertion_calls':asserts(new[method]),
            'before_method_AST':ast.dump(old[method],include_attributes=False),
            'after_method_AST':ast.dump(new[method],include_attributes=False)}
    save(HERE/'AST-delta.json',{'kind':'AUTHORISED_FIVE_DISPLAY_TEST_CONTRACT_MIGRATIONS',
        'original_A1_freeze_sha256':hashlib.sha256(frozen_raw).hexdigest(),'files':delta,
        'production_source_changed':False,'original_failures_retained':'../p3-full290-diagnostic',
        'numeric_or_eligibility_assertions_weakened':False})
    copy(ROOT/'scripts/verify_full_available.py',HERE/'root-maintained-runner.py')
    save(HERE/'source-before.json',before)
    safety=[]
    protected=(ROOT/'.local',ROOT/'local-settings.json')
    def audit(event,args):
        if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0])).resolve()
            if any(path==item or path.is_relative_to(item) for item in protected):
                safety.append({'event':'original_private_open_blocked','name':path.name})
                raise RuntimeError('Migration verification refuses private runtime data')
        if event in ('subprocess.Popen','socket.connect'):
            safety.append({'event':event+'_blocked'})
            raise RuntimeError('Migration verification refuses process/network access')
    sys.addaudithook(audit)
    def forbidden(*_args,**_kwargs):
        safety.append({'event':'game_or_chat_entry_blocked'})
        raise RuntimeError('Migration verification forbids game enumeration/capture and desktop chat')
    result=None;error=None;cleanup=None;ids=[]
    try:
        from rouge import app as application,capture,desktop_backend
        from PySide6.QtWidgets import QApplication
        from verify_full_available import AvailableResult
        with tempfile.TemporaryDirectory(prefix='rouge-290-display-migration-') as directory,ExitStack() as stack:
            temporary=Path(directory)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json',
                'OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():
                stack.enter_context(patch.object(application,name,value))
            for module,name in ((application,'list_game_windows'),(capture,'list_game_windows'),
                (capture.GameCapture,'connect'),(capture.GameCapture,'capture'),(capture.GameCapture,'next_frame'),
                (desktop_backend.DesktopBackend,'start'),(desktop_backend.DesktopBackend,'request')):
                stack.enter_context(patch.object(module,name,side_effect=forbidden))
            suite=unittest.defaultTestLoader.loadTestsFromNames(MODULES)
            ids=[test.id() for test in flatten(suite)]
            with (HERE/'first-unittest.log').open('x',encoding='utf8') as stream:
                result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=AvailableResult).run(suite)
            if QApplication.instance() and QApplication.instance().platformName()!='offscreen':
                raise RuntimeError('Native QApplication is forbidden in this module-only run')
            from qt_verification_cleanup import shutdown_verification_qt
            cleanup=shutdown_verification_qt()
    except BaseException as exc:error={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
    after={name:sha(ROOT/name) for name in expected}
    unchanged=before==after
    record={'kind':'FIRST_REAL_FIVE_MODULE_OFFSCREEN_DISPLAY_MIGRATION_RUN',
        'time':datetime.now(timezone.utc).isoformat(),'modules':list(MODULES),'ordered_test_ids':ids,
        'actual_argv':sys.argv,'qpa_environment':os.environ['QT_QPA_PLATFORM'],
        'source_sha256':sha(Path(__file__)),'AST_delta_sha256':sha(HERE/'AST-delta.json'),
        'actual_tests_run':None if result is None else result.testsRun,
        'actual_passed_count':None if result is None else result.passed_count,
        'actual_failures':[] if result is None else [{'test':test.id(),'traceback':trace} for test,trace in result.failures],
        'actual_errors':[] if result is None else [{'test':test.id(),'traceback':trace} for test,trace in result.errors],
        'actual_unavailable':[] if result is None else result.unavailable,
        'actual_skips':[] if result is None else [{'test':test.id(),'reason':why} for test,why in result.skipped],
        'source_unchanged_during_run':unchanged,
        'A1_source_changes_are_five_authorised_test_files_plus_exact_root_verbosity_runner':set(changed)==set(METHODS)|{'scripts/verify_full_available.py'},
        'original_A1_freeze_unchanged':(ROOT/'verification/full-290/source-freeze.json').read_bytes()==frozen_raw,
        'safety_events':safety,'exception':error,'qt_cleanup':cleanup,
        'private_state_read':False,'game_captures':0,'chat_requests':0,
        'actual_successful':bool(result and result.wasSuccessful() and unchanged and not safety and error is None),
        'native_or_full_validation_pass_claimed':False}
    save(HERE/'first-run.json',record)
    print(json.dumps({key:value for key,value in record.items() if key not in ('ordered_test_ids','actual_failures','actual_errors','actual_unavailable')},ensure_ascii=False),flush=True)
    return 0 if record['actual_successful'] else 1

if __name__=='__main__':raise SystemExit(main())
