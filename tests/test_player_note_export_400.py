from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
import unittest,os
from rouge.player_note_export import export_note,suggested_name

class NoteExportTests(unittest.TestCase):
    def test_exact_utf8_markdown_and_no_clobber_by_default(self):
        with TemporaryDirectory()as folder:
            path=Path(folder)/'关卡.md';result=export_note('# 标题\n\n**原文**',path)
            self.assertEqual(path.read_bytes(),'# 标题\n\n**原文**'.encode());self.assertEqual(result['bytes'],len(path.read_bytes()))
            with self.assertRaises(FileExistsError):export_note('另一个版本',path)
            self.assertIn('原文',path.read_text('utf8'));export_note('显式覆盖',path,overwrite=True);self.assertEqual(path.read_text('utf8'),'显式覆盖')
    def test_failed_publication_preserves_existing_and_cleans_temporary_file(self):
        with TemporaryDirectory()as folder:
            path=Path(folder)/'关卡.md';path.write_text('旧内容','utf8')
            with patch('rouge.player_note_export.os.replace',side_effect=OSError('owned fixture')):
                with self.assertRaises(OSError):export_note('新内容',path,overwrite=True)
            self.assertEqual(path.read_text('utf8'),'旧内容');self.assertEqual(list(Path(folder).iterdir()),[path])
    def test_destination_created_during_export_is_not_overwritten(self):
        with TemporaryDirectory()as folder:
            path=Path(folder)/'关卡.txt';original=os.fsync
            def competing(fd):original(fd);path.write_text('其他窗口','utf8')
            with patch('rouge.player_note_export.os.fsync',side_effect=competing):
                with self.assertRaises(FileExistsError):export_note('助手内容',path)
            self.assertEqual(path.read_text('utf8'),'其他窗口')
    def test_cleanup_error_after_publication_reports_known_saved_file(self):
        with TemporaryDirectory()as folder:
            path=Path(folder)/'关卡.md';unlink=Path.unlink
            def fail_temp(self,*args,**kwargs):
                if self.name.startswith('.note-export-'):raise PermissionError('owned fixture')
                return unlink(self,*args,**kwargs)
            with patch.object(Path,'unlink',fail_temp):result=export_note('确已导出',path)
            self.assertTrue(result['warning']);self.assertEqual(path.read_text('utf8'),'确已导出')
    def test_filename_truncation_reserved_names_and_type_validation(self):
        for title in('CON','PRN.txt','COM1','LPT9','abc<>:/\\|?*','x'*79+' .more','\ud800'):
            name=suggested_name(title);stem=name[:-3];self.assertTrue(stem);self.assertFalse(stem.endswith((' ','.')));self.assertNotIn('\ud800',name)
        with TemporaryDirectory()as folder:
            path=Path(folder)/'wrong.json'
            with self.assertRaises(ValueError):export_note('正文',path)
            self.assertFalse(path.exists())

if __name__=='__main__':unittest.main()
