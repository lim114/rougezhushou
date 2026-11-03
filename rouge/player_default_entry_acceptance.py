"""Actual normal player navigation, separate from old-layout diagnostics."""
from PySide6.QtCore import QPoint,Qt
from PySide6.QtWidgets import QApplication,QDialog
from PySide6.QtTest import QTest
import os
import win32gui,win32process
from shiboken6 import isValid

def owned(widget,parent):
    current=widget.parentWidget()
    while current is not None:
        if current is parent:return True
        current=current.parentWidget()
    return False

def check(window,gui,require):
    from .expansion_reference import CATEGORIES
    require(not window.include_historical_route_diagnostics,'normal_player_does_not_enable_historical_route_tools')
    require(type(window.centralWidget()).__name__=='PlayerWorkspace','actual_normal_player_workspace_not_diagnostic_layout')
    done=set()
    for category,_ in CATEGORIES:
        panel=window.reference_panel(category);gui.processEvents()
        require(window.centralWidget().currentWidget()is panel and panel.isVisible(),'normal_exact_category_home_'+category)
        panel.query_menu.sync()
        for button,action in panel.query_menu.actions:
            if not action.isVisible()or not action.isEnabled()or id(button)in done:continue
            done.add(id(button));panel.close_children();gui.processEvents()
            menu=panel.query_menu.menu;menu.popup(panel.query_menu.button.mapToGlobal(QPoint(0,panel.query_menu.button.height())));gui.processEvents()
            require(menu.isVisible()and not menu.actionGeometry(action).isEmpty(),'actual_normal_menu_item_reachable_'+str(len(done)))
            QTest.mouseClick(menu,Qt.MouseButton.LeftButton,pos=menu.actionGeometry(action).center());gui.processEvents()
            dialogs=[widget for widget in QApplication.topLevelWidgets()if isinstance(widget,QDialog)and owned(widget,panel)and widget.isVisible()]
            require(bool(dialogs),'normal_menu_opens_owned_dialog_'+str(len(done)))
            require(all(win32gui.IsWindowVisible(int(dialog.winId()))and win32process.GetWindowThreadProcessId(int(dialog.winId()))[1]==os.getpid()for dialog in dialogs),'normal_child_actual_Windows_owner_'+str(len(done)))
            panel.close_children();gui.processEvents()
            require(all(not isValid(dialog)or not dialog.isVisible()for dialog in dialogs),'normal_entry_closes_its_owned_dialog_'+str(len(done)))
    require(len(done)>=15,'all_documented_normal_menu_entry_families_exercised')
