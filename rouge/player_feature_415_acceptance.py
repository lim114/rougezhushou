def check(window,gui,require):
 from PySide6.QtCore import QPoint
 from PySide6.QtTest import QTest
 from . import public_archive
 from .player_item_sources import ItemSourceIndex
 from .player_inventory import inventory_rows
 from .player_source_cards import source_cards
 window.show_compact();window.compact_window.open_inventory();gui.processEvents();p=window.compact_window.inventory_popup.panel
 data=public_archive.load();index=ItemSourceIndex(data)
 row=next(r for r in inventory_rows({},held_only=False,public_data=data,version='dlc1')if len(index.pools('dlc1',r['id']))>=3)
 card=p.hover_card;card.install(row,'dlc1',index,'public-fixture');card.show();card.move(620,180);QTest.qWait(100);gui.processEvents()
 require(card.isVisible()and len(card.cards.buttons)>=3,'actual_source_cards_visible')
 require(all(b.isVisible()for b in card.cards.buttons[:2]),'two_column_pool_cards_visible')
 expected=source_cards(index,'dlc1',row['id']);require(len(card.cards.buttons)==len(expected['pools'])+len(expected['nodes']),'all_documented_pool_and_node_cards_present')
 button=card.cards.buttons[-1];button.click();gui.processEvents();require(card.pools.currentData()==button.property('poolIdentity'),'actual_card_selects_exact_pool')
 require(card.detail.isVisible()and bool(card.detail.toPlainText()),'actual_card_expands_conditions_and_samples')
 seen=[];card.poolRequested.connect(lambda v,i:seen.append((v,i)));card.open_pool();gui.processEvents();require(seen[-1]==('dlc1',button.property('poolIdentity')),'card_navigation_keeps_version_and_pool')
 card.pin.setChecked(True);require(not card.install({'id':'not-this','name':'other'},'dlc1',index,'other'),'fixed_reading_not_rebound')
 card.pin.setChecked(False);card.install(row,'dlc1',None,'gone');require(not card.cards.buttons and not card.open_button.isEnabled(),'lost_source_clears_cards')
 card.install(row,'dlc1',index,'restored');card.show_conditions.setChecked(False);card.show();QTest.qWait(100);gui.processEvents();window.player_validation_target=card
