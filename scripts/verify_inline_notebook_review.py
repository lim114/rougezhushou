"""Actual one-window notebook controls, using only isolated public fixtures."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import argparse,json,os,sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    original=player_acceptance.check;images=[]
    def check(section,window,gui,require):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QPushButton
        from rouge.player_note_scopes import scope
        from rouge.player_notes import content_key
        from rouge.player_reference_notes import open_note
        import win32gui,win32process
        original(section,window,gui,require)
        state=deepcopy(window.run.state);bar=window.compact_window;notes=window.player_notes
        def save(widget,name):
            gui.processEvents();h=int(widget.winId());require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
            path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_image_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest(),'visible_owned_at_save':True})
        def choose(combo,data):
            index=combo.findData(data);require(index>=0,'picker_contains_'+str(data))
            combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home)
            for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
            gui.processEvents();require(combo.currentData()==data,'actual_keyboard_selects_'+str(data))
        try:
            notes.discard();notes.autosave.setChecked(True);bar.open_recent_notes();popup=bar.recent_notes_popup;panel=popup.panel;panel.timer.start()
            choose(panel.selector.floor,'floor1');floor=scope(panel.selector.rows,'floor1')
            require(panel.context==floor and not panel.follow.isChecked(),'user_floor_choice_opens_manual_general_note_without_live_claim')
            panel.more.setChecked(True);gui.processEvents();QTest.mouseClick(panel.edit,Qt.MouseButton.LeftButton);gui.processEvents()
            require(notes.isVisible()and not notes.isWindow()and notes.window()is popup,'existing_editor_is_child_of_same_actual_notebook_window')
            require(panel.store is notes.store and notes.key==content_key(floor),'one_store_and_exact_floor_note_key')
            notes.editor.setPlainText('# 第一层\n\n先核对节点资料，再准备队伍。');QTest.qWait(1100);gui.processEvents()
            require(not notes.dirty and '第一层'in notes.store.read(notes.key)[0],'native_timer_saves_general_floor_note');save(popup,'inline-edit')
            QTest.mouseClick(panel.parent_toggle,Qt.MouseButton.LeftButton);gui.processEvents()
            require(len(panel.parent_views)==1 and panel.parent_views[0].isReadOnly(),'parent_topic_card_is_read_only')
            parent_button=panel.parent_layout.itemAt(0).widget();QTest.mouseClick(parent_button,Qt.MouseButton.LeftButton);gui.processEvents()
            topic=scope(panel.selector.rows);require(notes.key==content_key(topic),'actual_parent_button_opens_topic_in_same_editor')
            notes.editor.setPlainText('# 黑流树海通用提醒\n\n只记录自己想保存的资料。');QTest.qWait(1100);gui.processEvents();require(not notes.dirty,'topic_note_auto_saved_locally')
            choose(panel.selector.floor,'floor1');choose(panel.selector.node,'普通作战');node=scope(panel.selector.rows,'floor1','普通作战')
            require(notes.key==content_key(node),'node_general_note_is_distinct_from_floor_and_topic')
            notes.editor.setPlainText('# 普通作战\n\n- 留意关卡机制。');QTest.qWait(1100);gui.processEvents()
            require(len(panel.parent_views)==2 and '通用提醒'in panel.parent_views[0].toPlainText()and'第一层'in panel.parent_views[1].toPlainText(),'topic_and_floor_reading_visible_above_child_note')
            save(popup,'parent-notes')
            notes.pages.setCurrentIndex(1);gui.processEvents();require('普通作战'in notes.preview.toPlainText(),'markdown_preview_in_same_window');save(popup,'inline-preview')
            notes.pages.setCurrentIndex(0);notes.autosave.setChecked(False);notes.editor.insertPlainText('\n尚未保存，不能丢失。');draft=notes.editor.toPlainText();QTest.keyClick(notes,Qt.Key.Key_Escape);gui.processEvents()
            require(notes.isVisible()and notes.dirty and notes.editor.toPlainText()==draft,'escape_keeps_unsaved_embedded_draft')
            close=popup.findChild(QPushButton,'popoverCloseButton');QTest.mouseClick(close,Qt.MouseButton.LeftButton);gui.processEvents()
            require(popup.isVisible()and notes.dirty and notes.editor.toPlainText()==draft,'actual_notebook_close_refuses_unsaved_manual_draft')
            notes.store.path(notes.key).write_text('外部保存的另一份内容','utf8');notes.autosave.setChecked(True);notes.save_pending();gui.processEvents()
            require(notes.dirty and not notes.autosave.isChecked()and notes.editor.toPlainText()==draft and notes.store.read(notes.key)[0]=='外部保存的另一份内容','external_conflict_keeps_both_versions_and_pauses_autosave')
            save(popup,'draft-conflict')
            notes.discard();notes.autosave.setChecked(True);notes.editor.setPlainText('# 普通作战\n\n这是保留后的本机笔记。');QTest.qWait(1100);gui.processEvents()
            bar.open_note_library();library=bar.note_library;library.search.setText('第一层');QTest.qWait(210);gui.processEvents()
            entry=next(i for i,row in enumerate(library.rows)if row['content']==floor);library.entries.setCurrentRow(entry)
            QTest.mouseClick(library.open_button,Qt.MouseButton.LeftButton);gui.processEvents()
            require(popup.isVisible()and notes.window()is popup and notes.key==content_key(floor),'saved_generic_note_reopens_in_same_notebook_and_correct_scope')
            target=next(r['context']for r in panel.selector.rows if r['context']['kind']=='reference-stage')
            require(open_note(window,target),'fixed_reference_note_entry_opens_shared_notebook')
            gui.processEvents();require(notes.key==content_key(target)and notes.window()is popup and panel.selector.scene.currentData()==target,'exact_reference_entry_has_no_second_editor_window')
            notes.pages.setCurrentIndex(1);save(popup,'exact-reference-note')
            from rouge.player_note_library import NoteLibrary
            archived={'kind':'note-scope','title':'黑流树海 · 第1层','variant_id':json.dumps(['archived-isolated-version','floor1',None])};key=content_key(archived)
            old_parent_widgets=list(panel.parent_views)
            notes.store.save(key,'# 旧资料下的笔记\n\n保留原文件身份，不改挂到新版本。',notes.store.read(key)[1]);NoteLibrary(notes.store.folder).record(archived)
            bar.open_note_library();library.search.setText('旧资料');QTest.qWait(210);gui.processEvents();require(library.entries.count()==1,'archived_note_found_by_saved_text');library.entries.setCurrentRow(0)
            QTest.mouseClick(library.open_button,Qt.MouseButton.LeftButton);gui.processEvents()
            require(notes.key==key and '旧资料'in notes.editor.toPlainText()and'原分类暂不可核对'in panel.scene.text(),'actual_library_reopens_archived_note_under_original_key')
            from shiboken6 import isValid
            require(not panel.parent_views and panel.selector.scene.currentData()is None and all(not isValid(v)or not v.isVisible()for v in old_parent_widgets),'archived_note_does_not_borrow_current_parent_notes');save(popup,'archived-note')
            require(window.run.state==state,'notebook_and_parent_navigation_do_not_modify_run')
            notes.discard();notes.autosave.setChecked(True);panel.timer.stop();window.player_validation_target=popup
        finally:window.run.state=state
    player_acceptance.check=check;code=run(411,args.receipt)
    args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'isolated_public_fixtures_only':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
    raise SystemExit(code)
