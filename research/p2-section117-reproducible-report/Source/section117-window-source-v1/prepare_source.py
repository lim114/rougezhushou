"""Stdlib-only Source assembly. Never imports/executes the project or runner."""
from pathlib import Path
import ast, hashlib, json
OUT=Path(__file__).resolve().parent
BLUEPRINT=Path('/workspace/.continuation/section115-window-source-v1/window115.py')
source=BLUEPRINT.read_text()
source=source.replace('import json\n','import json\nimport math\n',1)
source=source.replace("OPERATORS = (('char_002_amiya',1,1,7),('char_1037_amiya3',2,2,10))", """DEEP = 'char_110_deepcl'
TOKEN = 'token_10001_deepcl_tentac'
SHU = 'char_2025_shu'
OPERATORS = ((DEEP,1,2,10),(SHU,3,2,7),('mechanist',3,2,7))
DEEP_TIMING = {'windup_frames':1,'recovery_frames':0,
    'initial_target_windows':[[0,3]],'movement_windows':[[2,3]],'interrupt_windows':[],
    'units':{TOKEN:{'windup_frames':1,'recovery_frames':0,
        'projectile_travel_seconds':10,'target_windows':[[0,30]]}}}
CASES = (
    {'id':'deep-s1-tail-one','operator':DEEP,'skill':1,'mode':'frames','window':30,'summon_count':1,'timing':DEEP_TIMING},
    {'id':'deep-s1-tail-zero','operator':DEEP,'skill':1,'mode':'frames','window':30,'summon_count':0,'timing':DEEP_TIMING},
    {'id':'shu-s1-known-and-unknown','operator':SHU,'skill':1,'mode':'frames','window':5,
        'timing':{'windup_frames':0,'recovery_frames':0}},
    {'id':'shu-s3-enemy-friendly','operator':SHU,'skill':3,'mode':'frames','window':5,
        'timing':{'windup_frames':0,'recovery_frames':0}},
    {'id':'shu-s3-continuous-reference','operator':SHU,'skill':3,'mode':'continuous','window':5,
        'timing':{'windup_frames':0,'recovery_frames':0}},
    {'id':'mechanist-s3-release-no-impact','operator':'mechanist','skill':3,'mode':'frames','window':2,
        'timing':{'windup_frames':6,'recovery_frames':9,'target_disappears_seconds':.3}},
)""")
source=source.replace('DEADLINE = 450','DEADLINE = 600')
source=source.replace("'level':1,\n        'trust':0", "'level':70 if op==DEEP else 1,\n        'trust':100 if op==DEEP else 0",1)
source=source.replace("'skill_ranks':{str(skill):rank}","'skill_ranks':{str(n):rank for n in ((1,3) if op==SHU else (skill,))}",1)
source=source.replace("'public115-window'","'public117-window'")
source=source.replace("'crew_count':2","'crew_count':len(OPERATORS)",1)
start=source.index('def component_fields(result):\n');end=source.index('\ndef main():\n',start)
source=source[:start]+'''def report_fields(caller,result):
    """Read only returned graph and declared UI inputs; call no production helper."""
    sections=result['report']['sections']
    blocks={b['id']:b for b in sections if b['id']=='calculation_context'
        or b['id'].startswith(('event_clock_','output_domain_'))}
    assert len(blocks)==sum(b['id']=='calculation_context' or b['id'].startswith(
        ('event_clock_','output_domain_')) for b in sections)
    wanted_ids={'calculation_context'}
    skill=result['estimate']['skill'];context=blocks['calculation_context']
    context_wanted={'timing_mode':'30帧/秒事件参考' if result['timing']['mode']=='frames' else '连续供靶参数参考',
        'window':skill['window_seconds'],'declared_window':str(caller['window_seconds'])+' 秒',
        'target_source':'手动情景输入参考','enemy_defense':caller['enemy_defense'],
        'enemy_resistance':caller['enemy_resistance']}
    actual={m['key']:m['value'] for m in context['metrics']}
    assert len(actual)==len(context['metrics'])
    assert_native_equal(actual,context_wanted,'actual context scalars to caller/returned observation')
    notes='\\n'.join(context['notes']);timing=caller['timing']
    for field,label in (('windup_frames','前摇预览'),('recovery_frames','后摇预览')):
        assert '本体声明 · '+label+'：'+str(timing[field])+' 帧。' in notes
    if caller['operator']==DEEP:
        for text in ('本体声明 · 初动敌方可获取区间：[0, 3) 秒。',
                     '本体声明 · 移动区间：[2, 3) 秒。',
                     '本体声明 · 打断区间：明确为空。',
                     '触手声明 · 手动弹道延迟：10 秒。',
                     '触手声明 · 敌方可获取区间：[0, 30) 秒。'):
            assert text in notes
    if caller['timing_mode']=='continuous':assert '连续模式保持既有参数参考' in notes
    if 'target_disappears_seconds' in timing:
        assert '本体声明 · 当前目标生命周期终点：'+str(timing['target_disappears_seconds'])+' 秒。' in notes
    assert '敌方供靶不等于友方受疗资格' in notes
    if result['timing']['mode']=='frames':
        for source_key in ('streams','recharge_streams'):
            for index,stream in enumerate(result['timing'].get(source_key,[])):
                identity='event_clock_'+source_key+'_'+str(index);wanted_ids.add(identity)
                block=blocks[identity]
                wanted={'target_scope':{'enemy':'敌方获取参考','friendly':'友方获取参考'}.get(
                    stream.get('target_scope'),'获取来源未确认')}
                for field in ('start_frames','release_frames','impact_frames','times_seconds',
                              'emitted_impact_frames','emitted_times_seconds'):
                    values=stream.get(field)
                    assert values is None or type(values) is list and all(type(v) in (int,float)
                        and math.isfinite(v) for v in values)
                    wanted.update({field+'_count':len(values) if values is not None else None,
                        field+'_first':values[0] if values else None,field+'_last':values[-1] if values else None})
                actual={m['key']:m['value'] for m in block['metrics']}
                assert len(actual)==len(block['metrics'])
                assert_native_equal(actual,wanted,'actual separate phase/index raw stream '+identity)
                if stream['unit']==TOKEN:assert '触手' in block['title']
                assert '各自阶段的相对参考' in '\\n'.join(block['notes'])
                assert '多只或零只' in '\\n'.join(block['notes'])
    kinds=('healing',) if caller['operator']==SHU and caller['skill']==1 else (
        ('damage','healing') if caller['operator']==SHU else ('damage',))
    for kind in kinds:
        identity='output_domain_'+kind;wanted_ids.add(identity);block=blocks[identity]
        total='total_'+kind;phase='phase_'+kind;window='window_'+kind;cycle='cycle_'+kind
        average='cycle_dps' if kind=='damage' else 'cycle_hps'
        wanted={'window_seconds':skill['window_seconds'],'window_total':skill.get(window,
            result.get('total_damage') if kind=='damage' else None),'cast_total':skill.get(total),
            'duration_seconds':skill.get('duration_seconds'),'phase_total':skill.get(phase),
            'recharge_seconds':skill.get('recharge_seconds'),'cycle_seconds':skill.get('cycle_seconds'),
            'cycle_total':skill.get(cycle),'cycle_average':skill.get(average)}
        subtotal=result.get('known_'+kind+'_subtotals')
        if type(subtotal) is dict:
            for field in (window,total,phase,cycle):
                if field in subtotal:wanted['known_'+field]=subtotal[field]
        actual={m['key']:m['value'] for m in block['metrics']}
        assert len(actual)==len(block['metrics'])
        assert_native_equal(actual,wanted,'actual output domain to existing masked/raw scalars '+kind)
        assert '不重新结算' in '\\n'.join(block['notes'])
    assert set(blocks)==wanted_ids
    return blocks

''' +source[end:]
source=source.replace("    parser.add_argument('--source-count',type=int,required=True)","    parser.add_argument('--source-count',type=int,required=True)\n    parser.add_argument('--section',type=int,required=True)",1)
source=source.replace("assert guard['section']==115 and len(expected)==args.source_count and source_map(root)==expected", "assert guard['section']==args.section and args.section==117\n    assert len(expected)==args.source_count and source_map(root)==expected",1)
source=source.replace("'ROOT_ACTUAL_115_REAL_MAINWINDOW'","'ROOT_ACTUAL_117_REAL_MAINWINDOW'")
source=source.replace("'phase':'candidate','passed':False", "'phase':'candidate','section':args.section,'passed':False",1)
start=source.index("        'comparison_scope':");end=source.index('\n    def save(',start)
source=source[:start]+'''        'comparison_scope':'Six actual public producer states. Every new context/domain/clock scalar is checked against the exact UI caller and returned complete raw graph; no original GUI Gold or independent formula/native gameplay proof.',
        'restart_scope':'One real close then direct RunState and AccountCache reloads; no second MainWindow.',
        'formatter_scope':'Three complete formatter group purity plus actual technical checkbox on/off; all complete texts are saved native.',
        'timing_scope':'Explicit manual owner/unit timing through actual advanced JSON; declarations are retained separately and do not establish client animation.',
        'PNG_scope':'Exactly two bounded visible excerpts: Deepcolor token window/potential-tail records, and Shu S1 window/full/phase rows with unknowns. Entire long tables are saved text/native; no whole-table PNG visibility claim.'}
''' +source[end:]
source=source.replace("prefix='public115-'","prefix='public117-'")
source=source.replace("window.resize(1400,1050)","window.resize(1400,1100)")
source=source.replace('calculator=None\n', 'calculator=None;old_paths=None\n',1)
source=source.replace('        backend=module.DesktopBackend;calculator=module.calculate_damage\n','        backend=module.DesktopBackend;calculator=module.calculate_damage\n        old_paths=(module.RUN_STATE,module.OPERATOR_STATE,module.SETTINGS)\n',1)
start=source.index('            def screenshot(');end=source.index("            idle();assert not window.run.preserve_unreadable",start)
source=source[:start]+'''            def screenshot(identity,block,first_key,last_key,include_title=False):
                title='【'+block['title']+'】';document=window.damage_text.document()
                title_cursor=document.find(title);assert not title_cursor.isNull()
                first=title_cursor if include_title else document.find(
                    next(m['label'] for m in block['metrics'] if m['key']==first_key)+'：',title_cursor)
                last=document.find(next(m['label'] for m in block['metrics'] if m['key']==last_key)+'：',first)
                assert not first.isNull() and not last.isNull() and first.blockNumber()<=last.blockNumber()
                middle=QTextCursor(first)
                for _ in range((last.blockNumber()-first.blockNumber())//2):
                    assert middle.movePosition(QTextCursor.MoveOperation.NextBlock)
                pure('center actual bounded report excerpt',lambda:(window.damage_text.setTextCursor(middle),window.damage_text.centerCursor()))
                head=QTextCursor(first);head.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                visible=[];rectangles=[]
                while head.blockNumber()<=last.blockNumber():
                    assert len(visible)<12
                    end=QTextCursor(head);end.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                    visible.append(head.block().text());rectangles.extend((window.damage_text.cursorRect(head),window.damage_text.cursorRect(end)))
                    if head.blockNumber()==last.blockNumber():break
                    assert head.movePosition(QTextCursor.MoveOperation.NextBlock)
                viewport=window.damage_text.viewport().rect()
                assert window.damage_text.isVisible() and all(viewport.contains(rect) for rect in rectangles)
                visual=save('actual_PNG_bounded_report_excerpt',section=block['id'],title=title,
                    first_key=first_key,last_key=last_key,title_visible=include_title,
                    entire_long_section_visible=False,displayed_text=window.damage_text.toPlainText(),visible_blocks=visible,
                    cursor_rects=[(r.x(),r.y(),r.width(),r.height()) for r in rectangles],
                    viewport_rect=(viewport.x(),viewport.y(),viewport.width(),viewport.height()))
                path=out/(identity+'.png');assert window.grab().save(str(path),'PNG')
                pngs.append({'path':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'visual':visual})
''' +source[end:]
start=source.index('            for op,skill,elite,rank in OPERATORS:\n');end=source.index("            active.update(case='window',phase='close_direct_RunState_reload')",start)
source=source[:start]+'''            deep_snapshots=[]
            for case in CASES:
                identity=case['id'];op=case['operator'];skill=case['skill'];mode=case['mode']
                active.update(case=identity,phase='actual_operator_configuration')
                pure('actual public recruited operator',lambda:window.operator_choices.select_value(op))
                index=window.skill.findData(skill);assert index>=0
                pure('actual selected skill',lambda:window.skill.setCurrentIndex(index))
                pure('actual frame/continuous checkbox',lambda:window.frame_timing.setChecked(mode=='frames'))
                pure('explicit observation window',lambda:window.window_seconds.setValue(case['window']))
                pure('explicit manual owner/unit timing JSON',lambda:window.timing_scenario.setPlainText(json.dumps(case['timing'])))
                if op==DEEP:
                    controls=[w for owner,key,skills,w in window.model_option_widgets
                        if owner==DEEP and key=='summon_count' and skill in skills]
                    assert len(controls)==1 and window.damage_form.isRowVisible(controls[0])
                    pure('actual deployed count assumption',lambda:controls[0].setValue(case['summon_count']))
                assert window.healing_targets.value()==1
                active['phase']='explicit_actual_snapshot';start=len(calls);pure('actual MainWindow.calculate',window.calculate)
                assert len(calls)==start+1 and calls[-1]['error'] is None and window.damage_result is not None
                call=calls[-1];caller=call['caller']['args'][0];result=window.damage_result['result']
                assert result is call['return_value']
                assert caller['operator']==op and caller['skill']==skill and caller['timing_mode']==mode
                assert caller['elite']==2 and caller['level']==(70 if op==DEEP else 1)
                assert caller['skill_rank']==(10 if op==DEEP else 7) and caller['trust']==(100 if op==DEEP else 0)
                assert caller['potential']==1 and caller['module_id'] is None and caller['module_level']==0
                assert caller['relic_ids']==[] and caller['continuous_attacks'] is True and caller['healing_targets']==1
                assert caller['enemy_defense']==0 and caller['enemy_resistance']==0
                assert 'base_attack' not in caller and 'target_enemy' not in caller
                assert window.normal_animation_reference.currentData() is None and window.skill_animation_reference.currentData() is None
                assert_native_equal(caller['window_seconds'],window.window_seconds.value(),'real widget/native caller observation')
                assert caller['window_seconds']==case['window']
                assert_native_equal(caller['timing'],case['timing'],'actual complete owner/unit timing caller')
                assert_native_equal(window.damage_result['scenario'],caller,'actual complete UI/native caller')
                blocks=report_fields(caller,result)
                if op==DEEP:
                    token_index=next(i for i,s in enumerate(result['timing']['streams']) if s['unit']==TOKEN)
                    token_stream=result['timing']['streams'][token_index]
                    component=next(c for c in result['components'] if c['name']=='触手')
                    assert len(token_stream['emitted_impact_frames'])>len(token_stream['impact_frames'])
                    assert token_stream['emitted_times_seconds'][-1]>result['estimate']['skill']['duration_seconds']
                    assert len(result['timing']['recharge_streams'])>=2
                    if case['summon_count']==0:
                        assert component['hits']==0 and component['total']==0 and len(token_stream['release_frames'])>0
                    else:assert component['hits']>0
                elif op==SHU and skill==1:
                    assert result['total_healing'] is None and result['estimate']['skill']['total_healing'] is None
                    assert result['next_attack_healing_reference']['actual_acquisition_times_seconds'] is None
                    assert 'known_window_healing' in {m['key'] for m in blocks['output_domain_healing']['metrics']}
                elif op==SHU and mode=='frames':
                    current=result['timing']['streams'];assert len(current)>=2
                    assert {s['target_scope'] for s in current}>={'enemy','friendly'}
                    assert {s['unit'] for s in current}=={SHU}
                elif mode=='continuous':assert not any(b.startswith('event_clock_') for b in blocks)
                else:
                    stream=result['timing']['streams'][0]
                    assert stream['release_frames'] and stream['impact_frames']==[] and stream['emitted_impact_frames']==[]
                before=freeze({'damage_result':window.damage_result,'joint':joint()})
                texts={'estimate':estimate.format_estimate(result),'default':reporting.format_report(result),
                       'technical':reporting.format_report(result,technical=True)}
                after=freeze({'damage_result':window.damage_result,'joint':joint()})
                save('actual_three_formatter_group',before=before,after=after,texts=texts)
                assert_native_equal(after,before,'three formatter joint purity')
                assert texts['estimate']==texts['default'] and window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                for block in blocks.values():
                    for text in texts.values():assert '【'+block['title']+'】' in text
                before=freeze({'damage_result':window.damage_result,'joint':joint()})
                pure('actual technical checkbox on',lambda:window.damage_technical.setChecked(True))
                assert window.damage_text.toPlainText()==texts['technical'].replace(chr(160),' ')
                pure('actual ordinary checkbox restored',lambda:window.damage_technical.setChecked(False))
                assert window.damage_text.toPlainText()==texts['default'].replace(chr(160),' ')
                assert_native_equal(freeze({'damage_result':window.damage_result,'joint':joint()}),before,
                    'both actual report views preserve complete result/run/account/disks')
                snapshot=freeze({'caller':caller,'damage_result':window.damage_result,'texts':texts,
                    'displayed_damage':window.damage_text.toPlainText(),'state_and_disks':joint()})
                ref=save('actual_window_snapshot',value=snapshot,report_blocks=blocks)
                rows.append({'id':identity,'operator':op,'skill':skill,'mode':mode,'window_seconds':case['window'],
                    'snapshot':ref,'numeric':call['native'],'new_report_ids':list(blocks)})
                if op==DEEP:
                    deep_snapshots.append((snapshot,ref))
                    if len(deep_snapshots)==2:
                        old,old_ref=deep_snapshots[0];new_caller=freeze(caller);new_caller['summon_count']=1
                        assert_native_equal(new_caller,old['caller'],'same exact UI caller except count0/1')
                        assert_native_equal(snapshot['state_and_disks'],old['state_and_disks'],'count preview state/account/all disk purity')
                        pairs.append({'kind':'count0_vs_count1','one':old_ref,'zero':ref,
                            'same_caller_except_count':True,'state_account_all_disks_preserved':True})
                with (out/'checkpoint.json').open('w',encoding='utf-8') as stream:
                    stream.write(json.dumps({'completed_case_ids':[r['id'] for r in rows],'next_case_index':len(rows),
                        'active':active,'source_guard_sha256':sha(guard_raw)}));stream.flush();os.fsync(stream.fileno())
                if identity=='deep-s1-tail-one':
                    screenshot('deep-token-window-and-tail',blocks['event_clock_streams_'+str(token_index)],
                        'impact_frames_count','emitted_impact_frames_last')
                if identity=='shu-s1-known-and-unknown':
                    screenshot('shu-next-attack-window-cast-unknown',blocks['output_domain_healing'],
                        'window_seconds','phase_total',True)
''' +source[end:]
source=source.replace('assert len(rows)==4 and len(pairs)==2 and len(pngs)==2 and not errors',
    'assert len(rows)==len(CASES)==6 and len(pairs)==1 and len(pngs)==2 and not errors\n        assert all(call[\'error\'] is None for call in calls)')
