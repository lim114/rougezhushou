from copy import deepcopy
import ctypes
from ctypes import wintypes
from PySide6.QtCore import Qt,QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QWidget

def check(window,gui,require):
    from .player_toolbar import ORDER,DIAMETER,LABEL_SPACE
    import win32gui
    before=deepcopy(window.run.state);window.show_compact();bar=window.compact_window
    area=bar.screen().availableGeometry();bar._move_dock(QPoint(area.right()-bar.width()-30,area.bottom()-bar.height()-30))
    probe=QWidget();probe.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,True)
    probe.setWindowTitle('隔离验收背景');probe.setGeometry(bar.x()-20,bar.y()-20,bar.width()+40,bar.height()+40)
    try:
        probe.show();bar.raise_();QTest.mouseMove(probe,QPoint(5,5));QTest.qWait(240);gui.processEvents()
        require(bar.height()==DIAMETER+4 and not hasattr(bar,'hover_label')and not hasattr(bar,'grip'),'single_row_without_subtitle_or_drag_handle')
        require(tuple(b.accessibleName()for b in bar.tool_buttons)==ORDER,'actual_buttons_follow_reference_function_order')
        require(bar.findChild(QWidget,'toolbarShell')is None,'continuous_panel_background_removed')
        require(bar.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground),'actual_toolbar_translucent_surface')
        require(len({b.y()for b in bar.tool_buttons})==1,'all_seven_tools_on_one_baseline')
        first,second=bar.tool_buttons[:2];gap=QPoint((first.geometry().right()+second.x())//2,DIAMETER//2+2)
        require(not bar.mask().contains(gap)and bar.mask().contains(first.geometry().center()),'window_region_contains_buttons_but_excludes_empty_gap')
        # Hit-test only our own background, never a game or another application.
        left,top,_,_=win32gui.GetWindowRect(int(bar.winId()));dpr=bar.devicePixelRatioF()
        point=(left+round(gap.x()*dpr),top+round(gap.y()*dpr))
        require(win32gui.WindowFromPoint(point)==int(probe.winId()),'native_gap_hit_test_reaches_owned_background_window')
        image=bar.grab();pixels=image.toImage();scale=image.devicePixelRatioF()
        require(pixels.pixelColor(round(gap.x()*scale),round(gap.y()*scale)).alpha()==0,'actual_idle_gap_pixels_are_transparent')
        window.player_idle_toolbar_image=image
        old_right=bar.x()+bar.width();button=bar.buttons['工具设置']
        QTest.mouseMove(button,QPoint(16,16));QTest.qWait(240);gui.processEvents()
        require(button.width()==DIAMETER+LABEL_SPACE and button._target,'real_mouse_hover_expands_settings_name_in_button')
        require(bar.x()+bar.width()==old_right,'hover_expansion_keeps_right_edge_stationary')
        require(area.contains(bar.geometry()),'expanded_toolbar_stays_in_available_screen')
        QTest.mouseClick(button,Qt.MouseButton.LeftButton,pos=QPoint(16,16));gui.processEvents()
        require(bar.settings_popup.isVisible()and not window.isVisible(),'actual_settings_button_keeps_native_compact_navigation')
        bar.settings_popup.close();QTest.mouseMove(probe,QPoint(5,5));QTest.qWait(240);gui.processEvents()
        require(all(b.width()==DIAMETER for b in bar.tool_buttons),'leaving_buttons_returns_to_round_faces')
        bar.activateWindow();gui.processEvents();previous=bar.buttons['干员与技能'];previous.setFocus(Qt.FocusReason.OtherFocusReason)
        QTest.keyClick(previous,Qt.Key.Key_Tab);QTest.qWait(220);gui.processEvents()
        require(button._keyboard and button.width()==DIAMETER+LABEL_SPACE,'owned_keyboard_focus_exposes_name_and_focus_indicator')
        QTest.keyClick(button,Qt.Key.Key_Space);gui.processEvents()
        require(bar.settings_popup.isVisible(),'owned_space_key_activates_selected_tool_without_external_key_injection')
        bar.settings_popup.close();button.clearFocus();gui.processEvents()
        clicked=[];first.clicked.connect(lambda:clicked.append(True));origin=bar.pos()
        QTest.mousePress(first,Qt.MouseButton.LeftButton,pos=QPoint(16,16));QTest.mouseMove(first,QPoint(-20,16));QTest.mouseRelease(first,Qt.MouseButton.LeftButton,pos=QPoint(16,16));gui.processEvents()
        require(bar.pos()!=origin and not clicked,'dragging_icon_moves_toolbar_without_opening_a_tool')
        bar._drag_dock(QPoint(100000,100000));gui.processEvents()
        require(area.contains(bar.geometry()),'dragged_toolbar_is_clamped_to_screen_work_area')
        QTest.mouseClick(bar.buttons['地图与节点'],Qt.MouseButton.LeftButton,pos=QPoint(16,16));gui.processEvents()
        require(bar.map_popup.isVisible(),'actual_map_icon_opens_existing_map_panel')
        selected=bar.map_popup.panel.details_toggle.isChecked();bar.toggle_visibility();gui.processEvents()
        require(not bar.isVisible()and not bar.map_popup.isVisible(),'existing_hide_action_hides_toolbar_and_open_map')
        bar.toggle_visibility();gui.processEvents()
        require(bar.isVisible()and bar.map_popup.isVisible()and bar.map_popup.panel.details_toggle.isChecked()==selected,'restore_retains_existing_map_reading')
        bar.map_popup.close();bar.buttons['场景笔记'].setEnabled(True)
        QTest.mouseClick(bar.buttons['场景笔记'],Qt.MouseButton.LeftButton,pos=QPoint(16,16));gui.processEvents()
        require(bar.recent_notes_popup.isVisible(),'actual_notebook_icon_retains_scene_notebook_entry')
        bar.recent_notes_popup.close();bar.refresh()
        QTest.mouseMove(bar.buttons['工具设置'],QPoint(16,16));QTest.qWait(240);gui.processEvents()
        require(bar.buttons['工具设置']._amount==1.,'final_native_window_contains_fully_expanded_name_capsule')
        window.player_validation_target=bar
        require(window.run.state==before,'toolbar_appearance_does_not_modify_run_state')
    finally:probe.close();probe.deleteLater()
