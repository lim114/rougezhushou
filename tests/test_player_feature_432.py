import unittest
from copy import deepcopy
from rouge.player_statistics_samples import sample_rows,sample_binding
from rouge.player_personal_statistics import statistics
from tests.test_player_statistics_406 import record

class StatisticSampleProvenance(unittest.TestCase):
 def test_zero_and_unknown_have_same_membership_as_actual_mean(self):
  records=[record('zero',resources={'gold':{'value':0}}),record('ten',resources={'gold':{'value':10}}),record('missing')]
  rows=sample_rows(records,'gold');result=statistics(records)['measures']['gold']
  self.assertEqual([r['value']for r in rows],[0,10,None]);self.assertEqual(sum(r['included']for r in rows),result['sample_count']);self.assertEqual(result['mean'],5)
 def test_duplicate_run_versions_are_not_extra_sample_rows(self):
  rows=sample_rows([record('one',relic_count=2),record('one',relic_count=100)],'relic_count')
  self.assertEqual(len(rows),1);self.assertEqual(rows[0]['value'],2)
 def test_relic_missing_inventory_is_not_confirmed_absence(self):
  from rouge.catalog import catalog
  identity=next(iter(catalog()['relics']))
  records=[record('held',relics={identity:{'held':True}},relic_count=1,inventory_verified=True),record('not-held',relic_count=0,inventory_verified=True),record('unknown')]
  rows=sample_rows(records,'relic',identity);self.assertEqual([r['value']for r in rows],[True,False,None]);self.assertEqual(sum(r['included']for r in rows),statistics(records,identity)['relic']['sample_count'])
 def test_invalid_numeric_types_stay_excluded(self):
  for value in(True,-1,float('nan'),float('inf'),'10',1.2,10**1000):
   rows=sample_rows([record('one',resources={'gold':{'value':value}})],'gold');self.assertFalse(rows[0]['included']);self.assertIsNone(rows[0]['value'])
 def test_archive_navigation_requires_exact_verified_state_digest(self):
  self.assertIsNone(sample_binding({'id':'one'}));self.assertIsNone(sample_binding({'id':'one','state_sha256':'bad'}))
  binding={'id':'one','state_sha256':'a'*64};self.assertEqual(sample_binding(binding),binding)
 def test_no_unknown_measure_or_item_fallback_and_no_state_mutation(self):
  records=[record('one')];before=deepcopy(records)
  self.assertEqual(sample_rows(records,'unknown'),[]);self.assertEqual(sample_rows(records,'relic','missing'),[]);self.assertEqual(records,before)

if __name__=='__main__':unittest.main()
