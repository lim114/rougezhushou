import copy
import unittest
from unittest.mock import patch
from rouge import current_sun_boss as model


class CurrentSunBoss368Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = model.packet(); assert cls.source is not None, 'Install the candidate before execution.'
        cls.refs = {sid: model.reference(sid) for sid in model.STAGES}; assert all(cls.refs.values())

    def test_two_exact_stages_six_form_references_and_one_declared_combat_actor_each(self):
        self.assertEqual(tuple(self.source['data']['bindings']), model.STAGES)
        self.assertEqual(sum(len(r['rows']) for r in self.source['data']['bindings'].values()), 6)
        for result in self.refs.values():
            self.assertEqual({r['form'] for r in result['rows']}, {'normal', 'sun', 'eclipse'})
            self.assertEqual(len(result['declared_appearances']), 1)
            self.assertEqual(result['declared_appearances'][0]['raw']['key'], 'enemy_2157_shadvr')
            self.assertIsNone(result['actual_form']); self.assertIsNone(result['actual_phase'])
            self.assertFalse(result['numeric_model_added'])

    def test_fifteen_complete_cards_and_three_full_named_form_panels(self):
        forms = self.source['materials']['forms']
        self.assertEqual({k: len(v['cards']) for k, v in forms.items()}, {'normal': 3, 'sun': 6, 'eclipse': 6})
        for form in forms.values():
            self.assertIn(form['name'], form['document_panel']['panel_id'])
            self.assertTrue(form['document_panel']['complete_DOM'].endswith('</div>'))
            for card in form['cards']:
                self.assertTrue(card['complete_DOM'].startswith('<div'))
                self.assertTrue(card['complete_DOM'].endswith('</div>'))
                self.assertIn(card['complete_DOM'], form['document_panel']['complete_DOM'])
        self.assertIn('实战不会出现', forms['normal']['cards'][-1]['body'])

    def test_mode_time_headers_are_preserved_without_guessed_mode_assignment(self):
        forms = self.source['materials']['forms']
        self.assertEqual(forms['sun']['cards'][3]['cost_header_raw'], ['6/8', '12/10', '/'])
        self.assertEqual(forms['eclipse']['cards'][3]['cost_header_raw'], ['3/5', '10/10', '/'])
        result = self.refs['ro6_b_7']; sun = next(r for r in result['rows'] if r['form'] == 'sun')
        text = model.player_text(result, sun['key'], 'skills', 3)
        self.assertIn('不猜对应关系', text)
        self.assertIsNone(result['actual_skill_time'])

    def test_game_skill_name_and_document_title_difference_are_visible(self):
        result = self.refs['ro6_b_7']; row = next(r for r in result['rows'] if r['form'] == 'eclipse')
        self.assertTrue(any('熄日的祭仪' in s for s in row['enemy']['abilities']))
        self.assertEqual(model.card(result, row['key'], 3)['title'], '熄日的祭坛')
        text = model.player_text(result, row['key'], 'skills', 3)
        self.assertIn('熄日的祭仪', text); self.assertIn('熄日的祭坛', text)
        self.assertIn('不擅自改名', text)

    def test_faith_and_second_phase_conditions_do_not_create_actual_progress_or_terrain(self):
        result = self.refs['ro6_b_7']; normal = next(r for r in result['rows'] if r['form'] == 'normal')
        faith = model.player_text(result, normal['key'], 'faith')
        self.assertIn('生命值发生实际降低', faith)
        self.assertIn('最多叠加2层', faith); self.assertIn('持续40秒', faith)
        phase = model.player_text(result, normal['key'], 'terrain')
        self.assertIn('停止积累信仰', phase); self.assertIn('祭台所在地块', phase)
        self.assertIn('不能给出唯一剩余地形', phase)
        self.assertIsNone(result['actual_terrain']); self.assertIsNone(result['actual_faith'])

    def test_altar_document_has_no_fabricated_predefined_object_or_position(self):
        result = self.refs['ro6_b_7']; row = result['rows'][0]
        text = model.player_text(result, row['key'], 'altar')
        self.assertIn('会被沉沦之人攻击', text); self.assertIn('没有祭台预置原项', text)
        self.assertIsNone(result['data']['altar_original_stage_binding'])
        self.assertEqual(result['data']['missing_linked_ids'], ['enemy_2160_shadve', 'enemy_2161_shadvj'])
        self.assertIsNone(result['actual_altar_cells'])

    def test_exact_related_form_requests_and_stale_snapshots(self):
        result = self.refs['ro6_b_7']; key = result['rows'][0]['key']; request = model.related_forms(result, key)[0]
        self.assertEqual(len(model.related_forms(result, key)), 2)
        with patch.object(model, 'reference', return_value=copy.deepcopy(result)):
            found = model.resolve_form(result, key, request)
            self.assertEqual(found['enemy_key'], request['key']); self.assertIsNone(found['actual_form'])
            self.assertIsNone(model.resolve_form(result, key, request | {'entity_id': 'enemy_2160_shadve'}))
            changed = copy.deepcopy(result); changed['stage_id'] = 'ro6_b_7_b'
            self.assertIsNone(model.resolve_form(changed, key, request))

    def test_strict_stage_reference_and_card_identity_guards(self):
        for args in (('same_name', None), ('ro6_b_7', True), ('ro6_b_7', '1'), (False, None)):
            self.assertIsNone(model.reference(*args))
        result = self.refs['ro6_b_7']; key = result['rows'][0]['key']
        self.assertIsNone(model.card(result, key, True)); self.assertIsNone(model.card(result, key, 99))
        self.assertEqual(model.cards(result, '999'), [])

    def test_fixed_map_link_rechecks_complete_geometry_without_second_phase_projection(self):
        from rouge import current_map_position as maps
        result = self.refs['ro6_b_7']; geometry = result['data']['originals']['levels'][result['level_key']]
        fixed = {'stage_id': 'ro6_b_7', 'current_level_key': result['level_key'], 'source_identity': 'test_map',
                 'complete_current_geometry': {'mapData': copy.deepcopy(geometry['mapData'])}}
        with patch.object(model, 'reference', return_value=copy.deepcopy(result)):
            with patch.object(maps, 'stage_reference', return_value=fixed):
                resolved = model.map_reference(result)
                self.assertEqual(resolved['stage_id'], 'ro6_b_7'); self.assertIsNone(resolved['actual_second_phase_terrain'])
                self.assertIsNone(resolved['actual_altar_cells'])
            changed = copy.deepcopy(fixed); changed['complete_current_geometry']['mapData']['map'][0][0] = 99
            with patch.object(maps, 'stage_reference', return_value=changed): self.assertIsNone(model.map_reference(result))
            with patch.object(maps, 'stage_reference', return_value=fixed | {'stage_id': 'ro6_b_7_b'}): self.assertIsNone(model.map_reference(result))
            with patch.object(maps, 'stage_reference', return_value=None): self.assertIsNone(model.map_reference(result))

    def test_current_database_and_stage_change_invalidate_reading(self):
        base = model.battle.packet(); changed = copy.deepcopy(base)
        changed['inputs']['enemy_definitions']['enemy_2157_shadvr'][0]['enemyData']['talentBlackboard'][0]['value'] += 1
        with patch.object(model.battle, 'packet', return_value=changed): self.assertIsNone(model.packet())
        changed = copy.deepcopy(base); changed['version']['current']['details']['stages']['ro6_b_7_b']['name'] = 'other'
        with patch.object(model.battle, 'packet', return_value=changed): self.assertIsNone(model.packet())

    def test_bad_manifest_clears_source(self):
        read = model.battle.version._file
        class Damaged:
            def read_bytes(self): return b'{}'
        with patch.object(model.battle.version, '_file', side_effect=lambda name: Damaged() if name == model.MANIFEST else read(name)):
            self.assertIsNone(model.packet())


if __name__ == '__main__': unittest.main()
