from copy import deepcopy
from hashlib import sha256
import json
from unittest import TestCase
from unittest.mock import patch
from rouge import current_map_position as positions, current_map_markers, boss_map_markers


class MarkerGeometryReuseTests(TestCase):
    def test_pinned_full_geometry_and_digest_contract(self):
        for module in (current_map_markers,boss_map_markers):
            packet=module.packet()
            for row in packet['data']['bindings'].values():
                with self.subTest(stage=row['stage_id']):
                    actual=sha256(json.dumps(row['full_selected_geometry'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                    self.assertEqual(actual,row['full_selected_geometry_sha256'])

    def test_parent_does_not_repeat_geometry_serialization(self):
        packet=positions.packet()
        for module in (current_map_markers,boss_map_markers):
            symbols=module.packet()
            with self.subTest(module=module.__name__),patch.object(module,'packet',return_value=symbols),patch.object(positions.json,'dumps',wraps=json.dumps) as dumps:
                result=positions.stage_reference(module.STAGES[0],prepared_packet=packet)
            self.assertIsNotNone(result)
            geometry_calls=[c for c in dumps.call_args_list if isinstance(c.args[0],dict) and set(c.args[0])==set(packet['data']['geometry_keys'])]
            self.assertEqual(len(geometry_calls),1)

    def test_binder_rejects_wrong_level_key_before_using_it(self):
        current=positions.packet()['current']
        for module in (current_map_markers,boss_map_markers):
            packet=deepcopy(module.packet());packet['data']['bindings'][module.STAGES[0]]['current_level_key']='wrong-key'
            with self.subTest(module=module.__name__),patch.object(module,'packet',return_value=packet):
                self.assertIsNone(module.mapping_for(module.STAGES[0],current))
