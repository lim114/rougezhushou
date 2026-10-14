"""Actual MainWindow and source-filter query using public temporary state only."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',required=True)
    parser.add_argument('--visible-ms',type=int,default=120000);args=parser.parse_args()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from rouge import app as app_module
    from rouge.offline_tools_view import run_offline_query,public_payload
    gui=QApplication([])
    source_files=('rouge/app.py','rouge/calibration.py','rouge/offline_tools_view.py',
        'rouge/shield_source_inventory.py','rouge/mechanist_barrier_ledger.py',
        'rouge/data/shield-source-inventory-source.json')
    loaded={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_files}
    with tempfile.TemporaryDirectory(prefix='rouge-268-public-') as state:
        temp=Path(state);app_module.ROOT=temp;app_module.SETTINGS=temp/'settings.json'
        app_module.OPERATOR_STATE=temp/'operators.json';app_module.RUN_STATE=temp/'run.json'
        window=app_module.MainWindow();window.setWindowTitle('第268节 · 来源屏障库存与溢出门（隔离公开条件）')
        window.resize(1550,1100);window.show()
        window.operator_choices.select_value('mechanist');window.skill.setCurrentIndex(window.skill.findData(2));gui.processEvents()
        mechanist_visible=not window.shield_inventory_button.isHidden()
        window.operator_choices.select_value('kaltsit');gui.processEvents();other_hidden=window.shield_inventory_button.isHidden()
        window.operator_choices.select_value('mechanist');window.skill.setCurrentIndex(window.skill.findData(2))
        window.shield_inventory_button.click();panel=window.offline_tools;panel.run_button.click()
        def check():
            if panel._workers:QTimer.singleShot(100,check);return
            result=panel.result_snapshot();assert result is not None,panel.status.text()
            assert window.centralWidget().currentWidget() is panel
            assert result==run_offline_query('calibration','shield-inventory',public_payload('calibration','shield-inventory'))
            assert mechanist_visible and other_hidden
            assert result['source_filters']['caster']['total_raw_reference']==20*(1<<32)
            assert result['source_filters']['recipient']['total_raw_reference']==0
            assert result['both_filters_pass_reference'] is False
            before=(panel.editor.toPlainText(),panel.result_view.toPlainText(),panel.current_query())
            panel.set_scenario({'operator':'kaltsit','skill':1})
            assert before==(panel.editor.toPlainText(),panel.result_view.toPlainText(),panel.current_query())
            report={'qpa':gui.platformName(),'visible':window.isVisible(),'main_window_route_verified':True,
                'mechanist_S2_button_visible':mechanist_visible,'other_operator_button_hidden':other_hidden,
                'query':panel.current_query(),'instance_count':len(result['source_filters']['caster']['rows']),
                'source_totals_raw':[result['source_filters'][r]['total_raw_reference'] for r in ('caster','recipient')],
                'both_filters_pass_reference':result['both_filters_pass_reference'],
                'actual_inventory_and_cancel_unknown':result['actual_inventory_complete'] is None and result['actual_overflow_cancelled'] is None,
                'refresh_preserved_editor_result_selection':True,'loaded_source_sha256':loaded,
                'private_state_read':False,'temporary_state_root':True,'game_operated':False,'chat_sent':False,
                'scope':'Actual Windows changed MainWindow route and public source inventory; not full game or original historic Windows validation'}
            p=Path(args.receipt);p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
        QTimer.singleShot(500,check);QTimer.singleShot(args.visible_ms,window.close)
        return gui.exec()


if __name__=='__main__':raise SystemExit(main())
