def check(window,gui,require):
 import os
 from PySide6.QtWidgets import QWidget
 from PySide6.QtCore import QRect
 from PySide6.QtTest import QTest
 from .player_game_binding import BindingApi
 # Preserve the original native-identity unittest under its actual prerequisites.
 # Its entire original assertion body is retained; no fake API, HWND or geometry.
 from tests.test_player_feature_416 import BindingTests
 import unittest,json
 require(gui.platformName()=='windows','native_identity_unittest_actual_windows_backend')
 case=BindingTests('test_owned_native_identity_and_geometry')
 BindingTests.setUpClass();result=unittest.TestResult();case.run(result)
 evidence={'kind':'actual_original_native_identity_unittest','selector':'tests.test_player_feature_416.BindingTests.test_owned_native_identity_and_geometry','qpa':gui.platformName(),'tests_run':result.testsRun,'failures':[(test.id(),trace)for test,trace in result.failures],'errors':[(test.id(),trace)for test,trace in result.errors],'skips':[(test.id(),reason)for test,reason in result.skipped],'was_successful':result.wasSuccessful(),'actual_assertion_body_not_replaced':True}
 print(json.dumps(evidence,ensure_ascii=False),flush=True)
 require(result.testsRun==1 and not result.skipped,'original_native_identity_case_executed_without_skip')
 require(result.wasSuccessful(),'original_native_identity_assertions_passed_'+str(result.failures+result.errors))
 window.show_compact();c=window.compact_window;binding=c.game_binding;binding.timer.stop()
 fixture=QWidget();fixture.setWindowTitle('自有窗口绑定验证，不是游戏');fixture.resize(900,650);fixture.move(100,100);fixture.show();gui.processEvents()
 try:
  target={'hwnd':int(fixture.winId()),'pid':os.getpid()};api=BindingApi();snap=api.read(target)
  require(snap is not None and snap['active'],'actual_owned_client_geometry_readable')
  binding.apply(snap);c.open_inventory();gui.processEvents();popup=c.inventory_popup;before=c.pos();p_before=popup.pos()
  fixture.move(180,155);gui.processEvents();after=api.read(target);binding.apply(after);gui.processEvents()
  require(c.pos()!=before,'actual_toolbar_follows_owned_client_move')
  require(popup.pos()!=p_before,'actual_popup_follows_owned_client_move')
  binding.apply({**after,'active':False});gui.processEvents();require(not c.isVisible()and not popup.isVisible(),'unavailable_client_hides_bound_surfaces')
  binding.apply(after);gui.processEvents();require(c.isVisible()and popup.isVisible(),'restored_client_restores_only_visible_surfaces')
  require(not c.settings_popup.isVisible(),'hidden_settings_not_opened_on_restore')
  binding.set_enabled(False);before=c.pos();binding.apply({**after,'logical_client':QRect(500,300,800,600)});require(c.pos()==before,'disabled_follow_leaves_window_free')
  require(api.read({'hwnd':target['hwnd'],'pid':target['pid']+10000000})is None,'reused_handle_wrong_pid_rejected')
  window.run.state.update({});c.binding_status.setText('隔离验收：自有窗口移动、隐藏与恢复通过；不是游戏连接证明。')
  popup.hide();c.present(c.settings_popup);QTest.qWait(100);gui.processEvents();window.player_validation_target=c.settings_popup
 finally:fixture.close();binding.previous=None;binding.snapshot=None;binding.ever_bound=False;binding.suspended=[]
