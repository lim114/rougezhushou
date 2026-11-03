from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from unittest.mock import patch
import sys,json
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import QApplication
from rouge import player_acceptance
from player_ui_verification import run
out=R/sys.argv[1];after='--after'in sys.argv;out.mkdir(parents=True,exist_ok=False)
original=player_acceptance.check;rows=[];images=[]
def shot(widget,name):
 QApplication.instance().processEvents();p=out/name;assert widget.isVisible()and widget.grab().save(str(p));images.append({'file':p.relative_to(R).as_posix(),'sha256':sha256(p.read_bytes()).hexdigest()})
def check(section,w,gui,require):
 original(445,w,gui,require);bar=w.compact_window;bar.open_inventory();popup=bar.inventory_popup;p=popup.panel
 before=deepcopy(w.run.state)
 try:
  p.hover_card.dismiss();p.held.setChecked(False);p.search.clear();p.rarity.setCurrentIndex(0);p.exchange.setCurrentIndex(0);p.kind.setCurrentIndex(0);p.category.setCurrentIndex(0);p.access.setCurrentIndex(0);p.source_node.setCurrentIndex(0)
  w.run.state['relics']={key:{}for key in list(p.rows)[:80]};w.run.state['relic_count']=80;w.run.state['inventory_verified']=False
  w.run.state['resources']={'parts_count':{'value':7,'capacity':12},'life':{'value':12,'capacity':12},'shield':{'value':20},'command':{'value':10},'hope':{'value':1,'capacity':92},'gold':{'value':155},'action':{'value':1},'valuation':{'value':34}}
  bar.refresh();p.reader.hide();gui.processEvents();shot(popup,'default.png')
  for width in(640,900,1200):
   popup.resize(width,560);gui.processEvents();p.entries.scrollToTop();gui.processEvents()
   rects=[p.entries.visualItemRect(p.entries.item(i))for i in range(p.entries.count())]
   first_y=min(r.y()for r in rects);columns=sum(r.y()==first_y for r in rects)
   visible=[r for r in rects if p.entries.viewport().rect().intersects(r)]
   rows.append({'requested_width':width,'actual_width':popup.width(),'actual_height':popup.height(),'columns':columns,'visible_items_partial_row_included':len(visible),'viewport_width':p.entries.viewport().width(),'viewport_height':p.entries.viewport().height(),'grid_size':[p.entries.gridSize().width(),p.entries.gridSize().height()]})
   require(p.entries.count()==len(p.rows),'density_all_rows_preserve_exact_identity_'+str(width))
   if after:
    require(popup.rect().contains(popup.mapFromGlobal(p.icon_scale.mapToGlobal(p.icon_scale.rect().bottomRight()))),'density_footer_not_clipped_'+str(width))
    require(popup.rect().contains(popup.mapFromGlobal(p.search.mapToGlobal(p.search.rect().topLeft()))),'density_search_not_clipped_'+str(width))
  popup.resize(1200,540);gui.processEvents();shot(popup,'wide.png')
  if after:
   require(not p.status.isVisible()and p.scope.isVisible(),'density_long_source_explanation_collapsed_with_visible_entry')
   require('未核对完整'in p.summary.text(),'density_incomplete_holding_remains_visible_without_expanding')
   p.entries.setCurrentRow(12);gui.processEvents();selected=p.entries.currentItem().data(Qt.ItemDataRole.UserRole);p.detail.verticalScrollBar().setValue(15);offset=p.detail.verticalScrollBar().value()
   require(p.reader.isVisible()and p.source_button.isVisible()and p.reference_button.isVisible(),'density_selected_item_actions_are_inside_reader')
   p.scope.click();gui.processEvents();require(p.status.isVisible()and'不是当前DLC完整目录或已生效证明'in p.status.text(),'density_full_scope_limits_can_be_read')
   p.more.click();p.more.click();bar.refresh();gui.processEvents()
   require(p.entries.currentItem().data(Qt.ItemDataRole.UserRole)==selected and p.detail.verticalScrollBar().value()==offset and p.scope.isChecked(),'density_refresh_preserves_selection_reading_and_open_source_explanation')
   p.scope.click();p.hide_reader.click();gui.processEvents();require(not p.source_button.isVisible()and not p.reference_button.isVisible(),'density_hiding_reader_removes_only_item_specific_actions')
   require(popup.title_label.isHidden()and popup.resources.parentWidget()is popup,'density_resources_replace_redundant_title_row')
   with patch('rouge.player_inventory.reference.packet',return_value=None):
    p.refresh();gui.processEvents();require(not p.entries.count()and'资料暂不可用'in p.summary.text(),'density_unavailable_source_not_hidden_in_collapsed_explanation')
   p.refresh();gui.processEvents();require(p.entries.currentItem()is None,'density_source_recovery_does_not_reselect_stale_item')
   shot(popup,'restored.png')
  w.player_validation_target=popup
 finally:w.run.state=before
with patch.object(player_acceptance,'check',side_effect=check):code=run(445,out/'window.json')
(out/'geometry.json').write_text(json.dumps({'after':after,'same_public_fixture':True,'rows':rows,'images':images,'game_chat_actions':False},ensure_ascii=False,indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes())
raise SystemExit(code)
