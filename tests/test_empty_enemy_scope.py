import json,unittest
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.timing import AttackTimeline

def calc(op,n,mode='continuous',**extra):
    return calculate_damage({'operator':op,'skill':n,'base_attack':1000,'enemy_defense':0,
        'enemy_resistance':0,'timing_mode':mode,'timing':{'target_disappears_seconds':0},**extra})

class EmptyEnemyScopeTests(unittest.TestCase):
    def test_continuous_enemy_attack_stream_has_no_events(self):
        stream=AttackTimeline({'operator':'char_002_amiya','skill':1,'timing_mode':'continuous',
            'timing':{'target_disappears_seconds':0}}).attacks(30,1)
        for key in ('times_seconds','start_frames','release_frames','impact_frames'):
            self.assertEqual(stream[key],[])

    def test_attack_sp_is_not_charged_by_an_absent_enemy(self):
        for mode in ('frames','continuous'):
            result=calc('mechanist',1,mode)
            self.assertEqual(result['total_damage'],0)
            self.assertIsNone(result['estimate']['skill']['recharge_seconds'])
            self.assertIsNone(result['estimate']['skill']['cycle_seconds'])
            self.assertGreater(result['estimate']['skill']['initial_seconds'],0)

    def test_amiya_natural_recharge_remains_without_attack_sp(self):
        result=calc('char_002_amiya',1)
        skill=result['estimate']['skill']
        self.assertEqual(result['total_damage'],0)
        self.assertEqual(skill['recharge_seconds'],30)
        self.assertEqual(skill['cycle_seconds'],60)
        self.assertEqual(skill['initial_seconds'],7)
        stunned=calc('char_002_amiya',2,effects=[{'kind':'sp_recovery','value':100}])
        self.assertEqual(stunned['estimate']['skill']['recharge_seconds'],10)

    def test_friendly_healing_survives_empty_enemy_sources(self):
        for mode in ('frames','continuous'):
            for op,n in [('kaltsit',1),('kaltsit',3),('char_298_susuro',1),
                    ('char_2025_shu',2),('char_4202_haruka',1)]:
                for timing in ({'target_disappears_seconds':0},{'target_windows':[]}):
                    result=calc(op,n,mode,timing=timing)
                    baseline=calculate_damage({'operator':op,'skill':n,'base_attack':1000,'timing_mode':mode})
                    self.assertEqual(result['total_damage'],0)
                    self.assertEqual(result['total_healing'],baseline['total_healing'])

    def test_medical_ammo_can_select_a_friend_without_an_enemy(self):
        for mode in ('frames','continuous'):
            result=calc('kaltsit',2,mode)
            skill=result['estimate']['skill']
            self.assertEqual(result['total_damage'],0)
            self.assertEqual(skill['total_healing'],50000)
            self.assertEqual(skill['cycle_damage'],0)
            result=calc('kaltsit',2,mode,healing_targets=0)
            self.assertEqual(result['total_damage'],0)
            self.assertEqual(result['estimate']['skill']['total_healing'],0)
            self.assertIsNone(result['estimate']['skill']['duration_seconds'])

    def test_independent_conditional_healing_and_damage_references_survive(self):
        for mode in ('frames','continuous'):
            result=calc('char_4202_haruka',2,mode,bubble_bursts=1)
            self.assertEqual(result['total_damage'],0)
            self.assertIsNone(result['total_healing'])
            references={c['name']:c for c in result['external_event_reference']['conditional_components']}
            self.assertEqual(references['扶摇花火']['total'],250)
            self.assertEqual(references['浮泡治疗衍生伤害']['total'],500)
            result=calc('char_1029_yato2',2,mode)
            self.assertEqual(result['total_damage'],0)
            self.assertGreater(result['unbound_cast_reference']['conditional_components'][0]['total'],0)

    def test_damage_to_healing_depends_on_actual_enemy_damage(self):
        for mode in ('frames','continuous'):
            for skill in (1,2):
                result=calc('char_1037_amiya3',skill,mode)
                self.assertEqual(result['total_damage'],0)
                self.assertEqual(result['total_healing'],0)

    def test_medical_s1_extra_heal_requires_a_body_attack_source(self):
        result=calc('char_1037_amiya3',1,'frames',timing={'target_windows':[]})
        self.assertEqual(result['total_damage'],0)
        self.assertEqual(result['total_healing'],0)
        healing=next(c for c in result['components'] if c['name']=='哀恸共情范围治疗')
        self.assertEqual(healing['hits'],0)
        for mode,damage,healing in [('frames',56000,42000),('continuous',54000,40500)]:
            result=calculate_damage({'operator':'char_1037_amiya3','skill':1,'base_attack':1000,'timing_mode':mode})
            self.assertEqual(result['total_damage'],damage)
            self.assertEqual(result['total_healing'],healing)

    def test_friendly_report_keeps_real_acquisition_unverified(self):
        text=format_estimate(calc('char_298_susuro',1,'frames'))
        self.assertIn('真实友方获取时钟未核验',text)

    def test_declared_charge_and_counter_parameters_do_not_damage_empty_target(self):
        for mode in ('frames','continuous'):
            result=calc('mechanist',3,mode,charge_count=2)
            self.assertEqual(result['total_damage'],0)
            self.assertEqual(result['charge_reference']['hits_requested'],2)
            self.assertEqual(result['charge_reference']['declared_count_damage'],22800)
            result=calc('char_1044_hsgma2',1,mode,incoming_hits=2)
            self.assertEqual(result['total_damage'],0)
            counter=next(c for c in result['components'] if c['name']=='恶业苦果反击')
            self.assertEqual(counter['conditional_hits_reference'],2)
            self.assertEqual(counter['conditional_damage_reference'],5950)

    def test_manual_shield_duration_does_not_create_ordinary_attacks(self):
        for mode in ('frames','continuous'):
            result=calc('mechanist',2,mode,skill_duration_seconds=2)
            self.assertEqual(result['total_damage'],0)
            for key in ('total_damage','phase_damage','cycle_damage','window_damage'):
                self.assertEqual(result['estimate']['skill'][key],0)

if __name__=='__main__':unittest.main()
