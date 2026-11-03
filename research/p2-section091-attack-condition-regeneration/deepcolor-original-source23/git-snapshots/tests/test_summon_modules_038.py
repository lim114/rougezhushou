import copy
import unittest
from rouge.damage import calculate_damage
from rouge.catalog import catalog
from rouge.summons import token_attributes

OP='char_110_deepcl';TOKEN='token_10001_deepcl_tentac';MODULE='uniequip_002_deepcl'
POEM='rogue_6_relic_legacy_134';PERFUME='rogue_6_relic_legacy_91';MEAT='rogue_6_relic_legacy_22'

class SummonModuleTests(unittest.TestCase):
    def scenario(self,**extra):
        return {'operator':OP,'skill':1,'elite':2,'level':70,
                'module_id':MODULE,'module_level':3,**extra}

    def token(self,result):
        return next(t for t in result['relic_token_stats'] if t['id']==TOKEN)

    def component(self,result):
        return next(c for c in result['components'] if c['name']=='触手')

    def section(self,result,kind):
        return next(b for b in result['report']['sections'] if b['id']==kind)

    def test_all_stages_have_documented_cost_stock_and_hp(self):
        for stage,hp in ((1,2016),(2,2217.6),(3,2318.4)):
            t=self.token(calculate_damage(self.scenario(module_level=stage)))
            self.assertAlmostEqual(t['hp'],hp)
            self.assertEqual(t['deployment_cost'],3)
            self.assertEqual(t['module_reference']['held_limit'],7)
            self.assertEqual(t['module_reference']['concurrent_limit'],7)

    def test_unlock_boundary_uses_actual_elite_and_level(self):
        low=calculate_damage(self.scenario(level=39))
        self.assertEqual(low['relic_token_stats'],[])
        t=self.token(calculate_damage(self.scenario(level=40)))
        self.assertAlmostEqual(t['hp'],2112.55)
        self.assertEqual(t['attack'],432)
        self.assertEqual(t['deployment_cost'],3)

    def test_unpromoted_run_does_not_apply_account_module(self):
        r=calculate_damage(self.scenario(elite=1,level=60,skill_rank=7,relic_ids=[POEM]))
        t=self.token(r)
        self.assertNotIn('module_reference',t)
        self.assertIsNotNone(t['hp'])
        self.assertEqual(t['deployment_cost'],0)

    def test_no_module_does_not_create_module_panel(self):
        r=calculate_damage(self.scenario(module_id=None,module_level=0))
        self.assertEqual(r['relic_token_stats'],[])
        self.assertNotIn('held_limit',str(r['report']))

    def test_all_skills_and_ranks_use_same_token_cultivation(self):
        for skill in (1,2):
            for rank in range(1,11):
                t=self.token(calculate_damage(self.scenario(skill=skill,skill_rank=rank)))
                self.assertAlmostEqual(t['hp'],2318.4)
                self.assertEqual((t['attack'],t['defense'],t['deployment_cost']),(462,335,3))

    def test_owner_trust_and_potential_do_not_change_token_stats(self):
        a=calculate_damage(self.scenario(trust=0,potential=1))
        b=calculate_damage(self.scenario(trust=100,potential=6))
        self.assertEqual(self.token(a),self.token(b))
        self.assertNotEqual(a['estimate']['base_stats'],b['estimate']['base_stats'])

    def test_owner_module_attack_does_not_leak_to_tentacle(self):
        base=calculate_damage(self.scenario(module_id=None,module_level=0))
        equipped=calculate_damage(self.scenario())
        self.assertEqual(self.component(base),self.component(equipped))
        self.assertGreater(equipped['estimate']['base_stats']['attack'],base['estimate']['base_stats']['attack'])

    def test_held_limit_does_not_automatically_multiply_output(self):
        single=calculate_damage(self.scenario(summon_count=1))
        four=calculate_damage(self.scenario(summon_count=4))
        self.assertEqual(self.component(four)['total'],4*self.component(single)['total'])
        self.assertEqual(self.token(four)['module_reference']['held_limit'],7)

    def test_zero_selected_tokens_produce_no_token_damage(self):
        r=calculate_damage(self.scenario(summon_count=0))
        self.assertEqual(self.component(r)['total'],0)
        self.assertGreater(r['total_damage'],0)

    def test_verified_module_cap_is_separate_from_global_deployment_slots(self):
        calculate_damage(self.scenario(summon_count=7))
        with self.assertRaises(ValueError):calculate_damage(self.scenario(summon_count=8))
        text=str(self.section(calculate_damage(self.scenario()),'relic_token_'+TOKEN))
        self.assertIn('关卡可用部署位',text)
        self.assertNotIn('实际同时在场限制未核验',text)

    def test_stage_one_and_poem_have_known_hp_and_cost(self):
        t=self.token(calculate_damage(self.scenario(module_level=1,relic_ids=[POEM])))
        self.assertEqual(t['hp'],2621) # raw rune round-even(2016*1.3)
        self.assertEqual(t['deployment_cost'],0)
        self.assertFalse(t['module_reference']['hp_composition_pending'])
        self.assertTrue(t['free_deployment_slot'])

    def test_module_poem_composite_hp_uses_verified_talent_layer(self):
        r=calculate_damage(self.scenario(relic_ids=[POEM]));t=self.token(r)
        self.assertAlmostEqual(t['hp'],3014.15)
        self.assertAlmostEqual(t['module_reference']['module_only_hp'],2318.4)
        self.assertEqual(t['module_reference']['other_sources_only_hp'],2621)
        self.assertFalse(t['module_reference']['hp_composition_pending'])
        self.assertIsNotNone(r['estimate']['skill']['total_damage'])
        self.assertIsNotNone(r['estimate']['skill']['cycle_dps'])

    def test_squad_hp_requires_verified_effect_before_module_composition(self):
        config={'squad':{'id':'rogue_6_band_6','effect_verified':True}}
        r=calculate_damage(self.scenario(run_config=config));t=self.token(r)
        base=self.token(calculate_damage(self.scenario(module_id=None,module_level=0,run_config=config)))
        self.assertEqual(t['module_reference']['other_sources_only_hp'],base['hp'])
        self.assertAlmostEqual(t['hp'],base['hp']*1.15)
        config['squad']['effect_verified']=False
        self.assertAlmostEqual(self.token(calculate_damage(self.scenario(run_config=config)))['hp'],2318.4)

    def test_percentage_regeneration_uses_known_module_hp(self):
        r=calculate_damage(self.scenario(relic_ids=[PERFUME]));t=self.token(r)
        self.assertAlmostEqual(t['regeneration_rate'],23.184)

    def test_verified_composite_hp_supplies_percentage_regeneration(self):
        r=calculate_damage(self.scenario(relic_ids=[POEM,PERFUME]));t=self.token(r)
        self.assertAlmostEqual(t['regeneration_rate'],30.1415)
        rows=self.section(r,'relic_token_'+TOKEN)['metrics']
        self.assertAlmostEqual(next(m for m in rows if m['key']=='regeneration_rate')['value'],30.1415)

    def test_fixed_regeneration_and_s1_remain_independent_of_hp(self):
        r=calculate_damage(self.scenario(relic_ids=[POEM,MEAT]));t=self.token(r)
        self.assertEqual(t['regeneration_rate'],3)
        rows=self.section(r,'regeneration')['metrics']
        self.assertEqual(next(m for m in rows if m['key']=='per_token_rate')['value'],70)

    def test_calculation_keeps_input_and_cached_rules_isolated(self):
        s=self.scenario(relic_ids=[POEM]);original=copy.deepcopy(s)
        a=calculate_damage(s);self.assertEqual(s,original)
        self.token(a)['module_reference']['held_limit']=999
        self.assertEqual(self.token(calculate_damage(s))['module_reference']['held_limit'],7)

    def test_engine_and_reporting_share_independent_token_profile(self):
        p=catalog()['operators'][OP]
        t=token_attributes(p,self.scenario(),TOKEN)
        reported=self.token(calculate_damage(self.scenario()))
        for k in ('hp','attack','defense','resistance','deployment_cost','interval','block_count','redeploy_seconds'):
            self.assertEqual(t[k],reported[k],k)

if __name__=='__main__':unittest.main()
