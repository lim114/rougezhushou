from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import sys,json
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge import player_acceptance
from player_ui_verification import run
from tests.test_player_feature_426 import observations
out=R/sys.argv[1];after='--after'in sys.argv;out.mkdir(parents=True,exist_ok=False)
original=player_acceptance.check;images=[];geometry=[]
def shot(widget,name):
 QApplication.instance().processEvents();p=out/name;assert widget.isVisible()and widget.grab().save(str(p));images.append({'file':p.relative_to(R).as_posix(),'sha256':sha256(p.read_bytes()).hexdigest()})
def check(section,w,gui,require):
 original(445,w,gui,require);bar=w.compact_window;bar.open_inventory();d=bar.inventory_popup;p=d.panel;before=deepcopy(w.run.state);issue=w.run.save_issue
 try:
  p.hover_card.dismiss();p.held.setChecked(False);p.search.clear();p.reader.hide();w.run.state['relics']={k:{}for k in list(p.rows)[:50]};w.run.state['relic_count']=51;w.run.state['inventory_verified']=False
  from rouge.player_tools import tool_rows
  tool=tool_rows({},held_only=False)[0]['id'];w.run.state['tactical_tools']={tool:{'held':True}}
  w.run.state['resources']={'parts_count':{'value':7,'capacity':12},'life':{'value':12,'capacity':12},'shield':{'value':20},'command':{'value':10},'hope':{'value':1,'capacity':92},'gold':{'value':155},'action':{'value':1},'valuation':{'value':34}}
  w.run.state['history']=[observations()];bar.refresh();gui.processEvents()
  for page,name in((p,'inventory'),(d.tools,'tools'),(d.parts,'parts'),(d.shop,'shop')):
   d.pages.setCurrentWidget(page);d.resize(1200,540);gui.processEvents();shot(d,name+'-grid.png')
   if page.entries.count():page.entries.setCurrentRow(0);gui.processEvents();shot(d,name+'-reading.png')
   if after:
    require(page.summary.isVisible()and not page.notice.isVisible()if page is not p else page.summary.isVisible(),'header_summary_visible_'+name)
    if page is not p:
     require(page.scope.isVisible(),'header_scope_entry_available_'+name)
     page.scope.click();gui.processEvents();require(page.notice.isVisible(),'header_full_source_limits_open_'+name);page.scope.click()
     if page.entries.count():
      selected=page.entries.currentItem();text=page.detail.toPlainText();page.details_toggle.click();bar.refresh();gui.processEvents();require(not page.detail.isVisible()and page.entries.currentItem()is selected and page.detail.toPlainText()==text,'header_refresh_keeps_collapsed_exact_reading_'+name)
  d.pages.setCurrentWidget(p);p.reader.hide()
  for width in(480,640,900,1200):
   d.resize(width,560);gui.processEvents();strip=d.resources;boxes=[chip.geometry()for chip in strip.chips.values()]
   require(all(strip.rect().contains(r)for r in boxes)and all(not a.intersects(b)for i,a in enumerate(boxes)for b in boxes[i+1:]),'header_resource_layout_no_overlap_'+str(width))
   geometry.append({'requested_width':width,'actual_size':[d.width(),d.height()],'resource_rows':len({r.y()for r in boxes}),'resource_keys':list(strip.chips),'resource_height':strip.height(),'grid_height':p.entries.viewport().height()})
   if after:
    require(d.navigation.isVisible()and d.crew_button.isVisible()and not d.pages.tabBar().isVisible(),'header_single_navigation_and_crew_'+str(width))
    boxes=[widget.geometry()for widget in(d.navigation,d.crew_button,*strip.chips.values())]
    require(all(strip.rect().contains(r)for r in boxes)and all(not a.intersects(b)for i,a in enumerate(boxes)for b in boxes[i+1:]),'header_navigation_and_all_resource_boxes_fit_'+str(width))
    d.navigation.setCurrentIndex(0);d.navigation.setFocus();QTest.keyClick(d.navigation,Qt.Key.Key_Right);gui.processEvents();require(d.pages.currentWidget()is d.tools,'header_keyboard_navigation_works_'+str(width));d.pages.setCurrentWidget(p);gui.processEvents();require(d.navigation.currentIndex()==0,'header_programmatic_page_sync_'+str(width))
  if after:
   require(d.navigation.tabText(0)=='收藏品 已读50'and d.navigation.tabText(1)=='道具 1'and d.navigation.tabText(2)=='零件箱 7/12','header_collection_tool_and_parts_counts_are_distinct')
   require('合计最近读到51'in d.navigation.tabToolTip(0)and'不是库存'in d.navigation.tabToolTip(2),'header_combined_total_and_partial_members_explained')
   shop=d.shop;d.pages.setCurrentWidget(shop);shop.entries.setCurrentRow(0);gui.processEvents();cursor=shop.detail.textCursor();cursor.setPosition(8);shop.detail.setTextCursor(cursor);selected=shop.entries.currentItem().data(Qt.ItemDataRole.UserRole);old_snapshot=shop.snapshots.currentData()
   second=observations();second['at']+=2;w.run.state['history'].append(second);bar.refresh();gui.processEvents();require(shop.snapshots.currentData()==old_snapshot and shop.entries.currentItem().data(Qt.ItemDataRole.UserRole)==selected and shop.detail.textCursor().position()==8,'header_old_shop_reading_survives_new_observation')
   w.run.save_issue='isolated-not-saved';shop.refresh();gui.processEvents();require('未保存'in shop.summary.text(),'header_save_failure_visible_without_scope');w.run.save_issue=issue
   d.pages.setCurrentWidget(p);d.resize(1200,540);gui.processEvents();shot(d,'final-inventory.png')
  w.player_validation_target=d
 finally:w.run.state=before;w.run.save_issue=issue
with patch.object(player_acceptance,'check',side_effect=check):code=run(445,out/'window.json')
(out/'details.json').write_text(json.dumps({'after':after,'public_fixture_not_user_run':True,'images':images,'geometry':geometry},ensure_ascii=False,indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes())
raise SystemExit(code)
