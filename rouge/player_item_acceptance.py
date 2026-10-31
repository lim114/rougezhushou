"""Public fixtures and owned Qt mouse dispatch; no global cursor or game input."""
from copy import deepcopy
from unittest.mock import patch
from PySide6.QtCore import Qt,QPoint,QPointF,QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from . import public_archive

def check_reading(window,gui,require):
    from PySide6.QtCore import QTimer
    from tests.test_item_reading_444 import choose,IDS
    before=deepcopy(window.run.state)
    for timer in window.findChildren(QTimer):timer.stop()
    try:
        window.run.state['relics']={identity:{}for identity in IDS}
        window.show_compact();bar=window.compact_window;bar.open_inventory();popup=bar.inventory_popup;panel=popup.panel;gui.processEvents()
        choose(panel,IDS[0]);panel.source_button.setFocus();QTest.keyClick(panel.source_button,Qt.Key.Key_Space);gui.processEvents()
        card=panel.hover_card
        require(card.isVisible()and card.pinned and card.identity==IDS[0],'item444_keyboard_opens_and_pins_exact_existing_source_card')
        require(popup.isVisible()and not window.isVisible(),'item444_sources_keep_compact_inventory_not_full_window')
        pool=card.pools.currentData();text=card.detail.toPlainText();bar.refresh();gui.processEvents()
        require(card.isVisible()and card.pinned and card.pools.currentData()==pool and card.detail.toPlainText()==text,'item444_refresh_keeps_pinned_source_reading')
        choose(panel,IDS[1]);panel.source_button.click();gui.processEvents()
        require(card.identity==IDS[1]and card.pinned,'item444_explicit_source_click_can_replace_another_pinned_item')
        bar.toggle_visibility();gui.processEvents()
        require(not popup.isVisible()and not card.isVisible()and card.pinned,'item444_temporary_hide_preserves_pinned_state')
        bar.toggle_visibility();gui.processEvents()
        require(popup.isVisible()and card.isVisible()and card.identity==IDS[1],'item444_hotkey_restore_returns_same_source')
        popup.close();gui.processEvents()
        require(not card.isVisible()and not card.pinned and card.identity is None,'item444_closing_inventory_clears_invisible_pin')
        bar.open_inventory();gui.processEvents();choose(panel,IDS[0]);panel.hover_pending=IDS[0];panel.show_hover();gui.processEvents()
        require(card.isVisible()and card.identity==IDS[0]and not card.pinned,'item444_hover_works_after_reopening_inventory')
        panel.reference_button.click();gui.processEvents()
        full=window.reference_panel('relics',activate=False)
        require(window.isVisible()and not popup.isVisible()and not card.isVisible(),'item444_explicit_full_read_closes_obscuring_inventory')
        require(full.result['row']['id']==IDS[0],'item444_explicit_full_read_uses_exact_item')
        require(full.map_image.isHidden(),'item444_no_empty_map_takes_item_reading_space')
        require(not full.entries.currentItem().icon().pixmap(36,36).isNull(),'item444_full_reader_uses_exact_existing_picture')
        window.show_compact();bar.open_inventory();gui.processEvents();choose(panel,IDS[0]);panel.source_button.click();gui.processEvents()
        with patch('rouge.player_inventory.reference.packet',return_value=None):panel.refresh()
        require(not card.isVisible()and not panel.source_button.isEnabled()and not panel.reference_button.isEnabled(),'item444_source_loss_clears_and_disables_both_entries')
        panel.refresh();gui.processEvents();require(panel.entries.currentItem()is None,'item444_source_recovery_does_not_restore_old_choice')
        choose(panel,IDS[0]);panel.source_button.click();gui.processEvents()
        require(card.isVisible()and card.identity==IDS[0]and card.pinned,'item444_source_entry_recovers_with_manual_selection')
        require('不是抽取权重或本局获得概率'in card.notice.text(),'item444_statistics_scope_is_readable_before_expanding')
        window.player_validation_target=card
    finally:window.run.state=before

