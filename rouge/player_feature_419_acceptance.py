def check(window,gui,require):
 from .player_notes import content_key
 window.show_compact();c=window.compact_window;c.open_recent_notes();gui.processEvents();panel=c.recent_notes_popup.panel;selector=panel.selector
 require(len(selector.rows)>0,'pinned_note_scene_directory_available')
 floor=selector.floor.findData('floor1');selector.floor.setCurrentIndex(floor);gui.processEvents();require(selector.scene.count()>0,'first_floor_note_branches_available')
 # The first entry now opens this range's general note; retain this scenario's
 # original exact-reference assertion by selecting the first detailed entry.
 selector.scene.setCurrentIndex(1);selector.select();gui.processEvents();target=selector.scene.currentData();require(panel.context==target and not panel.follow.isChecked(),'manual_reference_pauses_follow')
 require('手选固定资料'in panel.scene.text(),'manual_reference_not_current_position_claim')
 panel.refresh(force=True);require(panel.context==target,'same_refresh_preserves_manual_note')
 editor=window.player_notes;editor.set_context(target);editor.editor.setPlainText('隔离未保存笔记');old=editor.key
 other=next(r['context']for r in selector.rows if content_key(r['context'])!=old);require(not editor.set_context(other)and editor.key==old,'dirty_editor_not_rebound_by_other_scene');editor.discard()
 require(not editor.dirty,'isolated_unsaved_text_discarded_without_private_write')
 require(c.recent_notes_popup.isVisible(),'pale_scene_note_picker_visible');window.player_validation_target=c.recent_notes_popup
