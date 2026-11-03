from pathlib import Path

def check(window,gui,require):
    from .player_context import recent_content
    notes=window.player_notes
    require(notes.set_context({'kind':'battle','title':'隔离示例关卡','variant_id':'owned-example'}),'exact_scene_note_binding')
    text='# 关卡提醒\n\n- 先阅读敌人机制\n- 注意地图入口\n\n**只在本机保存**'
    notes.editor.setPlainText(text);notes.show();notes.pages.setCurrentIndex(1);gui.processEvents()
    require(notes.isVisible()and notes.preview.isVisible(),'native_markdown_preview_page_visible')
    require('关卡提醒'in notes.preview.toPlainText()and '**'not in notes.preview.toPlainText(),'markdown_is_readable_without_syntax_marks')
    require(notes.dirty and notes.editor.toPlainText()==text,'preview_keeps_exact_raw_edit_unsaved')
    original=notes.key;require(not notes.set_context({'kind':'event','title':'另一个场景'})and notes.key==original,'dirty_preview_cannot_rebind_to_another_scene')
    notes.close();gui.processEvents();require(notes.isVisible(),'closing_dirty_preview_preserves_edit')
    require(notes.save()and not notes.dirty,'explicit_save_records_exact_markdown')
    require(notes.store.read(original)[0]==text,'saved_note_bytes_match_raw_editor')
    notes.editor.insertPlainText('\n新增内容');notes.discard();require(notes.editor.toPlainText()==text,'discard_restores_own_saved_note_only')
    external='外部窗口的修改';notes.store.path(original).write_text(external,'utf8');notes.editor.setPlainText('当前窗口的修改')
    require(not notes.save()and notes.dirty,'stale_note_conflict_keeps_unsaved_edit')
    require(notes.store.read(original)[0]==external,'stale_note_does_not_overwrite_external_text')
    notes.discard();notes.editor.setPlainText(text);require(notes.save(),'explicit_reread_then_save_supported')
    notes.pages.setCurrentIndex(1);notes.refresh_preview();window.player_validation_target=notes

