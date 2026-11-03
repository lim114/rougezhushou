import unittest,json
from copy import deepcopy
from unittest.mock import patch
from rouge import public_node_statistics as m
class Statistics(unittest.TestCase):
 def test_real_aggregate_reconciles(self):
  d=m.load();self.assertEqual(sum(n for k,f in d['counts'].items()if k!='start'for b in f.values()for n in b.values()),d['metadata']['sampleCount'])
 def test_denominator_is_same_floor_distance(self):
  d=m.load();rows=m.frequency_rows(d,'0',1);total=sum(b.get('0',{}).get('1',0)for b in d['counts'].values())
  self.assertEqual(sum(r['count']for r in rows),total);self.assertAlmostEqual(sum(r['frequency']for r in rows),1)
 def test_missing_samples_unknown(self):self.assertEqual(m.frequency_rows(m.load(),'0',100),[])
 def test_bad_counts_rejected(self):
  d=m.load();d['counts']['combat']['0']['1']=True
  with self.assertRaises(ValueError):m.validate(d)
 def test_source_total_mismatch(self):
  d=m.load();d['metadata']['sampleCount']+=1
  with self.assertRaises(ValueError):m.validate(d)
 def test_literal_does_not_execute(self):
  with self.assertRaises(ValueError):m._literal('{a:process.exit()}')
 def test_all_types_have_chinese_labels(self):self.assertTrue(set(m.load()['counts'])<=set(m.LABELS))
