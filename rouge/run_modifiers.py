"""Current-run modifiers sourced from pinned raw squad buffs."""
from .run_config import config_data

def prepare_run(scenario):
    scenario=dict(scenario);config=scenario.get('run_config')
    if config is None:config={}
    if not isinstance(config,dict):raise ValueError('本局配置需要对象。')
    for field,label in (('squad','分队'),('difficulty','保密等级')):
        if config.get(field) is not None and not isinstance(config[field],dict):
            raise ValueError('本局'+label+'配置需要对象或空值。')
    resolution={'source':config_data()['source_url'],'squad':None,'difficulty':None,'applied':[],'pending':[],'notes':[]}
    squad=config.get('squad')
    if squad:
        if 'effect_verified' in squad and type(squad['effect_verified']) is not bool:
            raise ValueError('分队效果确认标记需要布尔值。')
        if not isinstance(squad.get('id'),str):raise ValueError('本局分队身份与固定档案不符。')
        record=config_data()['squads'].get(squad.get('id'))
        if not record or squad.get('name',record['name'])!=record['name']:raise ValueError('本局分队身份与固定档案不符。')
        resolution['squad']={**squad,'name':record['name']}
        rules=[]
        for buff in record['buffs']:
            if buff['key']!='char_attribute_mul':continue
            kinds={'atk':'attack_pct','max_hp':'hp_pct','def':'defense_pct'}
            for value in buff['blackboard']:
                if value['key'] in kinds:
                    rules.append({'kind':kinds[value['key']],'value':value['value'],
                        'target_scope':'all_units','origin':'run_squad','squad_id':record['id'],
                        'attribute_layer':'relic_rune','formula_item':'MULTIPLIER','source_buff_key':buff['key']})
        if rules and not squad.get('effect_verified'):
            resolution['pending'].append(record['name']+'效果阶段尚未确认，未套用分队属性加成。')
        else:
            scenario['effects']=list(scenario.get('effects',[]))+rules
            resolution['applied']=rules
        resolution['notes'].append(record['name']+'：'+('生命/攻击/防御加成与同类藏品符文合并，再计算天赋和技能；作用于我方单位。' if resolution['applied']
            else '本档案没有已确认并接入的直接生命/攻击/防御加成。'))
        resolution['notes'].append('分队起始赠送物品与资源不自动加入当前持有清单，仍以本局实际读取为准。')
    difficulty=config.get('difficulty')
    if difficulty:
        for field in ('modeDifficulty','mode'):
            if field in difficulty and difficulty[field]!='NORMAL':
                raise ValueError('当前保密等级数值计算仅支持NORMAL模式，其他模式不能套用常规难度修正。')
        value=difficulty.get('value')
        if isinstance(value,bool) or not isinstance(value,int) or str(value) not in config_data()['difficulties']:
            raise ValueError('本局保密等级需要0–15的整数。')
        record=config_data()['difficulties'][str(value)]
        resolution['difficulty']={**difficulty,'mode':record['modeDifficulty'],'rule':record['ruleDesc'],'extra':record['addDesc']}
        if not scenario.get('target_enemy'):
            resolution['pending'].append('已确认保密等级 '+str(value)+'；未选择关卡敌人，敌方难度/区域/关卡修正尚未自动计算，当前目标属性仍使用测试输入。')
    from .enemy_environment import resolve_enemy
    resolve_enemy(scenario,resolution)
    return scenario,resolution

def finish_run(result,resolution):
    enemy=resolution.get('enemy')
    if enemy:
        hp_without_relics=enemy['stats']['maxHp']
        effects=result.get('relic_resolution',{}).get('enemy_effects',{})
        defense=effects.get('defense_factor',1);hp=effects.get('hp_factors',[])
        if defense!=1:
            enemy['stats']['def']*=defense
            enemy['steps'].append({'label':'已计算藏品减防','factors':{'def':defense}})
        if hp:
            import math
            factor=math.prod(hp);enemy['stats']['maxHp']*=factor
            label='厄运火杆：已确认居民关卡单项生命参考' if effects.get('resident_hp_applied') else '已计算藏品生命倍率'
            enemy['steps'].append({'label':label,'factors':{'maxHp':factor}})
        if effects.get('hp_composition_pending'):
            enemy['pending'].append('当前生命参考尚未计入厄运火杆；其与其他生命藏品的复合效果未知。')
            resolution['pending'].append(enemy['pending'][-1])
        attack=effects.get('atk_factors',[])
        if attack:
            import math
            factor=math.prod(attack);enemy['stats']['atk']*=factor
            enemy['steps'].append({'label':'已计算藏品攻击倍率','factors':{'atk':factor}})
        weight_delta=effects.get('weight_delta',0)
        if weight_delta:
            enemy['stats']['massLevel']+=weight_delta
            enemy['steps'].append({'label':'已计算藏品重量修正','deltas':{'massLevel':weight_delta}})
        spawn_rules=effects.get('spawn_hp_rules',[])
        if len(spawn_rules)==1:
            rule=spawn_rules[0];probability=rule['probability'];excluded=rule['excluded_hp_sources']
            enemy['spawn_hp']={'relic_id':rule['relic_id'],
                'probabilities':{'untriggered':1-probability,'triggered':probability},
                'untriggered_max_hp':enemy['stats']['maxHp'],
                'triggered_max_hp':None if excluded else enemy['stats']['maxHp']*rule['value'],
                'single_item_triggered_max_hp':hp_without_relics*rule['value'],
                'excluded_hp_sources':excluded,'current_variant':None}
            if rule.get('verified_final_hp_sources'):
                enemy['spawn_hp']['verified_final_hp_sources']=rule['verified_final_hp_sources']
            resolution['notes'].append('猎犬咖啡列出出生时的生命分支；未观测本次抽签，不以概率加权生命代替当前敌人生命或击杀时间。')
    result['run_resolution']=resolution
    result['estimate']['notes'].extend(resolution['notes'])
    warnings=resolution['pending']
    result['warnings'].extend(warnings)
    if result['estimate']['warnings'] is not result['warnings']:result['estimate']['warnings'].extend(warnings)
    if warnings:result['complete']=result['estimate']['complete']=False
