from copy import deepcopy
from unittest import TestCase
from rouge.catalog import catalog
from rouge.mei_module_reference import reference
from tests.test_mei_airborne_module_reference import scenario


class MeiPartLookupTests(TestCase):
    def test_missing_module_has_no_reference_and_catalogue_parts_are_read_once(self):
        class Parts(list):
            scans = 0
            def __iter__(self):
                self.scans += 1
                return super().__iter__()

        profile = deepcopy(catalog()['operators']['char_133_mm'])
        module = next(m for m in profile['modules'] if m['id'] == 'uniequip_002_mm')
        stage = module['levels'][0]
        parts = stage['parts'] = Parts(stage['parts'])
        result, returned = reference(profile, scenario())
        self.assertIs(returned, parts)
        self.assertIsNotNone(result)
        self.assertEqual(parts.scans, 1)
        profile['modules'] = []
        self.assertEqual(reference(profile, scenario()), (None, ()))

    def test_equal_copied_part_keeps_first_source_index(self):
        profile=deepcopy(catalog()['operators']['char_133_mm'])
        module=next(m for m in profile['modules'] if m['id']=='uniequip_002_mm')
        parts=module['levels'][0]['parts']
        part=deepcopy(parts[0]);parts.append(deepcopy(part))
        result,returned=reference(profile,scenario(),[part])
        self.assertIn('.parts[0].',result['source_selectors'][-1])
        self.assertIs(returned,parts)

    def test_modified_part_is_rejected_without_mutating_source(self):
        profile=deepcopy(catalog()['operators']['char_133_mm']);before=deepcopy(profile)
        module=next(m for m in profile['modules'] if m['id']=='uniequip_002_mm')
        part=deepcopy(module['levels'][0]['parts'][0]);part['target']='FOREIGN'
        self.assertIsNone(reference(profile,scenario(),[part])[0])
        self.assertEqual(profile,before)
