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
