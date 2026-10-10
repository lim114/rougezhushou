"""Source assembly only. No project/runner/helper import or execution."""
from pathlib import Path
import ast,hashlib,json
OUT=Path(__file__).resolve().parent
BLUE=Path('/workspace/.continuation/section115-window-source-v1/window115.py')
PACKET=Path('/workspace/.continuation/p2-scenario-state-source-v1')
s=BLUE.read_text()
s=s.replace("OPERATORS = (('char_002_amiya',1,1,7),('char_1037_amiya3',2,2,10))", """A = 'mechanist'
B = 'char_002_amiya'
DEEP = 'char_110_deepcl'
TOKEN = 'token_10001_deepcl_tentac'
CARGO = 'rogue_6_relic_cargo_2'
OPERATORS = ((A,1,2,7),(B,1,2,7),(DEEP,1,1,7))
A_TIMING = '{ "windup_frames" : 0, "recovery_frames" : 0, "target_windows" : [] }\\n'
A_RELIC = '{ "parts_count" : 0, "unused" : "A 原文" }\\n'
B_TIMING = '{"windup_frames":0,"recovery_frames":0,"target_windows":[[0,5]]} '
B_RELIC = '{"parts_count":3,"unused":"B 原文"} '
POISON_TIMING = '{"windup_frames":0,"recovery_frames":0,"target_windows":[[0,2]]}'
POISON_RELIC = '{"parts_count":1,"unused":"unsupported edit"}'""")
s=s.replace('DEADLINE = 450','DEADLINE = 900')
plan=(PACKET/'PUBLIC_VALIDATION_PLAN120.json').read_bytes();api=json.loads(plan)['public_API_baseline_candidate_cases']
s=s.replace("HELPER_SHA =", 'PUBLIC_API_CASES = '+repr(api)+'\nHELPER_SHA =',1)
s=s.replace("'skill_ranks':{str(skill):rank}","'skill_ranks':{str(n):rank for n in ((1,2,3) if op in (A,B) else (skill,))}",1)
start=s.index('def fixture():\n');end=s.index('\ndef component_fields(',start)
s=s[:start]+'''def fixture():
    # Empty recruited overview is a real public state; valid operators are
    # revealed through actual profession branches using public account records.
    return {'id':'public120-window','started_at':0.0,'last_read':1000.0,'operators':{},
        'crew_count':0,'selected_operator':None,'relics':{},'tactical_tools':{},'relic_count':0,
        'inventory_verified':True,'inventory_confirmed_at':1000.0,'bar_signature':[],
        'relic_icon_memory':None,'history':[],'resources':{},'config':{},'maps':{},
        'last_node_content':None,'node_contents':[],
        'public_opaque':{'signed_zero':-0.0,'nullable':None}}

''' +s[end:]
start=s.index('def component_fields(');end=s.index('\ndef main():',start);s=s[:start]+s[end:]
s=s.replace("    parser.add_argument('--source-count',type=int,required=True)","    parser.add_argument('--source-count',type=int,required=True)\n    parser.add_argument('--section',type=int,required=True)\n    parser.add_argument('--phase',choices=('original','candidate'),required=True)",1)
s=s.replace("assert guard['section']==115 and len(expected)==args.source_count and source_map(root)==expected", "assert guard['section']==args.section and args.section==120\n    assert len(expected)==args.source_count and source_map(root)==expected\n    app_source=(root/'rouge/app.py').read_bytes()\n    assert (b'def sync_scenario_previews(' in app_source)==(args.phase=='candidate')",1)
s=s.replace("'ROOT_ACTUAL_115_REAL_MAINWINDOW'","'ROOT_ACTUAL_120_REAL_MAINWINDOW'")
s=s.replace("'phase':'candidate','passed':False","'phase':args.phase,'section':args.section,'passed':False,'observation_complete':False",1)
s=s.replace("rows=[];records=[];pngs=[];calls=[];errors=[];pairs=[];", "rows=[];records=[];pngs=[];calls=[];errors=[];pairs=[];groups=[];api_rows=[];",1)
s=s.replace("'rows':rows,'pairs':pairs,'records':records", "'rows':rows,'groups':groups,'API_rows':api_rows,'pairs':pairs,'records':records",1)
start=s.index("        'comparison_scope':");end=s.index('\n    def save(',start)
s=s[:start]+'''        'comparison_scope':'Six exact plan public API inputs plus six real legal GUI states and fourteen real editor workflows. Original is observation-only and must reproduce stale/edited cross-scope pollution; candidate must restore exact prior strings. Root separately compares legal original/candidate full native graphs and all texts.',
        'restart_scope':'One real close then direct RunState and AccountCache reloads, not a second MainWindow.',
        'formatter_scope':'Three complete formatter groups plus actual technical checkbox views for legal snapshots; actual raw/technical toggles keep current error text and resultNone for invalid snapshots.',
        'preview_scope':'Editor string/key/enabled/dictionary state saved at each actual UI step. No direct cache/key mutation or fake calculator result. Empty recruited overview uses healthy public empty RunState, with valid account previews through actual branches.',
        'PNG_scope':'Exactly two bounded real report excerpts with the timing editor visible. Legal context excerpt and actual profile-only stale/disabled state. Other long texts/states are complete native records, not claimed wholly visible.',
        'JSON_policy_scope':'Duplicates rejected as app editor policy, RFC SHOULD unique. Bare nonfinite is outside JSON grammar; exponent overflow rejection is app float-range policy. Public dict API/persistence semantics unchanged.'}
''' +s[end:]
s=s.replace('calculator=None\n','calculator=None;old_paths=None\n',1)
s=s.replace('from PySide6.QtCore import qVersion','from PySide6.QtCore import QPoint,qVersion',1)
s=s.replace('from PySide6.QtWidgets import QApplication','from PySide6.QtWidgets import QApplication,QScrollArea',1)
s=s.replace('        from rouge.run_state import RunState\n','        from rouge.run_state import RunState\n        from rouge.branch_choice import OVERVIEW\n',1)
s=s.replace('        backend=module.DesktopBackend;calculator=module.calculate_damage\n','        backend=module.DesktopBackend;calculator=module.calculate_damage\n        old_paths=(module.RUN_STATE,module.OPERATOR_STATE,module.SETTINGS)\n',1)
s=s.replace("prefix='public115-'","prefix='public120-'")
s=s.replace('window.resize(1400,1050)','window.resize(1400,1200)')
s=s.replace("before=freeze({'joint':joint(),'damage_result':window.damage_result})\n                value=callback();idle();after=freeze({'joint':joint(),'damage_result':window.damage_result})", "before=freeze({'joint':joint(),'damage_result':window.damage_result,'editors':editor_state()})\n                value=callback();idle();after=freeze({'joint':joint(),'damage_result':window.damage_result,'editors':editor_state()})",1)
start=s.index('            def screenshot(');end=s.index("            idle();assert not window.run.preserve_unreadable",start)
s=s[:start]+'''            def editor_state():
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
''' +s[end:]
start=s.index('            for op,skill,elite,rank in OPERATORS:\n');end=s.index("            active.update(case='window',phase='close_direct_RunState_reload')",start)
s=s[:start]+'''            pure('five-second observation',lambda:window.window_seconds.setValue(5))
            # Exact six public API fixtures are distinct from the longer UI callers.
            for case in PUBLIC_API_CASES:
                active.update(case='API-'+case['id'],phase='exact_public_API')
                source=freeze(case['input']);before=freeze({'input':source,'joint':joint()})
                result=module.calculate_damage(source)
                texts={'estimate':estimate.format_estimate(result),'default':reporting.format_report(result),
                    'technical':reporting.format_report(result,technical=True)}
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
''' +s[end:]
s=s.replace('assert len(rows)==4 and len(pairs)==2 and len(pngs)==2 and not errors\n        receipt.update(passed=True,workflow_complete=True,actual_windows=1)',
'''assert len(api_rows)==6 and len(groups)==14 and len(pngs)==2 and not errors
        assert all(call['error'] is None for call in calls)
        if args.phase=='candidate':receipt.update(passed=True,workflow_complete=True,actual_windows=1)
        else:receipt.update(observation_complete=True,passed=False,workflow_complete=False,
            actual_windows=1,original_issue_observed=True)''')
