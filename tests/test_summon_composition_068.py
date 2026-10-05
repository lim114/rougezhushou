import copy
import unittest
from unittest.mock import patch
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.summons import module_rules,token_attributes

OP='char_110_deepcl';TOKEN='token_10001_deepcl_tentac';MOD='uniequip_002_deepcl'
POEM='rogue_6_relic_legacy_134';PERFUME='rogue_6_relic_legacy_91'

class SummonCompositionTests(unittest.TestCase):
    def scenario(self,**kw):return dict(operator=OP,skill=1,elite=2,level=70,module_id=MOD,module_level=3,**kw)
    def token(self,r):return next(t for t in r['relic_token_stats'] if t['id']==TOKEN)

    def test_rune_rounding_precedes_all_three_module_stages(self):
        for level in (40,41,57,70):
            for stage,pct in ((1,0),(2,.1),(3,.15)):
                s=self.scenario(relic_ids=[POEM]);s.update(level=level,module_level=stage)
                old=self.scenario(relic_ids=[POEM]);old.update(level=level,module_level=0,module_id=None)
                base=self.token(calculate_damage(old))['hp']
                token=self.token(calculate_damage(s))
                self.assertAlmostEqual(token['hp'],base*(1+pct))
                self.assertFalse(token['module_reference']['hp_composition_pending'])

    def test_rune_and_squad_add_before_module(self):
        s=self.scenario(relic_ids=[POEM,PERFUME],run_config={'squad':{'id':'rogue_6_band_6','effect_verified':True}})
        base=calculate_damage({**s,'module_id':None,'module_level':0})
        r=calculate_damage(s);a=self.token(base);b=self.token(r)
        self.assertAlmostEqual(b['hp'],a['hp']*1.15)
        self.assertAlmostEqual(b['regeneration_rate'],b['hp']*.01)
        self.assertFalse(any('叠加层尚未核验' in w for w in r.get('warnings',[])))

    def test_ordinary_hp_shares_multiplier_instead_of_multiplying(self):
        p=catalog()['operators'][OP];s=self.scenario()
        for ordinary in (.25,-.25,-1.2):
            t=token_attributes(p,s,TOKEN,ordinary,rune_effects=[{'kind':'hp_pct','value':.3,
                'attribute_layer':'relic_rune','formula_item':'MULTIPLIER'}])
            self.assertAlmostEqual(t['hp'],2621*max(0,1+ordinary+.15))

    def test_hp_resolution_does_not_change_attack_or_skill_timing(self):
        for skill in (1,2):
            s={**self.scenario(relic_ids=[POEM,PERFUME]),'skill':skill}
            base=calculate_damage({**s,'module_id':None,'module_level':0});r=calculate_damage(s)
            a=self.token(base);b=self.token(r)
            self.assertEqual((a['attack'],a['defense'],a['attack_speed']),(b['attack'],b['defense'],b['attack_speed']))
            for key in ('duration_seconds','initial_seconds','recharge_seconds','cycle_seconds'):
                self.assertEqual(base['estimate']['skill'][key],r['estimate']['skill'][key])
            self.assertEqual(next(c for c in base['components'] if c['name']=='触手'),next(c for c in r['components'] if c['name']=='触手'))

    def test_unverified_rules_still_refuse_composite_hp(self):
        rules=copy.deepcopy(module_rules());rules[MOD]['hp_composition_verified']=False
        with patch('rouge.summons.module_rules',return_value=rules):
            t=token_attributes(catalog()['operators'][OP],self.scenario(),TOKEN,.3)
        self.assertIsNone(t['hp']);self.assertTrue(t['module_reference']['hp_composition_pending'])

    def test_report_shows_predicted_hp_without_isolated_unknowns(self):
        r=calculate_damage(self.scenario(relic_ids=[POEM,PERFUME]))
        section=next(s for s in r['report']['sections'] if s['id']=='relic_token_'+TOKEN)
        metrics={m['key']:m['value'] for m in section['metrics']}
        self.assertAlmostEqual(metrics['hp'],3014.15)
        self.assertAlmostEqual(metrics['regeneration_rate'],30.1415)
        self.assertNotIn('module_only_hp',metrics);self.assertNotIn('other_sources_only_hp',metrics)
        self.assertTrue(any('再计入模组天赋' in note for note in section['notes']))

if __name__=='__main__':unittest.main()
