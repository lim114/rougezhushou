"""Chinese battle reports preserve references and never promote them to forecasts."""
import ast,copy,hashlib,json,re,unittest
from pathlib import Path
from unittest.mock import patch
from rouge.battle_preview import battle_data,enemy_preview,enemy_text,spawn_rows,spawn_text
from rouge.enemy_skills import enemy_skill_reference,enemy_skill_text
from rouge.spawn_reference import sequence_text,local_sequence
from tests.test_enemy_skills_042 import fixture
from tests.test_spawn_reference_040 import row

ROOT=Path(__file__).resolve().parents[1]
SID='ro6_n_1_2'
EID='enemy_1093_ccsbr'


class ReadableBattleTests(unittest.TestCase):
    def test_numerical_and_reference_functions_are_identical_to_public_backup(self):
        groups={'rouge/battle_preview.py':('battle_data','display_cell','route_reference',
            'hidden_group_reference','spawn_rows','enemy_preview','value_text'),
            'rouge/enemy_skills.py':('skill_data','enemy_skill_reference','raw_text','blackboard_text','definition_text'),
            'rouge/spawn_reference.py':('finite_nonnegative','local_sequence','ordinal_offset','movement_reference')}
        for file,names in groups.items():
            old=ast.parse((ROOT/'.cache/batch-047-before'/file).read_text(encoding='utf-8'))
            new=ast.parse((ROOT/file).read_text(encoding='utf-8'))
            for name in names:
                before=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name==name)
                after=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name==name)
                self.assertEqual(ast.dump(before,include_attributes=False),ast.dump(after,include_attributes=False),(file,name))

    def test_enemy_sections_follow_results_features_mechanisms_then_limits(self):
        text=enemy_text(enemy_preview(SID,EID,0))
        headings=['【预计面板】','【作战特征】','【机制资料】','【技能状态】','【异常免疫】','【预测范围】']
        self.assertEqual([text.index(h) for h in headings],sorted(text.index(h) for h in headings))
        self.assertIn('攻击方式：近战；移动方式：地面',text)
        self.assertIn('图鉴伤害类型：物理',text)
        self.assertNotIn(EID,text);self.assertNotIn('Def.def',text)
        self.assertNotIn('MELEE',text);self.assertNotIn('WALK',text)
        self.assertNotIn('https://',text)

    def test_enemy_predictions_use_environment_only_when_confirmed(self):
        known=enemy_preview(SID,EID,0,{'difficulty':{'value':15},'zone':{'id':'zone_3'}})
        text=enemy_text(known)
        self.assertIn('预计生命值：5840.64',text)
        self.assertIn('预计攻击力：501.12',text)
        unknown=enemy_text(enemy_preview(SID,EID,0))
        self.assertIn('预计生命值：未知',unknown)
        self.assertNotIn('预计生命值：2600',unknown)

    def test_unverified_enum_is_explicit_without_fake_translation(self):
        entry=enemy_preview(SID,EID,0)
        entry.update(attack_way='FUTURE_ATTACK',motion='FUTURE_MOTION',damage_types=['FUTURE_DAMAGE'])
        text=enemy_text(entry)
        self.assertIn('攻击方式：未知（分类未核验）',text)
        self.assertIn('未知（类型未核验）',text)
        self.assertNotIn('FUTURE_',text)
        raw=enemy_text(entry,technical=True)
        self.assertIn('FUTURE_ATTACK',raw);self.assertIn('FUTURE_MOTION',raw);self.assertIn('FUTURE_DAMAGE',raw)

    def test_enemy_technical_mode_contains_original_ids_and_source_links(self):
        text=enemy_text(enemy_preview(SID,EID,0),technical=True)
        self.assertIn('【敌人技术资料】',text)
        self.assertIn(EID,text);self.assertIn('本关卡引用等级：0',text)
        self.assertIn('Def.def = 130',text)
        self.assertIn(battle_data()['source']['enemy_database']['url'],text)

    def test_immunity_unknown_does_not_become_false_and_rows_are_readable(self):
        text=enemy_text(enemy_preview(SID,EID,0))
        self.assertIn('眩晕：未知；沉默：是；沉睡：未知',text)
        lines=text.split('【异常免疫】',1)[1].split('【预测范围】',1)[0].splitlines()
        self.assertTrue(all(line.count('；')<=2 for line in lines))

    def test_skill_summary_hides_unverified_keys_but_keeps_unknowns(self):
        data=fixture();data['definitions']['enemy']['1']['talentBlackboard']=[{'key':'prob','value':.25,'valueStr':None}]
        with patch('rouge.enemy_skills.skill_data',return_value=data):r=enemy_skill_reference('stage','enemy',1)
        text=enemy_skill_text(r)
        self.assertIn('另有2项未核验参数',text)
        self.assertIn('实际首次发动时刻：未知',text)
        self.assertIn('完整技能伤害：未知',text)
        self.assertNotIn('prob',text);self.assertNotIn('scale',text);self.assertNotIn('INCREASE_WHEN_ATTACK',text)
        self.assertNotIn('999',text);self.assertNotIn('25%',text)
        raw=enemy_skill_text(r,technical=True)
        self.assertIn('prob = 0.25',raw);self.assertIn('初始冷却参数：0',raw)
        self.assertIn('冷却参数：999',raw);self.assertIn('INCREASE_WHEN_ATTACK',raw)

    def test_skill_technical_mode_keeps_explicit_null_empty_and_unmerged_overrides(self):
        with patch('rouge.enemy_skills.skill_data',return_value=fixture()):r=enemy_skill_reference('stage','enemy',1)
        text=enemy_skill_text(r,technical=True)
        self.assertIn('"skills":null',text);self.assertIn('"talentBlackboard":[]',text)
        self.assertIn('完整本关卡覆盖字段',text)
        self.assertFalse(r['inheritance_resolved']);self.assertIsNone(r['first_activation_seconds'])

    def test_skill_missing_level_and_empty_data_never_claim_no_mechanisms(self):
        data=fixture();data['definitions']['enemy']={};data['bindings']['stage']['enemy@1']['stage_overrides']={}
        with patch('rouge.enemy_skills.skill_data',return_value=data):r=enemy_skill_reference('stage','enemy',1)
        text=enemy_skill_text(r)
        self.assertIn('不证明没有默认或隐藏技能',text)
        self.assertIn('不能当作已确认的有效继承',text)

    def test_malformed_blackboard_is_flagged_without_parameter_semantic_guess(self):
        data=fixture();data['definitions']['enemy']['0']['skills'][0]['blackboard']='not-list'
        with patch('rouge.enemy_skills.skill_data',return_value=data):r=enemy_skill_reference('stage','enemy',1)
        text=enemy_skill_text(r)
        self.assertIn('部分参数格式未确认',text);self.assertNotIn('not-list',text)
        self.assertIn('not-list',enemy_skill_text(r,technical=True))

    def test_spawn_sections_use_chinese_labels_and_keep_local_clock_boundary(self):
        text=spawn_text(spawn_rows(SID)[0],SID)
        headings=['【出场条目】','【出场条件】','【局部时间计划】','【调度参考】','【路线检查点】']
        self.assertEqual([text.index(h) for h in headings],sorted(text.index(h) for h in headings))
        self.assertIn('本波开始前延迟',text);self.assertIn('同条目相邻生成间隔',text)
        self.assertIn('原地等待：100秒（配置）',text)
        for raw in ('preDelay','interval','count','WAIT_FOR_SECONDS','routeIndex','time=','https://'):
            self.assertNotIn(raw,text)
        self.assertIn('绝对出场时刻：未知',text);self.assertIn('不直接相加为全局时间',text)
        self.assertIn('名义偏移不是开局绝对时刻',text)

    def test_spawn_technical_mode_keeps_all_raw_action_keys_and_values(self):
        r=spawn_rows(SID)[0];text=spawn_text(r,SID,technical=True)
        self.assertIn('【出场技术资料】',text)
        self.assertIn(json.dumps(r['action'],ensure_ascii=False),text)
        self.assertIn(json.dumps(r['route'],ensure_ascii=False),text)
        self.assertIn(battle_data()['stages'][SID]['level_source']['url'],text)

    def test_branch_position_stays_unknown_and_selector_name_is_technical_only(self):
        r=next(x for x in spawn_rows(SID) if x['branch']);text=spawn_text(r,SID)
        self.assertIn('出生位置：未知/未映射',text)
        self.assertIn('条件分支 · 第',text)
        self.assertIn('基础/额外路线选择信息',text)
        self.assertNotIn(r['branch'],text);self.assertNotIn('useExtraRoute',text)
        raw=spawn_text(r,SID,technical=True)
        self.assertIn(r['branch'],raw);self.assertIn('useExtraRoute',raw)

    def test_random_weight_remains_a_reference_and_is_not_normalized(self):
        r=next(x for x in spawn_rows(SID) if x['action'].get('randomSpawnGroupKey'))
        text=spawn_text(r,SID)
        self.assertIn('原始权重',text);self.assertIn('非概率',text)
        self.assertIsNone(r['probability'])
        self.assertNotIn(r['action']['randomSpawnGroupKey'],text)

    def test_unknown_checkpoint_keeps_type_and_time_in_technical_mode_only(self):
        r=spawn_rows(SID)[0];r['route']['checkpoints']=[{'type':'FUTURE_CP','cell':None,'time':23}]
        text=spawn_text(r,SID)
        self.assertIn('未知检查点类型',text);self.assertNotIn('FUTURE_CP',text)
        self.assertIn('FUTURE_CP',spawn_text(r,SID,technical=True))

    def test_sequence_wraps_four_occurrences_per_line_without_rounding_changes(self):
        r=row(count=33,delay=.1,interval=.1);text=sequence_text(r)
        lines=[line for line in text.splitlines() if re.match(r'第\d+次',line)]
        self.assertEqual(len(lines),8);self.assertTrue(all(line.count('次')==4 for line in lines))
        self.assertIn('最后一次 +3.3秒',text)
        self.assertNotIn('preDelay',text);self.assertNotIn('count',sequence_text(row(count=0)))
        self.assertEqual(local_sequence(r)['last_offset'],3.3)

    def test_rendering_both_modes_does_not_change_inputs(self):
        e=enemy_preview(SID,EID,0);r=spawn_rows(SID)[0]
        before_e=copy.deepcopy(e);before_r=copy.deepcopy(r)
        for technical in (False,True):enemy_text(e,technical);spawn_text(r,SID,technical)
        self.assertEqual(e,before_e);self.assertEqual(r,before_r)

    def test_all_public_references_render_without_raw_metadata_in_normal_mode(self):
        enemies=spawns=0
        for sid,stage in battle_data()['stages'].items():
            for e in stage['enemies']:
                text=enemy_text(enemy_preview(sid,e['id'],e['level']))
                for raw in ('enemy_','INCREASE_WHEN_ATTACK','INCREASE_WITH_TIME','prefabKey','https://'):
                    self.assertNotIn(raw,text,(sid,e['id'],raw))
                enemies+=1
            for r in spawn_rows(sid):
                text=spawn_text(r,sid)
                for raw in ('preDelay','routeIndex','useExtraRoute','WAIT_FOR_SECONDS','https://'):
                    self.assertNotIn(raw,text,(sid,r['id'],raw))
                self.assertIsNone(r['absolute_time']);self.assertIsNone(r['probability']);spawns+=1
        self.assertEqual((enemies,spawns),(1087,3938))

    def test_term_receipt_lists_pinned_sources_and_no_new_numerical_model(self):
        receipt=json.loads((ROOT/'.cache/research/readable-047/battle-terms.json').read_text(encoding='utf-8'))
        self.assertFalse(receipt['numerical_model_changed'])
        for item in receipt['local_sources']:
            self.assertEqual(hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest(),item['sha256'])
        self.assertEqual(receipt['terms']['attack_way']['RANGED'],'远程')
        self.assertEqual(receipt['terms']['motion']['WALK'],'地面')


if __name__=='__main__':unittest.main()
