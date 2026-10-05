"""Isolated 87-skill panels, book references and prior preview wiring."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile,time
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication,Qt
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFontDatabase,QFont

RIVER='rogue_6_relic_fight_22'
WINES=('rogue_6_relic_legacy_95','rogue_6_relic_legacy_97')
BOOKS=('rogue_6_relic_legacy_139','rogue_6_relic_legacy_140')


def main():
    started=time.perf_counter()
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda _path,callback:backend(p/'chat',callback)
        app=QApplication([])
        # Windows' offscreen plugin exposes no installed families. Load a CJK
        # font for readable evidence; the native desktop font engine is separate.
        font_id=QFontDatabase.addApplicationFont(str(Path(os.environ['WINDIR'])/'Fonts/msyh.ttc'))
        assert font_id>=0
        app.setFont(QFont(QFontDatabase.applicationFontFamilies(font_id)[0],9))
        window=OfflineWindow()
        def select(ids):
            window.relic_list.blockSignals(True)
            for i in range(window.relic_list.count()):
                item=window.relic_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in ids else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False);window.calculate()
            assert window.damage_result,window.damage_text.toPlainText()
        skills=panels=range_panels=0
        try:
            assert not window.auto.isChecked() and window.capture.target is None
            assert not hasattr(window,'received_sp_scenario')
            window.auto_relics.setChecked(False)
            for op,profile in module.catalog()['operators'].items():
                for skill in range(1,len(profile['skills'])+1):
                    window.operator.setCurrentIndex(window.operator.findData(op))
                    window.skill.setCurrentIndex(window.skill.findData(skill))
                    for ids in (set(),{RIVER},{WINES[0]},{WINES[1]}):
                        select(ids);r=window.damage_result['result'];text=window.damage_text.toPlainText()
                        fixed=op=='mechanist' and skill==3
                        assert ('本体固定落地延迟' in text)==fixed,(op,skill,ids)
                        if fixed:
                            assert '工程学十字星本体弹道按资料固定延迟0.8秒落地' in text
                            assert r['timing']['streams'][0]['fixed_impact_delay_frames']==24
                            assert not r['timing']['streams'][0]['exact_binding']
                        secondary=op=='char_1042_phatm2' and skill==3
                        assert ('空剧场 · 持续损伤待核验' in text)==secondary,(op,skill,ids)
                        if secondary:
                            assert '当前情景损伤爆发次数：未知' in text
                            assert r['estimate']['skill']['total_damage'] is None
                            assert r['estimate']['skill']['cycle_damage'] is None
                        assert ('河谷祭祈 · 神经爆发参考' in text)==bool(r.get('neural_relic_reference'))
                        assert ('已建模伤害小计' in text)==bool(r.get('known_damage_subtotals'))
                        if 'phase_estimate' in r['relic_resolution']:
                            assert ids in ({WINES[0]},{WINES[1]})
                            assert not r['relic_resolution']['phase_estimate']['verified_phase']
                            assert '相位范围' in text
                            range_panels+=1
                        assert not window.damage_form.isRowVisible(window.relic_context)
                        for owner,key,supported,widget in window.model_option_widgets:
                            assert window.damage_form.isRowVisible(widget)==(owner==op and skill in supported),(op,skill,key)
                        panels+=1
                    skills+=1
            assert skills==87 and panels==348
            book_panels=refill_panels=unknown_panels=combo_panels=0
            for op,profile in module.catalog()['operators'].items():
                for skill,entry in enumerate(profile['skills'],1):
                    window.operator.setCurrentIndex(window.operator.findData(op))
                    window.skill.setCurrentIndex(window.skill.findData(skill))
                    for rid in BOOKS:
                        select({rid});r=window.damage_result['result'];text=window.damage_text.toPlainText()
                        reference=next((b for b in r['report']['sections'] if b['id']=='ammo_refill_reference'),None)
                        known=(op,skill) in (('kaltsit',2),('mechanist',1),('char_1035_wisdel',3),('char_1041_angel2',1)) or (
                            (op,skill)==('char_1041_angel2',3) and rid==BOOKS[1])
                        assert bool(reference)==known,(op,skill,rid)
                        assert ('藏品补弹参考' in text)==known,(op,skill,rid)
                        assert window.damage_text.isReadOnly()
                        if reference:
                            assert '单次补充额度' in text and '检查相位' in text
                            assert '实际已补回' not in '\n'.join(m['label'] for m in reference['metrics'])
                            if op=='mechanist':assert '不能触发补弹' in text and r['relic_resolution']['complete']
                            refill_panels+=1
                        elif entry['levels'][-1]['duration_type']=='AMMO':
                            assert '单次技能总伤：未知' in text,(op,skill,rid,text)
                            # Manually spent board ammo is already labelled
                            # nonrepeatable; it must not gain a fake cycle.
                            assert r['estimate']['skill']['cycle_seconds'] is None
                            assert '预计回转：未知' in text or '预计回转：不适用' in text
                            assert r['estimate']['skill']['cycle_dps'] is None
                            unknown_panels+=1
                        book_panels+=1
                    if entry['levels'][-1]['duration_type']=='AMMO':
                        select(set(BOOKS));text=window.damage_text.toPlainText()
                        assert '获取先后未确认' in text and '单次技能总伤：未知' in text
                        assert '藏品补弹参考' not in text
                        combo_panels+=1
            assert book_panels==174 and refill_panels==9 and unknown_panels==9 and combo_panels==9
            window.operator.setCurrentIndex(window.operator.findData('kaltsit'))
            window.skill.setCurrentIndex(window.skill.findData(2))
            with patch('rouge.ammo_reference.refill_before_empty_is_safe',return_value=False):
                select({BOOKS[0]})
            assert '耗尽前检查窗口不足' in window.damage_text.toPlainText()
            assert '单次技能总治疗：未知' in window.damage_text.toPlainText()
            select({BOOKS[0]});app.processEvents()
            snapshot=ROOT/'.cache/refresh-045/refill-report.png'
            window.centralWidget().setCurrentIndex(1)
            window.damage_text.moveCursor(window.damage_text.textCursor().MoveOperation.Start)
            assert window.damage_text.find('【藏品补弹参考】')
            window.show();app.processEvents();assert window.grab().save(str(snapshot),'PNG')
            module_panels=0
            op='char_110_deepcl'
            window.use_run_training.setChecked(False)
            for stage in (1,2,3):
                window.operator_observations[op]={'id':op,'scope':'account',
                    'fields':{'elite':2,'level':70,'trust':100,'potential':1,
                        'module_id':'uniequip_002_deepcl','module_level':stage},
                    'skill_ranks':{'1':10,'2':10}}
                window.operator.setCurrentIndex(window.operator.findData(op));window.update_operator()
                for skill in (1,2):
                    window.skill.setCurrentIndex(window.skill.findData(skill))
                    for ids in (set(),{'rogue_6_relic_legacy_134'},
                                {'rogue_6_relic_legacy_134','rogue_6_relic_legacy_91'}):
                        select(ids);r=window.damage_result['result'];text=window.damage_text.toPlainText()
                        assert window.damage_result['scenario']['module_level']==stage
                        assert window.damage_result['scenario']['level']==70
                        assert '触手持有上限：7' in text
                        assert '参与测算触手数（局外假设）' in text
                        t=r['relic_token_stats'][0]
                        pending=stage>1 and bool(ids)
                        assert (t['hp'] is None)==pending
                        assert ('仅模组的生命参考' in text)==pending
                        if pending and len(ids)==2:assert '藏品常态生命回复：未知' in text
                        assert isinstance(window.attack,QLabel) and window.damage_text.isReadOnly()
                        module_panels+=1
            assert module_panels==18
            window.operator.setCurrentIndex(window.operator.findData('mechanist'))
            window.skill.setCurrentIndex(window.skill.findData(3));select(set())
            assert '触手持有上限' not in window.damage_text.toPlainText()
            assert window.run.state['config']=={} and window.run.state['history']==[]
            assert not window.desktop.process and not window.auto.isChecked()
            receipt={'version':'0.45.0','passed':True,'verified_at':time.time(),'skills_checked':skills,
                'panel_scenarios':panels,'wine_phase_panels':range_panels,
                'book_panels':book_panels,'refill_reference_panels':refill_panels,
                'book_unknown_panels':unknown_panels,'book_combination_panels':combo_panels,
                'book_polling_race_guard_visible':True,
                'refill_screenshot':str(snapshot.relative_to(ROOT)),
                'refill_screenshot_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),
                'synthetic_module_panels':module_panels,'module_hp_unknown_guard_visible':True,
                'only_readonly_module_metrics':True,'synthetic_cultivation_only':True,
                'unrelated_sections_hidden':True,'native_options_appropriate':True,
                'fixed_delay_only_on_supported_skill':True,'fixed_delay_panels':4,
                'event_input_absent':True,'private_data_isolated':True,'elapsed_seconds':time.perf_counter()-started,
                'game_actions':0,'chat_requests':0,'source_hashes':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
                    for n in ('rouge/app.py','rouge/damage.py','rouge/timing.py','rouge/reporting.py',
                        'rouge/data/skill-impact-delays.json','scripts/verify_skill_ui_045.py',
                        'rouge/relics.py','rouge/relic_events.py','rouge/ammo_reference.py','rouge/operator_engine.py',
                        'rouge/data/ammo-refill-reference.json','rouge/summons.py','rouge/data/summon-module-rules.json')}}
            receipt['source_hashes']['rouge/relic_recognition.py']=hashlib.sha256((ROOT/'rouge/relic_recognition.py').read_bytes()).hexdigest()
            receipt['source_hashes'].update({n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ('rouge/battle_preview.py','rouge/battle_view.py','rouge/spawn_reference.py','rouge/data/battle-previews.json','scripts/verify_battle_widgets_045.py')})
            receipt['source_hashes'].update({n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ('rouge/enemy_skills.py','rouge/data/enemy-skill-references.json')})
            (ROOT/'SKILL_UI_0.45_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps({k:receipt[k] for k in ('passed','skills_checked','panel_scenarios',
                'wine_phase_panels','private_data_isolated','elapsed_seconds')}),flush=True)
        finally:window.close();app.processEvents()


if __name__=='__main__':main()
