"""Build each event from one provider snapshot while retaining the fixed catalogue."""
from collections import Counter
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from rouge import current_event_directory as model, current_node_readers, node_catalog


class EventDirectoryDeriveReview(unittest.TestCase):
    def test_one_reference_per_event_preserves_all_fixed_rows_and_choices(self):
        catalogue = node_catalog.all_events(include_indirect=True)['rows']
        bindings = {e['id']: current_node_readers.binding_for(e) for e in catalogue}
        providers = model.providers()
        wrapped = {key: SimpleNamespace(reference=Mock(wraps=value.reference),
                                        scene_label=Mock(wraps=value.scene_label))
                   for key, value in providers.items()}
        result = model.derive(catalogue, bindings, wrapped)
        expected = json.loads((model.ROOT / model.DATA).read_bytes())
        self.assertEqual(result, expected)
        calls = Counter((key, c.args[0]) for key, value in wrapped.items()
                        for c in value.reference.call_args_list)
        self.assertEqual(calls, Counter((r['reader'], r['event_id']) for r in result['rows']))
        labels = Counter((key, c.args[1]) for key, value in wrapped.items()
                         for c in value.scene_label.call_args_list)
        expected_labels = Counter((r['reader'], sid) for r in result['rows']
                                  for sid in r['event']['scene_ids'] if r['scenes'][sid]['choice_ids'])
        self.assertEqual(labels, expected_labels)


    def test_build_stops_at_missing_binding_source_event_or_groups(self):
        group = {'id': 'group'}
        with self.assertRaisesRegex(ValueError, 'retain its exact current reader'):
            model.derive([group], {'group': None}, {})
        provider = SimpleNamespace(reference=Mock(return_value=None))
        binding = {'group': {'reader':'flows321', 'current_event_id':'missing'}}
        with self.assertRaisesRegex(ValueError, 'Current event source unavailable'):
            model.derive([group], binding, {'flows321':provider})
        with self.assertRaisesRegex(ValueError, 'Current extra event source unavailable'):
            model.derive([], {}, {'flows321':provider})
        with self.assertRaisesRegex(ValueError, 'Exact current event required'):
            model._snapshot({'events':{}}, 'missing')
        with self.assertRaisesRegex(ValueError, '38 source groups'):
            model.derive([], {}, model.providers())


if __name__ == '__main__':
    unittest.main()
