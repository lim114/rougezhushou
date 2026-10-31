from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from unittest.mock import patch
import sys,json
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtWidgets import QDialog,QPushButton
from PySide6.QtGui import QPalette
from rouge import player_acceptance
from rouge.player_notes import content_key
from rouge.player_note_selector import catalogue_snapshot
from player_ui_verification import run
out=R/'verification/maintenance/player-theme-20261101/native';out.mkdir(exist_ok=False);images=[]
original=player_acceptance.check
def screenshot(widget,name):
 path=out/name;assert widget.isVisible();assert widget.grab().save(str(path));images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
def check(section,w,gui,require):
 original(445,w,gui,require);bar=w.compact_window;card=bar.inventory_popup.panel.hover_card
 require(card.property('playerTheme')=='dark'and bar.inventory_popup.property('playerTheme')=='dark','theme_dark_inventory_and_item_card')
 require(bar.map_popup.property('playerTheme')=='light','theme_light_map_and_local_palette')
 require(bar.styleSheet()==''and bar.testAttribute(__import__('PySide6.QtCore',fromlist=['Qt']).Qt.WidgetAttribute.WA_TranslucentBackground),'theme_transparent_toolbar_not_restyled')
 before=deepcopy(w.run.state);base=bar.styleSheet()
 try:
  bar.open_inventory();inventory=bar.inventory_popup.panel;inventory.held.setChecked(False);inventory.entries.setCurrentRow(0);gui.processEvents();key=inventory.entries.currentItem().data(256);inventory.refresh()
  require(inventory.entries.currentItem().data(256)==key,'theme_inventory_selection_survives_refresh');inventory.reader.hide();screenshot(bar.inventory_popup,'inventory.png')
  bar.open_recent_notes();popup=bar.recent_notes_popup;notes=popup.panel;context=next(r['context']for r in catalogue_snapshot()['rows']if r['context']['kind']=='reference-stage');editor=w.player_notes
  editor.autosave.setChecked(False);k=content_key(context);editor.store.save(k,'# 样式隔离验证\n\n这是固定资料对应的测试笔记。\n\n- 用于检查中文字号、阅读与编辑。\n- 不是用户本局记录。',editor.store.read(k)[1]);require(notes.open_for_context(context),'theme_exact_public_reference_note_opens');gui.processEvents()
  require(popup.property('playerTheme')=='light'and editor.property('playerTheme')=='light','theme_note_reader_and_embedded_editor_light');screenshot(popup,'notes.png')
  require(notes.open_editor(context),'theme_existing_inline_editor_opens');editor.editor.insertPlainText('\n未保存的测试内容');require(not popup.close()and popup.isVisible(),'theme_unsaved_note_still_refuses_close')
  editor.discard();require(popup.close(),'theme_discarded_temporary_note_can_close')
  w.run.state['history']=[{'kind':'node_content_seen','title':'遗忘时间','at':4},{'kind':'resource_updated','resource':'gold','value':5,'at':5}];bar.open_replay();replay=bar.replay_popup.panel
  require(bar.replay_popup.property('playerTheme')=='light','theme_history_reader_light');gui.processEvents();screenshot(bar.replay_popup,'history.png')
  bar.open_inventory();inventory.held.setChecked(True);w.run.state['relics']={'rogue_6_relic_legacy_1':{}};inventory.refresh();inventory.entries.setCurrentRow(0);inventory.source_button.click();gui.processEvents();card=inventory.hover_card
  require(card.isVisible()and card.pinned,'theme_source_card_still_opens_after_other_readers');require(bar.styleSheet()==base,'theme_other_readers_do_not_restyle_transparent_toolbar')
  w.player_validation_target=card
 finally:w.run.state=before
with patch.object(player_acceptance,'check',side_effect=check):code=run(445,out/'window.json')
(out/'extra-images.json').write_text(json.dumps({'images':images,'all_owned_temporary_widgets':True},ensure_ascii=False,indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes())
raise SystemExit(code)
