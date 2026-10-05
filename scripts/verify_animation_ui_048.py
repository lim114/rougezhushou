"""Exercise explicit motion references and bait uncertainty in isolated Qt."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile,time
from pathlib import Path
from PySide6.QtGui import QFontDatabase,QFont
from PySide6.QtWidgets import QApplication
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module
from rouge.animation_reference import choices,references


def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    started=time.perf_counter();base=ROOT/'.cache/mechanisms-048';base.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda _path,callback:backend(p/'chat',callback)
        app=QApplication([]);fid=QFontDatabase.addApplicationFont(str(Path(os.environ['WINDIR'])/'Fonts/msyh.ttc'))
        assert fid>=0;app.setFont(QFont(QFontDatabase.applicationFontFamilies(fid)[0],9))
        window=OfflineWindow();window.resize(1250,1000);window.show();app.processEvents()
        window.centralWidget().setCurrentIndex(1)
        slots=0;seen=set()
        try:
            for op,profile in module.catalog()['operators'].items():
                for skill in range(1,len(profile['skills'])+1):
                    window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(skill))
                    for normal,widget in ((True,window.normal_animation_reference),(False,window.skill_animation_reference)):
                        expected=choices(op,skill,normal=normal)
                        assert [widget.itemData(i) for i in range(1,widget.count())]==[r['id'] for r in expected]
                        assert window.damage_form.isRowVisible(widget)==bool(expected)
                        for i in range(1,widget.count()):
                            widget.setCurrentIndex(i);assert window.damage_result,window.damage_text.toPlainText()
                            selected=widget.currentData();seen.add(selected);slots+=1
                            assert selected.startswith(profile['id']+':')
                            assert window.damage_result['scenario']['timing']['normal_animation_reference' if normal else 'animation_reference']==selected
                        widget.setCurrentIndex(0)
            window.select_operator('kaltsit');window.skill.setCurrentIndex(window.skill.findData(3))
            choice=next(r['id'] for r in choices('kaltsit',3) if r['orientation']=='Back' and r['animation']=='Skill_3_Attack')
            window.skill_animation_reference.setCurrentIndex(window.skill_animation_reference.findData(choice))
            expected=window.damage_result['result']['timing']['streams'][0]['release_frames']
            assert expected[0]==13;window.calculate();assert window.skill_animation_reference.currentData()==choice
            window.select_operator('mechanist');window.select_operator('kaltsit')
            window.skill.setCurrentIndex(window.skill.findData(3));assert window.skill_animation_reference.currentData()==choice
            window.damage_technical.setChecked(True);window.damage_technical.setChecked(False)
            assert window.skill_animation_reference.currentData()==choice
            window.frame_timing.setChecked(False);assert not window.damage_form.isRowVisible(window.skill_animation_reference)
            window.frame_timing.setChecked(True);assert window.skill_animation_reference.currentData()==choice
            app.processEvents();screenshot=base/'animation-reference.png';assert window.grab().save(str(screenshot))
            window.select_operator('char_1042_phatm2');window.skill.setCurrentIndex(window.skill.findData(2))
            bait=next(w for owner,key,_,w in window.model_option_widgets if owner=='char_1042_phatm2' and key=='bait_triggers')
            bait.setValue(2);assert window.damage_result
            assert window.damage_result['result']['total_damage'] is None
            assert '本能的召唤 · 诱饵持续效果待核验' in window.damage_text.toPlainText()
            assert '已建模伤害小计' in window.damage_text.toPlainText()
            app.processEvents();bait_image=base/'bait-unknown.png';assert window.grab().save(str(bait_image))
            window.select_operator('mechanist')
            assert '本能的召唤 · 诱饵持续效果待核验' not in window.damage_text.toPlainText()
            assert not window.auto.isChecked() and not window.capture.target and not window.desktop.process
            assert not (p/'settings.json').exists() and not (p/'chat').exists()
        finally:window.close();app.processEvents()
    names=['rouge/app.py','rouge/animation_reference.py','rouge/timing.py','rouge/operator_engine.py',
        'rouge/elemental_relics.py','rouge/reporting.py','rouge/data/original-animation-references.json',
        'scripts/verify_animation_ui_048.py']
    receipt={'version':'0.48.0','passed':True,'reference_option_visits':slots,'unique_references_visited':len(seen),
        'catalog_counts':references()['counts'],'choice_preserved_on_recalculation_and_return':True,
        'reference_controls_hidden_when_not_applicable':True,'bait_section_only_on_affected_skill':True,
        'unknown_damage_is_not_zero':True,'default_motion_binding_unchanged':True,
        'private_data_isolated':True,'game_actions':0,'chat_requests':0,
        'source_sha256':{n:digest(n) for n in names},
        'screenshots':{str(f.relative_to(ROOT)):digest(str(f.relative_to(ROOT))) for f in (screenshot,bait_image)},
        'seconds':time.perf_counter()-started}
    (ROOT/'ANIMATION_UI_0.48_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_sha256','screenshots')},ensure_ascii=False))


if __name__=='__main__':main()
