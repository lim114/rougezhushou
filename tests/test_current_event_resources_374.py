from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import json
from rouge import current_event_resources as model


def clone(folder):
    root = Path(folder); names = {model.MANIFEST}
    names.update(json.loads((model.ROOT / model.MANIFEST).read_bytes())['files'])
    for name in names:
        path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((model.ROOT / name).read_bytes())
    return root


def find(result, title, choice=None):
    return next(r for r in result['rows'] if r['event_title'] == title and (choice is None or r['entry']['title'] == choice))


class CurrentEventResourcesTests(TestCase):
    def test_complete_literal_coverage_and_source_domain(self):
        result = model.reference(); self.assertIsNotNone(result)
        self.assertEqual((result['data']['source_event_count'], result['data']['source_occurrence_count']), (39, 277))
        self.assertEqual(len(result['rows']), 88); self.assertEqual(sum(len(r['effects']) for r in result['rows']), 100)
        self.assertEqual(len({r['id'] for r in result['rows']}), 88)

    def test_resource_classes_and_directions_remain_distinct(self):
        for resource, _ in model.RESOURCES:
            result = model.reference(resource=resource); self.assertTrue(result['rows'], resource)
            self.assertTrue(all(any(e['resource'] == resource for e in r['matching_effects']) for r in result['rows']))
        for kind, _ in model.KINDS: self.assertTrue(model.reference(kind=kind)['rows'])

    def test_gain_filter_never_hides_cost_from_selected_entry(self):
        result = model.reference(resource='processed', kind='item'); row = find(result, '货从口出')
        selected = model.reference(row['id'], resource='processed', kind='item')
        self.assertEqual(len(selected['selected']['matching_effects']), 1)
        self.assertEqual({e['kind'] for e in selected['selected']['effects']}, {'cost', 'item'})
        self.assertIn('源石锭：4', model.player_text(selected))

    def test_hp_max_hp_and_shield_not_conflated(self):
        one = model.extract('获得3目标生命值上限，获得5护盾，回复1目标生命值')
        self.assertEqual([(e['resource'], e['quantity']) for e in one], [('max_life', 3), ('shield', 5), ('life', 1)])

    def test_half_and_all_never_guessed_or_rounded(self):
        one = model.extract('消耗一半的源石锭，失去一半目标生命上限，消耗全部行动力')
        self.assertEqual([e['amount_rule'] for e in one], ['half', 'half', 'all'])
        self.assertTrue(all(e['quantity'] is None for e in one))

    def test_equal_ap_conversion_is_not_guessed_net(self):
        result = model.reference(query='转化为等量希望'); self.assertEqual(len(result['rows']), 4)
        for row in result['rows']:
            pairs = {(e['resource'], e['amount_rule'], e['quantity']) for e in row['effects']}
            self.assertIn(('ap', 'all', None), pairs); self.assertIn(('hope', 'equal_spent_ap', None), pairs)
            self.assertIsNone(result['actual_net_change'])

    def test_original_only_exit_choices_do_not_gain_free_part(self):
        rows = model.reference(query='转化为等量希望')['rows']
        unbound = [r for r in rows if r['entry']['choice_id'] in ('choice_ro6_final1_6', 'choice_ro6_final1_7')]
        self.assertEqual(len(unbound), 2)
        self.assertTrue(all(not any(e['resource'] == 'processed' for e in r['effects']) for r in unbound))

    def test_reward_class_quantity_not_named_pool(self):
        one = model.extract('获得1件珍贵的加工品，获得3件随机收藏品')
        self.assertEqual([(e['resource'], e['quantity'], e['quality']) for e in one], [('processed', 1, '珍贵'), ('relic', 3, None)])
        self.assertTrue(all(e['complete_pool'] is None for e in one))
        self.assertEqual(model.extract('获得收藏品源私钥'), [])

    def test_capacity_unit_not_map_square(self):
        one = model.extract('可携带干员+1，零件箱容量+1')
        self.assertEqual([(e['resource'], e['quantity']) for e in one], [('carry', 1), ('weight', 1)])
        self.assertNotIn('格', model._amount(one[1]))

    def test_exact_original_dialogue_destination(self):
        for title, choice in [('色味不同源', '拿走看上去像是苹果的食物'), ('手术祭坛', '小心地移除电极'), ('沉重的契约', '推翻石磨')]:
            row = find(model.reference(), title, choice); target = model.destination(model.reference(row['id']))
            self.assertEqual((target['scene_id'], target['choice_id']), (row['entry']['scene_id'], row['entry']['choice_id']))

    def test_forgery_types_and_filtered_selection_rejected(self):
        self.assertIsNone(model.reference(resource=True)); self.assertIsNone(model.reference(query=None))
        self.assertIsNone(model.reference(kind='best')); self.assertIsNone(model.destination(model.reference()))
        row = model.reference()['rows'][0]; result = model.reference(row['id']); result['selected']['entry']['choice_id'] = 'foreign'
        self.assertIsNone(model.destination(result))

    def test_damaged_new_and_old_sources_refuse_then_recover(self):
        with TemporaryDirectory() as folder:
            root = clone(folder); path = root / model.DATA; raw = path.read_bytes()
            with patch.object(model, 'ROOT', root):
                path.write_bytes(raw + b'x'); self.assertIsNone(model.packet()); path.write_bytes(raw)
                self.assertIsNotNone(model.reference())
                other = root / model.directory.DATA; other.write_bytes(other.read_bytes() + b'x'); self.assertIsNone(model.packet())

    def test_life_minimum_boundary_and_unknown_run_are_visible(self):
        row = find(model.reference(), '黑诞', '落荒而逃'); result = model.reference(row['id'])
        self.assertIn('不当作生命不足时仍无条件扣满', model.player_text(result))
        self.assertIsNone(result['actual_net_change']); self.assertFalse(result['run_updated'])
