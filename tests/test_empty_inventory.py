import unittest
import tempfile,time
from pathlib import Path
import cv2,numpy as np
from rouge.recognition import ScreenReader
from rouge.run_state import RunState

ROOT=Path(__file__).resolve().parents[1]

class EmptyInventoryTests(unittest.TestCase):
    def test_visible_zero_is_confirmed_but_hidden_counter_is_not_assumed_empty(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-map-empty.png',dtype=np.uint8),1)
        reader=ScreenReader()
        run=reader.read(image,client_rect=[2,45,2050,1125])['run']
        self.assertEqual(run['relics']['count'],0)
        self.assertEqual(run['relics']['ids'],[])
        masked=image.copy();masked[1025:1080,210:285]=30
        self.assertIsNone(reader.read(masked,client_rect=[2,45,2050,1125])['run']['relics']['count'])

    def test_empty_count_resizes_and_enters_same_run_memory_without_clearing_history(self):
        source=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-map-empty.png',dtype=np.uint8),1)[45:-2,2:-2]
        reader=ScreenReader()
        with tempfile.TemporaryDirectory() as directory:
            memory=RunState(Path(directory)/'run.json');identity=memory.state['id']
            for height in [720,1440]:
                with self.subTest(height=height):
                    image=cv2.resize(source,(round(source.shape[1]*height/source.shape[0]),height))
                    image=cv2.copyMakeBorder(image,35,63,27,41,cv2.BORDER_CONSTANT,value=0)
                    run=reader.read(image)['run']
                    self.assertEqual(run['relics']['count'],0)
                    self.assertTrue(memory.apply(run,time.time()))
                    self.assertTrue(memory.inventory_status()['complete'])
                    self.assertEqual(memory.state['id'],identity)
            self.assertEqual(memory.inventory_status()['expected_count'],0)

    def test_zero_counter_cannot_clear_a_visibly_nonempty_bar(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-map-empty.png',dtype=np.uint8),1)
        held=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-relic-multicard-closed.png',dtype=np.uint8),1)
        image[1019:1107,394:482]=held[1019:1107,394:482]
        run=ScreenReader().read(image)['run']
        self.assertIsNone(run['relics']['count'])
        self.assertIn('rogue_6_relic_fight_26',run['relics']['ids'])
