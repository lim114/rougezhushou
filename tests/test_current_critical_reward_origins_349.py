from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json, subprocess, sys, unittest
from rouge import current_critical_reward_origins as model, current_reward_origins as unified

def clone(root):
    for name in (model.MANIFEST, *json.loads((model.ROOT / model.MANIFEST).read_bytes())['files']):
        path = root / name; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((model.ROOT / name).read_bytes())

class CriticalReward349Tests(unittest.TestCase):
    def test_build_and_all_three_explicit_grants_exactly_match_original(self):
        result = subprocess.run([sys.executable, '-B', 'scripts/build_current_critical_reward_origins_349.py', '--check'], cwd=model.ROOT, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = model.packet()['data']['rows']; self.assertEqual(len(rows), 3)
        current = model.version.packet()['current']['details']
        self.assertEqual({r['item']['name'] for r in rows}, {'谒日之祈', '破碎噩兆', '生命蓝图'})
        for row in rows:
            self.assertEqual(row['choice'], current['choices'][row['choice_id']])
            self.assertEqual(row['item'], current['items'][row['item_id']])
            self.assertEqual(row['choice']['displayData']['itemId'], row['item_id'])
            self.assertNotIn(row['item']['name'], model.version._plain(row['choice']['description']))
            self.assertEqual(unified.reference('relics', row['item_id'])['kind'], 'critical_acquisition_349')

    def test_entry_cost_boundary_unlock_and_event_not_inferred_from_cost(self):
        iid = 'rogue_6_relic_final_7'
        for gold, match in [(None, None), (0, False), (9, False), (10, True), (11, True)]:
            result = model.reference('relics', iid, {'node_type': '险路尽头', 'floor': 1, 'gold': gold, 'post_update_clear': True})
            checked = result['condition_reference']; cid = result['rows'][0]['choice_id']
            self.assertEqual(checked['listed_conditions_status'], 'listed_matched')
            self.assertIs(checked['choice_checks'][cid][-1]['matches'], match)
            self.assertIsNone(checked['actual_choice_eligible']); self.assertFalse(result['run_updated'])
        bad = model.reference('relics', iid, {'node_type': '险路尽头', 'floor': 3})
        self.assertEqual(bad['condition_reference']['listed_conditions_status'], 'not_matched')
        locked = model.reference('relics', iid, {'gold': 10, 'post_update_clear': False})
        self.assertEqual(locked['condition_reference']['choice_conditions_status']['choice_ro6_final1_8'], 'not_matched')

    def test_rescue_one_use_and_blueprint_unknown_not_arbitrary_node(self):
        iid = 'rogue_6_relic_final_9'
        for used, status in [(None, 'unknown'), (False, 'listed_matched'), (True, 'not_matched')]:
            result = model.reference('relics', iid, {'node_type': '不期而遇', 'next_unmarked_after_first_down': True, 'rescue_used': used})
            self.assertEqual(result['condition_reference']['listed_conditions_status'], status)
            self.assertIn('不是当前生命值', model.player_text(result))
        result = model.reference('relics', 'rogue_6_relic_final_10', {'floor': 1, 'node_type': '不期而遇'})
        self.assertEqual(result['condition_reference']['listed_conditions_status'], 'unknown')
        self.assertIn('不能把每个不期而遇', model.player_text(result))

    def test_tampered_source_pointer_role_and_parent_rejected(self):
        current = model.version.packet()['current']['details']; packets = [p.packet() for p in model.PROVIDERS]
        cid = 'choice_ro6_revive_1'
        for change in ('pointer', 'role', 'parent'):
            c = deepcopy(current); p = deepcopy(packets)
            if change == 'pointer': c['choices'][cid]['displayData']['itemId'] = 'rogue_6_relic_final_8'
            elif change == 'role': c['choices'][cid]['description'] = '持有收藏品'
            else: p[1]['data']['choices'][cid]['event_id'] = 'blueprint'
            if change != 'parent':
                p[0]['data']['selected_originals']['choices'][cid] = deepcopy(c['choices'][cid])
                p[1]['data']['originals']['choices'][cid] = deepcopy(c['choices'][cid])
            with self.assertRaises(ValueError): model.source_rows(c, *p)

    def test_every_manifest_file_loss_after_success_closes_new_only_and_recovers(self):
        with TemporaryDirectory() as folder:
            root = Path(folder); clone(root)
            with patch.object(model, 'ROOT', root):
                for name in (model.MANIFEST, *json.loads((root / model.MANIFEST).read_bytes())['files']):
                    path = root / name; raw = path.read_bytes(); self.assertIsNotNone(model.packet())
                    path.write_bytes(raw + b'x'); self.assertIsNone(model.packet(), name)
                    self.assertIsNotNone(unified.reference('relics', 'rogue_6_relic_artifact_5'))
                    self.assertIsNotNone(unified.reference('relics', 'rogue_6_relic_cargo_13'))
                    path.write_bytes(raw); self.assertIsNotNone(model.packet())

    def test_upstream_loss_unknown_quantities_types_and_mutable_isolation(self):
        for provider in model.PROVIDERS:
            with patch.object(provider, 'packet', return_value=None): self.assertIsNone(model.packet())
        for category, iid in [(True, 'rogue_6_relic_final_7'), ('scrap', 'rogue_6_relic_final_7'), ('relics', True), ('relics', 'rogue_6_relic_final_8')]:
            self.assertIsNone(model.reference(category, iid))
        r = model.reference('relics', 'rogue_6_relic_final_9')
        self.assertIsNone(r['actual_quantity']); self.assertIsNone(r['actual_received']); self.assertFalse(r['complete_acquisition_pool'])
        r['rows'][0]['target'].clear(); self.assertTrue(model.reference('relics', 'rogue_6_relic_final_9')['rows'][0]['target'])

if __name__ == '__main__': unittest.main()
