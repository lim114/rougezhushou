"""Prepared tests; run only after installing the complete candidate."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch
from rouge import current_elbert_reference as model


class CurrentElbert366Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=model.packet()
        assert cls.base is not None,'Install the full candidate and pinned data first.'
        cls.current=model.battle.packet()

    def reference(self,sid,key=None,card=None):
        with patch.object(model,'packet',return_value=deepcopy(self.base)):
            return model.reference(sid,key,card)

    def test_all_four_current_stages_keep_eight_exact_original_bindings(self):
        total=0
        for sid in model.STAGES:
            result=self.reference(sid);source=self.current['version']['current']['details']['stages'][sid]
            key='levels/'+source['levelId'].lower()+'.json'
            self.assertEqual(result['stage']['complete_level'],self.current['inputs']['levels'][key])
            self.assertEqual(len(result['entities']),2)
            for row in result['entities']:
                self.assertEqual(row['raw_binding'],result['stage']['complete_level']['enemyDbRefs'][int(row['key'])])
                self.assertEqual(type(row['level']),int);total+=1
        self.assertEqual(total,8)

    def test_independent_firebrand_never_inherits_database_default(self):
        for sid in model.STAGES:
            result=self.reference(sid);row=next(r for r in result['entities']if r['enemy_id']==model.FIRE)
            cfg=row['declared_configuration'];values={r['key']:r['value']for r in cfg['talentBlackboard']}
            if sid in('ro6_b_3_b','ro6_b_3_b_dlc1'):
                self.assertEqual(row['constructor'],'independent');self.assertFalse(row['raw_binding']['useDb'])
                self.assertEqual(cfg,row['raw_binding']['overwrittenData'])
                self.assertEqual((values['DamageAura.duration'],values['DamageAura.value'],values['DamageAura.circle']),(6,500,1.5))
                self.assertNotEqual(cfg,row['database_definitions'][0]['enemyData'])
            else:
                self.assertEqual(row['constructor'],'database');self.assertEqual((values['DamageAura.duration'],values['DamageAura.value'],values['DamageAura.circle']),(10,1000,2))

    def test_false_identity_wrappers_are_preserved_without_becoming_identity(self):
        row=self.reference('ro6_b_3')['entities'][0]
        self.assertEqual(row['override_status'],'undefined_wrappers')
        self.assertIsNone(row['raw_binding']['overwrittenData']['name']['m_value'])
        self.assertFalse(row['raw_binding']['overwrittenData']['name']['m_defined'])
        self.assertEqual(row['name'],'埃尔伯特')
        changed=deepcopy(self.current['inputs']);level=changed['levels'][self.reference('ro6_b_3')['stage']['level_key']]
        level['enemyDbRefs'][0]['overwrittenData']['name']={'m_defined':True,'m_value':'foreign'}
        with self.assertRaises(ValueError):model.source_rows(self.current['version']['current'],changed)

    def test_unreviewed_constructor_or_boolean_grade_is_rejected(self):
        for field,value in(('level',False),('useDb',1)):
            changed=deepcopy(self.current['inputs']);key=self.reference('ro6_b_3')['stage']['level_key']
            changed['levels'][key]['enemyDbRefs'][0][field]=value
            with self.assertRaises(ValueError):model.source_rows(self.current['version']['current'],changed)

    def test_blink_and_staff_text_have_full_conditions_and_distinct_values(self):
        for sid,cooldown,recovery in(('ro6_b_3',30,'0.5'),('ro6_b_3_b',75,'0.33')):
            result=self.reference(sid,'0','overview');text=model.player_text(result)
            for term in('未被阻挡时','正常结束','下一个路径点','后摇'+recovery+'秒','之后冷却'+str(cooldown)+'秒','退场后','半径20','攻击速度+50','150%','同名效果不叠加'):
                self.assertIn(term,text)
            self.assertIn('不是增加150%',text);self.assertIn('不是整场战斗的绝对时间',text)

    def test_complete_three_source_cards_retain_tooltips_and_stage_rule(self):
        cards=self.base['data']['complete_cards'];self.assertEqual(set(cards),{'elbert','heretic','firebrand'})
        for kind in('elbert','heretic'):
            text=cards[kind]['full_visible_text']
            for term in('仅未被阻挡时可触发','在关卡内的配置','后摇','退场后','无视其可选性','同名效果不叠加'):
                self.assertIn(term,text)
        for term in('每秒变化一次','由0线性提升至最大值','预计算近战途径法术普通伤害','不受迷彩','视为无原因退场','半径0.25'):
            self.assertIn(term,cards['firebrand']['full_visible_text'])

    def test_firebrand_output_keeps_independent_direction_and_clocks_unknown(self):
        result=self.reference('ro6_b_3_b','1','configuration');text=model.player_text(result)
        for term in('独立配置','6秒','1.5','法术500','不因为本关首领叫“异端”','不按路程反算','不是当前敌人预计面板'):
            self.assertIn(term,text)
        for field in('actual_fire_direction','actual_staff_position','actual_damage','actual_clock','actual_received_buff'):
            self.assertIsNone(result[field])
        self.assertFalse(result['numerical_model_applied']);self.assertFalse(result['run_updated'])
        self.assertNotIn('闪现',dict(model.CARDS['fire']).values())

    def test_exact_bidirectional_entity_requests_reject_other_stage_name_or_reference(self):
        result=self.reference('ro6_b_3','0');request=model.related_entities(result,'0')[0]
        self.assertEqual(request['enemy_key'],'1');self.assertEqual(request['enemy_id'],model.FIRE)
        with patch.object(model,'packet',return_value=deepcopy(self.base)):
            self.assertEqual(model.resolve_related(result,'0',request),{'stage_id':'ro6_b_3','enemy_key':'1'})
            self.assertEqual(model.locate('ro6_b_3','1'),{'stage_id':'ro6_b_3','enemy_key':'1'})
            for changed in({**request,'stage_id':'ro6_b_3_b'},{**request,'name':'same image'},{**request,'enemy_key':True}):
                self.assertIsNone(model.resolve_related(result,'0',changed))
            self.assertIsNone(model.locate('ro6_b_3',1));self.assertIsNone(model.locate('狂热敬虔','0'))

    def test_unknown_or_unrelated_entity_has_no_foreign_special_topics(self):
        self.assertIsNone(self.reference('ro6_b_3','999'));self.assertIsNone(self.reference('ro6_b_1','0'))
        self.assertIsNone(self.reference('ro6_b_3','1','staff'));self.assertIsNone(self.reference('ro6_b_3','0','configuration'))
        self.assertIsNone(model.view_result(self.reference('ro6_b_3'),'1','blink'))

    def test_bad_public_source_or_battle_packet_cannot_retain_stale_document(self):
        original=model._read_public
        def broken(name):
            raw=original(name)
            return raw+b'changed'if name.endswith('firebrand-page.html')else raw
        with patch.object(model,'_read_public',side_effect=broken):self.assertIsNone(model.packet())
        with patch.object(model.battle,'packet',return_value=None):self.assertIsNone(model.packet())


if __name__=='__main__':unittest.main()
