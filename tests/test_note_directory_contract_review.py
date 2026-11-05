"""Approved D35-D37 boundaries and blank-query work in the note directory."""
import cProfile
import json
from pathlib import Path
import pstats
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from rouge.player_note_library import NoteLibrary
from rouge.player_notes import NoteStore, content_key


class NoteDirectoryContractTests(unittest.TestCase):
    def setUp(self):
        self.folder = Path(self.enterContext(TemporaryDirectory()))/'notes'
        self.library = NoteLibrary(self.folder)
        self.content = {'kind':'event','title':'测试场景','event_id':'owned-fixture'}
        self.library.record(self.content)
        self.tag = next(self.folder.glob('*.meta.json'))

    def test_linked_tag_is_not_read_or_overwritten(self):
        original = self.tag.read_bytes()
        with patch.object(Path, 'is_symlink', autospec=True, side_effect=lambda p:p==self.tag):
            self.assertEqual(self.library.records(), {})
            self.assertEqual(self.library.issues, [self.tag.name])
            with self.assertRaisesRegex(ValueError, '位置为链接'):
                self.library.record(self.content)
        self.assertEqual(self.tag.read_bytes(), original)

    def test_linked_parent_rejects_both_read_and_write(self):
        original = self.tag.read_bytes()
        parent = self.folder.parent
        with patch.object(Path, 'is_symlink', autospec=True, side_effect=lambda p:p==parent):
            with self.assertRaisesRegex(ValueError, '目录为链接'):
                self.library.records()
            with self.assertRaisesRegex(ValueError, '目录为链接'):
                self.library.record(self.content)
        self.assertEqual(self.tag.read_bytes(), original)

    def test_bad_or_different_existing_tag_keeps_original_bytes(self):
        cases = ['not json', '[]', json.dumps({'schema':'other','content':self.content}),
                 json.dumps({'schema':'player-note-context-v1','content':[]}),
                 json.dumps({'schema':'player-note-context-v1','content':{**self.content,'event_id':'other'}})]
        for raw in cases:
            with self.subTest(raw=raw):
                self.tag.write_text(raw,encoding='utf-8')
                original = self.tag.read_bytes()
                with self.assertRaises(ValueError): self.library.record(self.content)
                self.assertEqual(self.tag.read_bytes(), original)

    def test_same_identity_tag_can_be_updated(self):
        changed = {**self.content, 'title':'更新标题'}
        self.library.record(changed)
        self.assertEqual(self.library.records()[content_key(changed)]['content'], changed)

    def test_directory_path_that_is_a_file_reports_error(self):
        path = self.folder.parent/'not-a-directory'; path.write_text('原文件',encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '笔记目录不可用'):
            NoteLibrary(path).records()
        self.assertEqual(path.read_text(encoding='utf-8'), '原文件')
        self.assertEqual(NoteLibrary(self.folder.parent/'missing').records(), {})

    def test_blank_search_avoids_per_body_casefold_and_keeps_search_results(self):
        store = NoteStore(self.folder)
        for i, text in enumerate(('Alpha正文\n'*100, 'Beta正文\n'*100)):
            content = {**self.content, 'event_id':f'item-{i}'}
            key = content_key(content); store.save(key,text,store.read(key)[1]);self.library.record(content)
        profile = cProfile.Profile(); profile.enable()
        rows = self.library.rows('  ')
        profile.disable()
        self.assertEqual(len(rows), 2)
        folds = sum(data[1] for code,data in pstats.Stats(profile).stats.items() if code[2]=="<method 'casefold' of 'str' objects>")
        self.assertEqual(folds, 1, 'Blank search should normalize only its query, not every note body.')
        self.assertEqual([row['text'] for row in self.library.rows('aLPHa')], ['Alpha正文\n'*100])
        self.assertEqual(self.library.rows('找不到的内容'), [])


if __name__ == '__main__': unittest.main()
