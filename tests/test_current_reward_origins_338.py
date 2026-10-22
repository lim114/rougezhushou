from copy import deepcopy
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib, json, subprocess, sys, unittest
from rouge import current_reward_origins as model

ITEMS = (('relics', 'rogue_6_relic_artifact_5', 3), ('relics', 'rogue_6_relic_cargo_10', 1), ('scrap', 'rogue_6_scrap_G_12', 2))

def clone(root):
    names = {model.MANIFEST}
    for m in (model, *model.PROVIDERS.values()):
        names.add(m.MANIFEST); names.update(json.loads((model.ROOT / m.MANIFEST).read_bytes())['files'])
    for name in names:
        dest = root / name; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes((model.ROOT / name).read_bytes())

class CurrentRewardOrigins338Tests(unittest.TestCase):
    def test_build_reproduces_all_six_exact_reward_rows(self):
        result = subprocess.run([sys.executable, '-B', 'scripts/build_current_reward_origins_338.py', '--check'], cwd=model.ROOT, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr); self.assertEqual(len(model.packet()['data']['rows']), 6)

    def test_three_named_items_counts_types_and_exact_current_record(self):
        for category, key, count in ITEMS:
            with self.subTest(item=key):
                r = model.reference(category, key); self.assertEqual(len(r['rows']), count)
                self.assertEqual(r['item'], model.version.detail(category, key)['row']['value']['item'])
                self.assertIsNone(r['actual_received']); self.assertIsNone(r['actual_eligible']); self.assertIsNone(r['actual_quantity'])
                self.assertIs(r['run_updated'], False); self.assertIs(r['complete_acquisition_pool'], False)

    def test_only_acquisition_roles_not_consumption_holding_movement_or_marking(self):
        rows = model.packet()['data']['rows']; choices = {r['choice_id'] for r in rows}
        self.assertNotIn('choice_ro6_normal5_4', choices)
        self.assertNotIn('choice_ro6_task2_3', choices); self.assertNotIn('choice_ro6_task2_4', choices)
        key_rows = model.reference('relics', 'rogue_6_relic_cargo_13')['rows']
        self.assertEqual([r['choice_id'] for r in key_rows], ['choice_ro6_surprise_1'])
        self.assertTrue(all(not r['choice_id'].startswith('choice_ro6_end3_') for r in key_rows))
        self.assertEqual({r['event_title'] for r in rows}, {'愈创之心', '独活', '沉寂之屋'})

    def test_three_memory_costs_are_separate_and_not_added(self):
        r = model.reference(*ITEMS[0][:2]); costs = [model.version._plain(v['choice']['description']) for v in r['rows']]
        self.assertIn('3行动力', costs[0]); self.assertIn('随机2件加工品', costs[1]); self.assertIn('源私钥', costs[2])
        self.assertNotIn('99', model.player_text(r, r['rows'][2]['key']))

    def test_controller_two_different_costs_and_unknown_quantities(self):
        r = model.reference(*ITEMS[2][:2]); first, second = r['rows']
        self.assertEqual(first['choice']['target_life_cost_reference'], 2)
        self.assertEqual(second['choice']['gold_cost_reference'], 8)
        self.assertTrue(all(v['choice']['named_part_quantity'] is None for v in r['rows']))

    def test_exact_event_scene_and_all_choice_membership(self):
        for row in model.packet()['data']['rows']:
            p = model.PROVIDERS[row['reader']].packet()['data']; c = p['choices'][row['choice_id']]
            self.assertEqual(c, row['choice']); self.assertIn(row['choice_id'], p['scenes'][row['scene_id']]['choice_ids'])

    def test_unknown_wrong_category_and_bad_inputs_have_no_entry(self):
        for category, key in [('scrap', ITEMS[0][1]), ('relics', ITEMS[2][1]), ('scenes', ITEMS[0][1]), ('relics', '追忆'), ('relics', ITEMS[0][1] + '_2'), (True, ITEMS[0][1]), ('relics', None)]:
            self.assertIsNone(model.reference(category, key))

    def test_isolated_results_do_not_mutate_later_queries(self):
        r = model.reference(*ITEMS[0][:2]); r['rows'][0]['choice']['title'] = 'forged'; r['item']['name'] = 'forged'
        fresh = model.reference(*ITEMS[0][:2]); self.assertEqual(fresh['item']['name'], '追忆'); self.assertNotEqual(fresh['rows'][0]['choice']['title'], 'forged')

    def test_every_manifest_member_damage_fails_closed_after_prior_success(self):
        with TemporaryDirectory() as folder:
            root = Path(folder); clone(root)
            with patch.object(model, 'ROOT', root):
                manifest = json.loads((root / model.MANIFEST).read_bytes())
                for name in (model.MANIFEST, *manifest['files']):
                    p = root / name; raw = p.read_bytes()
                    self.assertIsNotNone(model.reference(*ITEMS[0][:2])); p.write_bytes(raw + b' ')
                    self.assertIsNone(model.reference(*ITEMS[0][:2]), name); p.write_bytes(raw)

    def test_underlying_document_loss_cannot_reuse_cached_provider_result(self):
        with TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder); clone(root); stack.enter_context(patch.object(model, 'ROOT', root))
            for provider in model.PROVIDERS.values(): stack.enter_context(patch.object(provider, 'ROOT', root))
            self.assertIsNotNone(model.packet())
            path = root / 'research/p3-current-vine-events-333/documented-tables.html'; raw = path.read_bytes(); path.write_bytes(raw + b' ')
            self.assertIsNone(model.packet()); path.write_bytes(raw); self.assertIsNotNone(model.packet())

    def test_current_item_mismatch_rejects_same_named_foreign_entry(self):
        original = model.version.detail(*ITEMS[0][:2]); forged = deepcopy(original); forged['row']['value']['item']['usage'] += ' changed'
        with patch.object(model.version, 'detail', return_value=forged): self.assertIsNone(model.reference(*ITEMS[0][:2]))

    def test_player_text_has_plain_scope_and_never_complete_pool_or_claim(self):
        for category, item, _ in ITEMS:
            r = model.reference(category, item)
            for row in r['rows']:
                text = model.player_text(r, row['key']); self.assertIn(row['event_title'], text); self.assertIn(row['choice']['title'], text)
                for word in ('不是完整获取池', '原文未独立写明', '不支付、不领取', '没有列出不等于无法取得'): self.assertIn(word, text)

if __name__ == '__main__': unittest.main()
