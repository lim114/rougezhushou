"""Native failures remain recoverable; programming faults are no longer swallowed."""
import unittest
from unittest.mock import patch

import pywintypes
from rouge import capture, credentials


class NativeBoundaryTests(unittest.TestCase):
    def test_missing_credential_keeps_empty_result(self):
        with patch.object(credentials.win32cred, 'CredRead', side_effect=pywintypes.error(1168, 'CredRead', 'not found')):
            self.assertEqual(credentials.read_key('isolated-test'), '')

    def test_credential_programming_error_is_not_an_absent_key(self):
        with patch.object(credentials.win32cred, 'CredRead', side_effect=RuntimeError('programming error')):
            with self.assertRaisesRegex(RuntimeError, 'programming error'):
                credentials.read_key('isolated-test')

    def test_credential_decode_remains_exact(self):
        with patch.object(credentials.win32cred, 'CredRead', return_value={'CredentialBlob': 'test-only'.encode('utf-16-le')}):
            self.assertEqual(credentials.read_key('isolated-test'), 'test-only')

    def test_window_disappearing_during_enumeration_is_skipped(self):
        with patch.object(capture, 'process_names', return_value={}), \
             patch.object(capture.win32gui, 'EnumWindows', side_effect=lambda visit, arg: visit(123, arg)), \
             patch.object(capture.win32gui, 'IsWindowVisible', return_value=True), \
             patch.object(capture.win32gui, 'GetWindowText', return_value='明日方舟'), \
             patch.object(capture.win32process, 'GetWindowThreadProcessId', side_effect=pywintypes.error(1400, 'GetWindowThreadProcessId', 'invalid handle')):
            self.assertEqual(capture.list_game_windows(), [])

    def test_window_programming_error_is_not_an_empty_window_list(self):
        with patch.object(capture, 'process_names', return_value={}), \
             patch.object(capture.win32gui, 'EnumWindows', side_effect=lambda visit, arg: visit(123, arg)), \
             patch.object(capture.win32gui, 'IsWindowVisible', return_value=True), \
             patch.object(capture.win32gui, 'GetWindowText', return_value='明日方舟'), \
             patch.object(capture.win32process, 'GetWindowThreadProcessId', side_effect=RuntimeError('programming error')):
            with self.assertRaisesRegex(RuntimeError, 'programming error'):
                capture.list_game_windows()
