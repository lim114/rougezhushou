"""Public fixtures and owned Qt mouse dispatch; no global cursor or game input."""
from copy import deepcopy
from unittest.mock import patch
from PySide6.QtCore import Qt,QPoint,QPointF,QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from . import public_archive

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
    require('2026年10月16日'in panel.status.text()and '当前DLC'in card.notice.text(),'catalog_and_pool_version_limits_visible')
    window.run.state=original
    panel.status.setText('隔离验收示例：三件公开藏品；不是本局读取。按稀有度、交换资格和类别筛选，悬停查池。')
