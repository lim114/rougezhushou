"""Validate raw statistics once per entry; preserve accepted snapshots."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import public_node_statistics as model, player_map_reference as maps
from rouge.node_statistics_source import NodeStatisticsSource
from tests.test_node_card_source_review import public_example


class StatisticsEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_file_startup_validates_once_and_accept_keeps_one_validation(self):
        with TemporaryDirectory()as folder:
            path=Path(folder)/'nodes.json';path.write_text(json.dumps(public_example()),encoding='utf-8')
            with patch.object(model,'validate',wraps=model.validate)as validate:
                source=NodeStatisticsSource(path)
                self.assertEqual(validate.call_count,1)
                self.assertEqual(source.index.rows('0',2)[0]['frequency'],.7)
                validate.reset_mock();source.accept(public_example(80))
                self.assertEqual(validate.call_count,1)
                self.assertEqual(source.index.rows('0',2)[0]['frequency'],.8)

    def test_default_refresh_does_not_reuse_second_hidden_cache(self):
        maps.default_frequencies.cache_clear();self.addCleanup(maps.default_frequencies.cache_clear)
        with patch.object(model,'load',side_effect=[public_example(),public_example(80)])as load:
            self.assertEqual(maps.default_frequencies().rows('0',2)[0]['frequency'],.7)
            self.assertEqual(maps.default_frequencies().rows('0',2)[0]['frequency'],.7)
            maps.default_frequencies.cache_clear()
            self.assertEqual(maps.default_frequencies().rows('0',2)[0]['frequency'],.8)
            self.assertEqual(load.call_count,2)

    def test_raw_constructor_and_empty_index_contract_are_unchanged(self):
        with patch.object(model,'validate',wraps=model.validate)as validate:
            index=model.FrequencyIndex(public_example())
            self.assertEqual(validate.call_count,1)
            self.assertEqual(index.rows('0',2)[0]['frequency'],.7)
        for index in (model.FrequencyIndex(),model.FrequencyIndex(None)):
            self.assertIsNone(index.identity);self.assertEqual(index.rows('0',2),[])
        bad=public_example();bad['metadata']['sampleCount']+=1
        with self.assertRaises(ValueError):model.FrequencyIndex(bad)

    def test_invalid_accept_never_changes_cache_snapshot_or_emits_update(self):
        with TemporaryDirectory()as folder:
            path=Path(folder)/'nodes.json';path.write_text(json.dumps(public_example()),encoding='utf-8')
            source=NodeStatisticsSource(path);events=[];source.changed.connect(lambda:events.append(True))
            original=path.read_bytes();identity=source.index.identity
            for value in (None,[],True,12,'missing',{}):
                with self.subTest(value=value),self.assertRaises(ValueError):source.accept(value)
                self.assertEqual(path.read_bytes(),original);self.assertEqual(source.index.identity,identity)
            self.assertEqual(events,[])


if __name__=='__main__':unittest.main()
