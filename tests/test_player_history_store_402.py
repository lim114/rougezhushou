from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import json
import math,struct
import unittest
from rouge.player_history_store import RunHistoryStore, archive_before_manual_reset

def state(identity='fixture-run'):
    return {'id':identity,'operators':{},'relics':{},'maps':{},'resources':{},'config':{},'history':[],'last_read':None}

class HistoryStoreTests(unittest.TestCase):
    def test_manual_archive_reads_back_without_reset_or_mutation(self):
        with TemporaryDirectory()as tmp:
            saved=state();saved['history']=[{'at':2,'kind':'map_confirmed'}];before=deepcopy(saved)
            store=RunHistoryStore(Path(tmp)/'history');path=archive_before_manual_reset(SimpleNamespace(state=saved),store.folder)
            self.assertEqual(store.read(path)['state'],before);self.assertEqual(saved,before)
            self.assertIsNone(store.read(path)['outcome']);self.assertEqual(store.records()[1],[])

    def test_empty_initial_state_is_not_an_archived_game(self):
        with TemporaryDirectory()as tmp:
            store=RunHistoryStore(Path(tmp)/'history');self.assertIsNone(store.archive(state()));self.assertFalse(store.folder.exists())

    def test_same_state_deduplicates_and_versions_of_one_run_count_once(self):
        with TemporaryDirectory()as tmp:
            saved=state();saved['last_read']=2;store=RunHistoryStore(tmp)
            with patch('rouge.player_history_store.time.time',return_value=5):first=store.archive(saved)
            self.assertEqual(store.archive(saved),first)
            saved['last_read']=3
            with patch('rouge.player_history_store.time.time',return_value=8):second=store.archive(saved)
            records,issues=store.records();self.assertEqual(len(records),1);self.assertEqual(records[0]['state']['last_read'],3)
            self.assertNotEqual(first,second);self.assertTrue(first.is_file());self.assertFalse(issues)

    def test_failed_atomic_publication_never_changes_current_run(self):
        with TemporaryDirectory()as tmp:
            saved=state();saved['last_read']=1;before=deepcopy(saved)
            with patch('rouge.player_history_store.os.link',side_effect=OSError('no atomic links')):
                with self.assertRaises(OSError):archive_before_manual_reset(SimpleNamespace(state=saved),tmp)
            self.assertEqual(saved,before);self.assertEqual(list(Path(tmp).glob('*.json')),[])

    def test_damaged_history_stays_on_disk_and_does_not_hide_good_history(self):
        with TemporaryDirectory()as tmp:
            saved=state();saved['last_read']=1;store=RunHistoryStore(tmp);good=store.archive(saved)
            bad=Path(tmp)/'bad.json';bad.write_bytes(b'broken')
            records,issues=store.records();self.assertEqual(len(records),1);self.assertEqual(len(issues),1)
            self.assertEqual(bad.read_bytes(),b'broken');self.assertTrue(good.is_file())

    def test_content_tamper_and_outside_path_cannot_be_installed(self):
        with TemporaryDirectory()as tmp:
            store=RunHistoryStore(Path(tmp)/'history');saved=state();saved['last_read']=1;path=store.archive(saved)
            raw=json.loads(path.read_bytes());raw['state_payload']=['null'];path.write_text(json.dumps(raw),'utf8')
            with self.assertRaises(ValueError):store.read(path)
            with self.assertRaises(ValueError):store.read(Path(tmp)/'outside.json')

    def test_unreadable_or_failed_session_never_starts_new_archive_io(self):
        saved=state();saved['last_read']=1
        for flags in({'save_issue':'failed'},{'preserve_unreadable':True}):
            run=SimpleNamespace(state=saved,**flags)
            with patch.object(RunHistoryStore,'archive',side_effect=AssertionError('new IO forbidden')):
                self.assertIsNone(archive_before_manual_reset(run,'unused-history'))

    def test_opaque_nonfinite_numbers_surrogates_and_types_round_trip_exactly(self):
        with TemporaryDirectory()as tmp:
            saved=state();saved['last_read']=1;saved['opaque']={'paired':'\ud800\udc00','astral':'\U00010000','float':-0.0,'nan':float('nan'),'inf':float('inf'),'tuple':(1,True,None)}
            store=RunHistoryStore(tmp);path=store.archive(saved);restored=store.read(path)['state']['opaque']
            self.assertEqual([ord(c)for c in restored['paired']],[0xd800,0xdc00]);self.assertEqual(restored['astral'],'\U00010000')
            self.assertEqual(struct.pack('>d',restored['float']),struct.pack('>d',-0.0));self.assertTrue(math.isnan(restored['nan']));self.assertEqual(restored['inf'],float('inf'))
            self.assertEqual(restored['tuple'],(1,True,None));self.assertIs(type(restored['tuple']),tuple);self.assertIs(type(restored['tuple'][1]),bool)
            self.assertEqual(json.loads(path.read_text('ascii'))['state_encoding'],'typed-json-v1')

    def test_unsupported_objects_refuse_before_creating_archive_folder(self):
        with TemporaryDirectory()as tmp:
            saved=state();saved['last_read']=1;saved['opaque']=object();folder=Path(tmp)/'history'
            with self.assertRaises(ValueError):RunHistoryStore(folder).archive(saved)
            self.assertFalse(folder.exists())

if __name__=='__main__':unittest.main()
