from copy import deepcopy
from PySide6.QtCore import Qt

def check(window,gui,require):
    before=deepcopy(window.run.state);window.show_compact();bar=window.compact_window;bar.open_inventory();gui.processEvents();inventory=bar.inventory_popup.panel
    from .player_exchange_view import related_exchanges
    data=inventory.source_index.data;version=inventory.version.currentData()
    inputs=[identity for identity in inventory.rows if related_exchanges(data,version,identity)]
    inventory.held.setChecked(False);inventory.refresh();inputs=[identity for identity in inventory.rows if related_exchanges(data,version,identity)];require(bool(inputs),'fixed_relics_have_explicit_exchange_source_links')
    identity=inputs[0]
    for index in range(inventory.entries.count()):
        if inventory.entries.item(index).data(Qt.ItemDataRole.UserRole)==identity:inventory.entries.setCurrentRow(index);break
    gui.processEvents();require(inventory.exchange_button.isVisible(),'eligible_relic_has_visible_exchange_candidate_entry')
    inventory.exchange_button.click();gui.processEvents();popup=bar.exchange_popup;page=popup.panel
    require(popup.isVisible()and page.identity==identity and page.version==version,'exact_item_and_source_range_bound_without_run_change')
    require(page.entries.count()==0 and not page.open_button.isEnabled(),'reward_relation_requires_explicit_choice')
    page.choices.setCurrentIndex(1);require(page.entries.count()==len(page.current_link()['members']),'source_output_members_not_guessed_from_input_rarity')
    page.entries.setCurrentRow(0);require('不能据此认定本次'in page.detail.toPlainText(),'reference_candidates_not_actual_reward_claim')
    seen=[];page.openPool.connect(lambda *value:seen.append(value));page.open_button.click();gui.processEvents()
    require(seen==[(version,page.current_link()['output_id'])],'complete_source_link_carries_exact_output_id')
    archive=window.public_archive;require(archive is not None and archive.isVisible(),'output_pool_source_opens_as_actual_local_dialog');archive.close();bar.open_exchange(version,identity);page.choices.setCurrentIndex(1);page.entries.setCurrentRow(0)
    old=page.entries.currentItem();bar.refresh();require(page.entries.currentItem()is old,'unrelated_frame_refresh_keeps_exchange_reading')
    page.refresh_source(None,None);require(page.entries.count()==0 and not page.open_button.isEnabled(),'source_failure_clears_reward_candidates_and_navigation')
    page.refresh_source(data,inventory.source_signature);require(page.entries.count()==0,'source_recovery_requires_relation_selection')
    page.choices.setCurrentIndex(1);page.entries.setCurrentRow(0);window.player_validation_target=popup;require(window.run.state==before,'exchange_reference_does_not_transact_or_reset_run')

