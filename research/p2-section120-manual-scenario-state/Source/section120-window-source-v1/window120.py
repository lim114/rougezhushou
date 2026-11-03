"""Source only; Root executes original observation/candidate editor isolation workflows."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import traceback

from native_evidence import freeze, assert_native_equal, write_record, source_map

A = 'mechanist'
B = 'char_002_amiya'
DEEP = 'char_110_deepcl'
TOKEN = 'token_10001_deepcl_tentac'
CARGO = 'rogue_6_relic_cargo_2'
OPERATORS = ((A,1,2,7),(B,1,2,7),(DEEP,1,1,7))
A_TIMING = '{ "windup_frames" : 0, "recovery_frames" : 0, "target_windows" : [] }\n'
A_RELIC = '{ "parts_count" : 0, "unused" : "A 原文" }\n'
B_TIMING = '{"windup_frames":0,"recovery_frames":0,"target_windows":[[0,5]]} '
B_RELIC = '{"parts_count":3,"unused":"B 原文"} '
POISON_TIMING = '{"windup_frames":0,"recovery_frames":0,"target_windows":[[0,2]]}'
POISON_RELIC = '{"parts_count":1,"unused":"unsupported edit"}'
DAMAGE_TYPES = ('physical','magic','true','elemental','weakness','damage_reference')
PUBLIC_API_CASES = [{'id': 'mechanist_empty_target', 'input': {'skill_rank': 10, 'elite': 2, 'level': 1, 'potential': 1, 'trust': 0, 'module_id': None, 'module_level': 0, 'relic_ids': [], 'enemy_defense': 0, 'enemy_resistance': 0, 'timing_mode': 'frames', 'window_seconds': 5, 'operator': 'mechanist', 'skill': 3, 'timing': {'target_windows': []}}}, {'id': 'amiya_empty_target', 'input': {'skill_rank': 7, 'elite': 1, 'level': 1, 'potential': 1, 'trust': 0, 'module_id': None, 'module_level': 0, 'relic_ids': [], 'enemy_defense': 0, 'enemy_resistance': 0, 'timing_mode': 'frames', 'window_seconds': 5, 'operator': 'char_002_amiya', 'skill': 1, 'timing': {'target_windows': []}}}, {'id': 'amiya_nonempty', 'input': {'skill_rank': 7, 'elite': 1, 'level': 1, 'potential': 1, 'trust': 0, 'module_id': None, 'module_level': 0, 'relic_ids': [], 'enemy_defense': 0, 'enemy_resistance': 0, 'timing_mode': 'frames', 'window_seconds': 5, 'operator': 'char_002_amiya', 'skill': 1, 'timing': {'target_windows': [[0, 5]]}}}, {'id': 'deepcolor_token_independent', 'input': {'skill_rank': 7, 'elite': 1, 'level': 1, 'potential': 1, 'trust': 0, 'module_id': None, 'module_level': 0, 'relic_ids': [], 'enemy_defense': 0, 'enemy_resistance': 0, 'timing_mode': 'frames', 'window_seconds': 5, 'operator': 'char_110_deepcl', 'skill': 1, 'summon_count': 1, 'timing': {'target_windows': [], 'units': {'token_10001_deepcl_tentac': {'target_windows': [[0, 5]]}}}}}, {'id': 'relic_parts_zero', 'input': {'skill_rank': 7, 'elite': 1, 'level': 1, 'potential': 1, 'trust': 0, 'module_id': None, 'module_level': 0, 'relic_ids': ['rogue_6_relic_cargo_2'], 'enemy_defense': 0, 'enemy_resistance': 0, 'timing_mode': 'frames', 'window_seconds': 5, 'operator': 'mechanist', 'skill': 1, 'relic_context': {'parts_count': 0}}}, {'id': 'relic_parts_three', 'input': {'skill_rank': 7, 'elite': 1, 'level': 1, 'potential': 1, 'trust': 0, 'module_id': None, 'module_level': 0, 'relic_ids': ['rogue_6_relic_cargo_2'], 'enemy_defense': 0, 'enemy_resistance': 0, 'timing_mode': 'frames', 'window_seconds': 5, 'operator': 'mechanist', 'skill': 1, 'relic_context': {'parts_count': 3}}}]
HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
DEADLINE = 900
def sha(raw):return hashlib.sha256(raw).hexdigest()

def error_record(error):
    return {'type':type(error).__name__,'message':str(error),
            'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}

def profile(op,skill,elite,rank):
    return {'id':op,'scope':'operator_profile','fields':{'elite':elite,'level':1,
        'trust':0,'potential':1,'module_id':None,'module_level':0,'selected_skill':skill},
        'skill_ranks':{str(n):rank for n in ((1,2,3) if op in (A,B) else (skill,))},'captured_at':1000.0,
        'sources':{},'field_times':{},'skill_times':{}}

def fixture():
    # Empty recruited overview is a real public state; valid operators are
    # revealed through actual profession branches using public account records.
    return {'id':'public120-window','started_at':0.0,'last_read':1000.0,'operators':{},
        'crew_count':0,'selected_operator':None,'relics':{},'tactical_tools':{},'relic_count':0,
        'inventory_verified':True,'inventory_confirmed_at':1000.0,'bar_signature':[],
        'relic_icon_memory':None,'history':[],'resources':{},'config':{},'maps':{},
        'last_node_content':None,'node_contents':[],
        'public_opaque':{'signed_zero':-0.0,'nullable':None}}



def main():
    parser=argparse.ArgumentParser()
    for key in ('root','guard','out'):parser.add_argument('--'+key,required=True)
    parser.add_argument('--source-count',type=int,required=True)
    parser.add_argument('--section',type=int,required=True)
    parser.add_argument('--phase',choices=('original','candidate'),required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    artifact=Path(__file__).resolve().parent;guard_path=Path(args.guard).resolve()
    assert not out.exists() and root not in out.parents and out!=root
    assert artifact!=root and root not in artifact.parents
    assert sha((artifact/'native_evidence.py').read_bytes())==HELPER_SHA
    guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert guard['section']==args.section and args.section==120
    assert len(expected)==args.source_count and source_map(root)==expected
    app_source=(root/'rouge/app.py').read_bytes()
    assert (b'def sync_scenario_previews(' in app_source)==(args.phase=='candidate')
    assert set(extra)=={'CORE_0.70_VERIFICATION.json'}
    for name,want in extra.items():assert sha((root/name).read_bytes())==want
    out.mkdir();(out/'records').mkdir();(out/'public-state').mkdir()
    rows=[];records=[];pngs=[];calls=[];errors=[];pairs=[];groups=[];api_rows=[];active={'case':'bootstrap','phase':'constructor'}
    started=time.perf_counter();done=threading.Event();window=None;module=None;backend=None;calculator=None;old_paths=None
    receipt={'kind':'ROOT_ACTUAL_120_REAL_MAINWINDOW','phase':args.phase,'section':args.section,'passed':False,'observation_complete':False,
        'workflow_complete':False,'runner_sha256':sha(Path(__file__).read_bytes()),
        'native_helper_sha256':HELPER_SHA,'source_guard_sha256':sha(guard_raw),
        'source_before':expected,'source_additional_before':extra,'source_count':args.source_count,
        'rows':rows,'groups':groups,'API_rows':api_rows,'pairs':pairs,'records':records,'pngs':pngs,'Qt_errors':errors,
        'deadline_seconds':DEADLINE,'private_state_access':False,'native_windows_verified':False,
        'game_chat_sampling_executed':False,
        'comparison_scope':'Six exact plan public API inputs plus six real legal GUI states and fourteen real editor workflows. Original is observation-only and must reproduce stale/edited cross-scope pollution; candidate must restore exact prior strings. Root separately compares legal original/candidate full native graphs and all texts.',
        'restart_scope':'One real close then direct RunState and AccountCache reloads, not a second MainWindow.',
        'formatter_scope':'Three complete formatter groups plus actual technical checkbox views for legal snapshots; actual raw/technical toggles keep current error text and resultNone for invalid snapshots.',
        'preview_scope':'Editor string/key/enabled/dictionary state saved at each actual UI step. No direct cache/key mutation or fake calculator result. Empty recruited overview uses healthy public empty RunState, with valid account previews through actual branches.',
        'PNG_scope':'Exactly two bounded real report excerpts with the timing editor visible. Legal context excerpt and actual profile-only stale/disabled state. Other long texts/states are complete native records, not claimed wholly visible.',
        'original_edit_scope':'Timing editor is visible and enabled in invalid selection. Original early return hides relic row even though it stays enabled; its actual widget setter corruption is a controlled boundary probe, not a claim of visible user typing. Candidate does not type into disabled widgets.',
        'JSON_policy_scope':'Duplicates rejected as app editor policy, RFC SHOULD unique. Bare nonfinite is outside JSON grammar; exponent overflow rejection is app float-range policy. Public dict API/persistence semantics unchanged.'}

    def save(kind,**value):
        ref=write_record(out/'records',len(records)+1,{'kind':kind,**active,**value})
        ref.update(kind=kind,**active);records.append(ref);return ref
    def watchdog():
        if not done.wait(DEADLINE):
            (out/'timeout.json').write_text(json.dumps({'passed':False,'active':active,'deadline_seconds':DEADLINE}))
            os._exit(124)
    threading.Thread(target=watchdog,daemon=True).start();old_hook=sys.excepthook
    def hook(kind,value,tb):
        errors.append({'case':active['case'],'phase':active['phase'],'type':kind.__name__,'message':str(value)})
        old_hook(kind,value,tb)
    sys.excepthook=hook
    try:
        sys.dont_write_bytecode=True;sys.path.insert(0,str(root))
        from PySide6.QtCore import QPoint,qVersion
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication,QScrollArea
        from rouge import app as module,estimate,reporting
        from rouge.run_state import RunState
        from rouge.branch_choice import OVERVIEW
        application=QApplication.instance() or QApplication([])
        backend=module.DesktopBackend;calculator=module.calculate_damage
        old_paths=(module.RUN_STATE,module.OPERATOR_STATE,module.SETTINGS)
        receipt.update(python=sys.version,qt=qVersion())
        def observed(*positional,**keywords):
            before=freeze({'args':positional,'kwargs':keywords,**({'joint':joint()} if window is not None else {})})
            try:value=calculator(*positional,**keywords)
            except Exception as error:
                details=error_record(error);after=freeze({'args':positional,'kwargs':keywords,**({'joint':joint()} if window is not None else {})})
                ref=save('actual_calculate_exception',before=before,after=after,error=details)
                calls.append({'caller':before,'error':details,'native':ref})
                assert_native_equal(after,before,'exception caller purity');raise
            after_context={'args':positional,'kwargs':keywords,**({'joint':joint()} if window is not None else {})}
            after=freeze(after_context)
            ref=save('actual_calculate_result',before=before,after=after_context,result=value)
            calls.append({'caller':before,'error':None,'native':ref,'return_value':value})
            assert_native_equal(after,before,'numeric caller purity');return value
        module.calculate_damage=observed
        with tempfile.TemporaryDirectory(prefix='public120-',dir=out/'public-state') as directory:
            folder=Path(directory);run_path=folder/'run.json';account_path=folder/'account.json'
            run_raw=(json.dumps(fixture(),ensure_ascii=False,indent=2)+'\n').encode()
            account_raw=(json.dumps({values[0]:profile(*values) for values in OPERATORS},ensure_ascii=False,indent=2)+'\n').encode()
            run_path.write_bytes(run_raw);account_path.write_bytes(account_raw)
            module.RUN_STATE=run_path;module.OPERATOR_STATE=account_path;module.SETTINGS=folder/'settings.json'
            module.DesktopBackend=lambda _path,callback:backend(folder/'chat',callback)
            window=module.MainWindow();window.resize(1400,1200);window.show();window.centralWidget().setCurrentIndex(1)
            def idle():
                application.processEvents()
                assert window.isVisible() and not window.auto.isChecked() and not window.timer.isActive()
                assert not window.busy and not window.chat_busy and not window.desktop_request_busy
                assert window.desktop.process is None and not window.desktop.pending and not errors
            def joint():
                return {'run':window.run.state,'account':window.account_cache.records,'disks':{
                    p.relative_to(folder).as_posix():p.read_bytes() for p in sorted(folder.rglob('*')) if p.is_file()}}
            def pure(label,callback):
                before=freeze({'joint':joint(),'damage_result':window.damage_result,'editors':editor_state()})
                value=callback();idle();after=freeze({'joint':joint(),'damage_result':window.damage_result,'editors':editor_state()})
                save('actual_UI_step',label=label,before=before,after=after)
                assert_native_equal(after['joint'],before['joint'],label+' state/account/disk purity');return value
            def editor_state():
                return {'operator':window.operator.currentData(),'skill':window.skill.currentData(),
                    'key':window.timing_preview_key,'timing_text':window.timing_scenario.toPlainText(),
                    'relic_text':window.relic_context.toPlainText(),
                    'timing_enabled':window.timing_scenario.isEnabled(),'relic_enabled':window.relic_context.isEnabled(),
                    'timing_blocked':window.timing_scenario.signalsBlocked(),'relic_blocked':window.relic_context.signalsBlocked(),
                    'timing_previews':window.timing_previews,'relic_previews':window.relic_context_previews,
                    'timing_row_visible':window.damage_form.isRowVisible(window.timing_scenario),
                    'relic_row_visible':window.damage_form.isRowVisible(window.relic_context)}
            def select(op,skill=None):
                assert pure('actual profession/operator branch '+str(op),lambda:window.operator_choices.select_value(op))
                if skill is not None:
                    index=window.skill.findData(skill);assert index>=0
                    pure('actual skill '+str(skill),lambda:window.skill.setCurrentIndex(index))
                assert window.operator.currentData()==op
            def cargo(enabled):
                matches=[window.relic_list.item(i) for i in range(window.relic_list.count())
                         if window.relic_list.item(i).data(module.Qt.ItemDataRole.UserRole)==CARGO]
                assert len(matches)==1
                pure('actual manual cargo selection '+str(enabled),lambda:matches[0].setCheckState(
                    module.Qt.CheckState.Checked if enabled else module.Qt.CheckState.Unchecked))
            def editors(timing,relic):
                pure('actual timing editor exact text',lambda:window.timing_scenario.setPlainText(timing))
                pure('actual relic editor exact text',lambda:window.relic_context.setPlainText(relic))
            def healthy_A(timing=A_TIMING,relic=A_RELIC):
                select(A,1);cargo(True);editors(timing,relic)
                assert window.timing_scenario.isEnabled() and window.relic_context.isEnabled()
            def snapshot(identity,error=None):
                active.update(case=identity,phase='explicit_actual_snapshot');start=len(calls)
                pure('actual MainWindow.calculate',window.calculate)
                displayed=window.damage_text.toPlainText();result=window.damage_result
                if error is not None:
                    assert result is None and error in displayed and len(calls)==start
                    original_text=displayed
                    pure('actual raw checkbox on error',lambda:window.raw_damage.setChecked(True))
                    pure('actual technical checkbox on error',lambda:window.damage_technical.setChecked(True))
                    assert window.damage_result is None and window.damage_text.toPlainText()==original_text
                    pure('actual raw checkbox restore',lambda:window.raw_damage.setChecked(False))
                    pure('actual technical checkbox restore',lambda:window.damage_technical.setChecked(False))
                    assert window.damage_text.toPlainText()==original_text
                    value=freeze({'damage_result':None,'displayed_error':displayed,'editors':editor_state(),'state_and_disks':joint()})
                    ref=save('actual_invalid_window_snapshot',value=value,error_fragment=error)
                else:
                    assert result is not None and len(calls)==start+1 and calls[-1]['error'] is None
                    call=calls[-1];caller=call['caller']['args'][0];raw=result['result']
                    assert raw is call['return_value']
                    assert caller['timing_mode']=='frames' and caller['window_seconds']==5
                    assert caller['enemy_defense']==0 and caller['enemy_resistance']==0
                    assert caller['healing_targets']==1 and caller['continuous_attacks'] is True
                    assert 'base_attack' not in caller and 'target_enemy' not in caller
                    assert caller['module_id'] is None and caller['module_level']==0 and caller['potential']==1 and caller['trust']==0
                    assert_native_equal(result['scenario'],caller,'actual complete UI/native caller')
                    before=freeze({'damage_result':result,'joint':joint(),'editors':editor_state()})
                    texts={'estimate':estimate.format_estimate(raw),'default':reporting.format_report(raw),
                        'technical':reporting.format_report(raw,technical=True)}
                    after=freeze({'damage_result':window.damage_result,'joint':joint(),'editors':editor_state()})
                    save('actual_three_formatter_group',before=before,after=after,texts=texts)
                    assert_native_equal(after,before,'three formatter full native/caller/state/editor purity')
                    assert texts['estimate']==texts['default'] and displayed==texts['default'].replace(chr(160),' ')
                    pure('actual technical checkbox on',lambda:window.damage_technical.setChecked(True))
                    assert window.damage_text.toPlainText()==texts['technical'].replace(chr(160),' ')
                    pure('actual technical checkbox restored',lambda:window.damage_technical.setChecked(False))
                    assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                    assert_native_equal(freeze({'damage_result':window.damage_result,'joint':joint(),'editors':editor_state()}),before,
                        'both report checkbox views preserve complete numeric/caller/state/editor graph')
                    value=freeze({'caller':caller,'damage_result':window.damage_result,'texts':texts,
                        'displayed_damage':window.damage_text.toPlainText(),'editors':editor_state(),'state_and_disks':joint()})
                    ref=save('actual_valid_window_snapshot',value=value,numeric=call['native'])
                rows.append({'id':identity,'valid':error is None,'snapshot':ref})
                with (out/'checkpoint.json').open('w',encoding='utf-8') as stream:
                    stream.write(json.dumps({'phase':args.phase,'completed_snapshot_ids':[r['id'] for r in rows],
                        'completed_group_ids':[g['id'] for g in groups],'active':active,
                        'source_guard_sha256':sha(guard_raw)}));stream.flush();os.fsync(stream.fileno())
                return value,ref
            def finish_group(identity,**details):
                ref=save('actual_editor_workflow_group',id=identity,final_editors=editor_state(),**details)
                groups.append({'id':identity,'record':ref});return ref
            def screenshot(identity,legal=False):
                document=window.damage_text.document()
                if legal:
                    block=next(b for b in window.damage_result['result']['report']['sections'] if b['id']=='calculation_context')
                    title='【'+block['title']+'】';first=document.find(title);assert not first.isNull()
                    last=document.find(block['metrics'][-1]['label']+'：',first);assert not last.isNull()
                else:
                    first=QTextCursor(document);first.movePosition(QTextCursor.MoveOperation.Start)
                    last=QTextCursor(first)
                    for _ in range(min(3,document.blockCount()-1)):last.movePosition(QTextCursor.MoveOperation.NextBlock)
                    title=None
                middle=QTextCursor(first)
                for _ in range((last.blockNumber()-first.blockNumber())//2):middle.movePosition(QTextCursor.MoveOperation.NextBlock)
                pure('center actual bounded report excerpt',lambda:(window.damage_text.setTextCursor(middle),window.damage_text.centerCursor()))
                head=QTextCursor(first);head.movePosition(QTextCursor.MoveOperation.StartOfBlock);visible=[];rectangles=[]
                while head.blockNumber()<=last.blockNumber():
                    assert len(visible)<12
                    end=QTextCursor(head);end.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                    visible.append(head.block().text());rectangles.extend((window.damage_text.cursorRect(head),window.damage_text.cursorRect(end)))
                    if head.blockNumber()==last.blockNumber():break
                    assert head.movePosition(QTextCursor.MoveOperation.NextBlock)
                viewport=window.damage_text.viewport().rect();assert all(viewport.contains(r) for r in rectangles)
                parent=window.timing_scenario.parentWidget()
                while parent is not None and not isinstance(parent,QScrollArea):parent=parent.parentWidget()
                assert parent is not None
                pure('show actual timing editor viewport',lambda:parent.ensureWidgetVisible(window.timing_scenario))
                point=window.timing_scenario.mapTo(parent.viewport(),QPoint(0,0));rect=window.timing_scenario.rect().translated(point)
                assert window.timing_scenario.isVisible() and parent.viewport().rect().contains(rect)
                ref=save('actual_PNG_bounded_editor_report_excerpt',title=title,visible_report_blocks=visible,
                    entire_long_report_visible=False,displayed_text=window.damage_text.toPlainText(),editors=editor_state(),
                    cursor_rects=[(r.x(),r.y(),r.width(),r.height()) for r in rectangles],
                    report_viewport=(viewport.x(),viewport.y(),viewport.width(),viewport.height()),
                    timing_control_rect=(rect.x(),rect.y(),rect.width(),rect.height()))
                path=out/(identity+'.png');assert window.grab().save(str(path),'PNG')
                pngs.append({'path':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'visual':ref})
            idle();assert not window.run.preserve_unreadable and window.run.save_issue is None
            initial=freeze(joint());assert run_path.read_bytes()==run_raw and account_path.read_bytes()==account_raw
            receipt['initial']=save('actual_public_fixture_loaded',run_bytes=run_raw,account_bytes=account_raw,value=initial)
            pure('manual no-relic inventory',lambda:window.auto_relics.setChecked(False))
            pure('read actual run training',lambda:window.use_run_training.setChecked(True))
            pure('use requested observation interval',lambda:window.limit_window.setChecked(True))
            pure('framed timing',lambda:window.frame_timing.setChecked(True))
            pure('zero manual enemy defense',lambda:window.defense.setValue(0))
            pure('zero manual enemy resistance',lambda:window.resistance.setValue(0))
            pure('declared continuous attacks',lambda:window.continuous_attacks.setChecked(True))
            pure('unbound normal animation',lambda:window.normal_animation_reference.setCurrentIndex(0))
            pure('unbound skill animation',lambda:window.skill_animation_reference.setCurrentIndex(0))
            pure('default report presentation',lambda:window.raw_damage.setChecked(False))
            pure('default report without technical expansion',lambda:window.damage_technical.setChecked(False))
            assert window.target_enemy.currentData() is None and not window.target_buff_test.isChecked()
            pure('five-second observation',lambda:window.window_seconds.setValue(5))
            # Exact six public API fixtures are distinct from the longer UI callers.
            for case in PUBLIC_API_CASES:
                active.update(case='API-'+case['id'],phase='exact_public_API')
                source=freeze(case['input']);before=freeze({'input':source,'joint':joint()})
                result=module.calculate_damage(source)
                formatter_before=freeze({'result':result,'input':source,'joint':joint()})
                texts={'estimate':estimate.format_estimate(result),'default':reporting.format_report(result),
                    'technical':reporting.format_report(result,technical=True)}
                assert_native_equal(freeze({'result':result,'input':source,'joint':joint()}),formatter_before,'exact public API formatter group purity')
                assert texts['estimate']==texts['default']
                assert_native_equal(freeze({'input':source,'joint':joint()}),before,'six public API/formatters input/state purity')
                ref=save('actual_exact_public_API_snapshot',input=source,result=result,texts=texts,numeric=calls[-1]['native'])
                api_rows.append({'id':case['id'],'snapshot':ref})
            legal_cases=(
                ('mechanist_empty_target',A,3,'{"windup_frames":0,"recovery_frames":0,"target_windows":[]}',False,''),
                ('amiya_empty_target',B,1,'{"windup_frames":0,"recovery_frames":0,"target_windows":[]}',False,''),
                ('amiya_nonempty',B,1,B_TIMING,False,''),
                ('deepcolor_token_independent',DEEP,1,'{"windup_frames":0,"recovery_frames":0,"target_windows":[],"units":{"'+TOKEN+'":{"target_windows":[[0,5]]}}}',False,''),
                ('relic_parts_zero',A,1,A_TIMING,True,'{"parts_count":0}'),
                ('relic_parts_three',A,1,A_TIMING,True,'{"parts_count":3}'))
            for identity,op,skill,timing,has_cargo,relic in legal_cases:
                active.update(case='legal-'+identity,phase='actual_legal_UI_configuration')
                select(op,skill);cargo(has_cargo);editors(timing,relic)
                value,ref=snapshot('legal-'+identity)
                caller=value['caller'];assert caller['operator']==op and caller['skill']==skill
                assert caller['relic_ids']==([CARGO] if has_cargo else [])
                assert_native_equal(caller['timing'],json.loads(timing),'legal UI timing default JSON types')
                if has_cargo:
                    assert_native_equal(caller['relic_context'],json.loads(relic),'needed cargo condition exact')
                    assert window.damage_form.isRowVisible(window.relic_context)
            healthy_A();original,original_ref=snapshot('valid-owner-A-before')
            screenshot('legal-context-editor',True)
            select(B,1);editors(B_TIMING,B_RELIC);snapshot('valid-owner-B')
            select(A,1);restored,restored_ref=snapshot('valid-owner-A-return')
            assert window.timing_scenario.toPlainText()==A_TIMING and window.relic_context.toPlainText()==A_RELIC
            assert_native_equal(restored['damage_result'],original['damage_result'],'A-B-A complete legal caller/result')
            assert_native_equal(restored['texts'],original['texts'],'A-B-A complete three texts')
            finish_group('valid_owner_pair',before=original_ref,after=restored_ref)
            # Original pollution must actually be observed. Candidate does not
            # simulate typing into disabled controls; it proves restoration.
            for identity,destination,kind in (
                ('profile_only_with_skill','char_120_hibisc','profile'),
                ('profile_only_without_skill','char_285_medic2','profile'),
                ('empty_overview',None,'overview'),
                ('no_current_skill',None,'skill')):
                healthy_A();base_op=A
                if kind=='skill':
                    select(B,1);editors(A_TIMING,A_RELIC);base_op=B
                before,before_ref=snapshot(identity+'-owner-before')
                if kind=='profile':select(destination)
                elif kind=='overview':
                    assert window.run.state['operators']=={} and window.operator_choices.overview==()
                    assert pure('actual empty recruited overview branch',lambda:window.operator_choices.select_branch(OVERVIEW))
                    assert window.operator.currentData() is None
                else:pure('actual real QComboBox no current skill',lambda:window.skill.setCurrentIndex(-1))
                assert window.damage_result is None
                invalid=freeze(editor_state());invalid_ref=save('actual_invalid_selection',value=invalid,displayed=window.damage_text.toPlainText())
                if args.phase=='original':
                    assert invalid['key']==(base_op,1) and invalid['timing_text']==A_TIMING and invalid['relic_text']==A_RELIC
                    assert invalid['timing_enabled'] and invalid['relic_enabled']
                    editors(POISON_TIMING,POISON_RELIC)
                else:
                    assert invalid['key'] is None and invalid['timing_text']=='' and invalid['relic_text']==''
                    assert not invalid['timing_enabled'] and not invalid['relic_enabled']
                if identity=='profile_only_with_skill':screenshot('profile-only-editor-scope',False)
                select(base_op,1);after,after_ref=snapshot(identity+'-owner-return')
                if args.phase=='original':
                    assert after['editors']['timing_text']==POISON_TIMING and after['editors']['relic_text']==POISON_RELIC
                    assert after['caller']['timing']==json.loads(POISON_TIMING) and after['caller']['relic_context']['parts_count']==1
                else:
                    assert after['editors']['timing_text']==A_TIMING and after['editors']['relic_text']==A_RELIC
                    assert_native_equal(after['damage_result'],before['damage_result'],'invalid-selection return complete prior caller/result')
                    assert_native_equal(after['texts'],before['texts'],'invalid-selection return exact three texts')
                finish_group(identity,before=before_ref,invalid=invalid_ref,after=after_ref,
                    original_pollution_observed=args.phase=='original',candidate_restoration_checked=args.phase=='candidate')
            select(B,1);cargo(True);editors(B_TIMING,B_RELIC);before,br=snapshot('skill-pair-S1-before')
            select(B,3);editors('{"windup_frames":0,"recovery_frames":0,"target_windows":[]}',A_RELIC);snapshot('skill-pair-S3')
            select(B,1);after,ar=snapshot('skill-pair-S1-return')
            assert after['editors']['timing_text']==B_TIMING and after['editors']['relic_text']==B_RELIC
            assert_native_equal(after['damage_result'],before['damage_result'],'supported skill cache whole caller/result')
            assert_native_equal(after['texts'],before['texts'],'supported skill cache whole texts')
            finish_group('skill_pair',before=br,after=ar)
            healthy_A('{',A_RELIC);_,br=snapshot('bad-owner-A-before','战斗时序情景需要合法JSON对象。')
            select(B,1);editors(B_TIMING,B_RELIC);snapshot('bad-owner-B-valid')
            select(A,1);_,ar=snapshot('bad-owner-A-return','战斗时序情景需要合法JSON对象。')
            assert window.timing_scenario.toPlainText()=='{'
            finish_group('bad_valid_owner_back',before=br,after=ar)
            healthy_A(A_TIMING,'{');_,br=snapshot('needed-bad-relic-before','藏品测试条件需要合法JSON对象。')
            cargo(False);unused,ur=snapshot('not-needed-bad-relic-ignored')
            assert unused['caller']['relic_context']=={} and window.relic_context.toPlainText()=='{'
            assert not window.damage_form.isRowVisible(window.relic_context)
            cargo(True);_,ar=snapshot('needed-bad-relic-restored','藏品测试条件需要合法JSON对象。')
            finish_group('bad_relic_not_needed',active_before=br,ignored=ur,active_after=ar)
            duplicate_refs=[]
            for n,text in enumerate(('{"target_windows":[],"target_windows":[[0,5]]}',
                                     '{"target_windows":[[0,5]],"target_windows":[]}')):
                healthy_A(text,A_RELIC)
                value,ref=snapshot('ambiguous-target-'+str(n),'战斗时序情景不接受重复字段：target_windows。' if args.phase=='candidate' else None)
                assert window.timing_scenario.toPlainText()==text
                if args.phase=='original':assert_native_equal(value['caller']['timing'],json.loads(text),'original actual duplicate last field wins')
                duplicate_refs.append(ref)
            finish_group('ambiguous_target_duplicate',snapshots=duplicate_refs)
            select(DEEP,1);cargo(False)
            text='{"units":{"'+TOKEN+'":{"target_windows":[],"target_windows":[[0,5]]}}}'
            editors(text,'')
            value,ref=snapshot('nested-unit-duplicate','战斗时序情景不接受重复字段：target_windows。' if args.phase=='candidate' else None)
            if args.phase=='original':assert_native_equal(value['caller']['timing'],json.loads(text),'original nested last field wins')
            finish_group('nested_unit_duplicate',snapshot=ref)
            refs=[]
            for n,text in enumerate(('{"parts_count":0,"parts_count":3}','{"parts_count":3,"parts_count":0}')):
                healthy_A(A_TIMING,text)
                value,ref=snapshot('duplicate-relic-'+str(n),'藏品测试条件不接受重复字段：parts_count。' if args.phase=='candidate' else None)
                if args.phase=='original':assert_native_equal(value['caller']['relic_context'],json.loads(text),'original actual needed last counter wins')
                refs.append(ref)
            finish_group('relic_duplicate',snapshots=refs)
            refs=[]
            for token in ('NaN','Infinity','-Infinity','1e309'):
                text='{"windup_frames":0,"recovery_frames":0,"unused":'+token+'}'
                healthy_A(text,A_RELIC)
                value,ref=snapshot('nonfinite-unused-'+token,
                    '战斗时序情景不接受非有限JSON数值。' if args.phase=='candidate' else None)
                assert window.timing_scenario.toPlainText()==text
                if args.phase=='original':assert_native_equal(value['caller']['timing'],json.loads(text),'original inactive extension actual behavior')
                refs.append(ref)
            finish_group('nonfinite_literals',snapshots=refs,active_scope='nonfinite unknown key inside consumed timing editor')
            text='{"windup_frames":0,"recovery_frames":0,"target_windows":[],"unrelated":"NaN"}'
            healthy_A(text,A_RELIC);value,ref=snapshot('ordinary-string-NAN')
            assert value['caller']['timing']['unrelated']=='NaN' and value['caller']['relic_context']=={'parts_count':0}
            assert window.relic_context.toPlainText()==A_RELIC
            finish_group('strings_and_ordinary_JSON',snapshot=ref,unknown_relic_key_filtered_by_existing_needed_gate=True)
            refs=[]
            for n,text in enumerate(('', '   ')):
                healthy_A(text,'');value,ref=snapshot('blank-timing-'+str(n))
                assert 'timing' not in value['caller'] and value['caller']['relic_context']=={}
                assert window.timing_scenario.toPlainText()==text and window.relic_context.toPlainText()==''
                refs.append(ref)
            finish_group('empty_omission',snapshots=refs,confirmed_public_resources={})
            active.update(case='window',phase='close_direct_RunState_reload');before=freeze(joint())
            window.close();application.processEvents();assert_native_equal(joint(),before,'real close purity')
            restarted=RunState(run_path);assert not restarted.preserve_unreadable and restarted.save_issue is None
            assert_native_equal(restarted.state,initial['run'],'direct reload original accepted loaded graph')
            assert_native_equal(joint(),before,'direct reload disk purity')
            from rouge.account_cache import AccountCache
            from rouge.catalog import catalog,operator_profiles
            account_restarted=AccountCache(account_path,profiles=operator_profiles(),implemented_ids=catalog()['operators'])
            assert not account_restarted.issues and account_restarted.load_issue is None and not account_restarted.preserve_original
            assert_native_equal(account_restarted.records,initial['account'],'direct account reload original graph')
            assert_native_equal(joint(),before,'direct account reload disk purity')
            receipt['close_reload']=save('actual_close_RunState_reload',live_before=before,
                persisted_json=json.loads(run_path.read_bytes()),restart_state=restarted.state,
                account_restart_records=account_restarted.records,disks_after=joint()['disks'])
            window.deleteLater();application.processEvents();window=None
        assert len(api_rows)==6 and len(groups)==14 and len(pngs)==2 and not errors
        assert all(call['error'] is None for call in calls)
        if args.phase=='candidate':receipt.update(passed=True,workflow_complete=True,actual_windows=1)
        else:receipt.update(observation_complete=True,passed=False,workflow_complete=False,
            actual_windows=1,original_issue_observed=True)
    except BaseException as error:receipt['failure']=error_record(error)
    finally:
        if window is not None:window.close()
        if module is not None:
            if backend is not None:module.DesktopBackend=backend
            if calculator is not None:module.calculate_damage=calculator
            if old_paths is not None:module.RUN_STATE,module.OPERATOR_STATE,module.SETTINGS=old_paths
        sys.excepthook=old_hook;receipt['actual_numeric_calls']=len(calls)
        receipt['source_after']=source_map(root)
        receipt['source_additional_after']={name:sha((root/name).read_bytes()) for name in extra}
        receipt['source_drift']=[p for p in set(expected)|set(receipt['source_after']) if expected.get(p)!=receipt['source_after'].get(p)]
        if receipt['source_drift'] or receipt['source_additional_after']!=extra or guard_path.read_bytes()!=guard_raw or errors:
            receipt.update(passed=False,workflow_complete=False,observation_complete=False)
        receipt['elapsed_seconds']=time.perf_counter()-started
        with (out/'receipt.json').open('x',encoding='utf-8') as stream:
            stream.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
        done.set()
    print(json.dumps({'phase':args.phase,'passed':receipt['passed'],'observation_complete':receipt['observation_complete'],
        'API_cases':len(api_rows),'groups':len(groups),'snapshots':len(rows),'pngs':len(pngs)}))
    return 0 if (receipt['passed'] if args.phase=='candidate' else receipt['observation_complete']) else 1

if __name__=='__main__':raise SystemExit(main())
