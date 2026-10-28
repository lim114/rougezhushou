import unittest
from copy import deepcopy
from rouge.player_team import crew_rows, crew_text, qualified_fields
from rouge.catalog import operator_profiles

class TeamTests(unittest.TestCase):
    def test_only_present_run_members_and_no_state_mutation(self):
        state={'operators':{'mechanist':{'present':True,'fields':{'level':80,'elite':1}},
                            'kaltsit':{'present':False},'silverash':{'present':'true'},
                            'account-only':{'present':True,'scope':'account'}}}
        before=deepcopy(state)
        self.assertEqual([r['id']for r in crew_rows(state)],['mechanist'])
        self.assertEqual(state,before)

    def test_invalid_raw_training_is_not_player_data(self):
        profile=operator_profiles()['mechanist']
        for value in (True,float('nan'),float('inf'),-1,101,'100'):
            self.assertNotIn('trust',qualified_fields({'fields':{'trust':value}},profile))
        self.assertNotIn('level',qualified_fields({'fields':{'elite':0,'level':80}},profile))
        self.assertNotIn('potential',qualified_fields({'fields':{'potential':7}},profile))
        self.assertNotIn('selected_skill',qualified_fields({'fields':{'selected_skill':4}},profile))

    def test_masks_training_and_run_origin_not_account_defaults(self):
        state={'operators':{'mechanist':{'fields':{'elite':2,'level':90},'invalid_fields':['level'],
                'advanced':True,'recruitment_kind':'emergency_hire',
                'unconfirmed_run_metadata':['advanced','recruitment_kind']}}}
        text=crew_text(crew_rows(state)[0])
        self.assertIn('等级：未读到',text)
        self.assertIn('本局进阶：未确认',text)
        self.assertIn('招募来源：未确认',text)
        self.assertNotIn('等级：90',text)

    def test_all_skill_names_rank_and_selected_skill(self):
        row=crew_rows({'operators':{'mechanist':{'fields':{'selected_skill':2},'skill_ranks':{'1':7,'2':10,'3':9}}}})[0]
        text=crew_text(row)
        for skill in row['profile']['skills']:self.assertIn(skill['levels'][0]['name'],text)
        self.assertIn('专精三',text)
        self.assertIn('所选技能：'+row['profile']['skills'][1]['levels'][0]['name'],text)

    def test_module_identity_and_phase_are_independent_of_promotion(self):
        p=operator_profiles()['mechanist'];mid=p['modules'][0]['id']
        valid=qualified_fields({'fields':{'module_id':mid,'module_level':3}},p)
        self.assertEqual(valid,{'module_id':mid,'module_level':3})
        for fields in ({'module_id':'wrong','module_level':3},{'module_id':None,'module_level':2}):
            result=qualified_fields({'fields':fields},p)
            self.assertNotIn('module_id',result)
            self.assertNotIn('module_level',result)

    def test_no_module_is_distinct_from_unread_and_no_calculation_for_unknown(self):
        known=crew_rows({'operators':{'mechanist':{'fields':{'module_id':None}}}})[0]
        self.assertIn('模组：未装备',crew_text(known))
        unknown=crew_rows({'operators':{'unlisted-fixture':{'name':'独立测试成员','fields':{}}}})[0]
        self.assertFalse(unknown['calculable'])
        self.assertIn('未读到',crew_text(unknown))

if __name__=='__main__':unittest.main()
