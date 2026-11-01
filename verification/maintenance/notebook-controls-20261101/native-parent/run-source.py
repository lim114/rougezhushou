from pathlib import Path
import sys,subprocess,json
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/notebook-controls-20261101';out=B/'native-parent'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code},flush=True);raise SystemExit(code)
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
import player_ui_verification as ui
from rouge import player_acceptance
original_run=ui.run

def run_with_layout(section,receipt):
 original_check=player_acceptance.check
 def check(section,window,gui,require):
  original_check(section,window,gui,require)
  old=deepcopy(window.run.state);bar=window.compact_window;popup=bar.recent_notes_popup;p=popup.panel;e=window.player_notes;images=[];sizes=[]
  def snap(name):
   path=out/(name+'.png');require(popup.grab().save(str(path)),name+'_public_image_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
  try:
   content={'kind':'battle','title':'公开布局测试 · 林间作战','variant_id':'public-notebook-layout'};e.discard();require(p.open_for_context(content),'layout_opens_exact_public_note');e.autosave.setChecked(False);text='# 本关提醒\n\n- 先查看敌人机制。\n- 笔记只保存在本机。\n- 当前手动草稿不能被覆盖。';e.editor.setPlainText(text);p.more.setChecked(True);e.pages.setCurrentIndex(0)
   for width in (480,640,900,1200):
    popup.resize(width,500);QTest.qWait(40);gui.processEvents();p.fit_content();gui.processEvents();require(e.editor.viewport().height()>=4*e.editor.fontMetrics().lineSpacing(),'layout_actual_editor_has_four_lines_'+str(width));require(p.card.geometry().bottom()<=p.height(),'layout_actual_card_not_cut_'+str(width));require(e.editor.toPlainText()==text,'layout_actual_resize_keeps_exact_text_'+str(width));sizes.append({'requested_width':width,'actual_client_size':[popup.width(),popup.height()],'editor_viewport':e.editor.viewport().height(),'line_spacing':e.editor.fontMetrics().lineSpacing(),'options_view_height':p.options_scroll.height()});snap('expanded-'+str(width))
   require(not e.context.isVisible(),'layout_same_owner_does_not_repeat_context_in_card')
   p.options_scroll.ensureWidgetVisible(e.save_button);gui.processEvents();QTest.mouseClick(e.save_button,Qt.MouseButton.LeftButton);gui.processEvents();require(not e.dirty and e.store.read(e.key)[0]==text,'layout_real_scrolled_save_button_uses_original_store')
   e.editor.insertPlainText('\n新增但未保存。');draft=e.editor.toPlainText();e.store.path(e.key).write_text('外部保存的另一份正文','utf8');p.options_scroll.ensureWidgetVisible(e.save_button);gui.processEvents();QTest.mouseClick(e.save_button,Qt.MouseButton.LeftButton);gui.processEvents();reason=e.status.text();require(e.dirty and '本次未覆盖'in reason,'layout_real_save_conflict_preserved');p.more.setChecked(False);gui.processEvents();require(e.status.isVisible()and e.status.text()==reason,'layout_conflict_reason_visible_with_options_closed');require(e.editor.toPlainText()==draft and e.store.read(e.key)[0]=='外部保存的另一份正文','layout_conflict_keeps_both_actual_versions');popup.resize(900,500);QTest.qWait(40);snap('conflict-options-closed')
   window.run.state['last_node_content']={'kind':'battle','title':'另一处最近读取','variant_id':'public-other'};p.follow.setChecked(True);p.refresh(force=True);QTest.qWait(30);p.more.setChecked(False);gui.processEvents();require(e.context.isVisible()and e.context.parentWidget()is p and content['title']in e.context.text(),'layout_other_owner_warning_outside_card_and_options');require(e.editor.toPlainText()==draft and e.key!=p.key,'layout_follow_does_not_rebind_draft');require(e.editor.viewport().height()>=4*e.editor.fontMetrics().lineSpacing(),'layout_other_owner_editor_keeps_four_real_lines');snap('other-owner')
   e.discard();e.autosave.setChecked(True);p.select_context(content);p.open_editor(content);e.editor.setPlainText('# 本关提醒\n\n先查看关卡资料，再准备队伍。');QTest.qWait(1100);gui.processEvents();require(not e.dirty,'layout_original_autosave_still_runs');p.more.setChecked(False);p.request_edit();QTest.qWait(30);gui.processEvents();require(p.stack.currentWidget()is p.preview and '先查看关卡资料'in p.preview.toPlainText(),'layout_returns_same_card_to_markdown_reading');require(not p.options_scroll.isVisible()and not e.status.isVisible()and not e.context.isVisible(),'layout_clean_reading_does_not_reserve_option_or_owner_rows');popup.resize(900,360);QTest.qWait(30);snap('reading-compact')
   p.timer.stop();window.player_validation_target=popup
  finally:window.run.state=old
  require(window.run.state==old,'layout_public_cases_preserve_run_state');(out/'layout-images.json').write_text(json.dumps({'images':images,'sizes':sizes,'only_public_temporary_notes':True,'not_game_or_full_video_parity':True},ensure_ascii=False,indent=2)+'\n','utf8')
 with patch.object(player_acceptance,'check',check):return original_run(section,receipt)
ui.run=run_with_layout
import runpy
sys.argv=['scripts/verify_inline_notebook_review.py','--receipt',str(out/'window.json')]
runpy.run_path(str(R/'scripts/verify_inline_notebook_review.py'),run_name='__main__')
