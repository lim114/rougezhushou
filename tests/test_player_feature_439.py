import unittest
from tests.test_player_feature_435 import NodeDirectoryReading
class ExcludedReferences(NodeDirectoryReading):
 def test_exclusions_are_separate_collapsed_and_keep_reason(self):
  p=self.p;root=next(p.entries.topLevelItem(i)for i in range(p.entries.topLevelItemCount())if p.entries.topLevelItem(i).text(0).startswith('已列条件排除'));self.assertFalse(root.isExpanded());p.entries.setCurrentItem(root.child(0));self.assertIn('排除依据',p.detail.toPlainText());self.assertIn('不是候选',root.text(0));root.setExpanded(True);p.refresh();root=next(p.entries.topLevelItem(i)for i in range(p.entries.topLevelItemCount())if p.entries.topLevelItem(i).text(0).startswith('已列条件排除'));self.assertTrue(root.isExpanded())
if __name__=='__main__':unittest.main()
