import tempfile
import unittest
from pathlib import Path
from rouge.run_state import _validate_saved_containers
from rouge.player_team import crew_rows
from rouge.player_history_store import RunHistoryStore
from rouge.relic_quantities import kettle_copies, KETTLE
from rouge.player_shop_memory import recorded_shops


class RunAndArchiveBoundariesTests(unittest.TestCase):
    def test_active_run_rejects_invalid_member_before_installation(self):
        with self.assertRaises(ValueError):
            _validate_saved_containers({'operators': {'mechanist': None}})
        with self.assertRaises(AttributeError):
            crew_rows({'operators': {'mechanist': None}})

    def test_archive_preserves_opaque_items_and_consumers_qualify_them(self):
        state = {'id': 'isolated-contract-fixture', 'operators': {},
                 'relics': {KETTLE: {}, 'invalid': None},
                 'history': [None, {'kind': 'unrelated'}]}
        with tempfile.TemporaryDirectory() as folder:
            store = RunHistoryStore(Path(folder))
            path = store.archive(state)
            restored = store.read(path)['state']
        self.assertEqual(restored, state)
        self.assertIsNone(kettle_copies(restored))
        self.assertEqual(recorded_shops(restored), [])
