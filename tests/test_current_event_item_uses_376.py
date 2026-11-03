from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import json
from rouge import current_event_item_uses as model


def clone(folder):
    root = Path(folder); names = {model.MANIFEST}
    names.update(json.loads((model.ROOT / model.MANIFEST).read_bytes())['files'])
    for name in names:
        path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((model.ROOT / name).read_bytes())
    return root


class CurrentEventItemUsesTests(TestCase):
    def test_full_literal_coverage_and_roles(self):
        result = model.reference(); self.assertEqual(len(result['rows']), 12)
        self.assertEqual(len({r['item_id'] for r in result['rows']}), 7); self.assertEqual(len({r['event_id'] for r in result['rows']}), 6)
        self.assertEqual({role: sum(r['role'] == role for r in result['rows']) for role, _ in model.ROLES}, {'held': 5, 'offered': 6, 'consumed': 1})

    def test_every_named_relation_has_full_literal_and_unique_identity(self):
        for row in model.reference()['rows']:
            self.assertIn(row['literal'], row['entry']['description']); self.assertTrue(row['literal'].endswith(row['item']['name']))
            self.assertIsNone(row['quantity_reference']); self.assertIsNone(row['actual_eligible']); self.assertIsNone(row['actual_consumed'])

    def test_held_controller_not_spent_or_granted_hunter_item(self):
        rows = model.reference(item_id='rogue_6_scrap_G_12')['rows']
        self.assertEqual(len(rows), 3); self.assertTrue(all(r['role'] == 'held' for r in rows))
        self.assertEqual({r['event_title'] for r in rows}, {'黑诞', '呼吸的红苔', '愈创之心'})
        self.assertEqual(model.reference(item_id='rogue_6_relic_cargo_12')['rows'], [])

    def test_key_four_uses_and_three_offering_phases_not_merged(self):
        rows = model.reference(item_id='rogue_6_relic_cargo_13')['rows']; self.assertEqual(len(rows), 4)
        offered = [r for r in rows if r['role'] == 'offered']; consumed = [r for r in rows if r['role'] == 'consumed']
        self.assertEqual(len(offered), 3); self.assertEqual(len(consumed), 1)
        self.assertEqual(len({r['entry']['scene_id'] for r in offered}), 3)
        self.assertTrue(all(r['quantity_reference'] is None for r in rows))

    def test_clover_and_covenant_are_only_possession(self):
        for iid in ('rogue_6_relic_legacy_113', 'rogue_6_relic_final_8'):
            rows = model.reference(item_id=iid)['rows']; self.assertEqual(len(rows), 1); self.assertEqual(rows[0]['role'], 'held')

    def test_all12_exact_phase_targets(self):
        for row in model.reference()['rows']:
            target = model.destination(model.reference(row['id']))
            self.assertEqual((target['scene_id'], target['choice_id']), (row['entry']['scene_id'], row['entry']['choice_id']))
            self.assertIsNone(target['actual_eligible']); self.assertFalse(target['run_updated'])

    def test_filters_by_full_item_and_role_do_not_claim_inventory(self):
        result = model.reference(item_id='rogue_6_relic_cargo_13', role='offered', query='调谐仪式')
        self.assertEqual(len(result['rows']), 3); self.assertIsNone(result['actual_inventory'])
        self.assertTrue(all(r['actual_held'] is None for r in result['rows']))

    def test_existing_acquisition_links_are_optional_not_exhaustive(self):
        rows = model.reference()['rows']; got = set()
        for row in rows:
            target = model.acquisition_target(model.reference(row['id']))
            if target: got.add(target['item_id']); self.assertEqual(target['category'], row['category'])
        self.assertEqual(got, {'rogue_6_scrap_G_12', 'rogue_6_relic_cargo_13', 'rogue_6_relic_final_4', 'rogue_6_relic_final_6'})

    def test_unknown_quantity_and_missing_source_explained(self):
        row = model.reference(item_id='rogue_6_relic_cargo_13')['rows'][0]
        text = model.player_text(model.reference(row['id']))
        self.assertIn('不默认每次1件', text); self.assertIn('不能据此说一把钥匙可完成三步', text)
        self.assertIn('不表示无法获得', text)

    def test_invalid_types_and_forged_target_rejected(self):
        self.assertIsNone(model.reference(role=True)); self.assertIsNone(model.reference(query=None)); self.assertIsNone(model.reference(item_id=3))
        self.assertIsNone(model.destination(model.reference()))
        row = model.reference()['rows'][0]; result = model.reference(row['id']); result['selected']['role'] = 'consumed'
        self.assertIsNone(model.destination(result)); self.assertIsNone(model.acquisition_target(result))

    def test_damaged_own_or_current_item_source_refuses(self):
        with TemporaryDirectory() as folder:
            root = clone(folder); path = root / model.DATA; raw = path.read_bytes()
            with patch.object(model, 'ROOT', root):
                path.write_bytes(raw + b'x'); self.assertIsNone(model.packet()); path.write_bytes(raw); self.assertIsNotNone(model.reference())
                path = root / (model.version.PACK + '/current-topic.json'); path.write_bytes(path.read_bytes() + b'x'); self.assertIsNone(model.packet())

    def test_return_copy_cannot_mutate_other_reader_or_run(self):
        one = model.reference(); one['rows'][0]['item']['name'] = '局部改名'
        self.assertNotEqual(model.reference()['rows'][0]['item']['name'], '局部改名')
        self.assertFalse(model.reference()['run_updated'])
