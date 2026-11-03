"""Actual Windows resource links and layout, using public temporary state only."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import argparse, json, sys

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    original = player_acceptance.check
    images = []

    def check(section, window, gui, require):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from rouge.player_map_acceptance import fixtures

        original(section, window, gui, require)
        before = deepcopy(window.run.state)
        bar = window.compact_window

        def save(widget, name):
            path = args.receipt.with_name(name + '.png')
            require(widget.grab().save(str(path)), name + '_image_saved')
            images.append({'file': path.as_posix(), 'sha256': sha256(path.read_bytes()).hexdigest()})

        def click(strip, key):
            chip = strip.chips[key]
            QTest.mouseClick(chip, Qt.MouseButton.LeftButton, pos=chip.rect().center())
            gui.processEvents()

        try:
            graphs, *_ = fixtures()
            state = window.run.state
            state.update(maps={g['zone_id']: g for g in graphs},
                relic_count=3, inventory_verified=True,
                relics={'rogue_6_relic_legacy_1': {}, 'rogue_6_relic_cargo_1': {}},
                tactical_tools={'rogue_6_active_tool_5': {}}, crew_count=4,
                operators={'mechanist': {'present': True}},
                resources={'gold': {'value': 0, 'captured_at': 1000}, 'parts_count': {'value': 2, 'capacity': 8}})
            state['config']['difficulty'] = {'value': 15}
            state['config']['squad'] = {'name': '隔离样例分队'}
            state['history'] = [{'kind': 'floor_resources_read', 'source': 'same_frame_zone_and_resources',
                'at': 900, 'zone_id': graphs[0]['zone_id'], 'template_id': graphs[0]['template_id'], 'values': {'gold': 7}}]
            bar.open_map(); gui.processEvents()
            panel = bar.map_popup.panel
            panel.floors.setCurrentIndex(0); gui.processEvents()
            require('源石锭 7' in panel.floor_resources.text(), 'historical_floor_quantity_remains_separate')
            require(panel.resources.chips['gold'].accessibleName() == '源石锭 0', 'zero_current_quantity_is_not_historical_seven')
            require('保密等级 15' in panel.status.text() and '隔离样例分队' in panel.status.text(), 'difficulty_and_squad_remain_visible')
            selected = panel.view.selected
            panel.details_toggle.setChecked(False)
            for width in (840, 1100):
                bar.map_popup.resize(width, 650); QTest.qWait(100); gui.processEvents()
                boxes = [chip.geometry() for chip in panel.resources.chips.values()]
                require(all(panel.resources.rect().contains(box) for box in boxes), f'map_resource_pills_fit_{width}')
                require(all(not a.intersects(b) for i, a in enumerate(boxes) for b in boxes[i+1:]), f'map_resource_pills_do_not_overlap_{width}')
                panel.status.setText('隔离样例：仅验证显示与联动，不是本局实读。')
                save(bar.map_popup, 'map-' + str(width))
            click(panel.resources, 'items')
            inv = bar.inventory_popup
            require(inv.isVisible() and inv.pages.currentWidget() is inv.panel, 'map_items_link_opens_exact_inventory_tab')
            require(not bar.map_popup.isVisible(), 'resource_navigation_uses_single_active_popup')
            require(inv.resources.chips['items'].accessibleName() == '藏品/道具 3', 'inventory_reuses_current_resource_facts')
            click(inv.resources, 'parts')
            require(inv.isVisible() and inv.pages.currentWidget() is inv.parts, 'parts_link_selects_exact_parts_tab')
            click(inv.resources, 'items')
            inv.panel.search.clear(); inv.resize(840, 650); gui.processEvents()
            inv.layout().itemAt(0).layout().itemAt(0).widget().setText('隔离样例：收藏品与资源显示')
            save(inv, 'inventory-840')
            inv.panel.search.setText('隔离样例')
            state['resources']['gold']['value'] = 9
            bar.refresh(); gui.processEvents()
            require(inv.resources.chips['gold'].accessibleName() == '源石锭 9', 'visible_inventory_receives_fresh_resource_value')
            require(inv.panel.search.text() == '隔离样例', 'resource_update_preserves_inventory_search')
            click(inv.resources, 'crew')
            require(bar.team_popup.isVisible() and not inv.isVisible(), 'crew_link_opens_local_team_without_game_operation')
            bar.open_map(); gui.processEvents()
            require(panel.view.selected == selected, 'resource_navigation_keeps_selected_map_position')
            require(panel.resources.chips['gold'].accessibleName() == '源石锭 9', 'return_to_map_uses_latest_run_reading')
            window.run.state = deepcopy(before)
            bar.refresh(); gui.processEvents()
            require(panel.resources.chips['gold'].accessibleName() == '源石锭 未读', 'replaced_temporary_run_does_not_keep_stale_resources')
            window.player_validation_target = bar.map_popup
        finally:
            window.run.state = before

    player_acceptance.check = check
    code = run(440, args.receipt)
    args.receipt.with_name('resource-images.json').write_text(json.dumps({
        'kind': 'maintenance_not_new_section', 'images': images,
        'fixtures': 'Public synthetic temporary state, no private or actual-game readings.'},
        ensure_ascii=False, indent=2) + '\n', 'utf-8')
    raise SystemExit(code)