def check(window,gui,require):
    original=deepcopy(window.run.state)
    window.run.state['relics']={identity:{} for identity in ('rogue_6_relic_legacy_1','rogue_6_relic_legacy_3','rogue_6_relic_legacy_4')}
    window.show_compact();bar=window.compact_window;bar.open_inventory();panel=bar.inventory_popup.panel;gui.processEvents()
    require(panel.entries.count()==3,'inventory_only_confirmed_fixture_members')
    panel.rarity.setCurrentIndex(panel.rarity.findData('NORMAL'));require(panel.entries.count()==1 and next(iter(panel.rows.values()))['name']=='热水壶','rarity_filter_is_actual_separate_choice')
    panel.exchange.setCurrentIndex(panel.exchange.findData(False));require(panel.entries.count()==0,'rarity_exchange_filters_intersect')
    panel.exchange.setCurrentIndex(0);panel.rarity.setCurrentIndex(0);panel.kind.setCurrentIndex(panel.kind.findData('LEGACY'));require(panel.entries.count()==0,'category_filter_excludes_other_categories')
    panel.kind.setCurrentIndex(0);panel.version.setCurrentIndex(panel.version.findData('base'))
    target='rogue_6_relic_legacy_1';item=next(panel.entries.item(i)for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==target)
    panel.entries.setCurrentItem(item);selected=panel.entries.currentItem();offset=panel.entries.verticalScrollBar().value();panel.refresh()
    require(panel.entries.currentItem()is selected and panel.entries.verticalScrollBar().value()==offset,'unchanged_refresh_keeps_list_selection_and_position')
    QTest.qWait(180);gui.processEvents();point=panel.entries.visualItemRect(item).center();viewport=panel.entries.viewport()
    event=QMouseEvent(QEvent.Type.MouseMove,QPointF(point),QPointF(viewport.mapToGlobal(point)),Qt.MouseButton.NoButton,Qt.MouseButton.NoButton,Qt.KeyboardModifier.NoModifier)
    gui.sendEvent(viewport,event)
    require(panel.hover_pending==target and panel.hover_timer.isActive(),'owned_mouse_dispatch_arms_exact_hover_timer')
    panel.hover_timer.stop();panel.hover_timer.timeout.emit();gui.processEvents()
    card=panel.hover_card;require(card.isVisible()and card.identity==target,'owned_mouse_dispatch_opens_exact_item_source_card')
    require(card.testAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating),'item_hover_does_not_request_activation')
    require('不是抽取权重或本局获得概率'in card.notice.text()and'不相加'in card.notice.text(),'frequency_limits_visible_without_scrolling')
    require(not card.picture.pixmap().isNull(),'real_relic_icon_in_hover')
    expected=panel.source_index.pools('base',target);require(card.pools.count()==len(expected)and len(expected)>1,'hover_lists_all_exact_version_memberships')
    input_pool=next(p for p in expected if p['name'].endswith('藏品输入'));card.pools.setCurrentIndex(card.pools.findData(input_pool['id']))
    require('不是交换奖励池'in card.detail.toPlainText(),'input_membership_never_shown_as_drop_pool')
    counted=next(p for p in expected if any(r['rate']is not None for _,_,d in public_archive.distributions(p)for r in public_archive.members(panel.source_index.data,p,d)if r['id']==target))
    card.pools.setCurrentIndex(card.pools.findData(counted['id']));text=card.detail.toPlainText()
    require('次候选出现'in text and '不是本局最终获得概率'in text and '不相加'in text,'historical_frequency_has_denominator_and_scope')
    card.pin.click();identity=card.pools.currentData();card.detail.verticalScrollBar().setValue(18);reading=card.detail.verticalScrollBar().value();panel.refresh();gui.processEvents()
    require(card.isVisible()and card.pinned and card.pools.currentData()==identity and card.detail.verticalScrollBar().value()==reading,'refresh_preserves_pinned_pool_and_reading')
    other=next(panel.entries.item(i)for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)!=target);panel.queue_hover(other);QTest.qWait(220)
    require(card.identity==target,'pinned_item_not_replaced_by_other_hover')
    card.open_button.click();gui.processEvents();archive=window.public_archive
    require(archive.isVisible()and archive.version.currentData()=='base'and archive.pools.currentItem().data(Qt.ItemDataRole.UserRole)==identity,'hover_link_opens_exact_pool_and_version')
    require(not window.isVisible(),'pool_lookup_keeps_large_assistant_hidden')
    require(not archive.select_exact_pool('nonexistent','missing')and archive.pools.currentItem()is None and archive.members.rowCount()==0,'missing_exact_scope_clears_unrelated_old_pool')
    bar.open_inventory();panel.held.setChecked(False);panel.search.setText('希望');panel.rarity.setCurrentIndex(panel.rarity.findData('NORMAL'));panel.exchange.setCurrentIndex(panel.exchange.findData(True));panel.refresh()
    require(panel.entries.count()>0 and all('希望'in r['name']+r['usage']and r['rarity']=='NORMAL'and r['exchange']is True for r in panel.rows.values()),'text_ownership_and_typed_filters_work_together')
    panel.entries.setCurrentRow(0);panel.hover_pending=panel.entries.currentItem().data(Qt.ItemDataRole.UserRole);panel.show_hover();gui.processEvents();require(card.isVisible(),'card_available_after_return_from_pool')
    with patch('rouge.player_inventory.reference.packet',return_value=None):panel.refresh();require(not card.isVisible()and not panel.detail.toPlainText()and panel.entries.count()==0,'catalog_source_loss_clears_hover_list_and_detail')
    panel.search.clear();panel.rarity.setCurrentIndex(0);panel.exchange.setCurrentIndex(0);panel.held.setChecked(True);panel.version.setCurrentIndex(panel.version.findData('base'));panel.refresh()
    panel.entries.setCurrentRow(0);panel.hover_pending=panel.entries.currentItem().data(Qt.ItemDataRole.UserRole);panel.show_hover();card.pin.setChecked(True);panel.rarity.setCurrentIndex(panel.rarity.findData('SUPER_RARE'));gui.processEvents()
    require(not card.isVisible()and card.identity is None,'filter_excluding_pinned_item_clears_stale_card')
    panel.rarity.setCurrentIndex(0);panel.entries.setCurrentRow(0);panel.hover_pending=target;panel.show_hover();gui.processEvents();card.pin.setChecked(True)
    card.pools.setCurrentIndex(card.pools.findData(counted['id']))
    require('其它条目另注明固定基准'in panel.status.text()and '不是当前DLC完整目录或已生效证明'in panel.status.text()and '当前DLC适用性待核验'in card.notice.text(),'catalog_and_pool_version_limits_visible')
    window.run.state=original
    panel.status.setText('隔离验收示例：三件公开藏品；不是本局读取。按稀有度、交换资格和类别筛选，悬停查池。')
