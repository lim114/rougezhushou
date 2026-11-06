import unittest
from unittest.mock import patch
import pywintypes
import winerror
from rouge import credentials
from rouge.player_file_messages import file_issue


class CredentialFailureTests(unittest.TestCase):
    def test_only_missing_credentials_return_empty(self):
        for code in (winerror.ERROR_ACCESS_DENIED, winerror.ERROR_NO_SUCH_LOGON_SESSION, winerror.ERROR_INVALID_FLAGS):
            failure = pywintypes.error(code, 'CredRead', 'synthetic error')
            with self.subTest(code=code), patch.object(credentials.win32cred, 'CredRead', side_effect=failure):
                with self.assertRaises(pywintypes.error) as raised:
                    credentials.read_key('isolated-test')
                self.assertIs(raised.exception, failure)

    def test_corrupt_payload_surfaces_without_fallback(self):
        for payload, error in (({}, KeyError), ({'CredentialBlob': b'x'}, UnicodeDecodeError)):
            with patch.object(credentials.win32cred, 'CredRead', return_value=payload):
                with self.assertRaises(error):
                    credentials.read_key('isolated-test')

    def test_generic_message_does_not_claim_save_or_editor_state(self):
        text = file_issue(ValueError('synthetic failure'))
        self.assertEqual(text, '记录内容暂时无法核对，请查看具体原因。')
        self.assertEqual(file_issue(ValueError('保存期间已被修改')), '保存期间已被修改')
