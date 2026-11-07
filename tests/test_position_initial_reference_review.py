import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_stage_objects_view as objects, current_route_itinerary_view as routes


class PositionInitialReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_standalone_open_uses_one_position_lookup_then_refresh_reads_again(self):
        for module,cls,stage in [(objects,objects.CurrentStageObjectsPanel,'ro6_n_1_1'),(routes,routes.CurrentRouteItineraryPanel,'ro6_n_1_3')]:
            with self.subTest(stage=stage):
                panel=cls(stage)
                self.addCleanup(panel.close_children)
                self.addCleanup(panel.close)
                panel.entries.setCurrentIndex(1)
                if module is routes:
                    route=next(r for r in panel.result['entries'] if any(s['spatial_reference_permitted'] for s in r['steps']))
                    panel.entries.setCurrentIndex(panel.entries.findData(route['key']))
                    step=next(s for s in route['steps'] if s['spatial_reference_permitted'])
                    panel.steps.setCurrentIndex(panel.steps.findData(step['key']))
                with patch.object(module.model,'position_reference',wraps=module.model.position_reference) as read:
                    self.assertTrue(panel.open_position())
                    self.assertEqual(read.call_count,1)
                    self.assertTrue(panel.position_dialog.panel.refresh_reference())
                    self.assertEqual(read.call_count,2)

    def test_explicit_unavailable_initial_result_does_not_reload(self):
        for module,cls,args in [(objects,objects.CurrentObjectPositionPanel,('stage','object')),(routes,routes.CurrentRouteStepPositionPanel,('stage','route','step'))]:
            with self.subTest(module=module.__name__),patch.object(module.model,'stage_reference') as read:
                panel=cls(*args,initial_reference=None)
                self.addCleanup(panel.close)
                self.assertIsNone(panel.result)
                read.assert_not_called()
