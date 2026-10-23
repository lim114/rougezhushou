from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest

from rouge import current_region_reference as model


def clone(root):
    manifest = json.loads((model.ROOT / model.MANIFEST).read_bytes())
    for name in (model.MANIFEST, *manifest['files']):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((model.ROOT / name).read_bytes())


class CurrentRegions359Tests(unittest.TestCase):
    def test_exact_twenty_seven_region_and_grant_bindings(self):
        packet = model.packet()
        self.assertIsNotNone(packet)
        data = packet['data']
        current = model.version.packet()['current']
        self.assertEqual(len(data['rows']), 27)
        self.assertEqual({r['id'] for r in data['rows']}, set(current['details']['zones']))
        self.assertEqual(data['portal_zone_ids'], current['details']['gameConst']['portalZones'])
        grant_originals = current['details']['relics'][model.AP_FEATURE]['buffs']
        for row in data['rows']:
            self.assertEqual(row['zone'], current['details']['zones'][row['id']])
            self.assertEqual(row['mission'], current['modules']['gridZone']['zoneMissionBannerData'][row['id']])
            self.assertIn(row['entry_grant']['original'], grant_originals)
            self.assertFalse(row['entry_grant']['runtime_attached_verified'])
            self.assertIsNone(row['entry_grant']['actual_granted'])
        self.assertEqual([len(model.catalog(group)['rows']) for group in (None, 'exit', 'boss', 'return')], [27, 4, 4, 19])
        self.assertFalse(data['old_budget_replaced'])
        self.assertFalse(data['complete_action_point_calculation'])
        self.assertFalse(data['run_updated'])

    def test_document_corroboration_does_not_invent_variant_or_new_region_proof(self):
        source = model.packet()
        rows = {r['id']: r for r in source['data']['rows']}
        self.assertEqual(rows['zone_1']['document_ap_evidence'], 'unique_name_document_corroboration')
        self.assertEqual(rows['zone_1']['document_ap']['documented_base_ap'], 5)
        for key in ('zone_4', 'zone_4_1'):
            self.assertEqual(rows[key]['document_ap_evidence'], 'name_shared_not_variant_specific')
            self.assertIn('不能把文献当成具体变体的证明', model.player_text(model.reference(key)))
        self.assertEqual(rows['zone_7']['name'], '盲目者所见')
        self.assertEqual(rows['zone_7']['entry_grant']['amount'], 5)
        self.assertEqual(rows['zone_7']['document_ap_evidence'], 'parameter_only')
        self.assertIsNone(rows['zone_7']['document_ap'])
        for row in model.catalog('return')['rows']:
            self.assertEqual(row['document_ap_evidence'], 'parameter_only')
            self.assertIsNone(row['document_ap'])

    def test_optional_first_region_wings_is_only_a_partial_reference(self):
        for active, addition, subtotal in ((None, None, None), (False, 0, 5), (True, 1, 6)):
            result = model.reference('zone_1', wings=active)
            self.assertIs(result['declared']['wings'], active)
            self.assertEqual(result['wings_reference_addition'], addition)
            self.assertEqual(result['base_and_wings_reference_subtotal'], subtotal)
            self.assertIsNone(result['actual_final_entry_ap'])
            self.assertFalse(result['old_budget_replaced'])
        for row in model.catalog()['rows']:
            if row['id'] != 'zone_1':
                self.assertFalse(row['wings_applicable_reference'])
                self.assertIsNone(model.reference(row['id'], wings=True))
                self.assertIsNone(model.reference(row['id'])['base_and_wings_reference_subtotal'])

    def test_exhaustion_zero_boundaries_and_unknown_goal_never_claim_execution(self):
        for zone in ('zone_1', 'zone_3', 'zone_7'):
            for ap, goal, expected in ((None, None, None), (None, False, None), (None, True, False),
                    (0, None, None), (0, False, True), (0, True, False),
                    (1, None, False), (1, False, False), (1, True, False)):
                result = model.reference(zone, action_points=ap, goal_completed=goal)
                self.assertIs(result['exhaustion_description_conditions_match'], expected)
                for field in ('actual_exhaustion_triggered', 'actual_destination_zone', 'actual_return_node', 'actual_final_entry_ap'):
                    self.assertIsNone(result[field])
                self.assertFalse(result['route_recommended'])
        for row in model.catalog('return')['rows']:
            for ap, expected in ((None, None), (0, True), (1, False)):
                result = model.reference(row['id'], action_points=ap)
                self.assertIs(result['exhaustion_description_conditions_match'], expected)
                self.assertIsNone(result['actual_return_node'])
                self.assertIsNone(result['actual_destination_zone'])
                self.assertIn('不是“进入下一主层”', model.player_text(result))
            self.assertIsNone(model.reference(row['id'], goal_completed=False))
        self.assertIn('仅抵达其节点不能算目标完成', model.player_text(model.reference('zone_3')))

    def test_exact_reverse_entry_and_invalid_inputs(self):
        for row in model.catalog()['rows']:
            self.assertEqual(model.locate('regions', row['id']), {'zone_id': row['id']})
        for category, key in (('stages', 'zone_1'), ('regions', 'zone_70'), ('regions', '玻利瓦尔肤层'), (True, 'zone_1')):
            self.assertIsNone(model.locate(category, key))
        for value in (True, False, -1, 0.5, '0', [], 2147483648):
            self.assertIsNone(model.reference('zone_1', action_points=value))
        for value in (0, 1, '是', [], {}):
            self.assertIsNone(model.reference('zone_1', goal_completed=value))
            self.assertIsNone(model.reference('zone_1', wings=value))
        for group in ('unknown', True, [], {}):
            self.assertIsNone(model.catalog(group))
        with patch.object(model, 'packet', return_value=None):
            self.assertIsNone(model.locate('regions', 'zone_1'))
            self.assertIsNone(model.reference('zone_1'))

    def test_every_pinned_source_mutation_and_recovery(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            clone(root)
            with patch.object(model, 'ROOT', root):
                for name in (model.MANIFEST, *json.loads((root / model.MANIFEST).read_bytes())['files']):
                    path = root / name
                    original = path.read_bytes()
                    self.assertIsNotNone(model.packet())
                    path.write_bytes(original + b'x')
                    self.assertIsNone(model.packet(), name)
                    self.assertIsNone(model.reference('zone_1'), name)
                    path.write_bytes(original)
                    self.assertIsNotNone(model.packet(), name)

    def test_independent_results_and_strict_current_semantics(self):
        first = model.catalog()
        first['rows'][0]['entry_grant']['amount'] = 999
        self.assertEqual(model.reference('zone_1')['row']['entry_grant']['amount'], 5)
        current = model.version.packet()['current']
        receipt = json.loads((model.ROOT / model.DOCUMENT_RECEIPT).read_bytes())
        excerpts = json.loads((model.ROOT / model.EXCERPTS).read_bytes())
        changed = deepcopy(current)
        changed['details']['relics'][model.AP_FEATURE]['buffs'][0]['blackboard'][1]['value'] = True
        with self.assertRaises(ValueError):
            model.derive_data(changed, excerpts, receipt)
        changed = deepcopy(current)
        changed['details']['gameConst']['portalZones'][0] = 'zone_1'
        with self.assertRaises(ValueError):
            model.derive_data(changed, excerpts, receipt)
        changed = deepcopy(current)
        changed['customizeData']['commonDevelopment']['developments'][model.WINGS]['rawDesc'] = ['进入每层时，行动力+1']
        with self.assertRaises(ValueError):
            model.derive_data(changed, excerpts, receipt)
        changed_doc = deepcopy(excerpts)
        changed_doc['areas']['玻利瓦尔肤层']['documented_base_ap'] = 6
        with self.assertRaises(ValueError):
            model.derive_data(current, changed_doc, receipt)


if __name__ == '__main__':
    unittest.main()
