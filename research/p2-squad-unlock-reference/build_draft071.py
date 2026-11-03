from pathlib import Path
import shutil,hashlib,json,datetime
base=Path(__file__).parent;draft=base/'draft071'
if not draft.exists():shutil.copytree(base/'baseline',draft,ignore=shutil.ignore_patterns('__pycache__'))
name='rouge/run_modifiers.py';raw=(base/'baseline'/name).read_bytes();text=raw.decode()
needle="        resolution['squad']={**squad,'name':record['name']}\n"
addition="""        resolution['squad']={**squad,'name':record['name']}
        from .squad_unlock_reference import squad_unlock_reference
        reference=squad_unlock_reference(record['id'])
        if reference is not None:resolution['squad_unlock_reference']=reference
"""
assert text.count(needle)==1;text=text.replace(needle,addition)
(draft/name).write_bytes(text.encode())
name='rouge/reporting.py';text=(base/'baseline'/name).read_text()
needle="    return {'schema_version':2,'operator':{'id':op,'name':p['name'],'profession':p['profession']},"
addition="""    squad_reference=environment.get('squad_unlock_reference')
    if squad_reference:
        notes=['档案解锁条件：'+squad_reference['unlock_condition_reference']]
        technology=squad_reference['technology_node_reference']
        if technology:
            notes.append('对应科技资料：'+technology['name'])
            gate=technology['gate_reference']
            if gate:notes.append('科技生效门槛资料：'+gate['enable_description_reference'])
        notes.append('这里只列条件资料；账户解锁与条件实际激活未知，不据此切换分队版本或追加效果。当前明确确认的本局效果按原情景计算。')
        sections.append(section('squad_unlock_reference','强化分队 · 条件资料',[
            metric('account_unlock','账户解锁状态',None),
            metric('activation','解锁条件实际激活',None)],notes))
    return {'schema_version':2,'operator':{'id':op,'name':p['name'],'profession':p['profession']},"""
assert text.count(needle)==1;text=text.replace(needle,addition)
(draft/name).write_text(text)
shutil.copyfile(base/'squad_unlock_reference.py',draft/'rouge/squad_unlock_reference.py')
files={name:{'sha256':hashlib.sha256((draft/name).read_bytes()).hexdigest(),'bytes':(draft/name).stat().st_size}
       for name in ('rouge/run_modifiers.py','rouge/reporting.py','rouge/squad_unlock_reference.py')}
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':'59531ff2e9475410a84ef0e60836f89793fd35a9',
         'changed_sources':files,'no_math_state_unlock_or_mode_qualification_changed':True,
         'selected_strengthened_squad_reference_and_report_only':True}
(base/'draft-receipt071.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(receipt)