s=s.replace('            if calculator is not None:module.calculate_damage=calculator\n',
    '            if calculator is not None:module.calculate_damage=calculator\n            if old_paths is not None:module.RUN_STATE,module.OPERATOR_STATE,module.SETTINGS=old_paths\n',1)
s=s.replace("receipt.update(passed=False,workflow_complete=False)\n        receipt['elapsed_seconds']", "receipt.update(passed=False,workflow_complete=False,observation_complete=False)\n        receipt['elapsed_seconds']",1)
s=s.replace("print(json.dumps({'passed':receipt['passed'],'rows':len(rows),'pairs':len(pairs),'pngs':len(pngs)}))\n    return 0 if receipt['passed'] else 1", "print(json.dumps({'phase':args.phase,'passed':receipt['passed'],'observation_complete':receipt['observation_complete'],\n        'API_cases':len(api_rows),'groups':len(groups),'snapshots':len(rows),'pngs':len(pngs)}))\n    return 0 if (receipt['passed'] if args.phase=='candidate' else receipt['observation_complete']) else 1",1)
s=s.replace("                texts={'estimate':estimate.format_estimate(result),'default':reporting.format_report(result),\n                    'technical':reporting.format_report(result,technical=True)}\n                assert texts['estimate']==texts['default']",
    "                formatter_before=freeze({'result':result,'input':source,'joint':joint()})\n                texts={'estimate':estimate.format_estimate(result),'default':reporting.format_report(result),\n                    'technical':reporting.format_report(result,technical=True)}\n                assert_native_equal(freeze({'result':result,'input':source,'joint':joint()}),formatter_before,'exact public API formatter group purity')\n                assert texts['estimate']==texts['default']",1)
