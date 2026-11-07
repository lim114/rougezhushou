import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from rouge import timing


class RequiredTimingProfilesTests(unittest.TestCase):
    def tearDown(self):
        timing.profiles.cache_clear()

    def test_missing_required_file_is_not_cached_as_empty_profiles(self):
        timing.profiles.cache_clear()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(timing, '__file__', str(root / 'timing.py')):
                with self.assertRaises(FileNotFoundError) as error:
                    timing.profiles()
                self.assertIn('timing-profiles.json', str(error.exception))
                self.assertEqual(timing.profiles.cache_info().currsize, 0)
                (root / 'data').mkdir()
                expected = {'operators': {'fixture': {'source': 'isolated'}}}
                (root / 'data' / 'timing-profiles.json').write_text(json.dumps(expected), encoding='utf-8')
                self.assertEqual(timing.profiles(), expected)

    def test_installed_profiles_match_packaged_file(self):
        timing.profiles.cache_clear()
        path = Path(timing.__file__).with_name('data') / 'timing-profiles.json'
        expected = json.loads(path.read_text(encoding='utf-8'))
        self.assertTrue(expected['operators'])
        self.assertEqual(timing.profiles(), expected)
