"""Real Windows Qt widgets under Wine; isolated state; no capture/chat operations."""
import hashlib, importlib, importlib.metadata, json, os, platform, subprocess, sys, tempfile, time, traceback
from pathlib import Path
ROOT=Path(r'Z:\workspace\rougezhushou')
OUT=Path(r'Z:\workspace\.compat')
sys.path.insert(0,str(ROOT))
def source_hashes():
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in (ROOT/'rouge',) for p in sorted(folder.rglob('*'))
            if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
checks=[];started=time.perf_counter();window=None;app=None;before=source_hashes()
receipt={'scope':'Wine Windows binary compatibility; no native Windows or game integration',
         'native_windows_verified':False,'game_captures':0,'chat_requests':0,
         'private_state_isolated':True,'platform':platform.platform(),'python':sys.version,
         'checks':checks,'passed':False,'complete_ui_validation':False,'plain_text_normalization':'QPlainTextEdit converts non-breaking spaces to ordinary spaces'}
try:
    for name in ('PySide6.QtWidgets','numpy','cv2','win32gui','win32process','win32api','httpx','rapidocr_onnxruntime','windows_capture'):
        importlib.import_module(name)
        checks.append({'scope':'real_dependency_import','module':name,'passed':True})
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication,QPushButton
    import rouge.app as module
    from rouge.reporting import format_report
    diagnosis_path=ROOT/'research/p2-friendly-scope-report/independent-diagnosis.json'
    assert diagnosis_path.is_file(),str(diagnosis_path)
    diagnosis_bytes=diagnosis_path.read_bytes()
    diagnosis=json.loads(diagnosis_bytes)
    from rouge.capture import list_game_windows
    with tempfile.TemporaryDirectory() as folder:
        isolated=Path(folder)
        module.RUN_STATE=isolated/'run.json';module.OPERATOR_STATE=isolated/'operators.json';module.SETTINGS=isolated/'settings.json'
        backend=module.DesktopBackend
        module.DesktopBackend=lambda _path,callback:backend(isolated/'chat',callback)
        app=QApplication([]);window=module.MainWindow();window.show();app.processEvents()
        assert window.isVisible()
        assert not window.auto.isChecked() and window.capture.target is None
        assert not window.desktop.process and not window.desktop_request_busy
        assert not list_game_windows()
        checks.append({'scope':'actual_main_window_visible','title':window.windowTitle(),
                       'win32_game_enumeration':'no Arknights.exe window present',
                       'auto_sampling':False,'desktop_backend_started':False})
        window.auto_relics.setChecked(False)
        original_select=window.select_operator
        def checked_select(op):
            assert op in module.catalog()['operators'],op
            selected=original_select(op)
            assert window.operator.currentData()==op,(op,window.operator.currentData())
            return selected
        window.select_operator=checked_select
        skills=0
        for op,profile in module.catalog()['operators'].items():
            for skill in range(1,len(profile['skills'])+1):
                window.select_operator(op)
                window.skill.setCurrentIndex(window.skill.findData(skill))
                window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                actual=window.damage_text.toPlainText();expected=format_report(result,technical=window.damage_technical.isChecked()).replace(chr(160),' ')
                if actual!=expected:
                    (OUT/'wine-ui-report-difference-050.json').write_text(json.dumps({'operator':op,'skill':skill,'actual':actual,'expected':expected},ensure_ascii=False,indent=2),encoding='utf-8')
                    raise AssertionError(f'report text differs for {op} skill {skill}')
                skills+=1
        assert skills==87,skills
        checks.append({'scope':'actual_controls_calculate_all_profiles','skills':skills,'passed':True})
        for guarded_op,reference_key in (('char_437_mizuki','mizuki_s1_reference'),('char_4087_ines','ines_dot_reference')):
            window.select_operator(guarded_op)
            window.skill.setCurrentIndex(window.skill.findData(1));window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            guarded=window.damage_result['result']
            assert reference_key in guarded
            assert guarded['estimate']['skill']['duration_seconds'] is None
            assert guarded['estimate']['skill']['cycle_seconds'] is None
            assert '未知' in window.damage_text.toPlainText()
            checks.append({'scope':'unknown_s1_end_and_cycle_visible','operator':guarded_op,'skill':1,
                           'duration_seconds':None,'cycle_seconds':None,
                           'report_contains_unknown':True,'passed':True})
        window.select_operator('char_1044_hsgma2')
        window.skill.setCurrentIndex(window.skill.findData(3))
        terminal=next(widget for owner,key,_skills,widget in window.model_option_widgets
                      if owner=='char_1044_hsgma2' and key=='last_stand_seconds')
        terminal.setValue(5);window.limit_window.setChecked(True);window.window_seconds.setValue(1)
        window.calculate();app.processEvents()
        assert window.damage_result,window.damage_text.toPlainText()
        guarded=window.damage_result['result'];reference=guarded['manual_close_reference']
        assert reference['close_seconds'] is None
        assert guarded['estimate']['skill']['window_seconds']==1
        assert guarded['estimate']['skill']['duration_seconds'] is None
        assert guarded['total_damage'] is None
        assert '未知' in window.damage_text.toPlainText()
        checks.append({'scope':'positive_terminal_duration_preserves_window','operator':'char_1044_hsgma2','skill':3,
                       'last_stand_seconds':5,'requested_window_seconds':1,'reported_window_seconds':1,
                       'close_seconds':None,'complete_total':None,'passed':True})
        window.select_operator('char_1015_aglna2')
        window.skill.setCurrentIndex(window.skill.findData(1))
        weight=next(widget for owner,key,_skills,widget in window.model_option_widgets
                    if owner=='char_1015_aglna2' and key=='enemy_weight')
        window.window_seconds.setValue(3)
        talent=[]
        for mass in (3,4):
            weight.setValue(mass);window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            talent.append(next(c['per_hit'] for c in result['components'] if c['name']=='飘浮大地之上'))
        assert talent[0]>talent[1],talent
        checks.append({'scope':'actual_manual_weight_control_selects_talent','weights':[3,4],'per_hit':talent,'passed':True})
        for op,key in (('char_1015_aglna2','aglna_liftoff_reference'),('char_196_sunbr','next_attack_healing_reference'),('char_2025_shu','next_attack_healing_reference'),('char_1046_sbell2','snow_field_reference')):
            window.select_operator(op)
            window.skill.setCurrentIndex(window.skill.findData(2 if op in ('char_1015_aglna2','char_1046_sbell2') else 1))
            for horizon in (0,1):
                window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                assert key in result
                assert result['estimate']['skill']['window_seconds']==horizon
                amount=result['total_healing'] if key=='next_attack_healing_reference' else result['total_damage']
                assert amount==0 if horizon==0 else amount is None
                assert result['estimate']['skill']['cycle_seconds'] is None
            checks.append({'scope':'actual_short_window_controls_and_unknowns','operator':op,'zero_window_total':0,'one_second_total':None,'passed':True})
        tech=window.technology_reference
        assert tech.nodes.count()==57
        for index in range(tech.nodes.count()):
            tech.nodes.setCurrentIndex(index);app.processEvents()
            assert '账户解锁状态：未知' in tech.text.toPlainText()
        tech.search.setText('颊囊');app.processEvents();assert tech.nodes.count()==2
        tech.search.setText('不存在的科技xyz');app.processEvents();assert tech.nodes.count()==0
        assert '没有匹配' in tech.text.toPlainText()
        tech.search.clear();tech.nodes.setCurrentIndex(tech.nodes.findData('rogue_6_difficulty_1'));app.processEvents()
        assert '<保密等级3>' in tech.text.toPlainText()
        assert '原件SHA256' not in tech.text.toPlainText()
        tech.technical.setChecked(True);app.processEvents();assert '原件SHA256' in tech.text.toPlainText()
        tech.technical.setChecked(False);app.processEvents()
        checks.append({'scope':'actual_technology_browser','nodes':57,'duplicate_name_results':2,'empty_search':True,'grade_gate':3,'technical_toggle':True,'passed':True})
        for op,skills in (('char_4182_oblvns',(1,)),('char_1044_hsgma2',(2,)),('char_1048_orchd2',(1,2,3))):
            window.select_operator(op)
            for skill in skills:
                window.skill.setCurrentIndex(window.skill.findData(skill))
                for horizon in (0,1):
                    window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                    assert window.damage_result,window.damage_text.toPlainText()
                    result=window.damage_result['result']
                    assert 'unbound_cast_reference' in result
                    assert result['estimate']['skill']['window_seconds']==horizon
                    assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                    if op=='char_1044_hsgma2':
                        assert result['total_healing']==0 if horizon==0 else result['total_healing'] is None
                    assert result['estimate']['skill']['cycle_seconds'] is None
                checks.append({'scope':'actual_unbound_multihit_short_window_controls','operator':op,'skill':skill,'zero_window_total':0,'one_second_total':None,'passed':True})
        for op,skills in (('char_1029_yato2',(2,3)),('char_1050_chen3',(2,3)),('char_4202_haruka',(1,2,3)),('char_2027_wang',(1,2,3)),('char_4204_mantra',(1,2,3))):
            window.select_operator(op)
            for skill in skills:
                window.skill.setCurrentIndex(window.skill.findData(skill))
                if op in ('char_4202_haruka','char_4204_mantra'):
                    keys=('bubble_bursts','levitate_triggers') if op=='char_4202_haruka' else ('palsy_triggers','palsy_overflow_hits')
                    for owner,key,_skills,widget in window.model_option_widgets:
                        if owner==op and key in keys:widget.setValue(1)
                for horizon in (0,1):
                    window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                    assert window.damage_result,window.damage_text.toPlainText()
                    result=window.damage_result['result']
                    assert result['estimate']['skill']['window_seconds']==horizon
                    if horizon==0:
                        assert result['total_damage']==0
                        if op=='char_4202_haruka':assert result['total_healing']==0
                    elif op=='char_4202_haruka' and skill==1:
                        assert result['total_healing'] is None
                    else:assert result['total_damage'] is None
                checks.append({'scope':'actual_section31_35_short_window_and_event_controls','operator':op,'skill':skill,'zero_window_output':0,'positive_unplaced_source_unknown':True,'passed':True})
        for op in ('char_133_mm','char_1046_sbell2'):
            window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(1))
            for horizon in (0,1):
                window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                assert result['estimate']['skill']['window_seconds']==horizon
                assert result['estimate']['skill']['duration_seconds'] is None
                assert result['estimate']['skill']['cycle_seconds'] is None
                if horizon==0:assert result['total_damage']==0
                assert '未知' in window.damage_text.toPlainText()
            checks.append({'scope':'actual_mei_and_sbell_window_end_controls','operator':op,'zero_window':0,'positive_window_preserved':1,'actual_end_unknown':True,'passed':True})
        window.select_operator('char_1046_sbell2')
        snow_count=next(widget for owner,key,_skills,widget in window.model_option_widgets if owner=='char_1046_sbell2' and key=='snow_entries')
        snow_count.setValue(2)
        for skill in (1,2,3):
            window.skill.setCurrentIndex(window.skill.findData(skill))
            for horizon in (0,1):
                window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                assert result['estimate']['skill']['window_seconds']==horizon
            checks.append({'scope':'actual_snow_entry_controls','skill':skill,'manual_entries':2,'zero_window':0,'unplaced_positive_total':None,'passed':True})
        snow_count.setValue(0)
        for op in ('char_4087_ines','char_1041_angel2'):
            window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(3))
            for horizon in (0,1):
                window.window_seconds.setValue(horizon);window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                assert result['estimate']['skill']['window_seconds']==horizon
                assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                assert result.get('external_event_reference')
            checks.append({'scope':'actual_independent_deployment_projectile_controls','operator':op,'zero_window':0,'unplaced_positive_total':None,'passed':True})
        window.select_operator('char_298_susuro');window.skill.setCurrentIndex(window.skill.findData(1))
        window.window_seconds.setValue(10)
        window.timing_scenario.setPlainText(json.dumps({'target_disappears_seconds':0}))
        for use_frames in (True,False):
            window.frame_timing.setChecked(use_frames);window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            assert result['total_damage']==0 and result['total_healing']>0
            assert '真实友方获取时钟未核验' in window.damage_text.toPlainText()
            checks.append({'scope':'actual_friendly_clock_explanation_probe','passed':True,
                'mode':'frames' if use_frames else 'continuous','scenario':window.damage_result['scenario'],
                'report_contains_friendly_clock_unknown':True,'numerical_damage':result['total_damage'],
                'numerical_healing':result['total_healing']})
        checks.append({'scope':'actual_friendly_healing_survives_empty_enemy','modes':['frames','continuous'],'positive_healing':True,'enemy_damage':0,'passed':True})
        window.select_operator('char_002_amiya');window.skill.setCurrentIndex(window.skill.findData(1))
        window.timing_scenario.setPlainText(json.dumps({'target_disappears_seconds':0}))
        window.limit_window.setChecked(False);window.frame_timing.setChecked(False);window.calculate();app.processEvents()
        assert window.damage_result,window.damage_text.toPlainText()
        result=window.damage_result['result'];skill=result['estimate']['skill']
        assert result['total_damage']==0 and skill['initial_seconds']==7 and skill['recharge_seconds']==30
        checks.append({'scope':'actual_amiya_empty_enemy_natural_recharge','first':7,'recharge':30,'enemy_damage':0,'passed':True})
        window.timing_scenario.clear();window.frame_timing.setChecked(True);window.limit_window.setChecked(True);window.window_seconds.setValue(1)
        window.window_seconds.setValue(10)
        op='char_437_mizuki'
        window.operator_observations[op]={'fields':{'elite':2,'level':60,'potential':1,'trust':100,'module_id':'uniequip_003_mizuki','module_level':2},'skill_ranks':{'1':10,'2':10,'3':10}}
        window.select_operator(op);window.update_operator()
        for skill in (1,2,3):
            window.skill.setCurrentIndex(window.skill.findData(skill));window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            assert 'mizuki_amb_y_reference' in result and result['total_damage'] is None
            assert result['total_healing'] is None
            assert '模组实际额外回复：未知' in window.damage_text.toPlainText()
            checks.append({'scope':'actual_mizuki_amb_y_readonly_cultivation_preview','skill':skill,'module_level':2,'level':60,'actual_extra_healing':None,'passed':True})
        def train(op,fields,ranks=None):
            window.operator_observations[op]={'fields':fields,'skill_ranks':ranks or {'1':10,'2':10,'3':10}}
            window.select_operator(op);window.update_operator()
        def calculate_result():
            window.calculate();app.processEvents()
            assert window.damage_result,window.damage_text.toPlainText()
            result=window.damage_result['result']
            actual=window.damage_text.toPlainText()
            assert actual==format_report(result,technical=window.damage_technical.isChecked()).replace(chr(160),' ')
            return result
        def relics(ids):
            window.relic_list.blockSignals(True)
            for index in range(window.relic_list.count()):
                item=window.relic_list.item(index)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in ids else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False)
        for stage,expected in ((1,30),(2,28),(3,27)):
            train('char_1048_orchd2',{'elite':2,'level':60,'potential':1,'trust':100,'module_id':'uniequip_002_orchd2','module_level':stage})
            window.skill.setCurrentIndex(window.skill.findData(1));window.timing_scenario.clear()
            result=calculate_result()
            assert result['estimate']['base_stats']['redeploy_seconds']==expected
            assert result['orchid_redeploy_reference']['actual_next_deployment_seconds'] is None
            checks.append({'scope':'actual_orchid_module_redeploy_reference','module_level':stage,'parameter_seconds':expected,'actual_next_deployment':None,'passed':True})
        train('char_2027_wang',{'elite':2,'level':60,'potential':1,'trust':100,'module_id':'uniequip_002_wang','module_level':2})
        window.skill.setCurrentIndex(window.skill.findData(1));window.timing_scenario.clear()
        result=calculate_result()
        token=next(t for t in result['relic_token_stats'] if t['id']=='token_10064_wang_stone1')
        assert token['deployment_cost']==2 and token['module_cost_reference']['cost_add']==-1
        checks.append({'scope':'actual_wang_module_token_cost_reference','cost':2,'module_level':2,'passed':True})
        window.select_operator('char_4202_haruka');window.skill.setCurrentIndex(window.skill.findData(1));window.timing_scenario.clear()
        window.window_seconds.setValue(10)
        bubble=next(widget for owner,key,_skills,widget in window.model_option_widgets if owner=='char_4202_haruka' and key=='bubble_bursts')
        bubble.setValue(1);relics([])
        base=calculate_result()['known_healing_subtotals']['window_healing']
        relics(['rogue_6_relic_legacy_81']);result=calculate_result()
        assert abs(result['known_healing_subtotals']['window_healing']-base*1.2)<1e-7
        assert result['total_healing'] is None
        checks.append({'scope':'actual_known_healing_subtotal_factor','base_subtotal':base,'final_subtotal':result['known_healing_subtotals']['window_healing'],'actual_healing':None,'passed':True})
        relics([])
        for op in ('char_1001_amiya2','char_1037_amiya3'):
            window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(2))
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                window.timing_scenario.clear();window.limit_window.setChecked(True)
                for horizon in (0,1):
                    window.window_seconds.setValue(horizon);result=calculate_result()
                    assert result['estimate']['skill']['window_seconds']==horizon
                    assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                    assert result['estimate']['skill']['duration_seconds'] is None
                    if op=='char_1037_amiya3':
                        assert result['total_healing']==0 if horizon==0 else result['total_healing'] is None
                    checks.append({'scope':'actual_amiya_phase_window_controls','operator':op,'mode':'frames' if use_frames else 'continuous','window':horizon,'actual_output':result['total_damage'],'actual_end':None,'passed':True})
        window.frame_timing.setChecked(True);window.window_seconds.setValue(10)
        base=calculate_result()['known_healing_subtotals']['window_healing']
        relics(['rogue_6_relic_legacy_81']);result=calculate_result()
        known=result['known_healing_subtotals']['window_healing']
        assert abs(known-base*1.2)<1e-7
        assert abs(result['amiya_phase_reference']['opening_healing_reference']-known)<1e-7
        assert result['total_healing'] is None
        checks.append({'scope':'actual_medical_amiya_opening_healing_factor','unscaled_opening_reference':base,'scaled_known_reference':known,'actual_healing':None,'passed':True})
        # New section46-50 checks use only actual window controls and read-only cultivation.
        from rouge.operator_engine import selected_talents
        from rouge.gnosis_module_reference import DOT_NAME
        window.timing_scenario.clear();window.limit_window.setChecked(True)
        window.window_seconds.setValue(10);window.healing_targets.setValue(1);relics([])
        for owner,key,_skills,widget in window.model_option_widgets:
            if owner=='char_4202_haruka' and key in ('bubble_bursts','levitate_triggers'):widget.setValue(0)
            if owner=='char_4202_haruka' and key=='haruka_repeat':widget.setChecked(False)
        cold=next(widget for owner,key,_skills,widget in window.model_option_widgets
                  if owner=='char_206_gnosis' and key=='cold_state')
        for stage in (1,2,3):
            train('char_206_gnosis',{'elite':2,'level':60,'potential':1,'trust':100,
                                   'module_id':'uniequip_004_gnosis','module_level':stage})
            cold.setValue(1)
            for skill in (1,2,3):
                window.skill.setCurrentIndex(window.skill.findData(skill))
                for use_frames in (True,False):
                    window.frame_timing.setChecked(use_frames)
                    for horizon in (0,1):
                        window.window_seconds.setValue(horizon);result=calculate_result()
                        ref=result['gnosis_isw_a_reference']
                        assert ref['module_id']=='uniequip_004_gnosis' and ref['module_level']==stage
                        assert ref['original_talent']['blackboard']=={'cold':1,'damage_scale_cold':1.25,'damage_scale_freeze':1.5}
                        assert ref['original_talent']['prefab_key']=='1'
                        assert ref['original_talent']['talent_index']==0
                        assert not ref['original_talent']['module_coexistence_verified']
                        assert ref['dot_parameters']=={'atk_scale':.5,'interval':.5}
                        assert not ref['native_ability_attachment_verified'] and not ref['events_scheduled']
                        for key in ('actual_tick_count','actual_tick_times_seconds','actual_first_tick_seconds'):
                            assert ref[key] is None
                        records={r['prefab_key']:r for r in ref['module_records'] if r['kind']=='talent'}
                        if stage in (2,3):
                            assert set(records)=={'#','1','10_root','11_root'}
                            assert records['#']['blackboard']=={}
                            assert records['10_root']['blackboard']=={'cold':stage+1,'delay':.8}
                            assert records['11_root']['blackboard']=={'cold':1}
                            expected={'damage_scale_cold':1.25,'multi':2,'add':0,'max':1.5} if stage==2 else {'damage_scale_cold':1.3,'multi':2,'add':.05,'max':1.8}
                            assert records['1']['blackboard']==expected
                            assert records['10_root']['hidden'] and records['11_root']['hidden']
                            assert all(not r['attachment_verified'] for r in records.values())
                        else:assert records=={}
                        dot=next(c for c in result['components'] if c['name']==DOT_NAME)
                        assert dot['attack_scale_parameter']==.5 and dot['tick_interval_parameter_seconds']==.5
                        assert 'times_seconds' not in dot and dot['hits']==0
                        assert result['total_damage']==0 if horizon==0 else result['total_damage'] is None
                        assert ref['actual_dot_damage']==0 if horizon==0 else ref['actual_dot_damage'] is None
                        assert ref['source_possible']['window']==bool(horizon)
                        assert '灵知ISW-A' in window.damage_text.toPlainText()
                        checks.append({'scope':'actual_gnosis_isw_a_module_cultivation_and_unknown_boundaries',
                            'stage':stage,'skill':skill,'mode':'frames' if use_frames else 'continuous',
                            'window':horizon,'actual_damage':result['total_damage'],'dot_parameters':ref['dot_parameters'],
                            'original_talent':ref['original_talent'],'module_records':ref['module_records'],'passed':True})
        # Explicitly reset all Haruka manual sources left by the earlier suite.
        for owner,key,_skills,widget in window.model_option_widgets:
            if owner=='char_4202_haruka' and key in ('bubble_bursts','levitate_triggers'):widget.setValue(0)
            if owner=='char_4202_haruka' and key=='haruka_repeat':widget.setChecked(False)
        window.timing_scenario.clear();window.window_seconds.setValue(10)
        for stage in (1,2,3):
            train('char_4202_haruka',{'elite':2,'level':60,'potential':1,'trust':100,
                                    'module_id':'uniequip_002_haruka','module_level':stage})
            for skill in (1,3):
                window.skill.setCurrentIndex(window.skill.findData(skill))
                assert window.healing_targets.maximum()==2
                for use_frames in (True,False):
                    window.frame_timing.setChecked(use_frames)
                    window.healing_targets.setValue(1);one=calculate_result()
                    window.healing_targets.setValue(2);two=calculate_result()
                    assert one['total_healing']>0 and abs(two['total_healing']-one['total_healing']*2)<1e-7
                    assert two['haruka_healing_reference']['actual_target_count'] is None
                    assert not two['haruka_healing_reference']['native_attachment_verified']
                    checks.append({'scope':'actual_haruka_module_s1_s3_two_recipient_reference',
                        'stage':stage,'skill':skill,'mode':'frames' if use_frames else 'continuous',
                        'widget_maximum':2,'one_reference':one['total_healing'],'two_reference':two['total_healing'],'passed':True})
            window.skill.setCurrentIndex(window.skill.findData(2))
            assert window.skill_rank_value()==10 and window.healing_targets.maximum()==3
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                window.healing_targets.setValue(3);result=calculate_result()
                assert result['total_healing'] is None and result['total_damage'] is None
                assert result['known_healing_subtotals']['window_healing']>0
                assert result['haruka_healing_reference']['additional_conditional_targets']==1
                assert result['haruka_healing_reference']['skill_target_add_parameter']==1
                checks.append({'scope':'actual_haruka_rank10_s2_extra_conditional_recipient',
                    'stage':stage,'mode':'frames' if use_frames else 'continuous','widget_maximum':3,
                    'actual_healing':None,'known_healing':result['known_healing_subtotals']['window_healing'],'passed':True})
        for module_id,module_level,expected in (('uniequip_002_haruka',1,2),(None,0,1)):
            train('char_4202_haruka',{'elite':2,'level':60,'potential':1,'trust':100,
                'module_id':module_id,'module_level':module_level},ranks={'1':4,'2':4,'3':4})
            window.skill.setCurrentIndex(window.skill.findData(2))
            window.update_skill_options();app.processEvents()
            assert window.skill_rank_value()==4 and window.healing_targets.maximum()==expected
            window.healing_targets.setValue(expected);result=calculate_result()
            assert window.damage_result['scenario']['skill_rank']==4
            assert result['haruka_healing_reference']['skill_target_add_parameter']==0
            assert result['haruka_healing_reference']['conditional_target_limit_reference']==expected
            checks.append({'scope':'actual_haruka_rank4_readonly_training_input_limit',
                'module_id':module_id,'module_level':module_level,'read_skill_rank':4,
                'widget_maximum':expected,'passed':True})
        low_cost=next(widget for owner,key,_skills,widget in window.model_option_widgets
                      if owner=='char_298_susuro' and key=='low_cost_healing_target')
        from PySide6.QtWidgets import QCheckBox
        assert isinstance(low_cost,QCheckBox)
        train('char_298_susuro',{'elite':2,'level':60,'potential':1,'trust':100,
                               'module_id':None,'module_level':0})
        window.healing_targets.setValue(1);window.window_seconds.setValue(10)
        window.timing_scenario.clear();relics([])
        for skill in (1,2):
            window.skill.setCurrentIndex(window.skill.findData(skill))
            for use_frames in (True,False):
                window.frame_timing.setChecked(use_frames)
                low_cost.setChecked(False);plain=calculate_result()
                low_cost.setChecked(True);qualified=calculate_result()
                assert window.damage_result['scenario']['low_cost_healing_target'] is True
                talents,_=selected_talents(module.catalog()['operators']['char_298_susuro'],window.damage_result['scenario'])
                factor=next(t['values']['heal_scale'] for t in talents if t['name']=='微创治疗')
                assert abs(qualified['estimate']['skill']['cycle_healing']-plain['estimate']['skill']['cycle_healing']*factor)<1e-7
                for key in ('initial_seconds','recharge_seconds','cycle_seconds','duration_seconds','sp_recovery_per_second'):
                    assert qualified['estimate']['skill'][key]==plain['estimate']['skill'][key]
                checks.append({'scope':'actual_susuro_low_cost_checkbox_whole_cycle_factor',
                    'skill':skill,'mode':'frames' if use_frames else 'continuous','selected_factor':factor,
                    'plain_cycle_healing':plain['estimate']['skill']['cycle_healing'],
                    'qualified_cycle_healing':qualified['estimate']['skill']['cycle_healing'],
                    'natural_sp_clocks_unchanged':True,'passed':True})
        window.select_operator('char_1037_amiya3');window.skill.setCurrentIndex(window.skill.findData(2))
        opening=next(widget for owner,key,_skills,widget in window.model_option_widgets
                     if owner=='char_1037_amiya3' and key=='amiya_hit_targets')
        assert opening.minimum()==1
        calculate_result()
        assert window.rank.text() and window.skill_rank_value()==window.damage_result['scenario']['skill_rank']
        checks.append({'scope':'actual_medical_amiya_public_minimum_and_readonly_rank','minimum':1,'passed':True})
        # Final visible screenshot scenario demonstrates the restored explanation.
        train('char_298_susuro',{'elite':2,'level':60,'potential':1,'trust':100,'module_id':None,'module_level':0})
        window.skill.setCurrentIndex(window.skill.findData(1));window.healing_targets.setValue(1)
        low_cost.setChecked(False);relics([]);window.limit_window.setChecked(True)
        window.window_seconds.setValue(10);window.frame_timing.setChecked(False)
        window.timing_scenario.setPlainText(json.dumps({'target_disappears_seconds':0}))
        result=calculate_result()
        assert result['total_damage']==0 and result['total_healing']>0
        assert window.damage_result['scenario']['relic_ids']==[]
        assert window.damage_result['scenario']['timing_mode']=='continuous'
        assert '真实友方获取时钟未核验' in window.damage_text.toPlainText()
        checks.append({'scope':'actual_final_visible_friendly_scope_explanation','operator':'char_298_susuro',
            'mode':'continuous','window_seconds':10,'enemy_lifetime_seconds':0,'relic_ids':[],
            'report_contains_friendly_clock_unknown':True,'passed':True})
        receipt['manual_token_attribute_scope']='Public API inputs have related regression coverage; actual UI has no manual all_units effects control'
        receipt['deferred_probes']=[]
        receipt['resolved_problem']={'problem':'friendly scope report explanation was deferred after three historical attempts',
            'independent_diagnosis_source':str(diagnosis_path),'independent_diagnosis_sha256':hashlib.sha256(diagnosis_bytes).hexdigest(),
            'historical_evidence_preserved':'verification/full-045/wine-ui.json; original three failed attempts remain unchanged',
            'prior_tmp_diagnosis':'/tmp/p2-draft50/independent-diagnosis.json unavailable after machine restart; reconstructed from persistent historical receipt',
            'recovery':'Both actual report modes now assert the explicit friendly acquisition clock remains unknown',
            'current_available_probe_passed':True}
        receipt['complete_ui_validation']=False
        receipt['window_scenario']=window.damage_result['scenario']
        receipt['window_result']=window.damage_result['result']
        window.centralWidget().setCurrentIndex(1);app.processEvents()
        calculate_button=next(b for b in window.findChildren(QPushButton) if b.text()=='计算属性与技能预估')
        calculate_button.click();app.processEvents()
        assert window.damage_result and window.damage_text.toPlainText()
        checks.append({'scope':'actual_calculate_button_click','passed':True})
        window.centralWidget().setCurrentIndex(1);app.processEvents()
        from PySide6.QtGui import QTextCursor
        window.damage_text.moveCursor(QTextCursor.MoveOperation.Start)
        assert window.damage_text.find('真实友方获取时钟未核验')
        window.damage_text.ensureCursorVisible();app.processEvents()
        checks.append({'scope':'actual_friendly_scope_text_scrolled_visible_for_screenshot','passed':True})
        screenshot=OUT/'wine-window-050.png'
        assert window.grab().save(str(screenshot))
        receipt['window_screenshot']='wine-window-050.png'
        assert not isolated.joinpath('chat').exists()
        assert not window.auto.isChecked() and window.capture.target is None
        assert not window.desktop.process
        checks.append({'scope':'no_external_operations','game_captures':0,'chat_requests':0,'temporary_state':True})
        window.close();app.processEvents();window=None
    receipt['passed']=True
    receipt['complete_ui_validation']=True
    receipt['complete_ui_validation_scope']='Only this available actual Wine Qt suite; no native Windows, game capture, private replay or desktop integration certification'
except BaseException as error:
    receipt['complete_ui_validation']=False
    receipt['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
finally:
    if window is not None:
        window.close()
        if app is not None:app.processEvents()
    receipt['elapsed_seconds']=round(time.perf_counter()-started,3)
    after=source_hashes();drift=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]
    receipt['source_sha256']=before;receipt['source_sha256_after']=after;receipt['source_drift']=drift
    if drift:receipt['passed']=False;receipt['complete_ui_validation']=False
    (OUT/'wine-ui-050.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
    sys.exit(0 if receipt['passed'] else 1)
