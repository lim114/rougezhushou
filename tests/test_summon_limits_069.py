import copy
import unittest
from unittest.mock import patch
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.summons import module_rules,token_concurrent_limit

OP='char_110_deepcl';TOKEN='token_10001_deepcl_tentac';MOD='uniequip_002_deepcl'
POEM='rogue_6_relic_legacy_134';PERFUME='rogue_6_relic_legacy_91'

class SummonLimitTests(unittest.TestCase):
    def scenario(self,**kw):
        return dict(operator=OP,skill=1,elite=2,level=70,module_id=MOD,module_level=3,**kw)
    def component(self,r):return next(c for c in r['components'] if c['name']=='触手')

    def test_all_module_stages_and_skills_allow_seven_selected_tokens(self):
        for stage in (1,2,3):
            for skill in (1,2):
                base=self.scenario();base.update(module_level=stage,skill=skill)
                one=calculate_damage({**base,'summon_count':1})
                seven=calculate_damage({**base,'summon_count':7})
                a,b=self.component(one),self.component(seven)
                self.assertEqual(b['total'],a['total']*7)
                self.assertEqual(b['hits'],a['hits']*7)
                self.assertEqual(b['per_hit'],a['per_hit'])
                for key in ('duration_seconds','initial_seconds','recharge_seconds','cycle_seconds'):
                    self.assertEqual(one['estimate']['skill'][key],seven['estimate']['skill'][key])

    def test_no_module_cap_follows_actual_elite_stage(self):
        profile=catalog()['operators'][OP]
        for elite,cap in ((0,2),(1,3),(2,4)):
            s=self.scenario();s.update(elite=elite,level=profile['phases'][elite]['max_level'],
                skill_rank=7 if elite<2 else 10,module_id=None,module_level=0)
            self.assertEqual(token_concurrent_limit(profile,s,TOKEN),cap)
            one=calculate_damage({**s,'summon_count':1})
            r=calculate_damage({**s,'summon_count':cap})
            self.assertEqual(self.component(r)['total'],cap*self.component(one)['total'])
            with self.assertRaises(ValueError):calculate_damage({**s,'summon_count':cap+1})

    def test_module_unlock_level_changes_cap_without_changing_elite(self):
        profile=catalog()['operators'][OP]
        for level,cap in ((39,4),(40,7)):
            s={**self.scenario(),'level':level,'summon_count':cap}
            self.assertEqual(token_concurrent_limit(profile,s,TOKEN),cap)
            calculate_damage(s)
            with self.assertRaises(ValueError):calculate_damage({**s,'summon_count':cap+1})

    def test_unpromoted_run_cannot_use_account_module_capacity(self):
        s={**self.scenario(),'elite':1,'level':60,'skill_rank':7,'summon_count':3}
        self.assertEqual(token_concurrent_limit(catalog()['operators'][OP],s,TOKEN),3)
        calculate_damage(s)
        with self.assertRaises(ValueError):calculate_damage({**s,'summon_count':4})

    def test_invalid_counts_are_rejected_at_public_entry(self):
        for count in (-1,8,1.5,float('inf'),float('nan')):
            with self.assertRaises(ValueError):calculate_damage({**self.scenario(),'summon_count':count})

    def test_default_is_one_and_explicit_zero_removes_only_token_output(self):
        default=calculate_damage(self.scenario())
        self.assertEqual(self.component(default),self.component(calculate_damage({**self.scenario(),'summon_count':1})))
        zero=calculate_damage({**self.scenario(),'summon_count':0})
        self.assertEqual(self.component(zero)['total'],0)
        own=lambda r:next(c for c in r['components'] if c['name']=='本体普攻')
        self.assertEqual(own(default),own(zero))

    def test_inventory_alone_never_determines_concurrent_cap(self):
        rules=copy.deepcopy(module_rules());rules[MOD]['stages']['3']['stock_add']=999
        s=self.scenario();p=catalog()['operators'][OP]
        with patch('rouge.summons.module_rules',return_value=rules):
            self.assertEqual(token_concurrent_limit(p,s,TOKEN),7)
        rules[MOD]['concurrent_limit_verified']=False
        with patch('rouge.summons.module_rules',return_value=rules):
            self.assertIsNone(token_concurrent_limit(p,s,TOKEN))
        self.assertIsNone(token_concurrent_limit(p,s,'unknown_token'))

    def test_seven_token_relic_outputs_keep_per_token_hp_and_regeneration(self):
        base={**self.scenario(),'relic_ids':[POEM,PERFUME]}
        one=calculate_damage({**base,'summon_count':1});seven=calculate_damage({**base,'summon_count':7})
        t=next(t for t in seven['relic_token_stats'] if t['id']==TOKEN)
        self.assertAlmostEqual(t['hp'],3014.15);self.assertAlmostEqual(t['regeneration_rate'],30.1415)
        self.assertEqual(self.component(seven)['total'],7*self.component(one)['total'])
        rows=next(s for s in seven['report']['sections'] if s['id']=='regeneration')['metrics']
        values={m['key']:m['value'] for m in rows}
        self.assertEqual(values['all_tokens_rate'],values['per_token_rate']*7)

    def test_report_separates_selected_count_from_verified_cap_and_slots(self):
        s={**self.scenario(),'summon_count':5};before=copy.deepcopy(s);r=calculate_damage(s)
        self.assertEqual(s,before)
        for kind in ('summons','relic_token_'+TOKEN):
            section=next(b for b in r['report']['sections'] if b['id']==kind)
            values={m['key']:m['value'] for m in section['metrics']}
            self.assertEqual(values['concurrent_limit'],7)
        text=str(r['report'])
        self.assertIn('局外假设',text);self.assertIn('关卡可用部署位',text)
        self.assertNotIn('最多4个',text);self.assertNotIn('实际同时在场限制未核验',text)

if __name__=='__main__':unittest.main()
