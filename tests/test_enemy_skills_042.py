"""Exact raw enemy skill references and clear unknowns, through public previews."""
import copy,hashlib,json,unittest
from pathlib import Path
from unittest.mock import patch
from rouge.enemy_skills import skill_data,enemy_skill_reference,enemy_skill_text,blackboard_text,raw_text
from rouge.battle_preview import battle_data,enemy_preview,enemy_text

ROOT=Path(__file__).resolve().parents[1]
FIELDS=('skills','spData','talentBlackboard')


def fixture():
    return {'source':{'game_commit':'fixture'},'bindings':{'stage':{'enemy@1':{'stage_overrides':
        {'skills':[{'prefabKey':'override','cooldown':999}]}}}},'definitions':{'enemy':{
        '0':{'skills':[{'prefabKey':'base','priority':0,'cooldown':10,'initCooldown':0,'spCost':0,
            'blackboard':[{'key':'scale','value':0,'valueStr':None}]}],
            'spData':{'spType':'INCREASE_WHEN_ATTACK','maxSp':3,'initSp':0,'increment':1},'talentBlackboard':None},
        '1':{'skills':None,'spData':None,'talentBlackboard':[]},
        '2':{'skills':[{'prefabKey':'future','cooldown':1}]}}}}


class EnemySkillReferenceTests(unittest.TestCase):
    def test_reference_is_bound_to_stage_id_enemy_and_level(self):
        with patch('rouge.enemy_skills.skill_data',return_value=fixture()):
            for args in (('other','enemy',1),('stage','other',1),('stage','enemy',0),('stage','enemy',2)):
                with self.assertRaises(ValueError):enemy_skill_reference(*args)

    def test_invalid_reference_levels_do_not_default_to_zero(self):
        for value in (True,False,-1,1.0,None,'1',float('nan')):
            with self.assertRaises(ValueError):enemy_skill_reference('stage','enemy',value)

    def test_higher_level_definitions_are_never_borrowed(self):
        with patch('rouge.enemy_skills.skill_data',return_value=fixture()):r=enemy_skill_reference('stage','enemy',1)
        self.assertEqual([d['level'] for d in r['definitions']],[0,1])
        self.assertNotIn('future',enemy_skill_text(r))

    def test_null_skill_lists_are_not_cleared_or_inherited(self):
        with patch('rouge.enemy_skills.skill_data',return_value=fixture()):r=enemy_skill_reference('stage','enemy',1)
        self.assertIsNone(r['definitions'][1]['skills'])
        self.assertIsNone(r['definitions'][1]['spData'])
        self.assertEqual(r['definitions'][1]['talentBlackboard'],[])
        self.assertFalse(r['inheritance_resolved'])
        self.assertEqual(r['definitions'][0]['skills'][0]['prefabKey'],'base')

    def test_stage_overrides_are_separate_not_merged_into_base_definitions(self):
        with patch('rouge.enemy_skills.skill_data',return_value=fixture()):r=enemy_skill_reference('stage','enemy',1)
        self.assertEqual(r['stage_overrides']['skills'][0]['cooldown'],999)
        self.assertEqual(r['definitions'][0]['skills'][0]['cooldown'],10)
        self.assertIn('未推定合并',enemy_skill_text(r))

    def test_missing_exact_level_is_explicit_not_a_fake_effective_definition(self):
        data=fixture();data['definitions']['enemy'].pop('1')
        with patch('rouge.enemy_skills.skill_data',return_value=data):r=enemy_skill_reference('stage','enemy',1)
        self.assertFalse(r['exact_requested_level_present'])
        self.assertIn('不能当作已确认的有效继承',enemy_skill_text(r))

    def test_configured_zero_initial_cooldown_does_not_forecast_immediate_cast(self):
        with patch('rouge.enemy_skills.skill_data',return_value=fixture()):r=enemy_skill_reference('stage','enemy',1)
        self.assertIsNone(r['first_activation_seconds']);self.assertIsNone(r['effective_skill_damage'])
        text=enemy_skill_text(r,technical=True)
        self.assertIn('初始冷却参数：0',text)
        self.assertIn('实际首次发动时刻：未知',text)
        self.assertIn('字段0不证明出生即发动',text)

    def test_sp_configuration_preserves_zero_values_and_type(self):
        with patch('rouge.enemy_skills.skill_data',return_value=fixture()):r=enemy_skill_reference('stage','enemy',1)
        text=enemy_skill_text(r,technical=True)
        self.assertIn('INCREASE_WHEN_ATTACK',text)
        self.assertIn('初始技力 = 0',text)
        self.assertIn('回复增量 = 1',text)

    def test_absent_fields_are_unknown_without_default_zero(self):
        data=fixture();data['definitions']['enemy']['0']['skills']=[{'prefabKey':'only_id'}]
        with patch('rouge.enemy_skills.skill_data',return_value=data):text=enemy_skill_text(enemy_skill_reference('stage','enemy',1),technical=True)
        self.assertIn('冷却参数：未知',text);self.assertIn('初始冷却参数：未知',text)
        self.assertIn('技力需求：未知',text)

    def test_declared_empty_skills_are_kept_distinct_from_null(self):
        data=fixture();data['definitions']['enemy']['1']['skills']=[]
        with patch('rouge.enemy_skills.skill_data',return_value=data):r=enemy_skill_reference('stage','enemy',1)
        self.assertEqual(r['definitions'][1]['skills'],[])
        self.assertIn('不证明没有默认/隐藏技能',enemy_skill_text(r))

    def test_missing_all_data_does_not_claim_no_enemy_mechanisms(self):
        data=fixture();data['definitions']['enemy']={};data['bindings']['stage']['enemy@1']['stage_overrides']={}
        with patch('rouge.enemy_skills.skill_data',return_value=data):r=enemy_skill_reference('stage','enemy',1)
        self.assertEqual(r['definitions'],[])
        self.assertIn('不证明没有默认或隐藏技能',enemy_skill_text(r))

    def test_request_mutations_do_not_pollute_other_previews_or_shared_source(self):
        data=fixture();before=copy.deepcopy(data)
        with patch('rouge.enemy_skills.skill_data',return_value=data):
            r=enemy_skill_reference('stage','enemy',1);r['source'].clear()
            r['definitions'][0]['skills'][0]['cooldown']=200
            r['stage_overrides']['skills'].clear()
            self.assertEqual(enemy_skill_reference('stage','enemy',1)['definitions'][0]['skills'][0]['cooldown'],10)
        self.assertEqual(data,before)

    def test_string_blackboards_are_not_replaced_by_numeric_placeholder(self):
        self.assertEqual(blackboard_text([{'key':'name','value':0,'valueStr':'mode'}]),'name = mode')
        self.assertEqual(blackboard_text([{'key':'name','value':99,'valueStr':''}]),'name = ')
        self.assertEqual(blackboard_text([{'key':'zero','value':0,'valueStr':None}]),'zero = 0')

    def test_raw_nonfinite_numbers_are_not_shown_as_usable_values(self):
        for value in (float('nan'),float('inf'),-float('inf')):self.assertEqual(raw_text(value),'未知')
        self.assertEqual(raw_text(None),'未知');self.assertEqual(raw_text(False),'false')

    def test_unparsed_parameter_names_and_probabilities_are_not_reinterpreted(self):
        data=fixture();data['definitions']['enemy']['1']['talentBlackboard']=[{'key':'prob','value':.25,'valueStr':None}]
        with patch('rouge.enemy_skills.skill_data',return_value=data):text=enemy_skill_text(enemy_skill_reference('stage','enemy',1),technical=True)
        self.assertIn('prob = 0.25',text);self.assertNotIn('25%',text)
        self.assertIn('完整技能伤害：未知',text)

    def test_bad_raw_parameter_shape_remains_visible_without_executing_it(self):
        self.assertIn('格式未确认',blackboard_text('not-list'))
        self.assertIn('格式未确认',blackboard_text([None]))
        self.assertIn('未命名参数 = 未知',blackboard_text([{}]))

    def test_bundle_and_primary_enemy_database_hashes_match_receipts(self):
        receipt=json.loads((ROOT/'.cache/research/enemy-skills-042/data-receipt.json').read_text(encoding='utf-8'))
        self.assertEqual(hashlib.sha256((ROOT/'rouge/data/enemy-skill-references.json').read_bytes()).hexdigest(),receipt['data_sha256'])
        self.assertEqual(hashlib.sha256((ROOT/'.cache/game-data/levels/enemydata/enemy_database.json').read_bytes()).hexdigest(),receipt['source']['enemy_database']['sha256'])

    def test_every_raw_definition_field_is_exact_and_unmerged(self):
        data=skill_data();raw={r['Key']:r['Value'] for r in json.loads((ROOT/'.cache/game-data/levels/enemydata/enemy_database.json').read_text(encoding='utf-8'))['enemies']}
        count=0
        for eid,rows in data['definitions'].items():
            for n,d in rows.items():
                actual=next(r['enemyData'] for r in raw[eid] if str(r['level'])==n)
                self.assertEqual(d,{key:actual[key] for key in FIELDS if key in actual});count+=1
        self.assertEqual(count,333)

    def test_all_1087_public_previews_preserve_original_enemy_attributes(self):
        count=0
        for sid,s in battle_data()['stages'].items():
            for e in s['enemies']:
                r=enemy_preview(sid,e['id'],e['level'])
                for key,value in e.items():self.assertEqual(r[key],value)
                self.assertIsNone(r['skill_reference']['first_activation_seconds'])
                self.assertTrue(all(d['level']<=e['level'] for d in r['skill_reference']['definitions']))
                self.assertIn('机制资料',enemy_text(r));count+=1
        self.assertEqual(count,1087)

    def test_remaining_work_file_contains_no_completed_batches_or_receipts(self):
        remaining=(ROOT/'PROJECT_PROGRESS.md').read_text(encoding='utf-8')
        archive=(ROOT/'PROJECT_COMPLETED.md').read_text(encoding='utf-8')
        self.assertIn('PROJECT_COMPLETED.md',remaining)
        for term in ('已接入','已完成','验收：','FINAL_0.','## 上批','## 证据入口'):
            self.assertNotIn(term,remaining)
        old=(ROOT/'.cache/batch-042-before/PROJECT_PROGRESS.md').read_text(encoding='utf-8')
        start=old.index('更新：');end=old.index('## 未完成事项与建议顺序')
        self.assertIn(old[start:end].strip(),archive)
        self.assertIn('## 证据入口',archive)

if __name__=='__main__':unittest.main()
