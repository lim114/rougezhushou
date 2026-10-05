"""All profile skill choices and selectable overview branches in isolated Qt."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile,time
from pathlib import Path
from PySide6.QtGui import QFontDatabase,QFont
from PySide6.QtWidgets import QApplication
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module
from rouge.catalog import operator_profiles
from rouge.view_catalog import PROFESSIONS,ENEMY_TIERS
from rouge.branch_choice import OVERVIEW
from rouge.battle_preview import battle_data


def choices(combo):return [combo.itemData(i) for i in range(combo.count()) if combo.itemData(i) is not None]


def main():
    started=time.perf_counter();base=ROOT/'.cache/mechanisms-048'
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda _path,callback:backend(p/'chat',callback)
        app=QApplication([])
        font=QFontDatabase.addApplicationFont(str(Path(os.environ['WINDIR'])/'Fonts/msyh.ttc'))
        assert font>=0;app.setFont(QFont(QFontDatabase.applicationFontFamilies(font)[0],9))
        window=OfflineWindow();window.resize(1150,920);window.show();app.processEvents()
        slots=0;images={}
        try:
            for op,profile in operator_profiles().items():
                assert window.select_operator(op)
                expected=[i+1 for i,s in enumerate(profile['skills']) if s['unlock_elite']<=len(profile['phases'])-1]
                assert choices(window.skill)==expected,(op,choices(window.skill),expected)
                for i in range(window.skill.count()):
                    window.skill.setCurrentIndex(i)
                    sid=profile['skills'][window.skill.currentData()-1]['id']
                    assert not window.skill.itemIcon(i).isNull()
                    assert window.skill_picture.key[1]==sid and not window.skill_picture.image.pixmap().isNull()
                    slots+=1
            assert slots==949,slots
            window.centralWidget().setCurrentIndex(1)
            members=['mechanist','kaltsit','silverash']
            window.apply_run_observation({'operators':[{'id':op,'scope':'run','fields':{'elite':2,'level':90},
                'skill_ranks':{'1':10,'2':10,'3':10}} for op in members],
                'relics':{'ids':[],'icons':[],'source':'test'}},time.time())
            window.operator_choices.select_branch(OVERVIEW)
            assert set(choices(window.operator))==set(members)
            window.select_operator('mechanist');window.skill.setCurrentIndex(window.skill.findData(3))
            app.processEvents();file=base/'recruited-overview.png';assert window.grab().save(str(file));images['recruited_overview']=file
            profession=PROFESSIONS[operator_profiles()['silverash']['profession']]
            window.operator_choices.select_branch(profession);window.select_operator('silverash')
            assert all(PROFESSIONS[operator_profiles()[op]['profession']]==profession for op in choices(window.operator))
            app.processEvents();file=base/'profession-branch.png';assert window.grab().save(str(file));images['profession_branch']=file
            panel=window.battle_preview;window.centralWidget().setCurrentWidget(panel)
            sid=next(sid for sid,s in battle_data()['stages'].items() if any(e['level_type']=='BOSS' for e in s['enemies']))
            window.select_battle_stage(sid);panel.enemy_choices.select_branch('领袖')
            assert choices(panel.enemy_combo)
            assert all(next(e for e in battle_data()['stages'][sid]['enemies'] if (e['id'],e['level'])==value)['level_type']=='BOSS'
                       for value in choices(panel.enemy_combo))
            app.processEvents();file=base/'enemy-branch.png';assert window.grab().save(str(file));images['enemy_branch']=file
            panel.stage_choices.select_branch('第Ⅰ层')
            assert len(choices(panel.stage_combo))==11
            panel.stage_choices.select_value('ro6_n_1_2')
            panel.enemy_choices.select_branch(OVERVIEW)
            app.processEvents();file=base/'floor-branch.png';assert window.grab().save(str(file));images['floor_branch']=file
            assert not window.auto.isChecked() and not window.capture.target and not window.desktop.process
            assert not (p/'settings.json').exists() and not (p/'chat').exists()
            receipt={'version':'0.48.0','passed':True,'profile_panels':431,'skill_icon_slots':slots,
                     'recruited_overview_members':3,'profession_branch_filtered':True,'enemy_tier_branch_filtered':True,
                     'floor_branch_filtered':True,'private_data_isolated':True,'game_actions':0,'chat_requests':0,
                     'seconds':time.perf_counter()-started,'screenshots':{k:str(v.relative_to(ROOT)) for k,v in images.items()},
                     'screenshot_sha256':{k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in images.items()},
                     'source_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in (
                         'rouge/app.py','rouge/view_catalog.py','rouge/branch_choice.py','rouge/battle_view.py',
                         'rouge/data/skill-icons.json','scripts/verify_branch_ui_048.py')}}
            (ROOT/'BRANCH_UI_0.48_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps({k:receipt[k] for k in ('passed','profile_panels','skill_icon_slots','seconds')}),flush=True)
        finally:window.close();app.processEvents()


if __name__=='__main__':main()
