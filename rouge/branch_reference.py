"""Explicit fixed branch origins and phases, separate from native execution."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from .battle_preview import battle_data,display_cell
from .battle_planning import branch_phase_catalog

@lru_cache(maxsize=1)
def origin_data():
    return json.loads((Path(__file__).with_name('data')/'branch-origin-reference.json').read_text(encoding='utf8'))

def _document(origin):
    rule=origin_data()['observation']['rules'].get(origin.get('entity_id'))
    if not rule or origin['kind']!='predefined':return None
    if type(origin.get('instance_level')) is not int or type(origin.get('skill_level')) is not int:return None
    if origin.get('instance_level') not in rule['documented_instance_levels'] or origin.get('skill_level') not in rule['documented_skill_levels']:return None
    if ((origin.get('raw') or {}).get('inst') or {}).get('phase')!='PHASE_0':return None
    return deepcopy(rule)

def branch_reference(stage_id,branch_id=None,phase=None):
    if not isinstance(stage_id,str) or not stage_id:raise ValueError('固定关卡ID需要非空文本。')
    if branch_id is not None and (not isinstance(branch_id,str) or not branch_id):raise ValueError('分支ID需要非空文本。')
    data=origin_data();stage=battle_data()['stages'].get(stage_id);index=data['stages'].get(stage_id)
    if not stage or not index:raise ValueError('没有此固定关卡。')
    level=data['levels'][index['level_key']]
    if stage['level_source']['sha256']!=level['source']['sha256']:raise ValueError('分支来源与固定图版本不同。')
    if branch_id is not None and branch_id not in level['branches']:raise ValueError('没有此固定分支。')
    if phase is not None and (type(phase) is not int or phase<1 or branch_id is None):raise ValueError('阶段需要具名分支中的正整数。')
    phases=branch_phase_catalog(stage_id,branch_id)['branches'];nr,nc=len(stage['map']),len(stage['map'][0]);rows=[]
    for branch in phases:
        key=branch['branch_id'];refs=level['branches'][key];origins=[];locations=[]
        for raw in refs['origins']:
            origin=deepcopy(raw);origin['display_cell']=display_cell(raw.get('position'),nr,nc)
            origin['documented_trigger_reference']=_document(raw);origin['actual_trigger_verified']=False
            origin['actual_trigger']=None;origin['actual_seconds']=None
            origins.append(origin)
            if origin['display_cell']:
                locations.append({'reference_id':origin['id'],'name':origin.get('name') or '具名来源未确认',
                    'cell':origin['display_cell'],'source_kind':'producer_declaration',
                    'source_selector':origin['source_selector'],'stage_id':stage_id,'branch_id':key,
                    'level_sha256':stage['level_source']['sha256']})
        selected=branch['phases']
        if phase is not None:
            selected=[p for p in selected if p['phase']==phase]
            if not selected:raise ValueError('阶段超出固定分支范围。')
        selected=deepcopy(selected)
        for p in selected:
            for action in p['actions']:
                binding=next((a for a in refs['activations'] if a['action_id']==action['id']),None)
                action['predefined_binding']=deepcopy(binding)
                entity_names=[e['name'] for e in stage['enemies'] if e['id']==action['action'].get('key')]
                if binding:entity_names=[o.get('name') for o in binding['objects'] if o.get('name')]
                action['entity_name']=' / '.join(dict.fromkeys(entity_names)) or '实体名称未确认'
                action['display_cell']=None;action['actual_execution_seconds']=None
                if binding and binding['binding_status']=='exact_alias':
                    obj=binding['objects'][0];cell=display_cell(obj.get('position'),nr,nc)
                    action['display_cell']=cell
                    if cell:locations.append({'reference_id':action['id'],'name':obj.get('name') or '预置对象名称未确认',
                        'cell':cell,'source_kind':'activation_object','source_selector':obj['source_selector'],
                        'action_selector':action['source_selector'],'stage_id':stage_id,'branch_id':key,
                        'phase':p['phase'],'level_sha256':stage['level_source']['sha256']})
        rows.append({'branch_id':key,'catalog_ordinal':list(level['branches']).index(key)+1,'origins':origins,'phases':selected,'phase_count':branch['phase_count'],
            'origin_status':'explicit_parameter_reference' if origins else 'unknown',
            'map_references':locations,'actual_trigger':None,'phase_selection':None,
            'actual_global_seconds':None,'raw_nonphase_fields':branch['raw_nonphase_fields']})
    return {'stage_id':stage_id,'stage_name':stage['name'],'source':deepcopy(level['source']),
        'rows':rows,'selected_branch':branch_id,'selected_phase':phase,
        'full_runtime_sources_known':False,'all_routes_bound':False,'limits':list(data['limits'])}

def branch_reference_text(result,technical=False):
    lines=['条件分支资料：'+result['stage_name'],
        '原件字段同值引用与公开触发说明分开显示；实际触发、阶段选择和全局时刻保持未知。']
    if not result['rows']:lines.append('固定配置没有声明条件分支；动态脚本仍未知。')
    for row in result['rows']:
        lines += ['',f"分支 {row['catalog_ordinal']} · 固定阶段 {row['phase_count']} 个"+(' · '+row['branch_id'] if technical else '')]
        if not row['origins']:lines.append('来源：没有找到本关原件中直接命名此branch_id的来源，保持未知。')
        for origin in row['origins']:
            lines.append('来源字段：'+(origin.get('name') or '名称未确认的敌人引用')+'；仅配置引用已证。')
            doc=origin['documented_trigger_reference']
            lines.append('精确实体/级别的公开触发参考：'+doc['trigger_reference'] if doc else '公开触发参考：没有精确实体/级别的可用依据，未知。')
            if doc:lines.append('公开说明来源：'+doc['source']['url'])
            if technical:lines.append('原件参数位置：'+origin['parameter_selector'])
        for p in row['phases']:
            lines += ['',f"阶段 {p['phase']} · 动作 {len(p['actions'])} 个；实际阶段开始时刻未知。"]
            if technical:lines.append('阶段预延迟原参数：'+str(p['pre_delay_parameter']))
            if not p['actions']:lines.append('空配置阶段；不造动作、时间或路线。')
            for action in p['actions']:
                a=action['action'];lines.append(action['type_label']+' · '+action['entity_name']+f"；配置数量 {a.get('count')}。"+(' · '+str(a.get('key') or '空键') if technical else ''))
                cell=action['display_cell'];binding=action['predefined_binding']
                lines.append(f"唯一alias对应预置格：第{cell['row']+1}行、第{cell['col']+1}列。" if cell else
                    ('预置alias未唯一绑定，位置未知。' if binding else '生成位置/路线数组未知；不按routeIndex借基础路线。'))
                if technical:
                    lines += ['动作原件位置：'+action['source_selector'],'完整动作原参数：'+json.dumps(a,ensure_ascii=False,indent=2)]
    lines += ['',*result['limits']]
    if technical:lines.append('固定关卡来源：'+result['source']['url'])
    return '\n'.join(lines)
