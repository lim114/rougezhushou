"""Real isolated MainWindow verification of declared skill-SP references."""
from copy import deepcopy
import argparse,hashlib,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

def main():
    p=argparse.ArgumentParser();p.add_argument('--receipt',required=True);p.add_argument('--visible-ms',type=int,default=25000);args=p.parse_args()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from rouge import app as app_module
    from rouge.offline_tools_view import public_payload,run_offline_query,PRODUCT_QUERIES,QUERIES
    from rouge.skill_sp_cost_reference import source_data
    if not source_data()['valid']:raise RuntimeError('Unbound skill cost sources')
    files={'rouge/app.py','rouge/calibration.py','rouge/offline_tools_view.py','rouge/information_scope.py',
           'rouge/skill_sp_cost_reference.py','tests/test_skill_sp_cost_independent_277.py',
           'scripts/verify_skill_sp_cost_window_277.py'}
    files.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'research/p2-skill-sp-cost-277').rglob('*') if p.is_file())
    before={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sorted(files)}
    gui=QApplication([])
    class PublicWindow(app_module.MainWindow):
        def refresh_windows(self):self.windows.clear()
    with tempfile.TemporaryDirectory(prefix='rouge-277-sp-cost-') as state:
        temp=Path(state);app_module.ROOT=temp;app_module.SETTINGS=temp/'settings.json'
        app_module.OPERATOR_STATE=temp/'operators.json';app_module.RUN_STATE=temp/'run.json'
        w=PublicWindow();w.resize(1500,1050);w.setWindowTitle('第277节 · 技力门槛与消耗意图（独立声明）');w.show()
        panel=w.offline_tools;panel.select_query('calibration','sp-cost');w.centralWidget().setCurrentWidget(panel);panel.run_button.click()
        elapsed=[0]
        def check():
            try:
                if panel._workers:
                    elapsed[0]+=100
                    if elapsed[0]>15000:raise TimeoutError('Public skill cost query stalled')
                    QTimer.singleShot(100,check);return
                data=panel.result_snapshot();assert data is not None,panel.status.text()
                assert data==run_offline_query('calibration','sp-cost',public_payload('calibration','sp-cost'))
                assert data['source']['valid'] and len(data['rows'])==10
                rows={r['id']:r for r in data['rows']}
                assert rows['public.override']['result_reference'] is True
                assert rows['public.override']['arithmetic_reference']['threshold_int32']==5
                assert rows['public.changed_second']['arithmetic_reference']['threshold_int32']==7
                assert rows['public.changed_second']['result_reference'] is False
                debit=rows['public.debit20'];assert debit['normal'] is True and debit['result_reference'] is False
                assert debit['modifier_constructor_arguments']['magnitude_raw']==85899345920
                assert debit['apply_arguments']['force'] is False
                assert rows['public.free_admission']['result_reference'] is True
                assert rows['public.independent_debit']['apply_arguments'] is not None
                free=rows['public.free_debit'];assert free['result_reference'] is True
                assert all(s['called'] is False for s in free['stages'] if s['name']!='free_read')
                assert rows['public.min32']['arithmetic_reference']['input_raw']==-9223372036854775808
                assert rows['public.min32']['modifier_constructor_arguments']['magnitude_raw']==9223372036854775806
                for key in ('actual_owner_sp_after','actual_cost_paid','actual_cast_success','complete_cycle'):
                    assert data[key] is None and all(r[key] is None for r in data['rows'])
                assert len(QUERIES['calibration'])+len(QUERIES['battle'])==32
                assert len(PRODUCT_QUERIES['exploration'])==9 and len(QUERIES['exploration'])==13
                rendered=panel.result_view.toPlainText()
                assert '门槛5与费用20分开' in rendered and '实际技力、实际支付' in rendered
                snapshot=(panel.current_query(),panel.editor.toPlainText(),deepcopy(data),panel.result_view.toHtml(),panel.result_view.verticalScrollBar().value())
                panel.set_scenario({'operator':'mechanist','skill':2});gui.processEvents()
                assert not panel.import_scenario.isEnabled()
                assert snapshot==(panel.current_query(),panel.editor.toPlainText(),panel.result_snapshot(),panel.result_view.toHtml(),panel.result_view.verticalScrollBar().value())
                assert w.isVisible() and not w.auto.isChecked() and w.capture.target is None and w.desktop.process is None
                after={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sorted(files)};assert before==after
                report={'passed':True,'qpa':gui.platformName(),'visible':True,'query':['calibration','sp-cost'],
                    'public_rows':10,'calibration_and_battle_queries':32,'exploration_product_queries':9,'historical_exploration_queries':13,
                    'gate_override_not_cost_floor':True,'second_min_read_independent':True,'free_not_reused_for_debit':True,
                    'apply_normal_false_not_exception_or_paid_cost':True,'signed_MIN32_and_abs_special_case':True,
                    'unknown_actual_SP_payment_cast_and_cycle':True,'scenario_import_disabled':True,'refresh_preserved_input_result_selection_scroll':True,
                    'loaded_source_sha256':before,'source_sha256_after':after,'private_state_read':False,'temporary_state_root':True,
                    'game_operated':False,'game_captures':0,'chat_sent':False,'scope':'Actual isolated current public MainWindow; not game/private/historical native integration.'}
            except BaseException as error:
                report={'passed':False,'failure':{'type':type(error).__name__,'message':str(error)},'loaded_source_sha256':before,'private_state_read':False,'temporary_state_root':True,'game_operated':False,'chat_sent':False};gui.exit(1)
            destination=Path(args.receipt);destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
        QTimer.singleShot(500,check);QTimer.singleShot(args.visible_ms,w.close)
        return gui.exec()
if __name__=='__main__':raise SystemExit(main())
