def check(window,gui,require):
 from .player_item_hover import ItemHoverCard
 from .player_item_sources import ItemSourceIndex
 from tests.test_player_item_sources_394 import fixture
 window.show_compact();c=window.compact_window;c.game_binding.timer.stop();c.game_hover.timer.stop()
 card=ItemHoverCard(c);data=fixture();data['versions']['base'][0]['name']='收藏品来源的较长说明名称，需要完整阅读'
 try:
  card.install({'id':'a','name':'隔离测试藏品'},'base',ItemSourceIndex(data),'fixture');card.resize(400,500);card.show();gui.processEvents()
  require(card.cards.horizontalScrollBar().maximum()==0,'narrow_source_cards_without_horizontal_clipping')
  require(all(b.caption.wordWrap()for b in card.cards.buttons),'long_source_labels_wrap')
  seen=[];card.poolRequested.connect(lambda v,i:seen.append((v,i)));card.cards.buttons[0].click();card.open_pool();require(seen==[('base','pool1')],'wrapped_card_keeps_exact_navigation')
  card.hide();c.game_hover.card=card;c.game_hover.last_request={'serial':0};c.game_hover.gate.key=('old',)
  c.toggle_visibility();gui.processEvents();require(c.hidden_windows is not None,'hotkey_hides_owned_surfaces');require(c.game_hover.last_request is None,'hide_invalidates_pending_hover')
  c.game_hover.tick();require(c.game_hover.gate.key is None,'hidden_assistant_does_not_wait_or_capture')
  c.toggle_visibility();gui.processEvents();require(c.hidden_windows is None and c.isVisible(),'hotkey_restore_restarts_from_visible_state')
  c.game_hover.card=None;card.show_conditions.setChecked(False);card.show();window.player_validation_target=card
 finally:c.game_hover.card=None
