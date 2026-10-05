"""One isolated, readable configuration screenshot; no live game sampling."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication
from PySide6.QtGui import QFontDatabase,QFont
from rouge.battle_preview import battle_data
from rouge.enemy_skills import enemy_skill_reference


def main():
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda _path,callback:backend(p/'chat',callback)
        app=QApplication([])
        fid=QFontDatabase.addApplicationFont(str(Path(os.environ['WINDIR'])/'Fonts/msyh.ttc'));assert fid>=0
        app.setFont(QFont(QFontDatabase.applicationFontFamilies(fid)[0],9))
        window=OfflineWindow()
        try:
            panel=window.battle_preview;window.centralWidget().setCurrentWidget(panel)
            sid,enemy=next((s,e) for s,d in battle_data()['stages'].items() for e in d['enemies']
                if any(v.get('skills') for v in enemy_skill_reference(s,e['id'],e['level'])['definitions'])
                and any(v.get('spData') for v in enemy_skill_reference(s,e['id'],e['level'])['definitions']))
            panel.set_stage(sid)
            index=next(i for i in range(1,panel.enemy_combo.count())
                if panel.enemy_combo.itemData(i)==(enemy['id'],enemy['level']))
            panel.enemy_combo.setCurrentIndex(index)
            window.resize(1050,830);window.show();app.processEvents()
            detail=panel.enemy_detail;text=detail.toPlainText()
            assert '冷却参数：' in text and '技力配置：' in text
            detail.moveCursor(detail.textCursor().MoveOperation.Start)
            assert detail.find('冷却参数：')
            detail.centerCursor();app.processEvents()
            assert detail.viewport().rect().contains(detail.cursorRect().center())
            screenshot=ROOT/'.cache/preview-042/enemy-skill-readable.png'
            assert window.grab().save(str(screenshot))
            assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
            assert window.run.state['config']=={} and window.run.state['history']==[]
            receipt={'version':'0.42.0','passed':True,'verified_at':time.time(),'synthetic_gui_only':True,
                'stage_id':sid,'enemy_id':enemy['id'],'enemy_level':enemy['level'],
                'cooldown_parameter_on_screen':True,'screenshot':str(screenshot.relative_to(ROOT)),
                'screenshot_sha256':hashlib.sha256(screenshot.read_bytes()).hexdigest(),
                'chat_requests':0,'game_actions':0,'private_state_used':False,
                'source_hashes':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in (
                    'scripts/capture_enemy_ui_042.py','rouge/app.py','rouge/battle_preview.py',
                    'rouge/enemy_skills.py','rouge/data/enemy-skill-references.json')}}
            (ROOT/'PREVIEW_SCREENSHOT_0.42_VERIFICATION.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
            print(json.dumps({'passed':True,'screenshot':receipt['screenshot']}),flush=True)
        finally:window.close();app.processEvents()


if __name__=='__main__':main()
