from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import json
from rouge import current_event_directory as model


def clone(folder):
    root = Path(folder); names = {model.MANIFEST}
    names.update(json.loads((model.ROOT / model.MANIFEST).read_bytes())['files'])
    for name in names:
        p = root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes((model.ROOT / name).read_bytes())
    return root


class CurrentEventDirectoryTests(TestCase):
    def test_full_current_coverage_and_old_groups(self):
        ref = model.reference(); self.assertIsNotNone(ref)
        self.assertEqual(len(ref['rows']), 39)
        self.assertEqual(sum(len(r['catalogue_groups']) for r in ref['rows']), 38)
        self.assertEqual(sum(len(r['entries']) for r in ref['rows']), 277)
        self.assertEqual(len({r['id'] for r in ref['rows']}), 39)

    def test_three_picture_groups_not_three_current_events(self):
        rows = [r for r in model.reference()['rows'] if r['title'] == '三重身']
        self.assertEqual(len(rows), 1); self.assertEqual(len(rows[0]['catalogue_groups']), 3)
        self.assertEqual(len({r['id'] for r in rows[0]['catalogue_groups']}), 3)

    def test_unclassified_not_assigned_unknown_node_type(self):
        ref = model.reference(node_type='unclassified')
        self.assertEqual({r['title'] for r in ref['rows']}, {'安眠一隅', '大红按钮', '制图桌', '手术祭坛'})
        self.assertTrue(all(r['node_types'] == [] for r in ref['rows']))

    def test_search_in_choice_reward_and_name(self):
        self.assertEqual([r['title'] for r in model.reference(query='手术祭坛')['rows']], ['手术祭坛'])
        self.assertIn('黑诞', [r['title'] for r in model.reference(query='笼控器')['rows']])
        self.assertIn('愈创之心', [r['title'] for r in model.reference(query='追忆')['rows']])
        self.assertEqual(model.reference(query='不存在的资料检索词')['rows'], [])

    def test_literal_topic_filters_do_not_evaluate_eligibility(self):
        for topic, _ in model.TOPICS:
            ref = model.reference(topic=topic)
            self.assertTrue(ref['rows']); self.assertTrue(all(topic in r['topics'] for r in ref['rows']))
            self.assertTrue(all(r['actual_eligible'] is None for r in ref['rows']))
        self.assertIn('黑诞', [r['title'] for r in model.reference(topic='held')['rows']])

    def test_all277_memberships_are_exact_and_not_merged_across_phase(self):
        for row in model.reference()['rows']:
            self.assertEqual(len({e['key'] for e in row['entries']}), len(row['entries']))
            for entry in row['entries']:
                self.assertIn(entry['choice_id'], row['scenes'][entry['scene_id']]['choice_ids'])
                self.assertIn(entry['choice_id'], row['choices'])
                self.assertIsNone(entry['actual_eligible'])

    def test_all39_exact_event_targets_and_selected_choice(self):
        rows = model.reference()['rows']
        for row in rows:
            result = model.reference(row['id'])
            target = model.resolve(result)
            self.assertEqual(target['scene_id'], row['event']['entry_scene_id'])
            self.assertEqual(target['event']['reader'], row['reader'])
            if row['entries']:
                e = row['entries'][-1]; target = model.resolve(result, e['key'])
                self.assertEqual((target['scene_id'], target['choice_id']), (e['scene_id'], e['choice_id']))

    def test_invalid_types_and_filtered_selection_rejected(self):
        self.assertIsNone(model.reference(query=None)); self.assertIsNone(model.reference(topic=True))
        self.assertIsNone(model.reference(event_id=True)); self.assertIsNone(model.reference(query='a'*161))
        self.assertIsNone(model.reference('flows321:button', node_type='不期而遇'))
        self.assertIsNone(model.resolve(model.reference()))

    def test_forger_cannot_redirect_exact_target(self):
        result = model.reference('flows321:button'); row = result['selected']
        self.assertIsNone(model.resolve(result, 'foreign-choice'))
        row['event_id'] = 'revive'; self.assertIsNone(model.resolve(result))

    def test_word_classification_not_complete_qualification(self):
        self.assertEqual(model.topic_ids('没有这些词', False), [])
        self.assertEqual(model.topic_ids('持有笼控器，获得收藏品猎印', False), ['held'])
        self.assertIn('完整出现前置', model.player_text(model.reference('flows321:button')))
        self.assertIn('不是本局可能出现的完整清单', model.player_text(model.reference()))

    def test_damaged_new_source_and_manual_recovery(self):
        with TemporaryDirectory() as folder:
            root = clone(folder); path = root / model.DATA; raw = path.read_bytes()
            with patch.object(model, 'ROOT', root):
                path.write_bytes(raw + b'x'); self.assertIsNone(model.packet())
                path.write_bytes(raw); self.assertIsNotNone(model.reference())

    def test_damaged_existing_reader_source_refuses_directory(self):
        provider = model.providers()['resources']
        with TemporaryDirectory() as folder:
            root = clone(folder); path = root / provider.DATA
            path.write_bytes(path.read_bytes() + b'x')
            with patch.object(model, 'ROOT', root): self.assertIsNone(model.reference())

    def test_returned_objects_do_not_mutate_fresh_reader_or_run(self):
        one = model.reference(); one['rows'][0]['title'] = '局部改动'
        two = model.reference(); self.assertNotEqual(two['rows'][0]['title'], '局部改动')
        self.assertFalse(two['run_updated']); self.assertIsNone(two['actual_node']); self.assertIsNone(two['actual_eligible'])
