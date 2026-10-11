import unittest
from copy import deepcopy
from rouge import calibration as c

class CalibrationTests(unittest.TestCase):
    def test_151_layers_independent_oracles_and_no_mutation(self):
        s={'operator':'mechanist','skill':3,'charge_count':0,'relic_ids':['rogue_6_relic_legacy_16']}
        before=deepcopy(s);r=c.panel_layers(s)
        self.assertEqual(s,before)
        self.assertEqual(r['panels']['培养与模组']['attack'],573)
        self.assertEqual(r['panels']['藏品与分队符文写回']['attack'],716)
        self.assertAlmostEqual(r['panels']['技能期间参考']['attack'],2720.8)
        self.assertFalse(r['native_verified'])
        self.assertEqual(r['source']['commit'],'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add')
    def test_151_kaltsit_rune_before_talent(self):
        r=c.panel_layers({'operator':'kaltsit','skill':2,'relic_ids':['rogue_6_relic_legacy_90']})
        self.assertEqual(r['panels']['培养与模组']['hp'],2120)
        self.assertEqual(r['panels']['藏品与分队符文写回']['hp'],3180)
        self.assertEqual(r['panels']['已覆盖常态天赋与效果']['hp'],3975)

if __name__=='__main__':unittest.main()
