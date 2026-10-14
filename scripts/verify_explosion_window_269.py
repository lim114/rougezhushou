"""Actual public MainWindow explosion entry in a separate temporary state root."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',required=True)
    parser.add_argument('--visible-ms',type=int,default=120000);args=parser.parse_args()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from rouge import app as app_module
    from rouge.offline_tools_view import public_payload,run_offline_query
    gui=QApplication([])
    files=('rouge/app.py','rouge/calibration.py','rouge/offline_tools_view.py','rouge/mechanist_barrier_ledger.py',
        'rouge/mechanist_explosion_math.py','rouge/data/mechanist-explosion-source.json','rouge/shield_source_inventory.py')
    loaded={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}
    with tempfile.TemporaryDirectory(prefix='rouge-269-public-') as state:
        temp=Path(state);app_module.ROOT=temp;app_module.SETTINGS=temp/'settings.json'
        app_module.OPERATOR_STATE=temp/'operators.json';app_module.RUN_STATE=temp/'run.json'
        window=app_module.MainWindow();window.setWindowTitle('第269节 · 机械师爆炸双分支FP（隔离公开快照）')
        window.resize(1550,1100);window.show()
        window.operator_choices.select_value('mechanist');window.skill.setCurrentIndex(window.skill.findData(2));gui.processEvents()
        own=not window.explosion_values_button.isHidden()
        window.operator_choices.select_value('kaltsit');gui.processEvents();other=window.explosion_values_button.isHidden()
        window.operator_choices.select_value('mechanist');window.skill.setCurrentIndex(window.skill.findData(2))
        window.explosion_values_button.click();panel=window.offline_tools;panel.run_button.click()
        def check():
            if panel._workers:QTimer.singleShot(100,check);return
            r=panel.result_snapshot();assert r is not None,panel.status.text()
            assert r==run_offline_query('calibration','explosion-values',public_payload('calibration','explosion-values'))
            assert own and other and window.centralWidget().currentWidget() is panel
            b=r['rows'][0]['branches'];assert b['scaled']['calculate_damage_raw_reference']==6012954080000
            assert b['baseline']['calculate_damage_raw_reference']==3006477040000
            assert r['rows'][0]['origin_atk_raw_reference'] is None
            before=(panel.editor.toPlainText(),panel.result_view.toPlainText(),panel.current_query())
            panel.set_scenario({'operator':'kaltsit','skill':1})
            assert before==(panel.editor.toPlainText(),panel.result_view.toPlainText(),panel.current_query())
            report={'qpa':gui.platformName(),'visible':window.isVisible(),'main_window_route_verified':True,
                'mechanist_S2_button_visible':own,'other_operator_button_hidden':other,'query':panel.current_query(),
                'scaled_calculate_damage_raw':b['scaled']['calculate_damage_raw_reference'],
                'baseline_calculate_damage_raw':b['baseline']['calculate_damage_raw_reference'],
                'late_origin_atk_and_actual_damage_unknown':r['rows'][0]['origin_atk_raw_reference'] is None and r['actual_total_damage'] is None,
                'refresh_preserved_editor_result_selection':True,'loaded_source_sha256':loaded,
                'private_state_read':False,'temporary_state_root':True,'game_operated':False,'chat_sent':False,
                'scope':'Actual Windows changed MainWindow/public explosion snapshots only; not complete game/private/native-history validation'}
            p=Path(args.receipt);p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
        QTimer.singleShot(500,check);QTimer.singleShot(args.visible_ms,window.close)
        return gui.exec()


if __name__=='__main__':raise SystemExit(main())
