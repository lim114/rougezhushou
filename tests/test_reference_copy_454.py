import unittest
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QLabel
from rouge.reference_copy import mechanism_copy
from rouge.mechanism_reading import MechanismTextBrowser, replace_mechanism_text


class ReferenceCopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_game_conditions_and_unrecognised_text_are_preserved_verbatim(self):
        text = '【招式】\n不能被阻挡；生命低于50%时转入第二形态。\n未命中不消耗护盾。\n【备注】\n另一条未登记说明。'
        body, notes = mechanism_copy(text, '资料范围')
        self.assertEqual(body, text)
        self.assertEqual(notes, '')

    def test_scope_footer_moves_to_details_without_hiding_next_mechanism(self):
        text = '资料范围\n【招式】\n冷却80秒。\n【适用边界】\n来源与适用关卡。\n【第二形态】\n不能被阻挡。'
        body, notes = mechanism_copy(text, '资料范围')
        self.assertEqual(body, '【招式】\n冷却80秒。\n【第二形态】\n不能被阻挡。')
        self.assertEqual(notes, '【适用边界】\n来源与适用关卡。')

    def test_source_conflict_remains_visible_as_short_condition(self):
        line = '半血条件有两种来源口径：图鉴写“低于50%”，完整文献写“不高于50%”；恰好50%的当前服务器判定尚未核验。'
        body, notes = mechanism_copy(line, '范围')
        self.assertEqual(body, '半血条件：低于50% / 不高于50%（资料有差异）。')
        self.assertEqual(notes, line)

    def test_event_scope_heading_is_opt_in_and_game_condition_stays_by_default(self):
        text = '【仍需区分】\n生命低于50%时转入第二形态。'
        self.assertEqual(mechanism_copy(text,'范围'),(text,''))
        self.assertEqual(mechanism_copy(text,'范围',extra_detail_headings=('【仍需区分】',)),('',text))

    def browser(self):
        browser = MechanismTextBrowser()
        label = QLabel('资料范围')
        label.setProperty('referenceBaseText', '资料范围')
        self.addCleanup(browser.deleteLater)
        self.addCleanup(label.deleteLater)
        return browser, label

    def test_refresh_keeps_reading_and_full_notes_are_available(self):
        browser, label = self.browser()
        text = '资料范围\n【招式】\n冷却80秒。\n【来源与未知】\n来源版本。'
        replace_mechanism_text(browser, text, preserve=False, follow_change=False, details=label)
        cursor = QTextCursor(browser.document())
        cursor.setPosition(2)
        cursor.setPosition(6, QTextCursor.MoveMode.KeepAnchor)
        browser.setTextCursor(cursor)
        self.assertFalse(replace_mechanism_text(browser, text, preserve=True, follow_change=False, details=label))
        self.assertEqual(browser.textCursor().selectedText(), cursor.selectedText())
        self.assertEqual(label.text(), '资料范围\n\n【来源与未知】\n来源版本。')

    def test_clear_and_next_document_remove_previous_notes(self):
        browser, label = self.browser()
        replace_mechanism_text(browser, '【适用边界】\n旧来源。', preserve=False, follow_change=False, details=label)
        browser.setPlainText('暂无资料。')
        self.assertEqual(label.text(), '资料范围')
        replace_mechanism_text(browser, '【招式】\n不能被阻挡。', preserve=False, follow_change=False, details=label)
        self.assertEqual(browser.toPlainText(), '【招式】\n不能被阻挡。')
        self.assertEqual(label.text(), '资料范围')


if __name__ == '__main__':
    unittest.main()
