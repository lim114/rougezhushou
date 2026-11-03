"""Public fixtures and owned Qt mouse dispatch; no global cursor or game input."""
from copy import deepcopy
from unittest.mock import patch
from PySide6.QtCore import Qt,QPoint,QPointF,QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from . import public_archive

def check_inventory_modes(window,gui,require):
    from PySide6.QtCore import QTimer
    from .relic_quantities import KETTLE,kettle_copies
    from .player_resource_facts import inventory_summary
    from tests.test_inventory_modes_446 import observe,OTHER,TOOL
    before=deepcopy(window.run.state);images={}
    for timer in window.findChildren(QTimer):timer.stop()
    try:
        observe(window.run,[KETTLE]*3+[OTHER,TOOL]);window.show_compact();bar=window.compact_window;bar.open_inventory();popup=bar.inventory_popup;p=popup.panel;gui.processEvents()
        require(window.run.inventory_status()['complete']and inventory_summary(window.run.state)['relics']==4,'modes446_three_kettles_one_other_one_tool_are_five_physical_items')
        require(p.entries.count()==4 and len(p.rows)==2,'modes446_unmerged_rows_keep_three_identical_ids')
        item=next(p.entries.item(i)for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==KETTLE and p.entries.item(i).data(Qt.ItemDataRole.UserRole+1)==2);p.entries.setCurrentItem(item);gui.processEvents()
        p.merge_kettles.setFocus();QTest.keyClick(p.merge_kettles,Qt.Key.Key_Space);gui.processEvents()
        require(p.entries.count()==2 and p.entries.currentItem().data(Qt.ItemDataRole.UserRole)==KETTLE and'×3'in p.entries.currentItem().text(),'modes446_keyboard_merge_preserves_kettle_id')
        require(popup.navigation.tabText(0)=='收藏品 4'and popup.navigation.tabText(1)=='道具 1','modes446_header_counts_physical_items_separately_from_types')
        popup.resize(1200,540);gui.processEvents();images['merged-kettles']=popup.grab()
        p.source_button.click();gui.processEvents();require(p.hover_card.isVisible()and p.hover_card.identity==KETTLE and p.hover_card.pinned,'modes446_merged_source_button_still_opens_exact_kettle')
        p.hover_card.dismiss();p.merge_kettles.click();gui.processEvents();require(p.entries.count()==4,'modes446_expanding_restores_physical_copy_rows')
        p.held.setChecked(False);p.reader.hide();p.icon_scale.setValue(48);gui.processEvents()
        for width in(480,760,1200):
            popup.resize(width,560);gui.processEvents();p.entries.doItemsLayout();gui.processEvents();rect=p.entries.visualItemRect(p.entries.item(0))
            require(rect.width()>180 and rect.width()<=p.entries.viewport().width(),'modes446_cards_follow_actual_width_'+str(width))
            require(p.entries.count()==len(p.rows),'modes446_card_mode_does_not_remove_catalogue_entries_'+str(width))
            require(popup.rect().contains(popup.mapFromGlobal(p.icon_scale.mapToGlobal(p.icon_scale.rect().bottomRight()))),'modes446_wrapping_footer_is_inside_window_'+str(width))
        popup.resize(1200,620);gui.processEvents();images['effect-cards']=popup.grab()
        p.entries.setCurrentRow(0);selected=p.entries.currentItem();text=p.detail.toPlainText();p.icon_scale.setValue(104);gui.processEvents();bar.refresh();gui.processEvents();require(p.entries.currentItem()is selected and p.detail.toPlainText()==text,'modes446_card_to_icons_and_refresh_keep_exact_reading')
        p.reader.hide();images['icon-grid']=popup.grab()
        for page,name in((popup.parts,'parts'),(popup.tools,'tools'),(popup.shop,'shop')):
            popup.pages.setCurrentWidget(page);page.icon_scale.setValue(48);gui.processEvents();require(page.entries.descriptions,'modes446_other_item_catalogue_supports_effect_cards_'+name)
        popup.pages.setCurrentWidget(p);p.held.setChecked(True);p.icon_scale.setValue(60);p.reader.hide();window.run.state['relic_icon_memory']=None;window.run.state['inventory_verified']=False;bar.refresh();gui.processEvents()
        require('重复件数未确认'in p.summary.text()and p.entries.count()==2,'modes446_missing_quantity_is_not_expanded_or_guessed')
        require(not window.run.state['resources'],'modes446_copy_count_does_not_invent_life_or_hope')
        window.player_inventory_mode_images=images;window.player_validation_target=popup
    finally:window.run.state=before

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

