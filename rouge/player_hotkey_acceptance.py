"""Native registration and owned queue messages only; no keyboard injection."""
from copy import deepcopy
import ctypes
from ctypes import wintypes
import json
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from .player_hotkey import GlobalHotkey,WM_HOTKEY,load_preferences

def check(window,gui,require):
    window.show_compact();bar=window.compact_window;gui.processEvents()
    prefs=bar.hotkey_path
    require(not prefs.exists(),'startup_does_not_write_default_preferences')
    # Use a distinctive combination. Do not consume the user's plain Tab during tests.
    bar.hotkey_keys.setCurrentText('Ctrl+Alt+Shift+F11');bar.hotkey_apply.click();gui.processEvents()
    require(bar.hotkey.binding is not None,'real_Windows_RegisterHotKey_succeeded')
    require(load_preferences(prefs)[0]['shortcut']=='Ctrl+Alt+Shift+F11','manual_apply_saved_only_isolated_ui_preferences')
    first=bar.hotkey.binding
    other=GlobalHotkey()
    try:
        ok,message=other.configure(True,'Ctrl+Alt+Shift+F11')
        require(not ok and other.binding is None and '占用'in message,'actual_native_conflict_reported_without_stealing')
        other.configure(True,'Ctrl+Alt+Shift+F10');prior=other.binding
        require(prior is not None,'second_native_registration_succeeded')
        require(not other.configure(True,'Ctrl+Alt+Shift+F11')[0]and other.binding==prior,'conflicted_change_keeps_working_old_key')
    finally:other.close()
    bar.hotkey_apply.click();require(bar.hotkey.binding==first,'repeat_apply_not_duplicate_registration')
    bar.hotkey_keys.setCurrentText('Tab');bar.hotkey_single.setChecked(False);bar.hotkey_apply.click()
    require(bar.hotkey.binding==first and '占用'in bar.hotkey_status.text(),'single_Tab_requires_explicit_opt_in')
    bar.hotkey_keys.setCurrentText('Ctrl+Alt+Shift+F11')
    state=deepcopy(window.run.state);bar.open_map();mp=bar.map_popup.panel;mp.details_toggle.setChecked(True)
    mp.type_buttons['诡意行商'].click();selected=mp.view.filter_kind
    original_quit=gui.quitOnLastWindowClosed()
    post=ctypes.WinDLL('user32',use_last_error=True).PostMessageW
    post.argtypes=[wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM];post.restype=wintypes.BOOL
    hwnd=int(bar.hotkey.receiver.winId())
    def toggle():
        i,m,v=bar.hotkey.binding
        require(bool(post(hwnd,WM_HOTKEY,i,m|(v<<16))),'owned_receiver_message_posted')
        QTest.qWait(100);gui.processEvents()
    toggle();require(not bar.isVisible()and not bar.map_popup.isVisible()and not window.isVisible(),'native_dispatch_hides_all_owned_assistant_windows')
    require(not mp.hover_timer.isActive(),'hidden_map_cancels_pending_hover_popup')
    require(bar.hidden_windows is not None and gui.quitOnLastWindowClosed()==original_quit,'hide_preserves_process_policy_and_restore_list')
    toggle();require(bar.isVisible()and bar.map_popup.isVisible()and not window.isVisible(),'native_dispatch_restores_exact_compact_map_view')
    require(mp.view.filter_kind==selected and mp.details_toggle.isChecked(),'restore_preserves_map_filter_and_drawer')
    notes=window.player_notes;notes.set_context({'title':'隔离快捷键测试','kind':'battle'});bar.open_owner_dialog(notes.show,'player_notes');notes.editor.setPlainText('未保存的隔离测试笔记')
    toggle();require(notes.dirty and not notes.isVisible(),'hide_does_not_close_or_discard_dirty_note')
    toggle();require(notes.isVisible()and notes.dirty and notes.editor.toPlainText()=='未保存的隔离测试笔记','restore_keeps_unsaved_text')
    window.close();gui.processEvents();require(not window.closing and bar.hotkey.binding is not None,'refused_dirty_exit_keeps_hotkey_registered')
    notes.discard();notes.close();bar.present(bar.settings_popup)
    require(window.run.state==state,'hotkey_never_changes_run_memory')
    bar.hotkey_enabled.setChecked(False);bar.hotkey_apply.click()
    require(bar.hotkey.binding is None and not bar.hide_button.isEnabled(),'disabled_hotkey_disables_unrecoverable_hide_button')
    probe=GlobalHotkey()
    try:require(probe.configure(True,'Ctrl+Alt+Shift+F11')[0],'disable_releases_actual_OS_shortcut')
    finally:probe.close()
    bar.hotkey_enabled.setChecked(True);bar.hotkey_apply.click();binding=bar.hotkey.binding;bar.hotkey.close();bar.hotkey.close()
    require(bar.hotkey.binding is None,'normal_cleanup_idempotently_unregisters')
    probe=GlobalHotkey()
    try:require(probe.configure(True,'Ctrl+Alt+Shift+F11')[0],'released_shortcut_available_to_new_owner')
    finally:probe.close()
    bar.hotkey=GlobalHotkey(bar);bar.hotkey.triggered.connect(bar.toggle_visibility);bar.hotkey.configure(**bar.hotkey_preferences)
    require(bar.hotkey.binding is not None,'restored_test_registration_for_final_window')
    bar.hotkey_status.setText('隔离验收：注册、冲突、呼出/收起及清理已验证。\n仅向自己的窗口线程投递消息，未向游戏发送任何按键。')
