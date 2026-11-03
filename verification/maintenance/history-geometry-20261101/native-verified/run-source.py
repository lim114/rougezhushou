from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import json,sys,subprocess
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/maintenance/history-geometry-20261101/native-verified'
if len(sys.argv)==1:
 out.mkdir(parents=True)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__)),'child'],stdout=a,stderr=b);print({'actual_retained_PID':p.pid},flush=True);code=p.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance
from rouge.run_state import RunState
from rouge.player_replay_archive import reload_history
from tests.test_history_reader_review import history_example
from tests.test_inventory_modes_446 import observe,KETTLE,OTHER,TOOL
from player_ui_verification import run
images=[]
def check(section,w,gui,require):
 before=deepcopy(w.run.state)
 for timer in w.findChildren(QTimer):timer.stop()
 try:
  w.show_compact();bar=w.compact_window;bar.open_recent_notes();gui.processEvents();popup=bar.recent_notes_popup;p=popup.panel;e=w.player_notes
  combo=p.selector.floor;combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home);QTest.keyClick(combo,Qt.Key.Key_Down);gui.processEvents();require(p.context is not None,'compact_notes_real_floor_selection_binds_exact_context')
  require(popup.width()==900 and popup.height()==360,'compact_notes_actual_default900_by360')
  QTest.mouseClick(p.preview.viewport(),Qt.MouseButton.LeftButton,pos=QPoint(12,12));gui.processEvents();require(p.stack.currentWidget()is e,'compact_notes_same_editor_opens_from_body')
  text='第一层：先确认关卡机制。';e.editor.setPlainText(text);gui.processEvents();require(p.stack.height()<150 and e.editor.verticalScrollBar().maximum()==0,'compact_notes_short_text_fits_without_scrollbar')
  short=p.stack.height();e.editor.setPlainText('\n'.join('机制提醒'+str(i)for i in range(8)));gui.processEvents();require(p.stack.height()>short,'compact_notes_native_editor_grows_for_more_actual_lines')
  e.editor.setPlainText(text);require(e.save(),'compact_notes_explicit_save_uses_existing_temporary_store');e.editor.clearFocus();p.leave_editor();gui.processEvents();require(p.stack.currentWidget()is p.preview and p.preview.toPlainText()==text,'compact_notes_blur_returns_exact_saved_reading')
  def image(widget,name):
   gui.processEvents();f=out/(name+'.png');assert widget.grab().save(str(f));images.append({'file':f.relative_to(R).as_posix(),'sha256':sha256(f.read_bytes()).hexdigest()})
  image(popup,'plain-note')
  QTest.mouseClick(p.preview.viewport(),Qt.MouseButton.LeftButton,pos=QPoint(12,12));gui.processEvents();long='较长的中文机制提醒，需要自动换行。'*300;e.editor.setPlainText(long);popup.resize(640,420);gui.processEvents();require(e.editor.verticalScrollBar().maximum()>0 and e.editor.toPlainText()==long,'compact_notes_narrow_long_paragraph_scrolls_without_loss');require(p.card.geometry().bottom()<=p.height(),'compact_notes_narrow_card_inside_actual_window')
  e.editor.setPlainText(text);e.save();e.editor.clearFocus();p.leave_editor();gui.processEvents();bar.open_replay();gui.processEvents();history=bar.replay_popup;rp=history.panel;(out/'portrait-current.json').write_text(json.dumps({'requested':[640,650],'actual':[history.width(),history.height()],'exact_portrait_target_passed':history.width()==640 and history.height()==650,'original_three_failures_retained':True,'target_restored_without_lower_threshold':True},indent=2)+'\n','utf8');require(history.width()==640 and history.height()==650,'compact_history_actual_default640_by650')
  state,t,ids=history_example();state['id']='public-compact-history';fixture=RunState(Path(w.run.file).parent/'public-count-fixture.json');observe(fixture,[KETTLE]*3+[OTHER,TOOL])
  for key in('relics','tactical_tools','relic_count','inventory_verified','relic_icon_memory'):state[key]=deepcopy(fixture.state[key])
  rp.history_store.archive(state);reload_history(rp);gui.processEvents();require(rp.session_cards.count()==2,'compact_history_real_temp_archive_listed_with_current_run');item=next(rp.session_cards.item(i)for i in range(rp.session_cards.count())if rp.session_cards.item(i).data(Qt.ItemDataRole.UserRole)=='archive:public-compact-history')
  require('已确认藏品 4 件'in item.text(),'compact_history_kettle_copy_count_matches_confirmed_slots');require('结算分数与种子尚未确认'in item.toolTip()and len(item.text().splitlines())==3,'compact_history_canonical_scope_retained_beside_short_card')
  image(history,'compact-session-cards');rp.session_cards.scrollToItem(item);gui.processEvents();QTest.mouseClick(rp.session_cards.viewport(),Qt.MouseButton.LeftButton,pos=rp.session_cards.visualItemRect(item).center());gui.processEvents()
  require(rp.snapshot['id']=='public-compact-history'and rp.tabs.currentWidget()is rp.nodes,'compact_history_actual_card_click_opens_exact_saved_map')
  require(rp.reading_label.isVisible()and not rp.notice.isVisible()and not rp.nodes.notice.isVisible(),'compact_history_short_source_visible_full_scope_folded')
  selected=rp.nodes.view.selected;image(history,'compact-history-map');rp.history_scope_button.setFocus();QTest.keyClick(rp.history_scope_button,Qt.Key.Key_Space);gui.processEvents();require(rp.notice.isVisible()and rp.nodes.notice.isVisible(),'compact_history_keyboard_expands_full_scope')
  bar.refresh();gui.processEvents();require(rp.nodes.view.selected==selected and rp.history_scope_button.isChecked(),'compact_history_scope_refresh_keeps_exact_prefix');image(history,'expanded-history-scope')
  rp.history_views_button.click();rp.tabs.setCurrentWidget(rp.statistics);gui.processEvents();stats=rp.statistics;stats.refresh();stats.relic.setCurrentIndex(stats.relic.findData(KETTLE));gui.processEvents()
  require(rp.tabs.currentWidget()is stats and stats.isVisible(),'native_statistics_original_tab_identity_and_actions_remain')
  require(stats.result['relic']['sample_count']==1 and stats.result['relic']['held_count']==1 and stats.result['relic']['fraction']==1,'native_statistics_confirmed_repeated_kettles_qualify_one_archive_not_zero')
  require(stats.result['measures']['relic_count']['mean']==5,'native_statistics_physical_total_includes_tools_without_replay')
  require(stats.scroll.widgetResizable()and stats.scroll.horizontalScrollBar().maximum()==0,'native_statistics_scroll_uses_real_available_width_without_horizontal_overflow')
  require(rp.reading_label.text()=='个人统计 · 本机归档'and not rp.notice.isVisible()and not rp.history_scope_button.isVisible(),'native_statistics_header_uses_all_archive_scope_not_selected_history')
  plain=stats.detail.toPlainText();require('平均 / 比例'in plain and plain.index('100.0%')<plain.index('未读不当作0'),'native_statistics_values_and_counts_appear_before_scope_explanation')
  require('胜率'in plain and '不上传'in plain and '不是掉落概率'in plain,'native_statistics_short_visible_summary_keeps_outcome_probability_and_privacy_limits')
  require(stats.detail.horizontalScrollBar().maximum()==0,'native_statistics_summary_table_fits_real_text_viewport');image(history,'statistics-summary')
  stats.detail.verticalScrollBar().setValue(stats.detail.verticalScrollBar().maximum());gui.processEvents();anchor=None
  for y in range(stats.detail.viewport().height()):
   for x in range(0,stats.detail.viewport().width(),3):
    if stats.detail.anchorAt(QPoint(x,y))=='statistics-details':anchor=QPoint(x,y);break
   if anchor is not None:break
  require(anchor is not None,'native_statistics_full_scope_link_is_present_and_visible');QTest.mouseClick(stats.detail.viewport(),Qt.MouseButton.LeftButton,pos=anchor);gui.processEvents()
  require(stats.details_open and '筛选的是归档中已读保密等级'in stats.detail.toPlainText(),'native_statistics_real_link_opens_unchanged_full_cohort_scope')
  reading_offset=stats.detail.verticalScrollBar().value();bar.refresh();gui.processEvents();require(stats.details_open and stats.detail.verticalScrollBar().value()==reading_offset,'native_statistics_same_refresh_keeps_expanded_reading');image(history,'statistics-full-scope')
  stats.toggle_details(None);require(not stats.details_open,'native_statistics_full_scope_can_return_to_compact_values')
  chosen=stats.relic.currentData();before_result=deepcopy(stats.result);stats.scroll.ensureWidgetVisible(stats.reload);gui.processEvents();QTest.mouseClick(stats.reload,Qt.MouseButton.LeftButton);gui.processEvents()
  require(stats.relic.currentData()==chosen and stats.result==before_result,'native_statistics_actual_reload_keeps_exact_relic_scope_and_result')
  controls=stats.card_controls;controls.pages.setCurrentIndex(1);gui.processEvents();boxes=list(controls.fields.values())
  font=boxes[0].font();normal=font.pointSizeF();font.setPointSize(18)
  for box in boxes:box.setFont(font)
  history.resize(550,460);gui.processEvents()
  require(len({box.y()for box in boxes})>1,'native_statistics_large_text_options_really_wrap')
  require(all(box.geometry().right()<box.parentWidget().width()for box in boxes),'native_statistics_wrapped_options_not_clipped')
  require(stats.scroll.verticalScrollBar().maximum()>0 and stats.scroll.horizontalScrollBar().maximum()==0,'native_statistics_small_page_can_scroll_without_horizontal_overflow')
  stats.scroll.ensureWidgetVisible(controls.fields['relic']);gui.processEvents();QTest.mouseClick(controls.fields['relic'],Qt.MouseButton.LeftButton);gui.processEvents()
  require(not controls.fields['relic'].isChecked(),'native_statistics_field_choice_uses_actual_checkbox')
  stats.scroll.ensureWidgetVisible(controls.build);gui.processEvents();QTest.mouseClick(controls.build,Qt.MouseButton.LeftButton);gui.processEvents()
  require(controls.card is not None and controls.save.isEnabled(),'native_statistics_actual_button_builds_local_card')
  require(stats.result==before_result and not any('归档时持有率' in line for line in controls.card.lines),'native_statistics_card_choice_changes_display_not_numerical_result')
  require(controls.card.png().startswith(b'\x89PNG'),'native_statistics_local_card_still_renders_valid_png_without_export_or_upload')
  image(history,'statistics-large-text')
  font.setPointSizeF(normal)
  for box in boxes:box.setFont(font)
  controls.pages.setCurrentWidget(stats.samples);stats.samples.metric.setCurrentIndex(stats.samples.metric.findData('relic'));gui.processEvents()
  require(len(stats.samples.rows)==1 and stats.samples.rows[0]['included']and stats.samples.rows[0]['value'],'native_statistics_exact_sample_row_agrees_with_holding_denominator')
  stats.samples.table.selectRow(0);gui.processEvents();require(stats.samples.open_button.isEnabled(),'native_statistics_original_exact_archive_link_enabled')
  stats.scroll.ensureWidgetVisible(stats.samples.open_button);gui.processEvents();QTest.mouseClick(stats.samples.open_button,Qt.MouseButton.LeftButton);gui.processEvents()
  require(rp.sessions.currentData()=='archive:public-compact-history'and rp.tabs.currentIndex()==0,'native_statistics_real_sample_click_opens_exact_saved_reading_not_current_run')
  rp.tabs.setCurrentWidget(stats);gui.processEvents();require(stats.relic.currentData()==chosen and not controls.fields['relic'].isChecked(),'native_statistics_return_keeps_relic_and_display_choice')
  with patch.object(stats.store,'records',side_effect=OSError('isolated statistics unavailable')):stats.refresh()
  stats.scroll.ensureWidgetVisible(stats.notice);gui.processEvents();require(stats.result is None and controls.card is None and not controls.save.isEnabled(),'native_statistics_source_loss_clears_stale_card_and_results')
  require('暂时不可用'in stats.notice.text()and stats.notice.isVisible(),'native_statistics_source_loss_explained_in_current_page')
  require(not stats.samples.source_available and '本项统计未知'in stats.samples.notice.text()and '当前筛选下共0局'not in stats.samples.notice.text(),'native_statistics_source_loss_is_unknown_in_sample_page_not_zero_archives')
  require(w.run.state==before,'native_statistics_reading_never_changes_current_run');image(history,'statistics-unavailable');w.player_validation_target=history
 finally:w.run.state=before
with patch.object(player_acceptance,'check',check):code=run(999,out/'window.json')
(out/'images.json').write_text(json.dumps(images,ensure_ascii=False,indent=2)+'\n','utf8');raise SystemExit(code)
