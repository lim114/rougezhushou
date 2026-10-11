import copy,unittest
from rouge.catalog import catalog
from rouge.token_counts import token_count_reference,count_rules
from rouge.token_module_comparison import compare_token_module
from rouge.token_budget import token_budget

OP='char_2027_wang';TOKEN='token_10064_wang_stone1';MODULE='uniequip_002_wang'
def counts(**options):
    return token_count_reference(catalog()['operators'][OP],{'operator':OP,**options},TOKEN)

class WangCountReferenceTests(unittest.TestCase):
    def test_elite_potential_boundaries_separate_inventory_and_manual_counts(self):
        for elite in (0,1,2):
            for potential in range(1,7):
                with self.subTest(elite=elite,potential=potential):
                    r=counts(elite=elite,potential=potential)
                    bonus=int(potential>=3)
                    self.assertEqual(r['held_limit'],5+elite+bonus)
                    self.assertEqual(r['concurrent_limit'],4+elite+bonus)
                    self.assertIsNone(r['actual_presence']);self.assertIsNone(r['actual_available_stock'])
                    self.assertIsNone(r['automatic_extra_concurrent_limit'])
                    self.assertIsNone(r['skill_modified_limits'])

    def test_all_module_stages_raise_only_manual_concurrent_count_after_unlock(self):
        for level in (59,60,90):
            for stage in (1,2,3):
                r=counts(elite=2,level=level,potential=6,module_id=MODULE,module_level=stage)
                self.assertEqual(r['held_limit'],8)
                self.assertEqual(r['concurrent_limit'],8 if level>=60 else 7)
                self.assertEqual(r['module_applied'],level>=60)
        r=counts(elite=1,level=80,module_id=MODULE,module_level=3)
        self.assertFalse(r['module_applied']);self.assertEqual(r['concurrent_limit'],5)

    def test_actual_module_comparison_consumes_counts_without_filling_unknown_hp(self):
        r=compare_token_module(OP,{'elite':2,'level':80,'potential':3},MODULE)
        stages=r['tokens'][0]['stages']
        self.assertEqual(stages[0]['values']['held_limit'],8)
        self.assertEqual(stages[0]['values']['concurrent_limit'],7)
        for stage in stages[1:]:
            self.assertEqual(stage['values']['held_limit'],8)
            self.assertEqual(stage['values']['concurrent_limit'],8)
            self.assertIsNone(stage['values']['hp'])
            self.assertIsNotNone(stage['count_reference'])

    def test_default_stock_and_concurrency_overflow_do_not_claim_actual_deployable(self):
        training={'elite':2,'level':80,'potential':3,'module_id':MODULE,'module_level':3}
        args={TOKEN:{'additional':2,'present':7,'available_stock':9}}
        before=copy.deepcopy((training,args))
        r=token_budget(OP,training,args,100);row=r['rows'][0]
        self.assertFalse(row['stock_within_reference'])
        self.assertFalse(row['concurrent_within_reference'])
        self.assertEqual(row['counted_present_scope'],'ordinary_token_card_spawns')
        self.assertIsNone(row['actual_deployable'])
        self.assertEqual((training,args),before)
        self.assertTrue(any('自动额外棋子' in note for note in r['notes']))

    def test_unknown_stock_and_present_remain_unknown(self):
        row=token_budget(OP,{}, {TOKEN:{'additional':1,'present':None,'available_stock':None}},9)['rows'][0]
        self.assertIsNone(row['stock_within_reference'])
        self.assertIsNone(row['stock_sufficient_declared'])
        self.assertIsNone(row['concurrent_within_reference'])

    def test_counts_do_not_leak_to_other_identity_or_module(self):
        p=catalog()['operators'][OP]
        self.assertIsNone(token_count_reference(p,{'operator':'char_110_deepcl'},TOKEN))
        self.assertIsNone(token_count_reference(p,{'operator':OP},'unknown'))
        r=counts(module_id='uniequip_002_deepcl',module_level=3)
        self.assertFalse(r['module_applied']);self.assertEqual(r['concurrent_limit'],6)

    def test_result_mutations_do_not_pollute_cached_sources(self):
        before=copy.deepcopy(count_rules())
        r=counts(potential=6,module_id=MODULE,module_level=3)
        r['sources'].clear();r['base_counts']['held_base']=999
        self.assertEqual(counts()['held_limit'],7)
        self.assertEqual(count_rules(),before)

if __name__=='__main__':unittest.main()
