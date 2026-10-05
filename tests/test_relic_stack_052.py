"""Known final HP scalers compose after the coffee direct multiplier layer.

The pinned child templates and the attribute formula are cited in
.cache/research/relic-stack-052/evidence.json. These are static alternatives,
not sampled coffee outcomes or claimed automatic counter readings.
Independent same-key FINAL_SCALER instances are proved in
.cache/research/p1-native-runtime-054/timer-book-sniper-summary.json.
"""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

COFFEE = 'rogue_6_relic_fight_25'
DRAGON = 'rogue_6_start_3'
PROBE = 'rogue_6_relic_fight_30'
PICTURE = 'rogue_6_relic_legacy_84'
HYDRA = 'rogue_6_start_4'


def scenario(**extra):
    return {'operator': 'mechanist', 'skill': 3,
            'target_enemy': {'stage_id': 'ro6_n_1_2', 'enemy_id': 'enemy_2137_shsdgo', 'level': 0},
            'run_config': {'difficulty': {'value': 4}, 'zone': {'id': 'zone_1'}}, **extra}


class RelicStack052Tests(unittest.TestCase):
    def assert_branches(self, source, factor):
        base = calculate_damage({**source, 'relic_ids': []})['run_resolution']['enemy']['stats']['maxHp']
        result = calculate_damage(source)
        enemy = result['run_resolution']['enemy']
        branches = enemy['spawn_hp']
        self.assertEqual(branches['excluded_hp_sources'], [])
        self.assertAlmostEqual(enemy['stats']['maxHp'], base * factor)
        self.assertAlmostEqual(branches['untriggered_max_hp'], base * factor)
        self.assertAlmostEqual(branches['triggered_max_hp'], base * factor * 2)
        self.assertAlmostEqual(branches['single_item_triggered_max_hp'], base * 2)
        self.assertIsNone(branches['current_variant'])
        self.assertEqual(branches['probabilities'], {'untriggered': .97, 'triggered': .03})
        return result

    def test_coffee_composes_with_confirmed_active_dragon_final_scaler(self):
        for count in (0, 1, 2):
            with self.subTest(count=count):
                self.assert_branches(scenario(relic_ids=[COFFEE, DRAGON],
                                              relic_context={'entered_zone_count': count}), .5)

    def test_coffee_composes_with_confirmed_probe_final_scaler(self):
        for count in (0, 1, 2, 99, 100):
            with self.subTest(count=count):
                self.assert_branches(scenario(relic_ids=[COFFEE, PROBE],
                                              relic_context={'probe_stacks': count}), 1+.2*min(count, 99))

    def test_two_distinct_final_scalers_compose_after_coffee(self):
        self.assert_branches(scenario(relic_ids=[COFFEE, DRAGON, PROBE],
                                      relic_context={'entered_zone_count': 1, 'probe_stacks': 2}), .5*1.4)

    def test_missing_counter_still_blocks_coffee_combination(self):
        for rid in (DRAGON, PROBE):
            with self.subTest(relic=rid):
                branches = calculate_damage(scenario(relic_ids=[COFFEE, rid]))['run_resolution']['enemy']['spawn_hp']
                self.assertEqual(branches['excluded_hp_sources'], [rid])
                self.assertIsNone(branches['triggered_max_hp'])

    def test_native_same_key_hp_scalers_compose_but_hydra_growth_stays_pending(self):
        for rid, factor in ((PICTURE,.95),(HYDRA,1.3)):
            with self.subTest(relic=rid):
                result = self.assert_branches(scenario(relic_ids=[COFFEE, PROBE, rid],
                    relic_context={'probe_stacks': 2}), 1.4*factor)
                record=next(r for r in result['relic_resolution']['records'] if r['id']==rid)
                if rid==HYDRA:
                    # Only the initial1.3 prefab is verified; no region history
                    # or repeated ZoneIntoBuff applications are invented.
                    self.assertFalse(result['relic_resolution']['complete'])
                    self.assertTrue(any('zone_into_buff' in x for x in record['pending']))

    def test_duplicate_and_ordered_ids_do_not_change_known_composition_or_inputs(self):
        src = scenario(relic_ids=[COFFEE, DRAGON, PROBE],
                       relic_context={'entered_zone_count': 2, 'probe_stacks': 2})
        before = copy.deepcopy(src)
        first = self.assert_branches(src, .7)
        second = self.assert_branches({**src, 'relic_ids': [PROBE, COFFEE, DRAGON, PROBE, COFFEE]}, .7)
        self.assertEqual(first['run_resolution']['enemy']['spawn_hp'], second['run_resolution']['enemy']['spawn_hp'])
        self.assertEqual(src, before)

    def test_wrong_target_does_not_apply_probe_or_require_its_counter(self):
        self.assert_branches(scenario(relic_ids=[COFFEE, PROBE],
                                      target_enemy={'stage_id': 'ro6_n_1_2', 'enemy_id': 'enemy_1093_ccsbr', 'level': 0}), 1)

    def test_known_expired_dragon_does_not_change_coffee_branch(self):
        self.assert_branches(scenario(relic_ids=[COFFEE, DRAGON], relic_context={'entered_zone_count': 3}), 1)

    def test_report_shows_composite_alternatives_without_claiming_current_trigger(self):
        result = self.assert_branches(scenario(relic_ids=[COFFEE, PROBE], relic_context={'probe_stacks': 2}), 1.4)
        text = format_estimate(result)
        self.assertIn('猎犬咖啡出生生命分支', text)
        self.assertIn('未观测当前出生分支', text)
        self.assertNotIn('随机出生生命与其他生命藏品的组合尚未核验', text)


if __name__ == '__main__':
    unittest.main()
