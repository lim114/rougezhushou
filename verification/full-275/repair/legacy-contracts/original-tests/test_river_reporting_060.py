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
BASELINE = ROOT / '.cache/research/river-effects-060/integration-before.json'
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


class RiverReportingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        blob = BASELINE.read_bytes()
        if hashlib.sha256(blob).hexdigest() != '66e5babd5d88eeef681472958780822e6717617c1b403dbe1bdf75e1fc6e0326':
            raise AssertionError('Sealed pre-integration fixtures changed.')
        cls.fixtures = json.loads(blob)['cases']

    def test_complete_preintegration_results_preserved_except_documented_presentation_and_s1_timing(self):
        for name, fixture in self.fixtures.items():
            with self.subTest(name=name):
                current = public_json(calculate_damage(fixture['scenario']))
                before = deepcopy(fixture['result'])
                if RELIC_ID not in fixture['scenario'].get('relic_ids', []):
                    self.assertEqual(current, before)
                    continue
                if 'neural_relic_reference' in current:
                    current['neural_relic_reference'].pop('lifecycle_reference', None)
                old_warning = '河谷祭祈：未覆盖 ' + '、'.join(OLD_PENDING) + '。'
                new_warning = '河谷祭祈：未覆盖 ' + '、'.join(NEW_PENDING) + '。'
                for new_warnings, old_warnings in (
                    (current['warnings'], before['warnings']),
                    (current['estimate']['warnings'], before['estimate']['warnings']),
                    (current['relic_resolution']['warnings'], before['relic_resolution']['warnings'])):
                    self.assertEqual(len(new_warnings), len(old_warnings))
                    for index, old in enumerate(old_warnings):
                        if old == old_warning:
                            self.assertEqual(new_warnings[index], new_warning)
                            new_warnings[index] = old_warning
                        else:
                            self.assertEqual(new_warnings[index], old)
                self.assertEqual(len(current['relic_resolution']['records']), len(before['relic_resolution']['records']))
                for index, record in enumerate(current['relic_resolution']['records']):
                    self.assertEqual(record['id'], before['relic_resolution']['records'][index]['id'])
                    if record['id'] == RELIC_ID:
                        self.assertEqual(record['pending'], NEW_PENDING)
                        self.assertEqual(before['relic_resolution']['records'][index]['pending'], OLD_PENDING)
                        record['pending'] = OLD_PENDING
                blocks = current['report']['sections']
                self.assertEqual({block['id'] for block in blocks} & NEW_SECTIONS, NEW_SECTIONS)
                current['report']['sections'] = [block for block in blocks if block['id'] not in NEW_SECTIONS]
                old_neural = next((block for block in before['report']['sections'] if block['id'] == 'river_neural'), None)
                if old_neural:
                    new_neural = next(block for block in current['report']['sections'] if block['id'] == 'river_neural')
                    self.assertEqual(new_neural['notes'][0], old_neural['notes'][0])
                    self.assertIn('实际首跳时刻和每跳麻痹条件尚未确认', new_neural['notes'][1])
                    self.assertIn('四元素倍率、生命周期和条件逐跳规则', new_neural['notes'][2])
                    new_neural['notes'] = old_neural['notes']
                if name=='phantom_river':
                    # 0.70 replaces the historical unplaced S1/0.01s events
                    # and unproved cycle. Preserve the frozen original file;
                    # exclude only these documented dependent timing fields.
                    self.assertEqual(current['total_damage'],1590)
                    self.assertEqual(current['components'][0]['times_seconds'],[.5,.9])
                    self.assertEqual(current['estimate']['skill']['window_seconds'],1)
                    self.assertEqual(current['estimate']['skill']['window_dps'],1590)
                    self.assertNotIn('known_damage_subtotals',current)
                    self.assertEqual(before['known_damage_subtotals']['window_damage'],1590)
                    before.pop('known_damage_subtotals')
                    current['components'][0].pop('times_seconds')
                    for key in ('duration_seconds','recharge_seconds','cycle_seconds','phase_damage','phase_healing',
                                'cycle_damage','cycle_healing','cycle_dps','cycle_hps'):
                        self.assertIsNone(current['estimate']['skill'][key],key)
                        current['estimate']['skill'].pop(key);before['estimate']['skill'].pop(key)
                    for key in ('window_seconds','window_dps'):
                        current['estimate']['skill'].pop(key);before['estimate']['skill'].pop(key)
                    self.assertTrue(any('解除阻回尚未闭合' in n for n in current['estimate']['notes']))
                    current['estimate'].pop('notes');before['estimate'].pop('notes')
                    for key in ('streams','recharge_streams','notes','cycle_seconds','unplaced_components'):
                        current['timing'].pop(key);before['timing'].pop(key)
                    ref=current['neural_relic_reference']
                    self.assertEqual(ref['cast_burst_times'],[])
                    self.assertEqual(ref['window_burst_times'],[])
                    self.assertEqual(ref['cycle_burst_times'],[])
                    self.assertFalse(ref['periodic_damage_possible'])
                    self.assertEqual(ref['affected_damage_phases'],{'cast':False,'window':False,'cycle':False})
                    for key in ('cycle_burst_times','periodic_damage_possible','affected_damage_phases'):
                        ref.pop(key);before['neural_relic_reference'].pop(key)
                    changed={'timing','multi_melee','execution','damage','elemental','river_neural','known_damage_subtotals'}
                    for result in (current,before):
                        result['report']['sections']=[s for s in result['report']['sections'] if s['id'] not in changed]
                self.assertEqual(current, before)

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
        before = json.loads((ROOT / '.cache/batch-060-before' / path).read_bytes())['relics'][RELIC_ID]
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
