from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import json
from rouge import current_stage_objects as objects,current_route_itinerary as itinerary,current_enemy_spawns as enemies


class BattleReaderBoundaryTests(TestCase):
    def test_object_and_itinerary_pinned_members_reject_corruption(self):
        root=Path(__file__).resolve().parents[1]
        for model in (objects,itinerary):
            names=[model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']]
            with TemporaryDirectory() as temporary:
                target=Path(temporary)
                for name in names:
                    path=target/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((root/name).read_bytes())
                with patch.object(model.battle.version,'_file',side_effect=lambda name:target/name):
                    self.assertIsNotNone(model.packet())
                    for name in names:
                        with self.subTest(model=model.__name__,name=name):
                            path=target/name;raw=path.read_bytes();path.write_bytes(raw+b' ')
                            self.assertIsNone(model.packet());path.write_bytes(raw)

    def test_inventory_identity_stage_and_source_gate_before_derivation(self):
        current=objects.battle.stage_reference('ro6_n_1_1')
        for model in (objects,itinerary):
            reference=model.packet()
            for field in ('identity','stage','level','source'):
                changed=deepcopy(reference);inventory=changed['inventory']
                if field=='identity':inventory['battle_identity']='foreign'
                elif field=='stage':inventory['stages'].pop(current['id'])
                elif field=='level':inventory['stages'][current['id']]['level_key']='foreign'
                else:inventory['stages'][current['id']]['original_source']={}
                with self.subTest(model=model.__name__,field=field),patch.object(model,'packet',return_value=changed),patch.object(model,'_derive') as derive:
                    actual=objects.from_battle(current) if model is objects else itinerary.stage_reference(current['id'],prepared_current=current)
                    self.assertIsNone(actual);derive.assert_not_called()

    def test_public_selection_bad_shape_stops_before_fresh_lookup(self):
        for model,resolve in ((objects,objects.resolve),(itinerary,itinerary.resolve),(enemies,enemies.resolve_action)):
            with patch.object(model,'stage_reference') as lookup:
                self.assertIsNone(resolve(None,'0'));self.assertIsNone(resolve({},False))
                lookup.assert_not_called()
        self.assertIsNone(objects.resolve({},'0'))
        self.assertIsNone(itinerary.resolve({},'0'))
        self.assertIsNone(enemies.resolve_action({},'0'))

    def test_filter_normal_empty_and_internal_missing_fields_are_distinct(self):
        for read in (objects.rows,itinerary.routes,enemies.rows):
            self.assertEqual(read(None),[])
            self.assertEqual(read({'entries':[]}),[])
            with self.assertRaises(KeyError):read({})
        self.assertEqual(objects.rows({'entries':[]},kind='not-supported'),[])
        self.assertEqual(itinerary.routes({'entries':[]},scope='not-supported'),[])
        self.assertEqual(enemies.rows({'entries':[]},kind='not-supported'),[])
