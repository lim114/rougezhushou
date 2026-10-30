"""Notebook hierarchy and actual shared-editor ownership, without user state."""
from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
from unittest.mock import patch
import json,unittest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QWidget
from rouge.run_state import RunState
from rouge.player_notes import NotesDialog,content_key
from rouge.player_inline_notes import InlineNotesPanel
from rouge.player_note_scopes import scope,parents,scope_parts
from rouge.player_note_library import NoteLibrary


def rows():
    return [{'context':{'kind':'reference-stage','title':'同名关卡','event_id':identity,
             'variant_id':json.dumps(['pinned-public-version',identity])},
             'label':identity,'floors':floors,'nodes':nodes}
            for identity,floors,nodes in [('normal',['floor1'],['普通作战']),('many',['floor1','floor2'],['普通作战','紧急作战'])]]


class ScopeTests(unittest.TestCase):
    def test_parent_hierarchy_uses_only_selected_or_unique_classification(self):
        r=rows();c=r[0]['context']
        self.assertEqual(parents(c,r),[scope(r),scope(r,'floor1'),scope(r,'floor1','普通作战')])
        multi=r[1]['context'];self.assertEqual(parents(multi,r),[scope(r)])
        self.assertEqual(parents(multi,r,'floor2','紧急作战'),[scope(r),scope(r,'floor2'),scope(r,'floor2','紧急作战')])
        self.assertEqual(parents({'kind':'battle','title':c['title']},r),[])

    def test_generic_scope_keys_separate_versions_and_detailed_variants(self):
        r=rows();a=scope(r,'floor1','普通作战');b=scope(r,'floor2','普通作战');new=deepcopy(r);new[0]['context']['variant_id']=json.dumps(['other-version','normal'])
        self.assertEqual(len({content_key(a),content_key(b),content_key(scope(new,'floor1','普通作战')),content_key(r[0]['context'])}),4)
        self.assertEqual(parents(a,r),[scope(r),scope(r,'floor1')]);self.assertEqual(parents(scope(r),r),[])

    def test_stale_or_malformed_generic_scope_has_no_borrowed_parents(self):
        r=rows();a=scope(r,'floor1');bad=[{**a,'variant_id':'not-json'},{**a,'variant_id':'[]'},{**a,'variant_id':json.dumps(['pinned-public-version',[],None])},{**a,'title':'incorrect title'}]
        for c in bad:self.assertIsNone(scope_parts(c,r));self.assertEqual(parents(c,r),[])
        other=deepcopy(r);other[0]['context']['variant_id']=json.dumps(['other-version','normal']);self.assertEqual(parents(a,other),[])


class InlineNotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def setUp(self):
        self.temp=TemporaryDirectory();self.root=Path(self.temp.name);self.addCleanup(self.temp.cleanup)
        self.catalogue=rows();self.patch=patch('rouge.player_note_selector.catalogue_snapshot',return_value={'rows':self.catalogue,'unavailable':[]});self.patch.start();self.addCleanup(self.patch.stop)
        self.run=RunState(self.root/'run.json');self.editor=NotesDialog(self.root/'notes');self.editor.autosave.setChecked(False)
        self.panel=InlineNotesPanel(self.run,self.editor);self.panel.resize(850,650);self.panel.show();self.qt.processEvents()
        self.addCleanup(self.cleanup)
    def cleanup(self):
        self.panel.timer.stop();self.editor.discard();self.editor.autosave_timer.stop();self.panel.close();self.panel.deleteLater();self.qt.processEvents()
    def test_existing_editor_embedded_once_and_no_second_store(self):
        target={'kind':'battle','title':'隔离战斗','variant_id':'normal'};self.run.state['last_node_content']=target;self.panel.refresh(force=True);self.panel.edit.click();self.qt.processEvents()
        self.assertIs(self.panel.store,self.editor.store);self.assertFalse(self.editor.isWindow());self.assertIs(self.editor.window(),self.panel)
        self.assertTrue(self.editor.isVisible());self.assertEqual(self.editor.key,content_key(target));self.assertIs(self.panel.stack.currentWidget(),self.editor)
        self.panel.edit.click();self.assertIs(self.panel.stack.currentWidget(),self.panel.preview)

    def test_generic_floor_node_and_topic_can_be_edited_and_reopened_from_library(self):
        p=self.panel
        p.selector.floor.setCurrentIndex(p.selector.floor.findData('floor1'));p.selector.floor.activated.emit(p.selector.floor.currentIndex())
        floor=scope(self.catalogue,'floor1');self.assertEqual(p.context,floor);self.assertFalse(p.follow.isChecked());p.edit.click();self.editor.editor.setPlainText('第一层通用提醒');self.assertTrue(self.editor.save())
        topic=scope(self.catalogue);self.assertTrue(p.open_scope(topic));self.editor.editor.setPlainText('主题通用提醒');self.assertTrue(self.editor.save())
        library=NoteLibrary(self.editor.store.folder);saved=library.rows('第一层');self.assertEqual(len(saved),1);self.assertEqual(saved[0]['content'],floor)
        p.select_context(saved[0]['content']);self.assertEqual(self.editor.editor.toPlainText(),'第一层通用提醒');self.assertEqual(p.selector.floor.currentData(),'floor1')
        self.assertFalse(self.run.state.get('last_node_content'));self.assertEqual(self.editor.store.read(content_key(topic))[0],'主题通用提醒')

    def test_parent_cards_are_read_only_and_do_not_create_or_overwrite_notes(self):
        p=self.panel;floor=scope(self.catalogue,'floor1');node=scope(self.catalogue,'floor1','普通作战');topic=scope(self.catalogue)
        for context,text in((topic,'# 主题提醒'),(floor,'# 第一层说明')):self.editor.store.save(content_key(context),text,self.editor.store.read(content_key(context))[1])
        p.select_context(node);before={f.name:f.read_bytes()for f in self.editor.store.folder.iterdir()};state=deepcopy(self.run.state)
        p.parent_toggle.setChecked(True);self.qt.processEvents();self.assertEqual(len(p.parent_views),2);self.assertTrue(all(v.isReadOnly()for v in p.parent_views));self.assertIn('主题提醒',p.parent_views[0].toPlainText());self.assertIn('第一层',p.parent_views[1].toPlainText())
        self.assertEqual(before,{f.name:f.read_bytes()for f in self.editor.store.folder.iterdir()});self.assertEqual(self.run.state,state)
        p.parent_toggle.setChecked(False);self.assertFalse(p.parent_area.isVisible())

    def test_manual_draft_blocks_navigation_and_return_until_saved_or_discarded(self):
        p=self.panel;a=scope(self.catalogue,'floor1');b=scope(self.catalogue,'floor2');p.select_context(a);p.edit.click();self.editor.editor.setPlainText('保留草稿')
        p.select_context(b);self.assertEqual(p.context,a);self.assertEqual(self.editor.key,content_key(a));self.assertEqual(self.editor.editor.toPlainText(),'保留草稿')
        p.edit.click();self.assertIs(p.stack.currentWidget(),self.editor);self.assertTrue(self.editor.dirty)
        self.assertTrue(self.editor.save());p.select_context(b);self.assertEqual(p.context,b);self.assertEqual(self.editor.key,content_key(b));self.assertEqual(self.editor.store.read(content_key(a))[0],'保留草稿')

    def test_automatic_save_completes_exact_draft_before_explicit_switch(self):
        p=self.panel;a=scope(self.catalogue,'floor1');b=scope(self.catalogue,'floor2');p.select_context(a);p.edit.click();self.editor.autosave.setChecked(True);self.editor.editor.setPlainText('原范围的内容');p.select_context(b)
        self.assertEqual(p.context,b);self.assertEqual(self.editor.store.read(content_key(a))[0],'原范围的内容');self.assertFalse(self.editor.dirty);self.assertFalse(self.editor.autosave_timer.isActive())

    def test_external_conflict_blocks_close_and_preserves_both_copies(self):
        from rouge.player_compact import NotesPopover
        p=self.panel;a=scope(self.catalogue,'floor1');p.select_context(a);p.edit.click();self.editor.autosave.setChecked(True);self.editor.editor.setPlainText('当前草稿');self.editor.store.folder.mkdir(exist_ok=True);self.editor.store.path(self.editor.key).write_text('外部保存','utf8')
        owner=QWidget();popup=NotesPopover('隔离备忘录',p,owner);popup.panel=p;popup.show();self.qt.processEvents();self.assertFalse(popup.close())
        self.assertTrue(self.editor.dirty);self.assertFalse(self.editor.autosave.isChecked());self.assertEqual(self.editor.editor.toPlainText(),'当前草稿');self.assertEqual(self.editor.store.read(self.editor.key)[0],'外部保存')
        self.editor.discard();self.assertTrue(popup.close());owner.deleteLater()

    def test_follow_and_new_run_keep_unsaved_editor_with_visible_owner(self):
        p=self.panel;a={'kind':'battle','title':'第一关','variant_id':'a'};b={**a,'title':'第二关','variant_id':'b'};self.run.state['last_node_content']=a;p.refresh(force=True);p.edit.click();self.editor.editor.setPlainText('未保存正文')
        self.run.state['last_node_content']=b;p.refresh(force=True);self.assertEqual(p.context,b);self.assertEqual(self.editor.key,content_key(a));self.assertIn('第一关',p.status.text())
        self.run.reset(save=False);p.refresh(force=True);self.assertIsNone(p.context);self.assertTrue(self.editor.dirty);self.assertTrue(p.edit.isEnabled());self.assertEqual(self.editor.editor.toPlainText(),'未保存正文')

    def test_escape_obeys_draft_rule_instead_of_hiding_the_embedded_editor(self):
        p=self.panel;p.select_context(scope(self.catalogue));p.edit.click();self.editor.editor.setPlainText('不能静默消失');self.editor.editor.setFocus();QTest.keyClick(self.editor,Qt.Key.Key_Escape);self.qt.processEvents()
        self.assertTrue(self.editor.isVisible());self.assertTrue(self.editor.dirty);self.assertEqual(self.editor.editor.toPlainText(),'不能静默消失')

    def test_parent_read_failure_is_visible_and_does_not_erase_child(self):
        p=self.panel;a=scope(self.catalogue,'floor1','普通作战');p.select_context(a);p.edit.click();self.editor.editor.setPlainText('子范围草稿');self.editor.save()
        original=self.editor.store.read
        def read(key):
            if key==content_key(scope(self.catalogue)):raise PermissionError('isolated failure')
            return original(key)
        with patch.object(self.editor.store,'read',side_effect=read):p.parent_toggle.setChecked(True);self.assertIn('权限',p.parent_views[0].toPlainText())
        self.assertEqual(self.editor.editor.toPlainText(),'子范围草稿');self.assertEqual(original(content_key(a))[0],'子范围草稿')

    def test_unrelated_refreshes_reuse_note_until_saved_file_changes(self):
        p=self.panel;a=scope(self.catalogue,'floor1');p.select_context(a);p.edit.click();self.editor.editor.setPlainText('既有内容');self.editor.save();p.refresh(force=True)
        with patch.object(self.editor.store,'read',wraps=self.editor.store.read)as read:
            for _ in range(30):p.refresh()
            self.assertEqual(read.call_count,0)
            self.editor.store.path(self.editor.key).write_text('外部新保存的内容','utf8');p._next_check=0;p.refresh()
            self.assertEqual(read.call_count,2)
        self.assertEqual(self.editor.editor.toPlainText(),'外部新保存的内容');self.assertFalse(self.editor.dirty)

    def test_parent_navigation_updates_all_scope_pickers(self):
        p=self.panel;p.select_context(scope(self.catalogue,'floor1','普通作战'));p.edit.click();self.assertTrue(p.open_scope(scope(self.catalogue)))
        self.assertIsNone(p.selector.floor.currentData());self.assertIsNone(p.selector.node.currentData());self.assertEqual(p.selector.scene.currentData(),scope(self.catalogue))

    def test_saved_scope_from_other_reference_cannot_rebind_shared_editor(self):
        p=self.panel;a=scope(self.catalogue,'floor1');self.assertTrue(p.open_for_context(a));key=self.editor.key
        old=deepcopy(self.catalogue);old[0]['context']['variant_id']=json.dumps(['other-version','normal'])
        self.assertFalse(p.open_for_context(scope(old,'floor1')));self.assertEqual(self.editor.key,key);self.assertEqual(p.context,a)

    def test_explicit_saved_old_scope_remains_editable_under_original_identity(self):
        p=self.panel;old=deepcopy(self.catalogue);old[0]['context']['variant_id']=json.dumps(['other-version','normal']);context=scope(old,'floor1');key=content_key(context)
        self.editor.store.save(key,'旧资料下的私人笔记',self.editor.store.read(key)[1]);self.assertTrue(p.open_for_context(context,allow_archived=True));self.assertEqual(self.editor.key,key)
        self.assertEqual(self.editor.editor.toPlainText(),'旧资料下的私人笔记');self.assertIn('原分类暂不可核对',p.scene.text());p.parent_toggle.setChecked(True);self.assertEqual(p.parent_views,[])
        self.editor.editor.setPlainText('仍按原身份保存');self.assertTrue(self.editor.save());self.assertEqual(self.editor.store.read(key)[0],'仍按原身份保存')

    def test_invalid_parent_transition_hides_old_cards_before_deferred_delete(self):
        p=self.panel;p.select_context(scope(self.catalogue,'floor1','普通作战'));p.parent_toggle.setChecked(True);self.qt.processEvents();prior=list(p.parent_views);self.assertTrue(all(v.isVisible()for v in prior))
        old=deepcopy(self.catalogue);old[0]['context']['variant_id']=json.dumps(['other-version','normal']);context=scope(old,'floor1');key=content_key(context);self.editor.store.save(key,'旧资料笔记',self.editor.store.read(key)[1])
        self.assertTrue(p.open_for_context(context,allow_archived=True));self.assertEqual(p.parent_views,[]);self.assertTrue(all(v.isHidden()for v in prior))

    def test_external_exact_note_updates_picker_and_does_not_claim_autosave_disabled(self):
        p=self.panel;p.select_context(scope(self.catalogue,'floor2','紧急作战'));target=self.catalogue[0]['context']
        with patch('rouge.player_reference_notes.reference_target',return_value=('stages','normal')):self.assertTrue(p.open_for_context(target))
        self.assertEqual(p.selector.floor.currentData(),'floor1');self.assertEqual(p.selector.node.currentData(),'普通作战');self.assertEqual(p.selector.scene.currentData(),target)
        p.refresh(force=True);self.assertNotIn('此处不自动保存',p.status.text());self.assertIn('上方选项',p.status.text())

if __name__=='__main__':unittest.main()
