from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from rouge.technology_state import TechnologyState


class TechnologyCleanupTests(unittest.TestCase):
    def test_published_save_remains_success_and_reports_cleanup_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'technology.json'
            state = TechnologyState(path)
            with patch.object(Path, 'unlink', side_effect=OSError('cleanup denied')):
                self.assertTrue(state.set_status('rogue_6_outbuff_1', 'unlocked'))
            self.assertEqual(TechnologyState(path).view('rogue_6_outbuff_1')['status'], 'unlocked')
            self.assertFalse(state.preserve_original)
            self.assertIn('已保存', state.persistence_notice())
            self.assertIn('cleanup denied', state.persistence_notice())
            self.assertNotIn('仅在当前运行有效', state.persistence_notice())

    def test_failed_publish_keeps_original_failure_and_cleanup_notice(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'technology.json'
            state = TechnologyState(path)
            state.set_status('rogue_6_outbuff_1', 'locked')
            before = path.read_bytes()
            with patch('rouge.technology_state.os.replace', side_effect=OSError('publish denied')), patch.object(Path, 'unlink', side_effect=OSError('cleanup denied')):
                self.assertFalse(state.set_status('rogue_6_outbuff_1', 'unlocked'))
            self.assertEqual(path.read_bytes(), before)
            notice = state.persistence_notice()
            self.assertIn('保存未完成', notice)
            self.assertIn('cleanup denied', notice)
            self.assertNotIn('资料已保存', notice)

    def test_loading_link_or_unreadable_path_preserves_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'technology.json'
            for patches in ('linked', 'unreadable'):
                with self.subTest(case=patches):
                    target = 'is_symlink' if patches == 'linked' else 'read_bytes'
                    kwargs = {'return_value': True} if patches == 'linked' else {'side_effect': OSError('denied')}
                    with patch.object(Path, target, **kwargs):
                        state = TechnologyState(path)
                    self.assertTrue(state.preserve_original)
                    self.assertFalse(state.save())
                    self.assertFalse(path.exists())

    def test_missing_read_but_existing_entry_is_not_first_run(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'technology.json'
            with patch.object(Path, 'is_symlink', return_value=False), patch.object(Path, 'read_bytes', side_effect=FileNotFoundError()), patch.object(Path, 'lstat', return_value=object()):
                state = TechnologyState(path)
            self.assertTrue(state.preserve_original)
            self.assertFalse(state.save())

    def test_internal_type_error_is_not_converted_to_bad_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'technology.json'
            state = TechnologyState(path)
            state.set_status('rogue_6_outbuff_1', 'locked')
            with patch.object(TechnologyState, '_validate', side_effect=TypeError('internal defect')):
                with self.assertRaisesRegex(TypeError, 'internal defect'):
                    TechnologyState(path)
                with self.assertRaisesRegex(TypeError, 'internal defect'):
                    state.save()
