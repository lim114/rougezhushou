"""Temporary Qt state only: finite speed, native fees and two-book counts."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication,Qt
from rouge.reporting import format_report


def source_hashes():
    files=[*(ROOT/'rouge').rglob('*.py'),*(ROOT/'rouge/data').rglob('*.json'),
           Path(__file__),ROOT/'scripts/verify_relic_ui_025.py']
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files))}


def main():
    started=time.perf_counter();checks=[];before=source_hashes()
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda path,callback:backend(p/'chat',callback)
        app=QApplication([]);window=OfflineWindow()
        def select(op,skill,ids,context=None):
            window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(skill))
            window.relic_list.blockSignals(True)
            for i in range(window.relic_list.count()):
                item=window.relic_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in ids else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False)
            window.relic_context.setPlainText(json.dumps(context or {}));window.calculate()
            assert window.damage_result,window.damage_text.toPlainText()
            return window.damage_result['result'],window.damage_text.toPlainText()
        try:
            window.auto_relics.setChecked(False)
            assert window.windowTitle()=='黑流树海助手 0.70 · 识别与计算测试版'
            r,text=select('mechanist',3,{'rogue_6_relic_legacy_16'})
            assert abs(r['attack']-2720.8)<1e-7,r['attack']
            checks.append({'scope':'rune_before_skill_and_integer_writer','attack':r['attack']})
            r,text=select('kaltsit',2,{'rogue_6_relic_legacy_90','rogue_6_relic_legacy_14'})
            stats=r['estimate']['base_stats']
            assert stats['hp']==3975 and abs(stats['defense']-573.75)<1e-7,stats
            checks.append({'scope':'hp_defense_rune_before_talent','hp':stats['hp'],'defense':stats['defense']})
            for ids,cost in (({'rogue_6_relic_fight_11'},12),({'rogue_6_relic_book_3'},5),
                ({'rogue_6_relic_fight_11','rogue_6_relic_book_3'},3)):
                r,text=select('mechanist',3,ids)
                assert r['deployment_cost']==cost,(ids,r.get('deployment_reference'))
                assert not any('实际部署扣费' in m['label'] for s in r['report']['sections'] for m in s['metrics'])
                assert '实际部署扣费：未知' not in text
                checks.append({'scope':'fee','items':sorted(ids),'cost':cost})
            for ids,bonus in (({'rogue_6_relic_legacy_105'},40),({'rogue_6_relic_legacy_106'},70),
                ({'rogue_6_relic_legacy_105','rogue_6_relic_legacy_106'},110)):
                r,text=select('mechanist',1,ids)
                ref=r['deployment_buff_reference']
                assert sum(s['attack_speed_addition'] for s in ref['spans'])==bonus
                assert r['estimate']['base_stats']['attack_speed']==ref['permanent_attack_speed']+bonus
                assert '部署限时攻速' in text
                assert ref['live_state_verified'] is False
                checks.append({'scope':'finite_speed','bonus':bonus})
            r,text=select('char_1041_angel2',3,{'rogue_6_relic_legacy_139','rogue_6_relic_legacy_140'})
            assert r['estimate']['skill']['hit_counts']['技能攻击']==95
            assert r['ammo_refill_reference']['count_order_invariant']
            assert not r['ammo_refill_reference']['order_verified']
            proof=r['relic_resolution']['rules'][0]['ammo_parameters']['native_parameter_proof_sha256']
            assert proof not in text and proof in format_report(r,technical=True)
            checks.append({'scope':'two_books','full_cast_hits':95})
            r,text=select('mechanist',1,set())
            assert '部署限时攻速' not in text and '藏品补弹参考' not in text
            checks.append({'scope':'absent_sections'})
            bed='rogue_6_relic_cargo_3'
            for ids,context,expected in (({bed},{'empty_slots':4},17),
                ({bed,'rogue_6_relic_fight_11'},{'empty_slots':4},6),
                ({bed,'rogue_6_relic_book_3'},{'empty_slots':4},0),
                ({bed,'rogue_6_relic_fight_11','rogue_6_relic_book_3'},{'empty_slots':4},0),
                ({bed,'rogue_6_relic_fight_11'},{'empty_slots':3},12),
                ({bed},{},None),
                ({bed,'rogue_6_relic_fight_11'},{},None)):
                r,text=select('mechanist',3,ids,context)
                assert r['deployment_cost']==expected,(ids,context,r['deployment_cost'])
                assert r['deployment_reference']['cost']['actual_cost'] is None
                if expected is None:assert '未知' in text
                checks.append({'scope':'empty_bed_offline_cost','items':sorted(ids),
                    'condition':context,'expected_cost':expected,'actual_deployment_asserted':False})
            r,text=select('mechanist',3,{'rogue_6_relic_fight_22'})
            for name in ('凋亡','灼燃','神经','侵蚀'):
                assert '河谷祭祈 · '+name+'机制资料' in text
            assert '实际追加跳数与完整总伤仍未知' in text
            checks.append({'scope':'held_river_four_element_reference','actual_extra_damage_added':False})
            r,text=select('mechanist',3,set())
            assert '河谷祭祈' not in text
            checks.append({'scope':'unheld_river_reference_absent'})
            from unittest.mock import patch
            from rouge.damage import _prepare_damage, _evaluate_damage
            from rouge.relic_attributes import apply_attribute_runes
            for op,skill,ordinary,rune,ids,base,active in (
                ('kaltsit',1,-100,None,set(),20,50),
                ('kaltsit',2,30,-200,set(),50,50),
                ('mechanist',1,-100,None,{'rogue_6_relic_legacy_105'},40,20),
                ('char_1041_angel2',3,-1000,None,set(),20,20)):
                def boundary_scenario(scenario):
                    prepared=_prepare_damage(scenario)
                    current,attributes,_,_=prepared
                    if rune is not None:
                        attributes.update(apply_attribute_runes(attributes,[{'kind':'attack_speed','value':rune,
                            'attribute_layer':'relic_rune','formula_item':'ADDITION'}]))
                        current['_attribute_attack_speed']=attributes['attack_speed']
                    current['effects'].append({'kind':'attack_speed','value':ordinary,'_verified_rule':True})
                    return _evaluate_damage(prepared)
                with patch.object(module,'calculate_damage',side_effect=boundary_scenario):
                    r,text=select(op,skill,ids)
                assert r['estimate']['base_stats']['attack_speed_reference']==base
                assert r['estimate']['skill']['skill_attack_speed_reference']==active,(op,skill,r['estimate']['skill']['skill_attack_speed_reference'],active)
                assert '攻速' in text and text==format_report(r,technical=window.damage_technical.isChecked())
                checks.append({'scope':'default_attack_speed_bounds','operator':op,'base':base,'skill':active,
                    'input':'synthetic_resolved_modifier','live_game_panel_verified':False})
            for op,skill,ids,expected in (
                ('kaltsit',1,{'rogue_6_relic_legacy_74'},1.3),
                ('silverash',1,{'rogue_6_relic_legacy_74'},1.0),
                ('char_2025_shu',3,{'rogue_6_relic_legacy_74'},1.0),
                ('kaltsit',1,{'rogue_6_relic_legacy_'+str(n) for n in (2,3,4,74)},2.35)):
                r,text=select(op,skill,ids)
                assert abs(r['estimate']['skill']['sp_recovery_per_second']-expected)<1e-8
                assert '技力' in text and text==format_report(r,technical=window.damage_technical.isChecked())
                checks.append({'scope':'medical_sp_selector','operator':op,'skill':skill,
                    'natural_sp_rate':expected,'input':'temporary_manual_relic_selection'})
            window.use_run_training.setChecked(False)
            op='char_110_deepcl'
            for stage,pct in ((1,0),(2,.1),(3,.15)):
                window.operator_observations[op]={'id':op,'scope':'account',
                    'fields':{'elite':2,'level':70,'trust':100,'potential':1,
                        'module_id':'uniequip_002_deepcl','module_level':stage},
                    'skill_ranks':{'1':10,'2':10}}
                window.select_operator(op);window.update_operator()
                for skill in (1,2):
                    for ids in (set(),{'rogue_6_relic_legacy_134'},
                                {'rogue_6_relic_legacy_134','rogue_6_relic_legacy_91'}):
                        r,text=select(op,skill,ids)
                        t=next(t for t in r['relic_token_stats'] if t['id']=='token_10001_deepcl_tentac')
                        expected=(2621 if ids else 2016)*(1+pct)
                        assert abs(t['hp']-expected)<1e-7,(stage,skill,ids,t['hp'],expected)
                        assert '仅模组的生命参考' not in text and '叠加层尚未核验' not in text
                        if len(ids)==2:
                            assert abs(t['regeneration_rate']-expected*.01)<1e-7
                            assert '藏品常态生命回复：未知' not in text
                        assert text==format_report(r,technical=window.damage_technical.isChecked())
                        checks.append({'scope':'summon_module_hp_composition','stage':stage,'skill':skill,
                            'relics':sorted(ids),'expected_hp':expected,'input':'synthetic_observed_training'})
            # Actual form controls, temporary observed cultivation, no capture.
            control=next(w for owner,key,skills,w in window.model_option_widgets if owner==op and key=='summon_count')
            ids={'rogue_6_relic_legacy_134','rogue_6_relic_legacy_91'}
            for stage in (1,2,3):
                window.operator_observations[op]['fields']['module_level']=stage
                window.update_operator()
                for skill in (1,2):
                    r,text=select(op,skill,ids)
                    assert control.minimum()==0 and control.maximum()==7
                    control.setValue(1);window.calculate();one=window.damage_result['result']
                    control.setValue(7);window.calculate();seven=window.damage_result['result']
                    part=lambda r:next(c for c in r['components'] if c['name']=='触手')
                    assert part(seven)['total']==part(one)['total']*7
                    text=window.damage_text.toPlainText()
                    assert '触手同时在场上限：7' in text and '参与测算触手数（局外假设）：7' in text
                    assert '最多4个' not in text and '实际同时在场限制未核验' not in text
                    checks.append({'scope':'summon_concurrent_count','stage':stage,'skill':skill,
                        'selected_count':7,'input':'synthetic_observed_training','live_game_panel_verified':False})
            select(op,1,ids);control.setValue(0);window.calculate()
            r=window.damage_result['result'];assert part(r)['total']==0
            checks.append({'scope':'summon_zero_count','selected_count':0})
            control.setValue(7)
            for level,cap in ((39,4),(40,7)):
                window.level.setValue(level);window.calculate()
                assert control.maximum()==cap and control.value()==4
                assert window.damage_result,window.damage_text.toPlainText()
                checks.append({'scope':'summon_module_unlock','level':level,'cap':cap,
                    'selected_count':control.value(),'automatic_count_increase':False})
            window.level.setValue(70);control.setValue(7)
            for elite,cap in ((2,4),(1,3),(0,2)):
                fields=window.operator_observations[op]['fields']
                fields.update(elite=elite,level=(70,60,45)[2-elite],module_id=None,module_level=0)
                window.operator_observations[op]['skill_ranks']={'1':7,'2':7}
                window.update_operator();window.calculate()
                assert control.maximum()==cap and control.value()==cap
                assert window.damage_result,window.damage_text.toPlainText()
                checks.append({'scope':'summon_cultivation_cap','elite':elite,'cap':cap,
                    'selected_count':control.value()})
            r,text=select('mechanist',1,set())
            assert control.isHidden()
            assert '触手持有上限' not in text and '再计入模组天赋' not in text and '触手同时在场上限' not in text
            checks.append({'scope':'summon_controls_absent_on_other_operator'})
            window.operator_observations['char_1042_phatm2']={'id':'char_1042_phatm2','scope':'account',
                'fields':{'elite':2,'level':90,'trust':100,'potential':1,'module_id':None,'module_level':0},
                'skill_ranks':{'1':10,'2':10,'3':10}}
            window.limit_window.setChecked(True)
            for seconds,hits,total in ((.5,0,0),(.51,1,795),(.9,1,795),(.91,2,1590)):
                window.window_seconds.setValue(seconds)
                r,text=select('char_1042_phatm2',1,set())
                assert r['components'][0]['hits']==hits
                assert r['total_damage']==total,(seconds,r['attack'],r['total_damage'])
                assert r['estimate']['skill']['cycle_seconds'] is None
                assert '暗夜回声 · 两段动作参考' in text and '两段相对等待：12' in text
                assert r['timing']['streams'][0]['multi_melee_reference']['relative_wait_frames']==12
                assert '完整结束' in text and '预计回转：实际结束' in text
                assert text==format_report(r,technical=window.damage_technical.isChecked())
                checks.append({'scope':'wine_two_hit_window','seconds':seconds,'hits':hits,
                    'total':total,'actual_frame_measurement':False})
            window.timing_scenario.setPlainText('{"interrupt_windows":[[0.3,0.8]]}')
            window.calculate()
            assert '移动/打断机制尚未核验' in window.damage_text.toPlainText()
            checks.append({'scope':'wine_unverified_interrupt_rejected'})
            window.timing_scenario.setPlainText('');window.limit_window.setChecked(False)
            r,text=select('char_1042_phatm2',2,set())
            assert '两段动作参考' not in text
            checks.append({'scope':'wine_s1_section_absent_on_s2'})
            r,text=select('mechanist',1,set())
            assert '两段动作参考' not in text
            checks.append({'scope':'wine_s1_section_absent_on_other_operator'})
            assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
            assert window.run.state['history']==[] and window.run.state['config']=={}
            after=source_hashes()
            changed=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]
            assert not changed,changed
            receipt={'version':'0.70.0','passed':True,'checks':checks,'game_actions':0,'chat_requests':0,
                'private_data_isolated':True,'elapsed_seconds':time.perf_counter()-started,
                'source_sha256':before,'source_sha256_after':after,'source_drift':changed,'runner_sealed':True}
            with (ROOT/'NATIVE_UI_0.70_VERIFICATION.json').open('x',encoding='utf-8') as stream:
                json.dump(receipt,stream,ensure_ascii=False,indent=2)
            print(json.dumps({'passed':True,'checks':len(checks),'elapsed_seconds':receipt['elapsed_seconds']}),flush=True)
        finally:window.close();app.processEvents()


if __name__=='__main__':main()
