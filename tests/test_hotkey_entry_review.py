"""Shortcut entry and approved failure behavior, without real hotkey registration."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QWidget
from rouge import player_hotkey as hotkeys
from rouge.player_compact import CompactAssistant
from tests.test_player_hotkey_393 import Api


class PreferenceEntryTests(unittest.TestCase):
    def test_non_text_and_missing_shortcut_disable_without_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'preferences.json'
            for value in (None, 17, [], {}, True):
                with self.subTest(value=value):
                    raw = json.dumps({'enabled': True, 'allow_single': False, 'shortcut': value})
                    path.write_text(raw)
                    data, warning = hotkeys.load_preferences(path)
                    self.assertFalse(data['enabled'])
                    self.assertTrue(warning)
                    self.assertEqual(path.read_text(), raw)
            path.write_text('{"enabled":true,"allow_single":false}')
            self.assertFalse(hotkeys.load_preferences(path)[0]['enabled'])

    def test_unreadable_file_disables_and_does_not_write(self):
        with patch.object(Path, 'read_text', side_effect=PermissionError('denied')), patch.object(Path, 'write_text') as write:
            data, warning = hotkeys.load_preferences('isolated.json')
        self.assertFalse(data['enabled'])
        self.assertIn('未启用', warning)
        write.assert_not_called()


class ShortcutEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.owner = QWidget()
        self.owner.run = SimpleNamespace(state={})
        self.owner.closing = True
        self.owner.map_overlay_reference = None
        self.owner.session_recorder = None
        self.owner.node_statistics_source = lambda: None
        self.bar = CompactAssistant(self.owner)
        self.bar.hotkey.api = self.api = Api()
        self.addCleanup(self.owner.deleteLater)
        self.addCleanup(self.bar.close)

    def test_apply_parses_once_and_preserves_previous_on_invalid_or_conflicting_input(self):
        self.bar.hotkey_enabled.setChecked(True)
        self.bar.hotkey_keys.setCurrentText('alt+ctrl+space')
        with patch.object(hotkeys, 'parse_shortcut', wraps=hotkeys.parse_shortcut) as parse:
            self.bar.apply_hotkey()
        self.assertEqual(parse.call_count, 1)
        self.assertEqual(self.bar.hotkey_keys.currentText(), hotkeys.DEFAULT)
        prior = dict(self.bar.hotkey_preferences)
        original = self.bar.hotkey.binding
        self.bar.hotkey_keys.setCurrentText('Ctrl+')
        self.bar.apply_hotkey()
        self.assertEqual(self.bar.hotkey.binding, original)
        self.assertEqual(self.bar.hotkey_preferences, prior)
        self.api.fail = True
        self.bar.hotkey_keys.setCurrentText('Ctrl+Shift+F10')
        self.bar.apply_hotkey()
        self.assertEqual(self.bar.hotkey.shortcut, hotkeys.DEFAULT)
        self.assertEqual(self.bar.hotkey_preferences, prior)
        self.assertEqual(self.bar.hotkey.binding, original)

    def test_disabled_configuration_keeps_canonical_text_without_registration(self):
        self.bar.hotkey_keys.setCurrentText('shift+ctrl+f10')
        self.bar.hotkey_enabled.setChecked(False)
        with patch.object(hotkeys, 'parse_shortcut', wraps=hotkeys.parse_shortcut) as parse:
            self.bar.apply_hotkey()
        self.assertEqual(parse.call_count, 1)
        self.assertEqual(self.bar.hotkey_preferences['shortcut'], 'Ctrl+Shift+F10')
        self.assertFalse(self.api.keys)

    def test_save_error_keeps_current_binding_and_explicit_warning(self):
        self.bar.hotkey_enabled.setChecked(True)
        self.bar.hotkey_path = Path('isolated-not-written.json')
        with patch.object(hotkeys, 'save_preferences', side_effect=OSError('save failed')) as save:
            self.bar.apply_hotkey()
        save.assert_called_once()
        self.assertIsNotNone(self.bar.hotkey.binding)
        self.assertIn('重启后不会保留', self.bar.hotkey_status.text())

    def test_unregister_failure_rolls_back_new_binding_and_keeps_old_name(self):
        key = self.bar.hotkey
        key.configure(True, hotkeys.DEFAULT)
        old = key.binding
        unregister = self.api.unregister
        with patch.object(self.api, 'unregister', side_effect=lambda identity: False if identity == old[0] else unregister(identity)):
            self.assertFalse(key.configure(True, 'Ctrl+Shift+F10')[0])
        self.assertEqual(key.binding, old)
        self.assertEqual(key.shortcut, hotkeys.DEFAULT)
        self.assertEqual(list(self.api.keys), [old[0]])

    def test_identifier_limit_does_not_call_register(self):
        with patch.object(hotkeys.GlobalHotkey, '_next_id', 0xC000), patch.object(self.api, 'register') as register:
            self.assertFalse(self.bar.hotkey.configure(True, hotkeys.DEFAULT)[0])
        register.assert_not_called()

    def test_button_drag_signal_uses_current_position(self):
        origin = self.bar.pos()
        with patch.object(self.bar, '_move_dock') as move:
            self.bar.tool_buttons[0].dragged.emit(QPoint(12, -9))
        move.assert_called_once_with(origin + QPoint(12, -9))
