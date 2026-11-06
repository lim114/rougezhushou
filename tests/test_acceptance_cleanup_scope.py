from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import unittest
from rouge import player_feature_418_acceptance as a418
from rouge import player_feature_422_acceptance as a422
from rouge import player_feature_423_acceptance as a423


class Hover:
    def __init__(self):
        self.timer = MagicMock()
        self.gate = SimpleNamespace(key=None)
        self.clears = 0
        self.tick = MagicMock()
        self._card = None
    @property
    def card(self): return self._card
    @card.setter
    def card(self, value):
        self._card = value
        if value is None: self.clears += 1


class AcceptanceCleanupTests(unittest.TestCase):
    def test_hover_cleanup_once_on_success_and_exception(self):
        for fail in (False, True):
            with self.subTest(fail=fail):
                hover = Hover()
                compact = MagicMock(); compact.game_hover = hover
                window = SimpleNamespace(show_compact=lambda: None, compact_window=compact)
                card = MagicMock()
                if fail: card.install.side_effect = RuntimeError('interrupted')
                with patch('rouge.player_item_hover.ItemHoverCard', return_value=card):
                    if fail:
                        with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                            a418.check(window, MagicMock(), lambda *args: None)
                    else:
                        a418.check(window, MagicMock(), lambda *args: None)
                        self.assertIs(window.player_validation_target, card)
                self.assertEqual(hover.clears, 1)
                self.assertIsNone(hover.card)

    def test_floor_failure_restores_isolated_state(self):
        before = {'maps': {'existing': 1}, 'history': [], 'resources': {}}
        window = SimpleNamespace(run=SimpleNamespace(state=deepcopy(before)))
        def interrupt():
            window.run.state['maps'] = {'changed': 2}
            raise RuntimeError('interrupted')
        with patch('rouge.player_map_acceptance.fixtures', side_effect=interrupt):
            with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                a422.check(window, MagicMock(), lambda *args: None)
        self.assertEqual(window.run.state, before)

    def test_shop_failure_restores_isolated_state(self):
        before = {'id': 'isolated', 'relics': {}}
        window = SimpleNamespace(run=SimpleNamespace(state=deepcopy(before)))
        def interrupt(*args):
            window.run.state['id'] = 'changed'
            raise RuntimeError('interrupted')
        with patch('rouge.player_shop_hover.ShopNameReader', side_effect=interrupt):
            with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                a423.check(window, MagicMock(), lambda *args: None)
        self.assertEqual(window.run.state, before)

    def test_other_approved_entries_restore_state_on_interruption(self):
        from importlib import import_module
        cases = [(426, 'check_prices'), (426, 'check'), (427, 'check'),
                 (428, 'check'), (430, 'check'), (431, 'check'),
                 (432, 'check'), (435, 'check'), (436, 'check'),
                 (437, 'check'), (438, 'check'), (439, 'check'), (440, 'check')]
        for section, entry in cases:
            with self.subTest(section=section, entry=entry):
                before = {'id': 'isolated', 'history': [], 'maps': {},
                          'resources': {}, 'relics': {}, 'started_at': 0}
                old_graph = {'original': True}
                view = SimpleNamespace(graph=old_graph, historical=False)
                def set_map(graph, *, historical):
                    view.graph = graph
                    view.historical = historical
                view.set_map = set_map
                window = SimpleNamespace(run=SimpleNamespace(state=deepcopy(before)), map_view=view,
                                         findChildren=lambda *args: [])
                reached = []
                def interrupt(*args):
                    reached.append(True)
                    window.run.state['id'] = 'interrupted'
                    raise RuntimeError('deliberate interruption')
                window.show_compact = interrupt
                window.apply_run_observation = interrupt
                module = import_module(f'rouge.player_feature_{section}_acceptance')
                with self.assertRaisesRegex(RuntimeError, 'deliberate interruption'):
                    getattr(module, entry)(window, MagicMock(), lambda *args: None)
                self.assertEqual(reached, [True])
                self.assertEqual(window.run.state, before)
                if section == 438:
                    self.assertIs(view.graph, old_graph)
                    self.assertFalse(view.historical)
