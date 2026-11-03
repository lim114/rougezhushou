from copy import deepcopy
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QPushButton

def check(window,gui,require):
    from .player_notes import content_key
    old=deepcopy(window.run.state);window.show_compact();bar=window.compact_window;notes=window.player_notes
    first={'kind':'battle','title':'隔离示例 · 林间作战','variant_id':'validation-normal'}
    other={**first,'variant_id':'validation-emergency'}
    for row,text in((first,'# 林间作战\n\n- 注意第二阶段的机制。\n- 先查看敌人资料，再决定自己的准备。'),(other,'# 紧急作战\n\n这是另一份独立备忘录。')):
        key=content_key(row);notes.store.save(key,text,notes.store.read(key)[1])
    window.run.state['last_node_content']=first;bar.refresh()
    QTest.mouseClick(bar.buttons['场景笔记'],Qt.MouseButton.LeftButton);gui.processEvents()
    popup=bar.recent_notes_popup;panel=popup.panel
    require(popup.isVisible()and panel.context==first,'actual_toolbar_click_opens_recent_scene_notebook')
    require('第二阶段'in panel.preview.toPlainText(),'matching_saved_note_automatically_presented')
    require('最近读取'in panel.scene.text()and'不表示当前'in panel.status.text(),'recent_read_not_claimed_as_current_position')
    require(panel.preview.isReadOnly(),'automatic_scene_preview_is_read_only')
    QTest.mouseClick(panel.edit,Qt.MouseButton.LeftButton);gui.processEvents()
    require(notes.isVisible()and notes.key==content_key(first),'actual_edit_button_routes_existing_exact_note_editor')
    notes.editor.insertPlainText('\n尚未保存的计划');dirty=notes.editor.toPlainText()
    window.run.state['last_node_content']=other;panel.refresh(force=True)
    require(notes.key==content_key(first)and notes.dirty and notes.editor.toPlainText()==dirty,'scene_follow_does_not_overwrite_or_move_unsaved_editor')
    require('另一份独立'in panel.preview.toPlainText(),'same_name_variant_uses_its_own_saved_note')
    notes.discard();notes.close();bar.open_recent_notes();gui.processEvents()
    panel.follow.click();window.run.state['last_node_content']=first;bar.refresh();gui.processEvents()
    require(panel.context==other and'暂停'in panel.scene.text(),'pause_retains_reading_with_explicit_status')
    panel.follow.click();gui.processEvents();require(panel.context==first,'resume_uses_latest_confirmed_scene')
    key=content_key(first);notes.store.save(key,'# 本机更新\n\n外部修改已读取。',notes.store.read(key)[1])
    QTest.qWait(2200);gui.processEvents()
    require('外部修改'in panel.preview.toPlainText(),'visible_notebook_timer_follows_external_saved_change')
    panel.reload.click();gui.processEvents();require('外部修改'in panel.preview.toPlainText(),'real_refresh_button_reads_new_saved_text')
    window.run.state['last_node_content']=None;bar.refresh();gui.processEvents()
    require(panel.preview.toPlainText()==''and not panel.edit.isEnabled(),'missing_scene_clears_old_preview_and_edit_target')
    window.run.state['last_node_content']=first;bar.refresh();gui.processEvents()
    require(panel.context==first,'new_confirmed_scene_recovers_without_mutating_saved_note')
    require('#sceneNotesSurface'in popup.styleSheet()and'background:white'in panel.styleSheet(),'light_surface_and_white_note_card_style_installed')
    panel.preview.linkBlocked.emit();require('不会自动打开'in panel.status.text(),'note_links_do_not_launch_external_apps')
    panel.reload.click()
    close=popup.findChild(QPushButton,'popoverCloseButton');QTest.mouseClick(close,Qt.MouseButton.LeftButton);gui.processEvents()
    require(not popup.isVisible(),'actual_notebook_close_button_closes_only_reading_window')
    bar.open_recent_notes();gui.processEvents();require(popup.isVisible(),'toolbar_reopens_existing_notebook_with_saved_reading')
    panel.timer.stop()
    window.player_validation_target=popup
    window.run.state=old
    require(window.run.state==old,'owned_fixture_run_restored_before_external_guard')
