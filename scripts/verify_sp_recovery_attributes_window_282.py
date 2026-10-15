"""Actual isolated Windows MainWindow fixture. Promote before running; no game/chat."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import traceback

ROOT=next(parent for parent in Path(__file__).resolve().parents
          if (parent/'rouge/app.py').is_file())
sys.path.insert(0,str(ROOT))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--receipt',required=True)
    parser.add_argument('--visible-ms',type=int,default=120000)
    args=parser.parse_args()
    destination=Path(args.receipt)
    if destination.exists():
        raise FileExistsError('Preserve the first receipt; use a new receipt path.')
    before={}

    def write_report(report):
        destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists():
            raise FileExistsError('The fixture does not overwrite a prior receipt.')
        destination.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))

    def failure_report(error):
        return {'passed':False,'failure':{'type':type(error).__name__,'message':str(error),
                                        'traceback':traceback.format_exc()},
                'loaded_source_sha256':before,'private_state_read':False,
                'temporary_state_root':True,'game_operated':False,'game_captures':0,'chat_sent':False}

    try:
        if sys.platform!='win32':
            raise RuntimeError('This fixture requires actual Windows, not compatibility/headless validation.')
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication
        from rouge import app as app_module
        from rouge.offline_tools_view import public_payload,run_offline_query,PRODUCT_QUERIES,QUERIES
        from rouge.sp_recovery_attribute_reference import source_data,INIT_STAGES,NOTIFY_STAGES
        source=source_data()
        if not source['valid']:
            raise RuntimeError('Unbound SP recovery attribute source')
        files={'rouge/app.py','rouge/calibration.py','rouge/offline_tools_view.py','rouge/information_scope.py',
               'rouge/sp_recovery_attribute_reference.py','rouge/recovery_attributes.py',
               'rouge/sp_recovery_clock.py','rouge/skill_sp_increment_reference.py',
               'tests/test_sp_recovery_attribute_independent_282.py',
               'scripts/verify_sp_recovery_attributes_window_282.py'}
        packet=ROOT/'research/p2-sp-recovery-attributes-282'
        if not packet.is_dir():
            raise FileNotFoundError(str(packet))
        files.update(p.relative_to(ROOT).as_posix() for p in packet.rglob('*') if p.is_file())
        manifest=json.loads((packet/'source_manifest.json').read_bytes())
        files.update(manifest['files_sha256'])
        before={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sorted(files)}
        gui=QApplication([])
        if gui.platformName()!='windows':
            raise RuntimeError('A non-Windows QPA cannot prove the actual Windows window.')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        with tempfile.TemporaryDirectory(prefix='rouge-282-sp-recovery-attributes-') as state:
            temp=Path(state)
            app_module.ROOT=temp
            app_module.SETTINGS=temp/'settings.json'
            app_module.OPERATOR_STATE=temp/'operators.json'
            app_module.RUN_STATE=temp/'run.json'
            w=PublicWindow()
            w.resize(1500,1050)
            w.setWindowTitle('第282节 · 技力回复属性14/30（条件参考）')
            w.show()
            panel=w.offline_tools
            panel.select_query('calibration','sp-attributes')
            w.centralWidget().setCurrentWidget(panel)
            panel.run_button.click()
            elapsed=[0];checked=[False];failed=[False]

            def check():
                try:
                    if panel._workers:
                        elapsed[0]+=100
                        if elapsed[0]>15000:
                            raise TimeoutError('Public SP recovery attributes query stalled')
                        QTimer.singleShot(100,check)
                        return
                    data=panel.result_snapshot()
                    assert data is not None,panel.status.text()
                    public=public_payload('calibration','sp-attributes')
                    assert set(public)=={'sp_attributes'}
                    assert data==run_offline_query('calibration','sp-attributes',public)
                    assert data['source_valid'] is True
                    assert source['method_count']==16 and source['byte_span_count']==1833
                    assert len(data['readings'])==7 and len(data['rate_reads'])==2 and len(data['rows'])==2
                    assert set(public['sp_attributes'])=={'readings','rate_reads','initializations','notifications'}
                    assert len(public['sp_attributes']['initializations'])==1
                    assert len(public['sp_attributes']['notifications'])==1
                    values={r['id']:r for r in data['readings']}
                    assert values['ratio-over-one']['attribute']==30
                    assert values['ratio-over-one']['getter_raw_reference']==12884901888
                    assert values['negative14']['getter_raw_reference']==0
                    init,notify=data['rows']
                    assert init['kind']=='initial_slot0' and notify['kind']=='dirty_notification'
                    assert tuple(s['name'] for s in init['stages'])==INIT_STAGES
                    assert tuple(s['name'] for s in notify['stages'])==NOTIFY_STAGES

                    def stage(row,name):
                        return next(s for s in row['stages'] if s['name']==name)

                    assert init['normal'] is True
                    assert init['slot0_fp_argument_raw_reference']==6442450944
                    assert stage(init,'raw_encode')['reference']['argument_raw']==6442450944
                    assert init['stored_prefix']==[{'field':'rawData[14]','byte_count':40,
                                                   'payload_identity':None,'decoded_value':None}]
                    assert init['refresh_reference']['id']=='init.refresh14'
                    assert init['refresh_reference']['getter_raw_reference']==30064771072
                    assert init['raw_value_after'] is None and init['cache_value_after'] is None
                    assert stage(init,'mark_dirty')['reference']['partial_mask_state'] is None
                    assert stage(init,'mark_dirty')['reference']['callback_target'] is None
                    assert init['clock_reference'] is None and init['clock_request'] is None
                    assert notify['normal'] is True and notify['attribute']==30
                    assert notify['new_rate_reference']['id']=='new-rate'
                    assert notify['new_rate_reference']['rate_raw_reference']==8589934592
                    assert notify['can_recover_snapshot_reference']['attr14_raw']==4294967296
                    assert notify['can_recover_snapshot_reference']['attr30_raw']==4294967296
                    action=notify['clock_request']['actions'][0]
                    assert action['id']=='sp282.reconfigure' and action['kind']=='reconfigure'
                    assert action['rate_input_raw']==8589934592
                    update=stage(notify,'controller_update')['reference']
                    assert update['source_body']=='inline_UpdateSpRecoveryPerSec'
                    assert update['old_value_used_by_ordinary_body'] is False
                    clock=notify['clock_reference']
                    assert clock['source_valid'] is True and len(clock['rows'])==1
                    assert clock['rows'][0]['can_recover']['rate_raw_reference']==4294967296
                    assert clock['final_period_raw_reference']==2147483648
                    assert clock['final_remaining_raw_reference']==1073741824
                    for key in ('actual_attribute_values','actual_cache_or_dirty_state','actual_sp_after','actual_timer','complete_cycle'):
                        assert data[key] is None and all(row[key] is None for row in data['rows'])
                    assert data['events_scheduled'] is False and data['hotfix_equivalence_proven'] is False
                    assert len(QUERIES['calibration'])+len(QUERIES['battle'])==37
                    assert len(PRODUCT_QUERIES['exploration'])==9 and len(QUERIES['exploration'])==13
                    rendered=panel.result_view.toPlainText()
                    for phrase in ('技力回复属性14/30',
                                   '初始化写入参数与后续解码读值分开',
                                   '变更通知生成独立计时器参考',
                                   '实际属性、当前技力、实际计时器与完整周期：未知'):
                        assert phrase in rendered,phrase
                    snapshot=(panel.current_query(),panel.editor.toPlainText(),deepcopy(data),
                              panel.result_view.toHtml(),panel.result_view.verticalScrollBar().value())
                    panel.set_scenario({'operator':'mechanist','skill':2})
                    gui.processEvents()
                    assert not panel.import_scenario.isEnabled()
                    assert snapshot==(panel.current_query(),panel.editor.toPlainText(),panel.result_snapshot(),
                                      panel.result_view.toHtml(),panel.result_view.verticalScrollBar().value())
                    assert w.isVisible() and not w.auto.isChecked()
                    assert w.capture.target is None and w.desktop.process is None
                    after={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sorted(files)}
                    assert before==after
                    report={'passed':True,'qpa':gui.platformName(),'visible':True,
                            'query':['calibration','sp-attributes'],'payload_key':'sp_attributes',
                            'public_attribute_reads':7,'public_rate_reads':2,'public_rows':2,
                            'selected_source_records':16,'bound_source_spans':1833,
                            'native_primary_readback_performed_by_window':False,
                            'attribute30_default_range_allows_above_one':True,
                            'slot0_encoder_argument_raw':6442450944,'raw14_opaque_stored_bytes':40,
                            'refresh_independent_raw':30064771072,'mark_dirty_callback_and_mask_unknown':True,
                            'new_rate_raw':8589934592,'independent_eligibility_rate_raw':4294967296,
                            'reference_timer_period_raw':2147483648,'reference_timer_remaining_raw':1073741824,
                            'inline_controller_body_reference_not_real_callee_observation':True,
                            'actual_attributes_cache_SP_timer_cycle_unknown':True,
                            'events_scheduled':False,'hotfix_equivalence_proven':False,
                            'calibration_and_battle_queries':37,'exploration_product_queries':9,
                            'historical_exploration_queries':13,'scenario_import_disabled':True,
                            'refresh_preserved_input_result_selection_scroll':True,
                            'loaded_source_sha256':before,'source_sha256_after':after,
                            'private_state_read':False,'temporary_state_root':True,
                            'game_operated':False,'game_captures':0,'chat_sent':False,
                            'scope':'Actual isolated public Windows MainWindow; not game/private integration or native execution.'}
                except BaseException as error:
                    report=failure_report(error);failed[0]=True
                checked[0]=True
                write_report(report)
                if failed[0]:gui.exit(1)

            def close():
                if not checked[0]:
                    write_report(failure_report(TimeoutError('Window closed before a checked result was obtained')))
                    failed[0]=True
                w.close()

            QTimer.singleShot(500,check)
            QTimer.singleShot(max(20000,args.visible_ms),close)
            result=gui.exec()
            if not checked[0] and not destination.exists():
                write_report(failure_report(RuntimeError('The actual window exited before verification')))
                failed[0]=True
            return 1 if failed[0] else result
    except BaseException as error:
        if not destination.exists():write_report(failure_report(error))
        raise


if __name__=='__main__':
    raise SystemExit(main())
