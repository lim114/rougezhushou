from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest

from rouge import current_bank_reference as model


def clone(root):
    manifest = json.loads((model.ROOT / model.MANIFEST).read_bytes())
    for name in (model.MANIFEST, *manifest['files']):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((model.ROOT / name).read_bytes())


class CurrentBank356Tests(unittest.TestCase):
    def test_five_complete_sources_and_explicit_name_binding(self):
        result = model.reference()
        self.assertIsNotNone(result)
        self.assertEqual([r['threshold'] for r in result['rows']], [15, 50, 125, 250, 500])
        self.assertEqual({r['id'] for r in result['rows']}, set(model.REWARD_IDS))
        self.assertTrue(all(r['cumulative_condition_matches'] is None for r in result['rows']))
        current = model.version.packet()['current']['details']
        self.assertEqual(result['data']['bank_records'], sorted(current['bankRewards'], key=lambda r: r['unlockGoldCnt']))
        self.assertEqual(result['data']['item'], current['items'][model.ITEM_ID])
        self.assertEqual(result['data']['document']['revision'], 433770)
        self.assertIn('not_original_item_id_pointer', result['data']['item_binding']['basis'])
        self.assertIsNone(result['actual_unlocked'])
        self.assertFalse(result['run_updated'])
        self.assertFalse(result['account_updated'])

    def test_every_threshold_boundaries_never_become_actual_unlock_or_grant(self):
        for threshold in model.THRESHOLDS:
            for value in (threshold - 1, threshold, threshold + 1):
                result = model.reference(cumulative=value)
                row = next(r for r in result['rows'] if r['threshold'] == threshold)
                self.assertEqual(row['cumulative_condition_matches'], value >= threshold)
                self.assertEqual(row['cumulative_difference'], max(0, threshold - value))
                self.assertIsNone(row['actual_unlocked'])
                self.assertIsNone(row['actual_received'])
                self.assertIsNone(result['actual_shop_slots'])
                self.assertIsNone(result['actual_unlock_total'])

    def test_conflicting_counters_stay_independent_and_both_originals_visible(self):
        for cumulative, peak, cumulative_match, peak_match in ((250, 249, True, False),
                (249, 250, False, True), (None, 250, None, True), (250, None, True, None)):
            result = model.reference(cumulative=cumulative, peak_balance=peak)
            row = next(r for r in result['rows'] if r['id'] == 'bank_reward_4')
            self.assertIs(row['cumulative_condition_matches'], cumulative_match)
            self.assertIs(row['legacy_peak_condition_matches'], peak_match)
            text = model.player_text(result, row['id'])
            self.assertIn('历史累计投资', text)
            self.assertIn('投资储备余额最高达到过250', text)
            self.assertIn('实际解锁', text)
            self.assertIn('不能直接记为领取1件', text)
        for row in model.reference(500, 500)['rows']:
            if row['id'] != 'bank_reward_4':
                self.assertFalse(row['has_counter_conflict'])
                self.assertIsNone(row['legacy_peak_condition_matches'])
                self.assertIsNone(row['item_target'])

    def test_exact_forward_and_reverse_targets_and_source_failure(self):
        self.assertEqual(model.locate('relics', model.ITEM_ID), {'reward_id': 'bank_reward_4'})
        item = model.item_reference('bank_reward_4')
        self.assertEqual(item['target'], {'category': 'relics', 'key': model.ITEM_ID})
        self.assertTrue(item['unlock_not_acquisition'])
        self.assertIsNotNone(model.icon_bytes())
        for target in (None, True, 'bank_reward_2', 'bank_reward_4-extra'):
            self.assertIsNone(model.item_reference(target))
        for cat, key in (('scrap', model.ITEM_ID), ('relics', 'rogue_6_relic_legacy_61'), (True, model.ITEM_ID)):
            self.assertIsNone(model.locate(cat, key))
        with patch.object(model, 'packet', return_value=None):
            self.assertIsNone(model.locate('relics', model.ITEM_ID))
            self.assertIsNone(model.item_reference('bank_reward_4'))
            self.assertIsNone(model.icon_bytes())

    def test_each_pinned_file_mutation_and_recovery(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            clone(root)
            with patch.object(model, 'ROOT', root):
                names = [model.MANIFEST, *json.loads((root / model.MANIFEST).read_bytes())['files']]
                for name in names:
                    path = root / name
                    raw = path.read_bytes()
                    self.assertIsNotNone(model.packet())
                    path.write_bytes(raw + b'x')
                    self.assertIsNone(model.packet(), name)
                    self.assertIsNone(model.reference(250, 250), name)
                    path.write_bytes(raw)
                    self.assertIsNotNone(model.packet(), name)

    def test_invalid_numbers_no_boolean_coercion_and_defensive_results(self):
        for value in (True, False, -1, 0.5, '250', [], 2147483648):
            self.assertIsNone(model.reference(cumulative=value))
            self.assertIsNone(model.reference(peak_balance=value))
        result = model.reference(500)
        result['rows'][0]['threshold'] = 0
        result['data']['item']['name'] = '伪造'
        self.assertEqual(model.reference(500)['rows'][0]['threshold'], 15)
        self.assertEqual(model.item_reference('bank_reward_4')['item']['name'], '金酒之杯')

    def test_full_document_fragment_and_current_source_semantics_required(self):
        current = model.version.packet()['current']['details']
        receipt = json.loads((model.ROOT / model.DOCUMENT_RECEIPT).read_bytes())
        fragment = (model.ROOT / model.EXCERPT).read_text(encoding='utf8')
        with self.assertRaises(ValueError):
            model.derive_data(current, fragment.replace('<td>500</td>', '<td>501</td>'), receipt)
        changed = json.loads(json.dumps(current))
        changed['gameConst']['bankRewardCountType'] = 'MAX_BALANCE'
        with self.assertRaises(ValueError):
            model.derive_data(changed, fragment, receipt)
        changed = json.loads(json.dumps(current))
        changed['items'][model.ITEM_ID]['unlockCondDesc'] = '已修正为累计投资'
        with self.assertRaises(ValueError):
            model.derive_data(changed, fragment, receipt)


if __name__ == '__main__':
    unittest.main()
