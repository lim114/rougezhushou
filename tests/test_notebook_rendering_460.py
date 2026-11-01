from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QTextTable
from PySide6.QtWidgets import QApplication
from rouge.player_note_preview import NotePreview
from rouge.player_note_library import NoteLibrary, NoteLibraryPanel
from rouge.player_notes import NoteStore, content_key


class NotebookRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def preview(self,text):
        p=NotePreview();self.addCleanup(p.close);p.resize(600,250);p.show();p.read_markdown(text);self.qt.processEvents();return p

    def test_entered_single_line_breaks_remain_separate_readable_lines(self):
        text='先处理左侧敌人\n留一个技能应对第二波\n最后回收部署费用'
        p=self.preview(text)
        self.assertEqual(p.toPlainText().splitlines(),text.splitlines())
        ys=[]
        for line in text.splitlines():
            c=p.document().find(line);self.assertFalse(c.isNull());ys.append(p.cursorRect(c).top())
        self.assertTrue(ys[0]<ys[1]<ys[2])

    def test_markdown_structure_and_literal_code_survive_line_preserving_render(self):
        p=self.preview('# 关卡提醒\n\n**优先目标**\n下一行\n\n- 普通列表\n- [x] 已处理\n- [ ] 待处理\n\n```text\n# 不是标题\n  保留缩进\n```\n\n| 敌人 | 注意事项 |\n| --- | --- |\n| 甲 | 远程 |\n\n~~过期提醒~~')
        plain=p.toPlainText();self.assertIn('☑ 已处理',plain);self.assertIn('☐ 待处理',plain)
        self.assertIn('# 不是标题\n  保留缩进',plain)
        self.assertEqual(p.document().begin().blockFormat().headingLevel(),1)
        bold=p.document().find('优先目标');self.assertGreater(bold.charFormat().fontWeight(),400)
        strike=p.document().find('过期提醒');self.assertTrue(strike.charFormat().fontStrikeOut())
        self.assertTrue(any(isinstance(f,QTextTable)for f in p.document().rootFrame().childFrames()))

    def test_unchanged_refresh_and_same_note_update_keep_reading_selection(self):
        text='\n'.join('第'+str(i)+'行提醒'for i in range(90));p=self.preview(text)
        c=p.document().find('第15行提醒');p.setTextCursor(c);p.verticalScrollBar().setValue(150)
        selected=p.textCursor().selectedText();offset=p.verticalScrollBar().value();position=p.textCursor().position()
        p.read_markdown(text);self.assertEqual(p.textCursor().selectedText(),selected);self.assertEqual(p.verticalScrollBar().value(),offset)
        p.read_markdown(text+'\n补充提醒');self.qt.processEvents()
        self.assertEqual(p.textCursor().position(),position);self.assertEqual(p.textCursor().selectedText(),selected);self.assertEqual(p.verticalScrollBar().value(),offset)

    def test_library_previews_markdown_and_resets_reading_only_when_note_changes(self):
        with TemporaryDirectory()as folder:
            store=NoteStore(folder);library=NoteLibrary(folder)
            for name in ['甲','乙']:
                context={'kind':'battle','title':name,'variant_id':'public-'+name};key=content_key(context)
                store.save(key,'# 提醒\n\n'+'\n'.join('第'+str(i)+'行'for i in range(80)),store.read(key)[1]);library.record(context)
            p=NoteLibraryPanel(folder);self.addCleanup(p.close);p.resize(800,430);p.show();p.entries.setCurrentRow(0);self.qt.processEvents()
            self.assertIsInstance(p.detail,NotePreview);self.assertEqual(p.detail.document().begin().blockFormat().headingLevel(),1)
            p.detail.verticalScrollBar().setValue(120);offset=p.detail.verticalScrollBar().value();self.assertGreater(offset,0)
            selected=p.reference_context();p.refresh();self.qt.processEvents();self.assertEqual(p.reference_context(),selected);self.assertEqual(p.detail.verticalScrollBar().value(),offset)
            p.entries.setCurrentRow(1);self.qt.processEvents();self.assertEqual(p.detail.verticalScrollBar().value(),0)
            for row in library.rows():self.assertTrue(row['text'].startswith('# 提醒\n\n'))
