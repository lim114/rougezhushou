"""Readable motion/bait evidence in a temporary, sampling-disabled window."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile
from pathlib import Path
from PySide6.QtWidgets import QApplication,QScrollArea
from PySide6.QtGui import QFontDatabase,QFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module
from rouge.animation_reference import choices


def main():
    images=[]
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda _path,callback:backend(p/'chat',callback)
        app=QApplication([]);fid=QFontDatabase.addApplicationFont(str(Path(os.environ['WINDIR'])/'Fonts/msyh.ttc'))
        assert fid>=0;app.setFont(QFont(QFontDatabase.applicationFontFamilies(fid)[0],9))
        window=OfflineWindow();window.resize(1250,1000);window.show();window.centralWidget().setCurrentIndex(1)
        try:
            window.select_operator('kaltsit');window.skill.setCurrentIndex(window.skill.findData(3))
            identity=next(r['id'] for r in choices('kaltsit',3) if r['orientation']=='Back' and r['animation']=='Skill_3_Attack')
            window.skill_animation_reference.setCurrentIndex(window.skill_animation_reference.findData(identity))
            assert window.damage_result['result']['timing']['streams'][0]['release_frames'][0]==13
            scroll=next(s for s in window.findChildren(QScrollArea) if s.isAncestorOf(window.skill_animation_reference))
            for file,widget,heading in (('animation-controls.png',window.skill_animation_reference,'战斗时序参考'),
                                        ('bait-controls.png',None,'本能的召唤 · 诱饵持续效果待核验')):
                if widget is None:
                    window.select_operator('char_1042_phatm2');window.skill.setCurrentIndex(window.skill.findData(2))
                    widget=next(w for owner,key,_,w in window.model_option_widgets if owner=='char_1042_phatm2' and key=='bait_triggers')
                    widget.setValue(2);assert window.damage_result['result']['total_damage'] is None
                app.processEvents();scroll.ensureWidgetVisible(widget,30,55)
                position=window.damage_text.toPlainText().find(heading);assert position>=0
                cursor=window.damage_text.textCursor();cursor.setPosition(position)
                window.damage_text.setTextCursor(cursor);window.damage_text.ensureCursorVisible();app.processEvents()
                target=ROOT/'.cache/mechanisms-048'/file;assert window.grab().save(str(target));images.append(target)
            assert not window.auto.isChecked() and not window.capture.target and not window.desktop.process
            assert not (p/'settings.json').exists() and not (p/'chat').exists()
        finally:window.close();app.processEvents()
    receipt={'version':'0.48.0','passed':True,'private_data_isolated':True,'game_actions':0,'chat_requests':0,
        'source_sha256':{str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        'screenshots':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in images}}
    (ROOT/'ANIMATION_SCREENSHOT_0.48_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))


if __name__=='__main__':main()
