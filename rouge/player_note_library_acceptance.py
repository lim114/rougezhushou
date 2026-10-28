from pathlib import Path
from PySide6.QtCore import Qt

def check(window,gui,require):
    notes=window.player_notes
    for identity,text in [('normal','普通说明'),('emergency','紧急机关说明')]:
        require(notes.set_context({'kind':'battle','title':'隔离同名关卡','variant_id':identity}),f'note_context_{identity}')
        notes.editor.setPlainText(text);require(notes.save(),f'note_saved_{identity}')
    window.show_compact();bar=window.compact_window;bar.open_note_library();gui.processEvents();library=bar.note_library
    require(library.isVisible()and library.entries.count()==2,'saved_notes_reachable_without_current_scene')
    library.search.setText('机关');gui.processEvents();require(library.entries.count()==1,'library_search_matches_raw_note_body')
    library.entries.setCurrentRow(0);require('紧急机关说明'in library.detail.toPlainText(),'selected_note_readable_in_library')
    require(library.detail.isReadOnly(),'library_preview_never_edits_note_file')
    library.open_button.click();gui.processEvents();require(notes.isVisible()and 'emergency'in notes.key,'library_returns_to_exact_variant_editor')
    notes.editor.setPlainText('未保存的紧急记录');require(not bar.open_note_library(),'dirty_editor_refuses_implicit_close_to_library');gui.processEvents()
    require(notes.dirty and notes.isVisible()and notes.editor.toPlainText()=='未保存的紧急记录'and 'emergency'in notes.key,'library_switch_cannot_discard_dirty_other_note')
    notes.discard();bar.open_note_library();library.search.clear();library.refresh();target=next(i for i,row in enumerate(library.rows)if row['content']['variant_id']=='normal');library.entries.setCurrentRow(target);library.open_button.click();gui.processEvents()
    require('normal'in notes.key and notes.editor.toPlainText()=='普通说明','saved_note_can_reopen_after_explicit_discard')
    bar.open_note_library();library.search.setText('机关');library.entries.setCurrentRow(0);selected=library.entries.currentItem().data(Qt.ItemDataRole.UserRole);library.refresh()
    require(library.entries.currentItem().data(Qt.ItemDataRole.UserRole)==selected,'refresh_keeps_library_selection_and_search')
    window.player_validation_target=library

