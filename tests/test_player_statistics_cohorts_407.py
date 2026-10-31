from copy import deepcopy
import unittest
from rouge.run_config import config_data
from rouge.player_statistics_cohorts import cohort,cohort_options,select_cohort,cohort_note,UNREAD

def record(identity,grade=None,squad=None):
    config={}
    if grade is not None:config['difficulty']={'value':grade,'captured_at':1}
    if squad is not None:config['squad']={'id':squad,'name':config_data()['squads'][squad]['name'],'captured_at':1}
    return {'state':{'id':identity,'config':config}}

class CohortTests(unittest.TestCase):
    def test_base_and_strengthened_variant_share_only_known_family(self):
        rows=[record('a',15,'rogue_6_band_1'),record('b',15,'rogue_6_band_2'),record('c')];before=deepcopy(rows)
        self.assertEqual([r['state']['id']for r in select_cohort(rows,squad='rogue_6_band_1')],['a','b']);self.assertEqual(rows,before)
        self.assertIn('不表示效果完全相同',cohort_note(None,None))
    def test_unread_missing_or_unverified_config_are_separate_from_zero(self):
        rows=[record('zero',0),record('missing'),record('invalid',True),record('outside',17)]
        self.assertEqual([r['state']['id']for r in select_cohort(rows,difficulty=0)],['zero'])
        self.assertEqual([r['state']['id']for r in select_cohort(rows,difficulty=UNREAD)],['missing','invalid','outside'])
        self.assertEqual(select_cohort(rows,difficulty=True),[])
    def test_combined_filters_and_unknown_ids_do_not_silently_show_all(self):
        rows=[record('a',15,'rogue_6_band_1'),record('b',0,'rogue_6_band_1'),record('c',15,'rogue_6_band_3')]
        self.assertEqual([r['state']['id']for r in select_cohort(rows,difficulty=15,squad='rogue_6_band_1')],['a'])
        self.assertEqual(select_cohort(rows,squad='unknown'),[]);self.assertEqual(select_cohort(rows,difficulty='15'),[])
    def test_unverified_name_and_missing_capture_do_not_create_known_squad(self):
        row=record('a',15,'rogue_6_band_1');row['state']['config']['squad']['name']='其他名称';self.assertEqual(cohort(row)['squad'],UNREAD)
        row=record('b',15,'rogue_6_band_1');row['state']['config']['squad'].pop('captured_at');self.assertEqual(cohort(row)['squad'],UNREAD)
    def test_multiple_versions_of_one_run_do_not_duplicate_filter_sample(self):
        rows=[record('a',15),record('a',0)];self.assertEqual(len(select_cohort(rows)),1);self.assertEqual(select_cohort(rows,difficulty=0),[])

if __name__=='__main__':unittest.main()
