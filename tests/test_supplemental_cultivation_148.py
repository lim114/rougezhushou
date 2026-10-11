import os
import unittest
from copy import deepcopy
from rouge.supplemental_skills import defaults,_cultivated_stats
from rouge.supplemental_cultivation import compare_cultivation,cultivation_defaults
from tests.test_supplemental_run_141 import environment


class Cultivation148Tests(unittest.TestCase):
    def test_talent_gate_hp_and_trust_are_recalculated(self):
        p=defaults('char_209_ardign');e=environment()
        proposals=cultivation_defaults(p,e)['proposals'][:2]
        proposals[1].update(trust=0,potential=6)
        r=compare_cultivation(p,e,{'proposals':proposals})
        a,b=[v['result'] for v in r['variants']]
        self.assertTrue(a['talents']);self.assertFalse(b['talents'])
        self.assertNotEqual(a['attributes']['hp'],b['attributes']['hp'])
        self.assertEqual(a['rows'][1]['value'],a['attributes']['hp']*.4)

    def test_emergency_source_changes_only_declared_variant(self):
        p=defaults();e=environment(['rogue_6_relic_cargo_10'])
        e['operator_metadata'][p['operator']]={'recruitment_kind':'non_emergency'}
        old=deepcopy((p,e));r=compare_cultivation(p,e,cultivation_defaults(p,e))
        ordinary=r['variants'][0]['result'];emergency=r['variants'][3]['result']
        self.assertAlmostEqual(emergency['attributes']['attack']-ordinary['attributes']['attack'],_cultivated_stats(p)['attack']*.4)
        self.assertEqual((p,e),old)
        self.assertEqual(r['baseline']['environment']['operator_metadata'][p['operator']]['recruitment_kind'],'non_emergency')

    def test_potential_cost_changes_and_fang_combo_not_zero(self):
        p=defaults('char_124_kroos');e=environment()
        r=compare_cultivation(p,e,cultivation_defaults(p,e))
        self.assertLess(r['variants'][2]['result']['deployment_reference']['estimated_cost'],r['baseline']['deployment_reference']['estimated_cost'])
        p=defaults('char_123_fang');e=environment(['rogue_6_relic_hand_1'])
        r=compare_cultivation(p,e,cultivation_defaults(p,e))
        row=next(row for row in r['rows'] if row['proposal']=='当前培养及来源' and row['key']=='deployment')
        self.assertIsNone(row['value']);self.assertIsNone(row['delta'])

    def test_invalid_cultivation_does_not_destroy_other_variants(self):
        p=defaults();e=environment();choices=cultivation_defaults(p,e)
        choices['proposals'][1]['level']=999
        r=compare_cultivation(p,e,choices)
        self.assertIsNone(r['variants'][1]['result']);self.assertTrue(r['variants'][1]['error'])
        self.assertIsNotNone(r['variants'][2]['result'])
        invalid=next(row for row in r['rows'] if row['key']=='invalid')
        self.assertIsNone(invalid['delta'])

    def test_unknown_recipient_stays_partial_and_schema_is_strict(self):
        p=defaults();e=environment(['rogue_6_relic_cargo_10'])
        choices=cultivation_defaults(p,e);r=compare_cultivation(p,e,choices)
        self.assertFalse(r['variants'][0]['result']['attribute_resolution']['complete_for_attribute_scope'])
        for value in [True,'temporary',[],{}]:
            broken=deepcopy(choices);broken['proposals'][0]['recruitment_kind']=value
            with self.subTest(value=value),self.assertRaises(ValueError):compare_cultivation(p,e,broken)
        choices['proposals'][1]['name']=choices['proposals'][0]['name']
        with self.assertRaises(ValueError):compare_cultivation(p,e,choices)

    @unittest.skipUnless(os.name=="nt" or os.environ.get("QT_QPA_PLATFORM")=="offscreen" or os.environ.get("DISPLAY"),
                         "Qt entry unavailable without a display/offscreen capability")
    def test_ui_entry_and_pending_edit_cannot_use_stale_cultivation(self):
        try:
            from PySide6.QtWidgets import QApplication
            from rouge.supplemental_run_view import SupplementalRunDialog
        except ImportError:self.skipTest('Qt unavailable')
        app=QApplication.instance() or QApplication([])
        d=SupplementalRunDialog(defaults(),environment)
        d.show_cultivation();self.assertIsNotNone(d.children_dialogs[-1].result)
        d.children_dialogs[-1].close();count=len(d.children_dialogs)
        d.editor.setPlainText('{}');d.show_cultivation()
        self.assertEqual(len(d.children_dialogs),count);d.close();app.processEvents()