s=s.replace("        'JSON_policy_scope':","        'original_edit_scope':'Timing editor is visible and enabled in invalid selection. Original early return hides relic row even though it stays enabled; its actual widget setter corruption is a controlled boundary probe, not a claim of visible user typing. Candidate does not type into disabled widgets.',\n        'JSON_policy_scope':",1)
s=s.replace('Source preparation only; Root runs one real current-output breakdown window.',
    'Source only; Root executes original observation/candidate editor isolation workflows.')
assert 'component_fields' not in s and 'public115' not in s and '==115' not in s
ast.parse(s);compile(s,'<Source120window>','exec');(OUT/'window120.py').write_text(s,encoding='utf-8')
helper=Path('/workspace/.continuation/section116-window-source-v1/native_evidence.py').read_bytes();assert hashlib.sha256(helper).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a';(OUT/'native_evidence.py').write_bytes(helper)
(OUT/'public-plan120.json').write_bytes(plan)
checks={'kind':'SOURCE_ASSEMBLY_AST_COMPILE_NOEXEC','runner_executed':False,'project_imports_API_tests_Qt_Wine_helpers_native_gzip_Git_executed':False,'tracked_mutations':False,'blueprint':{'bytes':len(BLUE.read_bytes()),'sha256':hashlib.sha256(BLUE.read_bytes()).hexdigest()},'six_exact_plan_API_inputs':6,'six_real_legal_UI_states':6,'actual_UI_workflow_groups':14,'old_phase':'observation_only_not_product_PASS','Source_count':'CLI actual guard count; never predicted','helper_f040_bytes_identical':True,'Root_actual_PNGs':2,'Root_actual_saved_reader_required':True}
(OUT/'source-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw=(OUT/'window120.py').read_bytes();print(json.dumps({'runner':str(OUT/'window120.py'),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'compile_noexec':True}))
