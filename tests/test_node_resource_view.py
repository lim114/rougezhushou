"""Qt node details with public declarations; no private run or game interactions."""
from copy import deepcopy
import unittest
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge.node_catalog_view import NodeCatalogPanel


class NodeResourceViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.panel=NodeCatalogPanel();self.panel.resize(1000,700);self.panel.show();self.qt.processEvents()
    def tearDown(self):self.panel.close();self.panel.deleteLater();self.qt.processEvents()
    def select(self,title):
        self.panel.list.setCurrentRow(next(i for i,e in enumerate(self.panel.entries) if e['title']==title))
        self.qt.processEvents();return self.panel.detail.toPlainText()
    def context(self,value):self.panel.set_map_context(None,runtime_context=value)

    def test_visible_resource_budgets_three_states_do_not_exclude_event(self):
        self.select('货从口出')
        entry=next(e for e in self.panel.entries if e['title']=='货从口出')
        before=entry['qualification']['status']
        for value,label in (({},'预算未知'),({'gold':3},'不足已列费用'),({'gold':4},'覆盖已列费用')):
            self.context(value);text=self.select('货从口出')
            self.assertIn('费用参考：消耗4源石锭',text)
            self.assertIn('名义预算：'+label,text)
            entry=next(e for e in self.panel.entries if e['title']=='货从口出')
            self.assertEqual(entry['qualification']['status'],before)
            self.assertIn('不改变事件资格',text)
            self.assertIn('完整效果未证',text)
        text=self.select('安眠一隅');self.assertIn('增量或回复参考：获得20希望',text)

    def test_half_hp_and_minimum_retained_hp_remain_reference_only(self):
        self.context({'resources':{'hp':5}});text=self.select('沉重的契约')
        self.assertIn('比例 1/2；算术参考 2.5',text)
        self.assertIn('实际整数费用和取整规则未证',text)
        self.context({'resources':{'hp':2}});text=self.select('黑诞')
        self.assertIn('最低保留参考：1目标生命值',text)
        self.assertIn('特殊扣除规则未证',text)
        self.assertIn('服务器是否可选仍未知',text)

    def test_category_cost_partial_stock_and_unparsed_effects_stay_visible(self):
        stock={'item_quantities':{'rogue_6_scrap_G_01':1}}
        self.context(stock);text=self.select('回滚文明')
        self.assertIn('2件自然物',text)
        self.assertIn('已声明数量小计 1件，有关零件数量不完整',text)
        self.assertIn('名义预算：预算未知',text)
        self.context({**stock,'inventory_complete':True});text=self.select('回滚文明')
        self.assertIn('名义预算：不足已列费用',text)
        text=self.select('安眠一隅')
        self.assertIn('未识别顶层明确数量；不能视为零费用或零收益',text)
        self.assertIn('括号内藏品效果不自动计即时增减',text)
        first_scene=text.split('场景 1\n',1)[1].split('\n场景 2\n',1)[0]
        self.assertNotIn('明确数量 99源石锭',first_scene)
        # A later scene really grants 99 gold directly; preserve that distinction.
        self.assertIn('增量或回复参考：获得99源石锭',text)

    def test_terminal_version_warning_never_uses_current_inventory_as_snapshot(self):
        ctx={'item_quantities':{'rogue_6_relic_artifact_3':0,'rogue_6_relic_artifact_4':0},
             'inventory_complete':True}
        before=deepcopy(ctx);self.context(ctx);text=self.select('被歌颂的影子')
        self.assertIn('固定旧版 427904',text);self.assertIn('较新文档 440271',text)
        self.assertIn('当前持有不能替代',text)
        self.assertIn('当前文档分支参考：犬植浆 × 1；资格未确认',text)
        self.assertIn('当前文档分支参考：1行动力；资格未确认',text)
        self.assertEqual(ctx,before)
        self.assertNotIn('pre_entry_item_quantities',self.panel.runtime_context)
        self.context({**ctx,'pre_entry_inventory_complete':True});text=self.select('被歌颂的影子')
        self.assertIn('当前文档分支参考：犬植浆 × 1；已列条件相符',text)
        self.assertIn('当前文档分支参考：1行动力；已列条件不符',text)
        self.assertIn('实际领取：未知',text)

    def test_same_event_refresh_preserves_reading_selection_and_navigation(self):
        text=self.select('思乡心切');signals=[];self.panel.stageSelected.connect(signals.append)
        self.assertIn('场景 1',text);self.assertIn('选择参考：强行驱赶',text)
        self.panel.battle_button.click();self.assertEqual(signals,['ro6_t_1'])
        key=self.panel.detail_key;cursor=self.panel.detail.textCursor()
        cursor.setPosition(3);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor)
        self.panel.detail.setTextCursor(cursor);selection=self.panel.detail.textCursor().selectedText()
        self.panel.collapse_button.click();self.panel.refresh();self.qt.processEvents()
        self.assertEqual(self.panel.detail_key,key)
        self.assertEqual(self.panel.detail.textCursor().selectedText(),selection)
        self.assertFalse(self.panel.list.expanded_groups())
        self.assertEqual(self.panel.event_stage.currentData(),'ro6_t_1')


if __name__=='__main__':unittest.main()
