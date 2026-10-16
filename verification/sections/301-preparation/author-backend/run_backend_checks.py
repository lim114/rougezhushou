"""Isolated pure backend candidate; original public query imports only."""
from pathlib import Path
import os
import sys
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
os.environ['ROUGE_NAMED_REWARD_ITEMS_MODULE']=str(HERE/'candidate/rouge/named_reward_items.py')
suite=unittest.defaultTestLoader.discover(str(HERE/'candidate/tests'),pattern='test_named_reward_items_301.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
