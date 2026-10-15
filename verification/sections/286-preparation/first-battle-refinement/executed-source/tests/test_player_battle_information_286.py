"""Player-facing fixed references keep conditions, unknowns and raw access."""
import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest

from rouge.battle_preview import battle_data,enemy_preview,enemy_text,spawn_rows,spawn_text
from rouge.battle_reward_planning import stage_reward_sources,reward_source_text

ROOT=Path(__file__).resolve().parents[1]
SID='ro6_n_1_2'
EID='enemy_1093_ccsbr'


class PlayerBattleInformation286Tests(unittest.TestCase):
    def test_01_only_the_three_authorized_renderers_change(self):
        guards={
          'rouge/battle_preview.py':(('enemy_text','spawn_text'),
            'f94464de55ab66219b09258bcb91c1c74516274635398c409ebf2922cf8bdb20'),
          'rouge/battle_reward_planning.py':(('reward_source_text',),
            '5cf75322db27997eaaa130c8b8183e265b1135607b34ad9f190a360566525dc3')}
        for relative,(names,expected) in guards.items():
            tree=ast.parse((ROOT/relative).read_text(encoding='utf-8'))
            tree.body=[node for node in tree.body if not isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) or node.name not in names]
            actual=sha256(ast.dump(tree,include_attributes=False).encode()).hexdigest()
            self.assertEqual(actual,expected,relative)

    def test_02_spawn_first_screen_names_enemy_position_and_correct_local_clock(self):
        row=next(r for r in spawn_rows(SID) if r['wave'])
        text=spawn_text(row,SID)
        name=next(e['name'] for e in battle_data()['stages'][SID]['enemies'] if e['id']==row['action']['key'])
        self.assertIn(name,text)
        for expected in ('出生位置：','本片段的出场计划启动','启动前的等待另列',
                         '不是开战倒计时','不是从首只敌人出现计时','资料条目数不是实际敌人数',
                         '绝对出场时刻：未知','本条目生成数量：'):
            self.assertIn(expected,text)
        self.assertLess(text.index('时间口径'),text.index('【局部时间计划】'))
        player=text.replace('【调度参考】','')
        for term in ('动作队列','锚点','名义偏移','调度','配置','生成回调'):
            self.assertNotIn(term,player)
        for expected in ('计时起点','出场时间差','本波开始前等待','本条计划相邻两次出场间隔'):
            self.assertIn(expected,text)
        unlimited=deepcopy(row);unlimited['wave_max_wait']=-1
        self.assertIn('清场等待上限：无上限',spawn_text(unlimited,SID))
        self.assertNotIn('原始配置为负一',spawn_text(unlimited,SID))
        technical=spawn_text(unlimited,SID,True)
        for expected in ('动作队列','锚点','名义偏移','原始配置为负一'):
            self.assertIn(expected,technical)

    def test_03_random_candidates_hide_raw_weights_but_not_uncertainty(self):
        row=next(r for r in spawn_rows(SID) if r['action'].get('randomSpawnGroupKey'))
        before=deepcopy(row);plain=spawn_text(row,SID);raw=spawn_text(row,SID,technical=True)
        for expected in ('随机候选','不保证出现','候选不能相加','不提供生成概率'):
            self.assertIn(expected,plain)
        self.assertNotIn('原始权重',plain)
        self.assertNotIn(row['action']['randomSpawnGroupKey'],plain)
        self.assertIn('原始权重：',raw)
        self.assertIn('非概率',raw)
        self.assertIn(json.dumps(row['action'],ensure_ascii=False),raw)
        self.assertIn(json.dumps(row['route'],ensure_ascii=False),raw)
        self.assertEqual(row,before);self.assertIsNone(row['probability'])

    def test_04_branch_clock_and_unknown_route_are_never_promoted_to_live_spawn(self):
        row=next(r for r in spawn_rows(SID) if r['branch'])
        plain=spawn_text(row,SID);raw=spawn_text(row,SID,True)
        self.assertIn('本分支阶段的出场计划启动',plain)
        self.assertIn('出生位置：未知/未映射',plain)
        self.assertIn('触发时刻和阶段选择仍待核验',plain)
        self.assertNotIn('useExtraRoute',plain);self.assertIn('useExtraRoute',raw)
        self.assertIsNone(row['absolute_time']);self.assertIsNone(row['route']['start'])

    def test_05_enemy_predictions_keep_results_first_and_explain_their_scope(self):
        known=enemy_preview(SID,EID,0,{'difficulty':{'value':15},'zone':{'id':'zone_3'}})
        before=deepcopy(known);text=enemy_text(known)
        self.assertIn('预计生命值：5840.64',text)
        self.assertIn('预计攻击力：501.12',text)
        self.assertIn('不含藏品',text);self.assertIn('不跟踪战斗中的技能或阶段变化',text)
        self.assertIn('图鉴与已核验的条件资料',text)
        self.assertLess(text.index('【预计面板】'),text.index('【机制资料】'))
        self.assertNotIn(EID,text);self.assertNotIn('https://',text)
        self.assertEqual(known,before)

    def test_06_unknown_enemy_panel_does_not_fall_back_to_raw_white_values(self):
        entry=enemy_preview(SID,EID,0);text=enemy_text(entry);raw=enemy_text(entry,True)
        self.assertIn('预计生命值：未知',text)
        self.assertIn('未知不等于0',text)
        self.assertNotIn('预计生命值：2600',text)
        self.assertIn('【异常免疫】',text);self.assertIn('沉默：是',text)
        self.assertIn('眩晕：未知',text)
        for term in ('基包','构造','字段','控制器'):
            self.assertNotIn(term,text)
        self.assertIn(EID,raw);self.assertIn('各字段明确来源',raw)
        self.assertIn('敌人原始数据',raw)

    def test_07_reward_outcome_appears_before_activation_and_keeps_currency_types(self):
        result=stage_reward_sources('ro6_n_1_1')
        row=next(r for r in result['rows'] if r['entity_id']=='trap_320_shtlbx')
        before=deepcopy(result);text=reward_source_text(result,row)
        self.assertIn('地图参考位置：',text)
        self.assertIn('+1随机零件',text)
        self.assertIn('50点部署费用；不等于源石锭或探索行动力',text)
        self.assertIn('完整候选池未知',text)
        self.assertLess(text.index('数量参考'),text.index('是否出现或可领取'))
        self.assertNotIn('预置容器',text);self.assertNotIn('routeIndex',text)
        self.assertNotIn(row['entity_id'],text);self.assertNotIn(row['source_selector'],text)
        self.assertEqual(result,before)

    def test_08_reward_technical_mode_retains_container_identity_and_source(self):
        result=stage_reward_sources('ro6_n_1_1')
        row=next(r for r in result['rows'] if r['kind']=='predefined_device')
        raw=reward_source_text(result,row,True)
        self.assertIn('预置容器',raw)
        self.assertIn(row['entity_id'],raw);self.assertIn(row['source_selector'],raw)
        self.assertIn(row['rule']['quantity_source']['url'],raw)
        self.assertIn(result['source']['url'],raw)
        self.assertIn('已检查：',raw)

    def test_09_reward_candidates_and_related_targets_are_not_added_as_actual_totals(self):
        result=stage_reward_sources('ro6_n_1_1')
        box=next(r for r in result['rows'] if r['entity_id']=='trap_323_shsbox')
        plain=reward_source_text(result,box)
        self.assertIn('不能把两条来源各算一次10源石锭',plain)
        self.assertIn('不同目标',plain)
        self.assertIn('额外出现条件',plain)
        rare=next(r for r in result['rows'] if r['kind']=='rare_enemy_action')
        text=reward_source_text(result,rare)
        for expected in ('+1收藏品','空候选','不能相加','完整结算池：未知'):
            self.assertIn(expected,text)
        self.assertNotIn('+4收藏品',text)
        self.assertIsNone(result['actual_reward_total'])
        self.assertFalse(result['complete_settlement_pool_known'])

    def test_10_missing_reward_quantity_and_position_stay_unknown(self):
        result=stage_reward_sources('ro6_n_1_1')
        row=deepcopy(next(r for r in result['rows'] if r['entity_id']=='enemy_2152_shezlc'))
        row['display_cell']=None
        for outcome in row['rule']['outcomes']:outcome['quantity']=None
        plain=reward_source_text(result,row)
        self.assertIn('数量未证',plain);self.assertIn('位置：未绑定',plain)
        self.assertIn('不能借用其他目标的路线定位',plain)
        self.assertNotIn('+10源石锭',plain)
        self.assertNotIn('routeIndex',plain)


if __name__=='__main__':unittest.main()
