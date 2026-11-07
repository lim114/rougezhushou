"""Source-qualified environment subtotals from legacy or current snapshots."""
from copy import deepcopy
from .battle_preview import battle_data, preview_environment
from .enemy_panel import enemy_panel_reference, panel_data
from .run_config import config_data, difficulty_value


def component_numbers(forecast):
    values=(forecast or{}).get('environment_component')or{}
    return ['未知'if values.get(key)is None else format(values[key],',.2f').rstrip('0').rstrip('.')
            for key in('maxHp','atk','def','magicResistance')]


def forecasts(result, config):
    from .current_enemy_environment import qualify_current
    return _forecasts(result, config, qualify_current)


def _forecasts(result, config, current_environment):
    """Use the current-source check appropriate to this stage's provenance."""
    if not config or result is None:
        return {}
    grade=difficulty_value(config.get('difficulty'))
    current=result['difficulty_reference'].get(str(grade))
    configuration=config_data()
    old_profile=configuration['difficulties'].get(str(grade))
    reason=None
    if grade is None or current is None:
        reason='本页尚无已支持的常规保密等级，未借用其它难度或模式。'
    elif old_profile is not None and any(current[key]!=old_profile[key]for key in current):
        reason='这一难度的资料已变化，暂不套用旧计算。'
    legacy=battle_data()['stages'].get(result['id'])
    current_reference=None
    if legacy is None or legacy['level_source']['sha256']!=result['source']['sha256']:
        if reason is None:
            current_reference = current_environment(result)
            if current_reference is None:
                reason='此关的当前关卡与敌人属性来源无法核对，未借用旧计算。'
    zone=config.get('zone')or{}
    zone_name=zone.get('name')or configuration['zones'].get(zone.get('id'),{}).get('name')or'区域未确认'
    raw_grade=(config.get('difficulty')or{}).get('value')
    label='保密等级 '+str(raw_grade if raw_grade is not None else'未确认')+' · '+zone_name
    difficulty_reference=({'profiles':result['difficulty_reference'],'source':result['difficulty_source']}
                          if current is not None and old_profile is None else None)
    conditions = {key: config[key] for key in ('difficulty', 'zone') if key in config}
    legacy_enemies = {}
    if legacy is not None and reason is None and current_reference is None:
        for row in legacy['enemies']:
            legacy_enemies.setdefault((row['id'], row['level']), []).append(row)
    output={}
    for enemy in result['enemies']:
        item={'environment_component':None,'complete_current_total':None,'pending':[reason]if reason else[],
              'scope':'source_equal_fixed_environment_component','actual_gameplay_verified':False,
              'battle_source_identity':result['source_identity'],'reference_key':enemy['key'],'conditions_label':label}
        output[enemy['key']]=item
        if reason:
            continue
        if current_reference is not None:
            from .current_enemy_environment import environment
            component,pending=environment(current_reference,enemy,config,grade)
            item['scope']='current_declared_fixed_environment_component'
            if component is None:
                item['pending'].append(pending)
            else:
                item['environment_component']=component['stats']
                item['steps']=component['steps']
                item['pending']=component['pending']
                item['qualified_inputs']={'current_snapshot_level_and_enemy_declarations_equal':True,
                    'four_core_attributes_explicit':True,'exact_database_level_or_independent_override':True,
                    'known_tier':True,'shared_documented_environment_rules':True}
                item['difficulty_profile_source']=dict(result['difficulty_source'])
            continue
        matches = legacy_enemies.get((enemy['id'], enemy['level']), [])
        if len(matches)!=1 or matches[0]['level_type']!=enemy['tier']:
            item['pending'].append('该敌人的精确引用或类别尚不能与原计算对应。');continue
        prior=enemy_panel_reference(result['id'],enemy['id'],enemy['level'])
        binding=panel_data()['bindings'][result['id']][enemy['id']+'@'+str(enemy['level'])]
        values=enemy['declared_traits']['explicit_core_attributes']
        if binding['use_db']!=enemy['use_db'] or any(key not in values or values[key]!=prior['attributes'][key]
                for key in('maxHp','atk','def','magicResistance')):
            item['pending'].append('这一引用的完整属性来源缺失或已变化，未借用其它等级或默认值。');continue
        # Only the enemy-facing difficulty/zone inputs belong to this subtotal.
        # Operator squad benefits are not enemy attributes, and relic effects
        # remain a separately unfinished component of the complete total.

        environment, pending = preview_environment(result['id'], enemy['id'], enemy['level'],
                                                   prior, conditions, difficulty_reference)
        if environment is not None:
            item['environment_component']={key:environment['stats'][key]for key in('maxHp','atk','def','magicResistance')}
            item['steps']=deepcopy(environment['steps'])
        item['pending']=list(pending)
        item['qualified_inputs']={'whole_stage_bytes_equal':True,'four_explicit_core_attributes_equal':True,
                                  'constructor_mode_and_tier_equal':True,'difficulty_fields_equal':old_profile is not None}
        if difficulty_reference is not None:item['difficulty_profile_source']=dict(difficulty_reference['source'])
    for item in output.values():
        scripts=sum(line.startswith('关卡脚本修正待核验：')for line in item['pending'])
        item['player_pending']=[line for line in item['pending']if not line.startswith('关卡脚本修正待核验：')]
        if scripts:item['player_pending'].insert(0,f'还有{scripts}项关卡特殊规则未计入；完整数值仍未知，可展开原始资料查阅来源。')
    return output