def check_source_nodes(window,gui,require):
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QLabel
    from .player_map_acceptance import fixtures
    from tests.test_item_reading_444 import choose,IDS
    before=deepcopy(window.run.state)
    try:
        for timer in window.findChildren(QTimer):timer.stop()
        graphs,*_=fixtures();kind='作战';graphs[0]['nodes'][0].update(observed_type=kind)
        window.run.state['maps']={g['zone_id']:g for g in graphs};window.run.state['relics']={IDS[0]:{}}
        original=deepcopy(window.run.state);window.show_compact();bar=window.compact_window;bar.open_inventory();panel=bar.inventory_popup.panel
        choose(panel,IDS[0]);panel.source_button.click();gui.processEvents();card=panel.hover_card
        labels=[w.text()for w in card.cards.findChildren(QLabel)]
        require('对应地图节点'in labels and '其它取得来源'in labels,'sources445_separates_map_nodes_from_other_origins')
        buttons=[b for b in card.cards.buttons if b.property('mapKind')]
        require(buttons and all(not b.picture.pixmap().isNull()for b in buttons),'sources445_exact_nodes_use_shared_original_icons')
        origins=[b for b in card.cards.buttons if b.caption.text().startswith('流窜的')]
        require(origins and all(not hasattr(b,'picture')and'未直接对应地图节点'in b.toolTip()for b in origins),'sources445_roaming_origin_has_no_guessed_map_icon')
        target=next(b for b in buttons if b.property('mapKind')==kind);pool_id=target.property('poolIdentity');target.setFocus();QTest.keyClick(target,Qt.Key.Key_Space);gui.processEvents();mp=bar.map_popup.panel
        require(bar.map_popup.isVisible()and not window.isVisible(),'sources445_keyboard_node_card_opens_compact_map')
        require(mp.view.filter_kind==kind and mp.view.overlay[graphs[0]['nodes'][0]['id']]['match']=='observed','sources445_exact_type_highlights_corresponding_recorded_position')
        require(not bar.inventory_popup.isVisible()and not card.isVisible(),'sources445_map_navigation_closes_obscuring_origin_card')
        require(window.run.state==original,'sources445_map_navigation_preserves_run_state')
        mp.refresh();require(mp.view.filter_kind==kind,'sources445_refresh_keeps_source_type')
        require('不保证可达或掉落'in mp.filter_notice.text(),'sources445_map_entry_does_not_claim_reachability_or_drop')
        window.player_source_map_image=bar.map_popup.grab()
        mp.clear_filter.click();require(mp.view.filter_kind is None,'sources445_existing_clear_type_action_is_preserved')
        bar.open_inventory();choose(panel,IDS[0]);panel.source_button.click();gui.processEvents()
        next(b for b in card.cards.buttons if b.property('mapKind')is None).click();gui.processEvents()
        require(card.isVisible()and card.show_conditions.isChecked()and not bar.map_popup.isVisible(),'sources445_pool_click_reads_conditions_without_opening_map')
        with patch('rouge.player_inventory.reference.packet',return_value=None):panel.refresh()
        require(not card.isVisible()and not card.open_map_source(pool_id,kind),'sources445_expired_identity_cannot_navigate')
        panel.refresh();choose(panel,IDS[0]);panel.source_button.click();gui.processEvents();card.show_conditions.setChecked(False)
        require('不是抽取权重或本局获得概率'in card.notice.text(),'sources445_frequency_scope_remains_visible')
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
