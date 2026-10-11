"""Report actual scoped previews without claiming a new event clock."""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.reporting import format_report
from tests.test_unit_lifetime_123 import OP,TOKEN,scenario,tentacle


def notes(result):
    block=next(b for b in result['report']['sections'] if b['id']=='calculation_context')
    return '\n'.join(block['notes'])


class UnitScenarioProvenance124Tests(unittest.TestCase):
    def test_continuous_unit_conditions_visible_without_invented_frame_stream(self):
        result=calculate_damage(scenario('continuous','0'))
        self.assertEqual(tentacle(result)['total'],0)
        self.assertEqual(result['timing']['streams'],[])
        text=notes(result)
        self.assertIn('触手声明 · 当前目标生命周期终点：0 秒',text)
        self.assertIn('目标生命周期来源：单位自身声明',text)
        self.assertEqual(result['timing']['unit_scenarios'][0]['options']['target_disappears_seconds'],0)

    def test_inherited_and_unspecified_lifetimes_are_distinguished(self):
        for mode in ('frames','continuous'):
            for timing,source in (({'target_disappears_seconds':0},'继承本体声明'),
                                  ({},'未声明，沿用既有无限生命周期参考')):
                result=calculate_damage({'operator':OP,'skill':1,'window_seconds':10,
                    'timing_mode':mode,'timing':timing})
                self.assertIn('目标生命周期来源：'+source,notes(result))

    def test_unused_unit_preview_not_reported_as_an_applied_condition(self):
        args=scenario('continuous',10)
        args['timing']['units']['unused']={'target_disappears_seconds':0}
        result=calculate_damage(args)
        self.assertEqual({r['unit'] for r in result['timing']['unit_scenarios']},{TOKEN})
        self.assertNotIn('独立单位声明',notes(result))

    def test_recorded_options_are_isolated_from_caller_and_formatted_without_mutation(self):
        args=scenario('frames',10)
        args['timing']['units'][TOKEN]['target_windows']=[[0,3]]
        before=copy.deepcopy(args)
        result=calculate_damage(args)
        saved=copy.deepcopy(result)
        for technical in (False,True):
            self.assertIn('目标生命周期来源：单位自身声明',format_report(result,technical=technical))
        self.assertEqual(result,saved)
        result['timing']['unit_scenarios'][0]['options']['target_windows'][0][0]=99
        self.assertEqual(args,before)


if __name__=='__main__':unittest.main()
