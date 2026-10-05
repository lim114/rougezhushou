"""Public reader contracts when UI panels move within a differently sized frame."""
import unittest
from pathlib import Path
import cv2
import numpy as np
from rouge.recognition import ScreenReader

ROOT = Path(__file__).resolve().parents[1]

def sample(name):
    return cv2.imdecode(np.fromfile(ROOT / f'samples/native-client/{name}.png', dtype=np.uint8), 1)

def relocated(image, dx=500, dy=100):
    # Non-black padding prevents the viewport crop from undoing the layout change.
    canvas = np.full((1800, 3200, 3), 8, dtype=np.uint8)
    h, w = image.shape[:2]
    canvas[dy:dy+h, dx:dx+w] = image
    return canvas

class AdaptiveRecognitionTests(unittest.TestCase):
    def test_map_registration_and_configuration_survive_relocation(self):
        image=sample('map-template-node-detail')
        result=ScreenReader().read(relocated(image))
        self.assertEqual(result['map']['status'],'matched')
        self.assertEqual(result['map']['template_id'],'1c')
        self.assertEqual(result['run']['config']['zone']['id'],'zone_1')

    def test_changed_icon_is_not_reported_as_fresh_and_geometry_change_rediscovers(self):
        reader=ScreenReader();image=sample('operator-mechanist')
        first=reader.read(image)
        self.assertEqual(first['operator']['fields']['potential'],6)
        changed=image.copy();changed[400:590,1700:1920]=0
        second=reader.read(changed)
        self.assertNotIn('potential',second['operator']['fields'])
        self.assertGreater(second['observed_at'],first['observed_at'])
        self.assertLess(second['performance']['ocr']['pixels'],image.shape[0]*image.shape[1])
        third=reader.read(relocated(image))
        self.assertEqual(third['operator']['fields']['potential'],6)
        self.assertEqual(third['performance']['ocr']['mode'],'full_discovery')

    def test_module_and_roster_panels_survive_relocation(self):
        module=ScreenReader().read(relocated(sample('module-mechanist')))['operator']
        self.assertEqual(module['fields']['module_level'],3)
        roster=ScreenReader().read(relocated(sample('run-mechanist-selected')))['run']
        self.assertEqual(roster['selected_operator'],'mechanist')
        member=next(m for m in roster['operators'] if m['id']=='mechanist')
        self.assertEqual(member['fields']['level'],80)
        self.assertEqual(member['fields']['elite'],1)
        self.assertEqual(member['skill_ranks'],{1:7,2:7})

    def test_held_bar_and_resources_follow_their_labels_when_panel_moves(self):
        result=ScreenReader().read(relocated(sample('run-map-closed')))
        self.assertIsNotNone(result['run'])
        self.assertEqual(result['run']['relics']['ids'],['rogue_6_relic_legacy_52'])
        self.assertEqual(result['run']['relics']['count'],1)
        self.assertEqual(result['run']['crew_count'],6)

    def test_operator_fields_survive_relocation_without_user_calibration(self):
        result = ScreenReader().read(relocated(sample('operator-mechanist')))
        self.assertEqual(result['page'], 'operator_detail')
        operator = result['operator']
        self.assertEqual(operator['id'], 'mechanist')
        self.assertEqual(operator['fields']['potential'], 6)
        self.assertEqual(operator['fields']['level'], 90)
        self.assertEqual(operator['fields']['elite'], 2)
        self.assertEqual(operator['fields']['module_level'], 3)
        self.assertEqual(operator['skill_ranks'], {1: 10, 2: 9, 3: 10})
