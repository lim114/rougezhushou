"""Run only the isolated candidate's pure backend contracts, with live public catalog."""
from pathlib import Path
import os
import sys
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
os.environ['ROUGE_FUTURE_REGION_MODULE']=str(HERE/'candidate/rouge/future_region_effects.py')
suite=unittest.defaultTestLoader.discover(str(HERE/'candidate/tests'),pattern='test_future_region_effects_300.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
