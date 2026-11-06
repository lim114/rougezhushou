from copy import deepcopy
from unittest.mock import patch
import unittest

from rouge import recipient_native_ratio as native


class RecipientPreparedBoundaryReviewTests(unittest.TestCase):
    def test_cultivation_resolves_module_once_for_all_supported_operators(self):
        class Modules(list):
            scans=0
            def __iter__(self):
                self.scans+=1
                return super().__iter__()
        for operator in native.OPERATORS:
            with self.subTest(operator=operator):
                profile=deepcopy(native.operator_profiles()[operator])
                profile['modules']=Modules(profile['modules'])
                with patch.object(native,'operator_profiles',return_value={operator:profile}):
                    result=native.recipient_native_ratio_diagnostic(native.public_recipient_ratio_payload(operator))
                self.assertTrue(result['cultivation']['matching_source_trait_selected'])
                self.assertEqual(profile['modules'].scans,1)

    def test_validated_observations_do_not_reenter_raw_input_validation(self):
        with patch.object(native,'native_positive_ratio_division',wraps=native.native_positive_ratio_division) as raw_entry:
            result=native.recipient_native_ratio_diagnostic(native.public_recipient_ratio_payload())
        self.assertTrue(result['source_available'])
        self.assertEqual(raw_entry.call_count,0)
