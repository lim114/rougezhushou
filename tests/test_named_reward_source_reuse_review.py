from contextlib import ExitStack
from copy import deepcopy
import unittest
from unittest.mock import patch

from rouge import current_named_reward_origins as model


class NamedRewardSourceReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = model.providers()
        cls.packets = {key: module.packet() for key, module in cls.modules.items()}
        cls.current = model.version.packet()['current']['details']

    def test_row_build_uses_supplied_provider_packets(self):
        expected = model.source_rows(self.packets, self.current, self.modules)
        with ExitStack() as stack:
            for module in self.modules.values():
                stack.enter_context(patch.object(module, 'packet', side_effect=AssertionError('unexpected reread')))
            actual = model.source_rows(self.packets, self.current, self.modules)
        self.assertEqual(actual, expected)

    def test_provider_identity_normalized_once_and_rows_remain_independent(self):
        with patch.object(model.json, 'dumps', wraps=model.json.dumps) as normalize:
            rows = model.source_rows(self.packets, self.current, self.modules)
        self.assertEqual(normalize.call_count, len(self.modules))
        sibling = deepcopy(rows[1]['reader_source_identity'])
        original = deepcopy(self.packets['resources']['source_identity'])
        rows[0]['reader_source_identity'].append('changed')
        self.assertEqual(rows[1]['reader_source_identity'], sibling)
        self.assertEqual(self.packets['resources']['source_identity'], original)

    def test_packet_loads_each_provider_once(self):
        with ExitStack() as stack:
            readers = {key: stack.enter_context(patch.object(module, 'packet', wraps=module.packet))
                       for key, module in self.modules.items()}
            self.assertIsNotNone(model.packet())
        self.assertEqual({key: read.call_count for key, read in readers.items()},
                         dict.fromkeys(self.modules, 1))


if __name__ == '__main__':
    unittest.main()
