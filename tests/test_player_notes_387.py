import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from rouge.player_notes import NoteStore,content_key
class Notes(unittest.TestCase):
 def test_explicit_local_markdown(self):
  with TemporaryDirectory()as f:
   store=NoteStore(f);text,digest=store.read('a');self.assertEqual(text,'');self.assertEqual(list(Path(f).iterdir()),[])
   store.save('a','# 注意\n保留第二阶段',digest);self.assertEqual(store.read('a')[0],'# 注意\n保留第二阶段')
 def test_external_change_not_overwritten(self):
  with TemporaryDirectory()as f:
   store=NoteStore(f);_,digest=store.read('a');store.path('a').write_text('外部编辑',encoding='utf8')
   with self.assertRaises(ValueError):store.save('a','旧窗口',digest)
   self.assertEqual(store.read('a')[0],'外部编辑')
 def test_exact_variants_separate(self):self.assertNotEqual(content_key({'title':'同名','variant_id':'a'}),content_key({'title':'同名','variant_id':'b'}))
 def test_missing_title_not_bound(self):self.assertIsNone(content_key({}))
