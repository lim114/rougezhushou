import copy
import json
import unittest
from pathlib import Path

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.summons import token_attributes,token_cost_reference,token_concurrent_limit

OP='char_2027_wang'
TOKEN='token_10064_wang_stone1'
MODULE='uniequip_002_wang'
PERFUME='rogue_6_relic_legacy_91'
POEM='rogue_6_relic_legacy_134'

def scenario(**extra):
    return {'operator':OP,'skill':1,'elite':2,'level':80,
            'module_id':MODULE,'module_level':1,**extra}


class WangTokenModuleReferenceTests(unittest.TestCase):
    def token(self,result):return next(t for t in result['relic_token_stats'] if t['id']==TOKEN)

    def test_all_unlocked_stages_reduce_only_token_cultivation_cost(self):
        base=token_attributes(catalog()['operators'][OP],scenario(module_id=None,module_level=0),TOKEN)
        for stage in (1,2,3):
            token=self.token(calculate_damage(scenario(module_level=stage)))
            self.assertEqual(token['deployment_cost'],2)
            self.assertEqual(token['module_cost_reference']['base_cost'],3)
            self.assertEqual(token['module_cost_reference']['cost_add'],-1)
            for key in ('hp','attack','defense','resistance','attack_speed','redeploy_seconds','block_count'):
                self.assertEqual(token[key],base[key])
            self.assertNotIn('module_reference',token)

    def test_module_unlock_boundary_and_absent_module_keep_three_cost(self):
        for args in (scenario(level=59),scenario(elite=1,level=80,skill_rank=7),
                     scenario(elite=0,level=50,skill_rank=7),scenario(module_id=None,module_level=0)):
            with self.subTest(scenario=args):
                result=calculate_damage({**args,'relic_ids':[PERFUME]})
                token=self.token(result)
                self.assertEqual(token['deployment_cost'],3)
                self.assertNotIn('module_cost_reference',token)
        token=self.token(calculate_damage(scenario(level=60)))
        self.assertEqual(token['deployment_cost'],2)

    def test_all_skills_and_ranks_share_the_same_cultivation_reference(self):
        for skill in (1,2,3):
            for rank in (1,7,10):
                for mode in ('frames','continuous'):
                    result=calculate_damage(scenario(skill=skill,skill_rank=rank,timing_mode=mode,module_level=3))
                    self.assertEqual(self.token(result)['deployment_cost'],2)

    def test_relic_cost_and_regeneration_keep_existing_independent_effects(self):
        token=self.token(calculate_damage(scenario(relic_ids=[PERFUME])))
        self.assertEqual(token['deployment_cost'],2)
        self.assertEqual(token['modifier_sources'],['模组','藏品'])
        self.assertEqual(token['hp'],1000)
        self.assertEqual(token['regeneration_rate'],10)
        poem=self.token(calculate_damage(scenario(relic_ids=[POEM,PERFUME])))
        self.assertEqual(poem['deployment_cost'],0)
        self.assertEqual(poem['hp'],1300)
        self.assertEqual(poem['attack'],130)
        self.assertEqual(poem['regeneration_rate'],13)
        self.assertTrue(poem['free_deployment_slot'])

    def test_owner_potential_trust_and_module_attack_do_not_change_token_stats(self):
        low=self.token(calculate_damage(scenario(potential=1,trust=0,module_level=1)))
        high=self.token(calculate_damage(scenario(potential=6,trust=100,module_level=3)))
        for key in ('hp','attack','defense','attack_speed','deployment_cost'):
            self.assertEqual(low[key],high[key])
        self.assertEqual(high['attack'],100)

    def test_exact_operator_module_and_token_pair_does_not_leak(self):
        p=catalog()['operators'][OP]
        self.assertIsNone(token_cost_reference(p,scenario(module_id='uniequip_002_deepcl'),TOKEN))
        self.assertIsNone(token_cost_reference(p,scenario(),'token_10001_deepcl_tentac'))
        deep=catalog()['operators']['char_110_deepcl']
        self.assertIsNone(token_cost_reference(deep,scenario(),TOKEN))
        self.assertIsNone(token_cost_reference(p,scenario(module_level=0),TOKEN))
        result=calculate_damage({'operator':'char_110_deepcl','skill':1,'elite':2,'level':70,
            'module_id':'uniequip_002_deepcl','module_level':3})
        token=result['relic_token_stats'][0]
        self.assertEqual(token['deployment_cost'],3)
        self.assertEqual(token['module_reference']['concurrent_limit'],7)
        self.assertNotIn('module_cost_reference',token)

    def test_reference_does_not_bind_deployment_limits_lifecycle_or_damage(self):
        r=token_cost_reference(catalog()['operators'][OP],scenario(),TOKEN)
        self.assertIsNone(r['actual_deployment_count'])
        self.assertIsNone(r['actual_alive_seconds'])
        self.assertFalse(r['live_state_verified'])
        self.assertIsNone(token_concurrent_limit(catalog()['operators'][OP],scenario(),TOKEN))
        self.assertNotIn('held_limit',r)
        self.assertNotIn('concurrent_limit',r)
        base=calculate_damage(scenario(module_id=None,module_level=0,base_attack=1000))
        equipped=calculate_damage(scenario(base_attack=1000))
        for key in ('total_damage','timing','components'):
            self.assertEqual(base[key],equipped[key])

    def test_no_relic_still_exposes_the_known_module_cost_panel(self):
        result=calculate_damage(scenario())
        self.assertEqual(self.token(result)['modifier_sources'],['模组'])
        block=next(s for s in result['report']['sections'] if s['id']=='relic_token_'+TOKEN)
        metrics={m['key']:m['value'] for m in block['metrics']}
        self.assertEqual(metrics['cost'],2)
        self.assertEqual(metrics['module_cost_add'],-1)
        self.assertNotIn('held_limit',metrics)
        self.assertNotIn('concurrent_limit',metrics)
        self.assertIn('额外部署数',str(block))
        self.assertIn('仍未核验',str(block))
        self.assertNotIn('触手',str(block))

    def test_locked_module_alone_does_not_create_a_panel(self):
        for args in (scenario(level=59),scenario(module_id=None,module_level=0)):
            result=calculate_damage(args)
            self.assertEqual(result['relic_token_stats'],[])
            self.assertNotIn('relic_token_'+TOKEN,str(result['report']))

    def test_cached_reference_and_input_are_isolated(self):
        args=scenario();original=copy.deepcopy(args)
        r=token_cost_reference(catalog()['operators'][OP],args,TOKEN)
        r['sources']['battle_equip_table']['sha256']='changed'
        public=calculate_damage(args)
        self.token(public)['module_cost_reference']['cost_add']=100
        self.assertEqual(args,original)
        self.assertEqual(self.token(calculate_damage(args))['deployment_cost'],2)
        self.assertEqual(len(token_cost_reference(catalog()['operators'][OP],args,TOKEN)['sources']['battle_equip_table']['sha256']),64)

    def test_shared_api_and_public_result_have_identical_module_cost(self):
        args=scenario(module_level=2)
        attrs=token_attributes(catalog()['operators'][OP],args,TOKEN)
        public=self.token(calculate_damage(args))
        self.assertEqual(attrs['module_cost_reference'],public['module_cost_reference'])
        self.assertEqual(attrs['deployment_cost'],public['deployment_cost'])

    def test_persisted_parameter_is_pinned_and_keeps_exact_source_selectors(self):
        data=json.loads((Path(__file__).resolve().parents[1]/'rouge/data/token-module-cost-reference.json').read_text())
        self.assertEqual(data['source_commit'],'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add')
        rule,=data['rules']
        self.assertEqual((rule['module_unlock_elite'],rule['module_unlock_level']),(2,60))
        self.assertEqual([r['cost_add'] for r in rule['stages']],[-1,-1,-1])
        self.assertIn('phases[2].tokenAttributeBlackboard.token_10064_wang_stone1[0]',rule['stages'][2]['source_selector'])
        self.assertEqual(data['sources']['battle_equip_table']['sha256'],'006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460')


if __name__=='__main__':unittest.main()
