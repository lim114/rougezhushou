"""Image-only experimental path, including honest unsupported fields."""
import unittest
import numpy as np
from rouge.visual_recognition import VisualReader
from tests.test_adaptive_recognition import sample,relocated

class VisualRecognitionTests(unittest.TestCase):
    def test_image_only_identity_and_potential_survive_panel_relocation(self):
        reader=VisualReader()
        for file,key,potential in [('operator-mechanist','mechanist',6),
                                   ('operator-silverash','silverash',1),
                                   ('operator-kaltsit','kaltsit',2)]:
            with self.subTest(operator=key):
                result=reader.read(relocated(sample(file)))
                self.assertEqual(result['operator']['id'],key)
                self.assertEqual(result['operator']['fields'],{'potential':potential})
                self.assertFalse(result['operator']['complete'])
                self.assertEqual(result['performance']['ocr_model_calls'],0)
                self.assertEqual(result['texts'],[])

    def test_unsupported_page_and_empty_frame_never_supply_reference_values(self):
        reader=VisualReader()
        for image in [sample('module-mechanist'),np.full((720,1280,3),8,np.uint8)]:
            result=reader.read(image)
            self.assertIsNone(result['operator'])
            self.assertIsNone(result['run'])
            self.assertEqual(result['performance']['ocr_model_calls'],0)
