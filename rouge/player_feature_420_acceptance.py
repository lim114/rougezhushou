def check(window,gui,require):
 from PySide6.QtTest import QTest
 from .player_reference_notes import note_for
 from . import expansion_reference as model
 window.show_compact();notes=window.player_notes;target=note_for('stages',model.rows('stages',changes_only=False)[0]['id']);require(notes.set_context(target),'exact_note_target_loaded');notes.show()
 require(notes.autosave.isChecked(),'local_auto_save_enabled')
 notes.editor.setPlainText('# 测试笔记\n\n- 此处是隔离验证正文。\n- 停止输入后自动保存在本机。');QTest.qWait(1100);gui.processEvents()
 require(not notes.dirty and '测试笔记'in notes.store.read(notes.key)[0],'native_timer_saves_exact_markdown')
 from PySide6.QtGui import QTextCursor
 notes.editor.moveCursor(QTextCursor.MoveOperation.End);notes.editor.insertPlainText('\n待保存的第二稿');notes.store.path(notes.key).write_text('外部窗口的测试正文','utf8');QTest.qWait(1100);gui.processEvents()
 require(notes.dirty and not notes.autosave.isChecked(),'native_conflict_pauses_autosave')
 require(notes.editor.toPlainText().endswith('待保存的第二稿')and notes.store.read(notes.key)[0]=='外部窗口的测试正文','both_versions_preserved_on_conflict')
 notes.discard();notes.autosave.setChecked(True);notes.editor.setPlainText('# 战斗要点\n\n- 对应准确资料，不代表当前所在位置。\n- 笔记只保存到本机，不会上传。');QTest.qWait(1100);gui.processEvents();require(not notes.dirty,'auto_save_resumes_after_explicit_reread');notes.pages.setCurrentIndex(1);notes.show();gui.processEvents();window.player_validation_target=notes
