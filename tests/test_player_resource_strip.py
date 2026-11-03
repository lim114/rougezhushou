"""Qualified current resources, readable pills and actual width-driven wrapping."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge.player_resource_facts import inventory_summary, resource_rows
from rouge.player_resource_strip import ResourceStrip
from rouge.player_overview import overview_facts
from rouge.run_state import RunState


def fixture():
    return {'relic_count': 3, 'inventory_verified': True,
        'relics': {'rogue_6_relic_legacy_1': {}, 'rogue_6_relic_cargo_1': {}},
        'tactical_tools': {'rogue_6_active_tool_5': {}},
        'operators': {'mechanist': {'present': True}}, 'crew_count': 4,
        'resources': {'gold': {'value': 0, 'captured_at': 1000},
                      'parts_count': {'value': 2, 'capacity': 8}}}


class ResourceFactsTests(unittest.TestCase):
    def test_actual_run_badge_includes_tool_but_relic_denominator_does_not(self):
        with TemporaryDirectory() as folder:
            run = RunState(Path(folder)/'run.json')
            ids = ['rogue_6_relic_legacy_1', 'rogue_6_relic_cargo_1', 'rogue_6_active_tool_5']
            run.apply({'relics': {'ids': ids[:2], 'count': 3, 'source': 'public-test',
                'icons': [{'id': key, 'candidates': [key], 'confirmed': True} for key in ids]}},
                run.state['started_at']+1)
            view = inventory_summary(run.state)
            self.assertTrue(view['complete'])
            self.assertEqual(view['expected_relics'], run.inventory_status()['expected_count'])
            self.assertEqual(view['expected_relics'], 2)
            self.assertEqual(overview_facts(run.state)['已读收藏品'], '2件 / 共2件（另已读1件道具）')

    def test_missing_or_conflicting_evidence_does_not_claim_complete(self):
        for change in ({'relic_count': None}, {'relic_count': True}, {'relic_count': 2},
                       {'inventory_verified': 1}, {'inventory_verified': 'true'}):
            state = {**fixture(), **change}
            self.assertFalse(inventory_summary(state)['complete'], change)
        state = fixture()
        state['relics']['unknown'] = {'held': None}
        self.assertFalse(inventory_summary(state)['complete'])

    def test_partial_tools_do_not_silently_reduce_unknown_relic_total(self):
        state = fixture()
        state['inventory_verified'] = False
        self.assertIsNone(inventory_summary(state)['expected_relics'])
        self.assertNotIn('/ 共', overview_facts(state)['已读收藏品'])

    def test_zero_and_read_life_do_not_fill_other_unknown_resources(self):
        state = fixture()
        state['resources']['life'] = {'value': 99}
        state['config'] = {'difficulty': {'value': 15}}
        before = deepcopy(state)
        rows = {r['key']: r for r in resource_rows(state)}
        self.assertEqual(rows['gold']['value'], '0')
        self.assertEqual(rows['parts']['value'], '2/8')
        self.assertEqual(rows['items']['value'], '3')
        self.assertEqual(rows['crew']['value'], '1/4')
        self.assertEqual(rows['life']['value'], '99')
        for key in ('shield', 'command', 'hope', 'action', 'valuation'):
            self.assertEqual(rows[key]['value'], '未读')
        self.assertEqual(state, before)

    def test_invalid_quantity_and_inconsistent_capacity_stay_distinct(self):
        for value in (None, True, -1, float('inf'), float('nan'), '7'):
            state = fixture()
            state['resources']['gold']['value'] = value
            self.assertEqual(next(r for r in resource_rows(state) if r['key']=='gold')['value'], '未读')
        state = fixture()
        state['resources']['parts_count']['capacity'] = 1
        self.assertEqual(next(r for r in resource_rows(state) if r['key']=='parts')['value'], '2')
        state['crew_count'] = 0
        self.assertEqual(next(r for r in resource_rows(state) if r['key']=='crew')['value'], '待核对')


class ResourceStripTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_wraps_without_overlap_and_reuses_widgets_after_updates(self):
        strip = ResourceStrip(fixture())
        self.addCleanup(strip.close)
        identities = dict(strip.chips)
        row_counts = []
        for width in (280, 480, 840, 1200):
            height = strip.flow.heightForWidth(width)
            strip.resize(width, height)
            strip.show()
            self.qt.processEvents()
            boxes = [w.geometry() for w in strip.chips.values()]
            self.assertTrue(all(strip.rect().contains(r) for r in boxes), (width, height, boxes))
            self.assertTrue(all(not a.intersects(b) for i, a in enumerate(boxes) for b in boxes[i+1:]))
            row_counts.append(len({r.y() for r in boxes}))
        self.assertGreater(row_counts[0], row_counts[-1])
        changed = fixture()
        changed['resources']['gold']['value'] = 9
        strip.refresh(changed)
        self.assertEqual(strip.chips, identities)
        self.assertEqual(strip.chips['gold'].accessibleName(), '源石锭 9')
        strip.refresh({})
        self.assertEqual(strip.chips['gold'].accessibleName(), '源石锭 未读')

    def test_actual_mouse_links_emit_only_local_resource_actions(self):
        for dark in (False, True):
            strip = ResourceStrip(fixture(), dark=dark)
            self.addCleanup(strip.close)
            strip.resize(1200, strip.flow.heightForWidth(1200))
            strip.show()
            self.qt.processEvents()
            actions = []
            strip.requested.connect(actions.append)
            for key in ('items', 'parts', 'crew'):
                widget = strip.chips[key]
                QTest.mouseClick(widget, Qt.MouseButton.LeftButton, pos=widget.rect().center())
            self.assertEqual(actions, ['items', 'parts', 'crew'])


if __name__ == '__main__':
    unittest.main()
