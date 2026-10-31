from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import json,sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtCore import Qt,QPoint
from PySide6.QtTest import QTest
from rouge import player_acceptance
from rouge.player_notes import content_key
from player_ui_verification import run
out=R/'verification/maintenance/notebook-layout-review-20261031/native-final'
out.mkdir(exist_ok=False);images=[]

def check(section,w,gui,require):
    w.show_compact();bar=w.compact_window;bar.open_recent_notes();gui.processEvents()
    popup=bar.recent_notes_popup;p=popup.panel;e=w.player_notes;popup.resize(900,360);gui.processEvents()
    combo=p.selector.floor;combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home);QTest.keyClick(combo,Qt.Key.Key_Down);gui.processEvents()
    require(p.context is not None,'actual_floor_picker_selects_note')
    require(not p.options.isVisible()and not e.pages.tabBar().isVisible(),'default_compact_surface_hides_extra_controls')
    require(p.save_state.isVisible()and p.card_title.isVisible(),'top_save_state_and_card_title_visible')
    def image(name):
        gui.processEvents();file=out/(name+'.png');assert popup.grab().save(str(file));images.append({'path':file.relative_to(R).as_posix(),'sha256':sha256(file.read_bytes()).hexdigest()})
    def click_body():
        QTest.mouseClick(p.preview.viewport(),Qt.MouseButton.LeftButton,pos=QPoint(15,15));gui.processEvents()
        require(p.stack.currentWidget()is e and e.isVisible(),'actual_body_click_opens_same_editor')
    def blur():
        QTest.mouseClick(p,Qt.MouseButton.LeftButton,pos=QPoint(p.width()-12,p.height()-8));QTest.qWait(80);gui.processEvents()
    key=content_key(p.context);image('empty-note')
    click_body();require(e.key==key and e.store is p.store,'one_editor_one_store_exact_note_key')
    e.editor.setPlainText('# 第一层\n\n- 注意关卡机制。');QTest.qWait(1100);gui.processEvents()
    require(not e.dirty and '注意关卡机制'in e.store.read(key)[0],'native_idle_timer_autosaves_same_markdown');image('inline-edit')
    blur();require(p.stack.currentWidget()is p.preview,'actual_blank_surface_click_returns_to_markdown_reading')
    require('注意关卡机制'in p.preview.toPlainText()and p.save_state.text()=='已保存','reading_and_save_badge_reflect_saved_note');image('inline-reading')
    p.more.click();gui.processEvents();require(p.options.isVisible(),'actual_more_button_reveals_existing_actions')
    for name,widget in [('save',e.save_button),('discard',e.discard_button),('export',e.export_button),('follow',p.follow)]:
        require(widget.isVisible(),'original_'+name+'_action_still_available')
    e.autosave.setChecked(False);p.more.click();click_body();e.editor.insertPlainText('\n手动草稿');draft=e.editor.toPlainText();blur()
    require(e.dirty and p.stack.currentWidget()is e and e.editor.toPlainText()==draft,'manual_draft_is_not_hidden_or_saved_on_blank_click')
    require('手动草稿'not in e.store.read(key)[0],'manual_draft_does_not_autowrite')
    require(not popup.close()and popup.isVisible(),'close_still_refuses_manual_draft')
    p.more.setChecked(True);e.discard_button.click();e.autosave.setChecked(True);p.more.click();p.open_editor(p.context)
    e.editor.setFocus();e.editor.setPlainText('当前冲突草稿');e.store.path(key).write_text('外部保存原件','utf8');blur()
    require(e.dirty and not e.autosave.isChecked()and p.more.isChecked(),'conflict_preserves_draft_and_reveals_details')
    require(e.editor.toPlainText()=='当前冲突草稿'and e.store.read(key)[0]=='外部保存原件','both_versions_survive_conflict');image('conflict-visible')
    e.discard();e.autosave.setChecked(True);p.more.setChecked(False);p.request_edit();gui.processEvents()
    for width,height in [(720,420),(1100,450),(900,360)]:
        popup.resize(width,height);gui.processEvents();p.fit_content()
        require(p.card.geometry().bottom()<=p.height(),'card_fits_'+str(width)+'x'+str(height))
    image('reading-after-resize')
    archived={'kind':'note-scope','title':'旧分类笔记','variant_id':'["old-version","floor1",null]'}
    archived_key=content_key(archived);e.store.save(archived_key,'旧笔记原文',e.store.read(archived_key)[1])
    require(p.open_for_context(archived,allow_archived=True),'saved_archived_note_opens_exact_existing_key')
    require('原分类暂不可核对' in p.card_title.text() and not p.options.isVisible(),'archived_warning_visible_without_advanced_actions');image('archived-note')
    w.player_validation_target=popup

with patch.object(player_acceptance,'check',check):code=run(999,out/'receipt.json')
(out/'images.json').write_text(json.dumps({'images':images,'isolated_fixtures_not_game_samples':True},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(code)
