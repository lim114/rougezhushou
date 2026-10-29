from copy import deepcopy
from unittest.mock import patch
from PySide6.QtCore import Qt,QPoint
from PySide6.QtTest import QTest

def check(window,gui,require):
    from . import expansion_reference as model
    from .player_reference_notes import note_for,reference_target,open_reference
    before=deepcopy(window.run.state);rows=model.rows('stages',changes_only=False);first=next(row for row in rows if row['name'].strip());context=note_for('stages',first['id'])
    panel=window.reference_panel('stages');panel.search.clear();panel.stage_floor.setCurrentIndex(0);panel.stage_kind.setCurrentIndex(0);panel.refresh_reference()
    for index in range(panel.entries.count()):
        if panel.entries.item(index).data(Qt.ItemDataRole.UserRole)==first['id']:panel.entries.setCurrentRow(index);break
    window.show();gui.processEvents();menu=panel.query_menu.menu;menu.popup(panel.query_menu.button.mapToGlobal(QPoint(0,panel.query_menu.button.height())));gui.processEvents();action=panel.reference_note_action
    require(action.isVisible()and not menu.actionGeometry(action).isEmpty(),'exact_selected_reference_note_is_real_visible_menu_entry')
    QTest.mouseClick(menu,Qt.MouseButton.LeftButton,pos=menu.actionGeometry(action).center());gui.processEvents();notes=window.player_notes
    require(notes.isVisible()and notes.content==context,'actual_menu_click_opens_exact_versioned_manual_note')
    notes.editor.setPlainText('# 固定关卡笔记\n\n- 注意入口与机制');require(notes.save(),'manual_reference_note_saved_only_to_owned_temporary_folder')
    require(notes.reference_button.isVisible(),'manual_note_has_exact_reference_return_entry')
    notes.editor.insertPlainText('\n尚未保存');key=notes.key;notes.reference_button.click();gui.processEvents()
    require(window.isVisible()and panel.result['row']['id']==first['id'],'note_source_button_selects_exact_reference_row')
    require(notes.key==key and notes.dirty,'source_navigation_does_not_discard_or_rebind_unsaved_note')
    with patch.object(model,'packet',return_value=None):
        require(not open_reference(window,context),'lost_source_does_not_open_same_name_alternative')
        require(notes.key==key and notes.dirty,'source_loss_preserves_personal_edit')
    notes.discard();window.show_compact();bar=window.compact_window;bar.open_note_library();gui.processEvents();library=bar.note_library;library.refresh();library.entries.setCurrentRow(0)
    require(library.reference_button.isEnabled(),'saved_reference_note_library_exposes_verified_return')
    library.reference_button.click();gui.processEvents();require(panel.result['row']['id']==first['id']and window.isVisible(),'library_link_returns_to_same_fixed_reference')
    window.show_compact();bar.open_saved_note(context);notes.pages.setCurrentIndex(1);notes.refresh_preview();window.player_validation_target=notes
    require(window.run.state==before,'manual_reference_note_never_changes_current_run_or_scene')

