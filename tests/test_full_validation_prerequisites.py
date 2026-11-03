"""A missing link privilege is disclosed, never a pass or a blanket error mask."""
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.verify_full_available import AvailableResult
from tests import test_persistence_initial_install as initial_fixture
from tests import test_persistence_temporary_no_clobber_261 as temporary_fixture


def run_case(case):
    return unittest.TextTestRunner(stream=io.StringIO(), resultclass=AvailableResult).run(case)


class FullValidationPrerequisiteTests(unittest.TestCase):
    def test_original_relative_link_case_is_attempted_and_not_counted_passed_when_blocked(self):
        result = run_case(initial_fixture.InitialInstallTests(
            'test_manual_reset_retains_relative_link_text_and_target_resolution'))
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])
        if result.native_symlink_prerequisite.get('available') is False:
            self.assertEqual(len(result.unavailable), 1)
            self.assertEqual(result.passed_count, 0)
            row = result.unavailable[0]
            self.assertEqual(row['winerror'], 1314)
            self.assertTrue(row['actual_test_creation_attempted'])
            self.assertIn('os.symlink', row['traceback'])
            self.assertFalse(row['counted_as_passed'])
        else:
            self.assertEqual(result.unavailable, [])
            self.assertEqual(result.passed_count, 1)

    def test_partial_subtests_keep_original_cases_and_parent_unavailable(self):
        result = run_case(temporary_fixture.TemporaryRecordNoClobberTests(
            'test_private_directory_name_collision_never_enters_an_old_namespace'))
        self.assertEqual((result.testsRun, len(result.errors), len(result.failures)), (1, 0, 0))
        if result.native_symlink_prerequisite.get('available') is False:
            self.assertEqual(len(result.unavailable), 4)
            self.assertEqual(len(result.unavailable_parents), 1)
            self.assertEqual(result.passed_count, 0)
            self.assertTrue(all(r['actual_test_creation_attempted'] for r in result.unavailable))
        else:
            self.assertEqual(result.unavailable, [])
            self.assertEqual(result.passed_count, 1)

    def test_actual_symlink_error_outside_registered_prerequisite_stays_error(self):
        class UnregisteredCase(unittest.TestCase):
            def runTest(self):
                with tempfile.TemporaryDirectory(prefix='rouge-public-unregistered-link-') as name:
                    folder = Path(name).resolve()
                    assert folder.parent == Path(tempfile.gettempdir()).resolve()
                    (folder / 'public-link').symlink_to('public-absent-target')
        result = run_case(UnregisteredCase())
        self.assertEqual(result.unavailable, [])
        if result.native_symlink_prerequisite.get('available') is False:
            self.assertEqual(len(result.errors), 1)
            self.assertEqual(result.passed_count, 0)
        else:
            self.assertEqual(result.errors, [])
            self.assertEqual(result.passed_count, 1)

    def test_same_winerror_without_actual_symlink_frame_cannot_be_disclosed_as_unavailable(self):
        error = OSError(22, 'public setup error, not a symlink creation')
        error.winerror = 1314
        method = 'test_manual_reset_retains_relative_link_text_and_target_resolution'
        with patch.object(initial_fixture.InitialInstallTests, method, side_effect=error):
            result = run_case(initial_fixture.InitialInstallTests(method))
        self.assertEqual((len(result.errors), result.passed_count), (1, 0))
        self.assertEqual(result.unavailable, [])

    def test_generic_permission_error_with_similar_message_remains_error(self):
        method = 'test_manual_reset_retains_relative_link_text_and_target_resolution'
        with patch.object(initial_fixture.InitialInstallTests, method,
                          side_effect=PermissionError(13, '[WinError 1314] public similar message')):
            result = run_case(initial_fixture.InitialInstallTests(method))
        self.assertEqual((len(result.errors), result.passed_count), (1, 0))
        self.assertEqual(result.unavailable, [])


if __name__ == '__main__':
    unittest.main()
