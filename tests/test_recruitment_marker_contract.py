"""Approved D312: invalid templates fail before scoring any observation."""
import unittest
from unittest.mock import patch
import numpy as np
from rouge import recruitment_recognition as model


class RecruitmentMarkerContractTests(unittest.TestCase):
    def test_empty_mask_is_rejected_before_observation(self):
        image=np.zeros((1080,1920,3),np.uint8)
        with patch.object(model,'reference',return_value=np.zeros((51,49),np.uint8)), \
                patch.object(model.cv2,'cvtColor') as read_observation:
            with self.assertRaisesRegex(ValueError,'白色像素'):
                model.recruitment_marker(image,.5,.5)
            read_observation.assert_not_called()

    def test_zero_template_size_is_rejected_at_entry(self):
        with self.assertRaisesRegex(ValueError,'尺寸'):
            model.recruitment_marker(np.zeros((1,1,3),np.uint8),.5,.5)

    def test_black_observation_is_non_emergency_with_valid_template(self):
        with patch.object(model,'reference',wraps=model.reference) as reference:
            result=model.recruitment_marker(np.zeros((1080,1920,3),np.uint8),.5,.5)
        self.assertEqual(result['kind'],'non_emergency')
        self.assertEqual(result['score'],0)
        reference.assert_called_once_with('emergency')

    def test_no_in_bounds_observation_remains_unconfirmed(self):
        self.assertIsNone(model.recruitment_marker(np.zeros((1080,1920,3),np.uint8),0,0))
