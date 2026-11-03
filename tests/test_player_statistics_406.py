from copy import deepcopy
import unittest
from rouge.catalog import catalog
from rouge.player_personal_statistics import statistics,statistics_text,complete_inventory

def record(identity,**fields):
    return {'state':{'id':identity,'resources':{},'relics':{},'tactical_tools':{},**fields}}

class PersonalStatisticsTests(unittest.TestCase):
    def test_missing_is_not_zero_and_real_zero_is_included(self):
        rows=[record('a',resources={'gold':{'value':0}}),record('b',resources={'gold':{'value':10}}),record('c')]
        result=statistics(rows)['measures']['gold']
        self.assertEqual(result['mean'],5);self.assertEqual((result['sample_count'],result['missing_count']),(2,1))

    def test_invalid_numbers_do_not_enter_displayed_means(self):
        for value in(True,-1,float('nan'),float('inf'),'10',1.5,10**1000):
            result=statistics([record('a',resources={'gold':{'value':value}})])
            self.assertIsNone(result['measures']['gold']['mean'])

    def test_no_complete_denominator_means_unknown_not_zero_percent(self):
        identity=next(iter(catalog()['relics']))
        result=statistics([record('a',relics={identity:{'held':True}})],identity)
        self.assertIsNone(result['relic']['fraction']);self.assertEqual(result['relic']['sample_count'],0)

    def test_holding_rate_only_uses_complete_count_and_qualified_flags(self):
        identity=next(iter(catalog()['relics']))
        rows=[record('a',relics={identity:{'held':True}},relic_count=1,inventory_verified=True),
              record('b',relic_count=0,inventory_verified=True),
              record('c',relics={identity:{'held':True}},relic_count=2,inventory_verified=True),
              record('d',relics={identity:{'held':'true'}},relic_count=1,inventory_verified=True)]
        result=statistics(rows,identity)['relic'];self.assertEqual(result['fraction'],.5)
        self.assertEqual((result['held_count'],result['sample_count'],result['excluded_incomplete_count']),(1,2,2))

    def test_duplicate_versions_of_one_run_are_not_extra_games(self):
        rows=[record('a',resources={'gold':{'value':4}}),record('a',resources={'gold':{'value':100}})]
        result=statistics(rows);self.assertEqual(result['archive_count'],1);self.assertEqual(result['measures']['gold']['mean'],4)

    def test_no_outcome_or_drop_probability_claim_and_no_mutation(self):
        rows=[record('a')];before=deepcopy(rows);result=statistics(rows)
        self.assertEqual(rows,before);self.assertFalse(result['outcomes_observed'])
        text=statistics_text(result);self.assertIn('不表示通关',text);self.assertIn('没有胜负',text)
        with self.assertRaises(ValueError):statistics(rows,'unlisted-item')

if __name__=='__main__':unittest.main()
