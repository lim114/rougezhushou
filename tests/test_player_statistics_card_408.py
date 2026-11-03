import unittest
from rouge.player_personal_statistics import statistics
from rouge.player_statistics_card import card_lines

class StatisticsCardTests(unittest.TestCase):
    def test_missing_history_is_unknown_not_empty_card(self):self.assertIsNone(card_lines(None,'全部样本'))
    def test_card_keeps_denominator_missing_and_non_outcome_limits(self):
        result=statistics([{'state':{'id':'private-identity','resources':{'gold':{'value':0}}}},{'state':{'id':'other-private'}}]);lines=card_lines(result,'保密等级未读到');text='\n'.join(lines)
        self.assertIn('平均：0.00；有效1局，缺失1局',text);self.assertIn('不是通关场数',text);self.assertIn('不是掉落概率',text);self.assertIn('版本未完整记录',text)
        self.assertNotIn('private-identity',text);self.assertNotIn('other-private',text)
    def test_only_chosen_fields_included_but_boundaries_remain(self):
        result=statistics([{'state':{'id':'owned','resources':{}}}]);text='\n'.join(card_lines(result,'全部分队',{'gold'}))
        self.assertIn('源石锭',text);self.assertNotIn('零件数',text);self.assertNotIn('藏品栏总数',text);self.assertIn('未读不按0',text)
    def test_zero_archives_not_zero_means_or_zero_percent(self):
        text='\n'.join(card_lines(statistics([]),'当前筛选'));self.assertIn('样本：0局',text);self.assertIn('平均：未知',text);self.assertNotIn('0.0%',text)

if __name__=='__main__':unittest.main()
