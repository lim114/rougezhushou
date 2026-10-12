"""Literal nextSceneId references, separate from origin and execution claims."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
import re
from pathlib import Path
from . import node_catalog as catalog, event_planning as planning

DATA = Path(__file__).with_name('data')


@lru_cache(maxsize=1)
def _data():
    return json.loads((DATA/'original-destinations.json').read_text(encoding='utf-8'))


def _fingerprint(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':')).encode('utf-8')).hexdigest()


def _reference():
    data = _data()
    for name, digest in data['runtime_source_sha256'].items():
        if sha256((DATA/name).read_bytes()).hexdigest() != digest:
            raise ValueError('原选项目的地或目录来源已变化；需重新核验绑定，拒绝复用旧导航。')
    return data


def _choice(choice_id, checked_data=None):
    catalog._text(choice_id, '原选项引用')
    data = _reference() if checked_data is None else checked_data
    row = data['choices'].get(choice_id)
    raw = catalog._original()['choices'].get(choice_id)
    if row is None or raw is None:
        raise ValueError('原选项引用不存在，不能按名称或编号猜测目的地。')
    if _fingerprint(raw) != row['original_record_sha256']:
        raise ValueError('原选项记录与冻结原件不同，拒绝导航。')
    return data, row, raw


def _destination_context(context):
    context = planning._context(context)
    # The origin's node type / natural entry never proves the destination's.
    context.update(node_type=None, entry_mode='content',
        reference_context_scope='declared_destination_comparison_only')
    return context


def destination_reference(choice_id, context=None):
    data, row, raw = _choice(choice_id)
    context = _destination_context(context)
    target_id = row['next_scene_id']
    result = {'choice_id':choice_id, 'choice':deepcopy(raw),
        'destination_scene_id':target_id, 'destination_scene':None,
        'catalog_references':[], 'context':deepcopy(context),
        'original_destination_field_verified':bool(target_id),
        'source_scene_origin_verified':False, 'source_scene_id':None,
        'reachable_from_entry':None, 'actual_destination_entered':None,
        'actual_server_eligible':None, 'actual_selected_battle_id':None,
        'state_after_transition_known':False, 'inventory_updated':False,
        'map_node_binding_created':False, 'generation_probability':None,
        'sources':deepcopy(data['sources']),
        'source_scope':'literal original destination plus independent fixed catalog references'}
    if not target_id:
        result['status']='no_explicit_destination'
        return result
    target = catalog._original()['scenes'].get(target_id)
    if target is None or _fingerprint(target) != row['destination_record_sha256']:
        raise ValueError('原目的地场景缺失或内容已变化，拒绝补造目标。')
    result['destination_scene']=deepcopy(target)
    result['status']='literal_destination_reference'
    for binding in row['catalog_references']:
        event = catalog._event(binding['event_id'])
        scene = catalog._scene(binding['event_id'],binding['scene_key'])
        if target_id not in scene['game_scene_ids'] or _fingerprint(scene)!=binding['scene_record_sha256']:
            raise ValueError('目的地的独立目录场景绑定变化，拒绝按同名拼接。')
        result['catalog_references'].append({
            'event_id':event['id'], 'event_title':event['title'],
            'scene_key':scene['key'], 'scene':deepcopy(scene),
            'exact_original_scene_id_matches':True,
            'event_qualification':planning.event_eligibility(event['id'],context),
            'choice_qualifications':planning.choice_eligibility(event['id'],scene['key'],context),
            'battle_links':planning.event_battle_links(event['id'],scene['key'],context=context),
            'battle_source':'independent fixed catalog explicit battle page links',
            'original_next_field_proves_battle':False,
            'server_scene_reachability_verified':False})
    return result


def event_destination_choices(event_id):
    """Community option-to-original IDs are candidates, not an origin script."""
    data=_reference();event=catalog._event(event_id);rows=[]
    for scene_number,scene in enumerate(event['scenes'],1):
        for choice in scene['choices']:
            for original_id in choice['game_choice_ids']:
                _,reference,raw=_choice(original_id,data)
                if not reference['next_scene_id']:continue
                rows.append({'event_id':event_id,'scene_key':scene['key'],
                    'scene_number':scene_number,'choice_key':choice['key'],
                    'choice_title':choice['title'],'original_choice_id':original_id,
                    'destination_scene_id':reference['next_scene_id'],
                    'original_choice_title':raw['title'],
                    'source_origin_scene_binding_verified':False,
                    'community_option_reference_only':True})
    return {'rows':rows,'source_scene_relation_verified':False,
        'actual_option_displayed':None,'sources':deepcopy(data['sources'])}


STATUS={'matched':'已列条件相符','unknown':'资格未确认','excluded':'已列条件不符'}


def _plain(value):
    return re.sub(r'<[^<>]*>', '', value or '')


def destination_text(result, technical=False):
    if type(technical) is not bool:raise ValueError('技术字段开关需要布尔值。')
    choice=result['choice'];target=result['destination_scene']
    lines=['【原选项目的地参考】','原选项：'+_plain(choice['title']),
        '来源场景与实际可达链：未知；明确目的地不反推选项来源。']
    if target is None:
        lines += ['原件没有明确目的地字段；不从选项类型、名称或编号推断场景。']
    else:
        lines += ['','目的地原文 · '+_plain(target['title']),_plain(target['description']),
            '','目的地条件与作战入口：独立目录参考',
            '按当前声明的层数、难度与持有核对文档；跳转后状态、实际进入及服务器资格未知。']
        if not result['catalog_references']:
            lines.append('该原场景尚未对应目录场景；只显示原文，不猜测选项或作战。')
        for number,reference in enumerate(result['catalog_references'],1):
            q=reference['event_qualification']
            lines.append(f"目录场景参考 {number} · {reference['event_title']}：{STATUS[q['status']]}")
            for check in q['checks']:
                state='相符' if check['matches'] is True else '不符' if check['matches'] is False else '未知'
                lines.append('  条件 '+state+'：'+check['source_text'])
            for ch in reference['choice_qualifications']['rows']:
                lines.append('  '+ch['choice_title']+'：'+STATUS[ch['status']]+'；实际可选未知。')
                if ch['conditional_text']:lines.append('    条件原文：'+ch['conditional_text'])
                if ch['unparsed_condition_text']:lines.append('    附加规则保留原文；完整脚本及实际触发未知。')
                for check in ch['checks']:
                    if check not in q['checks']:
                        state='相符' if check['matches'] is True else '不符' if check['matches'] is False else '未知'
                        lines.append('    条件 '+state+'：'+check['source_text'])
            links=reference['battle_links']['rows']
            if links:
                lines.append('  作战入口来自该目录场景自己的明确战斗链接；目的地字段本身不证明战斗。')
            else:lines.append('  本目录场景没有已绑定的固定作战入口；不从叙述推断关卡。')
        lines.append('已列条件不符的原件仍可阅读和预览，不列为当前可进入的事件。')
    lines += ['','这项预览不增加本局记录、不更新库存，也不将未来场景映射为当前已读地图节点。']
    if technical:
        lines += ['','原选项ID：'+result['choice_id'],
            '原nextSceneId：'+str(result['destination_scene_id']),
            '原选项类型：'+str(choice.get('type')),
            '原场景完整字段：'+json.dumps(target,ensure_ascii=False),
            '目录绑定：'+json.dumps([{'event_id':r['event_id'],'scene_key':r['scene_key']}
                for r in result['catalog_references']],ensure_ascii=False),
            '原件来源：'+result['sources']['original_game_data']['url'],
            '固定目录来源：'+result['sources']['cached_community_catalog']['url']]
    return '\n'.join(lines)
