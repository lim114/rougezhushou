from tempfile import TemporaryDirectory
from pathlib import Path
from hashlib import sha256
import unittest
from rouge.player_note_library import NoteLibrary
from rouge.player_notes import NoteStore,content_key

class NoteLibraryTests(unittest.TestCase):
    def write_note(self,folder,content,text):
        store=NoteStore(folder);key=content_key(content);store.save(key,text,store.read(key)[1]);return key
    def test_exact_variant_notes_remain_separate_and_search_body(self):
        with TemporaryDirectory()as folder:
            library=NoteLibrary(folder)
            for identity,text in [('a','普通提醒'),('b','紧急机关')]:
                content={'kind':'battle','title':'同名关卡','variant_id':identity};self.write_note(folder,content,text);library.record(content)
            rows=library.rows();self.assertEqual(len(rows),2);self.assertEqual({r['content']['variant_id']for r in rows},{'a','b'})
            self.assertEqual([r['text']for r in library.rows('机关')],['紧急机关'])
    def test_old_notes_are_readable_without_guessing_a_context(self):
        with TemporaryDirectory()as folder:
            self.write_note(folder,{'kind':'event','title':'旧事件'},'以前的记录');rows=NoteLibrary(folder).rows()
            self.assertEqual(len(rows),1);self.assertTrue(rows[0]['legacy']);self.assertIsNone(rows[0]['content']);self.assertEqual(rows[0]['text'],'以前的记录')
    def test_corrupt_context_is_preserved_and_does_not_hide_legacy_text(self):
        with TemporaryDirectory()as folder:
            content={'kind':'event','title':'事件'};key=self.write_note(folder,content,'原始正文');path=Path(folder)/(sha256(key.encode()).hexdigest()+'.meta.json');path.write_bytes(b'{broken')
            library=NoteLibrary(folder);rows=library.rows();self.assertEqual(len(rows),1);self.assertTrue(rows[0]['legacy']);self.assertEqual(len(library.issues),1)
            with self.assertRaises(ValueError):library.record(content)
            self.assertEqual(path.read_bytes(),b'{broken');self.assertEqual(rows[0]['text'],'原始正文')
    def test_only_real_note_files_are_listed_without_index_only_phantoms(self):
        with TemporaryDirectory()as folder:
            library=NoteLibrary(folder);library.record({'kind':'event','title':'未写正文'})
            Path(folder,'random.md').write_text('其他文件','utf8');self.assertEqual(library.rows(),[])
    def test_one_note_index_update_does_not_remove_other_note_context(self):
        with TemporaryDirectory()as folder:
            library=NoteLibrary(folder)
            for title in('甲','乙'):
                content={'kind':'event','title':title};self.write_note(folder,content,title);library.record(content)
            library.record({'kind':'event','title':'甲'});self.assertEqual({r['title']for r in library.rows()},{'甲','乙'})

if __name__=='__main__':unittest.main()
