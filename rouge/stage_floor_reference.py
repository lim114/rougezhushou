"""Named area identity for fixed battle browsing; never map topology or eligibility."""
from copy import deepcopy
from .base_settlement_planning import _data
from .catalog import catalog


def sixth_floor_reference(stage_id, stage=None):
    data = _data()
    record = data['stages'].get(stage_id)
    actual = catalog()['stages'].get(stage_id)
    if not record or not actual:
        return None
    original = record['original']
    binding = record.get('floor_zero_binding')
    if (not binding or record.get('settlement_source_floors') != [6]
            or binding.get('document_heading') != '0 源流交汇处 (VI)'
            or binding.get('original_zone_id') != 'zone_6'
            or binding.get('original_name') != '源流交汇处'
            or binding.get('original_icon') != 'zone_6'
            or original.get('id') != stage_id
            or any(original.get(k) != actual.get(k)
                   for k in ('name', 'code', 'difficulty', 'isBoss', 'isElite', 'levelId'))):
        return None
    if stage is not None and (stage.get('id', stage_id) != stage_id
            or any(stage.get(k) != original[k] for k in ('name', 'difficulty'))):
        return None
    return {'stage_id': stage_id, 'floor': 6, 'label': '第VI层 · 源流交汇处',
            'documented_pool_marker': 0, 'documented_floors': deepcopy(record['documented_floors']),
            'binding': deepcopy(binding), 'source': deepcopy(data['source']),
            'original_source': deepcopy(data['original_source']),
            'scope': 'fixed_named_area_identity', 'actual_server_eligibility': None,
            'map_connections_known': False, 'actual_occurrence': None}


def floor_reference_text(reference):
    if not reference:
        return ''
    return ('固定资料所属层：第VI层 · 源流交汇处。原目录标记0，'
            '依据同页“0 源流交汇处 (VI)”及原区域名称/icon独立对应；'
            '没有按关卡编号推测层数。当前入口资格与实际出现未知；'
            '本对应不证明第六层模板或连接。\n来源：' + reference['source']['url'])
