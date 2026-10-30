"""Read-only note follow/reset, clean reopen and local search in an isolated app."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import argparse,json,sys,os
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args();original=player_acceptance.check;images=[]
    def check(section,window,gui,require):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from rouge.player_notes import content_key
        from rouge.player_note_library import NoteLibrary
        from rouge import player_note_selector as selector,current_event_directory as events,current_event_resources as resources,current_event_item_uses as uses
        import win32gui,win32process
        original(section,window,gui,require);before=deepcopy(window.run.state);notes=window.player_notes;bar=window.compact_window
        def save(widget,name):
            gui.processEvents();h=int(widget.winId());require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_visible_owned')
            path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_image_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest(),'visible_owned_at_save':True})
        try:
            a={'kind':'battle','title':'隔离笔记示例','variant_id':'owned-normal'};b={**a,'variant_id':'owned-emergency'};store=notes.store
            for context,text in((a,'# 普通说明\n\n这是一份本机保存的示例。'),(b,'# 紧急说明\n\n这份记录与普通版本分开。')):store.save(content_key(context),text,store.read(content_key(context))[1])
            window.run.state['last_node_content']=a;bar.open_recent_notes();panel=bar.recent_notes_popup.panel;panel.follow.setChecked(True);panel.refresh(force=True);gui.processEvents()
            require(len(panel.selector.rows)==539,'full_current_note_catalogue_available_after_runtime_repair')
            require([panel.selector.layout().itemAtPosition(0,i).widget().text()for i in range(4)]==['主题','层数','节点','详情'],'selector_has_video_style_four_clear_headers')
            save(bar.recent_notes_popup,'notebook-selector')
            panel.follow.click();notes.autosave.setChecked(False);notes.set_context(a);notes.editor.setPlainText('隔离未保存草稿，必须保留。')
            window.run.reset(save=False);panel.refresh(force=True);gui.processEvents()
            require(panel.context is None and panel.preview.toPlainText()==''and not panel.edit.isEnabled(),'real_run_identity_reset_clears_old_paused_preview')
            require(notes.dirty and notes.key==content_key(a)and notes.editor.toPlainText()=='隔离未保存草稿，必须保留。','new_run_does_not_delete_or_rebind_unsaved_editor')
            require('本机保存'in store.read(content_key(a))[0],'new_run_keeps_saved_note_original');save(bar.recent_notes_popup,'new-run-reading-cleared')
            panel.select_context(b);require(panel.context==b and not panel.follow.isChecked(),'explicit_manual_choice_after_reset_stays_selected')
            notes.discard();notes.set_context(a);notes.close();store.path(content_key(a)).write_text('# 外部更新\n\n再次打开会读到这份已保存内容。','utf8')
            panel.select_context(a);panel.edit.click();gui.processEvents()
            require(notes.isVisible()and'再次打开'in notes.editor.toPlainText()and not notes.dirty,'actual_edit_click_reopens_clean_note_with_external_update')
            save(notes,'clean-note-reopened')
            notes.close();bar.open_recent_notes();target=panel.selector.rows[0]['context'];panel.select_context(target)
            with patch.object(selector.events,'packet',return_value=None):
                panel.reload.click();gui.processEvents();require(panel.selector.rows and all(r['context']['kind']=='reference-stage'for r in panel.selector.rows),'event_classifier_loss_keeps_verified_stage_picker')
                require(panel.selector.notice.isVisible()and'事件分类'in panel.selector.notice.text(),'partial_catalogue_explains_exact_missing_classifier');save(bar.recent_notes_popup,'partial-note-catalogue')
            panel.reload.click();require(len(panel.selector.rows)==539,'manual_reload_recovers_all_note_categories')
            for context in(a,b):NoteLibrary(store.folder).record(context)
            bar.open_note_library();library=bar.note_library;gui.processEvents()
            for text in('外','外部','外部更新'):library.search.setText(text)
            QTest.qWait(210);gui.processEvents();require(library.entries.count()==1,'search_burst_returns_matching_saved_body')
            require(library.objectName()=='sceneNotesLibrary'and'background:white'in library.styleSheet(),'saved_note_library_reuses_light_palette')
            library.entries.setCurrentRow(0);save(library,'saved-note-library')
            require(events.packet()is not None and len(events.reference()['rows'])==39,'current_event_directory_recovers_all_retained_events')
            require(len(resources.reference()['rows'])==88 and len(uses.reference()['rows'])==12,'resource_and_item_directories_recover_without_changed_values')
            notes.discard();notes.autosave.setChecked(True);bar.open_recent_notes();panel.select_context(a);panel.timer.stop();window.player_validation_target=bar.recent_notes_popup
        finally:window.run.state=before
    player_acceptance.check=check;code=run(411,args.receipt)
    args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'isolated_public_fixtures_only':True,'real_user_state_used':False,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8');raise SystemExit(code)
