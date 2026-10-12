"""Complete fixed enemy source fields, independent of hidden runtime mechanisms."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path

@lru_cache(maxsize=1)
def panel_data():
    return json.loads((Path(__file__).with_name('data')/'enemy-panel-reference.json').read_text(encoding='utf8'))

def enemy_panel_reference(stage_id,enemy_id,level):
    if type(level) is not int or level<0:raise ValueError('敌人引用等级需要非负整数。')
    data=panel_data()
    if not isinstance(stage_id,str) or not isinstance(enemy_id,str):
        raise ValueError('固定敌人面板需要关卡和敌人标识。')
    binding=data['bindings'].get(stage_id,{}).get(enemy_id+'@'+str(level))
    if binding is None:raise ValueError('固定面板必须绑定本关卡的敌人和引用等级。')
    fields={}
    for group,keys in (('attributes',data['attribute_fields']),('metadata',data['metadata_fields'])):
        fields.update({group+'.'+key:{'state':'undefined','value':None,
            'source_selector':None,'source_level':None} for key in keys})
    definitions=data['definitions'].get(enemy_id,{})
    for n,record in sorted(definitions.items(),key=lambda item:int(item[0])):
        if int(n)>level:continue
        for path,value in record['fields'].items():
            fields[path]={'state':'database_definition','value':deepcopy(value),
                'source_level':int(n),
                'source_selector':record['source_selector']+'.'+
                    (path if path.startswith('attributes.') else path.split('.',1)[1])+'.m_value'}
    for path,value in binding['overrides'].items():
        fields[path]={'state':'stage_override','value':deepcopy(value),'source_level':level,
            'source_selector':'$.enemyDbRefs['+str(binding['source_index'])+'].overwrittenData.'+
                (path if path.startswith('attributes.') else path.split('.',1)[1])+'.m_value'}
    exact=str(level) in definitions
    projection={'attributes':{key:fields['attributes.'+key]['value'] for key in data['attribute_fields']},
        'metadata':{key:fields['metadata.'+key]['value'] for key in data['metadata_fields']}}
    return {'stage_id':stage_id,'enemy_id':enemy_id,'requested_level':level,
        'scope':data['scope'],
        'attributes':deepcopy(projection['attributes']) if exact else {key:None for key in data['attribute_fields']},
        'metadata':deepcopy(projection['metadata']) if exact else {key:None for key in data['metadata_fields']},
        'source_projection':projection,
        'source_state':'exact_database_level_available' if exact else 'unavailable_exact_database_level',
        'compiled_database_result_available':exact,
        'field_provenance':fields,'exact_level_present':str(level) in definitions,
        'source':{'game_commit':data['source']['game_commit'],
            'enemy_database':deepcopy(data['source']['enemy_database']),
            'stage':deepcopy(data['source']['stages'][stage_id])},
        'complete_effective_panel':None,'actual_gameplay_verified':False,
        'limits':['精确数据库等级可用时按已证基包规则读取等级定义；精确等级缺失时构建器返回空，未借用较低等级字段。',
            '关卡覆盖的原字段仍保留为来源分项；缺少精确数据库等级的别名/默认构建路径未核验，不能当有效面板。',
            '本表含完整固定属性字段；技能、藏品、阶段和关卡动态脚本的完整有效面板仍未知。',
            '技力回复、命中率、攻击范围与扣除生命等均为字段参考；不推算实际发动、命中、范围或通过终点时的事件。',
            '固定数据版本不证明当前服务器、资源包或热更新一致；未合并技能/天赋/技力控制器配置。']}

def enemy_panel_text(reference,technical=False):
    from .battle_preview import value_text
    attrs=reference['attributes'];meta=reference['metadata']
    if not technical:
        additional=('attributes.spRecoveryPerSec','attributes.tauntLevel',
            'attributes.damageHitratePhysical','attributes.damageHitrateMagical',
            'attributes.epBreakRecoverSpeed',*('metadata.'+key for key in meta))
        written=sum(reference['field_provenance'].get(key,{}).get('state') not in (None,'undefined')
            for key in additional)
        unavailable=reference.get('source_state')=='unavailable_exact_database_level'
        return '\n'.join(['【扩展属性预测】',
            '预计技力回复、嘲讽、物理/法术命中率、元素爆发恢复速度：未知。',
            '漏怪扣血、分类和敌人计数适用性：未知；动态脚本与阶段尚未完全核验。',
            f'{written}项扩展字段已有明确来源，完整值仍未知；原文可在技术资料中查看。',
            *(['固定数据库精确等级不可用；别名/默认构建路径尚未核验。'] if unavailable else [])])
    labels=(('maxHp','生命'),('atk','攻击'),('def','防御'),('magicResistance','法抗'),
        ('attackSpeed','攻速'),('baseAttackTime','基础攻击间隔参数'),('moveSpeed','移速参数'),
        ('massLevel','重量'),('hpRecoveryPerSec','每秒生命回复参数'),
        ('spRecoveryPerSec','每秒技力回复参数'),('tauntLevel','嘲讽等级参数'),
        ('epDamageResistance','元素伤害抵抗参数'),('epResistance','元素损伤抵抗参数'),
        ('damageHitratePhysical','物理命中率参数'),('damageHitrateMagical','法术命中率参数'),
        ('epBreakRecoverSpeed','元素爆发恢复速度参数'))
    lines=['【固定资料面板】','以下为关卡引用的固定字段，不是已完整修正的战斗面板。']
    for start in range(0,len(labels),2):
        lines.append('；'.join(label+'：'+value_text(attrs.get(key)) for key,label in labels[start:start+2]))
    tags=meta.get('enemyTags')
    lines.append('分类标签：'+(str(len(tags))+'项固定标签（名称待核验，原文见技术资料）'
        if isinstance(tags,list) else '未知'))
    lines.append('扣除关卡生命参数：'+value_text(meta.get('lifePointReduce'))+
        '；不计入敌人总数：'+value_text(meta.get('notCountInTotal')))
    lines.extend(['完整固定属性字段：'+json.dumps(attrs,ensure_ascii=False),
        '其他固定敌人字段：'+json.dumps(meta,ensure_ascii=False),
        '各字段明确来源：'+json.dumps(reference['field_provenance'],ensure_ascii=False),
        '来源版本：'+reference['source']['game_commit'],
        '精确等级可用性：'+str(reference.get('compiled_database_result_available')),
        '原字段投影（不作为缺失精确等级的有效面板）：'+json.dumps(reference.get('source_projection'),ensure_ascii=False)])
    return '\n'.join(lines)
