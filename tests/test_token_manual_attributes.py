import copy
import unittest
from unittest.mock import patch

from rouge.damage import calculate_damage
from rouge.summons import manual_token_effects,manual_token_stat_effects,module_rules

OP='char_110_deepcl';TOKEN='token_10001_deepcl_tentac';MODULE='uniequip_002_deepcl'
PERFUME='rogue_6_relic_legacy_91';POEM='rogue_6_relic_legacy_134'


def scenario(**extra):
    return {'operator':OP,'skill':1,'elite':2,'level':70,'module_id':MODULE,'module_level':3,
            'window_seconds':10,**extra}


def effect(kind,value,**extra):return {'kind':kind,'value':value,'target_scope':'all_units',**extra}


class TokenManualAttributesTests(unittest.TestCase):
    def token(self,result):return next(t for t in result['relic_token_stats'] if t['id']==TOKEN)
    def component(self,result):return next(c for c in result['components'] if c['name']=='触手')

    def test_ordinary_manual_hp_uses_verified_module_layer_and_percentage_regeneration(self):
        result=calculate_damage(scenario(effects=[effect('hp_pct',.5)],relic_ids=[PERFUME]))
        token=self.token(result)
        self.assertAlmostEqual(token['hp'],2016*(1+.5+.15))
        self.assertAlmostEqual(token['regeneration_rate'],33.264)
        self.assertAlmostEqual(token['module_reference']['module_only_hp'],2318.4)
        self.assertEqual(token['module_reference']['other_sources_only_hp'],3024)
        self.assertFalse(token['module_reference']['hp_composition_pending'])

    def test_manual_attack_panel_matches_existing_combat_layer_without_moving_skill_bonus(self):
        result=calculate_damage(scenario(effects=[effect('attack_pct',.5)]))
        self.assertEqual(self.token(result)['attack'],693)
        self.assertAlmostEqual(self.component(result)['per_hit'],462*(1+.5+.6))
        normal=calculate_damage(scenario(skill=2,effects=[effect('attack_pct',.5)]))
        self.assertEqual(self.token(normal)['attack'],693)
        self.assertEqual(self.component(normal)['per_hit'],693)

    def test_manual_attack_speed_panel_matches_existing_token_interval(self):
        result=calculate_damage(scenario(effects=[effect('attack_speed',100)]))
        self.assertEqual(self.token(result)['attack_speed'],200)
        self.assertEqual(self.component(result)['hits'],15)
        baseline=calculate_damage(scenario())
        self.assertEqual(self.component(baseline)['hits'],7)
        self.assertEqual(self.component(result)['per_hit'],self.component(baseline)['per_hit'])

    def test_supplied_defense_and_resistance_have_explicit_all_unit_scope(self):
        result=calculate_damage(scenario(effects=[effect('defense_pct',.5),effect('resistance_flat',20)]))
        self.assertEqual(self.token(result)['defense'],502.5)
        self.assertEqual(self.token(result)['resistance'],20)
        capped=calculate_damage(scenario(effects=[effect('resistance_flat',200)]))
        self.assertEqual(self.token(capped)['resistance'],100)

    def test_manual_only_reference_creates_a_panel_without_relic_or_module(self):
        result=calculate_damage(scenario(module_id=None,module_level=0,effects=[effect('hp_pct',.5)]))
        token=self.token(result)
        self.assertEqual(token['hp'],3024)
        self.assertEqual(token['modifier_sources'],['手动输入'])
        block=next(s for s in result['report']['sections'] if s['id']=='relic_token_'+TOKEN)
        self.assertIn('手动输入',block['title'])
        self.assertEqual(next(m for m in block['metrics'] if m['key']=='hp')['value'],3024)
        self.assertNotIn('regeneration_rate',token)

    def test_operator_only_or_absent_scope_does_not_modify_token(self):
        base=calculate_damage(scenario(relic_ids=[PERFUME]));base_token=self.token(base)
        for scope in (None,'operator'):
            e={'kind':'hp_pct','value':.5}
            if scope is not None:e['target_scope']=scope
            result=calculate_damage(scenario(effects=[e],relic_ids=[PERFUME]))
            self.assertEqual(self.token(result),base_token)
            self.assertGreater(result['estimate']['base_stats']['hp'],base['estimate']['base_stats']['hp'])

    def test_token_ids_selector_matches_combat_and_panel(self):
        base=calculate_damage(scenario())
        absent=calculate_damage(scenario(effects=[effect('attack_pct',.5,token_ids=['token_10035_wisdel_wward'])]))
        present=calculate_damage(scenario(effects=[effect('attack_pct',.5,token_ids=[TOKEN])]))
        self.assertEqual(self.token(absent),self.token(base))
        self.assertEqual(self.component(absent),self.component(base))
        self.assertEqual(self.token(present)['attack'],693)
        self.assertAlmostEqual(self.component(present)['per_hit'],970.2)

    def test_shared_selector_preserves_existing_global_damage_taken_fallback(self):
        damage={'kind':'damage_taken','value':.2,'damage_type':'physical'}
        blocked={**damage,'profession':'caster'}
        scope=effect('attack_pct',.5,token_ids=[TOKEN])
        args={'effects':[damage,blocked,scope]}
        self.assertEqual(manual_token_effects(args,TOKEN),[damage,scope])
        self.assertEqual(manual_token_stat_effects(args,TOKEN),[scope])
        self.assertEqual(manual_token_effects(args,'other'),[damage])
        result=calculate_damage(scenario(effects=[damage]))
        base=calculate_damage(scenario())
        self.assertAlmostEqual(self.component(result)['per_hit'],self.component(base)['per_hit']*1.2)
        self.assertEqual(self.token(result),self.token(base))

    def test_non_attribute_all_unit_effect_alone_does_not_create_a_stat_panel(self):
        for e in (effect('damage_taken',.2,damage_type='physical'),effect('sp_recovery',.2)):
            result=calculate_damage(scenario(module_id=None,module_level=0,effects=[e]))
            self.assertEqual(result['relic_token_stats'],[])

    def test_relic_runes_and_squad_apply_once_before_ordinary_manual_hp(self):
        args=scenario(relic_ids=[POEM,PERFUME],effects=[effect('hp_pct',.5)],
            run_config={'squad':{'id':'rogue_6_band_6','effect_verified':True}})
        token=self.token(calculate_damage(args))
        # Both verified rune sources precede the manual ordinary layer and SUM-Y.
        baseline=self.token(calculate_damage({**args,'effects':[],'module_id':None,'module_level':0}))
        self.assertAlmostEqual(token['hp'],baseline['hp']*1.65)
        self.assertAlmostEqual(token['regeneration_rate'],token['hp']*.01)
        self.assertEqual(token['modifier_sources'].count('分队'),1)
        self.assertEqual(token['modifier_sources'].count('手动输入'),1)

    def test_run_squad_or_rune_markers_are_not_counted_as_manual_ordinary_stats(self):
        rune=effect('hp_pct',.3,attribute_layer='relic_rune',formula_item='MULTIPLIER')
        squad=effect('hp_pct',.3,origin='run_squad')
        self.assertEqual(manual_token_stat_effects({'effects':[rune,squad]},TOKEN),[])
        self.assertEqual(len(manual_token_effects({'effects':[rune,squad]},TOKEN)),2)

    def test_unverified_module_hp_layer_stays_unknown_in_panel_and_regeneration(self):
        rules=copy.deepcopy(module_rules());rules[MODULE]['hp_composition_verified']=False
        with patch('rouge.summons.module_rules',return_value=rules):
            result=calculate_damage(scenario(effects=[effect('hp_pct',.5)],relic_ids=[PERFUME]))
        token=self.token(result)
        self.assertIsNone(token['hp'])
        self.assertIsNone(token['regeneration_rate'])
        self.assertTrue(token['module_reference']['hp_composition_pending'])
        self.assertFalse(result['complete'])
        block=next(s for s in result['report']['sections'] if s['id']=='relic_token_'+TOKEN)
        self.assertIsNone(next(m for m in block['metrics'] if m['key']=='hp')['value'])
        self.assertIsNone(next(m for m in block['metrics'] if m['key']=='regeneration_rate')['value'])

    def test_manual_token_scope_does_not_change_cultivation_qualification_or_lifecycle(self):
        args={'operator':'mechanist','skill':1,'elite':0,'level':50,'skill_rank':7,
              'effects':[effect('hp_pct',.5)]}
        result=calculate_damage(args)
        self.assertEqual(result['token_duration_references'][0]['state'],'locked')
        self.assertIsNone(result['token_duration_references'][0]['actual_alive_seconds'])
        baseline=calculate_damage({**args,'effects':[],'relic_ids':[PERFUME]})
        self.assertEqual(result['relic_token_stats'][0]['hp'],baseline['relic_token_stats'][0]['hp']*1.5)

    def test_input_effects_token_selectors_and_cached_rules_are_immutable(self):
        args=scenario(effects=[effect('hp_pct',.5,token_ids=[TOKEN])],relic_ids=[PERFUME])
        original=copy.deepcopy(args);rules=copy.deepcopy(module_rules())
        a=calculate_damage(args);a['relic_token_stats'][0]['module_reference']['hp_pct']=99
        selected=manual_token_effects(args,TOKEN);selected[0]['token_ids'].append('changed')
        self.assertEqual(args,original)
        self.assertEqual(module_rules(),rules)
        self.assertAlmostEqual(self.token(calculate_damage(args))['hp'],3326.4)


if __name__=='__main__':unittest.main()
