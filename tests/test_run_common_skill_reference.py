"""Sealed native rank-use gates and opt-in shared common-rank calculation."""
from copy import deepcopy
import unittest

from rouge.catalog import catalog,operator_profiles
from rouge.damage import calculate_damage
from rouge.run_common_skill_reference import source,use_qualification,shared_common_reference,format_reference
from rouge.skill_cultivation import select_rank,rank_label,explanation,format_explanation
from rouge.training_view import select_training_view

OP='char_298_susuro'


def record(ranks=None,elite=1,**extra):
    return {'id':OP,'scope':'run','fields':{'elite':elite,'level':40},
            'run_confirmed_fields':['elite','level'],'skill_ranks':ranks or {'1':3},**extra}


class RunCommonSkillReferenceTests(unittest.TestCase):
    def choose(self,state=None,skill=2,elite=1,enabled=True,profile=None,**extra):
        state=state or record()
        before=deepcopy((state,profile,extra))
        result=select_rank(profile or catalog()['operators'][OP],skill,elite,state=state,
                           run_common_reference=enabled,level=40,**extra)
        self.assertEqual((state,profile,extra),before)
        return result

    def test_all431_profiles949_skills_bind_exactly_without_borrowing_patch_forms(self):
        profiles=operator_profiles();data=source()['operators']
        self.assertEqual(len(profiles),431)
        self.assertEqual(sum(len(p['skills']) for p in profiles.values()),949)
        self.assertEqual(len(data),431)
        for key,p in profiles.items():
            raw=data[p['id']]
            self.assertEqual(len(raw['skills']),len(p['skills']))
            for index,(skill,bound) in enumerate(zip(p['skills'],raw['skills'])):
                self.assertEqual(skill['id'],bound['skill_id'])
                gate=use_qualification(p,index+1,1,skill.get('unlock_elite',index),1)
                self.assertTrue(gate['native_static_rule_verified'])
                self.assertEqual(gate['gate'],bound['unlock_cond'])
        for native in ('char_1001_amiya2','char_1037_amiya3'):
            self.assertTrue(data[native]['skills'][0]['original_path'].startswith('char_patch_table.patchChars.'))

    def test_native_common_use_gate_is_skill_unlock_not_common_upgrade_gate(self):
        p=catalog()['operators'][OP]
        for rank in (5,6,7):
            gate=use_qualification(p,1,rank,0,1)
            self.assertTrue(gate['available']);self.assertEqual(gate['gate'],{'phase':'PHASE_0','level':1})
            self.assertTrue(gate['path'].endswith('.skills[0].unlockCond'))
            self.assertFalse(use_qualification(p,2,rank,0,1)['available'])
        self.assertFalse(use_qualification(p,1,7,0,0)['available'])
        self.assertFalse(use_qualification(p,1,8,1,40)['available'])
        self.assertTrue(use_qualification(p,1,8,2,1)['available'])

    def test_default_and_cancellation_preserve_original_unconfirmed_rank(self):
        plain=self.choose(enabled=False)
        picked=self.choose()
        self.assertEqual(plain['rank'],7);self.assertEqual(plain['source'],'preview_unconfirmed')
        self.assertEqual(picked['rank'],3);self.assertEqual(picked['source'],'manual_run_common_reference')
        self.assertFalse(picked['known']);self.assertTrue(picked['common_reference_applied'])
        self.assertIn('局外模拟',rank_label(picked));self.assertNotIn('（读取）',rank_label(picked))
        self.assertEqual(self.choose(enabled=False),plain)

    def test_directly_observed_selected_rank_is_never_replaced(self):
        selected=self.choose(state=record({'1':3,'2':3}))
        self.assertEqual(selected['rank'],3);self.assertEqual(selected['source'],'run_confirmed')
        self.assertFalse(selected['common_reference_applied']);self.assertFalse(selected['common_reference_usable'])

    def test_no_account_only_unconfirmed_elite_or_other_operator_source(self):
        for state in (record(scope='account'),record(run_confirmed_fields=[]),
                      record(invalid_fields=['elite']),record(id='mechanist'),
                      record(fields={'elite':0,'level':40})):
            selected=self.choose(state=state,account={'scope':'account','skill_ranks':{'1':5}})
            self.assertEqual(selected['rank'],7);self.assertFalse(selected['common_reference_applied'])

    def test_actual_training_view_keeps_account_grades_out_of_run_source(self):
        account={'id':OP,'scope':'operator_profile','fields':{'elite':2,'level':70},
                 'skill_ranks':{'1':7,'2':10}}
        member=record(present=True)
        view=select_training_view(OP,account,member,operator_profiles(),catalog()['operators'])['state']
        self.assertEqual(view['scope'],'run');self.assertEqual(view['skill_ranks'],{'1':3})
        selected=self.choose(state=view,account=account)
        self.assertEqual(selected['rank'],3);self.assertTrue(selected['common_reference_applied'])
        member['present']=None
        fallback=select_training_view(OP,account,member,operator_profiles(),catalog()['operators'])['state']
        self.assertEqual(fallback['scope'],'operator_profile')
        self.assertFalse(self.choose(state=fallback,account=account)['common_reference_applied'])

    def test_invalid_masked_and_mastery_sources_never_supply_public_rank(self):
        for ranks in ({'1':True},{'1':False},{'1':7.0},{'1':'7'},{'1':8},{'1':10},{'1':0},{'1':11},{'1':{}},{'1':[]}):
            self.assertFalse(self.choose(state=record(ranks))['common_reference_usable'])
        for invalid in (['1'],[1]):
            self.assertFalse(self.choose(state=record(invalid_skill_ranks=invalid))['common_reference_usable'])

    def test_source_conflicts_and_locked_skill_sources_do_not_resolve_missing_rank(self):
        p=catalog()['operators']['mechanist']
        state={'id':'mechanist','scope':'run','fields':{'elite':1,'level':40},
               'run_confirmed_fields':['elite','level'],'skill_ranks':{'1':3,'2':5}}
        r=shared_common_reference(p,1,40,state)
        self.assertFalse(r['usable']);self.assertEqual(r['candidate_ranks'],[3,5])
        state['skill_ranks']={'3':5}
        self.assertFalse(shared_common_reference(p,1,40,state)['usable'])
        state['skill_ranks']={'1':3,'3':5}
        r=shared_common_reference(p,1,40,state)
        self.assertTrue(r['usable']);self.assertEqual(r['rank'],3)
        self.assertFalse(r['all_skill_qualifications'][2]['qualification']['available'])

    def test_elite2_missing_mastery_and_account_mastery_are_not_truncated(self):
        selected=self.choose(elite=2,state=record({'1':7},elite=2))
        self.assertEqual(selected['rank'],10);self.assertFalse(selected['common_reference_applied'])
        selected=self.choose(account={'scope':'account','skill_ranks':{'2':10}},account_reference=True,enabled=False)
        self.assertEqual(selected['rank'],7);self.assertFalse(selected['manual_reference_applied'])
        self.assertIn('不会自动改成7级',selected['account_reason'])

    def test_account_explicit_reference_has_clear_precedence(self):
        selected=self.choose(account={'scope':'account','skill_ranks':{'2':5}},account_reference=True)
        self.assertEqual(selected['rank'],5);self.assertTrue(selected['manual_reference_applied'])
        self.assertFalse(selected['common_reference_applied'])

    def test_string_key_priority_and_full_skill_qualifications(self):
        r=self.choose(state=record({'1':5,1:3}))
        self.assertEqual(r['rank'],5)
        refs=r['common_reference']['all_skill_qualifications']
        self.assertEqual([x['rank'] for x in refs],[5,5])
        self.assertEqual([x['directly_observed'] for x in refs],[True,False])
        self.assertTrue(all(x['qualification']['available'] for x in refs))
        self.assertIn('S2',format_reference(r['common_reference']))
        self.assertIsNone(r['common_reference']['actual_unread_skill_ranks'])

    def test_original_identity_drift_disables_projection(self):
        p=deepcopy(catalog()['operators'][OP]);p['skills'][0]['id']='unknown_public_skill'
        selected=self.choose(profile=p)
        self.assertFalse(selected['common_reference_usable'])
        self.assertIsNone(use_qualification(p,2,5,1,40)['available'])

    def test_selected_common_rank_changes_real_healing_and_skill_budget(self):
        params={'operator':OP,'skill':2,'elite':1,'level':40,'trust':0,'potential':1,
                'window_seconds':10,'continuous_attacks':True,'healing_targets':1}
        plain=calculate_damage({**params,'skill_rank':self.choose(enabled=False)['rank']})
        selected=calculate_damage({**params,'skill_rank':self.choose()['rank']})
        self.assertNotEqual(selected['components'],plain['components'])
        self.assertNotEqual(selected['estimate']['skill']['recharge_seconds'],plain['estimate']['skill']['recharge_seconds'])
        self.assertEqual(calculate_damage({**params,'skill_rank':self.choose(enabled=False)['rank']}),plain)

    def test_explanation_retains_actual_unknown_and_training_use_separation(self):
        selected=self.choose()
        row=explanation(OP,catalog()['operators'][OP],2,1,selected)
        self.assertTrue(row['native_skill_use_rule']['available'])
        self.assertTrue(row['common_reference_applied'])
        self.assertIsNone(row['actual_activation_verified']);self.assertIsNone(row['account_training_verified'])
        self.assertIn('其它技能尚未直接读取',format_explanation(row))
        direct=select_rank(catalog()['operators'][OP],1,0,state=record({'1':7},elite=0),level=1)
        row=explanation(OP,catalog()['operators'][OP],1,0,direct)
        self.assertIsNone(row['e0_common_use_verified'])
        self.assertEqual(row['training_requirement']['raw'],{'phase':'PHASE_1','level':1})
        self.assertTrue(row['native_skill_use_rule']['available'])
        self.assertIn('静态门已核验',format_explanation(row));self.assertIn('实际本局使用仍未核验',format_explanation(row))


if __name__=='__main__':unittest.main()
