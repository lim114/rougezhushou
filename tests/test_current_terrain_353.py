"""One-tile source decoding, including every current original declaration."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest

from rouge.current_terrain import KNOWN_TILE_KEYS, terrain_info


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'research/p3-current-battle-314/source-inputs.json'


def tile(key, **parameters):
    return {'tileKey': key, 'blackboard': [
        {'key': k, 'value': v, 'valueStr': None} for k, v in parameters.items()]}


class CurrentTerrain353Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.originals = json.loads(INPUT.read_text(encoding='utf8'))

    def test_all_113_current_original_levels_and_all_10317_tile_declarations(self):
        levels = self.originals['levels']
        self.assertEqual(len(levels), 113)
        observed = set()
        count = 0
        for source, level in levels.items():
            for index, declaration in enumerate(level['mapData']['tiles']):
                with self.subTest(source=source, declaration=index):
                    before = deepcopy(declaration)
                    info = terrain_info(declaration)
                    self.assertEqual(declaration, before)
                    self.assertEqual(set(info), {'name', 'short_label', 'color', 'kind',
                                                'effects', 'unknowns', 'source_refs'})
                    self.assertRegex(info['color'], r'^#[0-9a-f]{6}$')
                    self.assertTrue(info['name'] and info['short_label'] and info['kind'])
                    self.assertTrue(info['source_refs'])
                    for field in ('effects', 'unknowns', 'source_refs'):
                        self.assertTrue(all(type(x) is str for x in info[field]))
                    observed.add(declaration['tileKey'])
                    count += 1
        self.assertEqual(count, 10317)
        self.assertEqual(observed, set(KNOWN_TILE_KEYS))
        self.assertEqual(len(observed), 19)

    def test_direct_evidence_bytes_and_actual_current_source_bound_in_notes(self):
        notes = json.loads((ROOT / 'research/p3-current-terrain-353/source-notes.json').read_text(encoding='utf8'))
        self.assertEqual(notes['game_commit'], 'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d')
        for name, pin in notes['public_file_pins'].items():
            raw = (ROOT / name).read_bytes()
            self.assertEqual(len(raw), pin['bytes'], name)
            self.assertEqual(sha256(raw).hexdigest(), pin['sha256'], name)
        self.assertEqual(notes['current_tile_keys'], list(KNOWN_TILE_KEYS))
        self.assertFalse(notes['origin_template_html_usable'])
        self.assertIsNone(notes['template_search_excerpt_revision'])
        self.assertIn('tile_pollution_roadf', notes['unresolved_exact_tile_keys'])

    def test_actual_spirit_rest_originals_read_all_three_independent_tile_effects(self):
        for name in ('level_rogue6_5-8.json', 'level_rogue6_5-8_dlc1.json'):
            level = next(value for key, value in self.originals['levels'].items() if key.endswith('/' + name))
            selected = {row['tileKey']: row for row in level['mapData']['tiles']
                        if row['tileKey'] in ('tile_healing', 'tile_bigforce', 'tile_infection')}
            self.assertEqual(set(selected), {'tile_healing', 'tile_bigforce', 'tile_infection'})
            with self.subTest(original=name):
                healing = '\n'.join(terrain_info(selected['tile_healing'])['effects'])
                infection = '\n'.join(terrain_info(selected['tile_infection'])['effects'])
                force = '\n'.join(terrain_info(selected['tile_bigforce'])['effects'])
                self.assertIn('最大生命值的3%', healing)
                for phrase in ('300秒', '100点真实伤害', '攻击力：增加50%',
                               '攻击速度：增加50（游戏攻速单位）'):
                    self.assertIn(phrase, infection)
                self.assertIn('力度：增加1个等级', force)

    def test_actual_volcano_variants_keep_their_distinct_values(self):
        expected = {
            'level_rogue6_3-5_dlc1.json': ('3000点', '5至10秒'),
            'level_rogue6_c-8.json': ('800点', '5至7秒'),
            'level_rogue6_d-1.json': ('2000点', '4至8秒'),
        }
        for name, phrases in expected.items():
            level = next(value for key, value in self.originals['levels'].items() if key.endswith('/' + name))
            selected = next(row for row in level['mapData']['tiles'] if row['tileKey'] == 'tile_volcano')
            text = '\n'.join(terrain_info(selected)['effects'])
            for phrase in phrases:
                self.assertIn(phrase, text)

    def test_supplied_values_not_stage_lookups_or_common_defaults(self):
        self.assertIn('最大生命值的1.25%', '\n'.join(terrain_info(tile(
            'tile_healing', HP_RECOVERY_PER_SEC_BY_MAX_HP_RATIO=0.0125))['effects']))
        info = terrain_info(tile('tile_infection', damage=23.5, duration=42.25,
                                 atk=0.175, attack_speed=7.5))
        text = '\n'.join(info['effects'])
        for expected in ('23.5点真实伤害', '42.25秒', '17.5%', '7.5（游戏攻速单位）'):
            self.assertIn(expected, text)
        self.assertNotIn('100点', text)
        self.assertIn('增加4个等级', '\n'.join(terrain_info(tile('tile_bigforce', base_force_level=4))['effects']))

    def test_absent_parameter_does_not_borrow_other_tiles_defaults(self):
        for key in ('tile_healing', 'tile_infection', 'tile_bigforce', 'tile_volcano'):
            info = terrain_info({'tileKey': key, 'blackboard': None})
            self.assertTrue(any('不套用常见默认值' in x for x in info['unknowns']))
            self.assertNotRegex('\n'.join(info['effects']), r'\d')
        # A previously decoded tile cannot populate a later missing value.
        terrain_info(tile('tile_healing', HP_RECOVERY_PER_SEC_BY_MAX_HP_RATIO=0.03))
        self.assertNotIn('3%', '\n'.join(terrain_info({'tileKey': 'tile_healing'})['effects']))

    def test_boolean_string_null_nonfinite_or_string_side_value_are_unknown(self):
        for invalid in (True, False, '0.03', None, float('nan'), float('inf'), -float('inf')):
            with self.subTest(value=repr(invalid)):
                info = terrain_info(tile('tile_healing', HP_RECOVERY_PER_SEC_BY_MAX_HP_RATIO=invalid))
                self.assertNotIn('每秒回复：', '\n'.join(info['effects']))
                self.assertTrue(info['unknowns'])
        declaration = tile('tile_healing', HP_RECOVERY_PER_SEC_BY_MAX_HP_RATIO=0.03)
        declaration['blackboard'][0]['valueStr'] = 'other-meaning'
        self.assertNotIn('每秒回复：', '\n'.join(terrain_info(declaration)['effects']))

    def test_duplicate_parameter_even_same_value_does_not_choose_a_winner(self):
        for second in (0.03, 0.8, True):
            declaration = tile('tile_healing', HP_RECOVERY_PER_SEC_BY_MAX_HP_RATIO=0.03)
            declaration['blackboard'].append({'key': 'HP_RECOVERY_PER_SEC_BY_MAX_HP_RATIO', 'value': second})
            info = terrain_info(declaration)
            self.assertNotIn('每秒回复：', '\n'.join(info['effects']))
            self.assertIn('重复', '\n'.join(info['unknowns']))

    def test_malformed_and_unrelated_parameters_are_not_applied(self):
        for raw in ('0.03', {}, 1, True, ('ratio', 0.03)):
            info = terrain_info({'tileKey': 'tile_healing', 'blackboard': raw})
            self.assertNotIn('每秒回复：', '\n'.join(info['effects']))
            self.assertIn('格式异常', '\n'.join(info['unknowns']))
        declaration = tile('tile_healing', HP_RECOVERY_PER_SEC_BY_MAX_HP_RATIO=0.03)
        declaration['blackboard'] += [None, {'value': 5}, {'key': 'damage', 'value': 999}]
        info = terrain_info(declaration)
        self.assertIn('3%', '\n'.join(info['effects']))
        self.assertNotIn('999', '\n'.join(info['effects']))
        self.assertIn('未解释', '\n'.join(info['unknowns']))

    def test_negative_life_damage_and_duration_not_reinterpreted_as_other_effects(self):
        cases = [('tile_healing', {'HP_RECOVERY_PER_SEC_BY_MAX_HP_RATIO': -0.03}, '每秒回复：'),
                 ('tile_infection', {'damage': -100, 'duration': -5}, '每秒受到：'),
                 ('tile_volcano', {'damage': -2000, 'cd_min': -2, 'cd_max': -1}, '每次喷发伤害：')]
        for key, parameters, prohibited in cases:
            info = terrain_info(tile(key, **parameters))
            self.assertNotIn(prohibited, '\n'.join(info['effects']))
            self.assertTrue(info['unknowns'])

    def test_signed_attack_and_speed_are_readable_and_zero_is_explicit(self):
        info = terrain_info(tile('tile_infection', damage=0, duration=0, atk=-0.2, attack_speed=-5))
        text = '\n'.join(info['effects'])
        for phrase in ('0点真实伤害', '0秒', '攻击力：减少20%', '攻击速度：减少5'):
            self.assertIn(phrase, text)
        self.assertIn('最大生命值的0%', '\n'.join(terrain_info(tile(
            'tile_healing', HP_RECOVERY_PER_SEC_BY_MAX_HP_RATIO=0))['effects']))

    def test_noninteger_force_and_inverted_interval_do_not_become_valid_effects(self):
        force = terrain_info(tile('tile_bigforce', base_force_level=1.5))
        self.assertNotIn('力度：增加', '\n'.join(force['effects']))
        self.assertIn('不是整数', '\n'.join(force['unknowns']))
        hot = terrain_info(tile('tile_volcano', damage=88, cd_min=10, cd_max=5))
        self.assertIn('88点', '\n'.join(hot['effects']))
        self.assertNotIn('配置的喷发间隔：', '\n'.join(hot['effects']))
        self.assertIn('上下限倒置', '\n'.join(hot['unknowns']))
        same = terrain_info(tile('tile_volcano', damage=88, cd_min=5, cd_max=5))
        self.assertIn('喷发间隔：5秒', '\n'.join(same['effects']))

    def test_special_names_and_documented_name_difference(self):
        for key, name in {'tile_floor': '不可放置位', 'tile_flystart': '空袭侵入点',
                          'tile_ftstart': '假侵入点', 'tile_telin': '通道入口',
                          'tile_telout': '通道出口', 'tile_fence_bound': '围墙'}.items():
            self.assertEqual(terrain_info({'tileKey': key})['name'], name)
        self.assertIn('BWIKI总表称围栏', '\n'.join(terrain_info({'tileKey': 'tile_fence_bound'})['unknowns']))

    def test_passage_ids_and_grass_do_not_prove_pairing_or_immunity(self):
        for key in ('tile_telin', 'tile_telout'):
            info = terrain_info(tile(key, avalanche_index=1, avalanche_state=2))
            self.assertIn('不按编号或距离自行连线', '\n'.join(info['unknowns']))
            self.assertNotRegex('\n'.join(info['effects']), r'\d')
        self.assertIn('不等于免疫', '\n'.join(terrain_info({'tileKey': 'tile_grass'})['effects']))

    def test_unknown_exact_suffix_and_unknown_input_do_not_match_similar_keys(self):
        exact = terrain_info({'tileKey': 'tile_pollution_roadf'})
        self.assertEqual(exact['kind'], 'unknown')
        self.assertFalse(exact['effects'])
        self.assertIn('不能仅凭名称片段', '\n'.join(exact['unknowns']))
        for value in (None, [], True, 3, 'tile_healing', {}, {'tileKey': []},
                      {'tileKey': 'tile_healing_extra'}, {'tileKey': 'TILE_HEALING'}):
            info = terrain_info(value)
            self.assertEqual(info['kind'], 'unknown')
            self.assertFalse(info['effects'])
            self.assertTrue(info['unknowns'])

    def test_opaque_effects_and_returned_lists_cannot_modify_other_calls(self):
        original = tile('tile_healing', HP_RECOVERY_PER_SEC_BY_MAX_HP_RATIO=0.03)
        original['effects'] = [{'key': 'uninterpreted'}]
        a = terrain_info(original)
        self.assertIn('附加效果声明', '\n'.join(a['unknowns']))
        a['effects'].clear()
        a['source_refs'].append('injected')
        b = terrain_info(original)
        self.assertIn('3%', '\n'.join(b['effects']))
        self.assertNotIn('injected', b['source_refs'])


if __name__ == '__main__':
    unittest.main()
