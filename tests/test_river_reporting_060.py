"""Held-relic presentation must preserve all existing calculation values."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.river_effects import RELIC_ID, reference


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'research/river-reporting-original-060/integration-before.json'
NEW_SECTIONS = {'river_dark', 'river_fire', 'river_sanity', 'river_water', 'river_limits'}
OLD_PENDING = [
    '凋亡增强及爆条期间减攻的局外参考待接入',
    '灼燃增强及爆条期间减法抗的局外参考待接入',
    '神经额外持续伤害的逐跳局外参考待接入',
    '侵蚀十次物理伤害与独立持续减防的局外参考待接入']
NEW_PENDING = [
    '凋亡额外减攻的实际生效和结束时刻，以及与其他减攻效果的组合尚未确认',
    '灼燃额外减法抗的实际生效和结束时刻，以及与其他法抗变化的组合尚未确认',
    '神经追加伤害的实际首跳和结束顺序、逐跳麻痹状态与目标减伤尚未确认',
    '侵蚀追加伤害的实际创建和触发时刻、目标减伤及当前热更新适用性尚未确认']


def public_json(value):
    return json.loads(json.dumps(value, ensure_ascii=False))


# Historical numeric leaf retirement is an exact selector set, not a broad
# exclusion of timing/reports/unknown output. Original070 and the public S1
# binding evidence withdraw these 49 old certainty claims; every other old
# numeric leaf remains conserved. MISSING means an intentionally removed
# old event/metric, distinct from an explicit unknown represented by None.
MISSING = object()
PHANTOM_RETIRED_NUMERIC = {
    '$.total_damage': (1590., None),
    '$.components[name=潜在神经损伤积累（不是生命伤害）].hits': (1, MISSING),
    '$.components[name=潜在神经损伤积累（不是生命伤害）].per_hit': (572.4, MISSING),
    '$.components[name=潜在神经损伤积累（不是生命伤害）].total': (572.4, MISSING),
    '$.components[name=神经损伤爆发].hits': (0, MISSING),
    '$.components[name=神经损伤爆发].per_hit': (12000., MISSING),
    '$.components[name=神经损伤爆发].total': (0., MISSING),
    '$.timing.recharge_streams[0].interval_frames': (48, MISSING),
    '$.timing.recharge_streams[0].interval_seconds': (1.6, MISSING),
    '$.timing.recharge_streams[0].start_frames[0]': (0, MISSING),
    '$.timing.recharge_streams[0].release_frames[0]': (48, MISSING),
    '$.timing.recharge_streams[0].impact_frames[0]': (48, MISSING),
    '$.timing.recharge_streams[0].times_seconds[0]': (1.6, MISSING),
    '$.timing.recharge_streams[0].emitted_impact_frames[0]': (48, MISSING),
    '$.timing.recharge_streams[0].emitted_times_seconds[0]': (1.6, MISSING),
    '$.timing.recharge_streams[0].emitted_release_frames[0]': (48, MISSING),
    '$.timing.recharge_streams[0].hit_release_frames[0]': (48, MISSING),
    '$.timing.recharge_streams[0].interval_frames_by_attack[0]': (48, MISSING),
    '$.timing.recharge_streams[0].resume_frame': (0, MISSING),
    '$.timing.cycle_seconds': (4.800000000000001, None),
    '$.estimate.skill.recharge_seconds': (3.2, None),
    '$.estimate.skill.cycle_seconds': (4.800000000000001, None),
    '$.estimate.skill.duration_seconds': (1.6, None),
    '$.estimate.skill.total_damage': (1590., None),
    '$.estimate.skill.phase_damage': (1590., None),
    '$.estimate.skill.phase_healing': (0, None),
    '$.estimate.skill.cycle_hps': (0., None),
    '$.estimate.skill.cycle_healing': (0, None),
    '$.estimate.skill.hit_counts.潜在神经损伤积累（不是生命伤害）': (1, MISSING),
    '$.estimate.skill.hit_counts.神经损伤爆发': (0, MISSING),
    '$.estimate.skill.window_seconds': (1.6, 1.),
    '$.estimate.skill.window_dps': (993.75, None),
    '$.neural_relic_reference.cycle_burst_times[0]': (3.2, MISSING),
    '$.known_damage_subtotals.phase_damage': (1590., None),
    '$.known_damage_subtotals.cycle_damage': (14120., None),
    '$.known_damage_subtotals.cycle_dps': (2941.666666666666, None),
    '$.known_damage_subtotals.window_dps': (993.75, 1590.),
    '$.report.sections[id=timing].metrics[key=duration].value': (1.6, None),
    '$.report.sections[id=timing].metrics[key=cycle].value': (4.800000000000001, None),
    '$.report.sections[id=timing].metrics[key=recharge].value': (3.2, None),
    '$.report.sections[id=damage].metrics[key=per_cast].value': (1590., None),
    '$.report.sections[id=damage].metrics[key=active_dps].value': (993.75, MISSING),
    '$.report.sections[id=damage].metrics[key=window_damage].value': (1590., None),
    '$.report.sections[id=damage].metrics[key=window_seconds].value': (1.6, 1.),
    '$.report.sections[id=damage].metrics[key=window_dps].value': (993.75, None),
    '$.report.sections[id=known_damage_subtotals].metrics[key=cycle].value': (14120., None),
    '$.report.sections[id=known_damage_subtotals].metrics[key=cycle_dps].value': (2941.666666666666, None),
    '$.report.sections[id=elemental].metrics[key=potential_buildup].value': (572.4, None),
    '$.report.sections[id=elemental].metrics[key=bursts].value': (0, None),
}


def identified_values(value, path='$'):
    """Read original leaves by explicit public identity, never by display order.

    Non-identity lists retain their exact indices. Container values are also
    recorded so None, an empty collection and a removed key remain distinct.
    """
    values = {path: value}
    if isinstance(value, dict):
        for key, child in value.items():
            values.update(identified_values(child, path + '.' + key))
    elif isinstance(value, list):
        identity = None
        if value and all(isinstance(child, dict) for child in value):
            for key in ('id', 'key', 'name'):
                if (all(isinstance(child.get(key), str) for child in value)
                        and len({child[key] for child in value}) == len(value)):
                    identity = key
                    break
        for index, child in enumerate(value):
            token = identity + '=' + child[identity] if identity else str(index)
            values.update(identified_values(child, path + '[' + token + ']'))
    return values


class RiverReportingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        blob = BASELINE.read_bytes()
        if hashlib.sha256(blob).hexdigest() != '66e5babd5d88eeef681472958780822e6717617c1b403dbe1bdf75e1fc6e0326':
            raise AssertionError('Sealed pre-integration fixtures changed.')
        cls.fixtures = json.loads(blob)['cases']

    def test_complete_preintegration_results_preserved_except_documented_presentation_and_s1_timing(self):
        # The sealed pre060 schema is historical, not a prohibition on later
        # source-qualified features. All ten original inputs still execute.
        # Full current results are paired across the exact five presentation
        # blocks; original numbers additionally retain their independent oracle.
        expected_case_names = {
            'mechanist_default', 'myrtle_default', 'mantra_default',
            'mantra_other_relic', 'mechanist_river', 'myrtle_river',
            'mantra_river', 'mantra_river_no_supply', 'phantom_river',
            'mantra_river_and_other',
        }
        self.assertEqual(set(self.fixtures), expected_case_names)
        conserved_non_phantom = 0
        for name, fixture in self.fixtures.items():
            with self.subTest(name=name):
                scenario = deepcopy(fixture['scenario'])
                original_input = deepcopy(scenario)
                with patch('rouge.river_effects.RiverInstance',
                           side_effect=AssertionError('presentation entered combat simulation')):
                    current = public_json(calculate_damage(scenario))
                    with patch('rouge.reporting.river_reference_sections', return_value=[]) as suppressed:
                        control = public_json(calculate_damage(deepcopy(original_input)))
                self.assertEqual(scenario, original_input)
                held = RELIC_ID in scenario.get('relic_ids', [])
                self.assertEqual(suppressed.call_count, int(held))
                additions = [block for block in current['report']['sections']
                             if block['id'] in NEW_SECTIONS]
                self.assertEqual({block['id'] for block in additions}, NEW_SECTIONS if held else set())
                self.assertEqual(len(additions), 5 if held else 0)
                self.assertFalse(any(block['id'] in NEW_SECTIONS
                                     for block in control['report']['sections']))
                without_five = deepcopy(current)
                without_five['report']['sections'] = [block for block in without_five['report']['sections']
                                                     if block['id'] not in NEW_SECTIONS]
                # No numeric, clock, unknown-state, warning, source, or other
                # report leaves are excluded from this whole-structure pair.
                self.assertEqual(without_five, control)

                # Preserve the original warning/pending presentation contract,
                # rather than trusting the paired renderer to generate it.
                old_warning = '河谷祭祈：未覆盖 ' + '、'.join(OLD_PENDING) + '。'
                new_warning = '河谷祭祈：未覆盖 ' + '、'.join(NEW_PENDING) + '。'
                before = fixture['result']
                for old_warnings, actual_warnings in (
                    (before['warnings'], current['warnings']),
                    (before['estimate']['warnings'], current['estimate']['warnings']),
                    (before['relic_resolution']['warnings'], current['relic_resolution']['warnings']),
                ):
                    self.assertEqual(actual_warnings, [new_warning if text == old_warning else text
                                                      for text in old_warnings])
                self.assertEqual(len(current['relic_resolution']['records']),
                                 len(before['relic_resolution']['records']))
                for old_record, record in zip(before['relic_resolution']['records'],
                                              current['relic_resolution']['records']):
                    self.assertEqual(record['id'], old_record['id'])
                    expected_pending = NEW_PENDING if record['id'] == RELIC_ID else old_record['pending']
                    self.assertEqual(record['pending'], expected_pending)

                before_values = identified_values(fixture['result'])
                current_values = identified_values(current)
                before_numbers = {path: value for path, value in before_values.items()
                                  if isinstance(value, (int, float)) and not isinstance(value, bool)}
                retired = PHANTOM_RETIRED_NUMERIC if name == 'phantom_river' else {}
                differences = {path for path, value in before_numbers.items()
                               if current_values.get(path, MISSING) != value}
                self.assertEqual(differences, set(retired), name)
                for path, value in before_numbers.items():
                    if path in retired:
                        old, required = retired[path]
                        self.assertEqual(value, old, path)
                        actual = current_values.get(path, MISSING)
                        if required is MISSING:
                            self.assertIs(actual, MISSING, path)
                        elif required is None:
                            self.assertIsNone(actual, path)
                            self.assertIn(path, current_values, path)
                        else:
                            self.assertIsInstance(actual, (int, float), path)
                            self.assertIsNot(type(actual), bool, path)
                            self.assertEqual(actual, required, path)
                    else:
                        self.assertIn(path, current_values, path)
                        self.assertIsInstance(current_values[path], (int, float), path)
                        self.assertIsNot(type(current_values[path]), bool, path)
                        self.assertEqual(current_values[path], value, path)
                if name != 'phantom_river':
                    conserved_non_phantom += len(before_numbers)
                    continue

                # Independent original-table parameters: attack530, scale1.5,
                # two arts hits, talent ratio.3; root1.8 applies conditionally.
                # Source: research/p2-s1-binding/source-receipt.json and the
                # original070 action proof. Known amounts do not prove clocks.
                self.assertEqual(len(before_numbers), 114)
                self.assertEqual(len(retired), 49)
                self.assertEqual(len(before_numbers) - len(retired), 65)
                self.assertFalse(current['complete'])
                self.assertFalse(current['estimate']['complete'])
                self.assertEqual(current['attack'], 530.)
                arts = next(c for c in current['components'] if c['name'] == '暗夜回声')
                self.assertEqual(arts['damage_type'], 'magic')
                self.assertEqual(arts['hits'], 2)
                self.assertEqual(arts['per_hit'], 530 * 1.5)
                self.assertEqual(arts['total'], 530 * 1.5 * 2)
                self.assertEqual(arts['times_seconds'], [.5, .9])
                self.assertIsNone(current['total_damage'])
                self.assertIsNone(current['estimate']['skill']['total_damage'])
                self.assertIsNone(current['estimate']['skill']['window_damage'])
                self.assertEqual(current['estimate']['skill']['window_seconds'], original_input['window_seconds'])
                self.assertEqual(current['known_damage_subtotals'], {
                    'total_damage': 1590., 'phase_damage': None, 'window_damage': 1590.,
                    'cycle_damage': None, 'cycle_dps': None, 'window_dps': 1590.,
                })
                basic = next(c for c in current['components']
                             if c['name'] == '未计束缚倍率的损伤基础参考（不是生命伤害）')
                self.assertEqual(basic['damage_type'], 'buildup')
                self.assertEqual(basic['per_hit'], 530 * .3 * 2)
                self.assertEqual(basic['total'], 530 * .3 * 2)
                self.assertFalse(basic['binding_multiplier_applied'])
                self.assertIsNone(basic['actual_total'])
                self.assertFalse(any(c['name'] in ('神经损伤爆发', '潜在神经损伤积累（不是生命伤害）')
                                     for c in current['components']))
                s1 = current['neural_s1_reference']
                self.assertEqual(s1['direct_buildup_ratio'], .3)
                self.assertEqual(s1['direct_buildup_raw'], 530 * .3)
                self.assertEqual(s1['binding_multiplier'], 1.8)
                self.assertEqual(s1['binding_duration_seconds'], 3.)
                self.assertFalse(s1['first_attachment_verified'])
                self.assertFalse(s1['refresh_order_verified'])
                self.assertFalse(s1['binding_multiplier_applied'])
                self.assertEqual(s1['qualified_hit_times'], {'cast': [.5, .9], 'window': [.5, .9]})
                self.assertEqual(s1['affected_damage_phases'], {'cast': True, 'window': True, 'cycle': False})
                river = current['neural_relic_reference']
                self.assertFalse(river['periodic_damage_scheduled'])
                self.assertTrue(river['periodic_damage_possible'])
                self.assertIsNone(river['cast_burst_times'])
                self.assertIsNone(river['window_burst_times'])
                self.assertEqual(river['cycle_burst_times'], [])
                self.assertEqual(river['burst_schedule_status'], 'unknown_due_to_s1_binding')
                self.assertEqual(river['affected_damage_phases'], {'cast': True, 'window': True, 'cycle': False})
                self.assertEqual(current['timing']['recharge_streams'], [])
                self.assertTrue(any('解除阻回尚未闭合' in note for note in current['estimate']['notes']))
        self.assertEqual(conserved_non_phantom, 2517)


    def test_held_river_shows_four_branches_on_non_neural_operators(self):
        for name in ('mechanist_river', 'myrtle_river'):
            with self.subTest(name=name):
                result = calculate_damage(self.fixtures[name]['scenario'])
                self.assertNotIn('neural_relic_reference', result)
                text = format_estimate(result)
                for element in ('凋亡', '灼燃', '神经', '侵蚀'):
                    self.assertIn('河谷祭祈 · ' + element + '机制资料', text)
                self.assertNotIn('河谷祭祈 · 神经爆发参考', text)
                self.assertNotIn('已建模伤害小计', text)

    def test_unheld_relic_has_no_reference_sections(self):
        for name in ('mechanist_default', 'myrtle_default', 'mantra_default', 'mantra_other_relic'):
            with self.subTest(name=name):
                result = calculate_damage(self.fixtures[name]['scenario'])
                self.assertFalse({block['id'] for block in result['report']['sections']} & NEW_SECTIONS)
                self.assertNotIn('河谷祭祈', format_estimate(result))

    def test_lifecycle_metadata_attached_only_to_existing_river_reference(self):
        fixture = self.fixtures['mantra_river_no_supply']
        result = calculate_damage(fixture['scenario'])
        self.assertEqual(result['neural_relic_reference']['lifecycle_reference'], reference())
        self.assertFalse(result['neural_relic_reference']['periodic_damage_possible'])
        self.assertEqual(result['total_damage'], 0)
        self.assertNotIn('lifecycle_reference', result)
        result['neural_relic_reference']['lifecycle_reference']['branches']['water']['raw_pulse_damage'] = 99
        fresh = calculate_damage(fixture['scenario'])
        self.assertEqual(fresh['neural_relic_reference']['lifecycle_reference']['branches']['water']['raw_pulse_damage'], 1500)

    def test_chinese_metrics_match_contract_and_keep_uncertain_total_unknown(self):
        result = calculate_damage(self.fixtures['mantra_river']['scenario'])
        blocks = {block['id']: block for block in result['report']['sections']}
        values = {key: {row['key']: row['value'] for row in blocks[key]['metrics']}
                  for key in NEW_SECTIONS}
        self.assertEqual(values['river_dark'], {'burst_factor': 2.5, 'enemy_attack_factor': .7})
        self.assertEqual(values['river_fire'], {'burst_factor': 3.8, 'enemy_mr_addition': -20})
        self.assertEqual(values['river_sanity'], {'burst_factor': 2., 'pulse_raw': 1000., 'period': 1., 'first_wait': 1.})
        self.assertEqual(values['river_water'], {'burst_factor': 1., 'pulse_raw': 1500., 'period': .03, 'maximum_pulses': 10, 'enemy_def_addition': -120})
        self.assertIsNone(result['total_damage'])
        self.assertIsNone(result['estimate']['skill']['cycle_dps'])
        self.assertFalse(result['neural_relic_reference']['periodic_damage_scheduled'])
        text = format_estimate(result)
        self.assertIn('实际首跳时刻和每跳麻痹条件尚未确认', text)
        self.assertIn('十次伤害结束后防御减算继续', text)
        self.assertIn('每次目标更新最多执行一次，不追赶补跳', text)
        self.assertIn('实际追加跳数与完整总伤仍未知', text)
        self.assertNotIn('凋亡、灼燃和侵蚀路径仍待接入', text)

    def test_river_record_preserves_mechanics_except_four_pending_strings(self):
        path = Path('rouge/data/relic-mechanics.json')
        # Other relics may receive independently verified fixes in later batches.
        before_blob = (ROOT / 'research/river-reporting-original-060/relic-mechanics-before.json').read_bytes()
        # This is the recovered original data, not a generated current fixture.
        archive = json.loads((ROOT / 'verification/full-275/repair/legacy-contracts/original-inputs-restored.json').read_bytes())
        expected = next(r['sha256'] for r in archive['exact_original_public_inputs']
                        if r['archive'].endswith('/relic-mechanics-before.json'))
        self.assertEqual(hashlib.sha256(before_blob).hexdigest(), expected)
        before = json.loads(before_blob)['relics'][RELIC_ID]
        current = json.loads((ROOT / path).read_bytes())['relics'][RELIC_ID]
        self.assertEqual(before['pending'], OLD_PENDING)
        self.assertEqual(current['pending'], NEW_PENDING)
        self.assertEqual(current['status'], 'partial')
        current['pending'] = OLD_PENDING
        self.assertEqual(current, before)

    def test_player_reference_sections_avoid_implementation_jargon(self):
        result = calculate_damage(self.fixtures['mechanist_river']['scenario'])
        blocks = [block for block in result['report']['sections'] if block['id'] in NEW_SECTIONS]
        text = '\n'.join(block['title'] + '\n' + '\n'.join(block['notes']) for block in blocks)
        for term in ('有理时间', '原生定点时钟', '六个完整模板', '同键', '属性组', '派生', 'Q32', 'palsy'):
            with self.subTest(term=term):
                self.assertNotIn(term, text)
        self.assertIn('没有默认目标处于麻痹', text)
        self.assertIn('不另加冷却加速', text)
        self.assertIn('热更新版本是否改变', text)

    def test_simulator_is_not_invoked_and_input_is_not_mutated(self):
        scenario = deepcopy(self.fixtures['mantra_river_and_other']['scenario'])
        before = deepcopy(scenario)
        with patch('rouge.river_effects.RiverInstance', side_effect=AssertionError('simulation entered calculation')):
            result = calculate_damage(scenario)
        self.assertEqual(scenario, before)
        self.assertEqual(result['known_damage_subtotals']['window_damage'], 18876.25)
        self.assertFalse(result['neural_relic_reference']['periodic_damage_scheduled'])


if __name__ == '__main__':
    unittest.main()
