from unittest.mock import patch
from PySide6.QtWidgets import QMessageBox

def check(window,gui,require):
    notes=window.player_notes;require(notes.set_context({'kind':'battle','title':'隔离导出示例','variant_id':'owned-export'}),'manual_export_has_exact_note_context')
    notes.editor.setPlainText('# 已保存正文');require(notes.save(),'export_fixture_note_saved')
    notes.editor.setPlainText('# 当前未保存修改\n\n- 只导出到隔离目录');notes.show();gui.processEvents();original=notes.store.read(notes.key)[0];target=notes.store.folder/'exported-owned-fixture.md'
    from . import player_note_export_ui as ui
    with patch.object(ui.QFileDialog,'getSaveFileName',return_value=(str(target),'Markdown笔记 (*.md)')):
        notes.export_button.click();gui.processEvents()
    require(target.read_text('utf8')==notes.editor.toPlainText(),'manual_export_uses_current_edit_exactly')
    require(notes.dirty and notes.store.read(notes.key)[0]==original,'export_does_not_save_or_rebind_scene_note')
    require('未保存修改'in notes.status.text(),'unsaved_state_explained_after_export')
    target.write_text('已有的外部文字','utf8')
    with patch.object(ui.QFileDialog,'getSaveFileName',return_value=(str(target),'Markdown笔记 (*.md)')),patch.object(ui.QMessageBox,'question',return_value=QMessageBox.StandardButton.No):
        notes.export_button.click();gui.processEvents()
    require(target.read_text('utf8')=='已有的外部文字','declining_overwrite_keeps_existing_file')
    with patch.object(ui.QFileDialog,'getSaveFileName',return_value=(str(target),'Markdown笔记 (*.md)')),patch.object(ui.QMessageBox,'question',return_value=QMessageBox.StandardButton.Yes):
        notes.export_button.click();gui.processEvents()
    require(target.read_text('utf8')==notes.editor.toPlainText(),'explicit_overwrite_updates_only_selected_export')
    with patch.object(ui.QFileDialog,'getSaveFileName',return_value=('','')):require(not ui.export_editor(notes),'cancelled_file_picker_has_no_export')
    require(notes.dirty and notes.store.read(notes.key)[0]==original,'export_paths_do_not_mark_local_note_saved')
    raced=notes.store.folder/'changed-during-owned-picker.md'
    def change_during_picker(*args,**kwargs):
        notes.editor.setPlainText('# 在选择位置期间修改');return str(raced),'Markdown笔记 (*.md)'
    with patch.object(ui.QFileDialog,'getSaveFileName',side_effect=change_during_picker):
        require(not ui.export_editor(notes),'changed_edit_during_file_picker_is_not_exported')
    require(not raced.exists() and notes.editor.toPlainText()=='# 在选择位置期间修改','changed_edit_remains_and_no_new_export_created')
    prior_export=target.read_bytes()
    def change_during_confirmation(*args,**kwargs):
        notes.editor.setPlainText('# 在覆盖确认期间修改');return QMessageBox.StandardButton.Yes
    with patch.object(ui.QFileDialog,'getSaveFileName',return_value=(str(target),'Markdown笔记 (*.md)')),patch.object(ui.QMessageBox,'question',side_effect=change_during_confirmation):
        require(not ui.export_editor(notes),'changed_edit_during_overwrite_confirmation_is_not_exported')
    require(target.read_bytes()==prior_export and notes.dirty and notes.store.read(notes.key)[0]==original,'changed_confirmation_preserves_existing_export_and_local_original')
    notes.discard();notes.pages.setCurrentIndex(1);notes.refresh_preview();window.player_validation_target=notes

