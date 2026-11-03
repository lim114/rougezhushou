from copy import deepcopy
from unittest.mock import patch
import unittest
from rouge import current_action_positions as model


class CurrentActionPositions320Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = model.battle.packet(); cls.map_packet = model.positions.packet()

    def data(self, sid='ro6_n_1_1'):
        with patch.object(model.battle, 'packet', return_value=self.packet), patch.object(model.positions, 'packet', return_value=self.map_packet):
            return model.battle.stage_reference(sid), model.positions.stage_reference(sid)

    def test_all184_current_actions_follow_exact_source_binding_and_cell_transform(self):
        stages = self.packet['version']['current']['details']['stages']; checked = 0; kinds = set()
        self.assertEqual(len(stages), 184)
        for sid in stages:
            current, grid = self.data(sid)
            for action in current['actions']:
                result = model._reference(current, grid, action['key']); checked += 1
                self.assertEqual(result['action'], action); self.assertFalse(result['run_updated']); self.assertIsNone(result['actual_path'])
                self.assertIsNone(result['absolute_time']); self.assertIsNone(result['actual_occurrence'])
                raw = action['raw']; kind = raw['actionType']; kinds.add(kind)
                if kind == 'SPAWN' and action['queue']['kind'] == 'main':
                    index = raw['routeIndex']; route = current['level']['routes'][index]
                    if route['motionMode'] in ('WALK', 'FLY'):
                        expected = [route['startPosition']] + [c['position'] for c in route['checkpoints'] or [] if c['type'] in ('MOVE', 'APPEAR_AT_POS')] + [route['endPosition']]
                        self.assertEqual([e['raw_position'] for e in result['entries']], expected)
                    else: self.assertEqual(result['entries'], [])
                elif kind == 'ACTIVATE_PREDEFINED' and raw['key'] and len(action['predefined_candidates']) == 1:
                    self.assertEqual(result['entries'][0]['raw_position'], action['predefined_candidates'][0]['raw']['position'])
                else: self.assertEqual(result['entries'], [])
                for entry in result['entries']:
                    position = entry['raw_position']; row = position['row']; col = position['col']
                    if type(row) is int and type(col) is int and 0 <= row < grid['rows'] and 0 <= col < grid['cols']:
                        self.assertEqual(entry['cell'], {'row': grid['rows'] - 1 - row, 'col': col})
                    else: self.assertIsNone(entry['cell'])
                    if entry['center']:
                        self.assertIn(entry['center'], grid['points']); self.assertEqual(entry['center']['row'], entry['cell']['row']); self.assertEqual(entry['center']['col'], entry['cell']['col'])
                    self.assertIsNone(entry['actual_position']); self.assertIsNone(entry['actual_time'])
        self.assertGreater(checked, 5000); self.assertIn('SPAWN', kinds); self.assertIn('ACTIVATE_PREDEFINED', kinds)

    def test_branch_never_selects_base_or_extra_route_by_equal_index(self):
        c, g = self.data(); action = next(a for a in c['actions'] if a['queue']['kind'] == 'branch' and a['raw']['actionType'] == 'SPAWN')
        self.assertTrue(c['level']['routes']); self.assertTrue(c['level']['extraRoutes'])
        r = model._reference(c, g, action['key']); self.assertEqual(r['entries'], []); self.assertIn('实际选择尚未确认', ''.join(r['notes']))

    def test_wait_and_disappear_placeholders_never_become_cells(self):
        c, g = self.data('ro6_n_1_3'); action = next(a for a in c['actions'] if a['raw']['actionType'] == 'SPAWN' and a['queue']['kind'] == 'main')
        route = c['level']['routes'][action['raw']['routeIndex']]; route['motionMode'] = 'WALK'
        route['checkpoints'] = [{'type': kind, 'position': {'row': 0, 'col': 0}, 'time': 3.5} for kind in ('WAIT_FOR_SECONDS', 'DISAPPEAR', 'WAIT_CURRENT_FRAGMENT_TIME', 'NEW_UNKNOWN')]
        r = model._reference(c, g, action['key']); self.assertEqual(len(r['entries']), 2); self.assertEqual(len(r['notes']), 4)
        self.assertIn('3.5秒', ''.join(r['notes'])); self.assertIn('类型尚未核实', ''.join(r['notes']))

    def test_route_index_bool_negative_float_missing_and_undefined_motion_are_unknown(self):
        c, g = self.data(); action = next(a for a in c['actions'] if a['raw']['actionType'] == 'SPAWN' and a['queue']['kind'] == 'main')
        for value in (None, True, -1, 1.0, len(c['level']['routes'])):
            action['raw']['routeIndex'] = value; r = model._reference(c, g, action['key']); self.assertEqual(r['entries'], [])
        action['raw']['routeIndex'] = 0; c['level']['routes'][0]['motionMode'] = 'E_NUM'
        self.assertEqual(model._reference(c, g, action['key'])['entries'], [])

    def test_outside_noninteger_and_edge_cells_are_not_clipped(self):
        c, g = self.data(); action = next(a for a in c['actions'] if a['raw']['actionType'] == 'SPAWN' and a['queue']['kind'] == 'main')
        route = c['level']['routes'][action['raw']['routeIndex']]; route['motionMode'] = 'WALK'; route['checkpoints'] = None
        for position in ({'row': -1, 'col': 0}, {'row': g['rows'], 'col': 0}, {'row': 0, 'col': g['cols']}, {'row': True, 'col': 0}, {'row': 0.0, 'col': 0}):
            route['startPosition'] = position; e = model._reference(c, g, action['key'])['entries'][0]; self.assertIsNone(e['cell']); self.assertIsNone(e['center'])
        route['startPosition'] = {'row': 0, 'col': 0}; self.assertEqual(model._reference(c, g, action['key'])['entries'][0]['cell'], {'row': g['rows'] - 1, 'col': 0})

    def test_empty_and_ambiguous_aliases_do_not_choose_one_or_use_route_index(self):
        c, g = self.data(); action = next(a for a in c['actions'] if a['raw']['actionType'] == 'ACTIVATE_PREDEFINED' and a['predefined_candidates'])
        self.assertEqual(len(model._reference(c, g, action['key'])['entries']), 1)
        action['predefined_candidates'] *= 2; self.assertEqual(model._reference(c, g, action['key'])['entries'], [])
        action['raw']['key'] = ''; self.assertEqual(model._reference(c, g, action['key'])['entries'], [])

    def test_offsets_and_random_ranges_are_retained_not_projected(self):
        c, g = self.data('ro6_b_6'); action = c['actions'][0]; route = c['level']['routes'][action['raw']['routeIndex']]
        route['spawnOffset'] = {'x': 0.7, 'y': -0.2}; route['spawnRandomRange'] = {'x': 3, 'y': 2}
        r = model._reference(c, g, action['key']); e = r['entries'][0]; self.assertEqual(e['offset'], route['spawnOffset']); self.assertEqual(e['random_range'], route['spawnRandomRange']); self.assertIn('不表示偏移后', model.player_text(r, e)); self.assertIsNone(e['actual_position'])

    def test_no_base_fallback_and_invalid_identity(self):
        self.assertIsNone(model.reference('not-a-stage', '0')); self.assertIsNone(model.reference('ro6_n_1_1', True))
        with patch.object(model.positions, 'stage_reference', return_value=None): self.assertIsNone(model.reference('ro6_n_1_1', '1'))
        c, g = self.data(); self.assertIsNone(model._reference(c, g, 'missing'))


if __name__ == '__main__': unittest.main()
