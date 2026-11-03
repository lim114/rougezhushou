"""Plain, field-by-field display of operator observations."""
from .catalog import operator_profiles

LABELS={'level':'等级','elite':'精英阶段','potential':'潜能','trust':'信赖',
        'module_id':'装备模组','module_level':'模组阶段','selected_skill':'所选技能'}

def format_operator_observation(operator,cultivation=None, *, technical=False):
    profile=operator_profiles()[operator['id']]
    invalid=set(operator.get('invalid_fields',[]))
    fields={key:value for key,value in operator.get('fields',{}).items() if key not in invalid}
    def value(key,fmt=str):return fmt(fields[key]) if key in fields else '未确认'
    trust=value('trust_display',lambda n:f'{n}%') if 'trust_display' in fields else value('trust',lambda n:f'{n}%（加成进度）')
    selected_number=fields.get('selected_skill')
    if not profile['skills']:selected='无技能'
    elif type(selected_number) is int and 1<=selected_number<=len(profile['skills']):
        selected=f'第{selected_number}技能 · '+profile['skills'][selected_number-1]['levels'][-1]['name']
    else:selected='未确认'
    if 'module_id' not in fields:module_text='未确认'
    elif fields['module_id'] is None:module_text='未装备' if profile['modules'] else '本档案无可装备模组'
    else:
        module=next((m for m in profile['modules'] if m['id']==fields['module_id']),None)
        module_text=(module['name'] if module else '名称未确认的装备模组')+' · 阶段 '+value('module_level')
    lines=[f"干员：{profile['name']}", '', '【培养信息】',
           f"精英阶段：{value('elite')}    等级：{value('level')}    潜能：{value('potential')}",
           f'信赖：{trust}',f'装备模组：{module_text}', '', '【技能信息】', f'所选技能：{selected}']
    if operator.get('recruitment_kind')=='emergency_hire':lines.insert(1,'来源：应急雇佣（人形/时钟标识）；仅一次作战，离队后保留历史。')
    if 'advanced' in operator:lines.insert(1,'本局进阶：'+('已进阶' if operator['advanced'] else '未进阶'))
    ranks={key:value for key,value in operator.get('skill_ranks',{}).items() if str(key) not in operator.get('invalid_skill_ranks',[])}
    for i,skill in enumerate(profile['skills'],1):
        rank=ranks.get(str(i),ranks.get(i))
        text='未确认' if rank is None else f'等级 {rank}' if rank<=7 else f'等级 7 · 专精 {rank-7}'
        lines.append(f'第{i}技能 · {skill["levels"][-1]["name"]}：{text}')
    missing=operator.get('missing_fields',[])
    if missing:
        labels=[('第'+key.rsplit('_',1)[-1]+'技能等级') if key.startswith('skill_rank_') else LABELS.get(key,'未确认的档案字段') for key in missing]
        lines.extend(['', '【读取状态】'])
        lines.append('本帧未读取：'+'、'.join(labels))
        if operator.get('merged_from_pages'):lines.append('上述已显示的历史字段来自此前读取的同一干员档案。')
    if operator.get('scope')=='run':
        if not missing:lines.extend(['', '【读取状态】'])
        lines.append('使用本局已确认记录；暂时不可见的字段继续保留。进阶后尚未重新确认的模组/技能信息不作为当前事实。')
    if technical:
        lines.extend(['', '【技术引用】', '干员引用：'+operator['id']])
        if fields.get('module_id'):lines.append('模组引用：'+fields['module_id'])
        if missing:lines.append('未读取字段引用：'+'、'.join(missing))
    return '\n'.join(lines)
