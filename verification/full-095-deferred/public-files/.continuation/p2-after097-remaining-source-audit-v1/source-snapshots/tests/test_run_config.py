import unittest
import tempfile,time
from pathlib import Path
import cv2,numpy as np
from rouge.recognition import ScreenReader
from rouge.run_state import RunState

ROOT=Path(__file__).resolve().parents[1]

class RunConfigTests(unittest.TestCase):
    def test_current_run_info_confirms_difficulty_and_strengthened_trade_squad(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-info-trade.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        run=ScreenReader().read(image)['run']
        self.assertEqual(run['config']['difficulty']['value'],10)
        self.assertEqual(run['config']['squad']['id'],'rogue_6_band_20')
        self.assertEqual(run['config']['squad']['name'],'多边贸易分队')
        self.assertEqual(run['config']['squad']['level'],1)

    def test_settings_survive_missing_pages_restart_and_only_manual_reset_clears_them(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'run.json';state=RunState(file)
            base={'relics':{'ids':[],'icons':[],'count':None,'source':'held_bar'},'operators':[]}
            config={'difficulty':{'value':10,'source':'label'},'squad':{'id':'rogue_6_band_20','name':'多边贸易分队','level':1,'effect_verified':True,'source':'effect'}}
            state.apply({**base,'config':config},time.time())
            state.apply(base,time.time())
            state.apply({**base,'config':{'squad':{'id':'rogue_6_band_19','name':'多边贸易分队','level':None,'effect_verified':False,'source':'name'}}},time.time())
            restored=RunState(file)
            self.assertEqual(restored.state['config']['difficulty']['value'],10)
            self.assertEqual(restored.state['config']['squad']['id'],'rogue_6_band_20')
            self.assertEqual(len([h for h in restored.state['history'] if h['kind']=='config_updated']),2)
            restored.reset()
            self.assertEqual(restored.state['config'],{})

