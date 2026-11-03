def check(window,gui,require):
 from copy import deepcopy
 import time
 import numpy as np
 from .player_shop_hover import ShopNameReader
 from .player_shop_memory import remember
 from tests.test_player_feature_417 import shop_fixture
 before=deepcopy(window.run.state)
 try:
  reader=ShopNameReader(lambda *a,**k:(shop_fixture(),None));image=np.zeros((600,800,3),np.uint8);reader.identify(image,(245,170));snapshot=reader.snapshot(image)
  require(remember(window.run,snapshot,window.run.state['id'],time.time()),'qualified_shop_names_saved_only_to_temporary_run')
  require(window.run.state['relics']==before['relics'],'shop_names_do_not_become_held_relics')
  window.show_compact();c=window.compact_window;c.open_inventory();popup=c.inventory_popup;popup.pages.setCurrentWidget(popup.shop);gui.processEvents();panel=popup.shop
  require(panel.entries.count()==len(snapshot['items']),'off_shop_panel_retains_exact_read_names')
  require('价格、剩余刷新次数'in panel.notice.text()and '未读'in panel.notice.text(),'unread_price_and_refresh_not_invented')
  panel.entries.setCurrentRow(0);gui.processEvents();require('资料效果'in panel.detail.toPlainText(),'shop_item_opens_fixed_effects')
  current=panel.entries.currentItem();c.refresh();require(panel.entries.currentItem()is current,'refresh_keeps_shop_item_reading');window.player_validation_target=popup
 finally:window.run.state=before
