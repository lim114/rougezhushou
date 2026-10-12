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
    from .enemy_reference_construction import source_path,construction_data,compiled_identity
    path=source_path(binding,exact)
    compiled={key:{'state':'undefined','value':None,'source_selector':None,'source_level':None} for key in fields}
    if path['compiled_result_available']:
        for key,value in construction_data()['defaults'].items():
            if key in compiled:compiled[key]={'state':'constructor_explicit_default','value':deepcopy(value),
                'source_selector':'current native EnemyData/AttributesData constructor explicit assignment', 'source_level':None}
        if path['database_records_used']:
            for n,record in sorted(definitions.items(),key=lambda item:int(item[0])):
                if int(n)>level:continue
                for key,value in record['fields'].items():
                    compiled[key]={'state':'database_definition','value':deepcopy(value),'source_level':int(n),
                        'source_selector':record['source_selector']+'.'+(key if key.startswith('attributes.') else key.split('.',1)[1])+'.m_value'}
        for key,value in binding['overrides'].items():
            compiled[key]={'state':'stage_override','value':deepcopy(value),'source_level':level,
                'source_selector':'$.enemyDbRefs['+str(binding['source_index'])+'].overwrittenData.'+
                    (key if key.startswith('attributes.') else key.split('.',1)[1])+'.m_value'}
    return {'stage_id':stage_id,'enemy_id':enemy_id,'requested_level':level,'scope':data['scope'],
        'attributes':{key:compiled['attributes.'+key]['value'] for key in data['attribute_fields']},
        'metadata':{key:compiled['metadata.'+key]['value'] for key in data['metadata_fields']},
        'source_projection':projection,'source_projection_used_for_construction':False,
        'source_state':path['state'],'compiled_database_result_available':path['compiled_result_available'],
        'compiled_result_available':path['compiled_result_available'],'construction_reference':path,
        'compiled_identity':compiled_identity(binding,path),
        'field_provenance':compiled,'exact_level_present':exact,
        'source':{'game_commit':data['source']['game_commit'],
            'enemy_database':deepcopy(data['source']['enemy_database']),
            'stage':deepcopy(data['source']['stages'][stage_id])},
        'complete_effective_panel':None,'actual_gameplay_verified':False,
        'limits':['useDb=true要求精确数据库等级；缺失时不可借用较低等级。useDb=false且有覆盖对象时采用独立构造，不使用数据库定义。',
            '仅写入有原生明确赋值的构造默认项；未闭合的攻击/防御结构默认值、免疫及空指针分配基线保持未知。',
            '资源key与关卡alias分开；不因别名把派生敌人属性、资源或机制替换成原型敌人。',
            '完整动态面板仍未知；范围、扣血、技力、命中率只是字段参考，不推定实际事件或完整回转。',
            '未推算通过终点时的扣血事件；当前服务器、热更新、实际生成和控制器仍未核验。']}


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
            *(['该引用要求数据库精确等级而条目缺失；不能以别名或默认路径替代所选构造模式。'] if unavailable else [])])
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
        '精确数据库等级存在：'+str(reference.get('exact_level_present')),
        '基包构造结果可用：'+str(reference.get('compiled_result_available')),
        '构造路径：'+json.dumps(reference.get('construction_reference'),ensure_ascii=False),
        '资源及关卡标识：'+json.dumps(reference.get('compiled_identity'),ensure_ascii=False),
        '原字段投影（按构造路径另行选择，不能直接当有效面板）：'+json.dumps(reference.get('source_projection'),ensure_ascii=False)])
    return '\n'.join(lines)