source=source.replace('            if calculator is not None:module.calculate_damage=calculator\n',
    '            if calculator is not None:module.calculate_damage=calculator\n            if old_paths is not None:module.RUN_STATE,module.OPERATOR_STATE,module.SETTINGS=old_paths\n',1)
source=source.replace('Source preparation only; Root runs one real current-output breakdown window.',
    'Source preparation only; Root executes six real producer/report window states.')
assert 'component_fields' not in source and 'public115' not in source and '==115' not in source
ast.parse(source);compile(source,'<section117-source-runner>','exec')
(OUT/'window117.py').write_text(source,encoding='utf-8')
helper=Path('/workspace/.continuation/section116-window-source-v1/native_evidence.py').read_bytes()
assert hashlib.sha256(helper).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
(OUT/'native_evidence.py').write_bytes(helper)
checks={'kind':'SOURCE_ASSEMBLY_AST_COMPILE_NOEXEC','runner_executed':False,'project_imports_or_API_tests_executed':False,
    'tracked_mutations':False,'blueprint':{'path':str(BLUEPRINT),'bytes':len(BLUEPRINT.read_bytes()),
    'sha256':hashlib.sha256(BLUEPRINT.read_bytes()).hexdigest()},'helper_bytes_identical':True,'public_producer_cases':6,
    'source_count':'required CLI argument; exact full map compared against guard, no future constant count',
    'evidence_kind':'Root alone may import/execute runner, save native/gzip records and PNGs; none exist from this Source assembly'}
(OUT/'source-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source_candidate':str(OUT/'window117.py'),'bytes':len(source.encode()),'sha256':hashlib.sha256(source.encode()).hexdigest(),'compile_noexec':True}))
