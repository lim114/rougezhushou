"""Actual MainWindow entry checks for sections 247/252/254/258/259/260.

Imported by the temporary current-window runner. This module does not create a
window, alter runtime backends, capture a game, send chat, or execute on import.
The runner owns the temporary public account/run directories and failure log.
"""
from copy import deepcopy
import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication


def run_extra_flows(window, qt, mark, save_result, out):
    def process():
        qt.processEvents()

    def choose(combo, value):
        # QVariant equality can conflate bool and integer declarations. Match
        # both the Python value and type, and compare cell dictionaries directly.
        index = next((i for i in range(combo.count())
                      if type(combo.itemData(i)) is type(value) and combo.itemData(i) == value), -1)
        assert index >= 0, (combo.accessibleName(), value)
        combo.setCurrentIndex(index)
        process()
        assert type(combo.currentData()) is type(value) and combo.currentData() == value

    def select_tree(tree, value):
        def children(parent):
            for index in range(parent.childCount()):
                item = parent.child(index)
                yield item
                yield from children(item)
        for item in children(tree.invisibleRootItem()):
            if item.data(0, Qt.ItemDataRole.UserRole) == value:
                tree.setCurrentItem(item)
                process()
                return item
        raise AssertionError('Missing actual tree row: ' + str(value))

    def reading(edit):
        cursor = edit.textCursor()
        return (cursor.anchor(), cursor.position(),
                edit.verticalScrollBar().value(), edit.horizontalScrollBar().value())

    def select_reading(edit, first=5, last=16, scroll=3):
        cursor = edit.textCursor()
        limit = max(0, edit.document().characterCount() - 1)
        cursor.setPosition(min(first, limit))
        cursor.setPosition(min(last, limit), QTextCursor.MoveMode.KeepAnchor)
        edit.setTextCursor(cursor)
        edit.verticalScrollBar().setValue(scroll)
        process()
        return reading(edit)

    def screenshot(section, widget, name):
        destination = Path(out) / ('current-' + str(section) + '-' + name + '.png')
        destination.parent.mkdir(parents=True, exist_ok=True)
        process()
        picture = widget.grab()
        assert not picture.isNull(), str(destination)
        assert picture.save(str(destination)), str(destination)

    def source_row(panel, channel, node=None, item_id=None, historical=False):
        for i in range(panel.sources.topLevelItemCount()):
            group = panel.sources.topLevelItem(i)
            for j in range(group.childCount()):
                item = group.child(j)
                key = json.loads(item.data(0, Qt.ItemDataRole.UserRole))
                if (key[2] == channel and key[3] == historical and
                        (node is None or key[1] == node) and
                        (item_id is None or key[0] == item_id)):
                    panel.sources.setCurrentItem(item)
                    process()
                    assert panel.selected_row() is not None
                    return panel.selected_row()
        raise AssertionError('Missing actual source row: ' + channel)

    # 247: Open the real secret-merchant action in the MainWindow catalogue.
    before_run = deepcopy(window.run.state)
    catalog = window.node_catalog
    window.centralWidget().setCurrentWidget(catalog)
    catalog.show_directory()
    choose(catalog.kind, None)
    choose(catalog.node_type, '秘境行商')
    choose(catalog.floor, None)
    catalog.search.clear()
    catalog.refresh()
    index = next(i for i, entry in enumerate(catalog.entries)
                 if entry['kind'] == 'function' and entry['record']['node_type'] == '秘境行商')
    catalog.list.setCurrentRow(index)
    process()
    assert catalog.seed_button.isVisible()
    catalog.seed_button.click()
    process()
    seed = catalog.seed_window
    assert seed is not None and seed.isVisible() and not seed.isModal()
    seed.set_reference('rogue_6_legacy_03', seed.context)
    seed.seed_quantity.setValue(1)
    choose(seed.completed, True)
    choose(seed.current_normal, True)
    choose(seed.next_normal, True)
    seed.regions.setValue(1)
    process()
    assert seed.result is not None, seed.summary.text()
    legacy = lambda: next(row for row in seed.result['rows'] if row['item_id'] == 'rogue_6_legacy_03')
    assert legacy()['next_effect_condition_status'] == 'excluded'
    one_region = deepcopy(seed.result)
    seed.regions.setValue(2)
    process()
    assert legacy()['next_effect_condition_status'] == 'matched'
    assert len(seed.result['rows']) == 43
    assert seed.result['actual_seed_consumed'] is None
    assert seed.result['actual_reward_quantity'] is None
    assert not seed.result['inventory_updated'] and not seed.result['run_memory_updated']
    assert not seed.result['next_run_state_created']
    seed.search.setText('襁褓三头犬')
    seed.technical.setChecked(True)
    seed.items.collapseAll()
    text_state = select_reading(seed.detail, 3, 10, 35)
    seed.refresh()
    process()
    assert seed.selected_id() == 'rogue_6_legacy_03'
    assert reading(seed.detail) == text_state
    assert not seed.items.topLevelItem(0).isExpanded()
    catalog.refresh()
    process()
    assert seed.selected_id() == 'rogue_6_legacy_03'
    assert seed.seed_quantity.value() == 1 and seed.regions.value() == 2
    assert seed.completed.currentData() is True and seed.next_normal.currentData() is True
    assert seed.current_normal.currentData() is True and seed.technical.isChecked()
    assert seed.result is not None, seed.summary.text()
    assert legacy()['next_effect_condition_status'] == 'matched'
    assert reading(seed.detail) == text_state
    assert not seed.items.topLevelItem(0).isExpanded()
    seed.close()
    catalog.seed_button.click()
    process()
    assert catalog.seed_window is seed and seed.isVisible()
    assert seed.seed_quantity.value() == 1 and seed.regions.value() == 2
    assert window.run.state == before_run
    save_result(247, {'one_region': one_region, 'two_regions': deepcopy(seed.result)})
    screenshot(247, seed, 'seed')
    mark(247, 'actual secret-merchant seed entry; 1/2-region boundary and reading/declare refresh')
    seed.close()

    # 252: Snapshot the actual temporary account and fill the real modal editor.
    from rouge.p2_technology_upgrade import capture_account_reference
    from rouge.p2_technology_upgrade_view import TechnologyTargetDialog
    technology = window.technology_reference
    window.centralWidget().setCurrentWidget(technology)
    account_before = capture_account_reference(technology.account_state)
    technology.upgrade_planner_button.click()
    process()
    planner = technology.upgrade_planner_window
    assert planner is not None and planner.isVisible()
    assert planner.snapshot == account_before
    assert planner.mode.currentData() is None
    assert (planner.grade.value(), planner.budget.value()) == (-1, -1)
    assert planner.gates.item(0, 7).text() == '未知'
    choose(planner.mode, 'regular')
    planner.grade.setValue(3)
    planner.budget.setValue(5)
    modal_errors = []

    def fill_real_target():
        editor = QApplication.activeModalWidget()
        try:
            assert isinstance(editor, TechnologyTargetDialog), type(editor)
            choose(editor.node, 'rogue_6_outbuff_10')
            choose(editor.acceptance, True)
            editor.charge.setValue(2)
            editor.refund.setValue(0)
            editor.accept()
        except BaseException as error:
            modal_errors.append(error)
            if editor is not None:
                editor.reject()

    QTimer.singleShot(0, fill_real_target)
    planner.add_button.click()
    if modal_errors:
        raise modal_errors[0]
    planner.calculate_button.click()
    process()
    assert planner.result is not None, planner.details.toPlainText()
    assert planner.table.rowCount() == 1
    assert planner.table.item(0, 6).text() == '3'
    assert planner.result['rows'][0]['nominal_new_node_cost'] == 2
    assert planner.result['declared_budget_after'] == 3
    assert planner.result['final_gates'][0]['eligible_reference'] is True
    assert planner.gates.item(0, 5).text() == '符合'
    assert planner.gates.item(0, 7).text() == '未知'
    assert planner.result['actual_activation'] is None
    regular_result = deepcopy(planner.result)
    steps_before = deepcopy(planner.steps)
    choose(planner.mode, 'other')
    assert planner.result is None and not planner.copy_button.isEnabled()
    assert planner.steps == steps_before and planner.snapshot == account_before
    planner.calculate_button.click()
    process()
    assert planner.result['final_gates'][0]['eligible_reference'] is False
    assert planner.result['declared_budget_after'] == 3
    assert capture_account_reference(technology.account_state) == account_before
    assert window.run.state == before_run
    save_result(252, {'regular': regular_result, 'other': deepcopy(planner.result),
                      'captured_account_snapshot': account_before})
    screenshot(252, planner, 'technology')
    mark(252, 'actual account-snapshot entry and real target modal; declared 5-2+0=3; mode invalidation')
    planner.close()

    # 254: Actual battle entry; source-backed top positions and unknown cells.
    from rouge.fixed_landmark_mapping import landmark_data
    from rouge.highland_top_mapping import highland_top_data
    ground_before = deepcopy(landmark_data())
    window.show_catalog_battle('ro6_n_4_1')
    process()
    battle = window.battle_preview
    assert battle.current_stage == 'ro6_n_4_1'
    assert battle.highland_top_button.isEnabled()
    battle.highland_top_button.click()
    process()
    highland = battle.highland_top_dialog
    assert highland is not None and highland.isVisible()
    panel = highland.panel
    assert panel.cell_combo.count() == 10

    def highland_cell(cell):
        choose(panel.cell_combo, cell)
        return panel.canvas.reference.top_center(cell) if panel.canvas.reference else None

    assert highland_cell({'row': 1, 'col': 3}) == (185, 65)
    assert '菱形表面参考' in panel.status.text()
    assert highland_cell({'row': 3, 'col': 3}) is None
    assert '位置未知' in panel.status.text()
    highland.set_stage('ro6_n_4_1')
    process()
    assert panel.canvas.selected_cell == {'row': 3, 'col': 3}
    choose(panel.stage_combo, 'ro6_e_4_1')
    assert panel.canvas.selected_cell == {'row': 3, 'col': 3}
    assert panel.canvas.reference.top_center(panel.canvas.selected_cell) is None
    assert highland_cell({'row': 2, 'col': 8}) == (367, 93)
    assert highland_cell({'row': 2, 'col': 3}) == (184, 93)
    for width, height in ((1050, 720), (680, 900), (1300, 480)):
        highland.resize(width, height)
        process()
        assert panel.canvas.reference.top_center(panel.canvas.selected_cell) == (184, 93)
        assert not highland.grab().isNull()
    for stage_id in ('ro6_n_2_4', 'ro6_e_2_4'):
        highland.set_stage(stage_id)
        process()
        assert panel.cell_combo.count() == 8 and panel.canvas.reference is None
        for index in range(panel.cell_combo.count()):
            panel.cell_combo.setCurrentIndex(index)
            process()
            assert '表面位置未知' in panel.cell_combo.currentText()
            assert '位置未知' in panel.status.text()
        selected = deepcopy(panel.canvas.selected_cell)
        highland.set_stage(stage_id)
        process()
        assert panel.canvas.selected_cell == selected
    highland.set_stage('ro6_n_4_1')
    assert highland_cell({'row': 3, 'col': 3}) is None
    highland.close()
    battle.highland_top_button.click()
    process()
    assert battle.highland_top_dialog is highland and highland.isVisible()
    assert panel.canvas.selected_cell == {'row': 3, 'col': 3}
    assert panel.canvas.reference.top_center(panel.canvas.selected_cell) is None
    assert landmark_data() == ground_before
    assert window.run.state == before_run
    save_result(254, {'source_reference': deepcopy(highland_top_data()),
                      'literal_known_points': [[1, 3, 185, 65], [2, 8, 367, 93], [2, 3, 184, 93]],
                      'selected_unknown_cell': deepcopy(panel.canvas.selected_cell),
                      'ground_reference_unchanged': True})
    screenshot(254, highland, 'highland-unknown')
    mark(254, 'actual highland battle entry; known/unknown cells, same-source retention and three ratios')
    highland.close()

    # 258: Open through MainWindow; declarations belong to an explicit local graph.
    window.centralWidget().setCurrentWidget(window.exploration_map_tab)
    window.movement_source_button.click()
    process()
    movement = window.movement_source_dialog
    assert movement is not None and movement.isVisible() and not movement.isModal()
    assert movement.targets.topLevelItemCount() == 12
    m04, m08 = 'rogue_6_scrap_M_04', 'rogue_6_scrap_M_08'
    shop_context = {'node_type': '秘境行商', 'gold': 6, 'item_quantities': {m04: 0}}
    movement.set_reference([m04], context=shop_context)
    source_row(movement, 'scrap_shop')
    assert movement.price.value() == -1 and not movement.unmodified.isChecked()
    choose(movement.access, True)
    choose(movement.stock, True)
    assert movement.selected_row()['status'] == 'unknown'
    movement.unmodified.setChecked(True)
    process()
    assert movement.selected_row()['status'] == 'matched'
    assert movement.selected_row()['comparison_price_reference'] == 6
    documented_shop = deepcopy(movement.result)
    movement.price.setValue(5)
    process()
    assert '矛盾' in movement.detail.toPlainText()
    assert movement.selected_row() is not None and movement.price.isEnabled()
    movement.unmodified.setChecked(False)
    process()
    assert movement.selected_row()['comparison_price_reference'] == 5
    assert movement.selected_row()['comparison_price_source'] == 'independent_declared_price'
    declared_shop = deepcopy(movement.result)
    graph = {'zone_id': 'z', 'template_id': 't', 'nodes': [
        {'id': 's', 'row': 0, 'col': 0, 'observed_type': '秘境行商'}]}
    epoch = window.run.state['id']
    movement.set_reference([m04, m08], graph, {'gold': 6}, epoch=epoch)
    source_row(movement, 'seed', 's', m04)
    assert movement.seed.isEnabled() and not movement.price.isEnabled()
    choose(movement.access, True)
    choose(movement.seed, True)
    choose(movement.completion, True)
    assert movement.selected_row()['status'] == 'matched'
    source_row(movement, 'seed', 's', m08)
    assert movement.selected_row()['status'] == 'matched'
    seed_sources = deepcopy(movement.result)
    movement.set_reference([m04], graph, {'gold': 6}, epoch=epoch)
    source_row(movement, 'scrap_shop', 's', m04)
    choose(movement.stock, True)
    movement.unmodified.setChecked(True)
    process()
    movement.sources.topLevelItem(0).setExpanded(False)
    key = movement.selected_key()
    text_state = select_reading(movement.detail)
    movement.set_map_context(deepcopy(graph), {'gold': 6}, epoch=epoch)
    process()
    assert movement.target_ids() == [m04] and movement.selected_key() == key
    assert movement.stock.currentData() is True and movement.unmodified.isChecked()
    assert not movement.sources.topLevelItem(0).isExpanded()
    assert reading(movement.detail) == text_state
    refreshed = deepcopy(movement.result)
    movement.set_map_context(graph, epoch=epoch + '-different-public-declaration')
    source_row(movement, 'scrap_shop', 's', m04)
    assert movement.selected_row()['stock_presence_declared'] is None
    movement.set_map_context(graph, {'gold': 6}, epoch=epoch)
    source_row(movement, 'scrap_shop', 's', m04)
    assert movement.selected_row()['stock_presence_declared'] is True
    assert not movement.result['inventory_updated'] and not movement.result['run_state_updated']
    # Verify catalogue buttons actually reach the real MainWindow catalogue.
    path_graph = {'zone_id': 'z', 'template_id': 'path-t', 'nodes': [
        {'id': 'e', 'row': 2, 'col': 4, 'observed_type': '险路小径'}]}
    movement.set_reference([m08], path_graph, epoch=epoch)
    source_row(movement, 'path_exit', 'e', m08)
    assert movement.catalogue.count() == 3
    assert len({movement.catalogue.itemText(i) for i in range(3)}) == 3
    for index, event_id in enumerate(('community_group_034', 'community_group_035', 'community_group_036')):
        movement.catalogue.setCurrentIndex(index)
        movement.catalogue_button.click()
        process()
        selected = catalog.list.selected_key()
        assert selected == 'event:' + event_id, (selected, event_id)
        assert window.centralWidget().currentWidget() is catalog
    assert not movement.result['source_origin_gap_closed']
    assert window.run.state == before_run
    save_result(258, {'documented_shop': documented_shop, 'declared_shop': declared_shop,
                      'seed_sources': seed_sources, 'same_scope_refresh': refreshed,
                      'path_catalogue': deepcopy(movement.result)})
    screenshot(258, movement, 'movement-sources')
    mark(258, 'actual source entry; explicit shop/seed declarations, scoped refresh and three catalogue links')
    movement.close()

    # 259: Actual map-page entry; route identity must be declared independently.
    window.centralWidget().setCurrentWidget(window.exploration_map_tab)
    window.fruit_marker_button.click()
    process()
    fruit = window.fruit_marker_dialog
    assert fruit is not None and fruit.isVisible() and not fruit.isModal()
    declaration = {'map_id': 'explicit-map', 'node_id': 'marked-A', 'node_type': '曲折密道',
                   'marker': 'fruit', 'paired_node_id': 'paired-B'}
    fruit.set_reference(declaration)
    choose(fruit.performed, True)
    fruit.set_corridor_route(entry_node_id='marked-A', exit_node_id='paired-B', from_other_end=True)
    fruit.visit_button.click()
    process()
    assert fruit.events == [] and '此步骤未加入' in fruit.summary.text()
    fruit.set_corridor_route(entry_node_id='paired-B', exit_node_id='marked-A', from_other_end=True)
    fruit.visit_button.click()
    process()
    assert len(fruit.result['rows']) == 1
    assert fruit.result['rows'][0]['condition_status'] == 'matched'
    assert fruit.result['rows'][0]['source_condition_reward_quantity'] == 1
    assert fruit.result['final_marker_reference'] == 'fruit'
    first_visit = deepcopy(fruit.result)
    fruit.visit_button.click()
    process()
    assert [row['source_condition_reward_quantity'] for row in fruit.result['rows']] == [1, 1]
    assert fruit.result['whole_reward_total'] is None and fruit.result['repeated_trigger_cap'] is None
    assert all(row['actual_reward_received'] is None and row['actual_marker_after'] is None
               for row in fruit.result['rows'])
    assert not fruit.result['run_state_written'] and not fruit.result['game_operated']
    fruit.technical.setChecked(True)
    fruit.steps.setCurrentItem(fruit.steps.topLevelItem(0))
    events_before = deepcopy(fruit.events)
    text_state = select_reading(fruit.detail)
    fruit.refresh()
    process()
    assert fruit.events == events_before and fruit.technical.isChecked()
    assert fruit.entry_id.text() == 'paired-B' and fruit.exit_id.text() == 'marked-A'
    assert fruit.from_other.currentData() is True
    assert fruit.steps.currentItem().data(0, Qt.ItemDataRole.UserRole) == 1
    assert reading(fruit.detail) == text_state
    map_selection = window.map_view.selected
    fruit.node_button.click()
    process()
    assert window.centralWidget().currentWidget() is window.exploration_map_tab
    assert '局外声明节点引用' in window.map_detail.toPlainText()
    assert 'explicit-map' in window.map_detail.toPlainText() and 'marked-A' in window.map_detail.toPlainText()
    assert '实际地图绑定未核实' in window.map_detail.toPlainText()
    assert window.map_view.selected == map_selection
    fruit.close()
    window.fruit_marker_button.click()
    process()
    assert window.fruit_marker_dialog is fruit and fruit.isVisible()
    assert fruit.events == events_before and reading(fruit.detail) == text_state
    repeated_visits = deepcopy(fruit.result)
    changed = deepcopy(declaration)
    changed['node_id'] = 'new-C'
    fruit.set_reference(changed)
    process()
    assert fruit.result is None and not fruit.node_button.isEnabled()
    assert fruit.events == events_before
    fruit.set_reference(declaration)
    process()
    assert fruit.result is not None
    assert window.run.state == before_run
    save_result(259, {'first_visit': first_visit, 'repeated_visits': repeated_visits,
                      'preserved_events_on_rebind': events_before})
    screenshot(259, fruit, 'fruit-marker')
    mark(259, 'actual fruit entry; wrong/correct opposite-end identity, conditional one and preserved offline steps')
    fruit.close()

    # 260: Real tab and buttons, overload math with independently declared weights.
    capacity = window.inventory_capacity
    window.centralWidget().setCurrentWidget(capacity)
    capacity.load_example.click()
    capacity.run_button.click()
    process()
    result = capacity.result_snapshot()
    assert result is not None, capacity.status.text()
    initial = result['initial']
    assert (initial['declared_occupied'], initial['capacity'], initial['free_units']) == (7, 5, -2)
    assert initial['minimum_release_units'] == 2 and initial['declared_overloaded'] is True
    assert initial['documented_action_gate'] == 'blocked_by_declared_overload'
    assert initial['pursuit_exempt_from_overload'] is False
    assert initial['actual_game_action_allowed'] is None
    assert result['minimum_release']['minimum_discarded_instances'] == 1
    assert result['minimum_release']['candidate_discard_sets'] == [
        {'instance_ids': ['b'], 'released_units': 2}, {'instance_ids': ['c'], 'released_units': 2}]
    assert result['proposals'][0]['after_discard']['declared_occupied'] == 5
    assert result['proposals'][0]['after_discard']['declared_overloaded'] is False
    assert result['proposals'][1]['after_receive']['declared_occupied'] == 4
    assert result['inventory_updated'] is False
    assert '含追猎' in capacity.result_view.toPlainText()
    editor_before = capacity.editor.toPlainText()
    html_before = capacity.result_view.toHtml()
    capacity.set_context({'capacity': 100, 'items': []})
    window.render_map()
    process()
    assert capacity.editor.toPlainText() == editor_before
    assert capacity.result_view.toHtml() == html_before and capacity.result_snapshot() == result
    capacity.editor.setPlainText('{"snapshot":1,"snapshot":2}')
    assert capacity.result_snapshot() is None
    capacity.run_button.click()
    process()
    assert '重复声明键' in capacity.status.text()
    assert capacity.result_snapshot() is None and capacity.result_view.toPlainText() == ''
    capacity.load_example.click()
    capacity.run_button.click()
    process()
    assert capacity.result_snapshot() == result
    assert window.run.state == before_run
    save_result(260, result)
    screenshot(260, window, 'capacity-mainwindow')
    mark(260, 'actual capacity tab; 7/5 overload, one-instance alternatives, host refresh and strict duplicate-key recovery')
